import os
import time
import win32com.client
import pythoncom

class FileSearchEngine:
    def __init__(self, limit: int = 5):
        self.limit = limit
        self.conn = None
        self._init_connection()

    def _init_connection(self):
        try:
            pythoncom.CoInitialize()
            conn = win32com.client.Dispatch("ADODB.Connection")
            conn.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';")
            self.conn = conn
        except Exception as e:
            print(f"[FileSearch] Failed to open Windows Search connection: {e}")
            self.conn = None

    def search(self, query: str, limit: int = None):
        query = query.strip()
        if not query or len(query) < 2:
            return []

        # If user is typing an absolute path directly (e.g. C:\ or D:\)
        if (len(query) >= 3 and query[1:3] in (":\\", ":/")) or query.startswith("\\\\"):
            return self._search_filesystem_path(query)

        if limit is None:
            limit = self.limit

        # Sanitize query for SQL LIKE to prevent injection/syntax errors
        safe_query = query.replace("'", "''").replace("[", "[[]")

        results = []
        try:
            pythoncom.CoInitialize()
            if self.conn is None:
                self._init_connection()

            if self.conn:
                sql = (
                    f"SELECT TOP {limit} System.ItemName, System.ItemPathDisplay, System.ItemType "
                    f"FROM SystemIndex WHERE SCOPE='file:' AND System.ItemName LIKE '%{safe_query}%' "
                    f"ORDER BY System.ItemName"
                )
                rs = win32com.client.Dispatch("ADODB.Recordset")
                rs.Open(sql, self.conn)

                while not rs.EOF:
                    name = rs.Fields.Item("System.ItemName").Value
                    path = rs.Fields.Item("System.ItemPathDisplay").Value
                    if name and path:
                        is_dir = os.path.isdir(path) if os.path.exists(path) else False
                        badge = "FOLDER" if is_dir else "FILE"
                        results.append({
                            "title": name,
                            "subtitle": path,
                            "type": "file",
                            "target": path,
                            "badge": badge,
                            "score": 45
                        })
                    rs.MoveNext()
                rs.Close()
        except Exception as e:
            print(f"[FileSearch] Query error for '{query}': {e}")
            # Reset connection on failure
            self.conn = None

        return results

    def _search_filesystem_path(self, path_str: str):
        """Allow direct filesystem browsing if path exists."""
        results = []
        try:
            clean_path = os.path.expandvars(path_str)
            if os.path.exists(clean_path):
                is_dir = os.path.isdir(clean_path)
                results.append({
                    "title": os.path.basename(clean_path) or clean_path,
                    "subtitle": f"Open: {clean_path}",
                    "type": "file",
                    "target": clean_path,
                    "badge": "FOLDER" if is_dir else "FILE",
                    "score": 100
                })
                if is_dir:
                    try:
                        for entry in os.scandir(clean_path):
                            results.append({
                                "title": entry.name,
                                "subtitle": entry.path,
                                "type": "file",
                                "target": entry.path,
                                "badge": "FOLDER" if entry.is_dir() else "FILE",
                                "score": 80
                            })
                            if len(results) >= 8:
                                break
                    except Exception:
                        pass
        except Exception:
            pass
        return results

    @staticmethod
    def execute(item: dict):
        """Open the file, folder or launch target."""
        target = item.get("target")
        if target and os.path.exists(target):
            os.startfile(target)
