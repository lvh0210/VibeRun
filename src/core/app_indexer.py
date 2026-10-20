import os
import sys
import subprocess
import threading
import winreg

class AppIndexer:
    def __init__(self):
        self.apps = []
        self._lock = threading.Lock()
        self.is_loaded = False

    def load_apps_async(self, on_complete=None):
        """Asynchronously index apps in a background thread."""
        def _worker():
            self.load_apps()
            if on_complete:
                on_complete()

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def load_apps(self):
        """Scan Start Menu shortcuts, Registry App Paths, and Get-StartApps."""
        discovered = {}

        # 1. Start Menu Shortcuts (.lnk files)
        start_menu_dirs = [
            os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Start Menu\\Programs")
        ]

        for base_dir in start_menu_dirs:
            if not os.path.isdir(base_dir):
                continue
            for root, _, files in os.walk(base_dir):
                for f in files:
                    if f.lower().endswith(".lnk"):
                        name = f[:-4]
                        # Filter out uninstall shortcuts
                        if "uninstall" in name.lower() or "gỡ cài đặt" in name.lower():
                            continue
                        full_path = os.path.join(root, f)
                        key = name.lower()
                        if key not in discovered:
                            discovered[key] = {
                                "title": name,
                                "subtitle": f"Ứng dụng: {full_path}",
                                "type": "lnk",
                                "target": full_path,
                                "badge": "APP"
                            }

        # 2. Get-StartApps (covers UWP / Store apps + modern packaged apps)
        try:
            cmd = ['powershell.exe', '-NoProfile', '-Command', 
                   '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Get-StartApps | ConvertTo-Json -Compress']
            output = subprocess.check_output(cmd, creationflags=subprocess.CREATE_NO_WINDOW).decode('utf-8', errors='ignore').strip()
            if output:
                import json
                parsed = json.loads(output)
                if isinstance(parsed, dict):
                    parsed = [parsed]
                for item in parsed:
                    name = item.get("Name", "")
                    appid = item.get("AppID", "")
                    if not name or not appid:
                        continue
                    if "uninstall" in name.lower():
                        continue
                    key = name.lower()
                    if key not in discovered:
                        is_uwp = not (appid.endswith(".exe") or appid.endswith(".bat") or appid.endswith(".cmd") or "\\" in appid)
                        target_type = "uwp" if is_uwp else "exe"
                        discovered[key] = {
                            "title": name,
                            "subtitle": f"Ứng dụng: {appid}",
                            "type": target_type,
                            "target": appid,
                            "badge": "APP"
                        }
        except Exception as e:
            print(f"[AppIndexer] Get-StartApps scan error: {e}")

        # 3. Registry App Paths
        for hkey in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(hkey, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
                    num_subkeys = winreg.QueryInfoKey(key)[0]
                    for i in range(num_subkeys):
                        try:
                            sub_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, sub_name) as sub_key:
                                target_val, _ = winreg.QueryValueEx(sub_key, "")
                                if target_val and os.path.exists(target_val):
                                    clean_name = sub_name.replace(".exe", "")
                                    k = clean_name.lower()
                                    if k not in discovered:
                                        discovered[k] = {
                                            "title": clean_name.capitalize(),
                                            "subtitle": f"Ứng dụng: {target_val}",
                                            "type": "exe",
                                            "target": target_val,
                                            "badge": "APP"
                                        }
                        except Exception:
                            continue
            except Exception:
                continue

        with self._lock:
            self.apps = list(discovered.values())
            self.is_loaded = True
        print(f"[AppIndexer] Indexed {len(self.apps)} applications.")

    def search(self, query: str):
        query = query.lower().strip()
        if not query:
            return []

        with self._lock:
            app_list = self.apps.copy()

        results = []
        for app in app_list:
            title_lower = app["title"].lower()
            score = 0

            if title_lower == query:
                score = 100
            elif title_lower.startswith(query):
                score = 85
            elif f" {query}" in title_lower or f"-{query}" in title_lower:
                score = 75
            elif query in title_lower:
                score = 60
            elif all(c in title_lower for c in query):
                # Acronym or fuzzy check
                score = 40

            if score > 0:
                results.append({
                    "title": app["title"],
                    "subtitle": app["subtitle"],
                    "type": app["type"],
                    "target": app["target"],
                    "badge": app["badge"],
                    "score": score
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    @staticmethod
    def execute(item: dict):
        """Launch the application."""
        itype = item.get("type")
        target = item.get("target")

        if itype == "uwp":
            # Launch UWP via shell:AppsFolder
            subprocess.Popen(f'explorer.exe shell:AppsFolder\\{target}', shell=True)
        elif itype in ("lnk", "exe"):
            os.startfile(target)
        else:
            os.startfile(target)
