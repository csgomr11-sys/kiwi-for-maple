export function useScroll(equipment,scroll,random=Math.random){
 if(equipment.destroyed||equipment.slots<1)throw Error('裝備已損壞或沒有可用次數。');
 const next={...equipment,stats:{...equipment.stats},slots:equipment.slots-1};
 const success=random()<scroll.successRate/100;
 const destroyed=!success&&random()<(scroll.destroyRate||0)/100;
 if(success)for(const[k,v]of Object.entries(scroll.effects||{}))next.stats[k]=(next.stats[k]||0)+v;
 return{...next,destroyed,result:success?'成功':destroyed?'失敗並損壞':'失敗'};
}
export function validScroll(equipment,scroll){const target=scroll.target||'';return target===equipment.subcategory||(target==='全身盔甲'&&equipment.subcategory==='套服')||(target==='套服'&&equipment.subcategory==='全身盔甲')}
export function drawPrizes(prizes,count,random=Math.random){if(!Number.isInteger(count)||count<1||count>10000)throw Error('次數需介於1至10000。');const total=prizes.reduce((s,p)=>s+Math.max(0,Number(p.chance)||0),0);if(!(total>0))throw Error('這個分組缺少可用機率。');const result=new Map();for(let i=0;i<count;i++){let n=random()*total;let picked=prizes.at(-1);for(const p of prizes){n-=Math.max(0,Number(p.chance)||0);if(n<0){picked=p;break}}const key=String(picked.id??picked.itemId??picked.name);const row=result.get(key)||{...picked,count:0};row.count++;result.set(key,row)}return[...result.values()].sort((a,b)=>b.count-a.count)}
export const towerPatterns=()=>Array.from({length:6},(_,a)=>Array.from({length:6-a},(_,b)=>[a,b,5-a-b])).flat();
export function towerCandidates(history){return towerPatterns().filter(pattern=>history.every(h=>pattern.filter((n,i)=>n===h.pattern[i]).length===h.correct))}
export function measuredDamage(hp,min,max,seconds=1,hits=1){if(!(hp>0&&min>0&&max>=min&&seconds>0&&hits>=1))throw Error('請填寫有效的怪物HP與實測傷害。');return{best:Math.ceil(hp/(max*hits)),worst:Math.ceil(hp/(min*hits)),average:Math.ceil(hp/((min+max)/2*hits)),seconds:Math.ceil(hp/((min+max)/2*hits))*seconds,dps:(min+max)/2*hits/seconds}}
export function exchangeTotals(materials,quantities,expPerBatch,shoes,shoeExp){if(!Number.isFinite(expPerBatch)||expPerBatch<0||!Number.isInteger(shoes)||shoes<0)throw Error('請輸入有效的兌換數值。');const rows=materials.map(m=>{const n=Number(quantities[m.id]||0);if(!Number.isInteger(n)||n<0)throw Error('材料數量需為非負整數。');return{...m,count:n,batches:Math.floor(n/m.batch),left:n%m.batch}});const batches=rows.reduce((s,r)=>s+r.batches,0);return{rows,batches,shoeExp:shoes*(shoeExp||0),exp:batches*expPerBatch+shoes*(shoeExp||0)}}
