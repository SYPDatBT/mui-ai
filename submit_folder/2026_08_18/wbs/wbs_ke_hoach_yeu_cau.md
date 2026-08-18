# Kế hoạch & yêu cầu dựng WBS — chốt 2026-08-19

File này là **đầu bài để dựng và sửa mọi bản WBS của task tái cấu trúc source app**. Ai dựng lại WBS thì đọc file này trước, làm đúng theo đây, không hỏi lại.
Sản phẩm: `wbs_app_restructure_20260819.md` (bảng) + `wbs_app_restructure_20260819_giaithich.md` (giải thích).

---

## 1. Mục đích và người đọc

| | |
|---|---|
| Mục đích | Trả lời 2 câu hỏi masao (mui) gửi Slack ngày 19/08: ① 内訳 của ước lượng **15~27 người-ngày** ② có rút về **khoảng 1 tuần** không (masao cho rằng được, vì kế hoạch/cấu trúc đã có sẵn và có thể dùng AI) |
| Người đọc | Nội bộ SYP trước; sau khi user duyệt thì dịch sang tiếng Nhật gửi mui |
| Ngôn ngữ | **Tiếng Việt trước**, bản Nhật chỉ làm khi user yêu cầu |

## 2. Nguồn để dựng — không được bịa kế hoạch mới

WBS là **bản chi tiết hoá của ước lượng đã nộp cho khách**, không phải kế hoạch mới:

1. `CLIENT_REPORT_APP_RESTRUCTURE_ja.md` **§5.6** — lộ trình 5 giai đoạn.
2. `CLIENT_REPORT_APP_RESTRUCTURE_ja.md` **§5.7** — ước lượng 15~27 người-ngày cho giai đoạn 1–5.
3. Đề bài mui: `requirements/app_source_change.md` (3 goal + lịch) và `requirements/chokkin_irai.md`.
4. Slack masao 19/08 (2 câu hỏi ở mục 1).
5. Số liệu source **đếm trực tiếp trên đĩa**, repo `syp-eminelstandard-app` commit `41ee385` — không lấy từ báo cáo, không đoán.

⇒ **Ràng buộc số học**: tổng công dự kiến của giai đoạn 1–5 phải đúng **15,0 MD**; trường hợp xấu nhất cộng lại đúng **27,0 MD**. Sửa một dòng thì phải sửa tổng, nếu không bảng mâu thuẫn với con số đã báo khách.

## 3. Template cột — bắt buộc, theo đúng file mẫu `WBS_au PAYアウトバウンド対応(SYP)`

Giữ nguyên 11 cột, đúng thứ tự này, **không thêm cột mới**:

| # | Cột | Ghi gì |
|---|---|---|
| 1 | № | Số thứ tự chạy 1…N |
| 2 | Hạng mục | Tên việc. **Hàng cha in đậm**, hàng con thụt lề bằng một khoảng trắng rộng |
| 3 | Phụ trách | `Lead` / `Dev1` / `Dev2` / `mui` — vai trò chung chung, không ghi tên thật |
| 4 | Công dự kiến (MD) | Ước lượng |
| 5 | Công thực tế (MD) | Điền khi làm xong |
| 6 | Tiến độ (%) | 0 / 100 hoặc số giữa |
| 7 | Bắt đầu dự kiến | dd/mm |
| 8 | Kết thúc dự kiến | dd/mm |
| 9 | Bắt đầu thực tế | dd/mm, để trống nếu chưa làm |
| 10 | Kết thúc thực tế | dd/mm, để trống nếu chưa làm |
| 11 | Ghi chú | Điều kiện hoàn thành, cảnh báo, **và con số "tối đa X MD"** của những dòng có biên độ rộng |

**Học từ file mẫu (phương pháp, không phải hạng mục)**: hàng cha mô tả nhóm rồi tới các hàng con · một dòng = một thứ kiểm chứng được · việc kiểm tra và việc review là dòng riêng · việc chờ khách vẫn có dòng nhưng công = `-`.
**Không bê hạng mục của file mẫu sang** — dự án khác nhau, phải bám đề bài mui lần này.

## 4. Quy ước công số

- Đơn vị **MD = người-ngày**; 1 MD = 1 người làm 1 ngày. Bước nhảy nhỏ nhất **0,25 MD**.
- Việc của khách hoặc thời gian chờ: công = `-`.
- Con số "tối đa" **không tạo cột riêng** (vi phạm mục 3) — viết trong cột Ghi chú.
- Việc đã làm phải có **công thực tế + ngày thực tế + tiến độ 100%**.

## 5. Quy ước cấu trúc bảng

- **Một bảng duy nhất** cho toàn bộ đầu việc. Không tách bảng theo mảng, **không đánh ký hiệu A/B/C**.
- Hai cấp là đủ: hàng cha (nhóm) → hàng con (đầu việc). Không đẻ cấp 3.
- **Khoảng 35 dòng**, không phải 100. Gộp các bước cơ học cùng buổi vào một dòng.
- Sau bảng chỉ giữ những khối thật cần: phân việc theo ngày · điều kiện · rủi ro · việc chờ mui. Không thêm mục tổng quan, quy ước, lịch sử.

## 6. Phạm vi

| Trong phạm vi | Ngoài phạm vi |
|---|---|
| Đề xuất cấu trúc + phản ánh review của mui | Refactor E-Smart (mui yêu cầu làm **sau khi có môi trường dev riêng**) |
| Dựng workspace, dời E-Smart, tách gói chung | Dựng môi trường AWS `dev` riêng cho E-GW |
| Khởi tạo app Eminel, CI/CD 2 app, hồi quy, bàn giao | Chiến lược branch BE / màn hình quản trị |
| | Điều tra danh sách batch backend |
| | Phát triển tính năng nghiệp vụ của Eminel |

## 7. Nhân sự và lịch

- Vai trò: **Lead** (thiết kế, review, đối khách) · **Dev1** (lập trình chính) · **Dev2** (lập trình phụ + hồi quy). Không ghi tên thật.
- Ngày làm việc **T2–T6**; nghỉ **02/09** (Quốc khánh).
- Mốc do mui đưa: mui review đề xuất **17–19/08** → SYP phản ánh **20–21/08** → tuần implement **24–28/08**.
- Kế hoạch phải cho thấy rõ **cần bao nhiêu người trong bao nhiêu ngày**, vì đó là câu hỏi của masao.

## 8. Nguyên tắc nội dung

1. **Xác nhận việc đã làm**: mọi đầu việc đã hoàn thành tính đến ngày lập phải nằm trong bảng với ngày thực tế.
2. **Nói thẳng chênh lệch**: nếu khối lượng không vừa mong muốn của khách thì ghi rõ, kèm phương án và rủi ro — không im lặng bóp số cho vừa.
3. **Được phép nhiều hơn mong muốn của khách một chút**, nhưng **bắt buộc giải thích vì sao nhiều hơn** trong file giải thích.
4. **Chỉ sửa cái sai đến mức đổi quyết định của người đọc** — không rà đến mức không bao giờ nộp được.
5. Mọi con số về source phải kiểm trên đĩa trước khi viết.

## 9. Quy trình bắt buộc

1. Dựng/ sửa WBS theo đúng file này.
2. **Review 3 vòng** theo skill `3-step-review`: **Vòng 1** xác thực dẫn chứng và số học · **Vòng 2** nhất quán nội bộ và giữa 2 file · **Vòng 3** dễ hiểu, tự chứa cho người đọc lần đầu.
3. Ghi kết quả 3 vòng vào mục 10 của chính file này.

---

## 10. Nhật ký review — 3 vòng, chạy ngày 19/08

**Vòng 1 — xác thực dẫn chứng & số học (4 finding, sửa hết)**

| # | Phát hiện | Đã xử lý |
|---|---|---|
| 1 | Hàng cha dòng 1 ghi "Tối đa 4,5" nhưng không hàng con nào có con số tối đa ⇒ không kiểm chứng được | Bỏ, thay bằng "Đã tiêu 3,25/3,75"; tổng tối đa toàn bảng sửa 33,0 → **32,25** |
| 2 | Hàng cha "Bàn giao" ghi tối đa 1,5 nhưng hàng con cộng ra 1,0 | Thêm "Tối đa 1,0" ở dòng 34 |
| 3 | Bảng phân việc theo ngày **vượt tải nhiều ô** (Dev1 ngày 24/08 = 1,25 · Dev2 ngày 28/08 = 1,5 · Lead ngày 31/08 = 1,5) và vi phạm thứ tự (xếp `features/common` cùng ngày `data` chưa xong) | Xếp lại toàn bộ, **kéo từ 6 lên 7 ngày** (thêm 01/09); đổi phụ trách dòng 19, 23, 28, 31, 35; dời dòng 30 sang 31/08 và dòng 32 sang 01/09. Sau khi sửa: **không ô nào vượt 1,0** — Dev1 6,25 · Dev2 5,25 · Lead 4,5 |
| 4 | Bảng ngày có việc "chuẩn bị máy build" không tương ứng dòng nào trong WBS | Bỏ khỏi bảng ngày |

**Vòng 2 — nhất quán nội bộ & giữa 2 file (3 finding, sửa hết)**

| # | Phát hiện | Đã xử lý |
|---|---|---|
| 1 | Sau khi đổi 6 → 7 ngày, 4 chỗ còn ghi "6 ngày" (đầu file, dòng tổng kết, tiêu đề điều kiện, mục chờ mui) | Sửa cả 4; kiểm lại bằng grep "6 ngày" = 0 |
| 2 | File giải thích còn trỏ "cột MD tối đa" trong khi cột đó **đã bỏ** để giữ đúng 11 cột của template mẫu | Sửa thành "con số tối đa ghi trong cột Ghi chú" |
| 3 | Điều kiện số 1 ghi "15 người-ngày" trong khi phần còn phải làm là 16,5 | Sửa thành 16,5 |

**Vòng 3 — dễ hiểu & tự chứa (2 finding, sửa hết)**

| # | Phát hiện | Đã xử lý |
|---|---|---|
| 1 | Dùng thuật ngữ "đường găng" mà không giải thích tại chỗ — người đọc phía mui không bắt buộc biết từ này | Viết lại thành "chuỗi việc không thể rút ngắn bằng cách thêm người", ở cả bảng rủi ro lẫn file giải thích |
| 2 | Lý do "vì sao nhiều hơn 1 tuần" ở file giải thích còn dùng lập luận cũ (15 ÷ 3 người = 5 ngày, không có đệm) — không còn khớp sau khi xếp lại lịch | Viết lại theo lý do thật: **ràng buộc thứ tự công việc**, kèm con số tải từng người |

**Kết luận sau 3 vòng**: bảng đứng vững về số học (giai đoạn 1–5 = 15,0 / tối đa 27,0 đúng con số đã báo mui; tổng 19,75 / 32,25), lịch xếp được thật không vượt tải, và hai file không còn mâu thuẫn. **Kết quả thay đổi so với bản trước review: 6 ngày → 7 ngày làm việc** (24–28/08 + 31/08 + 01/09).
