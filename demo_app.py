from pathlib import Path
import pandas as pd
import streamlit as st
from analysis import validate, rank_quests, aggregate

ROOT = Path(__file__).parent
st.set_page_config(page_title="楓之谷資料研究室", layout="wide")
st.title("🍁 楓之谷資料研究室")
st.warning("目前內建資料全部為虛構示範，不能作為遊戲攻略。目標遊戲：新楓之谷：經典版（官網已確認，完整遊戲數據待取得）。")
st.caption("可匯入有來源的 CSV／Excel；不同世界與版本分開分析。")

def load(kind, label):
    upload = st.sidebar.file_uploader(label, type=["csv", "xlsx"], key=kind)
    try:
        if upload is None:
            frame = pd.read_csv(ROOT / "data" / (kind + ".csv"))
        elif upload.name.lower().endswith(".xlsx"):
            frame = pd.read_excel(upload)
        else:
            frame = pd.read_csv(upload)
        return validate(frame, kind)
    except Exception as exc:
        st.error(f"{label}匯入失敗：{exc}")
        st.stop()

monsters = load("monsters", "怪物資料")
quests = load("quests", "任務資料")
choices = sorted(set(zip(monsters.world, monsters.version)) | set(zip(quests.world, quests.version)))
if not choices:
    st.info("請匯入至少一筆資料。")
    st.stop()
world, version = st.sidebar.selectbox("世界／版本", choices, format_func=lambda x: " / ".join(map(str, x)))
monsters = monsters[(monsters.world == world) & (monsters.version == version)]
quests = quests[(quests.world == world) & (quests.version == version)]
level = st.sidebar.number_input("角色等級", min_value=1, max_value=300, value=20)
tabs = st.tabs(["怪物與掉落", "練等地圖", "任務 CP 值", "任務需求彙總", "資料範本"])
with tabs[0]:
    query = st.text_input("搜尋怪物、掉落物或地圖")
    mask = monsters[["name", "drops", "map"]].astype(str).apply(lambda col: col.str.contains(query, regex=False)).any(axis=1)
    st.dataframe(monsters[mask], hide_index=True)
with tabs[1]:
    gap = st.slider("顯示角色等級上下範圍", 0, 50, 10)
    candidates = monsters[(monsters.level - level).abs() <= gap].copy()
    candidates["估計經驗／分鐘"] = candidates.exp * candidates.kills_per_min
    candidates = candidates.sort_values("估計經驗／分鐘", ascending=False)
    st.info("經驗／分鐘＝每隻經驗 × 每分鐘擊殺數。擊殺速度需實測；未計入等差懲罰、移動、補給、職業與組隊加成。地圖列為候選，不能僅憑等級判定適合。")
    st.dataframe(candidates, hide_index=True)
    if not candidates.empty:
        st.bar_chart(candidates.set_index("name")[["估計經驗／分鐘"]])
with tabs[2]:
    metric = st.radio("排序依據", ["經驗／分鐘", "楓幣／分鐘"], horizontal=True)
    ranked = rank_quests(quests, level).sort_values(metric, ascending=False)
    st.caption("依最低等級篩選；前置任務、職業及其他條件仍需確認。時間須包含收集與往返；道具收益未折算，楓幣為毛收入。")
    st.dataframe(ranked, hide_index=True)
with tabs[3]:
    selected = st.multiselect("選擇要規劃的任務（預設全部）", list(quests.id), default=list(quests.id), format_func=lambda key: key + " · " + str(quests.loc[quests.id == key, "name"].iloc[0]))
    plan = quests[quests.id.isin(selected)]
    st.write(f"共 {len(plan)} 個任務；預估 {plan.minutes.sum():g} 分鐘，經驗 {plan.exp.sum():g}，楓幣 {plan.mesos.sum():g}。")
    st.caption("需求直接加總；未自動扣除背包、任務獎勵材料或同時累計擊殺。前置任務不自動加入。")
    for col, title in [("materials", "材料需求"), ("kills", "擊殺需求")]:
        st.subheader(title)
        totals = aggregate(plan, col)
        st.dataframe(totals, hide_index=True)
        st.download_button("下載" + title, totals.to_csv(index=False).encode("utf-8-sig"), col + ".csv", key=col)
    st.dataframe(plan[["name", "prerequisites", "location", "recommended_map", "reward_items"]], hide_index=True)
with tabs[4]:
    st.write("請下載範本填寫。world、version、source 用來記錄世界、版本與出處。materials／kills 使用 名稱:數量;名稱:數量；空白代表未填，並非已確認沒有需求。")
    for kind in ["monsters", "quests"]:
        st.download_button("下載 " + kind + " 範本", (ROOT / "data" / (kind + ".csv")).read_bytes(), kind + ".csv")
