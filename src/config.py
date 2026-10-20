import json
import os

DEFAULT_CONFIG = {
    "hotkey": "alt+space",
    "max_results": 8,
    "file_search_limit": 5,
    "theme": {
        "bg_color": "#1e1e1e",
        "card_bg": "#252526",
        "card_hover": "#2d2d30",
        "card_selected": "#094771",
        "text_primary": "#ffffff",
        "text_secondary": "#cccccc",
        "accent_color": "#007acc",
        "font_family": "Segoe UI",
        "font_size_entry": 14,
        "font_size_title": 11,
        "font_size_subtitle": 9
    },
    "features": {
        "calculator": True,
        "apps": True,
        "system_tools": True,
        "files": True
    },
    "window": {
        "width": 720,
        "height_per_item": 52,
        "top_offset_ratio": 0.22
    }
}

class Config:
    def __init__(self, config_path: str = None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
        self.config_path = config_path
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_data = json.load(f)
                    # Merge with defaults
                    merged = DEFAULT_CONFIG.copy()
                    merged.update(user_data)
                    return merged
            except Exception as e:
                print(f"[Config] Error loading config: {e}. Using defaults.")
        # Create default config file if not exists
        self.save_defaults()
        return DEFAULT_CONFIG.copy()

    def save_defaults(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Error saving default config: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)
