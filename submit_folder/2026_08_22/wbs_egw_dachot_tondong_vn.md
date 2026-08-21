# Đầu vào WBS — phát triển server E-GW độc lập: đã chốt gì, còn treo gì

> ⚠️ **FILE NỘI BỘ, TIẾNG VIỆT.** Không nộp cho mui / 北ガス (⛔#4).
> Mục đích: khi bắt đầu task **lập WBS cho phase phát triển E-GW độc lập với E-Smart**, đọc file này + các nguồn nó trỏ là đủ tiền đề — không phải đào lại từng phiếu QA.

| | |
|---|---|
| Ngày lập | 2026-08-21 (chuẩn bị cho task đặt tại folder `2026_08_22/`) |
| Nguyên tắc lập WBS (user chốt 21/08) | Lấy **bảng phiếu No. 12 bản đã có comment mui** làm tiền đề phạm vi. Mục **chưa xác nhận** vẫn ghi thành đầu mục WBS, gắn nhãn 🔸chờ xác nhận rồi để đấy — **không chặn việc lập, không chờ trả lời mới lập** |
| Nguồn chi tiết | `requirements/onboarding_guide.md` (v1.3 + các đợt vá 08-20/21) ・ `submit_folder/2026_08_21/bang_47batch_phandinh_esmart_vn.md` ・ `submit_folder/qa/qa_dokuritsu_deploy_20260821.md` ・ `memory/00_INDEX.md` mục 🎯 |

---

## 1. ĐÃ CHỐT — nền để chia khối WBS

| # | Điều đã chốt | Nguồn | Ảnh hưởng lên WBS |
|---|---|---|---|
| 1 | **Phân công (担当)**: SYP = 7-3 EMINEL-smartサーバー ・ 7-4 管理画面 ・ mobile app │ mui Lab = 7-1 firmware ・ 7-2 GW管理クラウド | QA No. 10 (完了, swan) — guide §1.6②/§6.1 | WBS chỉ phủ 3 khối SYP; ranh giới với mui = IF-02 (GW管理クラウド API) |
| 2 | **Server E-GW = hệ ĐỘC LẬP** với E-Smart đang chạy (「基本的には」 còn nguyên — không phải độc lập tuyệt đối) | QA No. 2 (完了) — guide §9.4 | Có khối WBS "dựng môi trường mới" (project/bảng/credential riêng) |
| 3 | **管理画面 = chung source + chung deploy** với E-Smart — thêm màn hình E-GW vào chính repo `syp-eminelstandard-web-admin` | QA No. 3 (完了, masao) | Khối admin KHÔNG có mục dựng môi trường riêng |
| 4 | **App**: đối tượng phát triển, SYP làm; tái cấu trúc repo theo `apps/` + `packages/` (`packages/data` trong repo, không dùng gói `kurashi_data`) | No. 1/No. 7 (完了) + bản nộp 19/08 — `2026_08_18/CLIENT_REPORT_APP_RESTRUCTURE_ja.md` | Lịch mui: implement tái cấu trúc **tuần 24–28/08**; khối app của WBS xây trên cấu trúc mới |
| 5 | 🔴 **DR phần lớn = FY26** (đảo 21/08): server DR管理 `F-ES-07,08` cơ bản FY26 (**tiền đề nội bộ: coi TOÀN BỘ là FY26**, không trừ trước 判定ロジック) ・ admin `F-AD-08` FY26 ・ app `B5` FY26 | QA No. 12, 3 inline comment masao 08-20 — guide §6.4 | Thêm hẳn một nhánh DR vào cả 3 khối; batch `ControlDrOperation` (🔶 bảng 47) thành việc 2026 |
| 6 | **見守り通知 PHẢI làm** (logic phán định nằm ở gateway — phía mui; server/app làm phần của mình) ・ **BỎ chiều gửi log app lên Xzilla** (không port `PutLogFileCommand`) | QA No. 24 — guide §4.4③ | Một đầu mục làm + một đầu mục ghi rõ "không làm" (kẻo người sau tưởng sót) |
| 7 | **Cách gắn GW với khách: `GW-ID` ↔ `TagTag ID`**, gắn lúc pairing từ app đã đăng nhập TagTag; **BỎ EMS-SP番号** | QA No. 8 (comment masao 08-19) — guide §5.2 | Khối onboarding/đăng ký GW thiết kế theo đường này |
| 8 | **6 chức năng e-smart nên dùng tiếp**: Push/FCM ・ point+PI連携 ・ đường nhận Xzilla SFTP→S3→DynamoDB ・ admin export ・ giám sát CloudWatch+SNS ・ bảng tích luỹ + pattern batch nhập liệu. Tiền đề: dùng lại ≠ 0 công | Đã báo mui 21/08 (追記 phiếu No. 2) — `qa/qa_dokuritsu_deploy_20260821.md` | Các khối tương ứng ước công theo hướng "dùng lại pattern", KHÔNG ước như viết mới — nhưng chờ câu a/b (xem tồn đọng #1) |
| 9 | **Phán định đủ 47/47 batch hệ cũ**: ✅ dùng nguyên trạng 3 ・ 🔶 sửa 2 ・ ❌ làm mới 25 ・ 🔻 bỏ 4 ・ ⭕ tự tiêu biến 3 ・ còn lại ⚠️/🚫/— | `2026_08_21/bang_47batch_phandinh_esmart_vn.md` | Đây là danh mục gốc để đẻ đầu mục batch trong WBS |
| 10 | **Truy ngược dữ liệu: 24 tháng** (tạm — giá trị SYP đề xuất, mui xác nhận câu 1/3) ・ **設計書 giao nộp: màn hình = excel, API = markdown** | QA No. 14 ・ No. 9 — guide §7.4⑦/§7.7 | Ràng buộc spec F-AD-09 + đầu mục "làm 設計書" đúng định dạng |
| 11 | **Phạm vi điều tra hệ cũ = `conciergesv` + `eminelsv`**; `hemssv` ngoài phạm vi (GW nói chuyện qua HEMS-SV/m2-cloud của mui) | QA No. 4 (完了) | Không có đầu mục nào đụng hemssv |
| 12 | **Mốc lịch khung**: 2026/9 fix toàn bộ design+spec → 〜10月末 dev xong → 〜12月末 test → 2027/1〜 field試験; 劣後 → 2027/4〜 | camp day2 dòng 148 + `22_decisions` — guide §6.3 | Trục thời gian của WBS |

## 2. TỒN ĐỌNG — ghi thành đầu mục 🔸chờ xác nhận trong WBS

| # | Còn treo | Nó chặn gì trong WBS | Trạng thái / kênh |
|---|---|---|---|
| 1 | **Câu a/b phiếu No. 2**: 6 chức năng **bê sang E-GW chạy độc lập** hay **tách package dùng chung**? | Quyết định khối lượng lớn nhất — cách ước công của 6 khối dùng-lại | Đã hỏi 21/08 (追記 body No. 2), chờ mui |
| 2 | **Tư thế firmware DR**: GW có xây năng lực lưu trạng thái không (phương án kết thúc A/B) | Thiết kế khâu kết thúc DR phía server (server có phải gửi lại lệnh khi GW mất mạng, timeout…) | 🔴 Việc số 1 nhóm user: nêu với mui/kihara. No. 25 đáp 「後回し」 = tự chờ là vô ích |
| 3 | **No. 12: 9 dòng 劣後 chưa xác nhận** + **#6** `F-AD-02` mở rộng (一部 — phần nào lùi?) + **#12** `B4` 家電操作 (2026 hay 2027?) + ranh giới 「DR実施判定ロジック」 được coi là lùi | Ranh giới 2026/2027 của từng khối — dòng nào vào WBS năm nay | User quyết 21/08: KHÔNG thúc lúc này; ghi 🔸 rồi để đấy |
| 4 | **Điều kiện phân loại lỗi 重篤/軽微** — mui chưa liệt kê được danh mục lỗi, tự nói 「結構後になる」 | Màn hình C (quản lý E-GW) + D (dashboard) — thuộc 2026 | QA No. 6; cần đầu mục "làm trước phần không phụ thuộc phân loại" (guide Phụ lục C #1) |
| 5 | **7 loại tư vấn tiết kiệm mới chưa được định nghĩa** (gom từ 19 loại — code có 19, tài liệu ghi 約15) | `F-ES-03` advice engine + màn hình G + requirement C5 | QA No. 19 trống — guide Phụ lục B.6/C #8 |
| 6 | **No. 14 câu ②③**: có quy định đòi lưu >24 tháng? ZIP quá khứ có di trú? | Chốt spec `F-AD-09` (tải dữ liệu) + thiết kế hạn lưu DB (bảng 47: `DeleteData` — "có dữ liệu mà không có cơ chế hạn lưu") | Chờ mui/北ガス — guide Phụ lục C #11b |
| 7 | **IF-01 / CLD-07**: định nghĩa vào-ra với Xzilla chưa có | Cả nhóm batch nhận Xzilla (3 con ❌) chỉ dựng khung được, chưa chốt spec | Chờ spec — guide Phụ lục C #12 khu vực CLD |
| 8 | **Đích luồng export SFTP `/EST`** của e-smart chưa xác nhận (≒ F-ES-10?) | Quyết có kế thừa luồng export này không | Chưa hỏi — việc 9 hàng đợi (00_INDEX) |
| 9 | **Mâu thuẫn điểm thưởng chưa gỡ**: bảng No. 12 ghi `A3 ポイント = 全部 劣後` ↔ No. 25 đáp エコ暖房ポイント 「対応範囲内」 (giả thuyết: hai thứ khác nhau — chưa ai xác nhận) | Khối point: cái gì 2026, cái gì 2027 | Guide Phụ lục B.2 — đừng nói gộp "điểm thưởng trong phạm vi" |
| 10 | **Nhóm 集計・計算系 19 batch chưa được SYP điều tra chi tiết** (phán định hiện là trích lại của member) | Ước công nhóm nặng nhất của WBS dựa trên phán định chưa kiểm độc lập | Việc 13 hàng đợi — nếu WBS cần số chắc thì điều tra trước nhóm này |
| 11 | **3 vấn đề chặn nền**: CLD-01 (test spec — テスト=mui, 実装=SYP) ・ CLD-02 (tài khoản dev TagTag/PI/Xzilla) ・ GW-01 (spec logic sưởi) | Điều kiện bắt đầu của nhiều khối | Guide §8.4 |

## 3. Cách dùng khi lập WBS

1. Chia khối lớn theo bảng 担当 (mục 1-#1): **server E-GW độc lập** ・ **phần E-GW trong admin chung** ・ **app** (+ khối chung: dựng môi trường, 設計書, test theo phân công テスト=mui/実装=SYP).
2. Đẻ đầu mục batch từ **bảng 47** (mục 1-#9): ❌ 25 con làm mới + 🔶 2 con sửa (nhớ `ControlDrOperation` nay là 2026) + đầu mục "không làm" cho 🚫/🔻 để khỏi bị điều tra lại.
3. Mọi mục dính tồn đọng §2 → vẫn ghi đầu mục, gắn **🔸chờ xác nhận + số dòng ở §2**, không để trống.
4. Ước công các khối dùng-lại theo 2 kịch bản nếu câu a/b (§2-#1) chưa có trả lời lúc lập: (a) bê sang / (b) package chung.
