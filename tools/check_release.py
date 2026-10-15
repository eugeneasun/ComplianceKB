"""Check release integrity and additive version history, using only the stdlib."""
from pathlib import Path
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]
COUNTS={'v1.2.0':108,'v1.3.0':113,'v1.4.0':131,'v1.5.0':133}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest=ROOT/'RELEASE_MANIFEST.sha256'
    if not manifest.exists():raise SystemExit('Missing curated-release manifest')
    entries=0
    for line in manifest.read_text(encoding='utf-8').splitlines():
        expected,relative=line.split('  ',1)
        path=ROOT/relative
        assert path.is_file(),relative
        assert digest(path)==expected,relative
        entries+=1
    previous={}
    for version,count in COUNTS.items():
        directory=ROOT/'data/releases'/version
        data=json.loads((directory/'all_requirements.json').read_text(encoding='utf-8'))
        records={r['id']:r for r in data['requirements']}
        assert len(records)==len(data['requirements'])==count,(version,count)
        for identifier,record in previous.items():
            assert records[identifier]==record,(version,identifier,'earlier record changed')
        for record in records.values():
            source=record['provenance']
            text=source['source_text_excerpt'].lower().strip()
            text=re.sub(r'\s+',' ',text)
            text=re.sub(r'[^\w\s§.()\-]','',text)
            assert hashlib.sha256(text.encode('utf-8')).hexdigest()==source['source_text_hash'],record['id']
        for line in (directory/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
            expected,name=line.split('  ',1)
            assert digest(directory/name)==expected,(version,name)
        previous=records
        print(f'PASS: {version}: {count} unique records, source hashes and unchanged earlier records')
    print(f'PASS: {entries} curated files match RELEASE_MANIFEST.sha256')

if __name__=='__main__':main()
