import os
import pickle
import cv2
import mediapipe as mp
import numpy as np

# ---CONFIG---
data_dir = r"D:\python\ASL\idea\RealTime-ASL-Translator\dataset_vsl_ready" 


SAVE_FILE = "./VSL.pickle" 

# ---MEDIAPIPE ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True, 
    max_num_hands=1,            # Chỉ lấy 1 tay để tránh lỗi
    min_detection_confidence=0.3 # Độ nhạy 0.3 để bắt được nhiều ảnh hơn
)

dataset = []
labels = []

# Check dir folder is exis ?
if not os.path.exists(data_dir):
    print(f"LỖI: Không tìm thấy thư mục: {data_dir}")
    exit()

print("Start to processing data")

# ---The Loop Processing ---
directories = os.listdir(data_dir)
total_dirs = len(directories)

for i, directory in enumerate(directories):
    path = os.path.join(data_dir, directory)
    
    # Skip if not a folder
    if not os.path.isdir(path):
        continue

    # Get the list of image
    img_list = os.listdir(path)
    total_imgs = len(img_list)
    
    print(f"[{i+1}/{total_dirs}] In progress CLASS '{directory}'... ({total_imgs} IMAGE)")

    success_count = 0
    for img_idx, img_path in enumerate(img_list):
        # Read the image
        full_path = os.path.join(path, img_path)
        image = cv2.imread(full_path)

        if image is None:
            continue

        # Covert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # MediaPipe process
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            # Only the frist hand
            hand_landmark = results.multi_hand_landmarks[0]
            
            x_coordinates = []
            y_coordinates = []

            for landmark in hand_landmark.landmark:
                x_coordinates.append(landmark.x)
                y_coordinates.append(landmark.y)

            min_x = min(x_coordinates)
            min_y = min(y_coordinates)

            normalized_landmarks = []
            for landmark in hand_landmark.landmark:
                normalized_landmarks.extend([
                    landmark.x - min_x,
                    landmark.y - min_y
                ])
            
            dataset.append(normalized_landmarks)
            labels.append(directory)
            success_count += 1
        
        # Print the progress 
        if img_idx % 100 == 0:
            print(f"   -> Đã quét {img_idx}/{total_imgs} ảnh...", end="\r")

    print(f"   -> Hoàn thành lớp '{directory}': Lấy được {success_count}/{total_imgs} mẫu.")

# ---SAVE FILE---
print("\nSave file pickle...")
with open(SAVE_FILE, "wb") as f:
    pickle.dump({"dataset": dataset, "labels": labels}, f)

print(f"DONE! Saved in '{SAVE_FILE}'.")