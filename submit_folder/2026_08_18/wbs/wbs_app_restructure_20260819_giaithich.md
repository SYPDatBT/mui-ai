# Giải thích WBS tái cấu trúc source app

Đi kèm `wbs_app_restructure_20260819.md`, số dòng khớp cột №. Nội bộ SYP · 2026-08-19.
Trả lời 3 câu: **WBS dựng từ đâu** · **thời gian đi vào đâu** · **vì sao SYP đề xuất 7 ngày trong khi masao mong 1 tuần**.

---

## 1. WBS này dựng từ đâu

Không phải kế hoạch mới. Nó là **bản chi tiết hoá của chính ước lượng đã nộp cho mui**:

- `CLIENT_REPORT_APP_RESTRUCTURE_ja.md` **§5.6** — lộ trình 5 giai đoạn (dựng workspace → tách gói chung → app Eminel → CI/CD → hồi quy).
- `CLIENT_REPORT_APP_RESTRUCTURE_ja.md` **§5.7** — ước lượng **15~27 người-ngày** cho 5 giai đoạn đó.

Vì thế cột "Công dự kiến" của 5 giai đoạn cộng lại đúng **15,0**, và các con số "tối đa" ghi trong cột Ghi chú cộng lại đúng **27,0**. Sửa một dòng thì phải sửa cả tổng, nếu không bảng sẽ mâu thuẫn với con số đã báo khách.

Số liệu về source (481 file Dart, 30 nhóm widget, 20 file `server/`, 131 file `data/`, 23 nhóm màn hình, 33 chỗ `Navigator.push`, không có file test) đều đếm trực tiếp trên `syp-eminelstandard-app` commit `41ee385` ngày 19/08.

---

## 2. Giải thích từng nhóm việc

| Dòng | Nhóm | Làm gì | Vì sao tốn ngần ấy |
|---|---|---|---|
| 1–7 | Đề xuất & làm việc với mui (3,75 MD, đã tiêu 3,25) | Khảo sát source, viết báo cáo 8 chương, tự review, lập WBS; còn lại là đọc PDF của mui và phản ánh feedback | Phần khảo sát chiếm 1,5 MD vì phải đếm thật trên 3 repo chứ không đoán từ tên thư mục |
| 8–12 | Giai đoạn 1 — dựng workspace + dời E-Smart (2,0 MD) | Tạo `apps/` + `packages/`, dời toàn bộ app hiện tại vào `apps/e-smart-app`, sửa đường dẫn, build lại 2 nền tảng | Việc cơ học, rủi ro thấp. Chỉ 13% ước lượng — **phần "đổi thư mục" như hình trong đề bài là phần rẻ nhất** |
| 13–19 | Giai đoạn 2 — tách gói chung (6,5 MD) | Tách `theme`, `ui_components`, `utils`, `data`, `features/common` ra khỏi app | **43% ước lượng, chỗ tốn nhất.** Lâu không phải vì dời file mà vì **gỡ code dính nhau**: widget "chung" đang gọi chuỗi đa ngữ và asset của E-Smart, tầng `data` có sinh code (retrofit/freezed) chạy xuyên gói |
| 20–23 | Giai đoạn 3 — app Eminel (1,5 MD) | Tạo app thứ hai, `go_router`, theme riêng, build và cài song song với E-Smart | Rẻ, vì app mới không có gánh nặng tương thích. Đây cũng là **phép thử** cho việc tách gói ở giai đoạn 2 — gói tách sai thì lộ ở đây |
| 24–26 | Giai đoạn 4 — CI/CD (1,0 MD) | Thêm tham số chọn app, bắt buộc build cả 2 app mỗi PR | Biên độ rộng (1,0~2,5) vì SYP **chưa nắm pipeline hiện tại** của mui |
| 27–32 | Giai đoạn 5 — hồi quy E-Smart (4,0 MD) | Mở tay 23 nhóm màn hình kiểm app cũ còn nguyên vẹn, kiểm font/ảnh/chuỗi/push, sửa lỗi | **27% ước lượng.** Repo **không có một file test nào**, nên không có cách nào ngoài kiểm tay. E-Smart đang chạy thật ngoài thị trường nên không thể bỏ bước này |
| 33–35 | Bàn giao (1,0 MD) | `README` cấu trúc mới + 3 kỷ luật giữ goal 3 + buổi bàn giao | **Nằm ngoài con số 15~27** vì báo cáo chỉ tính giai đoạn 1–5 |

---

## 3. Vì sao ước lượng rộng đến 15~27 (câu hỏi 1 của masao)

Biên độ gấp gần 2 lần đến từ đúng 3 chỗ, tất cả đều là **chưa biết trước khi mở code ra làm**:

| Chỗ | Min | Max | Điều chưa biết |
|---|---|---|---|
| `ui_components` | 1,5 | 3,0 | Trong 30 nhóm widget, chưa biết bao nhiêu nhóm còn dính chuỗi/asset của E-Smart. Mỗi nhóm dính là phải đổi cách truyền tham số |
| `packages/data` | 2,0 | 3,5 | Sinh code chạy xuyên gói — nếu retrofit/freezed cấu hình lại êm thì 2,0; nếu vướng thì mất cả ngày dò |
| Hồi quy + sửa lỗi | 4,0 | 6,0 | Chưa biết việc dời chỗ làm hỏng bao nhiêu màn hình. Không có test tự động nên không đo trước được |

Ba chỗ này chiếm **7,5/12,0 phần chênh lệch**. Nói ngắn: phần cơ học thì ước lượng chắc, phần "gỡ code dính nhau và chứng minh app cũ không hỏng" thì không.

---

## 4. Vì sao SYP đề xuất **7 ngày** chứ không phải 5 (câu hỏi 2 của masao)

Đề xuất: **3 người × 7 ngày làm việc** — trọn tuần 24–28/08 như masao mong muốn, cộng **31/08 và 01/09**. Ba lý do:

**① Chia theo đầu người thì vừa, nhưng xếp theo thứ tự công việc thì không vừa.**
16,5 người-ngày còn lại ÷ 3 người = 5,5 ngày trên giấy. Nhưng khi xếp thật ra từng ngày thì vướng thứ tự bắt buộc: phải dời chỗ xong mới tách được gói, tách gói xong mới dựng được app thứ hai, và hồi quy chỉ có ý nghĩa khi hai việc kia đã xong. Xếp đúng ràng buộc đó thì hai ngày cuối (CI/CD, hồi quy vòng 2, sửa lỗi, bàn giao) không nhét vừa trong tuần — xem bảng phân việc theo ngày, không ô nào được vượt 1,0 người-ngày.

**② Con số 15 chưa gồm tài liệu bàn giao.**
Báo cáo §5.7 nói rõ 15~27 là cho giai đoạn 1–5. `README` cấu trúc mới và 3 kỷ luật giữ goal 3 (dòng 33–35, 1,0 MD) nằm ngoài. Nếu không viết, người viết tính năng Eminel sau này sẽ đặt code sai chỗ và cấu trúc vừa dựng sẽ hỏng dần — tức là mất đúng cái goal 1 và goal 3 mà mui đặt ra.

**③ Có một chuỗi việc không thể rút ngắn bằng cách thêm người.**
`packages/data` (2,0 người-ngày) phải do **một người làm liền mạch** — chia đôi cho hai người thì hai bên sửa import chồng lên nhau, mất nhiều thời gian gỡ hơn là làm. Cộng chuỗi bắt buộc tuần tự: dựng khung → tách `data` → app Eminel dùng thử → hồi quy, riêng chuỗi này đã khoảng 5 ngày. Người thứ 4 chỉ giúp được phần hồi quy, không rút ngắn được chuỗi này.

**Điểm SYP đồng ý với masao**: hai lý do masao đưa ra đều đúng và đã được tính vào con số 15 (cận dưới), không phải cận trên 27:
- *Kế hoạch và cấu trúc đã có sẵn*: đúng — nên giai đoạn 1 chỉ còn 2,0 MD và không có thời gian "nghiên cứu phương án" trong bảng.
- *Dùng AI*: đúng ở phần cơ học, xem mục 5.

---

## 5. AI rút được chỗ nào, không rút được chỗ nào

| AI giúp được | AI không giúp được |
|---|---|
| Sửa import hàng loạt sau khi dời file | Quyết định **cái gì được lên gói chung** (dòng 14) — sai là tách lại từ đầu |
| Sinh khung file gói, `pubspec` cho 5 gói | Chạy `build_runner` và gỡ lỗi sinh code xuyên gói (dòng 18) |
| Dựng checklist hồi quy từ danh sách màn hình | **Mở app kiểm 23 nhóm màn hình bằng tay** (dòng 29–31) — chiếm 27% khối lượng |
| Rà chỗ trùng lặp, tìm phụ thuộc ngược bằng grep | Sửa lỗi hồi quy (dòng 32) — phụ thuộc lỗi thật gặp phải |

Đó là lý do con số cận dưới đã là 15 chứ không thấp hơn: **hơn một phần tư khối lượng là kiểm tay, AI không thay được.**

---

## 6. Nếu mui vẫn muốn đúng 5 ngày

Làm được, với 2 điều kiện cắt bớt — SYP nêu để mui quyết chứ không tự cắt:

1. **Đẩy CI/CD (dòng 24–26), hồi quy vòng 2 (dòng 30–32) và bàn giao (dòng 33–35) ra khỏi tuần**, làm bù tuần sau (khoảng 4,0 người-ngày). Tuần 24–28/08 chỉ còn giai đoạn 1, 2, một phần 3 và hồi quy vòng 1.
2. **Chấp nhận không có ngày đệm**: nếu hồi quy phát hiện nhiều lỗi thì phần sửa lỗi (dòng 32) tràn sang tuần sau.

Rủi ro kèm theo: bản E-Smart sau khi dời chỗ chưa được CI kiểm tự động lần nào trước khi bàn giao — trong khi repo vốn không có test. Đây là rủi ro đối với app **đang chạy thật ngoài thị trường**, nên SYP khuyến nghị giữ phương án 7 ngày.
