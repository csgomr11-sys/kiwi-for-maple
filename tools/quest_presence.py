"""Record-level presence evidence, deliberately separate from client parsing."""
from copy import deepcopy

def publish_quest(raw, entry, sources):
    row=deepcopy(raw);source=sources[entry['source']]
    row['availability']={'presenceEvidence':True,'sourceUrl':source['url'],'sourceType':source['type'],
        'checkedAt':source['checkedAt'],'reportedAt':source['reportedAt'],
        'requirementsConfirmed':entry.get('requirementsConfirmed',False),'detailsConfirmed':False,
        'plannable':False,'notes':entry['notes']}
    row['minLevel']=entry.get('minLevel');row['maxLevel']=entry.get('maxLevel')
    for stage in ['startRequirements','completeRequirements']:
        row[stage]={'npc':None,'minLevel':None,'maxLevel':None,'jobs':[],'quests':[],'items':[],'monsters':[],'skills':[]}
    row['startRequirements'].update(minLevel=row['minLevel'],maxLevel=row['maxLevel'])
    approved={str(m['id']):m['count'] for m in entry.get('materials',[])}
    row['completeRequirements']['items']=[{k:m.get(k) for k in ['id','name','count','image']} for m in raw.get('completeRequirements',{}).get('items',[]) if str(m['id']) in approved and m['count']==approved[str(m['id'])]]
    for stage in ['startRewards','completeRewards']:
        row[stage]={'exp':None,'money':None,'pop':None,'items':[],'skills':[]}
    if entry['source'] in ['snail','official-event']:row['startNpc']=None;row['endNpc']=None
    if str(row['id'])=='506372':row['startRequirements']['quests']=[{'id':'506371','name':'[萬聖節] 今天的新客人','state':2,'stateLabel':'已完成'}]
    if str(row['id'])=='506374':row['startRequirements']['quests']=[{'id':'506373','name':'[萬聖節] 休息站的守火人','state':2,'stateLabel':'已完成'}]
    row['refs']={};row['nextQuest']=None;row['dependentQuests']=[]
    return row
