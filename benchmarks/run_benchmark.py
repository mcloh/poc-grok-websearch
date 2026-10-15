"""Benchmark pareado via OCI: 100 prompts idênticos, sem retry automático.

Sem --execute, apenas valida dados e apresenta o plano. Resultados ficam locais.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal
import argparse
import csv
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import time
from urllib.parse import urlparse
import requests

ROOT = Path(__file__).resolve().parent
MODELS = ['xai.grok-4.20-non-reasoning', 'xai.grok-4.3']
D = lambda value: Decimal(str(value))
SYSTEM = ('Você é um assistente em português brasileiro. Use web_search para verificar cada consulta, '
          'mesmo que conheça o assunto. A data de referência consta na pergunta. '
          'Responda em até 200 palavras, cite URLs e datas das fontes. '
          'Diferencie a data do fato e a data de publicação. Nunca invente preços, agendas, '
          'previsões ou disponibilidade. Informe explicitamente dados não confirmados.')

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def load_dataset():
    dataset = json.loads((ROOT/'intents.json').read_text())
    rows = dataset['intents']
    assert len(rows) == 100 and len({r['id'] for r in rows}) == 100
    assert len({r['prompt'] for r in rows}) == 100
    for row in rows:
        assert hashlib.sha256(row['prompt'].encode()).hexdigest() == row['prompt_sha256']
    assert all(sum(r['category'] == category for r in rows) == 25
               for category in ['culinaria', 'esportes', 'clima', 'entretenimento'])
    return dataset

def calculate_cost(usage, model, prices):
    """Saída já inclui raciocínio; cache é subconjunto da entrada. Sem duplicação."""
    try:
        total_in = usage['input_tokens']
        cached = usage['input_tokens_details']['cached_tokens']
        output = usage['output_tokens']
        calls = usage['server_side_tool_usage_details']['web_search_calls']
        if any(not isinstance(v, int) or v < 0 for v in [total_in, cached, output, calls]) or cached > total_in:
            return {'status': 'unknown', 'reason': 'Invalid usage counters'}
        detail = usage['server_side_tool_usage_details']
        if any(v for k, v in detail.items() if k != 'web_search_calls'):
            return {'status': 'unknown', 'reason': 'Other billable tools observed'}
        family = 'grok-4.20' if model.startswith('xai.grok-4.20-') else model.removeprefix('xai.')
        rate = prices['models'][family]
        def priced(band):
            regular_cost = D(total_in-cached)*D(rate['input_'+band]['usd'])/D(1000000)
            cached_cost = D(cached)*D(rate['cached_'+band]['usd'])/D(1000000)
            output_cost = D(output)*D(rate['output_'+band]['usd'])/D(1000000)
            search_cost = D(calls)*D(prices['web_search']['usd_per_1000'])/D(1000)
            return {'status': 'computed_from_measured_usage', 'input_usd': str(regular_cost),
                    'cached_input_usd': str(cached_cost), 'output_usd': str(output_cost),
                    'web_search_usd': str(search_cost),
                    'total_usd': str(regular_cost+cached_cost+output_cost+search_cost),
                    'input_tokens': total_in, 'cached_input_tokens': cached,
                    'output_tokens': output,
                    'reasoning_tokens': usage.get('output_tokens_details', {}).get('reasoning_tokens'),
                    'web_search_calls': calls}
        if total_in < 200000:
            return priced('short')
        # Uso de loops pode ser agregado. Resolver a faixa somente quando a fórmula
        # dos SKUs Oracle coincide exatamente com o custo nativo carregado pela OCI.
        ticks = usage.get('cost_in_usd_ticks')
        if not isinstance(ticks, int) or ticks < 0:
            return {'status': 'unknown', 'reason': 'Long-context band needs native cost reconciliation'}
        native = D(ticks)/D(10000000000)
        matches = [(band, priced(band)) for band in ['short', 'long']
                   if D(priced(band)['total_usd']) == native]
        if len(matches) != 1:
            return {'status': 'unknown', 'reason': 'No unique Oracle price band matching native cost'}
        band, result = matches[0]
        return {**result, 'pricing_band': band,
                'band_validation': 'Oracle SKU formula equals cost_in_usd_ticks / 10^10; not OCI invoice reconciliation'}
    except (KeyError, TypeError):
        return {'status': 'unknown', 'reason': 'Missing billing usage counters'}

def append_event(path, event):
    with path.open('a') as handle:
        handle.write(json.dumps(event, ensure_ascii=False)+'\n')
        handle.flush()
        os.fsync(handle.fileno())

def invoke(model, intent, base, headers, prices, raw_folder):
    neutral_body = {'input': [{'role': 'user', 'content': intent['prompt']}],
                    'instructions': SYSTEM, 'tools': [{'type': 'web_search'}],
                    'store': False, 'max_output_tokens': 2400}
    body = {'model': model, **neutral_body}
    result = {'model': model, 'intent_id': intent['id'], 'category': intent['category'],
              'prompt_sha256': intent['prompt_sha256'], 'shared_payload_sha256': digest(neutral_body),
              'started_at': datetime.now(timezone.utc).isoformat()}
    started = time.monotonic()
    try:
        response = requests.post(base+'/responses', headers=headers, json=body, timeout=(10, 150))
        result['http'] = response.status_code
        try:
            data = response.json()
        except ValueError:
            data = {}
        (raw_folder/f"{intent['id']}-{model}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
        output = data.get('output', [])
        events = [item for item in output if item.get('type') == 'web_search_call']
        citations = [a for item in output for content in item.get('content', [])
                     for a in content.get('annotations', []) if a.get('type') == 'url_citation']
        sources = [s for item in events for s in item.get('action', {}).get('sources', [])]
        answer = '\n'.join(content.get('text', '') for item in output for content in item.get('content', []))
        searches = [item for item in events if item.get('status') == 'completed'
                    and item.get('action', {}).get('type') == 'search']
        result.update(returned_model=data.get('model'), provider_response_id=data.get('id'),
                      usage=data.get('usage'),
                      tool_events=[{'action': e.get('action', {}).get('type'), 'status': e.get('status')} for e in events],
                      citation_count=len(citations), source_count=len(sources), answer_chars=len(answer),
                      response_status=data.get('status'),
                      incomplete_details=data.get('incomplete_details'),
                      websearch_confirmed=response.status_code == 200 and bool(searches) and bool(sources) and bool(citations),
                      cost=calculate_cost(data.get('usage') or {}, model, prices))
        if response.status_code != 200:
            result['failure'] = 'provider_http_error'
    except requests.RequestException as exc:
        # Timeout não prova ausência de cobrança. Não reenviar a interação.
        result.update(http=None, failure=type(exc).__name__,
                      cost={'status': 'unknown', 'reason': 'Transport failure; billing may have occurred'})
    result['seconds'] = round(time.monotonic()-started, 3)
    result['finished_at'] = datetime.now(timezone.utc).isoformat()
    return result

def export_results(folder, rows, reservation):
    fields = ['intent_id','category','model','http','websearch_confirmed','seconds',
              'input_tokens','cached_input_tokens','output_tokens','reasoning_tokens','web_search_calls',
              'input_usd','cached_input_usd','output_usd','web_search_usd','total_usd','cost_status',
              'citation_count','source_count','prompt_sha256','shared_payload_sha256']
    with (folder/'interactions.csv').open('w') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            flat = {**row, **row.get('cost', {}), 'cost_status': row.get('cost', {}).get('status')}
            writer.writerow({f: flat.get(f) for f in fields})
    summaries = []
    for model in MODELS:
        selected = [r for r in rows if r['model'] == model]
        known = [r for r in selected if r.get('cost', {}).get('total_usd') is not None]
        unknown = len(selected)-len(known)
        values = [D(r['cost']['total_usd']) for r in known]
        def total(key):
            return sum(D(r['cost'][key]) for r in known)
        summaries.append({'model': model, 'interactions': len(selected), 'http_200': sum(r.get('http') == 200 for r in selected),
                          'websearch_confirmed': sum(r.get('websearch_confirmed', False) for r in selected),
                          'cost_known_interactions': len(known), 'cost_unknown_interactions': unknown,
                          'total_usd_known': str(sum(values)),
                          'mean_usd_known': str(sum(values)/len(values)) if values else None,
                          'median_usd_known': str(statistics.median(values)) if values else None,
                          'p95_usd_known': str(sorted(values)[math.ceil(.95*len(values))-1]) if values else None,
                          'web_search_usd': str(total('web_search_usd')),
                          'input_tokens': int(total('input_tokens')), 'cached_input_tokens': int(total('cached_input_tokens')),
                          'output_tokens': int(total('output_tokens')), 'web_search_calls': int(total('web_search_calls')),
                          'median_seconds': statistics.median(r['seconds'] for r in selected) if selected else None})
    paired = {}
    for row in rows:
        paired.setdefault(row['intent_id'], []).append(row)
    complete_pairs = [pair for pair in paired.values() if len(pair) == 2]
    assert all(pair[0]['shared_payload_sha256'] == pair[1]['shared_payload_sha256'] for pair in complete_pairs)
    report = {'generated_at': datetime.now(timezone.utc).isoformat(), 'models': summaries,
              'completed_interactions': len(rows), 'expected_interactions': 200,
              'paired_intents': len(complete_pairs),
              'estimated_reserve_for_unknown_usd': str(sum(reservation for r in rows if r.get('cost', {}).get('total_usd') is None)),
              'billing_note': 'Custo calculado do uso medido a preços de lista Oracle; não é fatura OCI. Sem impostos, descontos contratuais, VM, rede e armazenamento.'}
    (folder/'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--budget-usd', type=Decimal)
    parser.add_argument('--run-id', default='comparison-2026-10-15')
    parser.add_argument('--pair-limit', type=int, default=100, help='Piloto retoma no mesmo run-id, sem repetir chamadas')
    args = parser.parse_args()
    assert 1 <= args.pair_limit <= 100
    assert args.run_id and all(c.isalnum() or c in '-_' for c in args.run_id)
    dataset = load_dataset()
    prices = json.loads((ROOT/'oracle-prices.json').read_text())
    print(f'100 intenções; {len(MODELS)} modelos; 200 interações; concorrência 2; sem retries.', flush=True)
    if not args.execute:
        print('Dry run: nenhuma chamada feita. Para executar, definir --execute --budget-usd LIMITE.')
        return
    assert args.budget_usd and args.budget_usd > 0, 'É necessário orçamento explícito'
    base = os.environ['OCI_BASE_URL'].rstrip('/')
    assert base == 'https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/v1'
    headers = {'Authorization': 'Bearer '+os.environ['OCI_API_KEY'], 'OpenAI-Project': os.environ['OCI_PROJECT_ID']}
    folder = ROOT/'runs'/args.run_id
    folder.mkdir(parents=True, exist_ok=True)
    lockfile = (folder/'run.lock').open('w')
    fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    raw_folder = folder/'raw'
    raw_folder.mkdir(exist_ok=True)
    manifest = {'dataset_sha256': digest(dataset), 'prices_sha256': digest(prices),
                'system_sha256': hashlib.sha256(SYSTEM.encode()).hexdigest(), 'models': MODELS,
                'reference_date': dataset['reference_date'], 'region': 'us-chicago-1',
                'concurrency': 2, 'max_output_tokens': 2400, 'retries': 0, 'transport_timeout_seconds': 150}
    manifest_file = folder/'manifest.json'
    if manifest_file.exists():
        assert json.loads(manifest_file.read_text()) == manifest, 'Manifesto alterado; use outro run-id'
    else:
        manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    ledger = folder/'events.jsonl'
    events = [json.loads(line) for line in ledger.read_text().splitlines()] if ledger.exists() else []
    rows = [e['result'] for e in events if e['event'] == 'finished']
    started = {(e['intent_id'],e['model']) for e in events if e['event'] == 'started'}
    finished = {(r['intent_id'],r['model']) for r in rows}
    assert started == finished, 'Há chamadas interrompidas sem resultado; revisar cobrança antes de continuar'
    assert len(finished) == len(rows), 'Interações duplicadas no registro'
    reservation = D('.25')
    def committed():
        return sum(D(r['cost']['total_usd']) if r.get('cost', {}).get('total_usd') is not None else reservation for r in rows)
    # Um piloto de cada categoria; depois alternância de categorias ao longo do lote.
    order = [i+25*c for i in range(25) for c in range(4)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for index in order[:args.pair_limit]:
            intent = dataset['intents'][index]
            pending = [m for m in MODELS if (intent['id'],m) not in finished]
            if not pending:
                continue
            if committed()+reservation*len(pending) > args.budget_usd:
                print('STOP orçamento: sem saldo para reservar o próximo par.', flush=True)
                break
            jobs=[]
            for model in pending:
                append_event(ledger, {'event': 'started', 'intent_id': intent['id'], 'model': model,
                                      'at': datetime.now(timezone.utc).isoformat(), 'reserved_usd': str(reservation)})
                jobs.append(pool.submit(invoke, model, intent, base, headers, prices, raw_folder))
            stop = False
            for job in jobs:
                result = job.result()
                append_event(ledger, {'event':'finished','result':result})
                rows.append(result)
                finished.add((result['intent_id'],result['model']))
                print(f"{len(rows)}/200 {result['intent_id']} {result['model']} HTTP={result.get('http')} busca={result.get('websearch_confirmed')} USD={result.get('cost',{}).get('total_usd','unknown')}", flush=True)
                # Falha exige diagnóstico; timeout não será repetido e custo não vira zero.
                stop |= result.get('http') != 200 or result.get('cost',{}).get('total_usd') is None
            export_results(folder, rows, reservation)
            if stop:
                print('STOP diagnóstico necessário; nenhuma nova interação será enviada.', flush=True)
                break
    report = export_results(folder, rows, reservation)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)

if __name__ == '__main__':
    main()
