# C4. Hiển thị trạng thái hiện tại của cảm biến (センサー情報の現在状態表示)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đang review |

## Tổng quan Requirement

Xem được giá trị hiện tại của nhiệt độ・độ ẩm theo từng phòng.

## Yêu cầu chính

- Xem được nhiệt độ hiện tại (℃)・độ ẩm (%)
  - Nguồn kế thừa chính là yêu cầu tích hợp (F-ES-01 trạng thái nhiệt độ phòng hiện tại) cùng với chức năng hiển thị màn hình HOME của app hiện hành (cả hai đều là nguồn chính); riêng ESTA chỉ tham khảo khung hiển thị Dashboard vì nguồn cảm biến khác nhau
- Nếu có cảm biến ở nhiều phòng, chuyển đổi xem nhiệt độ・độ ẩm theo từng phòng
  - Hiện hành tối đa 2 phòng (chính／phụ). Tên phòng dựa theo cài đặt cấu trúc hộ gia đình
- Với mục không lấy được giá trị đo, biết được là chưa lấy được
  - Cách thể hiện cụ thể (ví dụ hiển thị "--") thuộc về hình thái hiện thực hóa nên không đặt thành yêu cầu (hiển thị khi khuyết số liệu sẽ được định nghĩa ở tầng 機能仕様)

## Việc cần xác nhận

- Không có
