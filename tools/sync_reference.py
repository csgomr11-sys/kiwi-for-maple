from source_policy import approved_open, require_allowed
"""Import factual tables from the user-selected reference, never execute remote JS.

UI code and guide prose are not copied. Asset URLs remain links to the source.
"""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import urllib.request
ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://morrisrrrrrrr-svg.github.io/'
NAMES = ['monsters','items','quests','maps','skills','damage-calculator','combat-analysis','scroll-simulator','gacha-simulator','third-job','goddess-tower','exp-exchange','skill-changes','halloween','avatar-maker']
DROP = {'description','desc','areaDesc','dialogues','texts','textRefs','raw','html','journal','scene','scripts','steps','search','formula','textChanges','evidence','referenceEvidence','sourceNotice','note','text','summaryText'}
def clean(x):
    if isinstance(x,list):return [clean(v) for v in x]
    if not isinstance(x,dict):return x
    return {k:clean(v) for k,v in x.items() if k not in DROP}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cache-dir',type=Path);args=parser.parse_args()
    cache=ROOT/'.cache/reference';cache.mkdir(parents=True,exist_ok=True)
    out=ROOT/'data/catalog';out.mkdir(parents=True,exist_ok=True)
    manifest={'source':BASE,'retrievedAt':datetime.now(timezone.utc).isoformat(),'datasets':{}}
    staged={}
    for n in NAMES:
        url=BASE+('data.js' if n=='monsters' else n+'-data.js')
        local=args.cache_dir/('reference-data.json' if n=='monsters' else 'ref-'+n+'.json') if args.cache_dir else None
        if local and local.exists():
            raw=local.read_bytes();d=json.loads(raw);kind='parsed-json-cache'
        else:
            with approved_open(urllib.request.Request(url,headers={'User-Agent':'KiwiMapleResearch/0.1'}),timeout=60) as r:raw=r.read(100000001)
            if len(raw)>100000000:raise ValueError('Unexpected oversized response')
            js=raw.decode('utf-8-sig');prefix,value=js.split('=',1)
            if not prefix.strip().startswith('window.'):raise ValueError('Unsupported data wrapper')
            d,end=json.JSONDecoder().raw_decode(value.lstrip())
            if value.lstrip()[end:].strip() not in ['',';']:raise ValueError('Unexpected executable suffix')
            kind='javascript-response'
        (cache/(n+'.raw')).write_bytes(raw)
        normalized=clean(d)
        # Preserve only counts, not copied editorial source notices in the summary.
        if isinstance(normalized.get('summary'),dict):normalized['summary']={k:v for k,v in normalized['summary'].items() if isinstance(v,(int,float))}
        if n=='third-job':
            for q in normalized['questions']:q.pop('question',None)
        staged[n]=json.dumps(normalized,ensure_ascii=False,separators=(',',':'))
        manifest['datasets'][n]={'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'hashOf':kind,'version':d.get('metadata',{}).get('gameVersion') or d.get('gameVersion'), 'bytes':len(raw)}
        print(n,len(staged[n].encode()),flush=True)
    for n,body in staged.items():(out/(n+'.json')).write_text(body,encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
