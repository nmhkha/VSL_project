================================================================================
                    VSL COMMUNICATOR - LỊCH SỬ THAY ĐỔI
================================================================================

Phiên bản: 2.3
Ngày cập nhật: 2026-01-04

================================================================================
                        THAY ĐỔI MỚI: LAYOUT CAMERA (V2.3)
================================================================================

[THAY ĐỔI GIAO DIỆN]
- Di chuyển khung hiển thị Camera từ TRÊN xuống DƯỚI.
- Di chuyển khung điều khiển (Status, Buffer, Suggestions, Text Area) từ DƯỚI lên TRÊN.

[LÝ DO]
- Người dùng thường nhìn vào phần Text để đọc câu đã soạn, nên đưa nó lên trên để dễ nhìn.
- Camera ở dưới vẫn đủ lớn để quan sát tay khi cần.

[FILE THAY ĐỔI]
- src/gui.py: Đổi row positions (row 0 <-> row 1) cho video_frame và control_frame.

================================================================================
                              TÍNH NĂNG CŨ (V2.2)
================================================================================

1. Backend (src/word_suggester.py)
   - Module `WordSuggester` đọc file `data/words.csv`.
   - Xây dựng từ điển tra cứu nhanh (Key không dấu -> List từ có dấu).

2. Frontend (src/gui.py)
   - "Typing Buffer": Lưu trữ ký tự đang gõ/nhận diện.
   - "Suggestion Bar": Dải 5 nút hiển thị từ gợi ý.
   - Logic: Ký tự -> Buffer -> Gợi ý -> Chọn từ.

================================================================================
                              HƯỚNG DẪN SỬ DỤNG
================================================================================

1. Chạy app: `python main.py`
2. Đưa tay ra ký hiệu (Camera ở phía dưới).
3. Nhìn dòng "Buffer" ở trên để thấy các ký tự đang ghép.
4. Nhìn hàng nút gợi ý để chọn từ có dấu.
5. Click vào từ gợi ý hoặc nhấn Space để chốt.

================================================================================
