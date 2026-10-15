"""Show actual BM25 retrieval and source-linked audit fields; no model call."""
from pathlib import Path
import argparse,json,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'research/benchmark'))
from bm25_baseline import BM25Index,record_text

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query',default='employee training records')
    parser.add_argument('--release',choices=['v1.2.0','v1.3.0','v1.4.0','v1.5.0'],default='v1.2.0')
    parser.add_argument('--top-k',type=int,default=3)
    args=parser.parse_args()
    data=json.loads((ROOT/'data/releases'/args.release/'all_requirements.json').read_text(encoding='utf-8'))
    records={r['id']:r for r in data['requirements']}
    index=BM25Index([(r['id'],record_text(r,['requirement_text','source_text_excerpt'])) for r in records.values()],1.5,.75)
    print('Retrieval demonstration only: these are records to inspect, not a compliance decision.')
    for hit in index.search(args.query,args.top_k):
        r=records[hit['id']]
        print(json.dumps({'id':r['id'],'retrieval_score':hit['score'],
            'requirement_text':r['requirement_text'],'workflow_trigger':r['workflow_trigger'],
            'audit_evidence_type':r['audit_evidence_type'],
            'source_clause':r['provenance']['source_clause'],'source_url':r['provenance']['source_url']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
