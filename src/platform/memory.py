import os
import csv
import ctypes
import subprocess

class MemoryManager:
    @staticmethod
    def trim_working_set():
        """Trims process working set memory down to minimum."""
        try:
            hProcess = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.psapi.EmptyWorkingSet(hProcess)
        except Exception:
            pass

    @staticmethod
    def get_working_set_mb() -> float:
        """Get current working set memory in megabytes."""
        try:
            pid = os.getpid()
            out = subprocess.check_output(
                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                creationflags=subprocess.CREATE_NO_WINDOW
            ).decode('utf-8', errors='ignore').strip()
            
            reader = csv.reader([out])
            for row in reader:
                if len(row) >= 5:
                    mem_str = row[4].replace("K", "").replace(",", "").replace(".", "").strip()
                    return float(mem_str) / 1024.0
        except Exception:
            pass
        return 0.0
