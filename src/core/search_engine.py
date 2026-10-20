import os
import subprocess
import threading
from src.core.calculator import Calculator
from src.core.system_tools import SystemToolsIndexer
from src.core.app_indexer import AppIndexer
from src.core.file_search import FileSearchEngine

class SearchEngine:
    def __init__(self, config=None):
        self.config = config or {}
        features = self.config.get("features", {})

        self.enable_calc = features.get("calculator", True)
        self.enable_apps = features.get("apps", True)
        self.enable_sys = features.get("system_tools", True)
        self.enable_files = features.get("files", True)

        self.max_results = self.config.get("max_results", 8)
        self.file_limit = self.config.get("file_search_limit", 4)

        # Initialize components
        self.app_indexer = AppIndexer() if self.enable_apps else None
        self.sys_tools = SystemToolsIndexer() if self.enable_sys else None
        self.file_engine = FileSearchEngine(limit=self.file_limit) if self.enable_files else None

    def initialize_indexes_async(self, on_complete=None):
        """Asynchronously index apps on startup."""
        if self.app_indexer:
            self.app_indexer.load_apps_async(on_complete=on_complete)
        elif on_complete:
            on_complete()

    def search(self, query: str):
        query = query.strip()
        if not query:
            return []

        all_results = []

        # 1. Calculator
        if self.enable_calc:
            calc_res = Calculator.calculate(query)
            if calc_res:
                all_results.append(calc_res)

        # 2. System tools & Settings
        if self.sys_tools:
            sys_results = self.sys_tools.search(query)
            all_results.extend(sys_results)

        # 3. Installed Apps
        if self.app_indexer:
            app_results = self.app_indexer.search(query)
            all_results.extend(app_results)

        # Sort non-file results first
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        # 4. Files (if we still need results to fill max_results, or if query starts with file prefix)
        if self.enable_files and self.file_engine and len(query) >= 2:
            remaining_slots = max(2, self.max_results - len(all_results))
            file_results = self.file_engine.search(query, limit=remaining_slots)
            all_results.extend(file_results)

        # Re-sort keeping calculator at top
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        # De-duplicate by title + target
        seen = set()
        deduped = []
        for item in all_results:
            key = (item["title"], item.get("target", ""))
            if key not in seen:
                seen.add(key)
                deduped.append(item)
            if len(deduped) >= self.max_results:
                break

        return deduped

    def execute(self, item: dict):
        """Route execution to the appropriate handler."""
        if not item:
            return

        itype = item.get("type")
        target = item.get("target")

        if itype == "calc":
            # Copy result to clipboard
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(str(target))
                win32clipboard.CloseClipboard()
                print(f"[SearchEngine] Copied calculation result to clipboard: {target}")
            except Exception as e:
                print(f"[SearchEngine] Failed to copy to clipboard: {e}")
        elif itype in ("lnk", "exe", "uwp"):
            AppIndexer.execute(item)
        elif itype in ("cmd", "uri", "app_run"):
            SystemToolsIndexer.execute(item)
        elif itype == "file":
            FileSearchEngine.execute(item)
        else:
            if target:
                os.startfile(target)
