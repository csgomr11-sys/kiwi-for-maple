"""Analysis of sourced facts; no assumptions about current content availability."""
from collections import defaultdict

def eligible(quests, level, job="僧侶"):
    aliases = {"僧侶": ["法師", "僧侶", "初心者"], "法師": ["法師", "初心者"]}
    # Beginner-only quests are deliberately not eligible for an already advanced job.
    labels = [s for s in aliases.get(job, [job]) if s != "初心者"]
    return [q for q in quests if (q.get("lvmin") or 0) <= level
            and (not q.get("lvmax") or q["lvmax"] >= level)
            and (not q.get("jobLabel") or any(s in q["jobLabel"] for s in labels))]

def required_quests(quests, selected):
    by_id = {q['id']: q for q in quests}
    found, visiting, missing = set(), set(), set()
    def visit(qid):
        if qid in found:
            return
        if qid in visiting:
            raise ValueError("前置任務形成循環，不能自動展開")
        if qid not in by_id:
            missing.add(qid); return
        visiting.add(qid)
        for p in by_id[qid].get('prev') or []:
            if p.get('state') == 2:
                visit(p['id'])
        visiting.remove(qid); found.add(qid)
    for qid in selected:
        visit(qid)
    return [q for q in quests if q['id'] in found], sorted(missing)

def requirement_totals(quests, key):
    totals = {}
    for q in quests:
        for item in q.get(key) or []:
            if item['count'] > 0:
                row = totals.setdefault(item['id'], {'id': item['id'], 'name': item['name'], 'count': 0})
                row['count'] += item['count']
    return sorted(totals.values(), key=lambda r: (-r['count'], r['id']))

def hunting_maps(data, monster_ids):
    wanted = set(monster_ids)
    result = []
    for maprow in data['maps']:
        for mob in maprow['monsters']:
            if mob['id'] in wanted:
                result.append({'map_id': maprow['id'], 'map': maprow['name'], 'region': maprow['region'],
                               'monster_id': mob['id'], 'monster': mob['name'], 'spawn_points': mob['spawn_points'],
                               'source': maprow['source']})
    return sorted(result, key=lambda r: -(r['spawn_points'] or 0))

def item_sources(data, item_ids):
    wanted = set(item_ids)
    rows = []
    for m in data['monsters']:
        for item in m['drops']:
            if item['id'] in wanted:
                rows.append({'item_id': item['id'], 'item': item['name'], 'monster_id': m['id'],
                             'monster': m['name'], 'level': m['level'], 'maps': '、'.join(x['name'] for x in m['maps']),
                             'source': m['source']})
    return rows

def quest_rows(quests):
    rows = []
    for q in quests:
        complete = q['complete']
        rows.append({'id': str(q['id']), '任務': q['name'], '最低等級': q['lvmin'], '最高等級': q['lvmax'],
                     '職業限制': q['jobLabel'], '接取NPC': (q['start'] or {}).get('name'),
                     '接取地點': (q['start'] or {}).get('map'), '交付NPC': (q['end'] or {}).get('name'),
                     '交付地點': (q['end'] or {}).get('map'), '完成經驗': complete['exp'], '楓幣增減': complete['money'],
                     '名聲': complete['pop'], '材料種類': len(q['goalItems']), '擊殺數': sum(m['count'] for m in q['goalMobs']),
                     '另有腳本條件': q['goalScript'], '來源': q['source']})
    return rows
