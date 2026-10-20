import os
import threading
import win32api
import win32con
import win32gui

WM_TRAY_NOTIFY = win32con.WM_USER + 20

class SystemTrayIcon:
    def __init__(self, on_toggle_callback, on_reload_callback, on_exit_callback, config_path: str):
        self.on_toggle = on_toggle_callback
        self.on_reload = on_reload_callback
        self.on_exit = on_exit_callback
        self.config_path = config_path

        self.hwnd = None
        self.notify_id = None
        self.thread = None
        self.running = False
        self.hicon = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        msg_class = "VibeRunTrayClass"
        wc = win32gui.WNDCLASS()
        wc.hInstance = win32gui.GetModuleHandle(None)
        wc.lpszClassName = msg_class
        wc.lpfnWndProc = self._wnd_proc

        try:
            class_atom = win32gui.RegisterClass(wc)
        except Exception:
            pass

        self.hwnd = win32gui.CreateWindow(
            msg_class,
            "VibeRunTray",
            0,
            0, 0, 0, 0,
            win32con.HWND_MESSAGE,
            0,
            wc.hInstance,
            None
        )

        # Load custom VibeRun logo.ico if available, fallback to IDI_APPLICATION
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ico_path = os.path.join(base_dir, "assets", "logo.ico")

        self.hicon = None
        if os.path.exists(ico_path):
            try:
                self.hicon = win32gui.LoadImage(
                    0,
                    ico_path,
                    win32con.IMAGE_ICON,
                    0, 0,
                    win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                )
            except Exception as e:
                print(f"[Tray] Error loading custom icon: {e}")

        if not self.hicon:
            self.hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, WM_TRAY_NOTIFY, self.hicon, "VibeRun - Quick Launcher (Alt+Space)")
        try:
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
            self.notify_id = nid
        except Exception as e:
            print(f"[Tray] Shell_NotifyIcon error: {e}")

        win32gui.PumpMessages()

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_TRAY_NOTIFY:
            if lparam == win32con.WM_LBUTTONUP:
                if self.on_toggle:
                    self.on_toggle()
            elif lparam in (win32con.WM_RBUTTONUP, win32con.WM_CONTEXTMENU):
                self._show_menu()
        elif msg == win32con.WM_DESTROY:
            if self.notify_id:
                try:
                    win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, self.notify_id)
                except Exception:
                    pass
            if self.hicon:
                try:
                    win32gui.DestroyIcon(self.hicon)
                except Exception:
                    pass
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _show_menu(self):
        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(menu, win32con.MF_STRING, 101, "Open VibeRun (Alt+Space)")
        win32gui.AppendMenu(menu, win32con.MF_STRING, 102, "Reload Apps Index")
        win32gui.AppendMenu(menu, win32con.MF_STRING, 103, "Open Config (config.json)")
        win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
        win32gui.AppendMenu(menu, win32con.MF_STRING, 104, "Exit VibeRun")

        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        selected_id = win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_RETURNCMD | win32con.TPM_NONOTIFY,
            pos[0], pos[1],
            0,
            self.hwnd,
            None
        )

        if selected_id == 101 and self.on_toggle:
            self.on_toggle()
        elif selected_id == 102 and self.on_reload:
            self.on_reload()
        elif selected_id == 103:
            if os.path.exists(self.config_path):
                os.startfile(self.config_path)
        elif selected_id == 104 and self.on_exit:
            self.on_exit()

    def stop(self):
        if self.notify_id:
            try:
                win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, self.notify_id)
            except Exception:
                pass
        if self.hwnd:
            win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
