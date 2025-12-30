import cv2
import pickle
import numpy as np
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import urllib.request
import logging
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

class WebcamViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("App Demo")
        self.root.configure(bg='#2b2b2b')
        self.frame_id = 0
        # Window size
        self.window_width = 1000
        self.window_height = 800
        self.root.geometry(f"{self.window_width}x{self.window_height}")

        #Biến quản lý câu và khung hình
        self.sentence_tokens = []
        self.last_appended_token = ""
        self.frame_id = 0

        # Logging setup
        logging.basicConfig(
            filename="app.log",
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )
        logging.info("App started")
        # Load model - tìm trong VSL_project-main hoặc thư mục hiện tại
        print("Đang tải model...")
        model_paths = [
            './VSL_project-main/model.p',  # Trong thư mục VSL_project
            './model.p',  # Trong thư mục VSL_project-main
            'model.p'  # Trong thư mục hiện tại
        ]
        
        self.model = None
        for model_path in model_paths:
            if os.path.exists(model_path):
                try:
                    with open(model_path, 'rb') as f:
                        model_data = pickle.load(f)  # giải nén dict đã lưu, chứa model đã train
                        self.model = model_data['model']
                    print(f"Đã tải model thành công từ: {model_path}")
                    logging.info(f"Loaded model from {model_path}")
                    break
                except Exception as e:
                    print(f"Lỗi khi đọc {model_path}: {e}")
                    logging.error(f"Failed to load model from {model_path}: {e}")
        
        if self.model is None:
            print("Cảnh báo: Không tìm thấy file 'model.p'")
            logging.warning("model.p not found; running without prediction")
        
        # MediaPipe Tasks setup 
        self.hand_landmarker = self._init_hand_landmarker()
        
        # Webcam setup
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Lỗi: Không thể mở webcam!")
            self.cap = None
        else:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Prediction
        self.current_prediction = ""      # dự đoán tức thời của frame hiện tại
        self.confirmed_prediction = ""    # ký tự đã giữ ổn định đủ 3s để chọn
        self.last_prediction = ""         # dự đoán của frame trước (để so sánh đổi ký tự)
        self.prediction_start_time = None # thời điểm bắt đầu giữ cùng ký tự
        
        # Create UI
        self.create_ui()
        
        # Start video loop
        self.running = True
        self.update_frame()

        # Shortcut: nhấn 'q' để thoát
        self.root.bind('q', lambda event: self.on_closing())
        self.root.bind('Q', lambda event: self.on_closing())
        # Phím space để chèn khoảng trắng vào câu
        self.root.bind('<space>', self._on_space_press)
        
    def create_ui(self):
        # Top panel - Webcam feed
        self.webcam_frame = tk.Frame(self.root, bg='#1e1e1e', relief=tk.SUNKEN, bd=2)
        self.webcam_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.webcam_label = tk.Label(self.webcam_frame, bg='#1e1e1e')
        self.webcam_label.pack(expand=True)
        
        # Bottom panel - Empty (for future use)
        self.bottom_panel = tk.Frame(self.root, bg='#3d3d3d', height=200)
        self.bottom_panel.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        # Labels hiển thị trạng thái và câu ghép
        self.status_label = tk.Label(
            self.bottom_panel,
            text="Keep 3s: ",
            bg='#3d3d3d',
            fg='white',
            font=('Arial', 14)
        )
        self.status_label.pack(anchor='w', padx=10, pady=5)

        self.sentence_label = tk.Label(
            self.bottom_panel,
            text="Setence: ",
            bg='#3d3d3d',
            fg='white',
            font=('Arial', 16, 'bold')
        )
        self.sentence_label.pack(anchor='w', padx=10, pady=5)
    
    
    """tải file model MediaPipe hand_landmarker.task từ URL về đường dẫn model_path"""
    def _download_hand_model(self, model_path: str):
        """Tải file model hand_landmarker.task nếu chưa có"""
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        try:
            print("Đang tải hand_landmarker.task ...")
            urllib.request.urlretrieve(url, model_path)
            print("Tải xong hand_landmarker.task")
            logging.info(f"Downloaded hand_landmarker.task to {model_path}")
        except Exception as e:
            print(f"Lỗi tải model hand_landmarker: {e}")
            logging.error(f"Failed to download hand_landmarker.task: {e}")

    def _init_hand_landmarker(self):
        """Chuẩn bị HandLandmarker (MediaPipe Tasks)"""
        model_dir = os.path.join(os.path.expanduser("~"), ".mediapipe_models")
        model_path = os.path.join(model_dir, "hand_landmarker.task")
        if not os.path.exists(model_path):
            self._download_hand_model(model_path)

        if not os.path.exists(model_path):
            print("Không tìm thấy hand_landmarker.task sau khi tải. Hand tracking sẽ tắt.")
            logging.error("hand_landmarker.task missing after download attempt; disable hand tracking")
            return None

        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            running_mode=mp_vision.RunningMode.VIDEO
        )
        landmarker = mp_vision.HandLandmarker.create_from_options(options)
        logging.info("HandLandmarker initialized")
        return landmarker

    def _update_stable_prediction(self, current_pred: str, threshold: float = 3.0):
        """Giữ cùng prediction >= threshold (giây) thì xác nhận"""
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

        # cùng prediction
        if self.prediction_start_time is not None and (now - self.prediction_start_time) >= threshold:
            self.confirmed_prediction = current_pred

    def _on_space_press(self, event=None):
        """Thêm khoảng trắng vào câu khi nhấn phím cách"""
        # tránh chèn nhiều khoảng trắng liên tiếp
        if not self.sentence_tokens or self.sentence_tokens[-1] != ' ':
            self.sentence_tokens.append(' ')
            self.last_appended_token = ' '

            # cập nhật label ngay lập tức
            sentence = "".join(self.sentence_tokens)
            self.sentence_label.configure(text=f"Câu: {sentence}")
        return "break"

    def normalize_landmarks(self, landmarks):
        """Normalize landmarks same way as in create_dataset.py"""
        x_coordinates = [lm.x for lm in landmarks]
        y_coordinates = [lm.y for lm in landmarks]

        min_x = min(x_coordinates)
        min_y = min(y_coordinates)

        normalized_landmarks = []
        for lm in landmarks:
            normalized_landmarks.extend([
                lm.x - min_x,
                lm.y - min_y
            ])

        return normalized_landmarks
    
    def draw_hand_skeleton(self, image, hand_landmarks):
        """Draw colored hand skeleton similar to the image"""
        h, w, _ = image.shape
        
        # Define connections for each finger with colors
        # Colors: Blue (thumb), Green (index), Yellow (middle), Pink/Beige (ring), Purple (pinky)
        finger_connections = [
            # Thumb (Blue) - BGR: (255, 144, 30) for a nice blue
            ([0, 1, 2, 3, 4], (255, 144, 30)),  # Blue in BGR
            # Index finger (Green)
            ([0, 5, 6, 7, 8], (0, 255, 0)),  # Green
            # Middle finger (Yellow)
            ([0, 9, 10, 11, 12], (0, 255, 255)),  # Yellow
            # Ring finger (Pink/Beige) - BGR: (203, 192, 255) for light pink/beige
            ([0, 13, 14, 15, 16], (203, 192, 255)),  # Light pink/beige
            # Pinky (Purple)
            ([0, 17, 18, 19, 20], (255, 0, 255)),  # Purple
        ]
        
        # Draw connections for each finger
        for finger_indices, color in finger_connections:
            for i in range(len(finger_indices) - 1):
                start_idx = finger_indices[i]
                end_idx = finger_indices[i + 1]
                
                start_point = hand_landmarks.landmark[start_idx]
                end_point = hand_landmarks.landmark[end_idx]
                
                start = (int(start_point.x * w), int(start_point.y * h))
                end = (int(end_point.x * w), int(end_point.y * h))
                
                # Nối hai khớp liên tiếp của cùng ngón bằng một đoạn thẳng màu (color)
                cv2.line(image, start, end, color, 2)
        
        # Draw palm connections (gray lines)
        palm_connections = [
            (0, 1), (0, 5), (0, 9), (0, 13), (0, 17),
            (5, 9), (9, 13), (13, 17)
        ]
        for start_idx, end_idx in palm_connections:
            start_point = hand_landmarks.landmark[start_idx]
            end_point = hand_landmarks.landmark[end_idx]
            
            start = (int(start_point.x * w), int(start_point.y * h))
            end = (int(end_point.x * w), int(end_point.y * h))
            
            cv2.line(image, start, end, (128, 128, 128), 2)
        
        # Draw joints
        joint_colors = {
            # Base joints (red squares)
            0: (0, 0, 255),  # Red
            # Thumb joints (blue circles)
            1: (255, 144, 30), 2: (255, 144, 30), 3: (255, 144, 30), 4: (255, 144, 30),
            # Index joints (green circles)
            5: (0, 255, 0), 6: (0, 255, 0), 7: (0, 255, 0), 8: (0, 255, 0),
            # Middle joints (yellow circles)
            9: (0, 255, 255), 10: (0, 255, 255), 11: (0, 255, 255), 12: (0, 255, 255),
            # Ring joints (pink/beige circles)
            13: (203, 192, 255), 14: (203, 192, 255), 15: (203, 192, 255), 16: (203, 192, 255),
            # Pinky joints (purple circles)
            17: (255, 0, 255), 18: (255, 0, 255), 19: (255, 0, 255), 20: (255, 0, 255),
        }
        
        for idx, landmark in enumerate(hand_landmarks.landmark):
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            color = joint_colors.get(idx, (255, 255, 255))
            
            if idx == 0:  # Base joint - draw as square
                cv2.rectangle(image, (x-5, y-5), (x+5, y+5), color, -1)
            else:  # Other joints - draw as circle
                cv2.circle(image, (x, y), 4, color, -1)
    
    def update_frame(self):
        if not self.running:
            return

        if self.cap is None:
            # Webcam chưa mở được, thử lại sau
            self.root.after(500, self.update_frame)
            return
            
        ret, frame = self.cap.read()
        if ret:
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert BGR to RGB for MediaPipe Tasks
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.hand_landmarker is not None:
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                ts_us = int(time.time() * 1e6)
                results = self.hand_landmarker.detect_for_video(mp_image, ts_us)
            else:
                results = None
            
            # Draw hand landmarks and make prediction
            if results and results.hand_landmarks:
                hand_landmarks = results.hand_landmarks[0]
                
                # Wrap landmarks để tái sử dụng hàm vẽ cũ
                class LmWrapper:
                    def __init__(self, x, y): self.x, self.y = x, y
                class HandWrap:
                    def __init__(self, lms): self.landmark = [LmWrapper(lm.x, lm.y) for lm in lms]

                wrapped = HandWrap(hand_landmarks)

                # Draw skeleton
                self.draw_hand_skeleton(frame, wrapped)
                
                # Make prediction
                if self.model is not None:
                    try:
                        normalized_landmarks = self.normalize_landmarks(hand_landmarks)

                        if len(normalized_landmarks) == 42:
                            landmarks_array = np.array([normalized_landmarks])
                            prediction = self.model.predict(landmarks_array)[0]
                            self.current_prediction = str(prediction)
                        else:
                            self.current_prediction = ""
                    except Exception as e:
                        print(f"Lỗi khi dự đoán: {e}")
                        logging.error(f"Prediction error: {e}")
                        self.current_prediction = ""
            else:
                self.current_prediction = ""

            # Cập nhật trạng thái giữ 3 giây
            self._update_stable_prediction(self.current_prediction)
            
            # Draw prediction box in top-left corner
            if self.current_prediction:
                # Black box with white border
                box_size = 60
                cv2.rectangle(frame, (10, 10), (10 + box_size, 10 + box_size), (255, 255, 255), 2)
                cv2.rectangle(
                                frame,
                                (12, 12),
                                (12 + box_size - 4, 12 + box_size - 4),
                                (0, 0, 0),
                                -1
                            )

                
                # White text
                text_size = cv2.getTextSize(self.current_prediction, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
                text_x = 10 + (box_size - text_size[0]) // 2
                text_y = 10 + (box_size + text_size[1]) // 2
                cv2.putText(frame, self.current_prediction, (text_x, text_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)

            # Nếu có ký tự đã xác nhận mới, thêm vào câu
            if self.confirmed_prediction and self.confirmed_prediction != self.last_appended_token:
                self.sentence_tokens.append(self.confirmed_prediction)
                self.last_appended_token = self.confirmed_prediction

            # Cập nhật label dưới panel đen
            status_text = f"Giữ 3s: {self.confirmed_prediction}" if self.confirmed_prediction else "Giữ 3s: ..."
            self.status_label.configure(text=status_text)

            if self.sentence_tokens:
                sentence = "".join(self.sentence_tokens)
                sentence_text = f"Câu: {sentence}"
            else:
                sentence_text = "Câu: "
            self.sentence_label.configure(text=sentence_text)
            
            # Convert to RGB for tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize to fit panel
            panel_height = int(self.window_height * 0.6)
            aspect_ratio = frame.shape[1] / frame.shape[0]
            panel_width = int(panel_height * aspect_ratio)
            
            frame_resized = cv2.resize(frame_rgb, (panel_width, panel_height))
            
            # Convert to ImageTk format
            image = Image.fromarray(frame_resized)
            photo = ImageTk.PhotoImage(image=image)
            
            # Update label
            self.webcam_label.configure(image=photo)
            self.webcam_label.image = photo  # type: ignore[attr-defined]
        
        # Schedule next update
        self.root.after(30, self.update_frame)
    
    def on_closing(self):
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamViewerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
