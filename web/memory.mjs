import{nativePage,bindWorkbench,updateNativeTicks}from'./workbench.mjs?v=readability-20261022';
export const MEMORY_PAGES=[
 {id:'monsters',title:'怪物',page:'index',group:'楓葉圖鑑',icon:'assets/monster_frames/100100.png',description:'怪物搜尋、能力、出沒地圖與掉落品項。'},
 {id:'items',title:'道具',page:'items',group:'楓葉圖鑑',icon:'assets/items/2000000.png',description:'道具分類、裝備能力、取得與使用關係。'},
 {id:'quests',title:'任務',page:'quests',group:'楓葉圖鑑',icon:'assets/npcs/2005.png',description:'分類與等級搜尋，接取、前置、材料、擊殺及獎勵。'},
 {id:'maps',title:'地圖',page:'maps',group:'楓葉圖鑑',icon:'assets/map_marks/Henesys.png',description:'小地圖、生怪點、NPC 與地圖連接。'},
 {id:'skills',title:'技能',page:'skills',group:'楓葉圖鑑',icon:'assets/skills/2301002.png',description:'職業技能分類、逐級數值與技能圖示。'},
 {id:'scroll-simulator',title:'卷軸模擬器',page:'scroll-simulator',group:'實用工具',icon:'assets/items/2040407.png',description:'選裝備與卷軸，調整初始能力後模擬強化。'},
 {id:'damage-calculator',title:'戰鬥力計算機',page:'damage-calculator',group:'實用工具',icon:'assets/skills/1121002.png',description:'沿用職業與技能，以實測傷害估計擊殺次數。'},
 {id:'combat-analysis',title:'戰鬥分析',page:'combat-analysis',group:'實用工具',icon:'assets/meso/gold.png',description:'輸入戰鬥期間與經驗，分析練功效率。'},
 {id:'avatar-maker',title:'角色外觀搭配',page:'avatar-maker',group:'實用工具',icon:'assets/items/5150040.png',description:'依部位查外觀，按角色保存搭配收藏。'},
 {id:'boss-timer',title:'Boss 計時器',page:'boss-timer',group:'實用工具',icon:'assets/monster_frames/6130101.png',description:'選擇 Boss、頻道與時間，追蹤重生倒數。'},
 {id:'gacha-simulator',title:'轉蛋模擬器',page:'gacha-simulator',group:'實用工具',icon:'assets/items/5222214.png',description:'選擇獎池與次數，模擬抽取及查看結果。'},
 {id:'third-job',title:'三轉題庫',page:'third-job',group:'實用工具',icon:'assets/items/4031058.png',description:'搜尋三轉試題、答案與關聯對象。'},
 {id:'goddess-tower',title:'女神組隊',page:'goddess-tower',group:'實用工具',icon:'assets/items/4001158.png',description:'關卡流程、每日唱盤與組隊解題參考。'},
 {id:'exp-exchange',title:'經驗物工具',page:'exp-exchange',group:'實用工具',icon:'assets/items/4001000.png',description:'依實際EXP需求，試算材料兌換與升級進度。'},
 {id:'skill-changes',title:'技改資訊',page:'skill-changes',group:'其他',icon:'assets/skills/1001004.png',description:'比較職業技能的修改內容與數值。'},
 {id:'halloween',title:'萬聖節活動',page:'halloween',group:'其他',icon:'assets/items/1012939.png',description:'雪原面具祭典的任務、日程、需求與獎勵。'},
 {id:'patch-notes',title:'遊戲更新日誌',page:'patch-notes',group:'其他',icon:'assets/map_marks/Event.png',description:'依日期查閱遊戲更新與版本變化。'},
 {id:'web-changelog',title:'網頁更新日誌',page:'web-changelog',group:'其他',icon:'assets/map_marks/Quest.png',description:'查閱 Kiwi Maple 的功能與介面更新。'},
];
export function interfaceIcon(id,cls=''){return `<svg class="interface-icon ${cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><use href="icons.svg#${id}"></use></svg>`}
export const NATIVE_DATABASES=new Set(['monsters','items','quests','maps','skills']);
export const memoryRoute=p=>p.id;
export function sourceSwitch(){return ''}
export async function memoryPage(route,c){return nativePage(route.replace(/^source-/,''),c)}
export function memoryOverview(c){const{heading,e}=c;return heading('圖鑑與工具','Kiwi Maple 的資料查詢、角色規劃與遊戲工具。')+['楓葉圖鑑','實用工具','其他'].map(group=>`<section class="memory-group"><h2>${group}</h2><div class="memory-grid">${MEMORY_PAGES.filter(p=>p.group===group).map(p=>`<a class="memory-card" href="#${p.id}"><span class="memory-card-icon">${interfaceIcon(p.id)}</span><span><strong>${e(p.id==='avatar-maker'?'角色外觀搭配':p.title)}</strong><small>${e(p.description)}</small></span><span class="memory-card-arrow">→</span></a>`).join('')}</div></section>`).join('')}
export function bindMemory(c){bindWorkbench(c).catch(err=>c.toast(err.message))}
export {updateNativeTicks};
