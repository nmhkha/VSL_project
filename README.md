# VSL Communicator

**Ứng dụng Dịch Ngôn ngữ Ký hiệu Việt Nam (Vietnamese Sign Language)**

---

## � Cấu trúc dự án

```
VSL_project/
├── main.py                 # � Điểm khởi động chính
├── README.md
├── CHANGES.txt
├── src/                    # Source code
│   ├── __init__.py
│   ├── config.py           # ⚙️ Cấu hình
│   ├── backend.py          # 🧠 Logic xử lý
│   └── gui.py              # 🎨 Giao diện
├── models/                 # Model files
│   └── model.p
├── data/                   # Training scripts
│   ├── collect_images.py
│   └── create_dataset.py
└── legacy/                 # Backup
    └── app_demo.py
```

---

## 🔧 Cài đặt

```bash
pip install opencv-python mediapipe pillow numpy scikit-learn
pip install pyttsx3  # Tùy chọn: Text-to-Speech
```

---

## 🚀 Cách sử dụng

### Hướng dẫn:
1. Đưa tay vào camera
2. Ra ký hiệu ngôn ngữ ký hiệu
3. Giữ ổn định 3 giây → ký tự được thêm vào
4. Nhấn nút "Đọc" để nghe văn bản

---

## ⚙️ Cấu hình

Chỉnh sửa trong `src/config.py`:

| Thông số | Giá trị mặc định | Mô tả |
|----------|------------------|-------|
| `TEXT_AREA_FONT_SIZE` | 36 | Kích thước font text |
| `STABLE_PREDICTION_THRESHOLD` | 3.0 | Giây giữ để xác nhận |
| `WINDOW_WIDTH/HEIGHT` | 1200x900 | Kích thước cửa sổ |

---

## ⌨️ Phím tắt

| Phím | Chức năng |
|------|-----------|
| `q` / `Esc` | Thoát |

---

## 🔍 Khắc phục sự cố

- **Không mở webcam**: Kiểm tra webcam, đổi `WEBCAM_INDEX` trong config
- **Model không load**: Đảm bảo `models/model.p` tồn tại
- **TTS không hoạt động**: `pip install pyttsx3`

---

**© 2024 VSL Communicator Project**
