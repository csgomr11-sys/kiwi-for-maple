from source_policy import approved_open, require_allowed
"""Fetch public factual tables, preserving provenance and unknown values.

No game executables, images, guide prose, private APIs or authentication used.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from html import unescape
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://david27tainan.github.io/KargoData/"
CHECK = "https://bobogameguides.com/maplestory-classic/monsters/"

def get(url, cache):
    path = cache / (hashlib.sha256(url.encode()).hexdigest() + ".raw")
    req = urllib.request.Request(url, headers={"User-Agent": "KiwiMapleResearch/0.1 (public game-data research)"})
    with approved_open(req, timeout=40) as response:
        raw = response.read(15_000_001)
        if len(raw) > 15_000_000:
            raise ValueError("Unexpected oversized response")
    path.write_bytes(raw)
    return raw, {"url": url, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}

def build(raw, check_html):
    mobs, series, maps, layout = (raw[k] for k in ["mobs", "quests", "maps", "map_layout"])
    monsters = []
    for m in mobs:
        monsters.append({"id": m["i"], "name": m["n"], "level": m.get("lv"), "hp": m.get("hp"),
                         "exp": m.get("e"), "boss": bool(m.get("b")), "undead": bool(m.get("u")),
                         "book": bool(m.get("bk")), "hidden": bool(m.get("hide")),
                         "evade": m.get("ev"), "defense": m.get("pd"), "magic_defense": m.get("md"),
                         "elements": m.get("el", []), "heal_effect": (m.get("ee") or [None]*6)[-1],
                         "drops": [{"id": d[0], "name": d[1], "probability": None} for d in m.get("dri", [])],
                         "maps": [{"id": d[0], "name": d[1]} for d in m.get("mpi", [])],
                         "source": BASE + "mobs/?id=" + str(m["i"])})
    quests = []
    fields = ["id", "name", "lvmin", "lvmax", "jobLabel", "prev", "needItems", "goalItems", "goalMobs", "goalScript", "needFrom", "accept", "complete", "rewardNote", "serverGive", "serverExp"]
    for group in series:
        for q in group["steps"]:
            out = {k: q.get(k) for k in fields}
            out.update(series_id=group["sid"], series_name=group["name"], minutes=None,
                       start=q.get("start"), end=q.get("end"), source=BASE + "quests/?id=" + str(group["sid"]))
            quests.append(out)
    if len({q['id'] for q in quests}) != len(quests):
        raise ValueError("Duplicate quest IDs")
    map_rows = []
    for mid, region, name, mob_count, residents in maps:
        entry = layout.get(str(mid), {})
        visited = set()
        while "ln" in entry:
            target = str(entry["ln"])
            if target in visited:
                raise ValueError("Map layout link cycle")
            visited.add(target)
            entry = layout.get(target, {})
        counts = Counter(p[2] for p in entry.get("m", []))
        map_rows.append({"id": mid, "region": region, "name": name,
                         "monsters": [{"id": x[0], "name": x[1], "spawn_points": counts.get(x[0])} for x in residents],
                         "source": BASE + "maps/?id=" + str(mid)})
    # Cross-check facts from a second public page; agreement may share client origins.
    comparisons = []
    by_id = {m["id"]: m for m in monsters}
    for chunk in re.split(r'<details class="odb-row monster-row"', check_html)[1:]:
        chunk = chunk.split('<details class="odb-row monster-row"')[0]
        ident = re.search(r'id="mob-(\d+)"', chunk)
        if not ident or int(ident[1]) not in by_id:
            continue
        mid = int(ident[1]); main = by_id[mid]
        for field, label in [("hp", "HP"), ("exp", "EXP")]:
            value = re.search(r'<b>' + label + r'</b><span>([\d,]+)</span>', chunk)
            if value:
                n = int(value[1].replace(',', ''))
                comparisons.append({"monster_id": mid, "name": main["name"], "field": field,
                                    "primary": main[field], "comparison": n, "match": main[field] == n,
                                    "source": CHECK + "#mob-" + str(mid)})
    if len(comparisons) < 10:
        raise ValueError("Comparison page structure changed")
    return {"monsters": monsters, "quests": quests, "maps": map_rows, "cross_checks": comparisons}

def main():
    require_allowed(BASE)
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'data/classic.json')
    args = parser.parse_args()
    cache = ROOT / '.cache/research'; cache.mkdir(parents=True, exist_ok=True)
    raw, sources = {}, []
    homepage, meta = get(BASE, cache); sources.append(meta)
    version = re.search(r'MapleStory Classic\s*[·・]\s*(\d+\.\d+\.\d+)', homepage.decode('utf-8'))
    if not version:
        raise ValueError('Cannot verify the source site version label')
    for name in ['mobs', 'quests', 'maps', 'map_layout']:
        body, meta = get(BASE + 'data/' + name + '.json', cache)
        raw[name] = json.loads(body); sources.append(meta)
    body, meta = get(CHECK, cache); sources.append(meta)
    result = build(raw, body.decode('utf-8'))
    result['metadata'] = {"world": "新楓之谷：經典版（台灣）", "version": version[1] + "（來源站標示）",
                          "retrieved_at": datetime.now(timezone.utc).isoformat(), "sources": sources,
                          "status": "第三方客戶端資料整理，非官方背書；含未開放／特殊內容，未逐筆遊戲內實測"}
    # Replace only after all requests, parsing and validation succeed.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix('.tmp')
    tmp.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    tmp.replace(args.output)
    print(json.dumps({k: len(result[k]) for k in ['monsters', 'quests', 'maps', 'cross_checks']}, ensure_ascii=False))
    print('cross-check mismatches:', sum(not x['match'] for x in result['cross_checks']))

if __name__ == '__main__':
    main()
