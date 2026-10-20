import ctypes
import threading
from ctypes import wintypes

# Win32 Constants
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

VK_MAP = {
    "space": 0x20,
    "enter": 0x0D,
    "tab": 0x09,
    "esc": 0x1B,
    "f1": 0x70,
    "f2": 0x71,
    "f3": 0x72,
    "f4": 0x73,
    "f5": 0x74,
    "f6": 0x75,
    "f7": 0x76,
    "f8": 0x77,
    "f9": 0x78,
    "f10": 0x79,
    "f11": 0x7A,
    "f12": 0x7B
}

class GlobalHotkeyListener:
    def __init__(self, hotkey_str: str, on_trigger_callback):
        self.hotkey_str = hotkey_str.lower()
        self.callback = on_trigger_callback
        self.thread = None
        self.running = False
        self.hotkey_id = 1001
        self.thread_id = None

    def _parse_hotkey(self):
        parts = [p.strip() for p in self.hotkey_str.split("+")]
        modifiers = MOD_NOREPEAT
        vk = 0

        for p in parts:
            if p == "alt":
                modifiers |= MOD_ALT
            elif p in ("ctrl", "control"):
                modifiers |= MOD_CONTROL
            elif p == "shift":
                modifiers |= MOD_SHIFT
            elif p in ("win", "windows", "super"):
                modifiers |= MOD_WIN
            elif p in VK_MAP:
                vk = VK_MAP[p]
            elif len(p) == 1:
                vk = ord(p.upper())

        return modifiers, vk

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        self.thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        modifiers, vk = self._parse_hotkey()

        # Register hotkey on current thread message queue
        success = ctypes.windll.user32.RegisterHotKey(None, self.hotkey_id, modifiers, vk)
        if not success:
            err = ctypes.windll.kernel32.GetLastError()
            print(f"[Hotkey] Failed to register '{self.hotkey_str}' (Error: {err}). Hotkey might be occupied by another app.")
        else:
            print(f"[Hotkey] Successfully registered global hotkey: '{self.hotkey_str}'")

        msg = wintypes.MSG()
        user32 = ctypes.windll.user32

        while self.running:
            ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if ret <= 0:
                break
            if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                try:
                    if self.callback:
                        self.callback()
                except Exception as e:
                    print(f"[Hotkey] Callback exception: {e}")
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(None, self.hotkey_id)

    def stop(self):
        self.running = False
        if self.thread_id:
            ctypes.windll.user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
