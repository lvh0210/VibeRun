# CHECKPOINT - VibeRun v2.1 (Folder & File Search Enhanced)

## 1. Trạng thái hiện tại
- **Phiên bản:** VibeRun v2.1
- **Kho mã nguồn:** [https://github.com/lvh0210/VibeRun](https://github.com/lvh0210/VibeRun)
- **Hiệu năng:**
  - Bộ nhớ RAM: **~23.7 MB** (idle, tối ưu bằng `EmptyWorkingSet`).
  - Tải CPU khi chờ: **0.0%**.
  - Kiểm thử tự động: **20/20 Unit Tests ĐẠT (OK)**.

## 2. Tính năng mới v2.1 (Folder & File Search + Reveal in Explorer)
1. **Tìm kiếm Thư mục chuyên biệt (`FOLDER`):**
   - Hỗ trợ tiền tố `@folder `, `>folder `, `@dir `, `folder:`, `dir:` để lọc 100% chỉ trả về thư mục.
2. **Tìm kiếm Tệp tin chuyên biệt (`FILE`):**
   - Hỗ trợ tiền tố `@file `, `>file `, `file:` để lọc 100% chỉ trả về tệp tin.
3. **Duyệt cây thư mục trực tiếp (Filesystem Path Navigation):**
   - Hỗ trợ gõ trực tiếp đường dẫn ổ đĩa hoặc thư mục (vd: `D:\VibeCode\`, `C:\`, `~\Desktop`) với tính năng tự động gợi ý và liệt kê các tệp/thư mục bên trong.
4. **Mở thư mục chứa (Reveal in Explorer):**
   - Nhấn `Shift + Enter` hoặc `Ctrl + Enter` (hoặc Click chuột phải vào kết quả) để mở File Explorer và bôi đen (highlight) trực tiếp tệp tin đó.
