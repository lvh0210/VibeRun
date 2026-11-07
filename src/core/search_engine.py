import os
import subprocess
import threading
from src.core.calculator import Calculator
from src.core.system_tools import SystemToolsIndexer
from src.core.app_indexer import AppIndexer
from src.core.file_search import FileSearchEngine
from src.core.content_search import ContentSearchEngine

class SearchEngine:
    def __init__(self, config=None):
        self.config = config or {}
        features = self.config.get("features", {})

        self.enable_calc = features.get("calculator", True)
        self.enable_apps = features.get("apps", True)
        self.enable_sys = features.get("system_tools", True)
        self.enable_files = features.get("files", True)
        self.enable_content = features.get("content_search", True)

        self.max_results = self.config.get("max_results", 8)
        self.file_limit = self.config.get("file_search_limit", 4)

        # Initialize engines
        self.app_indexer = AppIndexer() if self.enable_apps else None
        self.sys_tools = SystemToolsIndexer() if self.enable_sys else None
        self.file_engine = FileSearchEngine(limit=self.file_limit) if self.enable_files else None
        self.content_engine = ContentSearchEngine(self.config) if self.enable_content else None

    def initialize_indexes_async(self, on_complete=None):
        """Asynchronously index apps on startup."""
        if self.app_indexer:
            self.app_indexer.load_apps_async(on_complete=on_complete)
        elif on_complete:
            on_complete()

    def search(self, raw_query: str):
        raw_query = raw_query.strip()
        if not raw_query:
            return []

        # Parse smart category filters
        prefix, clean_query = self._parse_prefix(raw_query)

        # 1. Dedicated Content Search Mode (DigUp style: 'in: ...', 'find: ...', '? ...', '@find ...')
        if prefix == "content":
            if self.content_engine and len(clean_query) >= 2:
                return self.content_engine.search_content(clean_query, limit=self.max_results)
            return []

        # 2. Filter: Only Apps (@app, >app)
        if prefix == "app":
            if self.app_indexer and clean_query:
                return self.app_indexer.search(clean_query)[:self.max_results]
            return []

        # 3. Filter: Only Settings & System (@set, >set)
        if prefix == "setting":
            if self.sys_tools and clean_query:
                return self.sys_tools.search(clean_query)[:self.max_results]
            return []

        # 4. Filter: Only Code Files & Content (@code, >code)
        if prefix == "code":
            results = []
            if self.content_engine and clean_query:
                results = self.content_engine.search_content(clean_query, limit=self.max_results, category_filter="CODE")
            return results

        # 5. Filter: Only Documents (@doc, >doc)
        if prefix == "doc":
            results = []
            if self.content_engine and clean_query:
                results = self.content_engine.search_content(clean_query, limit=self.max_results, category_filter="DOC")
            return results

        # 6. Default Multi-Source Blended Search
        return self._search_blended(clean_query)

    def _parse_prefix(self, query: str):
        """Parse query prefix for category filtering."""
        q_lower = query.lower()

        # In-file content search prefix
        if q_lower.startswith("in:"):
            return "content", query[3:].strip()
        if q_lower.startswith("find:"):
            return "content", query[5:].strip()
        if query.startswith("?") and len(query) > 1 and not query.startswith("??"):
            return "content", query[1:].strip()
        if q_lower.startswith("@find ") or q_lower.startswith(">find "):
            return "content", query[6:].strip()

        # Apps only
        if q_lower.startswith("@app ") or q_lower.startswith(">app "):
            return "app", query[5:].strip()

        # Settings only
        if q_lower.startswith("@set ") or q_lower.startswith(">set ") or q_lower.startswith("@settings "):
            idx = query.find(" ")
            return "setting", query[idx + 1:].strip()

        # Code only
        if q_lower.startswith("@code ") or q_lower.startswith(">code "):
            return "code", query[6:].strip()

        # Docs only
        if q_lower.startswith("@doc ") or q_lower.startswith(">doc ") or q_lower.startswith("@docs "):
            idx = query.find(" ")
            return "doc", query[idx + 1:].strip()

        return None, query

    def _search_blended(self, query: str):
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

        # Sort non-file results first by score
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        # 4. Files by name (Windows Search)
        if self.enable_files and self.file_engine and len(query) >= 2:
            remaining_slots = max(2, self.max_results - len(all_results))
            file_results = self.file_engine.search(query, limit=remaining_slots)
            all_results.extend(file_results)

        # 5. Hybrid Fallback: In-File Content Search (DigUp style)
        # If we have few matches (< 3) and user typed at least 3 characters, search inside file contents
        if self.enable_content and self.content_engine and len(query) >= 3 and len(all_results) < 4:
            needed = max(2, self.max_results - len(all_results))
            content_results = self.content_engine.search_content(query, limit=needed)
            all_results.extend(content_results)

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
            if target and os.path.exists(target):
                os.startfile(target)
