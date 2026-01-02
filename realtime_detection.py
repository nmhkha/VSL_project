import cv2
import numpy as np
import mediapipe as mp
import pickle
from PIL import Image, ImageTk

labels = {
    "a": "a", "b": "b", "c": "c", "d": "d", "dd": "đ", "e": "e", "f": "f", "g": "g", "h": "h", "i": "i", 
    "j": "j", "k": "k", "l": "l", "m": "m", "n": "n", "o": "o", "p": "p", "q": "q", "r": "r", 
    "s": "s", "t": "t", "u": "u", "v": "v", "w": "w", "x": "x", "y": "y", "z": "z",
}

try:
    with open("D:\python\ASL\idea\RealTime-ASL-Translator\VSL_model.p", "rb") as f:
        model = pickle.load(f)
    rf_model = model["model"]
except FileNotFoundError:
    print("ERROR: Not fine file ASL_model.p. Check train_classifier.py frist.")
    exit()

# Initialize Mediapipe
mp_hands = mp.solutions.hands # Hand tracking solution
mp_drawing = mp.solutions.drawing_utils # Drawing utility
mp_drawing_styles = mp.solutions.drawing_styles # Pre-defined drawing styles

hands = mp_hands.Hands(
    static_image_mode=False, # Use dynamic mode for video streams
    max_num_hands=1, # Track at most one hand
    min_detection_confidence=0.8 # Set a high detection confidence threshold
)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Strings to store the concatenated sentence
predicted_text = " "
same_characters = ""
final_characters = ""
count = 0

# Function to update each frame and predict the character
def update_frame(video_label, text_area):
    global predicted_text, same_characters, final_characters, count
    ret, frame = cap.read()  # Capture frame-by-frame
    
    if ret:
        # Process the frame to display hand landmarks and predict the character
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        processed_image = hands.process(frame_rgb)
        hand_landmarks = processed_image.multi_hand_landmarks

        if hand_landmarks:
            for hand_landmark in hand_landmarks:
                # Draw landmarks on the frame
                mp_drawing.draw_landmarks(
                    frame, hand_landmark, mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

                # Collect landmark coordinates for prediction
                x_coordinates = [landmark.x for landmark in hand_landmark.landmark]
                y_coordinates = [landmark.y for landmark in hand_landmark.landmark]
                min_x, min_y = min(x_coordinates), min(y_coordinates)
                
                normalized_landmarks = []
                for coordinates in hand_landmark.landmark:
                    normalized_landmarks.extend([
                        coordinates.x - min_x,
                        coordinates.y - min_y
                    ])
                
                # Input process 
                sample = np.asarray(normalized_landmarks)
                if sample.shape[0] > 42: sample = sample[:42] # Cut if it has two hands
                sample = sample.reshape(1, -1)
                
                predicted_character = rf_model.predict(sample)[0]

                # Debug: what it print ?
                # print(f"Model du doan: {predicted_character}") 

                if predicted_character != "nothing": 
                    predicted_text += predicted_character
                    
                    if predicted_text[-1] != predicted_text[-2]: 
                        count = 0
                        same_characters = ""
                    else:
                        same_characters += predicted_character
                        count += 1

                    # Display the concatenated sentence in the text area
                    if count == 15:
                        
                        # Logic Delete and Space
                        if predicted_character == "del" or predicted_character == "1":
                            if final_characters:
                                final_characters = final_characters[:-1]
                                text_area.delete("1.0", 'end')
                                text_area.insert("1.0", final_characters)

                        elif predicted_character == "clear" or predicted_character == "2":
                            final_characters = ""
                            text_area.delete("1.0", 'end')

                        elif predicted_character == "space" or predicted_character == "3":
                            final_characters += " "
                            text_area.delete("1.0", 'end')
                            text_area.insert("1.0", final_characters)

                        # Logic add a char
                        else:
                            # Get the char display is safe
                            try:
                                char_to_add = labels[predicted_character]
                            except KeyError:
                                char_to_add = predicted_character
                            
                            if char_to_add != "": # Don't add a empty 
                                final_characters += char_to_add
                                text_area.delete("1.0", 'end')
                                text_area.insert("1.0", final_characters)

                        count = 0
                        same_characters = ""

                
                # 1. identify the display
                try:
                    display_text = labels[predicted_character]
                except KeyError:
                    display_text = predicted_character # If not in dictionary it will show the original

                # 2. position and color
                text_position = (20, 50) 
                background_color = (0, 0, 0)  # Black
                text_color = (255, 255, 255)  # White
                font_scale = 1.5
                thickness = 2

                # 3. calcualte the w and h of background
                (text_width, text_height), baseline = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                
                background_top_left = (text_position[0], text_position[1] - text_height - 10)
                background_bottom_right = (text_position[0] + text_width + 20, text_position[1] + 10)

                # 4. The background
                cv2.rectangle(frame, background_top_left, background_bottom_right, background_color, -1)

                # 5. Display the text
                cv2.putText(
                    img=frame,
                    text=display_text, 
                    org=(text_position[0] + 10, text_position[1]), 
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=font_scale,
                    color=text_color,
                    thickness=thickness,
                    lineType=cv2.LINE_AA
                )

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk 
        video_label.configure(image=imgtk)

    video_label.after(10, lambda: update_frame(video_label, text_area))

def release_video():
    cap.release()
    cv2.destroyAllWindows()