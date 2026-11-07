# Kế hoạch phát triển VibeRun (Two-Level Dynamic Roadmap)

- [x] **Chặng 1: Nền tảng VibeRun v1.0 (Core Launcher & Platform Integration)**
  - [x] 1.1: Quét ứng dụng Win32/UWP & Windows Search OLE DB
  - [x] 1.2: Phím tắt toàn cục Alt+Space, giao diện dark mode Fluent
  - [x] 1.3: Tối ưu RAM ~20MB, auto-close click ngoài, focus caret
  - [x] 1.4: Đồng bộ GitHub public repo (https://github.com/lvh0210/VibeRun)
- [x] **Chặng 2: Nâng cấp v2.0 lấy cảm hứng từ DigUp (In-File Content Search & Smart Filtering)**
  - [x] 2.1: Phân tích kiến trúc DigUp & thiết kế Content Search Engine siêu nhẹ
  - [x] 2.2: Triển khai bộ trích xuất nội dung tệp tin & `content_search.py`
  - [x] 2.3: Xây dựng cơ chế kép Windows Search AutoSummary & Workspace Scanner
  - [x] 2.4: Bổ sung cú pháp tìm kiếm nội dung (`in:`, `find:`, `?`) kèm trích đoạn khớp (Snippet preview)
  - [x] 2.5: Phân loại danh mục đa phương tiện & bộ lọc thông minh (`@code`, `@doc`, `@app`)
- [-] **Chặng 3: Kiểm thử, đo đạc RAM & Phát hành v2.0**
  - [x] 3.1: Viết Unit tests (17 tests passed) & Benchmark RAM (23.5 MB)
  - [-] 3.2: Khởi động lại tiến trình chạy ngầm và đẩy commit lên GitHub
