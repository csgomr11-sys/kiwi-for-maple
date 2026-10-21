# Kiwi Maple：新楓之谷個人網站與資料研究室

已新增依你指定網站設計的個人靜態網站，預設帶入39級僧侶與你的能力、技能配置。**主網站使用方式與完整資料範圍見 [WEBSITE.md](WEBSITE.md)。**

快速啟動：`python tools/build_site.py`，接著 `python -m http.server 8000 --bind 0.0.0.0 --directory site`。以下內容為保留的Python資料研究介面。

中文資料查詢與分析工具，預設角色為 **39級僧侶**。已主動蒐集並接入台灣經典版社群客戶端資料，不需要先自行準備Excel。完整研究與角色建議見 [RESEARCH.md](RESEARCH.md)。

目前快照含1,238筆怪物、9,859筆掉落關係、591個任務步驟、1,838筆地圖。這是來源記錄數，含特殊、活動或可能未開放內容；不是宣稱全數可玩或已收錄所有伺服器資料。來源標示客戶端2.0.0，未逐筆遊戲內實測。

## 使用

```bash
cd /workspace/kiwi-for-maple
python -m venv /workspace/maple-venv
/workspace/maple-venv/bin/python -m pip install --no-cache-dir -r requirements.lock
/workspace/maple-venv/bin/python -m streamlit run app.py --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
```

瀏覽器入口需由執行平台提供。雲端環境的安裝、啟動步驟亦已保存至設定草稿。套件與資料快照保留於磁碟；發布或還原後需重啟服務。

## 功能

- **我的練等候選**：依角色等級與治癒有效性篩選怪物，查看出沒地圖、生怪點；輸入實測擊殺速度估計經驗／分鐘。
- **怪物與掉落**：用怪物、道具或地圖名稱反向搜尋，下載結果CSV。
- **任務與CP值**：篩選等級上下限、職業大類，顯示前置、NPC、材料、擊殺、接取與完成獎勵；輸入單任務耗時後估計CP。
- **材料與路線規劃**：挑選任務、展開需完成的前置、加總材料與擊殺，反查材料掉落怪物與候選地圖，下載需求清單。
- **來源與品質**：可查看擷取時間、來源URL、SHA-256與跨站數值差異。

## 更新資料

```bash
/workspace/maple-venv/bin/python tools/sync_data.py
```

指令只讀取公開來源，不需遊戲帳密。所有請求與解析成功才替換 `data/classic.json`；失敗時保留既有快照。原始回應存在被Git忽略的 `.cache/research/`，正式資料只保留事實與來源；沒有搬運圖片或攻略文章。資料更新需要網路，平常啟動及測試不需要。

來源及限制見 [data/SOURCES.md](data/SOURCES.md)。舊的虛構CSV保留供 `demo_app.py` 與匯入範例使用；正式介面不讀這兩份CSV。

## 計算限制

- 客戶端未提供掉落機率，不推估必掉擊殺數或刷寶時薪。卷軸成功率不是掉落率。
- 來源缺少全任務耗時與市場價格；預設按獎勵排序，並非完整淨收益或最快升級排名。
- 未自動判定已開放、活動期限、已完成及腳本條件；職業僅能依來源大類篩選。
- 前置state=2表示需完成才展開；state=1進行中、state=0尚未接不當作必須完成。缺失前置會警告。
- 材料按ID加總，不扣背包、任務發放材料，也不合併可共計的擊殺。候選地圖按生怪點排列，未作最短路線最佳化。
- 獎池中的隨機或依職業選一道具不能全部當作必得；部分獎勵在伺服器腳本中，來源無法完整取得。

## 驗證

```bash
/workspace/maple-venv/bin/python -m unittest discover -s tests -v
/workspace/maple-venv/bin/python -m pip check
```

測試涵蓋真實資料查詢、39級僧侶篩選、前置展開、材料來源與彙總、未知資料保留，以及原有CSV範例功能。

目前程式碼位於工作區，尚未提交或推送GitHub。
