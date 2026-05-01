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
