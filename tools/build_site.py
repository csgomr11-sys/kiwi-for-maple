"""Build a static website; no Python server dependencies needed at runtime."""
from pathlib import Path
import json, shutil
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'site'
def write(path,obj):
    p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def main():
    OUT.mkdir(exist_ok=True)
    for p in (ROOT/'web').rglob('*'):
        if p.is_file():
            target=OUT/p.relative_to(ROOT/'web');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    counts={}
    for kind in ['monsters','items','quests','maps','skills']:
        dataset=json.loads((ROOT/f'data/catalog/{kind}.json').read_text());rows=dataset[kind];counts[kind]=len(rows)
        keys={'monsters':['id','name','level','stats','image','continents','onlyUnnamedMaps','elemental'],
              'items':['id','name','category','subcategory','image','equipStats','hasSource','sourceCounts'],
              'quests':['id','name','minLevel','maxLevel','category','parent','startNpc','endNpc','startRequirements','completeRequirements','startRewards','completeRewards'],
              'maps':['id','name','street','regionName','specialMap','monsterSpawnCount','npcSpawnCount','portalCount','miniMapImage'],
              'skills':['id','name','jobId','jobName','jobGroup','advancement','maxLevel','image']}[kind]
        index=[{k:r.get(k) for k in keys} for r in rows]
        if kind=='monsters':
            for source,row in zip(rows,index):
                row['dropCount']=len(source.get('drops',[]))
                row['dropNames']=[x.get('name','') for x in source.get('drops',[])]
                row['mapNames']=[x.get('name','') for x in source.get('maps',[]) if not x.get('unnamed')]
                row['searchTerms']=' '.join(x.get('name','') for x in source.get('drops',[])+source.get('maps',[]))
        if kind=='quests':
            def compact_req(v):
                v=v or {};return {k:v.get(k) for k in ['minLevel','maxLevel','jobs','pop','items','monsters','skills']} | {'quests':[{k:q.get(k) for k in ['id','name','state','stateLabel']} for q in v.get('quests',[])]}
            for r in index:
                for k in ['startRequirements','completeRequirements']:r[k]=compact_req(r[k])
                for k in ['startNpc','endNpc']:
                    r[k]={a:r[k].get(a) for a in ['id','name','locationText']} if r[k] else None
        write(Path('data')/(kind+'.json'),index)
        buckets={}
        for r in rows:buckets.setdefault(str(int(r['id'])//1000),{})[str(r['id'])]=r
        for bucket,b in buckets.items():write(Path('data')/(kind+'-detail')/(bucket+'.json'),b)
    for p in (ROOT/'data/catalog').glob('*.json'):
        if p.stem not in counts:shutil.copy2(p,OUT/'data'/p.name)
    write(Path('data/counts.json'),counts)
    shutil.copy2(ROOT/'data/guides.json',OUT/'data/guides.json')
    for p in ['RESEARCH.md','REFERENCES.md','data/SOURCES.md']:
        shutil.copy2(ROOT/p,OUT/Path(p).name)
    print('Built',OUT,counts)
if __name__=='__main__':main()
