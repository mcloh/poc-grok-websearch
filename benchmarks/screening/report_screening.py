"""Pontuação congelada e relatório retrospectivo, sem inferência adicional."""
import argparse
from collections import Counter
from decimal import Decimal
import csv
import copy
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from run_screening import MODELS, read_results
D=lambda value:Decimal(str(value))

def config(model):return model.removeprefix('xai.').replace('-0309','')

def metrics(rows):
    known=[r for r in rows if r.get('cost',{}).get('total_usd') is not None]
    n=len(rows)
    def total(key):return sum((D(r['cost'][key]) for r in known if r['cost'].get(key) is not None),D(0))
    return {'interactions':n,'known_costs':len(known),'reliable_searches':sum(r.get('reliable_search',False) for r in rows),
            'total_usd':str(total('total_usd')),'mean_usd':str(total('total_usd')/n) if n and len(known)==n else None,
            **{k:str(total(k)) for k in ['input_usd','cached_input_usd','output_usd','web_search_usd']},
            **{k:int(total(k)) for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens','web_search_calls']},
            'mean_total_tokens':str((total('input_tokens')+total('output_tokens'))/n) if n else None,
            'median_seconds':statistics.median(r['seconds'] for r in rows) if n else None}

def score(rows,dataset,rules):
    index={(r['model'],r['intent_id']):r for r in rows}
    assert len(index)==len(rows)==84
    per_model={}
    for intent in dataset['intents']:
        group=[index[(model,intent['id'])] for model in MODELS]
        reliable=[r for r in group if r['reliable_search']]
        best_cost=min((D(r['cost']['total_usd']) for r in reliable),default=None)
        best_time=min((D(r['seconds']) for r in reliable),default=None)
        assert len({r['shared_payload_sha256'] for r in group})==1
        for row in group:
            ok=row['reliable_search']
            amount=D(row['cost']['total_usd']) if row['cost'].get('total_usd') is not None else None
            cost=(D(1) if amount==0 else best_cost/amount) if ok else D(0)
            latency=(D(1) if D(row['seconds'])==0 else best_time/D(row['seconds'])) if ok else D(0)
            rel=D(1) if ok else D(0)
            w=rules['weights']
            row['score_components']={'cost':float(cost*100),'search_reliability':float(rel*100),'latency':float(latency*100)}
            row['operational_score']=float(100*(D(w['cost'])*cost+D(w['search_reliability'])*rel+D(w['latency'])*latency))
    for model in MODELS:
        selected=[r for r in rows if r['model']==model]
        by_category={c:statistics.mean(r['operational_score'] for r in selected if r['category']==c)
                     for c in ['culinaria','esportes','clima','entretenimento']}
        value=sum(by_category.values())*rules['category_weight']
        stat=metrics(selected)
        gate=stat['known_costs']==rules['required_known_costs'] and stat['reliable_searches']>=rules['minimum_confirmed_searches']
        per_model[model]={'model':model,'configuration':config(model),'score':value,'by_category':by_category,
                          'operational_gate_passed':gate,'passed':gate and value>=rules['cutoff_score'],**stat}
    groups={}
    for name in dict.fromkeys(config(m) for m in MODELS):
        members=[m for m in MODELS if config(m)==name]
        stat=metrics([r for r in rows if r['model'] in members])
        value=statistics.mean(per_model[m]['score'] for m in members)
        gate=all(per_model[m]['operational_gate_passed'] for m in members)
        groups[name]={'configuration':name,'members':members,'score':value,
                      'operational_gate_passed':gate,'passed':gate and value>=rules['cutoff_score'],**stat}
    sortkey=lambda g:(-g['score'],D(g['mean_usd']) if g['mean_usd'] is not None else D('Infinity'),g['median_seconds'],g['configuration'])
    ranked=sorted(groups.values(),key=sortkey)
    selected=[g['configuration'] for g in ranked if g['passed']][:2]
    # Reamostrar casos iguais em todos os IDs, mantendo os estratos de três por tema.
    rng=random.Random(20261015);scores={m:[] for m in MODELS};group_scores={g:[] for g in groups};top=Counter()
    strata=[[i['id'] for i in dataset['intents'] if i['category']==c] for c in ['culinaria','esportes','clima','entretenimento']]
    for _ in range(2000):
        sample=[rng.choice(stratum) for stratum in strata for _ in range(3)]
        idscore={m:statistics.mean(index[(m,key)]['operational_score'] for key in sample) for m in MODELS}
        for m in MODELS:scores[m].append(idscore[m])
        candidates=[]
        for name,g in groups.items():
            value=statistics.mean(idscore[m] for m in g['members']);group_scores[name].append(value)
            if g['operational_gate_passed'] and value>=rules['cutoff_score']:
                sampled=[index[(m,key)] for m in g['members'] for key in sample]
                amounts=[D(r['cost']['total_usd']) for r in sampled]
                candidates.append((-value,sum(amounts)/len(amounts),statistics.median(r['seconds'] for r in sampled),name))
        for candidate in sorted(candidates)[:2]:top[candidate[-1]]+=1
    def interval(values):
        a=sorted(values);return [a[math.floor(.025*len(a))],a[math.ceil(.975*len(a))-1]]
    for m in MODELS:per_model[m]['case_bootstrap_95_range']=interval(scores[m])
    for name,g in groups.items():
        g['case_bootstrap_95_range']=interval(group_scores[name]);g['bootstrap_top2_frequency']=top[name]/2000
    return per_model,ranked,selected

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-id',default='screening-2026-10-15-v1');args=parser.parse_args()
    assert all(c.isalnum() or c in '-_' for c in args.run_id)
    source=ROOT.parent/'runs'/args.run_id
    manifest=json.loads((source/'manifest.json').read_text());events=[json.loads(l) for l in (source/'events.jsonl').read_text().splitlines()]
    rows=read_results(events);dataset=json.loads((ROOT/'intents-12.json').read_text());rules=json.loads((ROOT/'scoring-rules.json').read_text())
    assert len({(r['model'],r['intent_id']) for r in rows})==len(rows)
    print(f'{len(rows)}/84 chamadas coletadas')
    if len(rows)!=84:print('Pontuação final não calculada para uma matriz incompleta.');return
    assert hashlib.sha256((ROOT/'PROTOCOLO.md').read_bytes()).hexdigest()==manifest['protocol_sha256']
    models,groups,selected=score(rows,dataset,rules)
    prices=json.loads((ROOT/'oracle-prices.json').read_text())
    no_cache=copy.deepcopy(rows)
    for row in no_cache:
        family='grok-4.20' if row['model'].startswith('xai.grok-4.20-') else row['model'].removeprefix('xai.')
        rate=prices['models'][family]['input_'+row['cost'].get('pricing_band','short')]['usd']
        c=row['cost']
        c['input_usd']=str(D(c['input_tokens'])*D(rate)/D(1000000))
        c['cached_input_usd']='0'
        c['total_usd']=str(sum(D(c[k]) for k in ['input_usd','cached_input_usd','output_usd','web_search_usd']))
    _,no_cache_groups,no_cache_selected=score(no_cache,dataset,rules)
    original={'grok-4.3','grok-4.20-non-reasoning'}
    confirmed=set(selected)==original and len(selected)==2
    report={'retrospective':True,'run_id':args.run_id,'reference_date':dataset['reference_date'],
            'method':'12 prompts idênticos x sete IDs; três por tema; critérios congelados antes das novas inferências; recuperações de rejeições compartilhadas de infraestrutura documentadas à parte',
            'http_attempts':sum(e['event']=='started' for e in events),
            'infrastructure_rejections':sum(e['event']=='infrastructure_rejected' for e in events),
            'unknown_cost_infrastructure_attempts':sum(e['event']=='infrastructure_rejected' for e in events),
            'manifest':manifest,'rules':rules,'total':metrics(rows),'by_model':models,'configurations':groups,
            'selected_configurations':selected,'original_selection_confirmed':confirmed,
            'cache_discount_sensitivity':{'secondary':True,'method':'Mesmos tokens e latências observados; entrada em cache reprecificada como entrada normal, sem novas chamadas. Não simula execução fisicamente sem cache.','selected_configurations':no_cache_selected,'configurations':no_cache_groups},
            'original_selection':['grok-4.3','grok-4.20-non-reasoning'],
            'conclusion':'A amostra confirma os dois candidatos originais segundo a regra operacional congelada.' if confirmed else 'A amostra não confirma os dois candidatos originais como as duas primeiras configurações segundo a regra congelada.',
            'limits':'Nota operacional relativa, sem pontuação factual. Auditoria retrospectiva; 12 casos não permitem inferir o resultado de 100 intenções nos demais modelos.'}
    target=ROOT/'results'/args.run_id;target.mkdir(parents=True,exist_ok=True)
    (target/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    public=[{k:v for k,v in r.items() if k!='provider_response_id'} for r in rows]
    (target/'measured-usage.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
    prompts={r['id']:r['prompt'] for r in dataset['intents']}
    fields=['intent_id','category','model','http','reliable_search','truncated','final_answer_chars','seconds','input_tokens','cached_input_tokens','output_tokens','reasoning_tokens','web_search_calls','input_usd','cached_input_usd','output_usd','web_search_usd','total_usd','cost_score','search_score','latency_score','operational_score','prompt_sha256','shared_payload_sha256','prompt']
    with (target/'interactions.csv').open('w') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields,lineterminator='\n');writer.writeheader()
        for row in rows:
            flat={**row,**row['cost'],'cost_score':row['score_components']['cost'],
                  'search_score':row['score_components']['search_reliability'],'latency_score':row['score_components']['latency'],'prompt':prompts[row['intent_id']]}
            writer.writerow({key:flat.get(key) for key in fields})
    fmt=lambda v:f'{float(v):.4f}'
    lines=['# Pré-teste retrospectivo — 12 consultas por identificador', '',
           '**'+report['conclusion']+'**', '',
           f"84 novas respostas avaliadas; {report['http_attempts']} tentativas HTTP, das quais {report['infrastructure_rejections']} rejeitadas por infraestrutura; custo conhecido US$ {report['total']['total_usd']}; buscas operacionais confiáveis {report['total']['reliable_searches']}/84.", '',
           'A seleção original antecedeu este teste. Esta etapa é uma auditoria posterior e não reescreve a cronologia.', '',
           '## Classificação por identificador', '',
           '| ID OCI | Nota /100 | Busca confiável | Gate operacional | Corte >=70 | USD/interação | Tokens/interação | Mediana s | Faixa bootstrap das notas |',
           '|---|---:|---:|---|---|---:|---:|---:|---|']
    for row in sorted(models.values(),key=lambda r:-r['score']):
        lo,hi=row['case_bootstrap_95_range'];lines.append(f"| `{row['model']}` | {fmt(row['score'])} | {row['reliable_searches']}/12 | {row['operational_gate_passed']} | {row['passed']} | {fmt(row['mean_usd']) if row['mean_usd'] is not None else 'unknown'} | {float(row['mean_total_tokens']):.2f} | {row['median_seconds']:.3f} | {lo:.2f}–{hi:.2f} |")
    lines+=['','## Corte por configuração, com aliases agrupados', '',
            '| Configuração | IDs agrupados | Nota /100 | Aprovada | Selecionada | Frequência top 2 no bootstrap |', '|---|---:|---:|---|---|---:|']
    for row in groups:
        lines.append(f"| `{row['configuration']}` | {len(row['members'])} | {fmt(row['score'])} | {row['passed']} | {row['configuration'] in selected} | {row['bootstrap_top2_frequency']:.1%} |")
    lines+=['','## Sensibilidade ao desconto de cache', '',
            'Análise secundária e exploratória, sem alterar a seleção principal. Nos mesmos registros, cobrar toda a entrada pela tarifa sem cache e reaplicar os mesmos pesos. Selecionadas nesse cenário contábil: '+', '.join('`'+v+'`' for v in no_cache_selected)+'. Não é uma simulação física de serviço sem cache.', '',
            'A amostra não é holdout: os dois candidatos originais já receberam esses prompts no lote anterior. O cache da API não foi controlado. A sensibilidade apenas verifica a contribuição do desconto financeiro, mantendo tokens e tempos observados.', '',
            '## Interpretação dos aliases', '',
            'A nota agrupada é a média dos IDs da configuração. As duas versões de alias não ocupam vagas separadas. O gate operacional exige 12 custos conhecidos e ao menos 11 buscas confiáveis por ID; o corte de 70 aplica-se à nota da configuração.', '',
            '## Regra e limites', '',
            '- Pesos: 50% custo total, 30% busca operacional confiável e 20% latência; 25% por tema, com três consultas cada.',
            '- Eficiência de custo e tempo normalizada pela melhor resposta confiável da mesma intenção. Uma resposta não confiável recebe zero nos três componentes.',
            '- Busca confiável requer HTTP 200, custo conhecido, search completed, fontes, citações, texto final não vazio e ausência de sinal de truncamento. Não é avaliação factual.',
            '- Faixa bootstrap: sensibilidade descritiva aos casos em 2000 reamostragens estratificadas e pareadas. Não é intervalo de confiança populacional e não mede repetições independentes da mesma pergunta.',
            '- Gates de custo e confiabilidade ficam fixos na reamostragem; o corte de 70 é reaplicado às notas de cada reamostragem.',
            '- As 84 respostas avaliadas são novas; nenhuma resposta do lote original de 200 foi reutilizada como execução deste pré-teste.',
            '- As rejeições compartilhadas por HTTP 429 foram preservadas e recuperadas uma vez após controle de taxa; não foram computadas como custo zero ou como falha de um modelo. Veja o [adendo operacional](../../ADENDO-TAXA.md).',
            '- O contador financeiro cobre respostas com usage; o custo das rejeições sem usage permanece desconhecido e não integra as médias nem o custo conhecido publicado.',
            '- O limite de 2400 tokens de saída e os defaults do modelo são iguais aos do experimento. Truncamentos são penalizados; isso avalia esta configuração operacional, não a capacidade máxima de cada modelo.',
            '- Custos calculados a preço de lista Oracle incluem tokens e websearch; não são fatura conciliada.',
            '- O caso de contexto longo foi conciliado sem repetir a inferência; a memória de cálculo consta no [adendo de contabilidade](../../ADENDO-CONTABILIDADE.md).',
            '- O parâmetro max_output_tokens=2400 não limitou o uso agregado de saída do loop a 2400 em todas as respostas. Os custos usam o usage total retornado, incluindo etapas internas.', '',
            '## Evidências', '',
            '- [Protocolo anterior às novas chamadas](../../PROTOCOLO.md).',
            '- [Dataset de 12 intenções](../../intents-12.json), [regras de corte](../../scoring-rules.json) e [sensibilidade de cache](../../SENSIBILIDADES.md).',
            '- [CSV das 84 interações](interactions.csv), [métricas medidas](measured-usage.json) e [resumo com bootstrap](summary.json).', '']
    (target/'REPORT.md').write_text('\n'.join(lines))
    (target/'sha256.json').write_text(json.dumps({name:hashlib.sha256((target/name).read_bytes()).hexdigest() for name in ['summary.json','measured-usage.json','interactions.csv','REPORT.md']},indent=2)+'\n')
    print(report['conclusion']);print('Selecionadas:',selected);print('Custo novo USD:',report['total']['total_usd'])

if __name__=='__main__':main()
