import os
import sys

sys.path.insert(0, r"D:\VibeCode\VibeRun")

from src.core.file_search import FileSearchEngine

def test_file_folder_search():
    engine = FileSearchEngine(limit=8)
    
    # 1. Search folders
    print("--- Searching folders for 'Code' ---")
    folders = engine.search("Code", limit=5, filter_type="folder")
    for f in folders:
        print(f"[{f['badge']}] {f['title']} -> {f['target']}")
        
    # 2. Search files
    print("\n--- Searching files for 'python' ---")
    files = engine.search("python", limit=5, filter_type="file")
    for f in files:
        print(f"[{f['badge']}] {f['title']} -> {f['target']}")

if __name__ == "__main__":
    test_file_folder_search()
