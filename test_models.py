"""Teste pago da mesma aplicação ASGI com modelos Grok via OCI.

Executar com variáveis de .env exportadas. Concorrência máxima: 2.
Uma chamada por modelo, sem retries; até 2400 tokens de saída e timeout de 150s.
"""
import argparse
import concurrent.futures
import importlib.metadata
from datetime import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

MODELS = [
    'xai.grok-4.20-0309-non-reasoning', 'xai.grok-4.20-0309-reasoning',
    'xai.grok-4.20-non-reasoning', 'xai.grok-4.20-reasoning',
    'xai.grok-4.3', 'xai.grok-4.6', 'xai.grok-4.7',
]
ROOT = Path(__file__).resolve().parent

def worker(model):
    os.environ['OCI_MODEL'] = model
    from fastapi.testclient import TestClient
    import app
    captured = {}
    original = app.requests.post
    def observe(*args, **kwargs):
        response = original(*args, **kwargs)
        captured['http'] = response.status_code
        captured['body'] = response.json()
        return response
    app.requests.post = observe
    now = datetime.now(ZoneInfo('America/Sao_Paulo'))
    message = (f'Use web_search para encontrar uma notícia publicada hoje ({now.date()}). '
               'Faça uma consulta curta e cite uma fonte com URL e data. Responda em até 100 palavras. '
               'Se não encontrar notícia de hoje, declare isso.')
    started = time.monotonic()
    with TestClient(app.app) as client:
        health = client.get('/health').json()
        response = client.post('/api/chat', auth=('poc', os.environ['APP_PASSWORD']), json={'message': message})
    data = response.json()
    calls = data.get('web_search_calls', [])
    completed = [c for c in calls if c.get('status') == 'completed']
    # Exigir ação real de pesquisa, fontes e citações: HTTP 200 sozinho não basta.
    searches = [c for c in completed if c.get('action', {}).get('type') == 'search']
    sources = [s for c in searches for s in c.get('action', {}).get('sources', [])]
    confirmed = response.status_code == 200 and bool(searches) and bool(sources) and bool(data.get('citations'))
    body = captured.get('body', {})
    error = body.get('error', {})
    error_text = str(error.get('message', ''))
    for key in ('OCI_API_KEY', 'OCI_PROJECT_ID', 'APP_PASSWORD'):
        value = os.environ.get(key)
        if value: error_text = error_text.replace(value, '[redacted]')
    error_text = re.sub(r'ocid1\.[\w.-]+', '[redacted]', error_text)
    row = {'requested_model': model, 'returned_model': data.get('model'), 'tested_at': now.isoformat(),
           'app_http': response.status_code, 'oci_http': captured.get('http'),
           'seconds': round(time.monotonic()-started, 2), 'websearch_confirmed': confirmed,
           'completed_searches': len(searches), 'source_count': len(sources),
           'citation_count': len(data.get('citations', [])),
           'tool_events': [{'status': c.get('status'), 'action': c.get('action', {}).get('type')} for c in calls],
           'usage': data.get('usage'),
           'citation_urls': sorted({c['url'] for c in data.get('citations', []) if c.get('url')}),
           'error': error_text or data.get('detail'), 'health_model': health['model']}
    folder = ROOT/'evidence'/'model-tests-raw'
    folder.mkdir(parents=True, exist_ok=True)
    (folder/(model+'.json')).write_text(json.dumps({'message': message, 'app_response': data, 'upstream': captured}, ensure_ascii=False, indent=2))
    print(json.dumps(row, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', choices=MODELS)
    parser.add_argument('--models', nargs='+', choices=MODELS, default=MODELS)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    def run(model):
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker', model],
                                capture_output=True, text=True, timeout=180, cwd=ROOT)
        if result.returncode:
            raise RuntimeError(f'{model}: worker failed (exit {result.returncode})')
        row = json.loads(result.stdout)
        print(f"{model}: app={row['app_http']} OCI={row['oci_http']} search={row['websearch_confirmed']} {row['seconds']}s", flush=True)
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(run, args.models))
    previous = ROOT/'evidence/grok-websearch-models.json'
    if previous.exists():
        old = json.loads(previous.read_text())
        today = datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat()
        if old.get('tested_at', '').startswith(today):
            rows += [row for row in old['results'] if row['requested_model'] not in args.models]
            rows.sort(key=lambda row: MODELS.index(row['requested_model']))
    report = {'tested_at': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat(),
              'region': 'us-chicago-1', 'endpoint': '/v1/responses',
              'method': 'POST /api/chat via FastAPI TestClient; inferência OCI real; um processo isolado por modelo',
              'test_runtime': {'python': sys.version.split()[0], **{name: importlib.metadata.version(name) for name in ['fastapi', 'starlette', 'httpx', 'requests']}},
              'max_output_tokens': 2400, 'concurrency': 2, 'retries': 0,
              'confirmation_criteria': 'HTTP 200, search completed, fontes não vazias e citações estruturadas',
              'results': rows,
              'aggregate_usage': {key: sum((r.get('usage') or {}).get(key, 0) or 0 for r in rows)
                                  for key in ['input_tokens', 'output_tokens', 'total_tokens', 'num_server_side_tools_used', 'cost_in_usd_ticks']}}
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/grok-websearch-models.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

if __name__ == '__main__':
    main()
