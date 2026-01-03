# VSL Communicator

**Ứng dụng Dịch Ngôn ngữ Ký hiệu Việt Nam (Vietnamese Sign Language)**

Phiên bản: 2.2 (Beta - Tích hợp Gợi ý từ)

---

## 📁 Cấu trúc dự án

```
VSL_project/
├── main.py                 # 🚀 Điểm khởi động chính
├── README.md
├── CHANGES.txt
├── src/
│   ├── __init__.py
│   ├── config.py           # ⚙️ Cấu hình
│   ├── backend.py          # 🧠 Logic xử lý ảnh
│   ├── gui.py              # 🎨 Giao diện người dùng
│   └── word_suggester.py   # 📖 Logic gợi ý từ (MỚI)
├── models/
│   └── model.p
├── data/
│   ├── words.csv           # 📖 Từ điển tiếng Việt
│   ├── collect_images.py
│   └── create_dataset.py
└── legacy/
    └── app_demo.py
```

---

## ✨ Tính năng Nổi bật (Mới cập nhật)

### 📖 Gợi ý từ Tiếng Việt thông minh
- Khi gõ hoặc nhận diện các ký tự không dấu (vd: `h`, `o`, `c`), hệ thống sẽ tự động tra cứu.
- Hiển thị 5 từ gợi ý gần nhất (vd: `học`, `hóc`, `hốc`, `họa`, `hoặc`).
- **Nút Space**: Tự động chốt từ vào câu.
- **Click chọn**: Chọn nhanh từ gợi ý bằng chuột.

---

## 🔧 Cài đặt & Chạy

```bash
# Cài đặt thư viện
pip install opencv-python mediapipe pillow numpy scikit-learn pyttsx3

# Chạy ứng dụng
cd d:\Video\VSL_project
python main.py
```

---

## ⚙️ Cấu hình (src/config.py)

| Thông số | Giá trị | Mô tả |
|---|---|---|
| `WORDS_CSV_PATH` | `./data/words.csv` | Đường dẫn file từ điển |
| `STABLE_PREDICTION_THRESHOLD` | 3.0 | Giây giữ để nhận diện |

---

## 📖 Hướng dẫn sử dụng Gợi ý từ

1. **Nhập liệu**: Ra ký hiệu tay để nhập các chữ cái (vd: t, r, u, o, n, g).
2. **Buffer**: Các chữ cái sẽ hiện ở dòng `Buffer:` màu xanh lá.
3. **Gợi ý**: Các nút phía dưới sẽ hiện từ gợi ý (trường, trưởng, trướng...).
4. **Chọn từ**:
   - Nhấn **Space** để chọn buffer hiện tại.
   - Click chuột vào nút để chọn từ có dấu.
5. **Sửa lỗi**: Nhấn **Backspace** để xóa ký tự cuối trong Buffer.

---

**© 2024 VSL Communicator Project**
