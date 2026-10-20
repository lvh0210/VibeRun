import unittest
from src.core.search_engine import SearchEngine
from src.config import DEFAULT_CONFIG

class TestSearchEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = SearchEngine(DEFAULT_CONFIG)
        # Force load apps synchronously for testing
        if cls.engine.app_indexer:
            cls.engine.app_indexer.load_apps()

    def test_calculator_query(self):
        results = self.engine.search("1024 / 8")
        self.assertTrue(len(results) > 0)
        top = results[0]
        self.assertEqual(top["type"], "calc")
        self.assertEqual(top["target"], "128")

    def test_system_tool_query(self):
        results = self.engine.search("lock")
        self.assertTrue(any("Lock Screen" in r["title"] for r in results))

    def test_vietnamese_system_tool(self):
        results = self.engine.search("khoa may")
        self.assertTrue(any("Lock Screen" in r["title"] for r in results))

    def test_settings_query(self):
        results = self.engine.search("display")
        self.assertTrue(any("Display" in r["title"] for r in results))

    def test_app_query(self):
        results = self.engine.search("python")
        self.assertTrue(len(results) > 0)

if __name__ == "__main__":
    unittest.main()
