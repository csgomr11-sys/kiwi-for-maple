"""Keep source facts and attach evidence without treating table presence as gameplay proof."""
from copy import deepcopy

REFERENCE='https://morrisrrrrrrr-svg.github.io/quests.html'

def publish_quest(raw, entry, sources):
    row=deepcopy(raw)
    base={'sourceUrl':REFERENCE+'?quest='+str(raw['id']),
          'sourceType':'楓憶當期資料表', 'reportedAt':'2026-10-15',
          'checkedAt':'2026-10-22','presenceEvidence':False,
          'requirementsConfirmed':False,'detailsConfirmed':False,
          'plannable':True,'conditionSource':'source-table',
          'notes':'條件、材料、擊殺及獎勵按楓憶資料表整理；未逐筆遊戲實測。'}
    if entry:
        source=sources[entry['source']]
        base.update(sourceUrl=source['url'],sourceType=source['type'],reportedAt=source['reportedAt'],
                    checkedAt=source['checkedAt'],presenceEvidence=True,
                    requirementsConfirmed=entry.get('requirementsConfirmed',False),notes=entry['notes'])
    row['availability']=base
    row['catalogSourceUrl']=REFERENCE+'?quest='+str(raw['id'])
    if entry:
        for k in ['minLevel','maxLevel']:
            if k in entry:row[k]=entry[k];row['startRequirements'][k]=entry[k]
    row['refs']={}
    return row
