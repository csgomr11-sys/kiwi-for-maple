import{jobInfo,normalizeProfile}from'./character.mjs?v=quest-journal-20261022';
export const DEFAULT_PROFILE={jobId:230,attackSkill:2301002,attackLevel:7,attack:0,level:39,str:5,dex:5,int:204,luk:5,heal:7,absorb:20,teleport:1,magic:0,fame:0};
export function validProfile(p){if(!p||typeof p!=='object')return false;p=normalizeProfile(p);const bounds={level:[1,120],str:[4,9999],dex:[4,9999],int:[4,9999],luk:[4,9999],heal:[0,30],absorb:[0,20],teleport:[0,20],magic:[0,9999],attack:[0,9999],fame:[-30000,30000],attackLevel:[1,30]};const job=jobInfo(p.jobId);return !!job&&p.level>=job.minLevel&&Number.isInteger(p.attackSkill)&&(p.attackSkill===0||job.lineage.includes(Math.floor(p.attackSkill/10000)))&&Object.entries(bounds).every(([k,[lo,hi]])=>Number.isFinite(p[k])&&Number.isInteger(p[k])&&p[k]>=lo&&p[k]<=hi);}

export function eligible(q,p){if(!q||q.availability&&!q.availability.requirementsConfirmed&&q.availability.conditionSource!=='source-table')return false;const r=q.startRequirements||{};return (!q.minLevel||q.minLevel<=p.level)&&(!q.maxLevel||q.maxLevel>=p.level)&&(!r.jobs?.length||r.jobs.includes(p.jobId??230));}
export function expandPlan(quests,selected,completed=[]){const map=new Map(quests.map(q=>[String(q.id),q]));const done=new Set(completed.map(String)),out=new Set(),visiting=new Set(),missing=new Set();function visit(id){id=String(id);if(done.has(id)||out.has(id))return;if(visiting.has(id))throw Error('前置任務形成循環，請取消自動展開。');const q=map.get(id);if(!q){missing.add(id);return}visiting.add(id);for(const prev of q.startRequirements?.quests||[])if(prev.state===2)visit(prev.id);visiting.delete(id);out.add(id);}selected.forEach(visit);return{quests:[...out].map(id=>map.get(id)),missing:[...missing]};}
export function totals(quests,type){const out=new Map();for(const q of quests)for(const i of q.completeRequirements?.[type]||[])if(i.count>0){const k=String(i.id);const row=out.get(k)||{id:k,name:i.name,count:0};row.count+=i.count;out.set(k,row)}return [...out.values()].sort((a,b)=>b.count-a.count);}
export function combatResult(minutes,exp,cost){if(!(minutes>0)||!Number.isFinite(exp)||!Number.isFinite(cost))throw Error('請輸入有效的耗時、經驗與支出。');return{expPerMinute:exp/minutes,costPerMinute:cost/minutes};}
export function csv(rows){if(!rows.length)return '\ufeff';const keys=Object.keys(rows[0]);const quote=x=>'"'+String(x??'').replaceAll('"','""')+'"';return '\ufeff'+[keys.map(quote).join(','),...rows.map(r=>keys.map(k=>quote(r[k])).join(','))].join('\r\n');}
export function chooseWeighted(rows,random){const total=rows.reduce((s,x)=>s+Math.max(0,Number(x.chance)||0),0);if(!total)throw Error('這個獎池沒有可用機率。');let roll=random*total;for(const row of rows){roll-=Math.max(0,Number(row.chance)||0);if(roll<0)return row}return rows.at(-1);}
export function experienceBetween(levels,startLevel,startExp,endLevel,endExp){
 const table=new Map(levels.map(r=>[r.level,r.expToNextLevel]));
 for(const [level,exp]of[[startLevel,startExp],[endLevel,endExp]])if(!Number.isInteger(level)||!table.has(level)||!Number.isFinite(exp)||exp<0||exp>table.get(level))throw Error('等級或本級經驗超出經驗表範圍。');
 if(endLevel<startLevel)throw Error('結束等級不可低於開始等級。');
 let gained=endExp-startExp;for(let lv=startLevel;lv<endLevel;lv++){if(!table.has(lv))throw Error('經驗表缺少等級。');gained+=table.get(lv)}return gained;
}
export function experiencePlan(levels,{level,target,current=0,exp=0,minutes=10,multiplier=1,coupons=0,dailyHours=0}){
 if(!Number.isInteger(level)||!Number.isInteger(target)||target<=level||!Number.isFinite(current)||current<0||!Number.isFinite(exp)||exp<0||!Number.isFinite(minutes)||minutes<=0||!Number.isFinite(multiplier)||multiplier<1||!Number.isInteger(coupons)||coupons<0||!Number.isFinite(dailyHours)||dailyHours<0)throw Error('請檢查等級、經驗、倍率與時間設定。');
 const table=new Map(levels.map(r=>[r.level,r.expToNextLevel]));if(!table.has(target)||!table.has(level)||current>table.get(level))throw Error('等級或本級經驗超出經驗表範圍。');
 let remaining=-current;for(let lv=level;lv<target;lv++){if(!table.has(lv))throw Error('經驗表缺少等級。');remaining+=table.get(lv)}
 const rate=exp/minutes,baseMinutes=remaining===0?0:rate>0?remaining/rate:null,boostMinutes=remaining===0?0:rate>0?remaining/(rate*multiplier):null;
 const boostedOwned=rate>0?Math.min(boostMinutes,coupons*30):0;
 const ownedMinutes=remaining===0?0:rate>0?boostedOwned+Math.max(0,remaining-boostedOwned*rate*multiplier)/rate:null;
 return{remaining,levels:target-level,rate,perHour:rate*60,baseMinutes,boostMinutes,ownedMinutes,savedMinutes:baseMinutes===null?null:baseMinutes-boostMinutes,couponsNeeded:multiplier===1?0:boostMinutes===null?null:Math.ceil(boostMinutes/30),days:ownedMinutes!==null&&dailyHours>0?Math.ceil(ownedMinutes/(dailyHours*60)):null};
}
