# C1. Hiển thị Graph (グラフ表示)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đang review |

## Tổng quan Requirement

Có thể tự mình nhìn lại diễn biến của năng lượng, nhiệt độ phòng... qua graph. Có thể so sánh với trung bình của hộ gia đình tương tự hoặc với chính mình năm trước.

- Xem được graph diễn biến của môi trường sống (nhiệt độ phòng・độ ẩm・cảm biến chuyển động) và các loại năng lượng, mỗi loại theo đơn vị riêng
- Mỗi graph chuyển đổi được trục thời gian: giá trị theo giờ・theo ngày・theo tháng
- So sánh được kết quả tháng hiện tại với "trung bình thực tế", "trung bình hộ tương tự", "kết quả năm trước"
- Graph hiển thị được thay đổi tùy theo thiết bị lắp đặt・data lấy được

## Yêu cầu chính

### Chung cho graph

- Trục thời gian: giá trị giờ = 1 tuần gần nhất, giá trị ngày = 1 năm gần nhất, giá trị tháng = năm hiện tại (riêng cảm biến chuyển động có trục thời gian riêng)
  - Trục thời gian ở app hiện hành là ngày (24 giờ×7 ngày)・tháng (tháng trước+tháng này)・năm (năm ngoái+năm nay). Yêu cầu mới lấy đây làm nền, thay bằng phạm vi đã chốt theo yêu cầu tích hợp
- Chọn xem bất kỳ ngày・tháng・năm nào
- Ở graph giá trị ngày・tháng, so sánh được với trung bình thực tế (trung bình của chính nhà mình trong quá khứ, trừ cảm biến chuyển động)
- Ở graph giá trị ngày・tháng, so sánh được với trung bình hộ tương tự cho lượng tiêu thụ gas・lượng tiêu thụ điện・lượng phát điện (chỉ áp dụng cho giá trị tháng)
  - "Trung bình hộ tương tự" là khái niệm khác với trung bình thực tế của chính nhà mình ở trên. Nhóm được tạo từ giá trị nhập lúc onboarding hoặc thông tin thuộc tính TagTag đang có, cập nhật nhóm 1 lần/tháng. Ở hiện hành, so sánh trung bình chỉ có ở đơn vị năm (gas・điện・dầu hỏa・phát điện); điểm mở rộng của yêu cầu mới là thêm so sánh trung bình cho cả giá trị ngày・tháng
- Ở graph giá trị tháng, so sánh được với chính mình năm trước
  - Đối tượng so sánh năm trước ở hiện hành có 5 loại: gas・điện・dầu hỏa・phát điện・mua bán điện
- Graph hiển thị thay đổi theo thiết bị lắp đặt・data lấy được
  - Hiện hành: submenu được cấu thành theo loại data nhận được, graph nào không có data thì ẩn đi — yêu cầu mới kế thừa cơ chế này

### Graph môi trường sống

- Xem được diễn biến nhiệt độ phòng (℃) theo từng phòng
- 【Mới】Xem được diễn biến độ ẩm (%) theo từng phòng
  - Graph hiện hành không có độ ẩm, đây là bổ sung mới lần này. Cách xử lý theo từng phòng giống như nhiệt độ (với tiền đề là có cảm biến nhiệt độ-độ ẩm theo C4)
- Xem được diễn biến số lần phát hiện chuyển động (số lần phát hiện)
  - Không thuộc đối tượng so sánh trung bình・năm trước. Cài đặt giám sát・thông báo do D4 (thông báo theo dõi/mimamori) đảm nhận riêng

### Graph năng lượng

- Lượng tiêu thụ gas (㎥): nếu có lắp remote Wi-Fi + liên kết app hãng sản xuất thì xem được tách riêng sưởi/nước nóng, còn lại thì hiển thị tổng hợp
- Lượng điện tiêu thụ (kWh): giá trị tính theo công thức "điện mặt trời + phát điện gas + xả pin lưu trữ − sạc pin lưu trữ + mua điện − bán điện"
  - Ở hiện hành mục này được hiển thị dưới tên "lượng điện tiêu thụ"
- Lượng điện phát ra (kWh): trong số điện mặt trời・phát điện My Home, xem được dạng chồng (stack) những data lấy được
- Lượng bán/mua điện (kWh)
  - Chỉ hiển thị khi có lắp thiết bị phát điện (Coremo／điện mặt trời)
- Lượng sạc/xả của pin lưu trữ (kWh)
  - Ở hiện hành, phạm vi hiển thị tháng・năm của pin lưu trữ chỉ có tháng này・năm nay

## Việc cần xác nhận

- Cách xử lý graph lượng tiêu thụ dầu hỏa → Đã chốt: không cần
- Có hiển thị tất cả graph trên app EMINEL không (giả định không hiển thị màn hình TagTag trên app) → Đang xác nhận với Hokkaido Gas
- Cách ra số liệu trung bình thực tế của nhà mình (ví dụ: trung bình giá trị ngày = trung bình giá trị ngày của 1 tháng gần nhất, có đúng ý này không) → OK. Tuy nhiên phạm vi tính trung bình phụ thuộc vào range của trục thời gian
- Thời hạn lưu data graph 2 năm có ổn không → Về quy mô thì khoảng 2 năm là OK. Thời gian lưu trữ tối ưu theo từng độ chi tiết data đang được phía mui xem xét thêm
