# 資料來源追蹤

## 使用者指定入口

- 名稱：新楓之谷經典版（使用者提供）
- 網址：https://maplestoryclassic.beanfun.com/Main
- 紀錄日期：2026-10-21
- 狀態：最新重試成功，HTTP 200。先前 CONNECT 403 已不再重現。
- 已確認頁面標題：新楓之谷：經典版官方網站。
- 未確認：確切遊戲資料版本、是否屬於 MapleStory Worlds、完整怪物與任務表、掉落機率、資料使用條件。

## 已檢查的官方公開入口

官網 `/web/js/default.js` 引用官方 CDN 的 `navbarData.js`。以下連結來自該導覽，並已讀取頁面及頁面實際使用的公開唯讀 JSON API（`https://maplestoryclassic-event.beanfun.com/api/EventAd/GetDetail?EventADID=編號`，回傳 code=1）：

| 項目 | 官方連結 | 本次觀察 |
| --- | --- | --- |
| 玩法說明 | https://maplestoryclassic-event.beanfun.com/EventAd/EventAd?eventAdId=17819 | 伺服器、角色建立、基本操作、NPC 任務說明；非任務清單 |
| 職業介紹 | https://maplestoryclassic-event.beanfun.com/EventAd/EventAd?eventAdId=17814 | 主圖形式，JSON 無職業數值表；圖片未判讀 |
| 系統說明 | https://maplestoryclassic-event.beanfun.com/EventAd/EventAd?eventAdId=17818 | 好友、組隊、公會、聊天說明，另有交易系統連結 |

官網 `/web/js/api.js` 顯示公告、廣告及下載等前端介面；其中存在明確標記 MOCK 的測試資料，不能當作真實遊戲資訊匯入。這次檢查沒有取得完整怪物、掉落與任務資料，不代表整個網站一定沒有其他資料。

後續優先檢查官方更新公告中的版本與內容，再評估符合本作版本且有來源的資料。內建 CSV 繼續標記為 DEMO；不能宣稱資料完整或真實。

## 已接入的玩家整理資料（2026-10-21）

正式介面已改讀 `classic.json`，不再使用 DEMO CSV。原本的 `monsters.csv`、`quests.csv` 只供 `demo_app.py` 範例使用。

| 來源 | 用途 | 查閱結果 |
| --- | --- | --- |
| [魔龍數據](https://david27tainan.github.io/KargoData/) | 主要結構化資料 | 網站標示台版客戶端2.0.0，取得怪物、任務、地圖及配置公開JSON |
| [楓錄怪物資料庫](https://mapleclassictools.com/db/monster/) | 交叉參考 | 嫩寶數值、掉落與35張出沒地圖可讀；清楚聲明不提供客戶端未記錄的掉落機率 |
| [波波攻略島怪物圖鑑](https://bobogameguides.com/maplestory-classic/monsters/) | 自動數值比對 | 339隻怪物的HP／EXP共678項，671項一致，7項主要來源缺值、另一站列0；保留缺值 |
| [波波攻略島任務](https://bobogameguides.com/maplestory-classic/guides/quests.html) | 人工核對任務 | 核對2000、2001、2083、2084、2107的條件、需求及獎勵 |
| [波波攻略島練功路線](https://bobogameguides.com/maplestory-classic/guides/leveling-routes.html) | 39級僧侶候選 | 區分客戶端存在性、本服社群、他版與舊版；不把他版效率混成本服實測 |
| [4Gamers 30～40攻略](https://www.4gamers.com.tw/saged/detail/86x0we8xxmd44k) | 待驗證線索 | 文章摘要可讀，提及任務但部分未對應主資料；尚不匯入該獎勵數字，影片未觀看 |
| [楓典](https://api.maplecodex.com/) | 候選來源 | 已讀介紹頁，明確區分台版經典版與海外Classic World；未匯入其資料 |

主資料實際解析數：1,238筆怪物、9,859筆掉落關係、591個任務步驟、1,838筆地圖。這些不是已開放內容的保證數。完整研究、39級僧侶建議與待驗證缺口見根目錄 `RESEARCH.md`。

每次同步保存來源URL、時間及原始回應SHA-256；缺少的耗時、掉落機率維持null。各來源可能共同源自同一客戶端，一致不等於獨立官方驗證。只整理事實欄位，不搬運圖片或站長攻略文章。
