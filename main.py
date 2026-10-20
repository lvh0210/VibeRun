import sys
import os
import signal
import pythoncom

# Ensure src is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.core.search_engine import SearchEngine
from src.platform.hotkey import GlobalHotkeyListener
from src.platform.memory import MemoryManager
from src.ui.launcher_window import LauncherWindow
from src.ui.tray_icon import SystemTrayIcon

class VibeRunApp:
    def __init__(self):
        self.config_mgr = Config()
        self.config = self.config_mgr.data

        # Initialize COM for this thread
        pythoncom.CoInitialize()

        # Search Engine
        self.search_engine = SearchEngine(self.config)
        self.search_engine.initialize_indexes_async(on_complete=self._on_indexing_complete)

        # UI Window
        self.window = LauncherWindow(self.search_engine, self.config)

        # Global Hotkey
        hotkey_str = self.config.get("hotkey", "alt+space")
        self.hotkey = GlobalHotkeyListener(hotkey_str, self._on_hotkey_pressed)
        self.hotkey.start()

        # System Tray Icon
        self.tray = SystemTrayIcon(
            on_toggle_callback=self._on_tray_toggle,
            on_reload_callback=self._on_tray_reload,
            on_exit_callback=self.quit,
            config_path=self.config_mgr.config_path
        )
        self.tray.start()

        # Handle signals
        signal.signal(signal.SIGINT, lambda s, f: self.quit())
        signal.signal(signal.SIGTERM, lambda s, f: self.quit())

        print(f"[VibeRun] Initialized successfully. Press '{hotkey_str}' to toggle.")
        MemoryManager.trim_working_set()

    def _on_indexing_complete(self):
        print(f"[VibeRun] Background indexing complete. Working set RAM: {MemoryManager.get_working_set_mb():.1f} MB")
        MemoryManager.trim_working_set()

    def _on_hotkey_pressed(self):
        # Hotkey listener runs on a background thread; schedule UI update on main thread
        self.window.root.after(0, self.window.toggle)

    def _on_tray_toggle(self):
        self.window.root.after(0, self.window.toggle)

    def _on_tray_reload(self):
        print("[VibeRun] Reloading app indexes...")
        self.search_engine.initialize_indexes_async(on_complete=self._on_indexing_complete)

    def run(self):
        try:
            self.window.root.mainloop()
        except KeyboardInterrupt:
            self.quit()

    def quit(self):
        print("[VibeRun] Shutting down...")
        try:
            self.hotkey.stop()
            self.tray.stop()
            self.window.root.destroy()
        except Exception:
            pass
        sys.exit(0)

def main():
    app = VibeRunApp()
    app.run()

if __name__ == "__main__":
    main()
