# VSL Communicator

**Ứng dụng Dịch Ngôn ngữ Ký hiệu Việt Nam (Vietnamese Sign Language)**

Phiên bản: 2.3 (Camera ở Dưới)

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
│   └── word_suggester.py   # 📖 Logic gợi ý từ
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

## ✨ Tính năng Nổi bật

### 🎯 Giao diện Tối ưu (v2.3)
**Layout mới:**
```
┌──────────────────────────────────────────┐
│  Status | Progress | Buffer: hue         │
│  [huế] [huế] [huế] [Huế]  ← Gợi ý       │
├──────────────────────────────────────────┤
│  [Text Area - Font 36pt]                 │
│  bún bò                                  │
│                                          │
├──────────────────────────────────────────┤
│  📹 CAMERA VIDEO (Skeleton + Box)        │
│     Hiển thị tay và nhận diện           │
└──────────────────────────────────────────┘
```

### 📖 Gợi ý từ Tiếng Việt thông minh
- Khi gõ các ký tự không dấu (vd: `h`, `u`, `e`), hệ thống tự động tra cứu.
- Hiển thị 5 từ gợi ý gần nhất (vd: `huế`, `huế`, `Huế`).
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

## 📖 Hướng dẫn sử dụng

1. **Nhập liệu**: Ra ký hiệu tay ở phía dưới màn hình (vùng camera).
2. **Buffer**: Các chữ cái sẽ hiện ở dòng `Buffer:` màu xanh lá (phía trên).
3. **Gợi ý**: Các nút phía dưới Buffer sẽ hiện từ gợi ý.
4. **Chọn từ**:
   - Nhấn **Space** để chọn buffer hiện tại.
   - Click chuột vào nút để chọn từ có dấu.
5. **Sửa lỗi**: Nhấn **Backspace** để xóa ký tự cuối trong Buffer.

---

**© 2024 VSL Communicator Project**
