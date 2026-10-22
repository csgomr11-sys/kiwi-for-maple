# 資料來源限制（2026-10-22 使用者修正）

往後遊戲資料只從以下四處取得：

1. https://maplestoryclassic.beanfun.com/Main — 台版官網；包含官網直接連結的官方活動公告及 EventAd API。
2. https://forum.gamer.com.tw/B.php?bsn=85994 — 只限 85994 專板。
3. https://bobogameguides.com/maplestory-classic/ — 只限經典版專區。
4. https://morrisrrrrrrr-svg.github.io/index.html — 楓憶，取代已取消的楓錄。

`tools/source_policy.py` 對更新下載與轉址檢查網址；舊 Kargo 更新器會停止，歷史檔案僅保留追溯，不作新的實裝證據。楓憶仍可整理資料，但客戶端收錄、相同數值或版本範圍符合，都不能直接證明台版當期任務已開放。

本次任務修正：移除使用者回報未實裝的「內拉的夢」2103，連帶暫停依賴任務 2104。其餘沒有實裝證據的任務轉入待確認，不刪除個人完成紀錄。現有 23 筆公開任務是部分清單：包含官方活動與組隊公告，以及波波整理的台版玩家回報；後者多為 V001 舊日期，不能宣稱全部已在 V002 重新實測。未確認接取條件、材料與獎勵保留未知，暫停自動收益與材料規劃。

逐筆證據、日期與限制在 `data/quest_availability.json` 及網站「版本審核」頁。未取得證據前，不宣稱全任務資料已完成。
