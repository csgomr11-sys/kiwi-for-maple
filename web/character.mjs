export const JOBS=[
 [0,'初心者',1,[]],[100,'劍士',10,[0]],[110,'狂戰士',30,[0,100]],[111,'十字軍',70,[0,100,110]],
 [120,'見習騎士',30,[0,100]],[121,'騎士',70,[0,100,120]],[130,'槍騎兵',30,[0,100]],[131,'龍騎士',70,[0,100,130]],
 [200,'法師',8,[0]],[210,'火毒法師',30,[0,200]],[211,'火毒魔導士',70,[0,200,210]],
 [220,'冰雷法師',30,[0,200]],[221,'冰雷魔導士',70,[0,200,220]],[230,'僧侶',30,[0,200]],[231,'祭司',70,[0,200,230]],
 [300,'弓箭手',10,[0]],[310,'獵人',30,[0,300]],[311,'遊俠',70,[0,300,310]],[320,'弩弓手',30,[0,300]],[321,'狙擊手',70,[0,300,320]],
 [400,'盜賊',10,[0]],[410,'刺客',30,[0,400]],[411,'暗殺者',70,[0,400,410]],[420,'俠盜',30,[0,400]],[421,'神偷',70,[0,400,420]],
 [500,'海盜',10,[0]],[510,'打手',30,[0,500]],[511,'格鬥家',70,[0,500,510]],[520,'槍手',30,[0,500]],[521,'神槍手',70,[0,500,520]]
].map(([id,name,minLevel,parents])=>({id,name,minLevel,lineage:[...parents,id]}));
export const jobInfo=id=>JOBS.find(j=>j.id===Number(id));
export const jobName=profile=>jobInfo(profile.jobId??230)?.name||'未知職業';
export function normalizeProfile(p){if(!p||typeof p!=='object')return p;const jobId=p.jobId??230,attackSkill=p.attackSkill??([230,231].includes(jobId)&&p.heal>0?2301002:0);return{...p,jobId,attackSkill,attackLevel:p.attackLevel??(attackSkill===2301002?p.heal:1),attack:p.attack??0};}

export function availableAttacks(skills,jobId){const job=jobInfo(jobId);return [{id:0,name:'普通攻擊',jobId:Number(jobId),maxLevel:1,levels:[]},...skills.filter(s=>job?.lineage.includes(Number(s.jobId))&&s.attack)];}
export function defaultAttack(skills,jobId){const choices=availableAttacks(skills,jobId),preferred={100:1001004,200:2001005,230:2301002,231:2301002,400:4001344,410:4001344,411:4001344,420:4201005,421:4201005,520:5001003,521:5001003};return choices.find(s=>Number(s.id)===preferred[jobId])||[...(jobInfo(jobId)?.lineage||[])].reverse().flatMap(id=>choices.filter(s=>Number(s.jobId)===id&&Number(s.id)!==0))[0]||choices[0];}
export function attackMode(profile){if([0,4001334].includes(Number(profile.attackSkill)))return 'melee';if(Number(profile.attackSkill)===5001003)return 'ranged';if(Number(profile.attackSkill)===2301002&&[230,231].includes(Number(profile.jobId)))return 'heal';const family=Math.floor(Number(profile.jobId)/100);if(family===2)return 'magic';if([300,310,311,320,321,410,411,520,521].includes(Number(profile.jobId))||Number(profile.attackSkill)===4001344)return 'ranged';return 'melee';}
export function characterState(save){return Object.fromEntries(['profile','selected','completed','favorites','records','timers','workbench'].map(k=>[k,save[k]]));}
export function stashCharacter(save){const current=save.characters?.find(c=>c.id===save.activeCharacter);if(current)Object.assign(current,characterState(save));}
