"""Consolidar histórico original + auditoria, sem inferência e sem dupla contagem."""
from pathlib import Path
from decimal import Decimal
import hashlib
import json

ROOT=Path(__file__).resolve().parent
D=lambda value:Decimal(str(value))
INTS=['interactions','input_tokens','cached_input_tokens','output_tokens','reasoning_tokens','total_tokens','web_search_calls']
MONEY=['input_usd','cached_input_usd','output_usd','web_search_usd','total_usd']

def aggregate(values):
    row={key:int(sum(D(v[key]) for v in values)) for key in INTS}
    row.update({key:str(sum(D(v[key]) for v in values)) for key in MONEY})
    row['mean_usd']=str(D(row['total_usd'])/row['interactions'])
    return row

def main():
    baseline_path=ROOT.parent/'financial-consolidation.json'
    baseline=json.loads(baseline_path.read_text());study=json.loads((ROOT/'study.json').read_text())
    assert baseline['total']['interactions']==210
    assert hashlib.sha256(baseline_path.read_bytes()).hexdigest()==study['baseline_financial_sha256']
    source=ROOT/'results/screening-2026-10-15-v1';rows=json.loads((source/'measured-usage.json').read_text())
    assert len(rows)==84 and len({(r['model'],r['intent_id']) for r in rows})==84
    records=[]
    for row in rows:
        c=row['cost'];assert c.get('total_usd') is not None
        record={'model':row['model'],'interactions':1,'total_tokens':c['input_tokens']+c['output_tokens'],
                **{key:c[key] for key in INTS if key not in ['interactions','total_tokens']},
                **{key:c[key] for key in MONEY}}
        assert D(c['total_usd'])==sum(D(c[key]) for key in MONEY if key!='total_usd')
        records.append(record)
    summary=json.loads((source/'summary.json').read_text())
    stage=aggregate(records)
    total=aggregate([baseline['total'],stage])
    by_model={model:aggregate([previous]+[r for r in records if r['model']==model]) for model,previous in baseline['by_model'].items()}
    assert total['interactions']==294
    for key in INTS+MONEY:assert sum(D(row[key]) for row in by_model.values())==D(total[key])
    report={'scope':'294 interações com custo conhecido: histórico original de 210 + auditoria retrospectiva de 84. As etapas são diferentes e não formam uma amostra única para ranking.',
            'valuation_date':'2026-10-15','currency':'USD','pricing_basis':'Uso medido a preços de lista Oracle; não é fatura conciliada. Faixas de contexto longo resolvidas conforme adendo.',
            'sources':{'baseline':'../financial-consolidation.json','screening':'results/screening-2026-10-15-v1/measured-usage.json','pricing':'oracle-prices.json','accounting_addendum':'ADENDO-CONTABILIDADE.md'},
            'source_sha256':{'baseline':hashlib.sha256(baseline_path.read_bytes()).hexdigest(),'screening':hashlib.sha256((source/'measured-usage.json').read_bytes()).hexdigest()},
            'screening_http_attempts':summary['http_attempts'],
            'screening_infrastructure_rejections_without_usage':summary['unknown_cost_infrastructure_attempts'],
            'unknown_cost_note':'Rejeições sem usage não foram valoradas como zero; estão fora do total conhecido.',
            'total':total,'by_stage':{**baseline['by_stage'],'retrospective_screening':stage},'by_model':by_model}
    (ROOT/'financial-consolidation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Chamadas:',total['interactions'],'Custo acumulado USD:',total['total_usd'])

if __name__=='__main__':main()
