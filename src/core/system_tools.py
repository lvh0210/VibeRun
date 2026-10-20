import os
import subprocess

SYSTEM_ITEMS = [
    # --- System Commands & Actions ---
    {
        "title": "Lock Screen (Khóa màn hình)",
        "subtitle": "Hệ thống: Khóa máy tính ngay lập tức",
        "keywords": ["lock", "khoa may", "khoa man hinh", "lockscreen", "lock computer"],
        "type": "cmd",
        "target": "rundll32.exe user32.dll,LockWorkStation",
        "badge": "SYSTEM"
    },
    {
        "title": "Sleep (Chế độ ngủ)",
        "subtitle": "Hệ thống: Đưa máy vào trạng thái Sleep",
        "keywords": ["sleep", "ngu", "nghi", "standby"],
        "type": "cmd",
        "target": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
        "badge": "SYSTEM"
    },
    {
        "title": "Restart Computer (Khởi động lại)",
        "subtitle": "Hệ thống: Khởi động lại máy tính",
        "keywords": ["restart", "khoi dong lai", "reboot"],
        "type": "cmd",
        "target": "shutdown /r /t 0",
        "badge": "SYSTEM"
    },
    {
        "title": "Shutdown Computer (Tắt máy)",
        "subtitle": "Hệ thống: Tắt máy tính hoàn toàn",
        "keywords": ["shutdown", "tat may", "power off", "turn off"],
        "type": "cmd",
        "target": "shutdown /s /t 0",
        "badge": "SYSTEM"
    },
    {
        "title": "Sign Out / Log Off (Đăng xuất)",
        "subtitle": "Hệ thống: Đăng xuất người dùng hiện tại",
        "keywords": ["sign out", "log off", "logout", "dang xuat"],
        "type": "cmd",
        "target": "shutdown /l",
        "badge": "SYSTEM"
    },
    {
        "title": "Empty Recycle Bin (Dọn sạch thùng rác)",
        "subtitle": "Hệ thống: Xóa vĩnh viễn các file trong thùng rác",
        "keywords": ["empty recycle bin", "thung rac", "rac", "clean bin", "trash"],
        "type": "cmd",
        "target": 'powershell.exe -NoProfile -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"',
        "badge": "SYSTEM"
    },
    {
        "title": "Open Recycle Bin (Mở thùng rác)",
        "subtitle": "Thư mục: Thùng rác hệ thống",
        "keywords": ["recycle bin", "thung rac", "trash", "bin"],
        "type": "uri",
        "target": "shell:RecycleBinFolder",
        "badge": "FOLDER"
    },
    {
        "title": "Task Manager (Trình quản lý tác vụ)",
        "subtitle": "Công cụ: Quản lý ứng dụng, tiến trình & hiệu năng CPU/RAM",
        "keywords": ["task manager", "taskmgr", "quan ly tac vu", "tien trinh", "cpu", "ram"],
        "type": "app_run",
        "target": "taskmgr.exe",
        "badge": "TOOL"
    },
    {
        "title": "Device Manager (Quản lý thiết bị)",
        "subtitle": "Công cụ: Xem phần cứng & driver máy tính",
        "keywords": ["device manager", "devmgmt", "driver", "phan cung", "quan ly thiet bi"],
        "type": "app_run",
        "target": "devmgmt.msc",
        "badge": "TOOL"
    },
    {
        "title": "Disk Management (Quản lý ổ đĩa)",
        "subtitle": "Công cụ: Phân vùng ổ cứng, định dạng ổ đĩa",
        "keywords": ["disk management", "diskmgmt", "o dia", "phan vung", "o cung", "partition"],
        "type": "app_run",
        "target": "diskmgmt.msc",
        "badge": "TOOL"
    },
    {
        "title": "Services (Quản lý dịch vụ Windows)",
        "subtitle": "Công cụ: Bật, tắt và cấu hình các dịch vụ chạy ngầm",
        "keywords": ["services", "dich vu", "services.msc"],
        "type": "app_run",
        "target": "services.msc",
        "badge": "TOOL"
    },
    {
        "title": "Registry Editor (Chỉnh sửa Registry)",
        "subtitle": "Công cụ: Trình biên tập Windows Registry",
        "keywords": ["registry editor", "regedit", "registry"],
        "type": "app_run",
        "target": "regedit.exe",
        "badge": "TOOL"
    },
    {
        "title": "Terminal / Command Prompt (CMD)",
        "subtitle": "Công cụ: Dòng lệnh Windows Command Prompt",
        "keywords": ["cmd", "command prompt", "terminal", "console", "cmd.exe"],
        "type": "app_run",
        "target": "cmd.exe",
        "badge": "TOOL"
    },
    {
        "title": "PowerShell",
        "subtitle": "Công cụ: Windows PowerShell",
        "keywords": ["powershell", "ps", "terminal", "pwsh"],
        "type": "app_run",
        "target": "powershell.exe",
        "badge": "TOOL"
    },

    # --- Windows Settings (ms-settings:) ---
    {
        "title": "Settings: Windows Update (Cập nhật Windows)",
        "subtitle": "Cài đặt: Kiểm tra và cài đặt bản cập nhật hệ điều hành",
        "keywords": ["windows update", "cap nhat", "update", "patch"],
        "type": "uri",
        "target": "ms-settings:windowsupdate",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Display (Màn hình & Độ phân giải)",
        "subtitle": "Cài đặt: Độ sáng, độ phân giải, tỷ lệ thu phóng, HDR",
        "keywords": ["display", "man hinh", "do phan giai", "brightness", "resolution", "scale"],
        "type": "uri",
        "target": "ms-settings:display",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Sound (Âm thanh & Loa)",
        "subtitle": "Cài đặt: Thiết bị đầu ra, micrô, âm lượng",
        "keywords": ["sound", "am thanh", "loa", "speaker", "volume", "micro", "headphone"],
        "type": "uri",
        "target": "ms-settings:sound",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Bluetooth & Devices (Bluetooth & Thiết bị)",
        "subtitle": "Cài đặt: Ghép nối tai nghe, chuột, bàn phím Bluetooth",
        "keywords": ["bluetooth", "thiet bi", "ket noi", "tai nghe", "chuot", "ban phim"],
        "type": "uri",
        "target": "ms-settings:bluetooth",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Wi-Fi & Network (Mạng & Internet)",
        "subtitle": "Cài đặt: Kết nối Wi-Fi, mạng dây, trạng thái mạng",
        "keywords": ["wifi", "wi-fi", "mang", "internet", "network", "ethernet"],
        "type": "uri",
        "target": "ms-settings:network-wifi",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Installed Apps (Ứng dụng đã cài đặt)",
        "subtitle": "Cài đặt: Xem danh sách ứng dụng, gỡ cài đặt phần mềm",
        "keywords": ["installed apps", "go cai dat", "apps", "ung dung", "uninstall", "phan mem"],
        "type": "uri",
        "target": "ms-settings:appsfeatures",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Startup Apps (Ứng dụng khởi động cùng Windows)",
        "subtitle": "Cài đặt: Bật hoặc tắt ứng dụng tự chạy khi bật máy",
        "keywords": ["startup", "khoi dong", "tu dong chay", "khoi dong cung win"],
        "type": "uri",
        "target": "ms-settings:startupapps",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Power & Battery (Pin & Chế độ nguồn)",
        "subtitle": "Cài đặt: Chế độ tiết kiệm pin, thời gian tắt màn hình",
        "keywords": ["battery", "power", "pin", "nguon", "tiet kiem pin", "sleep timer"],
        "type": "uri",
        "target": "ms-settings:powersleep",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Storage (Dung lượng ổ đĩa & Dọn rác)",
        "subtitle": "Cài đặt: Quản lý bộ nhớ, Storage Sense tự dọn file tạm",
        "keywords": ["storage", "bo nho", "o dia", "don rac", "temp files", "dung luong"],
        "type": "uri",
        "target": "ms-settings:storagesense",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Windows Security (Bảo mật & Diệt virus)",
        "subtitle": "Cài đặt: Windows Defender, tường lửa, bảo vệ tài khoản",
        "keywords": ["security", "defender", "virus", "diet virus", "bao mat", "firewall"],
        "type": "uri",
        "target": "ms-settings:windowsdefender",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Personalization (Cá nhân hóa giao diện)",
        "subtitle": "Cài đặt: Hình nền, màu sắc, chế độ Sáng/Tối (Dark Mode)",
        "keywords": ["personalization", "hinh nen", "wallpaper", "theme", "dark mode", "giao dien"],
        "type": "uri",
        "target": "ms-settings:personalization",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Taskbar (Thanh tác vụ)",
        "subtitle": "Cài đặt: Hành vi thanh Taskbar, icon hệ thống",
        "keywords": ["taskbar", "thanh tac vu", "taskbar settings"],
        "type": "uri",
        "target": "ms-settings:taskbar",
        "badge": "SETTINGS"
    },
    {
        "title": "Settings: Date & Time (Ngày & Giờ)",
        "subtitle": "Cài đặt: Định dạng thời gian, múi giờ tự động",
        "keywords": ["date", "time", "ngay gio", "dong ho", "mui gio", "timezone"],
        "type": "uri",
        "target": "ms-settings:dateandtime",
        "badge": "SETTINGS"
    },
    {
        "title": "Control Panel (Bảng điều khiển cổ điển)",
        "subtitle": "Cài đặt: Trình quản lý Control Panel truyền thống",
        "keywords": ["control panel", "cpl", "bang dieu khien"],
        "type": "app_run",
        "target": "control.exe",
        "badge": "CONTROL"
    },
    {
        "title": "Network Connections (Các bộ chuyển đổi mạng)",
        "subtitle": "Cài đặt: Cấu hình card mạng, IPv4, IPv6, DNS (ncpa.cpl)",
        "keywords": ["ncpa.cpl", "card mang", "network connections", "dns", "ip", "adapter"],
        "type": "app_run",
        "target": "ncpa.cpl",
        "badge": "CONTROL"
    },
    {
        "title": "Sound Control Panel (Cài đặt âm thanh nâng cao)",
        "subtitle": "Cài đặt: Quản lý thiết bị Playback / Recording (mmsys.cpl)",
        "keywords": ["mmsys.cpl", "sound settings", "playback", "recording", "am thanh nang cao"],
        "type": "app_run",
        "target": "mmsys.cpl",
        "badge": "CONTROL"
    }
]

class SystemToolsIndexer:
    def __init__(self):
        self.items = SYSTEM_ITEMS

    def search(self, query: str):
        query = query.lower().strip()
        if not query:
            return []

        results = []
        for item in self.items:
            title_lower = item["title"].lower()
            sub_lower = item["subtitle"].lower()
            keywords = item["keywords"]

            score = 0
            # Exact title or keyword match
            if query in title_lower:
                if title_lower.startswith(query):
                    score = 90
                else:
                    score = 75
            elif any(k.startswith(query) for k in keywords):
                score = 80
            elif any(query in k for k in keywords):
                score = 65
            elif query in sub_lower:
                score = 50

            if score > 0:
                results.append({
                    "title": item["title"],
                    "subtitle": item["subtitle"],
                    "type": item["type"],
                    "target": item["target"],
                    "badge": item["badge"],
                    "score": score
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    @staticmethod
    def execute(item: dict):
        """Execute a system tool item."""
        itype = item.get("type")
        target = item.get("target")

        if itype == "uri":
            os.startfile(target)
        elif itype == "cmd":
            subprocess.Popen(target, shell=True)
        elif itype == "app_run":
            subprocess.Popen(target, shell=True)
