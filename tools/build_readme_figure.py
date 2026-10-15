"""Build the editable, dependency-free SVG for the project homepage."""
from pathlib import Path
from html import escape

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/figures/how_it_works.svg'
CARDS=[
    ('01','Regulatory source',['Clause + dated excerpt','Official source link','Stored text fingerprint']),
    ('02','Reviewed record',['Requirement + scope','Trigger + evidence','Author-reviewed fields']),
    ('03','AI audit proposal',['Retrieve record IDs','One constrained model call','Return labels + citations']),
    ('04','Human verification',['Check applicability','Inspect workplace evidence','Make the final judgment']),
]

def main():
    parts=['''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300" role="img" aria-labelledby="title desc">
<title id="title">From regulatory source to human-reviewed audit proposal</title>
<desc id="desc">Four stages: official source, author-reviewed regulatory record, retrieved and cited AI proposal, and human verification of applicability, workplace evidence and final judgment.</desc>
<rect width="1200" height="300" fill="#ffffff"/>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#414b56"/></marker></defs>
<g font-family="Arial, Helvetica, sans-serif" fill="#18212b">''']
    for index,(number,title,lines) in enumerate(CARDS):
        x=16+302*index
        parts.append(f'<g id="stage-{index+1}"><rect x="{x}" y="16" width="262" height="190" rx="5" fill="#fff" stroke="#8a939d" stroke-width="1.5"/>')
        parts.append(f'<text x="{x+18}" y="44" font-size="16" fill="#66717d">{number}</text>')
        parts.append(f'<text x="{x+18}" y="77" font-size="23" font-weight="700">{escape(title)}</text>')
        parts.append(f'<path d="M{x+18} 94H{x+244}" stroke="#d3d8de"/>')
        for row,line in enumerate(lines):parts.append(f'<text x="{x+18}" y="{123+29*row}" font-size="18">{escape(line)}</text>')
        parts.append('</g>')
        if index<3:parts.append(f'<path d="M{x+270} 111H{x+292}" fill="none" stroke="#414b56" stroke-width="2" marker-end="url(#arrow)"/>')
    parts.extend(['''<rect x="16" y="226" width="1168" height="58" rx="5" fill="#f2f4f6"/>
<text x="600" y="250" text-anchor="middle" font-size="18" font-weight="700">AI output is a proposal, not proof that a workplace complies.</text>
<text x="600" y="273" text-anchor="middle" font-size="17" fill="#46525f">Source review happens during curation; site-specific verification remains a human task.</text>
</g></svg>'''])
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8')
    print('Built docs/figures/how_it_works.svg')

if __name__=='__main__':main()
