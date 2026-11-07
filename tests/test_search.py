import unittest
import os
import sys

# Ensure project path is accessible
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.search_engine import SearchEngine
from src.config import Config

class TestSearchEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg = Config().data
        cls.engine = SearchEngine(cfg)
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

    def test_content_search_prefix_in(self):
        results = self.engine.search("in: EmptyWorkingSet")
        self.assertTrue(len(results) > 0)
        self.assertTrue(any(r.get("badge") in ("CODE", "DOC", "CONTENT") for r in results))
        # Ensure snippet exists
        self.assertTrue(any("EmptyWorkingSet" in r.get("subtitle", "") for r in results))

    def test_content_search_prefix_find(self):
        results = self.engine.search("find: PowerToys")
        self.assertTrue(len(results) > 0)

    def test_category_code_filter(self):
        results = self.engine.search("@code def ")
        self.assertTrue(len(results) > 0)
        self.assertTrue(all(r.get("badge") == "CODE" for r in results))

    def test_category_app_filter(self):
        results = self.engine.search("@app python")
        self.assertTrue(len(results) > 0)
        self.assertTrue(all(r.get("badge") == "APP" for r in results))

    def test_folder_filter_prefix(self):
        results = self.engine.search("@folder VibeRun")
        self.assertTrue(len(results) > 0)
        self.assertTrue(any(r.get("badge") == "FOLDER" for r in results))

    def test_file_filter_prefix(self):
        results = self.engine.search("@file main.py")
        self.assertTrue(len(results) > 0)
        self.assertTrue(all(r.get("badge") == "FILE" for r in results))

    def test_direct_path_navigation(self):
        results = self.engine.search(r"D:\VibeCode\VibeRun")
        self.assertTrue(len(results) > 0)
        self.assertTrue(any("main.py" in r.get("title", "") for r in results))

if __name__ == "__main__":
    unittest.main()
