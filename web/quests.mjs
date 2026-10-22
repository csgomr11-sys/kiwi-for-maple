import {JOBS} from './character.mjs?v=quest-journal-20261022';
const state={query:'',category:'',progress:'all',onlyRole:false,min:'',max:'',selected:null,showUnnamed:false};
const jobNames=new Map(JOBS.map(j=>[j.id,j.name]));
const levelText=q=>q.minLevel!=null?`Lv.${q.minLevel}${q.maxLevel!=null?'–'+q.maxLevel:' 起'}`:q.maxLevel!=null?`Lv.${q.maxLevel} 以下`:'等級未列';

export function questDetailHtml(q,c){
 const {e,fmt,image,questCompletion,save,link}=c;
 const req=q.completeRequirements||{},start=q.startRequirements||{},rewards=q.completeRewards||{},npc=q.startNpc||q.endNpc;
 const items=(rows,kind='items')=>rows?.length?`<div class="quest-objects">${rows.map(r=>`<div class="quest-object">${image(r.image,'quest-object-icon')}<span>${link(kind,r.id,r.name)}${r.choice||r.random?'<small>隨機／選一候選</small>':''}</span><strong>${r.count!=null?'× '+fmt(r.count):''}</strong></div>`).join('')}</div>`:'<p class="quest-none">來源未列</p>';
 const place=(n,title)=>`<div class="quest-npc"><div class="quest-npc-art">${image(n?.image)}</div><div><small>${title}</small><strong>${e(n?.name||'來源未列')}</strong><span>${e(n?.locationText||'地點未列')}</span></div></div>`;
 const conditions=[];
 if(q.minLevel!=null||q.maxLevel!=null)conditions.push(['等級',levelText(q)]);
 if(start.jobs?.length)conditions.push(['職業',start.jobs.map(id=>jobNames.get(id)||'職業 '+id).join('、')]);
 if(start.pop!=null)conditions.push(['名聲',fmt(start.pop)]);
 if(start.gender!=null)conditions.push(['性別',start.gender===0?'男性':start.gender===1?'女性':String(start.gender)]);
 const predecessors=(start.quests||[]).map(p=>`<div class="quest-chain-step">${link('quests',p.id,p.name)}<small>${e(save.completed.includes(String(p.id))?'已完成 ✓':p.state===2?'需先完成':p.state===0?'需未開始':p.stateLabel||'條件狀態 '+p.state)}</small></div>`).join('');
 const follows=[q.nextQuest,...(q.dependentQuests||[])].filter(Boolean),seen=new Set();
 const next=follows.filter(p=>{const id=String(p.id);if(seen.has(id))return false;seen.add(id);return true});
 const rewardItems=(rewards.items||[]).filter(r=>r.action!=='remove');
 const removed=(rewards.items||[]).filter(r=>r.action==='remove');
 const selected=save.selected.includes(String(q.id));
 return `<div class="quest-detail-heading"><div class="quest-portrait">${image(npc?.image)}</div><div><div class="quest-kicker">${e(q.category)} · ${e(levelText(q))}</div><h2>${e(q.name)}</h2><p>${e(q.parent||'任務手札')} <span>＃${e(q.id)}</span></p></div></div>
 <div class="quest-detail-actions">${questCompletion(q.id,q.name)}<button class="${selected?'secondary':'primary'}" data-plan="${e(q.id)}">${selected?'已加入材料清單 ✓':'加入材料清單 ＋'}</button></div>
 <div class="quest-reward-summary">${[['完成經驗',rewards.exp,'EXP'],['楓幣增減',rewards.money,'楓幣'],['名聲',rewards.pop,'']].map(([label,n,unit])=>`<div><small>${label}</small><strong>${fmt(n)}</strong><span>${unit}</span></div>`).join('')}</div>
 <section class="quest-section"><h3><span>⌖</span> 接取與交付</h3><div class="quest-npc-grid">${place(q.startNpc,'接取 NPC')}${place(q.endNpc,'交付 NPC')}</div></section>
 <section class="quest-section"><h3><span>☷</span> 接取條件</h3>${conditions.length?`<dl class="quest-conditions">${conditions.map(([k,v])=>`<dt>${e(k)}</dt><dd>${e(v)}</dd>`).join('')}</dl>`:'<p class="quest-none">來源未列額外條件</p>'}${predecessors?`<h4>前置任務</h4><div class="quest-chain">${predecessors}</div>`:''}${start.items?.length?`<h4>接取時需持有</h4>${items(start.items)}`:''}${start.skills?.length?`<h4>技能條件</h4>${items(start.skills,'skills')}`:''}</section>
 <div class="quest-requirements-grid"><section class="quest-section"><h3><span>◇</span> 繳交材料</h3>${items(req.items)}</section><section class="quest-section"><h3><span>⚔</span> 擊殺需求</h3>${items(req.monsters,'monsters')}</section></div>
 <section class="quest-section"><h3><span>✦</span> 完成獎勵</h3>${items(rewardItems)}${removed.length?`<details class="quest-secondary-details"><summary>任務回收道具（非獎勵）</summary>${items(removed)}</details>`:''}${rewards.skills?.length?`<h4>技能獎勵</h4>${items(rewards.skills,'skills')}`:''}</section>
 ${q.startRewards?.items?.length?`<section class="quest-section"><h3><span>↗</span> 接取時取得／回收</h3>${items(q.startRewards.items.filter(r=>r.action!=='remove'))}${q.startRewards.money!=null?`<p>楓幣增減 ${fmt(q.startRewards.money)}</p>`:''}${q.startRewards.items.some(r=>r.action==='remove')?`<h4>回收</h4>${items(q.startRewards.items.filter(r=>r.action==='remove'))}`:''}</section>`:''}
 ${next.length?`<section class="quest-section"><h3><span>→</span> 後續任務</h3><div class="quest-chain">${next.map(p=>`<div class="quest-chain-step">${link('quests',p.id,p.name)}</div>`).join('')}</div></section>`:''}
 <details class="quest-source"><summary>資料來源與核對紀錄</summary><p><a target="_blank" rel="noopener" href="${e(q.catalogSourceUrl||'https://morrisrrrrrrr-svg.github.io/quests.html?quest='+q.id)}">楓憶任務原頁 ↗</a> · 2.0.0 資料表，依台版 V002 範圍整理。</p><p>條件與數值按來源記錄呈現，未逐筆遊戲實測；未列不等於沒有。隨機／選一候選不能全部視為必得。</p>${q.availability?.presenceEvidence?`<p><a target="_blank" rel="noopener" href="${e(q.availability.sourceUrl)}">${e(q.availability.sourceType)} ↗</a> · ${e(q.availability.reportedAt)}<br>${e(q.availability.notes)}</p>`:''}</details>`;
}

export async function questPage(c){
 const {data,detail,e,fmt,image,heading,save,eligible}=c;
 const all=await data('quests');
 let rows=all.filter(q=>`${q.name} ${q.id} ${q.category} ${q.parent||''} ${q.startNpc?.name||''} ${q.startNpc?.locationText||''} ${q.searchTerms||''}`.toLowerCase().includes(state.query.toLowerCase()));
 if(!state.showUnnamed)rows=rows.filter(q=>!/^任務\s*\d+$/.test(q.name));
 if(state.category)rows=rows.filter(q=>q.category===state.category);
 if(state.progress!=='all')rows=rows.filter(q=>save.completed.includes(String(q.id))===(state.progress==='completed'));
 if(state.min!=='')rows=rows.filter(q=>q.minLevel!=null&&q.minLevel>=Number(state.min));
 if(state.max!=='')rows=rows.filter(q=>q.minLevel!=null&&q.minLevel<=Number(state.max));
 if(state.onlyRole)rows=rows.filter(q=>eligible(q,save.profile));
 rows.sort((a,b)=>(a.minLevel??0)-(b.minLevel??0)||a.name.localeCompare(b.name,'zh-Hant'));
 if(!rows.some(q=>String(q.id)===state.selected))state.selected=rows[0]?String(rows[0].id):null;
 const current=state.selected?await detail('quests',state.selected):null;
 const categories=[...new Set(all.map(q=>q.category))];
 const completed=all.filter(q=>save.completed.includes(String(q.id))).length;
 return heading('任務手札','查任務、找材料、看獎勵，把每一步冒險整理好。')+`<div class="quest-overview"><div><strong>${fmt(all.length)}</strong><span>收錄任務</span></div><div><strong>${fmt(completed)}</strong><span>已完成</span></div><div><strong>${fmt(all.length-completed)}</strong><span>未完成</span></div><a href="https://morrisrrrrrrr-svg.github.io/quests.html" target="_blank" rel="noopener">資料參考：楓憶 ↗</a></div>
 <div class="quest-workspace"><aside class="quest-browser" aria-label="任務列表"><div class="quest-filters"><div class="search"><input id="quest-search" type="search" aria-label="搜尋任務" placeholder="搜尋任務、NPC、材料或怪物…" value="${e(state.query)}"></div><div class="quest-filter-row"><select id="quest-category" aria-label="任務分類"><option value="">全部分類</option>${categories.map(v=>`<option ${v===state.category?'selected':''}>${e(v)}</option>`).join('')}</select><select id="quest-status" aria-label="任務進度">${[['all','全部進度'],['incomplete','未完成'],['completed','已完成']].map(([v,n])=>`<option value="${v}" ${v===state.progress?'selected':''}>${n}</option>`).join('')}</select></div><div class="quest-filter-row"><input id="quest-min" type="number" min="0" max="120" aria-label="任務最低等級" placeholder="最低等級" value="${e(state.min)}"><span>—</span><input id="quest-max" type="number" min="0" max="120" aria-label="任務最高等級" placeholder="最高等級" value="${e(state.max)}"></div><label class="check"><input id="quest-role" type="checkbox" ${state.onlyRole?'checked':''}>依我的等級／職業篩選</label><label class="check"><input id="quest-unnamed" type="checkbox" ${state.showUnnamed?'checked':''}>顯示未命名索引</label><div class="quest-list-meta"><span>${fmt(rows.length)} 個任務</span><button id="quest-reset" class="inline-link">清除條件</button></div></div>
 <div class="quest-index" role="list">${rows.map(q=>`<div class="quest-index-entry ${String(q.id)===state.selected?'active':''}" role="listitem"><button class="quest-pick" data-quest-select="${e(q.id)}" aria-current="${String(q.id)===state.selected}"><span class="quest-index-art">${image(q.startNpc?.image||q.endNpc?.image)}</span><span class="quest-index-text"><strong>${e(q.name)}</strong><small>${e(q.category)} · ${e(levelText(q))}</small><span>${e(q.startNpc?.name||q.parent||'任務')} ${q.startNpc?.locationText?'· '+e(q.startNpc.locationText):''}</span></span></button><label class="quest-index-check" title="標示已完成"><input type="checkbox" data-quest-completed="${e(q.id)}" aria-label="${e(q.name)} 已完成" ${save.completed.includes(String(q.id))?'checked':''}></label></div>`).join('')||'<div class="empty">沒有符合的任務。<br>可以調整搜尋或篩選條件。</div>'}</div></aside>
 <article id="quest-reader" class="quest-reader" aria-label="任務詳情">${current?questDetailHtml(current,c):'<div class="empty">選擇左側任務，查看條件、材料與獎勵。</div>'}</article></div>`;
}

export function bindQuestPage(c){
 const {bindSearchInput,render,$}=c;
 bindSearchInput('#quest-search',v=>{state.query=v});
 for(const [id,key]of[['quest-category','category'],['quest-status','progress'],['quest-min','min'],['quest-max','max']]){const el=$('#'+id);if(el)el.onchange=()=>{state[key]=el.value;render({search:true})}}
 if($('#quest-unnamed'))$('#quest-unnamed').onchange=event=>{state.showUnnamed=event.target.checked;render({search:true})};
 if($('#quest-role'))$('#quest-role').onchange=event=>{state.onlyRole=event.target.checked;render({search:true})};
 if($('#quest-reset'))$('#quest-reset').onclick=()=>{Object.assign(state,{query:'',category:'',progress:'all',onlyRole:false,min:'',max:'',showUnnamed:false});render({search:true})};
 document.querySelectorAll('[data-quest-select]').forEach(button=>button.onclick=async()=>{const top=$('.quest-index').scrollTop;state.selected=button.dataset.questSelect;await render({search:true});if($('.quest-index'))$('.quest-index').scrollTop=top;if(innerWidth<900)$('#quest-reader')?.scrollIntoView({behavior:'smooth',block:'start'})});
}
