"""Version-neutral analysis; rates are estimates, not game facts."""
import pandas as pd

SCHEMAS = {
    "monsters": ["world", "version", "source", "name", "level", "hp", "exp", "map", "kills_per_min", "drops"],
    "quests": ["world", "version", "source", "id", "name", "min_level", "prerequisites", "location", "recommended_map", "minutes", "exp", "mesos", "reward_items", "materials", "kills"],
}
NUMERIC = {"monsters": ["level", "hp", "exp", "kills_per_min"], "quests": ["min_level", "minutes", "exp", "mesos"]}

def validate(frame, kind):
    missing = set(SCHEMAS[kind]) - set(frame.columns)
    if missing:
        raise ValueError("缺少欄位：" + ", ".join(sorted(missing)))
    frame = frame.copy().fillna("")
    for col in NUMERIC[kind]:
        frame[col] = pd.to_numeric(frame[col], errors="raise")
        if not frame[col].map(lambda x: pd.notna(x) and float('-inf') < x < float('inf') and x >= 0).all():
            raise ValueError(col + " 必須是有限的非負數")
    if kind == "quests":
        if (frame.minutes <= 0).any():
            raise ValueError("任務分鐘數必須大於零")
        if frame.id.duplicated().any():
            raise ValueError("任務 id 不可重複")
        for col in ["materials", "kills"]:
            for cell in frame[col]:
                parse_counts(cell)
    return frame

def parse_counts(value):
    result = {}
    for part in str(value).split(";"):
        if not part.strip():
            continue
        name, count = part.rsplit(":", 1)
        count = int(count)
        if not name.strip() or count <= 0:
            raise ValueError("材料／擊殺格式必須為 名稱:正整數;名稱:正整數")
        result[name.strip()] = result.get(name.strip(), 0) + count
    return result

def aggregate(frame, column):
    totals = {}
    for value in frame[column]:
        for name, count in parse_counts(value).items():
            totals[name] = totals.get(name, 0) + count
    return pd.DataFrame(sorted(totals.items()), columns=["名稱", "數量"])

def rank_quests(frame, level):
    result = frame[frame.min_level <= level].copy()
    result["經驗／分鐘"] = result.exp / result.minutes
    result["楓幣／分鐘"] = result.mesos / result.minutes
    return result
