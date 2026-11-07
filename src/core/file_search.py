import os
import subprocess
import win32com.client
import pythoncom

class FileSearchEngine:
    def __init__(self, limit: int = 5, config: dict = None):
        self.limit = limit
        self.config = config or {}
        cfg_content = self.config.get("content_search", {})
        self.workspace_paths = cfg_content.get("workspace_paths", ["D:\\VibeCode\\VibeRun"])
        
        # Common quick locations
        user_home = os.path.expanduser("~")
        self.quick_locations = [
            os.path.join(user_home, "Desktop"),
            os.path.join(user_home, "Downloads"),
            os.path.join(user_home, "Documents"),
            "D:\\VibeCode"
        ]
        self.conn = None
        self._init_connection()

    def _init_connection(self):
        try:
            pythoncom.CoInitialize()
            conn = win32com.client.Dispatch("ADODB.Connection")
            conn.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';")
            self.conn = conn
        except Exception as e:
            print(f"[FileSearch] Windows Search connection error: {e}")
            self.conn = None

    def search(self, query: str, limit: int = None, filter_type: str = None):
        """
        Search for files and/or folders.
        `filter_type`: 'folder', 'file', or None (both)
        """
        query = query.strip()
        if not query:
            return []

        if limit is None:
            limit = self.limit

        # 1. Direct path or drive navigation (e.g. C:\, D:\VibeCode, ~\Desktop)
        if query.startswith("~") or (len(query) >= 2 and query[1] == ":") or query.startswith(("\\", "/")):
            return self._browse_filesystem_path(query, filter_type=filter_type, limit=limit)

        if len(query) < 2:
            return []

        results = []
        seen_paths = set()

        # 2. Windows Search Indexer (Fastest, indexed files/folders across Windows)
        win_results = self._search_windows_index(query, limit=limit, filter_type=filter_type)
        for r in win_results:
            p = r["target"]
            if p not in seen_paths:
                seen_paths.add(p)
                results.append(r)

        # 3. Quick Local Directory Scan for non-indexed locations (e.g. D:\VibeCode or Downloads)
        if len(results) < limit:
            local_results = self._search_local_common_dirs(query, limit=limit - len(results), filter_type=filter_type)
            for r in local_results:
                p = r["target"]
                if p not in seen_paths:
                    seen_paths.add(p)
                    results.append(r)
                    if len(results) >= limit:
                        break

        return results

    def _search_windows_index(self, query: str, limit: int = 5, filter_type: str = None):
        results = []
        safe_query = query.replace("'", "''").replace("[", "[[]")

        filter_clause = ""
        if filter_type == "folder":
            filter_clause = "AND System.Kind = 'folder'"
        elif filter_type == "file":
            filter_clause = "AND (System.Kind <> 'folder' OR System.Kind IS NULL)"

        try:
            pythoncom.CoInitialize()
            if self.conn is None:
                self._init_connection()

            if self.conn:
                sql = (
                    f"SELECT TOP {limit * 2} System.ItemName, System.ItemPathDisplay, System.ItemType, System.Kind "
                    f"FROM SystemIndex WHERE SCOPE='file:' {filter_clause} "
                    f"AND System.ItemName LIKE '%{safe_query}%' "
                    f"ORDER BY System.ItemName"
                )
                rs = win32com.client.Dispatch("ADODB.Recordset")
                rs.Open(sql, self.conn)

                while not rs.EOF and len(results) < limit:
                    name = rs.Fields.Item("System.ItemName").Value
                    path = rs.Fields.Item("System.ItemPathDisplay").Value
                    kind = rs.Fields.Item("System.Kind").Value

                    if name and path:
                        is_dir = (kind == "folder") or (os.path.isdir(path) if os.path.exists(path) else False)
                        if filter_type == "folder" and not is_dir:
                            rs.MoveNext()
                            continue
                        if filter_type == "file" and is_dir:
                            rs.MoveNext()
                            continue

                        badge = "FOLDER" if is_dir else "FILE"
                        type_label = "Thư mục" if is_dir else "Tệp tin"
                        score = 80 if name.lower().startswith(query.lower()) else 60

                        results.append({
                            "title": name,
                            "subtitle": f"{type_label}: {path}",
                            "type": "file",
                            "target": path,
                            "badge": badge,
                            "score": score
                        })
                    rs.MoveNext()
                rs.Close()
        except Exception as e:
            print(f"[FileSearch] Windows Search error: {e}")
            self.conn = None

        return results

    def _search_local_common_dirs(self, query: str, limit: int = 5, filter_type: str = None):
        """Quickly scan top-level folders and files in user-relevant directories."""
        results = []
        q_lower = query.lower()

        search_dirs = list(dict.fromkeys(self.quick_locations + self.workspace_paths))

        for base in search_dirs:
            if not os.path.isdir(base):
                continue

            try:
                with os.scandir(base) as entries:
                    for entry in entries:
                        if entry.name.startswith('.'):
                            continue
                        is_dir = entry.is_dir()
                        if filter_type == "folder" and not is_dir:
                            continue
                        if filter_type == "file" and is_dir:
                            continue

                        if q_lower in entry.name.lower():
                            badge = "FOLDER" if is_dir else "FILE"
                            type_label = "Thư mục" if is_dir else "Tệp tin"
                            score = 85 if entry.name.lower().startswith(q_lower) else 65
                            results.append({
                                "title": entry.name,
                                "subtitle": f"{type_label}: {entry.path}",
                                "type": "file",
                                "target": entry.path,
                                "badge": badge,
                                "score": score
                            })
                            if len(results) >= limit:
                                return results
            except Exception:
                continue

        return results

    def _browse_filesystem_path(self, path_str: str, filter_type: str = None, limit: int = 8):
        """Allow direct filesystem browsing and autocompletion when typing a path."""
        results = []
        try:
            if path_str.startswith("~"):
                expanded = os.path.expanduser(path_str)
            else:
                expanded = os.path.expandvars(path_str)

            # If path ends with a separator, list folder contents
            # If path doesn't exist, try parent folder + prefix match
            target_dir = expanded
            name_prefix = ""

            if not os.path.exists(expanded):
                target_dir = os.path.dirname(expanded)
                name_prefix = os.path.basename(expanded).lower()

            if os.path.isdir(target_dir):
                # Add the folder itself as top item
                results.append({
                    "title": os.path.basename(target_dir) or target_dir,
                    "subtitle": f"Mở thư mục: {target_dir}",
                    "type": "file",
                    "target": target_dir,
                    "badge": "FOLDER",
                    "score": 100
                })

                with os.scandir(target_dir) as entries:
                    for entry in entries:
                        # Skip hidden files/directories unless explicitly requested
                        if entry.name.startswith('.') and not name_prefix.startswith('.'):
                            continue

                        if name_prefix and not entry.name.lower().startswith(name_prefix):
                            continue

                        is_dir = entry.is_dir()
                        if filter_type == "folder" and not is_dir:
                            continue
                        if filter_type == "file" and is_dir:
                            continue

                        badge = "FOLDER" if is_dir else "FILE"
                        type_label = "Thư mục" if is_dir else "Tệp tin"
                        results.append({
                            "title": entry.name,
                            "subtitle": f"{type_label}: {entry.path}",
                            "type": "file",
                            "target": entry.path,
                            "badge": badge,
                            "score": 90
                        })
                        if len(results) >= limit:
                            break
        except Exception:
            pass

        return results

    @staticmethod
    def execute(item: dict):
        """Open the file or folder."""
        target = item.get("target")
        if target and os.path.exists(target):
            os.startfile(target)

    @staticmethod
    def reveal_in_explorer(item: dict):
        """Open Windows File Explorer with the target item highlighted."""
        target = item.get("target")
        if not target or not os.path.exists(target):
            return
        if os.path.isdir(target):
            os.startfile(target)
        else:
            subprocess.Popen(f'explorer.exe /select,"{target}"', shell=True)
