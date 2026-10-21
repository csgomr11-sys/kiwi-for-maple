"""Cache visible game thumbnails with normal TLS validation; no source UI assets."""
import concurrent.futures,json,urllib.request
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1];BASE='https://morrisrrrrrrr-svg.github.io/'
paths=set()
for kind in ['monsters','skills','items']:
    rows=json.loads((ROOT/f'data/catalog/{kind}.json').read_text())[kind]
    if kind=='items':rows=rows[:36]+[r for r in rows if str(r['id']) in ['4000035','4003000','4003001']]
    paths.update(r['image'].split('?')[0].removeprefix('./') for r in rows if r.get('image'))
paths.add('assets/monster_frames/210100.png')
def fetch(p):
    if not p.startswith('assets/') or '..' in Path(p).parts:return p,False
    out=ROOT/'web'/p
    if out.exists():return p,True
    try:
        with urllib.request.urlopen(BASE+p,timeout=20) as r:body=r.read(2000000)
        if not body.startswith(b'\x89PNG\r\n\x1a\n'):return p,False
        out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(body);return p,True
    except Exception:return p,False
results=list(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(fetch,sorted(paths)))
good=[p for p,ok in results if ok];(ROOT/'web/assets/manifest.json').write_text(json.dumps(good))
print('Cached',len(good),'of',len(paths),'thumbnails; failures',[p for p,ok in results if not ok][:10])
