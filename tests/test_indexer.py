import unittest
from src.core.system_tools import SystemToolsIndexer
from src.core.app_indexer import AppIndexer

class TestIndexers(unittest.TestCase):
    def test_system_tools(self):
        indexer = SystemToolsIndexer()
        res = indexer.search("wifi")
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0]["badge"], "SETTINGS")

        res_shutdown = indexer.search("tat may")
        self.assertTrue(any("Shutdown" in r["title"] for r in res_shutdown))

    def test_app_indexer(self):
        indexer = AppIndexer()
        indexer.load_apps()
        self.assertTrue(len(indexer.apps) > 0)

if __name__ == "__main__":
    unittest.main()
