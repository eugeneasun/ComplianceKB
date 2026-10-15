"""Recompute reported statistics from saved artifacts; never calls model APIs."""
from pathlib import Path
from collections import Counter
import csv,importlib.util,json,math,os,random,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
BENCH=ROOT/'research/benchmark'
sys.path.insert(0,str(BENCH))
from evaluate_benchmark import parse_set,retrieval_scores

def run(*arguments):
    env={**os.environ,'PYTHONIOENCODING':'utf-8','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'}
    p=subprocess.run([sys.executable,*arguments],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8')
    if p.returncode:raise RuntimeError(p.stdout+'\n'+p.stderr)
    print(p.stdout[-1800:].strip() if len(p.stdout)<2000 else 'PASS: '+arguments[0])

def close(actual,expected,where=''):
    if isinstance(expected,dict):
        for key,value in expected.items():close(actual[key],value,where+'/'+key)
    elif isinstance(expected,list):
        assert len(actual)==len(expected),where
        for i,(a,b) in enumerate(zip(actual,expected)):close(a,b,where+'/'+str(i))
    elif isinstance(expected,(int,float)):
        assert math.isclose(actual,expected,rel_tol=1e-10,abs_tol=1e-12),(where,actual,expected)
    else:assert actual==expected,(where,actual,expected)

def kappa(a,b):
    n=len(a);observed=sum(x==y for x,y in zip(a,b))/n
    ca,cb=Counter(a),Counter(b)
    chance=sum(ca[k]*cb[k] for k in set(a)|set(b))/(n*n)
    return math.nan if chance==1 else (observed-chance)/(1-chance)

def annotation():
    with (ROOT/'research/annotation/paired_labels.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==len({r['id'] for r in rows})==50
    expected=json.loads((ROOT/'research/annotation/reported_results.json').read_text(encoding='utf-8'))
    result={}
    for field in expected['fields']:
        a=[r['annotator_1_'+field] for r in rows];b=[r['annotator_2_'+field] for r in rows]
        agreements=sum(x==y for x,y in zip(a,b))
        score=kappa(a,b)
        rng=random.Random(20260928);scores=[]
        for _ in range(10000):
            indices=[rng.randrange(50) for _ in range(50)]
            value=kappa([a[i] for i in indices],[b[i] for i in indices])
            if not math.isnan(value):scores.append(value)
        scores.sort()
        def pct(p):
            x=(len(scores)-1)*p;i=int(x);j=min(i+1,len(scores)-1)
            return scores[i]*(1-(x-i))+scores[j]*(x-i)
        interval=[pct(.025),pct(.975)]
        target=expected['results'][field]
        close(score,target['cohen_kappa'],field)
        close(agreements,target['agreements'],field)
        close(interval,target['bootstrap_95ci'],field)
        result[field]={'kappa':score,'agreements':agreements,'bootstrap_95ci':interval}
    return result

def retrieval():
    with (BENCH/'scenarios_HUMAN_CONFIRMED_DEVELOPMENT.csv').open(encoding='utf-8-sig',newline='') as f:
        gold={r['scenario_id']:parse_set(r['gold_requirement_ids']) for r in csv.DictReader(f)}
    result={}
    for dirname,names in [('retrieval_provisional',['bm25','dense','hybrid']),('retrieval_e5_posthoc_20260930',['e5','bm25_e5_rrf'])]:
        for name in names:
            rows=[json.loads(line) for line in (BENCH/'runs'/dirname/(name+'_predictions.jsonl')).read_text(encoding='utf-8').splitlines()]
            assert len(rows)==24 and {r['scenario_id'] for r in rows}==set(gold)
            values=[retrieval_scores(gold[r['scenario_id']],r['ranked_requirement_ids'],10) for r in rows]
            result[name]=dict(zip(['recall','mrr','ndcg'],[sum(v[i] for v in values)/len(values) for i in range(3)]))
    saved=json.loads((BENCH/'runs/retrieval_e5_posthoc_20260930/manifest.json').read_text(encoding='utf-8'))['summary']
    for name in saved:close(result[name],saved[name],name)
    return result

def main():
    output=ROOT/'generated';output.mkdir(exist_ok=True)
    run('tools/check_release.py')
    for release in ['v1.2.0','v1.3.0','v1.4.0','v1.5.0']:
        run('tests/test_full_dataset.py','--release',release)
        run('tests/test_release_exports.py','--release',release)
    for name in ['test_benchmark_metrics.py','test_bm25_baseline.py','test_llm_benchmark.py','test_completed_llm_run.py']:
        run('tests/'+name)
    run('research/benchmark/validate_scenarios.py','research/benchmark/scenarios_HUMAN_CONFIRMED_DEVELOPMENT.csv')
    run('research/benchmark/aggregate_llm_results.py','--output-dir',str(output/'llm_analysis'))
    actual=json.loads((output/'llm_analysis/development_metrics.json').read_text(encoding='utf-8'))
    expected=json.loads((BENCH/'runs/llm_development_20260927/analysis/development_metrics.json').read_text(encoding='utf-8'))
    close(actual,expected,'development_metrics')
    result={'llm_metrics_exactly_reproduced':True,'retrieval':retrieval(),'annotation':annotation(),
            'scope':'Offline rescoring of frozen artifacts; no live model calls or embedding reruns.'}
    (output/'reproduction_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
