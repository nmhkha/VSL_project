# KẾ HOẠCH CẬP NHẬT & SO SÁNH (ORIGINAL vs VERSION 2.2)

Tài liệu này chi tiết hóa sự thay đổi giữa yêu cầu ban đầu và phiên bản hiện tại (v2.2) của ứng dụng VSL Communicator.

---

## 1. Kiến trúc Hệ thống (System Architecture)

| Tiêu chí | Kế hoạch Ban đầu | Thực tế Triển khai (v2.2) | Ghi chú |
| :--- | :--- | :--- | :--- |
| **Cấu trúc File** | 1 file `app_demo.py` hoặc chia 3 file (`config`, `backend`, `gui`) | **Package Structure**: Chia thành thư mục `src/`, `models/`, `data/`, `legacy/`. | Giúp dự án gọn gàng và chuyên nghiệp hơn, dễ mở rộng sau này. |
| **Entry Point** | Chạy trực tiếp `gui.py` hoặc `app.py` | Chạy `main.py` ở root, import module từ `src/`. | Tránh lỗi relative import và quản lý đường dẫn tốt hơn. |
| **Dữ liệu Từ điển** | Không đề cập chi tiết | File `data/words.csv` (79,200 từ). | Backend tự động load khi khởi động. |

---

## 2. Giao diện Người dùng (Frontend)

| Tính năng | Kế hoạch Ban đầu | Thực tế Triển khai (v2.2) | Trạng thái |
| :--- | :--- | :--- | :--- |
| **Layout** | Pack (xếp chồng) -> Grid (Lưới) | **Grid Layout** (65% Video / 35% Control). | ✅ Hoàn tất |
| **Hiển thị Video** | Góc trái | Full width phần trên. | ✅ Hoàn tất |
| **Khu vực Text** | Label nhỏ | **Text Area** khổng lồ (Font 36+), có thể chỉnh sửa, cuộn được. | ✅ Hoàn tất |
| **Nút chức năng** | Xóa, Đọc, Cài đặt | Xóa, Đọc, **Space**, **Backspace**, Cài đặt. | Thêm Space/Backspace để tiện thao tác cảm ứng/chuột. |
| **Khu vực Gợi ý** | *Chưa có* | **Suggestion Bar**: 5 nút gợi ý nằm ngang dưới Buffer. | 🌟 TÍNH NĂNG MỚI |
| **Hiển thị gõ** | Đưa thẳng vào câu | **Typing Buffer**: Hiển thị màu xanh lá các ký tự đang gõ dở (vd: 'h', 'o', 'c'). | 🌟 TÍNH NĂNG MỚI |

---

## 3. Logic & Backend

### 3.1. Xử lý Gợi ý từ (Word Suggestion) - *Mới hoàn toàn*
*   **Ban đầu**: Chỉ nhận diện ký tự đơn lẻ (A, B, C...) và ghép thẳng vào câu.
*   **Thực tế**:
    *   Xây dựng class `WordSuggester` trong `src/word_suggester.py`.
    *   Hỗ trợ tra cứu từ điển tiếng Việt không dấu -> có dấu.
    *   Ví dụ: Nhận diện `t`, `r`, `u`, `o`, `n`, `g` -> Gợi ý: `trường`, `trưởng`.

### 3.2. Luồng Nhập liệu (Input Flow)
*   **Ban đầu**:
    `Nhận diện` -> `Ổn định 3s` -> `Thêm vào Câu`
*   **Thực tế (Nâng cấp)**:
    1.  `Nhận diện` -> `Ổn định 3s` -> **Thêm vào Buffer**.
    2.  `Buffer thay đổi` -> **Gọi Gợi ý từ**.
    3.  `Người dùng chọn Gợi ý` HOẶC `Nhấn Space` -> **Chốt vào Câu** & **Xóa Buffer**.
    4.  `Nhấn Backspace` -> Xóa ký tự cuối trong Buffer (nếu có) -> Nếu Buffer rỗng mới xóa trong Câu.

---

## 4. Tổng kết Nâng cấp

So với yêu cầu ban đầu về việc "tách file và làm giao diện đẹp hơn", phiên bản 2.2 đã đi xa hơn với việc:

1.  **Tối ưu hóa trải nghiệm nhập liệu**: Không chỉ ghép chữ cái vô tri, hệ thống giờ đây hiểu và gợi ý từ vựng tiếng Việt có nghĩa.
2.  **Giao diện thông minh**: Có vùng đệm (buffer) để người dùng biết mình đang gõ gì trước khi chốt câu.
3.  **Tổ chức mã nguồn chuẩn**: Dễ dàng bảo trì, thêm tính năng mới mà không sợ phá vỡ logic cũ.
