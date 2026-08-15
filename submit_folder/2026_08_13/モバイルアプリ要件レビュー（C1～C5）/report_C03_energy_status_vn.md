# C3. Hiển thị trạng thái năng lượng hiện tại (エネルギーの現在状態表示)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đang review |

## Tổng quan Requirement

Có thể xem gộp trong 1 màn hình: tình trạng phát điện và dòng chảy năng lượng toàn nhà (cân bằng điện năng).

## Yêu cầu chính

### Trạng thái phát điện

- Xem được hiện có đang phát điện hay không (trạng thái phát điện) và công suất phát điện hiện tại (W)
  - Hiện hành đối tượng là trạng thái phát điện của Coremo／Enefarm, chạm vào icon trạng thái phát điện thì hiện số liệu công suất phát điện. Yêu cầu mới kế thừa cơ chế này

### Cân bằng điện năng

- Xem được trong 1 màn hình: phát điện mặt trời・phát điện My Home・điện tiêu thụ・mua điện・bán điện・sạc xả pin lưu trữ (kWh), tiêu thụ gas (㎥)
  - Hiển thị bắt buộc ở hiện hành gồm 5 mục: mức dùng gas・mua điện・bán điện・phát điện mặt trời・phát điện My Home. Yêu cầu tích hợp thêm điện tiêu thụ và sạc/xả pin lưu trữ vào danh sách đối tượng
- 【Mới】Chuyển đổi xem giữa giá trị tức thời・giờ・ngày・tháng
  - Giá trị tức thời là khái niệm không tồn tại ở app hiện hành (đơn vị ngắn nhất hiện hành là giá trị giờ)
- Biết được năm/tháng/ngày/giờ mà giá trị đang hiển thị là của thời điểm nào
- Chọn bất kỳ giờ・ngày・tháng để xem giá trị tại thời điểm đó
  - Hiện hành di chuyển bằng thao tác trượt trong phạm vi mỗi trục thời gian
- 【Mới】Trong lúc đang xem giá trị tức thời, có thể cập nhật data mới nhất vào bất kỳ lúc nào
  - Tần suất cập nhật・cách lấy data vẫn TBD trong yêu cầu tích hợp (sẽ chốt ở giai đoạn spec chi tiết)
- Hạng mục・kiểu hiển thị thay đổi tùy theo thiết bị lắp đặt và hợp đồng (thiết bị đối tượng: điện mặt trời・Coremo／Enefarm・pin lưu trữ)
  - Hiện hành có 12 kiểu theo tổ hợp danh sách thiết bị × thông tin hợp đồng, chi tiết điều kiện chuyển đổi vẫn TBD trong yêu cầu tích hợp
- Nếu không có thiết bị đối tượng của cân bằng thì không hiển thị cân bằng điện năng; nếu có thiết bị nhưng không có data thì biết được là không có data
  - Hành vi hiện hành: không có thiết bị phát/lưu điện thì xóa hẳn mục đó khỏi menu, có thiết bị nhưng không có data thì hiển thị "Không có data cần thiết"
- Nếu có lắp thiết bị phát điện・lưu trữ bán ngoài thị trường nhưng không liên kết với EMINEL thì không hiển thị cân bằng điện năng

### Tính lành mạnh của data

- Với mục không lấy được giá trị đo, được hiểu là chưa lấy được

## Việc cần xác nhận

- Định nghĩa "giá trị tức thời" (giá trị mới nhất lấy trực tiếp từ thiết bị, hay giá trị N phút được upload lên cloud) → Đang xem xét
  - Phía Hokkaido Gas dự kiến theo hướng lấy trực tiếp từ thiết bị, nhưng có lo ngại: nếu thời điểm lấy data từ nhiều thiết bị lệch nhau thì tính toán không khớp. Đặc biệt điện tiêu thụ được tính bằng công thức, nên khi người dùng tự kiểm tra lại có thể thấy lệch số
- Thời hạn lưu trữ data: giá trị tức thời = 0 (không nhìn lại quá khứ)／giá trị giờ = 1 tuần／giá trị ngày = 1 tuần／giá trị tháng = 2 năm
