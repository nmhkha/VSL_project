# =============================================================================
# VSL Communicator - Backend Logic
# =============================================================================
# Xử lý MediaPipe, dự đoán ký hiệu, và lọc nhiễu.
# Không chứa bất kỳ code GUI nào.
# =============================================================================

import cv2
import pickle
import numpy as np
import mediapipe as mp
import os
import time
import urllib.request
import logging
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

from . import config


class VSLBackend:
    """
    Backend xử lý nhận diện ngôn ngữ ký hiệu.
    
    Responsibilities:
    - Load và quản lý model dự đoán
    - Khởi tạo và sử dụng MediaPipe HandLandmarker
    - Xử lý frame video: phát hiện tay, vẽ skeleton, dự đoán
    - Quản lý logic ổn định dự đoán (giữ 3 giây)
    """
    
    def __init__(self):
        """Khởi tạo Backend với các model và webcam."""
        self._setup_logging()
        
        # Load prediction model
        self.model = self._load_prediction_model()
        
        # Initialize MediaPipe HandLandmarker
        self.hand_landmarker = self._init_hand_landmarker()
        
        # Initialize webcam
        self.cap = self._init_webcam()
        
        # Prediction state
        self.current_prediction = ""      # Dự đoán tức thời
        self.confirmed_prediction = ""    # Ký tự đã xác nhận (giữ đủ 3s)
        self.last_prediction = ""         # Dự đoán frame trước
        self.prediction_start_time = None # Thời điểm bắt đầu giữ cùng ký tự
        
        # Frame counter for MediaPipe timestamp
        self.frame_id = 0
        
    def _setup_logging(self):
        """Cấu hình logging."""
        logging.basicConfig(
            filename=config.LOG_FILE,
            level=logging.INFO,
            format=config.LOG_FORMAT,
        )
        logging.info("VSL Backend initialized")
        
    def _load_prediction_model(self):
        """Load model dự đoán từ file pickle."""
        print("Đang tải model dự đoán...")
        
        for model_path in config.MODEL_PATHS:
            if os.path.exists(model_path):
                try:
                    with open(model_path, 'rb') as f:
                        model_data = pickle.load(f)
                        model = model_data['model']
                    print(f"✓ Đã tải model thành công từ: {model_path}")
                    logging.info(f"Loaded model from {model_path}")
                    return model
                except Exception as e:
                    print(f"✗ Lỗi khi đọc {model_path}: {e}")
                    logging.error(f"Failed to load model from {model_path}: {e}")
        
        print("⚠ Cảnh báo: Không tìm thấy file 'model.p'. Chạy không có dự đoán.")
        logging.warning("model.p not found; running without prediction")
        return None
    
    def _download_hand_model(self, model_path: str):
        """Tải file model hand_landmarker.task nếu chưa có."""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        try:
            print("Đang tải hand_landmarker.task ...")
            urllib.request.urlretrieve(config.HAND_LANDMARKER_URL, model_path)
            print("✓ Tải xong hand_landmarker.task")
            logging.info(f"Downloaded hand_landmarker.task to {model_path}")
        except Exception as e:
            print(f"✗ Lỗi tải model hand_landmarker: {e}")
            logging.error(f"Failed to download hand_landmarker.task: {e}")
    
    def _init_hand_landmarker(self):
        """Khởi tạo MediaPipe HandLandmarker."""
        model_path = os.path.join(config.MEDIAPIPE_MODEL_DIR, config.HAND_LANDMARKER_MODEL)
        
        if not os.path.exists(model_path):
            self._download_hand_model(model_path)
        
        if not os.path.exists(model_path):
            print("✗ Không tìm thấy hand_landmarker.task. Hand tracking sẽ tắt.")
            logging.error("hand_landmarker.task missing; disable hand tracking")
            return None
        
        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=config.MAX_HANDS,
            running_mode=mp_vision.RunningMode.VIDEO
        )
        landmarker = mp_vision.HandLandmarker.create_from_options(options)
        logging.info("HandLandmarker initialized")
        print("✓ HandLandmarker đã khởi tạo")
        return landmarker
    
    def _init_webcam(self):
        """Khởi tạo webcam."""
        cap = cv2.VideoCapture(config.WEBCAM_INDEX)
        if not cap.isOpened():
            print("✗ Lỗi: Không thể mở webcam!")
            logging.error("Failed to open webcam")
            return None
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.WEBCAM_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.WEBCAM_HEIGHT)
        print("✓ Webcam đã sẵn sàng")
        logging.info("Webcam initialized")
        return cap
    
    def normalize_landmarks(self, landmarks):
        """
        Chuẩn hóa landmarks giống như trong create_dataset.py.
        
        Args:
            landmarks: Danh sách các landmark từ MediaPipe
            
        Returns:
            List[float]: 42 giá trị đã chuẩn hóa (21 điểm x 2 tọa độ)
        """
        x_coordinates = [lm.x for lm in landmarks]
        y_coordinates = [lm.y for lm in landmarks]
        
        min_x = min(x_coordinates)
        min_y = min(y_coordinates)
        
        normalized = []
        for lm in landmarks:
            normalized.extend([
                lm.x - min_x,
                lm.y - min_y
            ])
        
        return normalized
    
    def draw_hand_skeleton(self, image, hand_landmarks):
        """
        Vẽ khung xương tay lên hình ảnh.
        
        Args:
            image: numpy array (BGR)
            hand_landmarks: Landmark wrapper object với .landmark attribute
        """
        h, w, _ = image.shape
        colors = config.SKELETON_COLORS
        
        # Định nghĩa các kết nối cho từng ngón tay
        finger_connections = [
            ([0, 1, 2, 3, 4], colors['thumb']),      # Ngón cái
            ([0, 5, 6, 7, 8], colors['index']),      # Ngón trỏ
            ([0, 9, 10, 11, 12], colors['middle']),  # Ngón giữa
            ([0, 13, 14, 15, 16], colors['ring']),   # Ngón áp út
            ([0, 17, 18, 19, 20], colors['pinky']),  # Ngón út
        ]
        
        # Vẽ các đường nối ngón tay
        for finger_indices, color in finger_connections:
            for i in range(len(finger_indices) - 1):
                start_idx = finger_indices[i]
                end_idx = finger_indices[i + 1]
                
                start_point = hand_landmarks.landmark[start_idx]
                end_point = hand_landmarks.landmark[end_idx]
                
                start = (int(start_point.x * w), int(start_point.y * h))
                end = (int(end_point.x * w), int(end_point.y * h))
                
                cv2.line(image, start, end, color, 2)
        
        # Vẽ các đường nối lòng bàn tay
        palm_connections = [
            (0, 1), (0, 5), (0, 9), (0, 13), (0, 17),
            (5, 9), (9, 13), (13, 17)
        ]
        for start_idx, end_idx in palm_connections:
            start_point = hand_landmarks.landmark[start_idx]
            end_point = hand_landmarks.landmark[end_idx]
            
            start = (int(start_point.x * w), int(start_point.y * h))
            end = (int(end_point.x * w), int(end_point.y * h))
            
            cv2.line(image, start, end, colors['palm'], 2)
        
        # Vẽ các khớp
        joint_color_map = {
            0: colors['base_joint'],
            **{i: colors['thumb'] for i in range(1, 5)},
            **{i: colors['index'] for i in range(5, 9)},
            **{i: colors['middle'] for i in range(9, 13)},
            **{i: colors['ring'] for i in range(13, 17)},
            **{i: colors['pinky'] for i in range(17, 21)},
        }
        
        for idx, landmark in enumerate(hand_landmarks.landmark):
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            color = joint_color_map.get(idx, (255, 255, 255))
            
            if idx == 0:  # Khớp gốc - vẽ hình vuông
                cv2.rectangle(image, (x-5, y-5), (x+5, y+5), color, -1)
            else:  # Các khớp khác - vẽ hình tròn
                cv2.circle(image, (x, y), 4, color, -1)
    
    def draw_prediction_box(self, frame, prediction: str):
        """
        Vẽ box hiển thị dự đoán ở góc trái trên video.
        
        Args:
            frame: numpy array (BGR)
            prediction: Ký tự dự đoán
        """
        if not prediction:
            return
        
        box_size = config.PREDICTION_BOX_SIZE
        
        # Vẽ khung trắng
        cv2.rectangle(frame, (10, 10), (10 + box_size, 10 + box_size), (255, 255, 255), 2)
        # Vẽ nền đen
        cv2.rectangle(frame, (12, 12), (12 + box_size - 4, 12 + box_size - 4), (0, 0, 0), -1)
        
        # Vẽ chữ
        font_scale = 2.0
        text_size = cv2.getTextSize(prediction, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 3)[0]
        text_x = 10 + (box_size - text_size[0]) // 2
        text_y = 10 + (box_size + text_size[1]) // 2
        cv2.putText(frame, prediction, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 3, cv2.LINE_AA)
    
    def update_stable_prediction(self, current_pred: str):
        """
        Cập nhật trạng thái dự đoán ổn định.
        Nếu giữ cùng ký tự >= threshold giây thì xác nhận.
        
        Args:
            current_pred: Dự đoán hiện tại
        """
        threshold = config.STABLE_PREDICTION_THRESHOLD
        now = time.time()
        
        if not current_pred:
            self.last_prediction = ""
            self.prediction_start_time = None
            self.confirmed_prediction = ""
            return
        
        if current_pred != self.last_prediction:
            self.last_prediction = current_pred
            self.prediction_start_time = now
            self.confirmed_prediction = ""
            return
        
        # Cùng prediction
        if self.prediction_start_time is not None:
            elapsed = now - self.prediction_start_time
            if elapsed >= threshold:
                self.confirmed_prediction = current_pred
    
    def get_hold_progress(self) -> float:
        """
        Trả về tiến độ giữ ký tự (0.0 - 1.0).
        
        Returns:
            float: Tỷ lệ thời gian đã giữ / threshold
        """
        if self.prediction_start_time is None or not self.last_prediction:
            return 0.0
        
        elapsed = time.time() - self.prediction_start_time
        progress = min(elapsed / config.STABLE_PREDICTION_THRESHOLD, 1.0)
        return progress
    
    def process_frame(self):
        """
        Xử lý một frame từ webcam.
        
        Returns:
            tuple: (processed_frame, current_prediction, confirmed_prediction, hold_progress)
                   hoặc (None, "", "", 0.0) nếu không có frame
        """
        if self.cap is None:
            return None, "", "", 0.0
        
        ret, frame = self.cap.read()
        if not ret:
            return None, "", "", 0.0
        
        # Lật frame theo chiều ngang (hiệu ứng gương)
        frame = cv2.flip(frame, 1)
        
        # Chuyển BGR sang RGB cho MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Phát hiện tay
        if self.hand_landmarker is not None:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            ts_us = int(time.time() * 1e6)
            results = self.hand_landmarker.detect_for_video(mp_image, ts_us)
        else:
            results = None
        
        # Xử lý kết quả
        self.current_prediction = ""
        
        if results and results.hand_landmarks:
            hand_landmarks = results.hand_landmarks[0]
            
            # Wrap landmarks để tái sử dụng hàm vẽ
            class LmWrapper:
                def __init__(self, x, y):
                    self.x, self.y = x, y
            
            class HandWrap:
                def __init__(self, lms):
                    self.landmark = [LmWrapper(lm.x, lm.y) for lm in lms]
            
            wrapped = HandWrap(hand_landmarks)
            
            # Vẽ skeleton
            self.draw_hand_skeleton(frame, wrapped)
            
            # Dự đoán
            if self.model is not None:
                try:
                    normalized = self.normalize_landmarks(hand_landmarks)
                    
                    if len(normalized) == 42:
                        landmarks_array = np.array([normalized])
                        prediction = self.model.predict(landmarks_array)[0]
                        self.current_prediction = str(prediction)
                except Exception as e:
                    logging.error(f"Prediction error: {e}")
                    self.current_prediction = ""
        
        # Cập nhật trạng thái ổn định
        self.update_stable_prediction(self.current_prediction)
        
        # Vẽ prediction box
        self.draw_prediction_box(frame, self.current_prediction)
        
        # Tính tiến độ giữ
        hold_progress = self.get_hold_progress()
        
        self.frame_id += 1
        
        return frame, self.current_prediction, self.confirmed_prediction, hold_progress
    
    def release(self):
        """Giải phóng tài nguyên."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logging.info("VSL Backend released")
        print("Backend đã đóng.")


# =============================================================================
# Helper class để test backend độc lập
# =============================================================================
if __name__ == "__main__":
    print("Testing VSL Backend...")
    backend = VSLBackend()
    
    try:
        while True:
            frame, current, confirmed, progress = backend.process_frame()
            if frame is not None:
                # Hiển thị tiến độ
                if current:
                    print(f"\rCurrent: {current} | Progress: {progress*100:.0f}% | Confirmed: {confirmed}", end="")
                
                cv2.imshow("VSL Backend Test", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        backend.release()
