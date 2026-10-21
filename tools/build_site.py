"""Build a static website; no Python server dependencies needed at runtime."""
from pathlib import Path
import json, shutil
from version_scope import project
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'site'
def write(path,obj):
    p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def main():
    OUT.mkdir(exist_ok=True)
    for p in (ROOT/'web').rglob('*'):
        if p.is_file():
            target=OUT/p.relative_to(ROOT/'web');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    # Rebuild data from scratch so previously published quarantined details disappear.
    if (OUT/'data').exists():shutil.rmtree(OUT/'data')
    catalogs={kind:json.loads((ROOT/f'data/catalog/{kind}.json').read_text())[kind] for kind in ['monsters','items','quests','maps','skills']}
    original_maps={str(r['id']):r for r in catalogs['maps']}
    catalogs,audit=project(catalogs)
    counts={}
    for kind in ['monsters','items','quests','maps','skills']:
        rows=catalogs[kind];counts[kind]=len(rows)
        keys={'monsters':['id','name','versionReview','level','stats','image','continents','onlyUnnamedMaps','elemental'],
              'items':['id','name','mergedIds','category','subcategory','image','equipStats','hasSource','sourceCounts'],
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
        if kind=='items':
            for original,row in zip(rows,index):row['searchTerms']=' '.join(str(v) for v in original.get('activeAliasIds',[]))
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
        if kind=='items':
            drop_details={str(d['id']):d for m in catalogs['monsters'] for d in m['drops']}
            for r in rows:
                for alias in r.get('activeAliasIds',[]):
                    if alias==str(r['id']):continue
                    # The reference merges some gender variants. Never copy one variant's
                    # exact stats/trade flags onto another ID without an exact-ID source.
                    variant=dict(r,id=int(alias),canonicalItemId=r['id'])
                    variant['equipStats']=drop_details.get(alias,{}).get('equipStats')
                    variant['trade']=None
                    variant['versionReview']={**r['versionReview'],'status':'本服關聯符合範圍；來源曾合併同名ID，未核對欄位維持未知'}
                    buckets.setdefault(str(int(alias)//1000),{})[alias]=variant
        for bucket,b in buckets.items():write(Path('data')/(kind+'-detail')/(bucket+'.json'),b)
    for p in (ROOT/'data/catalog').glob('*.json'):
        if p.stem in counts:continue
        if p.stem in ['exp-exchange','combat-analysis']:
            original=json.loads(p.read_text())
            write(Path('data')/p.name,{'gameVersion':'V002','levelCap':120,'levels':[],'status':'暫停自動跨級換算：原經驗表來自OdinMS，尚未取得本服V002完整經驗表'})
        elif p.stem=='halloween':
            write(Path('data')/p.name,{'gameVersion':'V002','quests':[q for q in catalogs['quests'] if q['name'].startswith('[萬聖節]')]})
        elif p.stem=='goddess-tower':
            write(Path('data')/p.name,json.loads(p.read_text()))
        else:
            write(Path('data')/p.name,{'versionReview':{'version':'V002','status':'暫緩發布：尚未完成當期來源核對'},'records':[]})
    training=[]
    by_id={str(m['id']):m for m in catalogs['monsters']}
    from collections import Counter
    for area in catalogs['maps']:
        spawns=Counter(str(m['monsterId']) for m in original_maps[str(area['id'])].get('monsterSpawns',[]) if not m.get('coordinateMissing'))
        if not spawns:continue
        training.append({'id':str(area['id']),'name':area['name'],'regionName':area['regionName'],
                         'width':area.get('miniMap',{}).get('width'),'height':area.get('miniMap',{}).get('height'),
                         'unknownSpawns':sum(n for mid,n in spawns.items() if mid not in by_id),
                         'monsters':[{'id':mid,'name':by_id[mid]['name'],'level':by_id[mid]['level'],
                                      'hp':by_id[mid]['stats'].get('maxHP'),'exp':by_id[mid]['stats'].get('exp'),
                                      'undead':bool(by_id[mid]['stats'].get('undead')),'boss':bool(by_id[mid]['stats'].get('boss')),'count':n}
                                     for mid,n in spawns.items() if mid in by_id]})
    write(Path('data/training.json'),training)
    attacks=[{**r,'attack':str(r['id'])=='2301002' or int(r['id'])%10000>=1000 and any((v.get('values',{}).get('damage',0)>0 or v.get('values',{}).get('mad',0)>0) for v in r.get('levels',[]))} for r in catalogs['skills']]
    write(Path('data/attack-skills.json'),attacks)
    write(Path('data/version-audit.json'),audit)
    write(Path('data/counts.json'),counts)
    shutil.copy2(ROOT/'data/guides.json',OUT/'data/guides.json')
    for p in ['RESEARCH.md','REFERENCES.md','data/SOURCES.md','data/VERSION_AUDIT.md']:
        shutil.copy2(ROOT/p,OUT/Path(p).name)
    print('Built',OUT,counts)
if __name__=='__main__':main()
