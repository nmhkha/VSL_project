# =============================================================================
# VSL Communicator - Main Entry Point
# =============================================================================
# Điểm khởi động chính của ứng dụng.
# Khởi tạo Backend và GUI, sau đó chạy main loop.
# =============================================================================

import tkinter as tk
import sys
import os

# Thêm thư mục gốc vào path để import được src package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import các module của ứng dụng
try:
    from src.backend import VSLBackend
    from src.gui import VSLGUI
    from src import config
except ImportError as e:
    print(f"Lỗi import module: {e}")
    print("Đảm bảo các file nằm trong thư mục src/")
    sys.exit(1)


def main():
    """Hàm chính khởi động ứng dụng."""
    print("=" * 60)
    print("       VSL COMMUNICATOR - Giao tiếp bằng Ngôn ngữ Ký hiệu")
    print("=" * 60)
    print()
    
    # Khởi tạo Backend
    print("[1/3] Khởi tạo Backend...")
    try:
        backend = VSLBackend()
    except Exception as e:
        print(f"✗ Lỗi khởi tạo Backend: {e}")
        sys.exit(1)
    
    # Khởi tạo Tkinter root
    print("[2/3] Khởi tạo giao diện...")
    root = tk.Tk()
    
    # Khởi tạo GUI
    try:
        app = VSLGUI(root, backend)
    except Exception as e:
        print(f"✗ Lỗi khởi tạo GUI: {e}")
        backend.release()
        sys.exit(1)
    
    # Đăng ký handler đóng cửa sổ
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    print("[3/3] Khởi động ứng dụng...")
    print()
    print("=" * 60)
    print("  Ứng dụng đã sẵn sàng!")
    print("  - Đưa tay vào camera để nhận diện ký hiệu")
    print("  - Giữ ký hiệu 3 giây để xác nhận")
    print("  - Nhấn 'q' hoặc 'Esc' để thoát")
    print("=" * 60)
    print()
    
    # Chạy main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nĐang đóng ứng dụng...")
        app.on_closing()


if __name__ == "__main__":
    main()
