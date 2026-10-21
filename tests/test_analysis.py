import unittest
from pathlib import Path
import pandas as pd
from analysis import validate, rank_quests, aggregate
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.quests = validate(pd.read_csv(ROOT / "data/quests.csv"), "quests")

    def test_plan_totals(self):
        totals = dict(aggregate(self.quests, "materials").values)
        self.assertEqual(totals["示範菇傘"], 30)
        self.assertEqual(totals["示範石片"], 5)

    def test_level_and_rates(self):
        result = rank_quests(self.quests, 10)
        self.assertEqual(list(result.id), ["demo1"])
        self.assertEqual(result.iloc[0]["經驗／分鐘"], 100)

    def test_invalid_minutes(self):
        self.quests.loc[0, "minutes"] = 0
        with self.assertRaises(ValueError):
            validate(self.quests, "quests")

    def test_ui_and_search(self):
        app = AppTest.from_file(str(ROOT / "demo_app.py")).run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        app.text_input[0].set_value("不存在的怪物").run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(app.dataframe[0].value.empty)

if __name__ == "__main__":
    unittest.main()
