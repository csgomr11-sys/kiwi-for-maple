"""Project approved factual snapshots for independently implemented Kiwi tools."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build_native(catalogs,write):
    def read(name):return json.loads((ROOT/'data/catalog'/f'{name}.json').read_text())
    ids={str(r['id']) for r in catalogs['items']}
    scroll=read('scroll-simulator')
    write(Path('data/workbench/scroll.json'),{
        'equipment':[{k:r.get(k) for k in ['id','name','subcategory','image','stats']} for r in scroll['equipment'] if str(r['id']) in ids and (r.get('stats',{}).get('reqLevel') or 0)<=120],
        'scrolls':[{k:r.get(k) for k in ['id','name','target','image','successRate','destroyRate','effects']} for r in scroll['scrolls'] if str(r['id']) in ids]})
    write(Path('data/workbench/gacha.json'),read('gacha-simulator'))
    avatar=read('avatar-maker')
    write(Path('data/workbench/wardrobe.json'),{'categories':avatar['categories'],'items':[{k:r.get(k) for k in ['id','name','slot','image','cash']} for r in avatar['items'] if r['slot'] in ['Hair','Face','Chair'] or str(r['id']) in ids]})
    third=read('third-job')
    # Independently phrased prompts, not copies of site editorial content.
    prompts=json.loads((ROOT/'data/quiz_prompts.json').read_text())
    choices=json.loads((ROOT/'data/quiz_choices.json').read_text())
    write(Path('data/workbench/quiz.json'),{'classes':third['classes'],'questions':[{**{k:r.get(k) for k in ['id','answer','answerId','category','classId','entities']},'options':choices.get(str(r['id']),[]),'prompt':prompts.get(str(r['id']),'依相關NPC、地圖與職業條件辨識正確答案。')} for r in third['questions']]})
    write(Path('data/workbench/changes.json'),read('skill-changes'))
    halloween=read('halloween')
    write(Path('data/workbench/event.json'),{'chapters':halloween['chapters'],'dailyChecklist':halloween['dailyChecklist'],'quests':[q for q in catalogs['quests'] if q['name'].startswith('[萬聖節]')]})
    exp=read('exp-exchange')
    # Foreign server experience tables / Charlie prize weights are not imported.
    shoe=next((q for q in catalogs['quests'] if str(q['id'])=='2017'),None)
    write(Path('data/workbench/exchange.json'),{'materials':[{k:r.get(k) for k in ['id','name','image','batch']} for r in exp['charlie']['materials']], 'shoe':{'name':exp['shoes']['name'],'item':exp['shoes']['item'],'exp':shoe.get('completeRewards',{}).get('exp') if shoe else None,'minLevel':shoe.get('minLevel') if shoe else None}})
    write(Path('data/workbench/bosses.json'),[{'id':r['id'],'name':r['name'],'image':r.get('image'),'level':r['level'],'maps':r.get('maps',[])} for r in catalogs['monsters'] if r.get('stats',{}).get('boss')])
    write(Path('data/workbench/updates.json'),json.loads((ROOT/'data/kiwi_updates.json').read_text()))
