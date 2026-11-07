# CHECKPOINT - VibeRun v2.0 (DigUp Enhanced)

## 1. Trạng thái hiện tại
- **Phiên bản:** VibeRun v2.0
- **Kho mã nguồn:** [https://github.com/lvh0210/VibeRun](https://github.com/lvh0210/VibeRun)
- **Hiệu năng thực tế:**
  - Bộ nhớ RAM: **~23.5 MB** sau khi index 140 ứng dụng và kích hoạt tìm kiếm nội dung.
  - Tải CPU khi chờ: **0.0%**.
  - Kiểm thử: **17/17 Unit Tests ĐẠT (OK)**.

## 2. Tính năng mới v2.0 (Lấy cảm hứng từ ARahim3/DigUp)
- **In-File Content Search Engine (`content_search.py`):**
  - Tìm kiếm sâu vào nội dung tài liệu (.pdf, .docx, .txt, .md, .csv) và mã nguồn (.py, .js, .ts, .cpp, .cs, .java, .sql, .json, .yaml...).
  - **Snippet Preview:** Trích đoạn dòng/câu văn chứa từ khóa hiển thị ngay trong danh sách kết quả.
  - **Cơ chế Hybrid 2 tầng:** Kết hợp Windows Search OLE DB (`System.Search.AutoSummary`) và Local Workspace Scanner có cơ chế giới hạn thời gian (time budget 200ms) để không bao giờ gây giật lag UI.
- **Smart Category Filtering:**
  - `in: <từ khóa>`, `find: <từ khóa>`, `? <từ khóa>`: Tìm nội dung tệp.
  - `@code <từ khóa>`: Lọc tìm trong file mã nguồn.
  - `@doc <từ khóa>`: Lọc tìm trong tài liệu văn bản.
  - `@app <tên>`: Lọc tìm ứng dụng.
  - `@set <tên>`: Lọc tìm cài đặt Windows.
- **Tự động Fallback:** Khi tìm kiếm tên thông thường ít kết quả, tự động bổ sung kết quả tìm kiếm nội dung tệp liên quan.
