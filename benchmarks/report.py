"""Publica apenas métricas selecionadas do lote local, sem respostas brutas."""
import argparse
import csv
from collections import Counter
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent
D = lambda value: Decimal(str(value))

def stats(rows):
    known = [r for r in rows if r.get('cost', {}).get('total_usd') is not None]
    values = [D(r['cost']['total_usd']) for r in known]
    def total(key):
        return sum((D(r['cost'][key]) for r in known if r['cost'].get(key) is not None), D(0))
    return {'interactions':len(rows), 'http_200':sum(r.get('http') == 200 for r in rows),
            'websearch_confirmed':sum(r.get('websearch_confirmed',False) for r in rows),
            'unknown_cost':len(rows)-len(known), 'total_usd':str(sum(values)),
            'mean_usd':str(statistics.mean(values)) if values else None,
            'median_usd':str(statistics.median(values)) if values else None,
            'p95_usd':str(sorted(values)[math.ceil(.95*len(values))-1]) if values else None,
            'web_search_usd':str(total('web_search_usd')),
            'input_usd':str(total('input_usd')), 'cached_input_usd':str(total('cached_input_usd')),
            'output_usd':str(total('output_usd')),
            **{key:int(total(key)) for key in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens','web_search_calls']},
            'median_seconds':statistics.median(r['seconds'] for r in rows) if rows else None}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-id',default='comparison-2026-10-15')
    args=parser.parse_args()
    assert all(c.isalnum() or c in '-_' for c in args.run_id)
    source=ROOT/'runs'/args.run_id
    manifest=json.loads((source/'manifest.json').read_text())
    events=[json.loads(line) for line in (source/'events.jsonl').read_text().splitlines()]
    rows=[e['result'] for e in events if e['event']=='finished']
    assert len({(r['model'],r['intent_id']) for r in rows})==len(rows)
    intents=json.loads((ROOT/'intents.json').read_text())['intents']
    lookup={r['id']:r for r in intents}
    for row in rows:
        assert row['prompt_sha256']==lookup[row['intent_id']]['prompt_sha256']
        cost=row.get('cost',{})
        if cost.get('total_usd') is not None:
            assert D(cost['total_usd'])==sum(D(cost[k]) for k in ['input_usd','cached_input_usd','output_usd','web_search_usd'])
    models=manifest['models']
    by_model={m:stats([r for r in rows if r['model']==m]) for m in models}
    by_category={c:{m:stats([r for r in rows if r['model']==m and r['category']==c]) for m in models}
                 for c in ['culinaria','esportes','clima','entretenimento']}
    paired=[]
    for intent in intents:
        pair=[r for r in rows if r['intent_id']==intent['id']]
        if len(pair)!=2:continue
        assert pair[0]['shared_payload_sha256']==pair[1]['shared_payload_sha256']
        if any(r.get('cost',{}).get('total_usd') is None for r in pair):continue
        amounts={r['model']:D(r['cost']['total_usd']) for r in pair}
        minimum=min(amounts.values())
        winners=[model for model,value in amounts.items() if value==minimum]
        paired.append({'intent_id':intent['id'],'category':intent['category'],
                       'cheaper_model':winners[0] if len(winners)==1 else 'tie',
                       'all_websearch_confirmed':all(r.get('websearch_confirmed') for r in pair)})
    full=len(rows)==200 and all(v['interactions']==100 for v in by_model.values())
    report={'run_id':args.run_id,'status':'complete' if full else 'partial',
            'method':'100 prompts idênticos por modelo, OCI real, sem histórico e sem retry; concorrência 2',
            'region':manifest['region'],'reference_date':manifest['reference_date'],
            'manifest':manifest,'total':stats(rows),'by_model':by_model,'by_category':by_category,
            'paired_comparisons':len(paired),'paired_cheaper_counts':dict(Counter(p['cheaper_model'] for p in paired)),
            'billing_note':'Custo calculado de tokens e buscas medidos, a preços de lista Oracle; não é fatura conciliada. Sem impostos, descontos, VM, rede ou armazenamento.',
            'quality_note':'Confirmação de busca não prova correção factual, completude ou superioridade da resposta.'}
    target=ROOT/'results'/args.run_id
    target.mkdir(parents=True,exist_ok=True)
    (target/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    public=[]
    for row in rows:
        public.append({**{key:value for key,value in row.items() if key not in ['provider_response_id']},
                       'intent':lookup[row['intent_id']]['intent']})
    (target/'measured-usage.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
    with (source/'interactions.csv').open() as handle:
        reader=csv.DictReader(handle)
        fields=list(reader.fieldnames)+['intent','prompt']
        csvrows=list(reader)
    with (target/'interactions.csv').open('w') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields,lineterminator="\n")
        writer.writeheader()
        for row in csvrows:
            intent=lookup[row['intent_id']]
            writer.writerow({**row,'intent':intent['intent'],'prompt':intent['prompt']})
    def money(value):return f"{D(value):.6f}" if value is not None else 'indisponível'
    lines=['# Comparativo de 100 intenções — '+manifest['reference_date'], '',
           f"Estado: **{report['status']}**. {len(rows)} de 200 interações concluídas.", '',
           'Resultados calculados do uso medido a preço de lista Oracle, incluindo tokens de busca e chamadas da ferramenta. Não representam fatura OCI conciliada.', '',
           '| Modelo | Interações | Busca confirmada | Entrada¹ | Cache² | Saída³ | Buscas tarifadas | Custo USD | Média USD | Mediana USD | P95 USD |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for model,s in by_model.items():
        lines.append(f"| `{model}` | {s['interactions']} | {s['websearch_confirmed']} | {s['input_tokens']} | {s['cached_input_tokens']} | {s['output_tokens']} | {s['web_search_calls']} | {money(s['total_usd'])} | {money(s['mean_usd'])} | {money(s['median_usd'])} | {money(s['p95_usd'])} |")
    lines+=['','¹ Entrada total inclui cache. ² Cache é subconjunto da entrada. ³ Saída inclui raciocínio; este não é somado novamente.', '',
            '## Custos por categoria', '', '| Categoria | Modelo | Interações | Custo USD | Média USD | Buscas tarifadas |', '|---|---|---:|---:|---:|---:|']
    for category,model_stats in by_category.items():
        for model,s in model_stats.items():
            lines.append(f"| {category} | `{model}` | {s['interactions']} | {money(s['total_usd'])} | {money(s['mean_usd'])} | {s['web_search_calls']} |")
    lines+=['','## Composição do custo', '', '| Modelo | Entrada sem cache USD | Cache USD | Saída USD | Busca USD | Raciocínio (tokens) | Mediana de tempo (s) |', '|---|---:|---:|---:|---:|---:|---:|']
    for model,s in by_model.items():
        lines.append(f"| `{model}` | {money(s['input_usd'])} | {money(s['cached_input_usd'])} | {money(s['output_usd'])} | {money(s['web_search_usd'])} | {s['reasoning_tokens']} | {s['median_seconds']} |")
    lines+=['','## Auditoria e limites', '',
            f"- {len(paired)} pares completos com custo conhecido; os hashes do payload compartilhado coincidiram em todos esses pares.",
            '- Comparações pareadas de menor custo: '+json.dumps(report['paired_cheaper_counts'],ensure_ascii=False)+'.',
            '- Custos desconhecidos: '+str(report['total']['unknown_cost'])+'; se houver, ficam fora das médias de custo e não são tratados como zero.',
            '- Uma execução por intenção e modelo, com cache e condições reais do serviço; não há controle de todo o estado interno de cache ou dos resultados voláteis da web.',
            '- A mesma pergunta pode provocar números diferentes de buscas e tamanhos de contexto. Esse comportamento faz parte do custo observado.',
            '- Busca confirmada exige ação search completed, fontes e citações estruturadas. Isso não substitui avaliação factual da resposta.',
            '- Preços e metodologia: [protocolo](../../PROTOCOLO.md) e [SKUs Oracle](../../oracle-prices.json).',
            '- [CSV por interação](interactions.csv), [métricas e composição de custo](measured-usage.json), [resumo estruturado](summary.json).', '']
    (target/'REPORT.md').write_text('\n'.join(lines))
    files=['summary.json','measured-usage.json','interactions.csv','REPORT.md']
    (target/'sha256.json').write_text(json.dumps({name:hashlib.sha256((target/name).read_bytes()).hexdigest() for name in files},indent=2)+'\n')
    print(f"{report['status']}: {len(rows)}/200; USD {report['total']['total_usd']}; artefatos em benchmarks/results/{args.run_id}/")

if __name__=='__main__':main()
