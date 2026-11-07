import time
import sys
import os

sys.path.insert(0, r"D:\VibeCode\VibeRun")

from src.core.content_search import ContentSearchEngine

def test_engine():
    print("Testing ContentSearchEngine...")
    engine = ContentSearchEngine({"content_search": {"workspace_paths": ["D:\\VibeCode\\VibeRun"]}})
    
    # 1. Search code content
    t0 = time.time()
    results = engine.search_content("EmptyWorkingSet")
    elapsed = (time.time() - t0) * 1000
    print(f"\nQuery 'EmptyWorkingSet' found {len(results)} items in {elapsed:.2f} ms:")
    for r in results:
        print(f"[{r['badge']}] {r['title']} -> {r['subtitle']}")
        
    # 2. Search document content
    t0 = time.time()
    doc_results = engine.search_content("PowerToys")
    elapsed = (time.time() - t0) * 1000
    print(f"\nQuery 'PowerToys' found {len(doc_results)} items in {elapsed:.2f} ms:")
    for r in doc_results:
        print(f"[{r['badge']}] {r['title']} -> {r['subtitle']}")

if __name__ == "__main__":
    test_engine()
