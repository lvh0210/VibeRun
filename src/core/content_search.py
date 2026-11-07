import os
import re
import time
import win32com.client
import pythoncom

# Extensions categorized for smart badges and filtering
CODE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.html', '.css', '.scss',
    '.cpp', '.c', '.h', '.hpp', '.cs', '.java', '.kt', '.rs', '.go', '.php',
    '.sql', '.yaml', '.yml', '.ini', '.toml', '.xml', '.bat', '.ps1', '.sh'
}

DOC_EXTENSIONS = {
    '.txt', '.md', '.markdown', '.rst', '.csv', '.tsv', '.log',
    '.pdf', '.docx', '.doc', '.xlsx', '.pptx', '.rtf'
}

TEXT_SEARCHABLE_EXTENSIONS = CODE_EXTENSIONS | {'.txt', '.md', '.markdown', '.rst', '.csv', '.tsv', '.log', '.json', '.xml', '.yaml', '.yml'}

class ContentSearchEngine:
    """
    In-File Content Search Engine inspired by ARahim3/DigUp.
    Searches inside file contents and extracts matching excerpt snippets.
    Dual-layer approach:
      1. Windows Search OLE DB (ADODB with System.Search.Contents & AutoSummary)
      2. Fast Local Workspace Scanner (searching local source code and documents)
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        cfg_section = self.config.get("content_search", {})
        self.workspace_paths = cfg_section.get("workspace_paths", ["D:\\VibeCode"])
        self.max_file_size_bytes = cfg_section.get("max_file_size_kb", 1024) * 1024
        self.limit = cfg_section.get("max_results", 5)
        self.conn = None
        self._init_connection()

    def _init_connection(self):
        try:
            pythoncom.CoInitialize()
            conn = win32com.client.Dispatch("ADODB.Connection")
            conn.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';")
            self.conn = conn
        except Exception as e:
            print(f"[ContentSearch] Windows Search OLE DB init failed: {e}")
            self.conn = None

    def search_content(self, query: str, limit: int = None, category_filter: str = None):
        """
        Search inside file contents for `query`.
        Returns a list of result dictionaries with title, subtitle (snippet), target, badge.
        """
        query = query.strip()
        if not query or len(query) < 2:
            return []

        if limit is None:
            limit = self.limit

        results = []
        seen_paths = set()

        # 1. Search Local Workspace paths (High priority for active projects/code)
        local_results = self._search_local_workspaces(query, limit=limit, category_filter=category_filter)
        for item in local_results:
            path = item["target"]
            if path not in seen_paths:
                seen_paths.add(path)
                results.append(item)
                if len(results) >= limit:
                    return results

        # 2. Search Windows Index for system-wide indexed files (Documents, Desktop, etc.)
        remaining = limit - len(results)
        if remaining > 0:
            win_results = self._search_windows_index(query, limit=remaining, category_filter=category_filter)
            for item in win_results:
                path = item["target"]
                if path not in seen_paths:
                    seen_paths.add(path)
                    results.append(item)
                    if len(results) >= limit:
                        break

        return results

    def _search_windows_index(self, query: str, limit: int = 5, category_filter: str = None):
        """Query Windows Search Indexer for file contents and AutoSummary."""
        results = []
        safe_query = query.replace("'", "''").replace('"', '""')

        try:
            pythoncom.CoInitialize()
            if self.conn is None:
                self._init_connection()

            if self.conn:
                sql = (
                    f"SELECT TOP {limit * 2} System.ItemName, System.ItemPathDisplay, System.Search.AutoSummary "
                    f"FROM SystemIndex WHERE SCOPE='file:' AND FREETEXT(System.Search.Contents, '{safe_query}')"
                )
                rs = win32com.client.Dispatch("ADODB.Recordset")
                rs.Open(sql, self.conn)

                while not rs.EOF and len(results) < limit:
                    name = rs.Fields.Item("System.ItemName").Value
                    path = rs.Fields.Item("System.ItemPathDisplay").Value
                    summary = rs.Fields.Item("System.Search.AutoSummary").Value

                    if name and path and os.path.exists(path):
                        badge = self._get_badge_for_file(path)
                        if category_filter and badge != category_filter:
                            rs.MoveNext()
                            continue

                        snippet = self.clean_snippet(summary or "", query)
                        results.append({
                            "title": name,
                            "subtitle": f"{snippet}  |  {path}",
                            "type": "file",
                            "target": path,
                            "badge": badge,
                            "score": 65,
                            "snippet": snippet
                        })
                    rs.MoveNext()
                rs.Close()
        except Exception as e:
            print(f"[ContentSearch] Windows Search error for '{query}': {e}")
            self.conn = None

        return results

    def _search_local_workspaces(self, query: str, limit: int = 5, category_filter: str = None):
        """Fast file content scan across configured workspace paths with time budget and depth control."""
        results = []
        query_pattern = re.compile(re.escape(query), re.IGNORECASE)
        t_start = time.time()

        IGNORED_DIRS = {
            'node_modules', '__pycache__', 'venv', '.git', 'build', 'dist', 'bin', 'obj',
            '.gradle', '.idea', '.vscode', 'mods', 'config', 'kubejs', 'saves', 'assets', 'logs'
        }

        for base_path in self.workspace_paths:
            if not os.path.isdir(base_path):
                continue

            base_len = len(base_path)
            for root, dirs, files in os.walk(base_path):
                # Time budget protection: never block UI for more than 200ms
                if time.time() - t_start > 0.20:
                    return results

                # Depth protection (max 4 directory levels deep)
                depth = root[base_len:].count(os.sep)
                if depth > 4:
                    dirs.clear()
                    continue

                # Skip heavy, game data, or hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in IGNORED_DIRS]

                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext not in TEXT_SEARCHABLE_EXTENSIONS:
                        continue

                    badge = self._get_badge_for_file(f)
                    if category_filter and badge != category_filter:
                        continue

                    full_path = os.path.join(root, f)
                    try:
                        # Check file size before reading to keep memory footprint 0
                        if os.path.getsize(full_path) > self.max_file_size_bytes:
                            continue

                        with open(full_path, "r", encoding="utf-8", errors="ignore") as file_obj:
                            for line_num, line in enumerate(file_obj, start=1):
                                if query_pattern.search(line):
                                    line_clean = line.strip()
                                    snippet = f"Line {line_num}: {line_clean}"
                                    if len(snippet) > 85:
                                        snippet = snippet[:82] + "..."

                                    results.append({
                                        "title": f,
                                        "subtitle": f"{snippet}  |  {full_path}",
                                        "type": "file",
                                        "target": full_path,
                                        "badge": badge,
                                        "score": 75,
                                        "snippet": snippet
                                    })
                                    break # One snippet per matching file
                    except Exception:
                        continue

                    if len(results) >= limit:
                        return results

        return results

    def _get_badge_for_file(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in CODE_EXTENSIONS:
            return "CODE"
        elif ext in DOC_EXTENSIONS:
            return "DOC"
        return "CONTENT"

    @staticmethod
    def clean_snippet(text: str, query: str, max_len: int = 80) -> str:
        """Extract a readable contextual snippet centered around the query keyword."""
        if not text:
            return "Matches content inside file"

        # Replace multiple spaces, newlines, and tabs with a single space
        text = re.sub(r'\s+', ' ', text).strip()

        # Find query occurrence in text
        m = re.search(re.escape(query), text, re.IGNORECASE)
        if m:
            start_pos = max(0, m.start() - 25)
            end_pos = min(len(text), m.end() + 50)
            prefix = "..." if start_pos > 0 else ""
            suffix = "..." if end_pos < len(text) else ""
            excerpt = prefix + text[start_pos:end_pos].strip() + suffix
            return excerpt[:max_len]

        if len(text) > max_len:
            return text[:max_len - 3] + "..."
        return text

    @staticmethod
    def execute(item: dict):
        """Open the target file."""
        target = item.get("target")
        if target and os.path.exists(target):
            os.startfile(target)
