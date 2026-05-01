# CS406.Q11 - Trích xuất thông tin hóa đơn

## Giới thiệu
Cuộc thi **MC_OCR 2021** là cuộc thi về trích xuất thông tin quan trọng từ ảnh chụp hóa đơn bán lẻ tại Việt Nam.  
Thông tin chi tiết: https://www.rivf2021-mc-ocr.vietnlp.com/

Dưới đây là một số ảnh mẫu:

![samples](https://raw.githubusercontent.com/TranDucThien-0509/CS406.Q11/main/mc_ocr_samples.JPG)

---

## Mục tiêu

Dự án này hướng tới việc xây dựng một hệ thống tự động trích xuất thông tin từ ảnh hóa đơn bán lẻ tiếng Việt, với các mục tiêu chính:

- **Nhận dạng ký tự (OCR)** từ ảnh hóa đơn trong điều kiện thực tế (nhiễu, mờ, lệch góc, ánh sáng không đồng đều).

- **Trích xuất các trường thông tin quan trọng**, bao gồm:
  - Tên cửa hàng  
  - Địa chỉ  
  - Ngày giờ  
  - Tổng tiền  

- **Xử lý và chuẩn hóa dữ liệu đầu ra** để phục vụ các hệ thống downstream như:
  - Kế toán tự động  
  - Quản lý chi tiêu  
  - Phân tích dữ liệu bán lẻ  

- **Tối ưu độ chính xác và hiệu năng** của mô hình trong bối cảnh dữ liệu tiếng Việt đa dạng.

- **Xây dựng pipeline hoàn chỉnh**, bao gồm:
  - Tiền xử lý ảnh  
  - OCR  
  - Trích xuất thông tin  
  - Hậu xử lý  

---

## Định hướng

Dự án không chỉ tập trung vào độ chính xác của mô hình mà còn hướng tới khả năng triển khai thực tế, đảm bảo tính ổn định và khả năng mở rộng trên nhiều loại hóa đơn khác nhau.

---

## Phương pháp

Hệ thống được xây dựng theo pipeline tuần tự, bao gồm các bước chính sau:

1. **Text Detection** – Phát hiện vùng chứa văn bản trong ảnh hóa đơn  
2. **Rotation Correction** – Chuẩn hóa góc xoay của ảnh/vùng text  
3. **OCR (VietOCR)** – Nhận dạng nội dung văn bản  
4. **KIE (Key Information Extraction)** – Trích xuất thông tin quan trọng  

Pipeline tổng thể:

![pipeline](https://raw.githubusercontent.com/TranDucThien-0509/CS406.Q11/main/pipeline_task_2.JPG)

---

## Text Detector

Mô-đun này có nhiệm vụ xác định vị trí các vùng chứa văn bản trong ảnh đầu vào.

- Input: Ảnh hóa đơn gốc  
- Output: Các bounding boxes chứa text  
- Vai trò:
  - Tách riêng từng dòng / vùng text
  - Giảm nhiễu cho bước OCR phía sau
    
![pipeline](https://raw.githubusercontent.com/TranDucThien-0509/CS406.Q11/main/text_detector.png)
---

## Rotation Corrector

Do ảnh hóa đơn trong thực tế có thể bị xoay hoặc lệch góc, bước này giúp chuẩn hóa lại orientation.

- Input: Ảnh hoặc các vùng text đã detect  
- Output: Ảnh đã được xoay đúng chiều  
- Vai trò:
  - Cải thiện độ chính xác OCR
  - Đảm bảo text không bị nghiêng/lật
    
![pipeline](https://raw.githubusercontent.com/TranDucThien-0509/CS406.Q11/main/rotation_corrector.png)
---

## OCR (VietOCR)

Sử dụng mô hình VietOCR để nhận dạng nội dung văn bản từ ảnh.

- Input: Các vùng text đã được căn chỉnh  
- Output: Chuỗi ký tự tương ứng  
- Vai trò:
  - Chuyển ảnh → text
  - Hỗ trợ tiếng Việt tốt

---

## KIE (Key Information Extraction)

Bước cuối cùng nhằm trích xuất các thông tin quan trọng từ text đã nhận dạng.

- Input: Văn bản từ OCR  
- Output: Dữ liệu có cấu trúc (JSON / dictionary)  
- Thông tin trích xuất:
  - Tên cửa hàng  
  - Địa chỉ  
  - Ngày giờ  
  - Tổng tiền  

- Vai trò:
  - Biến dữ liệu thô thành thông tin có ý nghĩa
  - Phục vụ các hệ thống downstream

![pipeline](https://raw.githubusercontent.com/TranDucThien-0509/CS406.Q11/main/KIE.png)
---

## 📌 Ví dụ kết quả

![result](https://raw.githubusercontent.com/TranDucThien-0509/CS406.Q11/main/input_result.png)
