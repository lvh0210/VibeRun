import os
import time
import ctypes
from ctypes import wintypes
import tkinter as tk
from src.core.search_engine import SearchEngine
from src.platform.memory import MemoryManager

# DWM constants for Windows 11 rounded corners & dark mode
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2

VK_LBUTTON = 0x01
VK_RBUTTON = 0x02

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

BADGE_COLORS = {
    "APP": ("#107c41", "#ffffff"),      # Green
    "SETTINGS": ("#0078d4", "#ffffff"), # Blue
    "CONTROL": ("#498205", "#ffffff"),  # Olive
    "TOOL": ("#8764b8", "#ffffff"),     # Purple
    "SYSTEM": ("#d83b01", "#ffffff"),   # Orange/Red
    "FILE": ("#5c2d91", "#ffffff"),     # Indigo
    "FOLDER": ("#ca5010", "#ffffff"),   # Amber
    "CALC": ("#008272", "#ffffff")      # Teal
}

class LauncherWindow:
    def __init__(self, search_engine: SearchEngine, config: dict):
        self.search_engine = search_engine
        self.config = config
        self.theme = config.get("theme", {})
        self.window_cfg = config.get("window", {})

        self.root = tk.Tk()
        self.root.title("VibeRun")
        self.root.overrideredirect(True) # Borderless window
        self.root.attributes("-topmost", True)
        self.root.configure(bg=self.theme.get("bg_color", "#1e1e1e"))

        self.width = self.window_cfg.get("width", 720)
        self.height_base = 65
        self.height_per_item = self.window_cfg.get("height_per_item", 54)
        self.selected_index = 0
        self.current_results = []
        self._debounce_timer = None
        self._click_poll_id = None
        self._shown_timestamp = 0.0
        self.is_visible = False

        self._setup_assets()
        self._setup_ui()
        self._bind_events()
        self._apply_modern_win32_style()
        self.hide()

    def _setup_assets(self):
        """Load logo icon and window icon."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.logo_path = os.path.join(base_dir, "assets", "logo_28.png")
        self.ico_path = os.path.join(base_dir, "assets", "logo.ico")

        self.logo_image = None
        if os.path.exists(self.logo_path):
            try:
                self.logo_image = tk.PhotoImage(file=self.logo_path)
            except Exception as e:
                print(f"[LauncherWindow] Could not load logo image: {e}")

        if os.path.exists(self.ico_path):
            try:
                self.root.iconbitmap(self.ico_path)
            except Exception:
                pass

    def _setup_ui(self):
        # Outer container frame with border
        self.container = tk.Frame(
            self.root,
            bg=self.theme.get("bg_color", "#1e1e1e"),
            highlightbackground=self.theme.get("card_bg", "#333333"),
            highlightthickness=1
        )
        self.container.pack(fill=tk.BOTH, expand=True)

        # Search Bar Area
        self.search_frame = tk.Frame(self.container, bg=self.theme.get("bg_color", "#1e1e1e"), padx=14, pady=10)
        self.search_frame.pack(fill=tk.X)

        # Logo Icon indicator
        if self.logo_image:
            self.logo_label = tk.Label(
                self.search_frame,
                image=self.logo_image,
                bg=self.theme.get("bg_color", "#1e1e1e")
            )
            self.logo_label.pack(side=tk.LEFT, padx=(0, 10))
        else:
            self.logo_label = tk.Label(
                self.search_frame,
                text="⚡",
                font=(self.theme.get("font_family", "Segoe UI"), 14),
                bg=self.theme.get("bg_color", "#1e1e1e"),
                fg=self.theme.get("accent_color", "#007acc")
            )
            self.logo_label.pack(side=tk.LEFT, padx=(0, 10))

        # Search Entry input
        self.query_var = tk.StringVar()
        self.entry = tk.Entry(
            self.search_frame,
            textvariable=self.query_var,
            font=(self.theme.get("font_family", "Segoe UI"), self.theme.get("font_size_entry", 14)),
            bg=self.theme.get("bg_color", "#1e1e1e"),
            fg=self.theme.get("text_primary", "#ffffff"),
            insertbackground=self.theme.get("accent_color", "#007acc"),
            relief=tk.FLAT,
            bd=0
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Separator line (hidden when no results)
        self.sep = tk.Frame(self.container, height=1, bg=self.theme.get("card_bg", "#333333"))

        # Results container frame
        self.results_frame = tk.Frame(self.container, bg=self.theme.get("bg_color", "#1e1e1e"))
        self.results_frame.pack(fill=tk.BOTH, expand=True)

    def _bind_events(self):
        self.query_var.trace_add("write", self._on_text_change)
        self.entry.bind("<Down>", self._on_key_down)
        self.entry.bind("<Up>", self._on_key_up)
        self.entry.bind("<Return>", self._on_key_enter)
        self.entry.bind("<Escape>", lambda e: self.hide())
        self.root.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_out(self, event):
        if self.is_visible:
            self.root.after(100, self._check_and_hide_on_blur)

    def _check_and_hide_on_blur(self):
        focus = self.root.focus_get()
        if focus is None and self.is_visible:
            self.hide()

    def _apply_modern_win32_style(self):
        """Apply Windows 11 rounded corners and dark title attributes if supported."""
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if not hwnd:
                hwnd = self.root.winfo_id()

            val_dark = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(val_dark), ctypes.sizeof(val_dark)
            )

            val_round = ctypes.c_int(DWMWCP_ROUND)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, ctypes.byref(val_round), ctypes.sizeof(val_round)
            )
        except Exception:
            pass

    def show(self):
        """Display launcher window, focus entry, move mouse into entry, and monitor outside clicks."""
        self.is_visible = True
        self._shown_timestamp = time.time()
        self.root.deiconify()
        self._center_window()
        self.root.lift()
        self.root.attributes("-topmost", True)

        # 1. Bring window to absolute foreground
        try:
            hwnd = self.root.winfo_id()
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            ctypes.windll.user32.SetActiveWindow(hwnd)
        except Exception:
            pass

        # 2. Force focus on input entry and select existing text
        self.entry.focus_force()
        self.entry.select_range(0, tk.END)

        # 3. Automatically position mouse cursor into the search input box
        self.root.after(20, self._move_mouse_into_entry)

        # 4. Start monitoring clicks outside the VibeRun window
        self._start_outside_click_monitor()

    def _move_mouse_into_entry(self):
        """Position mouse cursor directly over the center of the search input field."""
        try:
            self.root.update_idletasks()
            rx = self.entry.winfo_rootx() + 40
            ry = self.entry.winfo_rooty() + self.entry.winfo_height() // 2
            ctypes.windll.user32.SetCursorPos(rx, ry)
        except Exception as e:
            print(f"[LauncherWindow] Error positioning cursor: {e}")

    def _start_outside_click_monitor(self):
        """Start polling for mouse clicks outside the window bounds."""
        if self._click_poll_id:
            try:
                self.root.after_cancel(self._click_poll_id)
            except Exception:
                pass
        self._click_poll_id = self.root.after(40, self._monitor_outside_clicks)

    def _monitor_outside_clicks(self):
        """Detect mouse clicks outside window or loss of foreground."""
        if not self.is_visible:
            return

        # Grace period right after being invoked
        if time.time() - self._shown_timestamp < 0.20:
            self._click_poll_id = self.root.after(35, self._monitor_outside_clicks)
            return

        user32 = ctypes.windll.user32

        # Check if left or right mouse button is pressed
        lbtn_down = (user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000) != 0
        rbtn_down = (user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000) != 0

        if lbtn_down or rbtn_down:
            pt = POINT()
            user32.GetCursorPos(ctypes.byref(pt))

            # Window screen coordinates
            win_x = self.root.winfo_rootx()
            win_y = self.root.winfo_rooty()
            win_w = self.root.winfo_width()
            win_h = self.root.winfo_height()

            # If click occurred outside window boundary -> close VibeRun
            is_inside = (win_x <= pt.x <= win_x + win_w) and (win_y <= pt.y <= win_y + win_h)
            if not is_inside:
                self.hide()
                return

        # Check if another window became foreground
        try:
            fg_hwnd = user32.GetForegroundWindow()
            root_hwnd = self.root.winfo_id()
            parent_hwnd = user32.GetParent(root_hwnd) or root_hwnd
            if fg_hwnd and fg_hwnd != root_hwnd and fg_hwnd != parent_hwnd:
                self.hide()
                return
        except Exception:
            pass

        # Continue monitoring while visible
        if self.is_visible:
            self._click_poll_id = self.root.after(35, self._monitor_outside_clicks)

    def hide(self):
        """Hide window, cancel monitor loop, and trim RAM."""
        self.is_visible = False
        if self._click_poll_id:
            try:
                self.root.after_cancel(self._click_poll_id)
                self._click_poll_id = None
            except Exception:
                pass

        self.root.withdraw()
        # Trim working set memory when idle in background
        MemoryManager.trim_working_set()

    def toggle(self):
        if self.is_visible:
            self.hide()
        else:
            self.show()

    def _center_window(self):
        self.root.update_idletasks()
        total_items = len(self.current_results)
        h = self.height_base + (total_items * self.height_per_item if total_items > 0 else 0)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = (screen_w - self.width) // 2
        y = int(screen_h * self.window_cfg.get("top_offset_ratio", 0.22))

        self.root.geometry(f"{self.width}x{h}+{x}+{y}")

    def _on_text_change(self, *args):
        if self._debounce_timer:
            self.root.after_cancel(self._debounce_timer)
        self._debounce_timer = self.root.after(30, self._perform_search)

    def _perform_search(self):
        query = self.query_var.get().strip()
        if not query:
            self._render_results([])
            return

        results = self.search_engine.search(query)
        self._render_results(results)

    def _render_results(self, results):
        self.current_results = results
        self.selected_index = 0

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not results:
            self.sep.pack_forget()
            self._center_window()
            return

        self.sep.pack(fill=tk.X, before=self.results_frame)

        for i, item in enumerate(results):
            self._create_item_row(i, item)

        self._update_selection_highlight()
        self._center_window()

    def _create_item_row(self, index: int, item: dict):
        bg = self.theme.get("bg_color", "#1e1e1e")
        row = tk.Frame(
            self.results_frame,
            bg=bg,
            padx=14,
            pady=6,
            cursor="hand2"
        )
        row.pack(fill=tk.X)

        # Badge (APP, SETTINGS, FILE, CALC, etc.)
        badge_text = item.get("badge", "ITEM")
        badge_bg, badge_fg = BADGE_COLORS.get(badge_text, ("#333333", "#ffffff"))

        badge = tk.Label(
            row,
            text=f" {badge_text} ",
            font=(self.theme.get("font_family", "Segoe UI"), 8, "bold"),
            bg=badge_bg,
            fg=badge_fg,
            padx=4,
            pady=1
        )
        badge.pack(side=tk.LEFT, padx=(0, 10))

        # Text container (Title + Subtitle)
        text_box = tk.Frame(row, bg=bg)
        text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        title = tk.Label(
            text_box,
            text=item.get("title", ""),
            font=(self.theme.get("font_family", "Segoe UI"), self.theme.get("font_size_title", 11), "bold"),
            bg=bg,
            fg=self.theme.get("text_primary", "#ffffff"),
            anchor="w"
        )
        title.pack(fill=tk.X)

        sub_text = item.get("subtitle", "")
        if len(sub_text) > 85:
            sub_text = sub_text[:82] + "..."

        subtitle = tk.Label(
            text_box,
            text=sub_text,
            font=(self.theme.get("font_family", "Segoe UI"), self.theme.get("font_size_subtitle", 9)),
            bg=bg,
            fg=self.theme.get("text_secondary", "#888888"),
            anchor="w"
        )
        subtitle.pack(fill=tk.X)

        # Mouse click & hover events
        row.bind("<Button-1>", lambda e, idx=index: self._on_item_clicked(idx))
        title.bind("<Button-1>", lambda e, idx=index: self._on_item_clicked(idx))
        subtitle.bind("<Button-1>", lambda e, idx=index: self._on_item_clicked(idx))

        row.bind("<Enter>", lambda e, idx=index: self._set_selected_index(idx))

    def _set_selected_index(self, index: int):
        self.selected_index = index
        self._update_selection_highlight()

    def _update_selection_highlight(self):
        rows = self.results_frame.winfo_children()
        sel_bg = self.theme.get("card_selected", "#094771")
        normal_bg = self.theme.get("bg_color", "#1e1e1e")

        for i, row in enumerate(rows):
            is_selected = (i == self.selected_index)
            color = sel_bg if is_selected else normal_bg
            row.configure(bg=color)
            for child in row.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=color)
                    for lbl in child.winfo_children():
                        lbl.configure(bg=color)

    def _on_key_down(self, event):
        if not self.current_results:
            return "break"
        self.selected_index = (self.selected_index + 1) % len(self.current_results)
        self._update_selection_highlight()
        return "break"

    def _on_key_up(self, event):
        if not self.current_results:
            return "break"
        self.selected_index = (self.selected_index - 1) % len(self.current_results)
        self._update_selection_highlight()
        return "break"

    def _on_key_enter(self, event):
        if self.current_results and 0 <= self.selected_index < len(self.current_results):
            selected = self.current_results[self.selected_index]
            self.hide()
            self.search_engine.execute(selected)
        return "break"

    def _on_item_clicked(self, index: int):
        if 0 <= index < len(self.current_results):
            selected = self.current_results[index]
            self.hide()
            self.search_engine.execute(selected)
