"""Conservative V002 publication projection; never mutate retained source snapshots.

A scope match is not proof of server-side availability, drop rate or reward scripts.
Uncertain rows and unsupported source relations are withheld and counted in the audit.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
BASE_REGIONS = {'楓之島', '維多利亞島', '奇幻村', '鯨魚號'}
LATER_REGIONS = {'路德斯湖', '米納爾森林', '納希沙漠', '桃花仙境', '水世界', '時間神殿', '鐘塔最下層', '瑞恩', '日本'}
CURRENT_JOBS = {0,100,110,111,120,121,130,131,200,210,211,220,221,230,231,300,310,311,320,321,400,410,411,420,421,500,510,511,520,521}
SUPPORTED_DROP_SOURCES = {'monsterBook', 'monsterCard', 'quest'}


def map_scope(row):
    mid = int(row['id'])
    if row.get('regionName') in LATER_REGIONS:
        return 'excluded', f"地區「{row['regionName']}」不在本次V002開放範圍"
    if 211041500 <= mid < 212000000 or 280000000 <= mid < 281000000:
        return 'pending', '廢礦後段／炎魔；官方僅開前半部，精確邊界未確認'
    if row.get('unnamed') or row.get('mapDataMissing'):
        return 'pending', '未命名或缺少單張地圖資料，不能由客戶端ID推定已開放'
    if row.get('regionName') in BASE_REGIONS and (
        mid < 2000000 or 100000000 <= mid < 106000000 or
        107000000 <= mid < 108000000 or 110000000 <= mid < 111000000 or
        120000000 <= mid < 121000000):
        return 'scoped', '本服2.0.0具名地圖／既有地區；伺服器開放細節仍待實測'
    if 200000000 <= mid < 200090000 or mid in {200090000, 200090001, 200090010, 200090011} or 211000000 <= mid < 211041500:
        return 'scoped', 'V002官方開放地區與本服2.0.0具名地圖相符'
    if 920010000 <= mid <= 920011300 and '雅典娜禁地' in row.get('name', ''):
        return 'scoped', '官方V002已開女神的痕跡；本服2.0.0地圖對照'
    if 876009750 <= mid <= 876011100 and '雅典娜禁地' in row.get('name', ''):
        return 'scoped', '本服V002女神的痕跡具名副本地圖'
    if 876011151 <= mid <= 876011157:
        return 'scoped', '官方當期雪原面具祭典；本服2.0.0具名地圖'
    return 'pending', '特殊／測試／活動或其他地圖，缺乏當期開放依據'


def project(catalogs):
    source = deepcopy(catalogs)
    report = {'version': 'V002', 'reviewedAt': '2026-10-21',
              'label': '台版新楓之谷：經典版 V002｜天空之城・冰原雪域',
              'levelCap': 120, 'official': json.loads((ROOT/'data/version-evidence/official-v002.json').read_text()),
              'limitations': ['已逐筆執行版本範圍與來源檢查；不等於逐筆遊戲內實測。',
                             '客戶端2.0.0與官方V002的命名不是同一種版本編號。',
                             '本服怪物圖鑑可支援掉落品項，不能證明伺服器機率；機率一律未知。',
                             '商店、製作、轉蛋與歷史兌換關係缺少當期證據，暫不發布。',
                             '廢礦精確開放邊界未獲官方逐圖說明；不確定地圖暫緩發布。',
                             '原經驗表引用OdinMS，已暫停自動升級／跨級換算，僅保留同級實測。'],
              'summary': {}, 'records': [], 'removedRelations': {}}
    removed = Counter()
    decisions = {k: {} for k in ['maps', 'monsters', 'quests', 'items']}
    def decide(kind, row, status, reason):
        decisions[kind][str(row['id'])] = status
        report['records'].append({'kind': kind, 'id': str(row['id']), 'name': row.get('name', ''), 'status': status, 'reason': reason})
    maps = {}
    for row in source['maps']:
        status, reason = map_scope(row)
        decide('maps', row, status, reason)
        if status == 'scoped':
            if 200000000<=int(row['id'])<201000000 or 920010000<=int(row['id'])<=920011300 or '雅典娜禁地' in row['name']:row['regionName']='天空之城'
            maps[str(row['id'])] = row
    monsters = {}
    for row in source['monsters']:
        valid = [m for m in row.get('maps', []) if str(m['id']) in maps]
        if not valid:
            decide('monsters', row, 'pending', '沒有可對應本次範圍的具名出沒地圖')
            continue
        if (row.get('level') or 0) > 120:
            decide('monsters', row, 'pending', '超過當期角色上限且缺乏獨立開放證據；暫不推薦')
            continue
        row['maps'] = valid
        row['continents'] = sorted({maps[str(m['id'])]['regionName'] for m in valid})
        row['onlyUnnamedMaps'] = False
        row.pop('mesoDrop', None)
        decide('monsters', row, 'scoped', '本服2.0.0怪物表，出沒地圖符合V002範圍；數值仍待遊戲實測')
        monsters[str(row['id'])] = row
    quests = {}
    for row in source['quests']:
        refs = list(row.get('mapReferences', []))
        for side in ['startNpc', 'endNpc']:
            refs.extend((row.get(side) or {}).get('maps', []))
        if (row.get('minLevel') or 0) > 120:
            status, reason = 'excluded', '接取等級超過V002上限120'
        elif any(decisions['maps'].get(str(m['id'])) == 'excluded' for m in refs):
            status, reason = 'excluded', '任務關聯地圖含未開放的後期地區'
        elif (row.get('startRequirements') or {}).get('jobs') and not any(j in CURRENT_JOBS for j in row['startRequirements']['jobs']):
            status, reason = 'excluded', '職業條件只含尚未開放的職業／四轉'
        elif row['category'] == '活動' and not row['name'].startswith('[萬聖節]'):
            status, reason = 'pending', '其他活動的當期時程與開放依據不足'
        elif str(row['id'])=='1203' and row.get('minLevel')==51 and row.get('maxLevel')==70:
            status, reason = 'scoped', '官方20209確認女神的痕跡51～70級、6人；過期地圖ID關聯已移除'
        elif row['name'].startswith('[萬聖節]'):
            status, reason = 'scoped', '官方當期萬聖節活動與本服2.0.0任務系列對照；逐項獎勵非官方逐筆驗證'
        elif not refs or any(str(m['id']) not in maps for m in refs):
            status, reason = 'pending', '任務地點／特殊場景尚未全部通過本次版本範圍核對'
        elif any(str(m['id']) not in monsters for stage in ['startRequirements', 'completeRequirements'] for m in (row.get(stage) or {}).get('monsters', [])):
            status, reason = 'pending', '擊殺需求含尚未確認的怪物'
        else:
            status, reason = 'scoped', '本服2.0.0任務條件與地點符合V002範圍；服務端腳本與收益仍待實測'
        decide('quests', row, status, reason)
        if status == 'scoped': quests[str(row['id'])] = row
    # Do not offer a quest whose required completed predecessor has been withheld.
    changed = True
    while changed:
        changed = False
        for qid, row in list(quests.items()):
            if any(str(q['id']) not in quests for q in (row.get('startRequirements') or {}).get('quests', []) if q.get('state') == 2):
                del quests[qid]; decisions['quests'][qid] = 'pending'; changed = True
                entry = next(r for r in report['records'] if r['kind'] == 'quests' and r['id'] == qid)
                entry.update(status='pending', reason='必要前置任務尚未通過範圍核對，暫不納入規劃')
    item_ids = set()
    for row in monsters.values():
        drops = []
        for drop in row.get('drops', []):
            if drop.get('source') not in SUPPORTED_DROP_SOURCES:
                removed['非本服圖鑑／卡片或任務的掉落關係'] += 1
                continue
            if drop.get('source') == 'quest' and not any(str(q) in quests for q in drop.get('questIds', [])):
                removed['未通過核對的任務限定掉落'] += 1
                continue
            removed['他版掉落率'] += len(drop.pop('dropRates', []))
            drop.pop('equipStatRanges', None); drop.pop('equipStatRangeSources', None)
            drop['questIds'] = [q for q in drop.get('questIds', []) if str(q) in quests]
            drop['questNames'] = [quests[str(q)]['name'] for q in drop['questIds']]
            drop['dropRateStatus'] = '本服機率未公開；不採用他版機率'
            item_ids.add(str(drop['id'])); drops.append(drop)
        row['drops'] = drops
        row['questRequirements'] = [q for q in row.get('questRequirements', []) if str(q.get('questId')) in quests]
    for row in quests.values():
        for stage in ['startRequirements', 'completeRequirements', 'startRewards', 'completeRewards']:
            item_ids.update(str(i['id']) for i in (row.get(stage) or {}).get('items', []))
    items = {}
    for row in source['items']:
        iid = str(row['id'])
        aliases={str(v) for v in row.get('mergedIds', [row['id']])}
        if not aliases & item_ids:
            decide('items', row, 'pending', '無通過本次核對的怪物掉落或任務關聯，不推定本服可取得')
            continue
        relations = row.get('sources', {})
        relations['monsterDrops'] = [r for r in relations.get('monsterDrops', []) if str(r['monsterId']) in monsters and r.get('source') in SUPPORTED_DROP_SOURCES and any(str(d['id']) in aliases for d in monsters[str(r['monsterId'])]['drops'])]
        for key in ['questRewards', 'questRequirements']:
            relations[key] = [r for r in relations.get(key, []) if str(r['questId']) in quests]
        for key in ['shops', 'crafts', 'craftRequirements', 'boxChoices', 'boxSources', 'gachaSources', 'exchangeSources']:
            removed['暫緩發布的'+key] += len(relations.get(key, [])); relations[key] = []
        row['sourceCounts'] = {k: len(v) for k, v in relations.items()}
        row['hasSource'] = any(row['sourceCounts'].values())
        decide('items', row, 'scoped', '至少一項本次範圍內怪物／任務關聯；不代表所有舊來源都適用')
        row['activeAliasIds']=sorted(aliases & item_ids)
        items[iid] = row
    accepted = {'maps': maps, 'monsters': monsters, 'quests': quests, 'items': items}
    def clean(value):
        if isinstance(value, list): return [clean(v) for v in value]
        if not isinstance(value, dict): return value
        out = {}
        for key, val in value.items():
            if key in {'dropRates', 'mesoDrop', 'equipStatRanges', 'equipStatRangeSources'}: continue
            if key == 'jobs' and isinstance(val, list): val = [j for j in val if j in CURRENT_JOBS]
            if key == 'maps' and isinstance(val, list): val = [{**m,'regionName':maps[str(m['id'])]['regionName']} for m in val if str(m.get('id')) in maps]
            if key == 'mapReferences' and isinstance(val, list): val = [m for m in val if str(m.get('id')) in maps]
            if key == 'portals' and isinstance(val, list): val = [p for p in val if str(p.get('targetMapId', p.get('targetMap'))) in maps]
            if key == 'monsterSpawns' and isinstance(val, list): val = [m for m in val if str(m.get('monsterId')) in monsters]
            if key in {'quests', 'dependentQuests'} and isinstance(val, list): val = [q for q in val if str(q.get('id', q.get('questId'))) in quests]
            out[key] = clean(val)
        if 'maps' in out and 'locationText' in out:out['locationText']='、'.join(maps[str(m['id'])].get('label',maps[str(m['id'])]['name']) for m in out['maps']) or '地點待核對'
        return out
    for kind, records in accepted.items():
        source[kind] = []
        for row in records.values():
            row = clean(row)
            row['versionReview'] = {'version': 'V002', 'status': '範圍核對通過，數值待實測', 'sourceVersion': '台版客戶端2.0.0（來源站標示）'}
            source[kind].append(row)
        report['summary'][kind] = dict(Counter(decisions[kind].values())) | {'total': len(catalogs[kind])}
    report['removedRelations'] = dict(removed)
    report['sourceFindings'] = {'allForeignRateEntries':sum(len(d.get('dropRates', [])) for m in catalogs['monsters'] for d in m.get('drops', [])), 'allHeavenMSShopEntries':sum(1 for i in catalogs['items'] for r in i.get('sources', {}).get('shops', []) if 'heavenms' in r.get('sourceFile', '').lower())}
    source['skills'] = [r for r in source['skills'] if int(r.get('jobId') or 0) in CURRENT_JOBS]
    report['crossChecks'] = crosscheck(source)
    if report['crossChecks']['conflicts']:raise ValueError('Conflicting numeric fields: inspect V002 audit before publishing')
    return source, report


def crosscheck(source):
    """Compare preserved TW client catalogs, not independent server validation."""
    other=json.loads((ROOT/'data/classic.json').read_text())
    result={'source':'https://david27tainan.github.io/KargoData/',
            'note':'另一份台版2.0.0整理；可能同源，不代表官方或獨立遊戲實測。缺值不補0。',
            'matched':0,'missing':0,'conflicts':[]}
    for kind in ['monsters','quests']:
        lookup={str(r['id']):r for r in other[kind]}
        for row in source[kind]:
            alt=lookup.get(str(row['id']))
            if not alt:result['missing']+=1;continue
            if kind=='monsters':
                pairs=[('level',row.get('level'),alt.get('level'))]+[(k,row['stats'].get(k),alt.get(v)) for k,v in [('maxHP','hp'),('exp','exp'),('MDDamage','magic_defense')]]
            else:
                pairs=[('minLevel',row.get('minLevel'),alt.get('lvmin')),('maxLevel',row.get('maxLevel'),alt.get('lvmax'))]+[(k,(row.get('completeRewards') or {}).get(k),(alt.get('complete') or {}).get(k)) for k in ['exp','money','pop']]
            for key,a,b in pairs:
                if a is None or b is None:result['missing']+=1
                elif a==b:result['matched']+=1
                else:result['conflicts'].append({'kind':kind,'id':row['id'],'field':key,'primary':a,'comparison':b})
    return result
