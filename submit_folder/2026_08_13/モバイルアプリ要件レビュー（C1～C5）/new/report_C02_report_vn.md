# C2. Hiển thị báo cáo (レポート表示)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã review xong (theo bảng README; header C02_report.md chưa cập nhật) |

## Tổng quan Requirement

Nhận được báo cáo tuần・tháng・năm, có thể nhìn lại thành quả tiết kiệm năng lượng và so sánh với hộ gia đình khác.

- Nhận và xem báo cáo tuần・tháng・năm theo đúng chu kỳ tương ứng
- Xem được chi tiết từng báo cáo: so sánh mức sử dụng/phí với quá khứ／dự báo mức sử dụng và lời khuyên (báo cáo "một câu")／hiệu quả tiết kiệm năng lượng／so sánh với hộ tương tự (xếp hạng)／hiệu quả thiết bị phát điện／hiệu quả giảm CO2
- Nhận thông báo khi mỗi báo cáo phát hành, và nhận được điểm ngay trong báo cáo
- Nội dung hiển thị và khả năng tính toán thay đổi tùy theo thiết bị lắp đặt・data thu được có hay không

## Yêu cầu chính

### Chung cho các báo cáo

- Nội dung hiển thị thay đổi tùy theo thiết bị lắp đặt・data thu được
  - Khi lắp cogen (đồng phát), dự kiến "so sánh hộ tương tự" và "hiệu quả giảm CO2" chỉ hiển thị giá trị tổng hợp (không tách riêng gas/điện)
- Biết được khi có mục/kỳ không tính toán được
  - Có thể phát sinh các trường hợp hiển thị khác nhau do thiếu data
- Nhận được thông báo (Push) khi báo cáo phát hành (cơ chế nhận thông báo do D3 đảm nhận)
- Nhận được điểm ngay trong báo cáo (quản lý số dư/lịch sử điểm do A3 đảm nhận)

### Phân loại nội dung (●=có xuất hiện)

| Nội dung | Tuần | Tháng | Năm |
|---|---|---|---|
| So sánh tuần (tuần này vs tuần trước, gas・điện) | ● | | |
| Mức sử dụng theo từng ngày | ● | | |
| Dự báo (mức sử dụng tháng này, điện・gas) | ● | | |
| Báo cáo "một câu" (bình luận・lời khuyên) | ●(của tuần này) | ●(của tháng này) | |
| So sánh tháng | | ● | |
| So sánh với hộ tương tự (xếp hạng) | | ● | ● |
| Hiệu quả tiết kiệm năng lượng (so với sưởi 24h, yên・chỉ mùa đông) | | ● | |
| Hiệu quả lắp thiết bị phát điện | | ● | |
| Tỷ lệ tự cung・tự tiêu thụ (%) | | ● | |
| So sánh năm nay và năm trước・tổng tiền tiết kiệm | | | ● |
| Hiệu quả giảm CO2 | | | ● |
| Graph | ● | ● | ● |
| Hiển thị phí (tiền gas・điện)? (cần xem xét) | ? | ? | ? |

### Báo cáo tuần

- 1 lần/tuần, nhận được so sánh mức sử dụng tuần này/tuần trước (gas・điện), mức sử dụng theo ngày, dự báo mức sử dụng tháng này, và báo cáo "một câu" dựa trên dự báo
  - Báo cáo tuần cũng có phương án do phía TagTag đảm nhận, nhưng đã chốt hiển thị trên app
  - Cách tính dự báo mức sử dụng dự kiến kế thừa nguyên cách tính sẽ triển khai ở phía nội dung tiết kiệm năng lượng

### Báo cáo tháng

- 【Mới】1 lần/tháng (sau khi có số đo đếm), nhận được so sánh phí tháng này với cùng tháng năm trước/tháng trước, và báo cáo "một câu" hướng tới tháng sau
  - Cụm "báo cáo tháng sau khi đo đếm" là khái niệm mới được đặt ra trong lần yêu cầu tích hợp này. So sánh tháng được đánh giá dựa trên phí
- Xem được hiệu quả tiết kiệm năng lượng (số tiền giảm phí gas tháng này so với sưởi 24 giờ)
  - Cách tính kế thừa nguyên cách tính của server concierge hiện hành
- Xem được so sánh với hộ tương tự (xếp hạng quy đổi 100 hộ, gas・điện・tổng hợp)
  - Có cogen thì chỉ hiển thị tổng hợp. Nếu số hộ trong nhóm không đạt mức tối thiểu thì hiển thị theo nhóm lớn hơn (trước khi lọc)
- 【Mới】Xem được hiệu quả của thiết bị phát điện (lượng bán điện・tiền bán điện・tỷ lệ tự cung・tỷ lệ tự tiêu thụ・tiền giảm mua điện/mua gas)
  - Tiền giảm mua điện・tiền giảm mua gas đang trong quá trình xem xét có triển khai hay không

### Báo cáo năm

- 【Mới】Xem được so sánh năm nay và năm trước, so sánh với hộ tương tự (thứ hạng), tổng số tiền tiết kiệm được
  - "So sánh năm nay và năm trước" là cách đọc lại từ cụm "so với 2 năm trước" trong yêu cầu tích hợp. Tuy nhiên tại thời điểm FY26 chưa có data thực tế quá khứ để so sánh
- Xem được hiệu quả giảm CO2 (lượng giảm・tỷ lệ tăng giảm theo so sánh cùng tháng năm trước, tính theo từng tháng)
  - Công thức của yêu cầu tích hợp là so sánh "tháng trước vs cùng tháng năm trước". Dự kiến tích lũy so sánh theo từng tháng để hiển thị trong năm. Có cogen thì chỉ hiển thị tổng hợp

## Việc cần xác nhận

- Đơn vị hiển thị của báo cáo tuần (có phát điện thì quy đổi năng lượng sơ cấp, hay trường hợp Ecojozu thì tách gas/điện) → Xác nhận với Hokkaido Gas
- Hiển thị phí (tiền gas・điện) trong báo cáo tháng (chỉ hiển thị 1 con số tổng, vì phí EMINEL là 1 mức phí cơ bản nên không tách được gas/điện) → Xác nhận với Hokkaido Gas
- Phần đảm nhận theo dõi phát điện (nội dung giống hệt theo dõi thời gian thực của C3, dự kiến C3 đảm nhận có đúng không) → Xác nhận với tích hợp §8-3 và Hokkaido Gas
- Có hiển thị phí ở mỗi báo cáo hay không → Hiện dự kiến "không" nhưng chưa chốt
- Phần đảm nhận báo cáo tuần của TagTag → Đã chốt: hiển thị trên app
- Việc có triển khai so sánh hộ tương tự (xếp hạng) hay không → Đã chốt: có triển khai
- Phạm vi xem lại báo cáo quá khứ → Tháng = tới 1 năm trước／Tuần = 1 tháng (cần xem xét spec)
- Phạm vi tạo hiệu quả tiết kiệm năng lượng → Của tháng đối tượng, OK
- Phân chia giữa báo cáo "một câu" và C5 (gợi ý tiết kiệm năng lượng) → Đã chốt là chức năng khác nhau (C2 chủ yếu là bình luận hướng tới tháng sau)
