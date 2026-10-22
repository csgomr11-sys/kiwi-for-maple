const ROOT='https://morrisrrrrrrr-svg.github.io/';
export const MEMORY_PAGES=[
 {id:'monsters',title:'怪物',page:'index',group:'楓葉圖鑑',icon:'assets/monster_frames/100100.png',description:'怪物搜尋、能力、出沒地圖與掉落品項。'},
 {id:'items',title:'道具',page:'items',group:'楓葉圖鑑',icon:'assets/items/2000000.png',description:'道具分類、裝備能力、取得與使用關係。'},
 {id:'quests',title:'任務',page:'quests',group:'楓葉圖鑑',icon:'assets/npcs/2005.png',description:'分類與等級搜尋，接取、前置、材料、擊殺及獎勵。'},
 {id:'maps',title:'地圖',page:'maps',group:'楓葉圖鑑',icon:'assets/map_marks/Henesys.png',description:'小地圖、生怪點、NPC 與地圖連接。'},
 {id:'skills',title:'技能',page:'skills',group:'楓葉圖鑑',icon:'assets/skills/2301002.png',description:'職業技能分類、逐級數值與技能圖示。'},
 {id:'scroll-simulator',title:'卷軸模擬器',page:'scroll-simulator',group:'實用工具',icon:'assets/items/2040407.png',description:'選裝備與卷軸，調整初始能力後模擬強化。'},
 {id:'damage-calculator',title:'戰鬥力計算機',page:'damage-calculator',group:'實用工具',icon:'assets/skills/1121002.png',description:'職業、技能、面板與怪物條件的戰鬥試算。'},
 {id:'combat-analysis',title:'戰鬥分析',page:'combat-analysis',group:'實用工具',icon:'assets/meso/gold.png',description:'輸入戰鬥期間與經驗，分析練功效率。'},
 {id:'avatar-maker',title:'線上紙娃娃',page:'avatar-maker',group:'實用工具',icon:'assets/items/5150040.png',description:'選擇身體、髮型、臉型與裝備，預覽外觀。'},
 {id:'boss-timer',title:'Boss 計時器',page:'boss-timer',group:'實用工具',icon:'assets/monster_frames/6130101.png',description:'選擇 Boss、頻道與時間，追蹤重生倒數。'},
 {id:'gacha-simulator',title:'轉蛋模擬器',page:'gacha-simulator',group:'實用工具',icon:'assets/items/5222214.png',description:'選擇獎池與次數，模擬抽取及查看結果。'},
 {id:'third-job',title:'三轉題庫',page:'third-job',group:'實用工具',icon:'assets/items/4031058.png',description:'搜尋三轉試題、答案與關聯對象。'},
 {id:'goddess-tower',title:'女神組隊',page:'goddess-tower',group:'實用工具',icon:'assets/items/4001158.png',description:'關卡流程、每日唱盤與組隊解題參考。'},
 {id:'exp-exchange',title:'經驗物工具',page:'exp-exchange',group:'實用工具',icon:'assets/items/4001000.png',description:'經驗物、兌換與目標等級數量試算。'},
 {id:'skill-changes',title:'技改資訊',page:'skill-changes',group:'其他',icon:'assets/skills/1001004.png',description:'比較職業技能的修改內容與數值。'},
 {id:'halloween',title:'萬聖節活動',page:'halloween',group:'其他',icon:'assets/items/1012939.png',description:'雪原面具祭典的任務、日程、需求與獎勵。'},
 {id:'patch-notes',title:'遊戲更新日誌',page:'patch-notes',group:'其他',icon:'assets/map_marks/Event.png',description:'依日期查閱遊戲更新與版本變化。'},
 {id:'web-changelog',title:'網頁更新日誌',page:'web-changelog',group:'其他',icon:'assets/map_marks/Quest.png',description:'查閱楓憶資料庫與工具的更新紀錄。'},
];
export const NATIVE_DATABASES=new Set(['monsters','items','quests','maps','skills']);
export const memoryRoute=p=>NATIVE_DATABASES.has(p.id)?'source-'+p.id:p.id;
export function sourceSwitch(id,{e}){const p=MEMORY_PAGES.find(p=>p.id===id);return p?`<div class="source-switch"><span>本站資料與個人紀錄</span><a href="#${memoryRoute(p)}">查看楓憶完整原頁 ↗</a></div>`:''}
export function memoryPage(route,c){
 const {heading,e,image}=c;
 const id=route.replace(/^source-/,''),p=MEMORY_PAGES.find(p=>p.id===id);
 if(!p)return memoryOverview(c);
 const url=ROOT+p.page+'.html';
 return heading(p.title,p.description)+`<div class="memory-toolbar"><div class="memory-origin">${image(p.icon)}<span>楓憶原頁 · 未套用本站當期版本篩選</span></div><div>${NATIVE_DATABASES.has(p.id)?`<a class="secondary" href="#${p.id}">回本站${p.title==='任務'?'任務手札':p.title+'資料'} →</a>`:''}<a class="secondary" href="${url}" target="_blank" rel="noopener">另開完整原頁 ↗</a><button class="secondary" id="memory-fullscreen">全螢幕 ⛶</button></div></div><div class="memory-frame-shell"><iframe id="memory-frame" title="楓憶 ${e(p.title)}" src="${url}" loading="eager" referrerpolicy="strict-origin-when-cross-origin" allow="display-capture; clipboard-write; fullscreen"></iframe></div><p class="memory-source-note">此區由楓憶原站提供介面、資料與運算，包含原站列出的參考值；未套用本站的 V002 範圍篩選。本站角色、任務勾選與材料清單獨立保存。<a href="#memory">查看全部 18 個入口 →</a></p>`;
}
export function memoryOverview(c){
 const{heading,e,image}=c;
 return heading('楓憶圖鑑與工具','18 個入口已逐頁檢視，保留可操作原頁與來源；任務另有個人完成紀錄。')+['楓葉圖鑑','實用工具','其他'].map(group=>`<section class="memory-group"><h2>${group}</h2><div class="memory-grid">${MEMORY_PAGES.filter(p=>p.group===group).map(p=>`<a class="memory-card" href="#${memoryRoute(p)}"><span class="memory-card-icon">${image(p.icon)}</span><span><strong>${e(p.title)}</strong><small>${e(p.description)}</small></span><span class="memory-card-arrow">↗</span></a>`).join('')}</div></section>`).join('')+`<p class="memory-source-note">2026/10/22 已檢視各頁的結構、控制項與桌面畫面。<a href="data/interface-review.json" target="_blank">逐頁檢查紀錄 ↗</a></p>`;
}
export function bindMemory(c){const b=document.querySelector('#memory-fullscreen');if(b)b.onclick=async()=>{try{await document.querySelector('.memory-frame-shell').requestFullscreen()}catch{c.toast('此瀏覽器不支援全螢幕，可另開完整原頁。')}}}
