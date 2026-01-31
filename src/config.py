# =============================================================================
# VSL Communicator - Configuration File
# =============================================================================
# Tất cả các thông số cấu hình được tập trung tại đây để dễ dàng điều chỉnh
# mà không cần sửa đổi code logic.
# =============================================================================

import os

# =============================================================================
# 1. WINDOW SETTINGS (Cài đặt cửa sổ)
# =============================================================================
WINDOW_TITLE = "VSL Communicator"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900

# Tỷ lệ phân chia layout (Video : Text Panel)
VIDEO_PANEL_WEIGHT = 65  # 65% cho video
TEXT_PANEL_WEIGHT = 35   # 35% cho text area

# =============================================================================
# 2. COLOR SCHEME (Bảng màu)
# =============================================================================
# Màu nền
BG_DARK = "#1e1e1e"      # Nền chính (tối)
BG_PANEL = "#2b2b2b"     # Nền panel
BG_TEXT = "#0d0d0d"      # Nền text area (đen đậm)

# Màu chữ
TEXT_PRIMARY = "#FFFFFF"   # Trắng - chữ chính
TEXT_SECONDARY = "#FFD700" # Vàng - chữ nhấn mạnh
TEXT_ACCENT = "#00FF00"    # Xanh lá - trạng thái tốt

# Màu nút
BUTTON_BG = "#4a4a4a"
BUTTON_FG = "#FFFFFF"
BUTTON_HOVER = "#5a5a5a"
BUTTON_ACTIVE = "#3a3a3a"

# =============================================================================
# 3. FONT SETTINGS (Cài đặt font chữ)
# =============================================================================
# Font cho Text Area (Khung soạn thảo lớn)
TEXT_AREA_FONT_FAMILY = "Arial"
TEXT_AREA_FONT_SIZE = 36
TEXT_AREA_FONT_WEIGHT = "bold"

# Font cho nút bấm
BUTTON_FONT_FAMILY = "Arial"
BUTTON_FONT_SIZE = 14
BUTTON_FONT_WEIGHT = "bold"

# Font cho status label
STATUS_FONT_FAMILY = "Arial"
STATUS_FONT_SIZE = 16
STATUS_FONT_WEIGHT = "normal"

# Font cho prediction box trên video
PREDICTION_BOX_FONT_SIZE = 48

# =============================================================================
# 4. MODEL PATHS (Đường dẫn model)
# =============================================================================
# Danh sách các đường dẫn tìm kiếm model dự đoán
MODEL_PATHS = [
    './models/model.p',
    './VSL_project-main/model.p',
    './model.p',
    'model.p'
]

# Thư mục lưu model MediaPipe
MEDIAPIPE_MODEL_DIR = os.path.join(os.path.expanduser("~"), ".mediapipe_models")
HAND_LANDMARKER_MODEL = "hand_landmarker.task"
HAND_LANDMARKER_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

# Đường dẫn file từ điển
WORDS_CSV_PATH = "./data/words.csv"

# =============================================================================
# 5. PREDICTION SETTINGS (Cài đặt dự đoán)
# =============================================================================
# Thời gian giữ ổn định để xác nhận ký tự (giây)
STABLE_PREDICTION_THRESHOLD = 3.0

# Frame counting mode (số frame liên tục cần để xác nhận)
FRAME_COUNT_THRESHOLD = 15
USE_FRAME_COUNTING = True  # True: đếm frame, False: đếm thời gian

# Số bàn tay tối đa phát hiện
MAX_HANDS = 1

# Labels mapping (chuyển đổi ký tự đặc biệt)
LABELS_MAP = {
    "a": "a", "b": "b", "c": "c", "d": "d", "dd": "đ", "e": "e", "f": "f", "g": "g", "h": "h", "i": "i",
    "j": "j", "k": "k", "l": "l", "m": "m", "n": "n", "o": "o", "p": "p", "q": "q", "r": "r",
    "s": "s", "t": "t", "u": "u", "v": "v", "w": "w", "x": "x", "y": "y", "z": "z",
}

# =============================================================================
# 6. WEBCAM SETTINGS (Cài đặt webcam)
# =============================================================================
WEBCAM_INDEX = 0
WEBCAM_WIDTH = 640
WEBCAM_HEIGHT = 480
FRAME_UPDATE_INTERVAL = 30  # milliseconds

# =============================================================================
# 7. SKELETON COLORS (Màu khung xương tay) - BGR format for OpenCV
# =============================================================================
SKELETON_COLORS = {
    'thumb': (255, 144, 30),      # Xanh dương
    'index': (0, 255, 0),          # Xanh lá
    'middle': (0, 255, 255),       # Vàng
    'ring': (203, 192, 255),       # Hồng nhạt
    'pinky': (255, 0, 255),        # Tím
    'palm': (128, 128, 128),       # Xám
    'base_joint': (0, 0, 255),     # Đỏ
}

# =============================================================================
# 8. UI DIMENSIONS (Kích thước UI)
# =============================================================================
PREDICTION_BOX_SIZE = 80  # Kích thước box hiển thị prediction trên video
BUTTON_WIDTH = 12
BUTTON_HEIGHT = 2
BUTTON_PADX = 10
BUTTON_PADY = 10

# =============================================================================
# 9. TEXT-TO-SPEECH SETTINGS (Cài đặt đọc văn bản)
# =============================================================================
TTS_LANGUAGE = "vi"  # Ngôn ngữ tiếng Việt
TTS_SLOW = False     # Tốc độ đọc bình thường

# =============================================================================
# 10. LOGGING SETTINGS (Cài đặt ghi log)
# =============================================================================
LOG_FILE = "vsl_communicator.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
