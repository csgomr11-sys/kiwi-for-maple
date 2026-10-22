import{attackMode}from'./character.mjs?v=quest-journal-20261022';
// Conservative recommendations from the published V002 map/spawn projection.
// These rules choose safe starting candidates; they do not estimate damage or EXP/hour.
export function recommendTraining(areas,profile){
 const mode=attackMode(profile),heal=mode==='heal',skillLevel=profile.attackLevel??profile.heal??1,softHp=heal?(skillLevel<16?800:skillLevel<25?1500:3000):Math.max(100,profile.level*25*(skillLevel>=15?2:1.2));
 const choices=new Map();
 for(const area of areas){
  if(area.unknownSpawns||!area.monsters.length)continue;
  const total=area.monsters.reduce((sum,m)=>sum+m.count,0);
  for(const monster of area.monsters){
   if(heal&&!monster.undead||monster.boss||!monster.hp||!monster.count||monster.level<Math.max(1,profile.level-18)||monster.level>profile.level+1)continue;
   const others=area.monsters.filter(m=>m.id!==monster.id);
   if(others.some(m=>m.boss||m.level>profile.level+3))continue;
   const burden=((area.width||5000)+2*(area.height||2500))/1000;
   const score=monster.count/total*(heal?35:20)+Math.log1p(monster.count)*5-burden*(mode==='ranged'?1:mode==='melee'?3:profile.teleport<=1?3:1);
   const option={map:area,monster,others,share:monster.count/total,score,
    tier:monster.hp<=softHp?0:monster.hp<=softHp*2?1:2};
   const previous=choices.get(monster.id);
   if(!previous||score>previous.score)choices.set(monster.id,option);
  }
 }
 return [...choices.values()].sort((a,b)=>a.tier-b.tier||Math.abs(a.monster.level-(profile.level-1))-Math.abs(b.monster.level-(profile.level-1))||b.score-a.score).slice(0,3);
}
