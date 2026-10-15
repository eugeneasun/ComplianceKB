"""Post-hoc, retrieval-only E5 and BM25/E5 sensitivity; preserves original run."""
import csv
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import torch
from sentence_transformers import SentenceTransformer
from bm25_baseline import BM25Index, record_text
from hybrid_baseline import reciprocal_rank_fusion
from evaluate_benchmark import parse_set, retrieval_scores

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MODEL='intfloat/e5-base-v2'
REVISION='f52bf8ec8c7124536f0efb74aca902b2995e5bcd'

def main():
    torch.set_num_threads(4)
    torch.manual_seed(20260930)
    dataset_path=ROOT/'data/releases/v1.2.0/all_requirements.json'
    scenario_path=HERE/'scenarios_HUMAN_CONFIRMED_DEVELOPMENT.csv'
    records=json.loads(dataset_path.read_text(encoding='utf-8'))['requirements']
    with scenario_path.open(encoding='utf-8-sig',newline='') as f:scenarios=list(csv.DictReader(f))
    sha=REVISION
    print('Loading',MODEL,'revision',sha,flush=True)
    model=SentenceTransformer(MODEL,revision=sha,device='cpu',cache_folder=str(ROOT/'tmp/model_cache'))
    model.max_seq_length=512
    docs=[(r['id'],record_text(r,['requirement_text','source_text_excerpt'])) for r in records]
    passages=['passage: '+x[1] for x in docs]
    queries=['query: '+s['scenario_text']+'\n'+s['organization_context'] for s in scenarios]
    truncated=sum(len(model.tokenizer(p,add_special_tokens=True,truncation=False)['input_ids'])>512 for p in passages)
    embeddings=model.encode(passages,batch_size=8,normalize_embeddings=True,show_progress_bar=False)
    qemb=model.encode(queries,batch_size=8,normalize_embeddings=True,show_progress_bar=False)
    bm=BM25Index(docs,1.5,.75)
    results={'e5':[],'bm25_e5_rrf':[]}
    metrics={name:[] for name in results}
    for s,q in zip(scenarios,qemb):
        scores=embeddings@q
        order=sorted(range(len(docs)),key=lambda i:(-float(scores[i]),docs[i][0]))[:20]
        dense=[{'id':docs[i][0],'rank':rank,'score':float(scores[i])} for rank,i in enumerate(order,1)]
        lexical=bm.search(s['scenario_text']+'\n'+s['organization_context'],20)
        fused=reciprocal_rank_fusion([lexical,dense],60)[:10]
        for name,items in [('e5',dense[:10]),('bm25_e5_rrf',fused)]:
            ids=[x['id'] for x in items]
            results[name].append({'scenario_id':s['scenario_id'],'ranked_requirement_ids':ids,'scores':items})
            metrics[name].append(retrieval_scores(parse_set(s['gold_requirement_ids']),ids,10))
    summary={name:dict(zip(['recall','mrr','ndcg'],[sum(x[i] for x in vals)/len(vals) for i in range(3)])) for name,vals in metrics.items()}
    out=HERE/'runs/retrieval_e5_posthoc_20260930'
    out.mkdir(parents=True,exist_ok=True)
    for name,rows in results.items():
        (out/(name+'_predictions.jsonl')).write_text(''.join(json.dumps(x)+'\n' for x in rows),encoding='utf-8')
    manifest={'status':'POST_HOC_RETRIEVAL_ONLY_SENSITIVITY_NO_LLM_RERUN','model':MODEL,'revision':sha,'seed':20260930,'device':'cpu','threads':4,'batch_size':8,'max_sequence_length':512,'prefixes':['query: ','passage: '],'normalization':'L2','similarity':'dot product','truncated_documents':truncated,'top_k':10,'component_k':20,'rrf_k':60,'bm25':{'k1':1.5,'b':.75},'n':len(scenarios),'python':platform.python_version(),'versions':{x:importlib.metadata.version(x) for x in ['torch','sentence-transformers','transformers','numpy','huggingface-hub']},'scenario_sha256':hashlib.sha256(scenario_path.read_bytes()).hexdigest(),'dataset_sha256':hashlib.sha256(dataset_path.read_bytes()).hexdigest(),'summary':summary}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,indent=2),flush=True)

if __name__=='__main__':main()
