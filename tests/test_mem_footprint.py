import os
import sys
import time

sys.path.insert(0, r"D:\VibeCode\VibeRun")

from src.config import Config
from src.core.search_engine import SearchEngine
from src.platform.memory import MemoryManager

def test_memory_footprint():
    cfg = Config().data
    engine = SearchEngine(cfg)
    
    print("Initial RAM:", MemoryManager.get_working_set_mb(), "MB")
    engine.app_indexer.load_apps()
    print("After App Indexing RAM:", MemoryManager.get_working_set_mb(), "MB")
    
    # Query test
    res = engine.search("python")
    print(f"Search 'python': found {len(res)} results.")
    
    res2 = engine.search("display")
    print(f"Search 'display': found {len(res2)} results.")
    
    res3 = engine.search("1024 * 4")
    print(f"Search '1024 * 4': {res3[0]['title']}")
    
    print("Before Trim RAM:", MemoryManager.get_working_set_mb(), "MB")
    MemoryManager.trim_working_set()
    time.sleep(0.1)
    print("After Trim RAM:", MemoryManager.get_working_set_mb(), "MB")

if __name__ == "__main__":
    test_memory_footprint()
