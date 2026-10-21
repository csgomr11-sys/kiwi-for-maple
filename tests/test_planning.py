import copy
import json
from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest
from planning import eligible, required_quests, requirement_totals, hunting_maps, item_sources

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/classic.json').read_text())

class PlanningTests(unittest.TestCase):
    def test_cleric_level_limits(self):
        ids = {q['id'] for q in eligible(DATA['quests'], 39, '僧侶')}
        self.assertIn(2084, ids)
        self.assertNotIn(2132, ids)  # first training is capped at level 13
        self.assertNotIn(2086, ids)  # flying potion delivery needs level 42
        self.assertFalse(any(q['jobLabel'] == '海盜系' for q in eligible(DATA['quests'], 39, '僧侶')))

    def test_prerequisite_and_material_totals(self):
        plan, missing = required_quests(DATA['quests'], [2001])
        self.assertEqual({q['id'] for q in plan}, {2000, 2001})
        self.assertEqual(missing, [])
        totals = {r['id']: r['count'] for r in requirement_totals(plan, 'goalItems')}
        self.assertEqual(totals[4000018], 50)
        self.assertEqual(totals[4000022], 100)

    def test_do_not_complete_negative_prerequisites(self):
        qs = copy.deepcopy(DATA['quests'][:2])
        qs[0]['id'], qs[1]['id'] = 1, 2
        qs[0]['prev'] = [{'id': 2, 'state': 0}]
        qs[1]['prev'] = []
        plan, _ = required_quests(qs, [1])
        self.assertEqual([q['id'] for q in plan], [1])
        qs[0]['prev'][0]['state'] = 2
        qs[1]['prev'] = [{'id': 1, 'state': 2}]
        with self.assertRaises(ValueError): required_quests(qs, [1])

    def test_cleric_targets_and_material_lookup(self):
        by_id = {m['id']: m for m in DATA['monsters']}
        self.assertTrue(by_id[3230101]['undead'])
        self.assertEqual(by_id[4230101]['heal_effect'], 3)
        maps = hunting_maps(DATA, [4230101])
        self.assertTrue(any(r['map_id'] == 107000403 for r in maps))
        sources = item_sources(DATA, [4000035])  # tablecloth
        self.assertTrue(any(r['monster_id'] == 3230101 for r in sources))

    def test_unknowns_and_provenance(self):
        self.assertTrue(all(q['minutes'] is None for q in DATA['quests']))
        self.assertTrue(all(d['probability'] is None for m in DATA['monsters'] for d in m['drops']))
        self.assertTrue(all(len(s['sha256']) == 64 for s in DATA['metadata']['sources']))
        self.assertGreater(sum(c['match'] for c in DATA['cross_checks']), 600)

    def test_real_app_search_and_plan(self):
        app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
        self.assertEqual(list(app.exception), [])
        self.assertEqual(app.number_input(key='player_level').value, 39)
        self.assertEqual(app.selectbox(key='player_job').value, '僧侶')
        app.text_input(key='monster_search').set_value('小幽靈').run()
        monster_results = [t.value for t in app.dataframe if '掉落物' in t.value.columns]
        self.assertEqual(monster_results[0]['怪物'].tolist(), ['小幽靈'])
        app.multiselect(key='plan_quests').set_value([2001]).run()
        self.assertEqual(list(app.exception), [])
        self.assertTrue(any('名稱' in t.value.columns and '石塊' in t.value['名稱'].tolist() for t in app.dataframe))

if __name__ == '__main__': unittest.main()
