"""Auditoria retrospectiva: 12 prompts x 7 IDs OCI; sem retry automático; dry run por padrão."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from collections import Counter

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
import run_benchmark as core

MODELS=['xai.grok-4.20-0309-non-reasoning','xai.grok-4.20-0309-reasoning',
        'xai.grok-4.20-non-reasoning','xai.grok-4.20-reasoning',
        'xai.grok-4.3','xai.grok-4.6','xai.grok-4.7']
D=lambda value:Decimal(str(value))

def check_dataset(data):
    assert len(data['intents'])==12
    assert len({row['id'] for row in data['intents']})==12
    for category in ['culinaria','esportes','clima','entretenimento']:
        assert sum(row['category']==category for row in data['intents'])==3
    for row in data['intents']:
        assert hashlib.sha256(row['prompt'].encode()).hexdigest()==row['prompt_sha256']

def read_results(events):
    rows=[]
    positions={}
    for event in events:
        if event['event']=='finished':
            row=event['result'];key=(row['intent_id'],row['model'])
            assert key not in positions,'Resultado duplicado'
            positions[key]=len(rows);rows.append(row)
        elif event['event']=='cost_reconciled':
            row=event['result'];key=(row['intent_id'],row['model'])
            assert key in positions
            original=rows[positions[key]]
            assert original['cost'].get('total_usd') is None
            assert original['usage']==row['usage'] and original['shared_payload_sha256']==row['shared_payload_sha256']
            rows[positions[key]]=row
        elif event['event']=='infrastructure_rejected':
            key=(event['intent_id'],event['model'])
            assert key in positions
            original=rows[positions[key]]
            assert original.get('http')==429 and original['cost'].get('total_usd') is None
            rows.pop(positions[key])
            positions={(r['intent_id'],r['model']):index for index,r in enumerate(rows)}
    return rows

def invoke(model,intent,base,headers,prices,folder):
    result=core.invoke(model,intent,base,headers,prices,folder)
    raw=folder/f"{intent['id']}-{model}.json"
    data=json.loads(raw.read_text()) if raw.exists() else {}
    text='\n'.join(content.get('text','') for item in data.get('output',[])
                   if item.get('type')=='message' for content in item.get('content',[])
                   if content.get('type')=='output_text')
    truncated=bool(data.get('incomplete_details')) or data.get('status') in ['incomplete','failed','cancelled']
    result['final_answer_chars']=len(text)
    result['truncated']=truncated
    result['reliable_search']=bool(result.get('websearch_confirmed') and text.strip() and not truncated
                                   and result['cost'].get('total_usd') is not None)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--budget-total-usd',type=Decimal)
    parser.add_argument('--run-id',default='screening-2026-10-15-v1')
    parser.add_argument('--intent-limit',type=int,default=12)
    parser.add_argument('--cooldown-seconds',type=int,default=75)
    args=parser.parse_args()
    assert 1<=args.intent_limit<=12
    assert args.run_id and all(c.isalnum() or c in '-_' for c in args.run_id)
    dataset=json.loads((ROOT/'intents-12.json').read_text())
    prices=json.loads((ROOT/'oracle-prices.json').read_text())
    rules=json.loads((ROOT/'scoring-rules.json').read_text())
    study=json.loads((ROOT/'study.json').read_text())
    check_dataset(dataset)
    assert sum(D(v) for v in rules['weights'].values())==1
    assert D(rules['category_weight'])*4==1
    print('12 intenções x 7 IDs = 84 respostas previstas; concorrência 2; sem retries automáticos (recuperações documentadas à parte).',flush=True)
    if not args.execute:
        print('Dry run: nenhuma inferência.');return
    assert args.budget_total_usd and args.budget_total_usd>D(study['baseline_cost_usd'])
    base=os.environ['OCI_BASE_URL'].rstrip('/')
    assert base=='https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/v1'
    headers={'Authorization':'Bearer '+os.environ['OCI_API_KEY'],'OpenAI-Project':os.environ['OCI_PROJECT_ID']}
    folder=ROOT.parent/'runs'/args.run_id;folder.mkdir(parents=True,exist_ok=True)
    lock=(folder/'run.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    raw=folder/'raw';raw.mkdir(exist_ok=True)
    manifest={'dataset_sha256':core.digest(dataset),'prices_sha256':core.digest(prices),
              'rules_sha256':core.digest(rules),'study_sha256':core.digest(study),
              'system_sha256':hashlib.sha256(core.SYSTEM.encode()).hexdigest(),
              'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOLO.md').read_bytes()).hexdigest(),
              'models':MODELS,'reference_date':dataset['reference_date'],'concurrency':2,
              'max_output_tokens':2400,'timeout_seconds':150,'retries':0,
              'region':'us-chicago-1','endpoint':'/v1/responses','retrospective':True}
    path=folder/'manifest.json'
    if path.exists():assert json.loads(path.read_text())==manifest,'Manifesto alterado'
    else:path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    log=folder/'events.jsonl'
    events=[json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    rows=read_results(events)
    done={(r['intent_id'],r['model']) for r in rows}
    starts=Counter((e['intent_id'],e['model']) for e in events if e['event']=='started')
    finishes=Counter((e['result']['intent_id'],e['result']['model']) for e in events if e['event']=='finished')
    assert len(done)==len(rows) and starts==finishes,'Chamadas interrompidas ou duplicadas; revisar antes de continuar'
    assert 0<=args.cooldown_seconds<=300
    rejected=[e for e in events if e['event']=='infrastructure_rejected']
    reserve=D('.50')
    def used():return D(study['baseline_cost_usd'])+reserve*len(rejected)+sum(D(r['cost']['total_usd']) if r.get('cost',{}).get('total_usd') is not None else reserve for r in rows)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for index,intent in enumerate(dataset['intents'][:args.intent_limit]):
            # Rotação reduz associação entre identificador e posição de envio.
            rotated=MODELS[index%7:]+MODELS[:index%7]
            pending=[m for m in rotated if (intent['id'],m) not in done]
            if not pending:continue
            if used()+reserve*len(pending)>args.budget_total_usd:
                print('STOP: limite acumulado, sem reserva para o próximo grupo.',flush=True);break
            if any(e['event']=='finished' for e in events) and args.cooldown_seconds:
                print(f'Controle de taxa: pausa de {args.cooldown_seconds}s antes do grupo {intent["id"]}.',flush=True)
                remaining=args.cooldown_seconds
                while remaining:
                    step=min(15,remaining);time.sleep(step);remaining-=step
            futures=[]
            for model in pending:
                key=(intent['id'],model)
                assert starts[key]<2,'Recuperação limitada a uma repetição após 429 documentado'
                if starts[key]:
                    assert any(e['intent_id']==intent['id'] and e['model']==model for e in rejected),'Repetição sem rejeição infra documentada'
                starts[key]+=1

                core.append_event(log,{'event':'started','intent_id':intent['id'],'model':model,'at':datetime.now(timezone.utc).isoformat()})
                futures.append(pool.submit(invoke,model,intent,base,headers,prices,raw))
            stop=False
            for future in futures:
                row=future.result();rows.append(row);done.add((row['intent_id'],row['model']))
                core.append_event(log,{'event':'finished','result':row})
                events.append({'event':'finished','result':row})
                print(f"{len(rows)}/84 {row['intent_id']} {row['model']} HTTP={row.get('http')} confiável={row['reliable_search']} USD={row['cost'].get('total_usd','unknown')}",flush=True)
                stop|=row.get('http')!=200 or row.get('cost',{}).get('total_usd') is None
            if stop:
                print('STOP: diagnóstico necessário; não haverá repetição automática.',flush=True);break
    total=sum(D(r['cost']['total_usd']) for r in rows if r.get('cost',{}).get('total_usd') is not None)
    print(f'Concluídas={len(rows)}/84; custo conhecido US$ {total}; histórico acumulado conhecido US$ {D(study["baseline_cost_usd"])+total}',flush=True)

if __name__=='__main__':main()
