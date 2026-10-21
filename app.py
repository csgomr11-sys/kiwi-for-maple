from pathlib import Path
import json
import pandas as pd
import streamlit as st
from planning import eligible, required_quests, requirement_totals, hunting_maps, item_sources, quest_rows

ROOT = Path(__file__).parent
st.set_page_config(page_title='楓之谷資料研究室', layout='wide')
st.title('🍁 新楓之谷：經典版資料研究室')
@st.cache_data
def load_data(modified):
    return json.loads((ROOT / 'data/classic.json').read_text(encoding='utf-8'))
path = ROOT / 'data/classic.json'
if not path.exists():
    st.error('遊戲資料尚未同步，請執行 tools/sync_data.py。')
    st.stop()
data = load_data(path.stat().st_mtime_ns)
meta = data['metadata']
st.caption(f"{meta['world']}｜{meta['version']}｜擷取時間：{pd.Timestamp(meta['retrieved_at']).tz_convert('Asia/Taipei').strftime('%Y-%m-%d %H:%M')} 台灣時間")
st.warning('社群客戶端資料整理，並非官方背書。可能包含尚未開放、活動或特殊內容；任務腳本與獎勵仍以遊戲內為準。')
level = st.sidebar.number_input('角色等級', min_value=1, max_value=200, value=39, key='player_level')
job = st.sidebar.selectbox('職業', ['僧侶', '法師', '劍士', '弓箭手', '盜賊', '海盜'], key='player_job')
st.sidebar.info('預設為你提供的 39 級僧侶。治癒術、命中與實測擊殺速度會影響練功選擇。')
for col, label, value in zip(st.columns(4), ['怪物記錄', '掉落關係', '任務步驟', '地圖記錄'], [len(data['monsters']), sum(len(m['drops']) for m in data['monsters']), len(data['quests']), len(data['maps'])]):
    col.metric(label, f'{value:,}')
st.caption('以上是來源快照記錄數，不代表全數已開放或本作完整內容。')
tabs = st.tabs(['我的練等候選', '怪物與掉落', '任務與 CP 值', '材料與路線規劃', '來源與資料品質'])
def show(rows, rename=None):
    frame = pd.DataFrame(rows)
    if 'id' in frame.columns: frame['id'] = frame['id'].astype(str)
    if rename: frame = frame.rename(columns=rename)
    st.dataframe(frame, hide_index=True, width='stretch')
    return frame
def download(label, frame, name):
    st.download_button(label, frame.to_csv(index=False).encode('utf-8-sig'), name, mime='text/csv')
with tabs[0]:
    st.subheader(f'{level} 級{job}的練功候選')
    if job == '僧侶' and 35 <= level <= 45:
        st.info('先比較地鐵小幽靈與猴子沼澤地Ⅲ的天使猴：來源均標示不死系、治癒有效。以相同時間測試擊殺、消耗與風險，再選效率較高的一張；非保證最快路線。')
    gap = st.slider('怪物與角色等級差範圍', 1, 40, 10)
    heal_only = st.checkbox('僅顯示治癒術有效的怪物', value=(job == '僧侶'))
    pool = [m for m in data['monsters'] if m['level'] is not None and m['hp'] and m['exp'] is not None and abs(m['level']-level) <= gap and m['maps'] and not m['hidden'] and not m['boss'] and (not heal_only or (m['undead'] and (m['heal_effect'] or 0) > 0))]
    rows = [{'id': m['id'], '怪物': m['name'], '等級': m['level'], 'HP': m['hp'], 'EXP': m['exp'], '每千HP經驗': round(1000*m['exp']/m['hp'], 2), '地圖': '、'.join(x['name'] for x in m['maps']), '來源': m['source']} for m in pool]
    rows.sort(key=lambda r: -r['每千HP經驗'])
    show(rows)
    st.caption('每千 HP 經驗僅比較數值，不含命中、多目標分攤、地形、重生與隊伍，不能當作每分鐘經驗。')
    if pool:
        chosen = st.selectbox('查看候選怪物地圖', [m['id'] for m in pool], format_func=lambda i: next(m['name'] for m in pool if m['id'] == i))
        show(hunting_maps(data, [chosen])[:30], {'map': '地圖', 'monster': '怪物', 'spawn_points': '生怪點數', 'source': '來源'})
        st.caption('生怪點數不是每波怪數或效率；地圖可能含特殊版本，需核對實際可進入狀態。')
        speed = st.number_input('這隻怪的實測每分鐘擊殺數（0＝未知）', min_value=0.0, value=0.0)
        if speed:
            exp = next(m['exp'] for m in pool if m['id'] == chosen)
            st.metric('情境估計經驗／分鐘', f'{speed*exp:,.0f}')
            st.caption('輸入速度 × 每隻經驗；未計組隊、等差與活動加成。')
with tabs[1]:
    query = st.text_input('搜尋怪物、掉落物或地圖', placeholder='例如：鍋蓋、天使猴、小幽靈', key='monster_search')
    known = st.checkbox('只列有圖鑑資料且有出沒地圖的怪物', value=True)
    filtered = [m for m in data['monsters'] if (not known or (m['book'] and m['maps'])) and query.casefold() in (' '.join([m['name']] + [x['name'] for x in m['drops']] + [x['name'] for x in m['maps']])).casefold()]
    frame = show([{'id': m['id'], '怪物': m['name'], '等級': m['level'], 'HP': m['hp'], 'EXP': m['exp'], '掉落物': '、'.join(x['name'] for x in m['drops']), '地圖': '、'.join(x['name'] for x in m['maps']), '來源': m['source']} for m in filtered])
    download('下載查詢結果', frame, 'monsters.csv')
    st.caption('掉落關係 ≠ 掉落機率。卷軸名稱的 10%／60% 是使用成功率，不是怪物掉落率。')
with tabs[2]:
    scope = st.radio('任務範圍', ['符合角色等級與職業', '全部來源任務'], horizontal=True)
    quests = eligible(data['quests'], level, job) if scope.startswith('符合') else data['quests']
    text = st.text_input('搜尋任務或 NPC')
    quests = [q for q in quests if text.casefold() in (q['name'] + str(q.get('start')) + str(q.get('end'))).casefold()]
    st.caption('篩選最低／最高等級及職業大類；前置、已完成、時間與伺服器條件尚未檢查。')
    frame = pd.DataFrame(quest_rows(quests))
    sort = st.selectbox('獎勵排序', ['完成經驗', '楓幣增減', '名聲'])
    if not frame.empty: frame = frame.sort_values(sort, ascending=False)
    st.dataframe(frame, hide_index=True, width='stretch')
    download('下載任務結果', frame, 'quests.csv')
    if quests:
        qid = st.selectbox('任務需求與獎勵詳情', [q['id'] for q in quests], format_func=lambda i: next(q['name'] + f'（{i}）' for q in quests if q['id'] == i), key='quest_detail')
        quest = next(q for q in quests if q['id'] == qid)
        st.write('前置條件：', quest['prev'] or '來源未列前置')
        st.write('接取持有／未持有條件（非繳交材料）：', quest['needItems'] or '來源未列')
        show(quest['goalItems'], {'name': '繳交材料', 'count': '數量'})
        show(quest['goalMobs'], {'name': '擊殺怪物', 'count': '數量'})
        st.write('接取獎勵與費用：', quest['accept'])
        st.write('完成獎勵與費用：', quest['complete'])
        st.caption('道具 prop=-1 為依條件選一；其他非空 prop 是來源權重欄，未轉成百分比。獎池不能全部當作必得。')
        if quest.get('rewardNote'): st.info(quest['rewardNote'])
        if quest.get('serverGive'): st.write('來源另列伺服器決定獎池：', quest['serverGive'])
        minutes = st.number_input('任務實測或假設總耗時（分鐘，含材料與往返；0＝未知）', min_value=0.0, value=0.0)
        if minutes:
            st.metric('情境 CP：完成經驗／分鐘', f"{quest['complete']['exp']/minutes:,.1f}")
            st.metric('情境楓幣增減／分鐘', f"{(quest['accept']['money']+quest['complete']['money'])/minutes:,.1f}")
            st.caption('未折算獎勵道具、補給與材料價格，並非完整淨收益。')
        else: st.info('來源沒有耗時及市場價格，目前依獎勵排序；輸入耗時後才計算 CP。')
with tabs[3]:
    choices = {q['id']: q for q in data['quests']}
    selected = st.multiselect('選擇要規劃的任務', list(choices), format_func=lambda i: f"{i} · {choices[i]['name']}", key='plan_quests')
    expand = st.checkbox('加入必須完成的前置任務', value=True)
    try:
        plan, missing = required_quests(data['quests'], selected) if expand else ([choices[i] for i in selected], [])
    except ValueError as exc:
        st.error(str(exc)); plan, missing = [], []
    if missing: st.warning('來源缺少前置任務，計畫不完整：' + str(missing))
    st.write(f"共 {len(plan)} 個步驟；完成經驗 {sum(q['complete']['exp'] for q in plan):,}，接取與完成楓幣增減 {sum(q['accept']['money']+q['complete']['money'] for q in plan):,}。")
    st.caption('未扣已完成任務、背包與任務發放材料；互斥或職業限制可能使任務不能全做。state=1（進行中）與 state=0（尚未接）不自動當作需完成。')
    for key, title in [('goalItems', '需繳交材料'), ('goalMobs', '需擊殺怪物')]:
        st.subheader(title)
        frame = show(requirement_totals(plan, key), {'name': '名稱', 'count': '數量'})
        download('下載' + title, frame, key + '.csv')
    st.subheader('材料的怪物掉落來源')
    requirements = requirement_totals(plan, 'goalItems')
    sources = item_sources(data, [r['id'] for r in requirements])
    show(sources, {'item': '材料', 'monster': '怪物', 'level': '等級', 'maps': '地圖', 'source': '來源'})
    uncovered = [r['name'] for r in requirements if r['id'] not in {s['item_id'] for s in sources}]
    if uncovered: st.info('未查得怪物掉落來源（可能為商店、合成、採集或任務）：' + '、'.join(uncovered))
    st.subheader('擊殺需求候選地圖（按生怪點數排序）')
    show(hunting_maps(data, [r['id'] for r in requirement_totals(plan, 'goalMobs')]), {'map': '地圖', 'monster': '怪物', 'spawn_points': '生怪點數', 'source': '來源'})
    st.subheader('接取與交付位置')
    show(quest_rows(plan))
with tabs[4]:
    st.markdown((ROOT / 'data/SOURCES.md').read_text(encoding='utf-8'))
    checks = pd.DataFrame(data['cross_checks'])
    st.write(f"第二來源 HP／EXP 比對：{int(checks.match.sum())} 項一致，{int((~checks.match).sum())} 項有差異或缺值。兩站可能共用客戶端來源，不代表獨立官方驗證。")
    st.dataframe(checks[~checks.match], hide_index=True)
    st.json(meta)
    st.download_button('下載本次資料快照（JSON）', path.read_bytes(), 'classic.json', mime='application/json')
