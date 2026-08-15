# C5. Gợi ý tiết kiệm năng lượng (省エネアドバイス)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đang review |

## Tổng quan Requirement

Nhận được gợi ý tiết kiệm năng lượng phù hợp với mình, và có thể hành động ngay (đổi cài đặt...). Đạt được thì tích điểm.

- Nhận gợi ý tiết kiệm năng lượng được phát riêng cho mình, có thể xem lại sau
- Từ gợi ý có thể chuyển tới màn hình/cài đặt liên quan để hành động ngay
- Đạt điều kiện của từng gợi ý thì được cộng điểm

## Yêu cầu chính

- Nhận gợi ý tiết kiệm năng lượng được phát riêng cho mình
  - Cơ chế nhận thông báo (Push) do D3 đảm nhận. C5 chỉ xử lý phần nội dung/trạng thái của gợi ý sau khi đã nhận được
- Xem lại được gợi ý đã nhận
  - Hiện hành có cấu trúc danh sách + dialog chi tiết. Cách thể hiện màn hình cụ thể sẽ quyết định ở giai đoạn thiết kế
- Từ gợi ý, chuyển tới màn hình/cài đặt liên quan để hành động ngay
  - Đích chuyển hướng được định nghĩa theo từng loại gợi ý (ví dụ: màn hình graph, màn hình cài đặt sưởi...). Hiện hành có nút "thử xem" đảm nhận vai trò này
- Đạt điều kiện quy định của từng gợi ý thì được cộng điểm
  - Điều kiện cấp và số điểm dự kiến có thể thay đổi từ phía vận hành (màn hình quản lý, F-AD-05). Giá trị hiện hành (5〜100pt) chỉ là giá trị riêng của app hiện hành, không chắc sẽ giữ nguyên. Việc quản lý số dư điểm sau khi cộng do A3 đảm nhận
- Xem được trạng thái của gợi ý (chưa đọc・đã đọc・đã đạt)
  - Có gợi ý chưa đọc thì hiển thị badge ở footer. Mở chi tiết thì thành đã đọc; gợi ý đã đạt được đánh dấu riêng (ví dụ dấu tick) nhưng vẫn giữ trong danh sách

### Các loại gợi ý

| Loại | Nội dung | Ví dụ ở hiện hành |
|---|---|---|
| Nhắc nhở | Thúc giục xác nhận kết quả・thành tích | Nhắc phí・nhắc lượng phát thải CO2 |
| Xem lại cài đặt | Thúc giục xem lại cách dùng・cài đặt | Xem lại cách dùng nước nóng/điện・xem lại cài đặt nhiệt độ・cài đặt hẹn giờ・thông báo tỷ lệ sưởi |
| Khác | Các loại phát riêng lẻ khác | Kỷ niệm ngày EMINEL・gợi ý tiết kiệm năng lượng tự do |

## Việc cần xác nhận

- Không có
