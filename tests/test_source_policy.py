import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from source_policy import require_allowed

class SourcePolicyTests(unittest.TestCase):
    def test_selected_sources(self):
        for url in ['https://maplestoryclassic.beanfun.com/Main', 'https://forum.gamer.com.tw/C.php?bsn=85994&snA=647', 'https://bobogameguides.com/maplestory-classic/guides/quests.html', 'https://morrisrrrrrrr-svg.github.io/data.js']:
            self.assertEqual(require_allowed(url), url)
    def test_rejected_sources_and_other_games(self):
        for url in ['https://mapleclassictools.com/', 'https://david27tainan.github.io/KargoData/', 'https://forum.gamer.com.tw/B.php?bsn=7650', 'https://bobogameguides.com/another-game/', 'https://morrisrrrrrrr-svg.github.io.evil.test/', 'http://morrisrrrrrrr-svg.github.io/']:
            with self.assertRaises(ValueError): require_allowed(url)
