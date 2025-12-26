# 📘 README: Model Testing & Evaluation
* **Thư viện cần thiết:** `scikit-learn`, `pandas`, `numpy`, `pickle`.

##  Các Model Được Thử Nghiệm

Script cấu hình sẵn 4 thuật toán phân loại (Classification) phổ biến:

| Model | Cấu hình tham số (Hyperparameters) | Đặc điểm |
| --- | --- | --- |
| **Random Forest** | `n_estimators=100` | Kết hợp 100 cây quyết định, giảm overfitting tốt. |
| **Decision Tree** | Default | Cây quyết định đơn lẻ, dễ bị overfitting. |
| **SVM (Linear)** | `kernel='linear'` | Máy vector hỗ trợ với nhân tuyến tính, tốt cho dữ liệu tách biệt rõ. |
| **k-NN** | `k=5` | Tìm 5 điểm dữ liệu gần nhất để phân loại. |

##  Quy Trình Xử Lý (Pipeline)

### Bước 1: Tiền xử lý dữ liệu

* Load file `.pickle`.
* **Chia tập dữ liệu (Data Splitting):**
* Tỷ lệ: **80% Train** - **20% Test**.
* `stratify=labels`: Đảm bảo tỷ lệ các nhãn (classes) trong tập Train và Test cân bằng nhau (tránh trường hợp tập Test thiếu hẳn một nhãn nào đó).
* `shuffle=True`: Trộn ngẫu nhiên dữ liệu.



### Bước 2: Huấn luyện & Đánh giá (Vòng lặp)

Chương trình chạy vòng lặp qua từng model để thực hiện:

1. **Fit:** Học trên tập `x_train`, `y_train`.
2. **Predict:** Dự báo lại trên cả `x_train` (để kiểm tra độ nhớ) và `x_test` (để kiểm tra độ tổng quát hóa).
3. **Reporting:** Sử dụng `classification_report` để tính các chỉ số:
* **Precision:** Độ chính xác khi dự báo đúng 1 class.
* **Recall:** Độ bao phủ (không bỏ sót mẫu của class).
* **F1-Score:** Trung bình điều hòa giữa Precision và Recall.
* **Accuracy:** Độ chính xác tổng thể.



> ** Note:** Việc so sánh kết quả giữa **Bảng 1 (Train)** và **Bảng 2 (Test)** giúp phát hiện hiện tượng **Overfitting** (nếu Train rất cao nhưng Test thấp) hoặc **Underfitting** (nếu cả 2 đều thấp).

### Bước 3: Lưu Model

* **Chiến lược:** Hard-code chọn model tốt nhất (trong code hiện tại đang set cứng là `"Random Forest"`).
* **Output:** Lưu model vào file `model.p` dưới dạng dictionary `{'model': final_model}` để các ứng dụng khác có thể load vào sử dụng.
