"""Publication checks against real retained snapshots and adversarial source cases."""
import json
from pathlib import Path
import sys
from functools import lru_cache
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from version_scope import map_scope

class VersionScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site=ROOT/'site/data'
        cls.audit=json.loads((cls.site/'version-audit.json').read_text())
        cls.datasets={k:json.loads((cls.site/(k+'.json')).read_text()) for k in ['maps','monsters','quests','items']}

    def test_map_ids_do_not_override_unknown_or_later_region_evidence(self):
        self.assertEqual(map_scope({'id':270010100,'name':'後期地圖','regionName':'時間神殿'})[0],'excluded')
        self.assertEqual(map_scope({'id':200082300,'name':'天空之塔','mapDataMissing':True})[0],'pending')
        self.assertEqual(map_scope({'id':211041600,'name':'廢棄礦坑Ⅱ'})[0],'pending')

    def test_foreign_rates_and_server_formulas_are_absent_from_published_details(self):
        for kind in self.datasets:
            for p in (self.site/(kind+'-detail')).glob('*.json'):
                content=p.read_text().lower()
                for forbidden in ['"droprates"','"mesodrop"','tmsv113','heavenms','maplelandhub','historicalcharlie']:
                    self.assertNotIn(forbidden,content,str(p))

    def test_every_published_drop_and_quest_item_link_resolves(self):
        @lru_cache(maxsize=None)
        def read_bucket(path):return json.loads(path.read_text())
        def exists(kind,item_id):
            p=self.site/(kind+'-detail')/(str(int(item_id)//1000)+'.json')
            return p.exists() and str(item_id) in read_bucket(p)
        for m in self.datasets['monsters']:
            details=json.loads((self.site/'monsters-detail'/(str(int(m['id'])//1000)+'.json')).read_text())[m['id']]
            for drop in details['drops']:self.assertTrue(exists('items',drop['id']),(m['id'],drop['id']))
            for area in details['maps']:self.assertTrue(exists('maps',area['id']))
        quests={str(q['id']) for q in self.datasets['quests']}
        for q in self.datasets['quests']:
            for prev in q['startRequirements']['quests']:
                if prev['state']==2:self.assertIn(str(prev['id']),quests)
            for stage in ['startRequirements','completeRequirements','startRewards','completeRewards']:
                for item in (q.get(stage) or {}).get('items',[]):self.assertTrue(exists('items',item['id']),(q['id'],item['id']))

    def test_audit_covers_source_rows_and_keeps_provenance_limitations(self):
        for kind,summary in self.audit['summary'].items():
            self.assertEqual(summary['total'],sum(summary.get(s,0) for s in ['scoped','pending','excluded']))
            self.assertEqual(len(self.datasets[kind]),summary.get('scoped',0))
        self.assertEqual(self.audit['crossChecks']['conflicts'],[])
        self.assertTrue(self.audit['limitations'])
        levels=json.loads((self.site/'exp-exchange.json').read_text())['levels']
        self.assertEqual(levels,[])
        self.assertEqual(json.loads((self.site/'gacha-simulator.json').read_text())['records'],[])
