import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

# --- CẤU HÌNH CÁC MODEL ---
models_config = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "SVM (Linear) ": SVC(kernel='linear'),
    "k-NN (k=5)   ": KNeighborsClassifier(n_neighbors=5)
}

# Load dữ liệu
print(" Đang tải dữ liệu...")
try:
    data_dict = pickle.load(open('./VSL.pickle', 'rb'))
    data = np.asarray(data_dict['dataset'])
    labels = np.asarray(data_dict['labels'])
except FileNotFoundError:
    print(" Lỗi: Không tìm thấy file 'VSL.pickle'.")
    exit()

# Chia tập dữ liệu
x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=labels, random_state=42)

print(f"\n BẮT ĐẦU SO SÁNH KÉP (TRAIN vs TEST) TRÊN {len(models_config)} MODEL")

# Hàm hỗ trợ tạo bảng 
def get_report_df(y_true, y_pred):
    report = classification_report(y_true, y_pred, output_dict=True)
    df = pd.DataFrame(report).transpose()
    
    # Đổi tên cột
    df.columns = ['Precision', 'Recall', 'F1-Score', 'Support']
    return df.round(4) # Làm tròn 4 chữ số

# Vòng lặp chạy từng model
for model_name, model in models_config.items():
    print("\n" + "#" * 90)
    print(f" MODEL: {model_name.upper()}")
    print("#" * 90)
    
    # Train
    model.fit(x_train, y_train)
    
    # Predict (Dự báo trên cả 2 tập)
    y_train_pred = model.predict(x_train)
    y_test_pred = model.predict(x_test)
    
    # Tạo 2 bảng dữ liệu
    df_train = get_report_df(y_train, y_train_pred)
    df_test = get_report_df(y_test, y_test_pred)
    
    # --- TRAIN ---
    print(f"\n🔹 BẢNG 1: KẾT QUẢ TRÊN TẬP HUẤN LUYỆN (TRAIN SET) - {model_name}")
    print(f"   (Độ chính xác tổng: {accuracy_score(y_train, y_train_pred)*100:.2f}%)")
    print("-" * 80)
    print(df_train)
    
    # --- TEST ---
    print(f"\n BẢNG 2: KẾT QUẢ TRÊN TẬP KIỂM THỬ (TEST SET) - {model_name}")
    print(f"   (Độ chính xác tổng: {accuracy_score(y_test, y_test_pred)*100:.2f}%)")
    print("-" * 80)
    print(df_test)
    
    print("\n" + "=" * 90)
    # Kết thúc 1 model, vòng lặp sẽ chuyển sang model tiếp theo


# Lưu model tốt nhất 
TOP_MODEL_NAME = "Random Forest"

if TOP_MODEL_NAME in models_config:
    # Lấy model đã được train từ dictionary ra
    final_model = models_config[TOP_MODEL_NAME]
    
    save_path = 'model.p'
    with open(save_path, 'wb') as f:
        pickle.dump({'model': final_model}, f)
        
    print(f" Đã chọn '{TOP_MODEL_NAME}' làm model chính thức.")
    print(f" Đã lưu thành công vào file '{save_path}'!")