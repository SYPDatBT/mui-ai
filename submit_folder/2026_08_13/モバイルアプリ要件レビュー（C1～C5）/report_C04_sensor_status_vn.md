# C4. Hiển thị trạng thái hiện tại của cảm biến (センサー情報の現在状態表示)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đang review |

## Tổng quan Requirement

Xem được giá trị hiện tại của nhiệt độ・độ ẩm theo từng phòng.

## Yêu cầu chính

- Xem được nhiệt độ hiện tại (℃)・độ ẩm (%)
  - Nguồn kế thừa chính là yêu cầu tích hợp (F-ES-01 trạng thái nhiệt độ phòng hiện tại); chức năng hiển thị màn hình HOME của app hiện hành chỉ là nguồn tham khảo phụ
- Nếu có cảm biến ở nhiều phòng, chuyển đổi xem nhiệt độ・độ ẩm theo từng phòng
  - Hiện hành tối đa 2 phòng (chính／phụ). Tên phòng dựa theo cài đặt cấu trúc hộ gia đình
- Với mục không lấy được giá trị đo, biết được là chưa lấy được
  - Cách thể hiện cụ thể (ví dụ hiển thị "--") thuộc về giai đoạn thiết kế nên không đặt thành yêu cầu

## Việc cần xác nhận

- Không có
