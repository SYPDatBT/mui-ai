# SESSION 2026-08-13 — Pull `1100487` (spec app xuất hiện) ・ vá `new_2/` để nộp lại ・ quy tắc QA folder
> Đọc SAU `00_INDEX.md`. ⭐ TRẠNG THÁI MỚI NHẤT (chưa có file nào thay).

## 1. Bối cảnh & mục tiêu phiên

User mở phiên bằng câu hỏi tiến độ, sau đó ra 4 chỉ đạo dứt điểm cho các mục treo của phiên 08-12:
① fetch source mới nhất ② **vá findings vào `new_2/` để nộp lại** (thay vì chỉ áp bài học cho tập sau)
③ thư mục `new/` — user đã tự xoá, xem như không tồn tại ④ Notion do user tự đăng, AI không đụng.
Giữa phiên user dời file QA sang thư mục mới và yêu cầu ghi thành quy tắc; cuối phiên điền link Notion vào bảng tổng hợp.

## 2. ĐÃ LÀM

### 2.1 Fetch 4 repo — phát hiện local `eminel_gw_project` cũ 10 ngày
- **`eminel_gw_project`: working tree đang ở `788b438` (03/08)**, không phải `460c671` như các phiên trước ghi.
  `git reflog` chỉ có đúng 2 dòng: `clone` → `merge origin/main: Fast-forward` (=`788b438`). → **các phiên 08-06/08-12 đọc nội dung commit mới bằng `git show <commit>:<path>`, KHÔNG phải từ working tree** (kết luận của họ vẫn đúng, chỉ là ghi chép "đã pull" gây hiểu nhầm).
- Đã `git pull --ff-only` → **`1100487`**. 3 repo còn lại không đổi (`legacy_eminel_docs@ccd8f56` ・ backend@`dc39aa39` ・ web-admin@`e550326`).

### 2.2 Vá `new_2/` (6 file JP+VN, +71/−49) — bản để user upload lại
⚠️ **Danh sách chi tiết 78 findings của phiên 08-12 KHÔNG được lưu ra đĩa** (đã tìm cả `submit_folder/`, workspace, scratchpad các phiên) — chỉ còn phần tóm tắt ở `05_session…` mục 4.2. Nên đợt vá này = **toàn bộ phần có ghi nhận**, mỗi finding kiểm lại trên code trước khi sửa:

| # | Vá | Bằng chứng đã kiểm lại |
|---|---|---|
| [cao] | Xzilla §7.6: "hệ cũ không có chiều gửi" là SAI | `PutLogFileCommand.php:34, 42-43, 47, 50, 100` PUT app-log `.tsv` lên `XZILLA_RELATION_SERVER_HOST` bằng `XZILLA_SEND_SFTP_USER`; cron `00 00 * * *` (`mng-webap_cron設定_20241029.txt:120` = `31_PutLogFile.sh`). Thuộc 監視・ログ系 → ngoài 11 batch. Sửa §7.6 + dòng đối chiếu + hàng §3-4 |
| [cao] | Xzilla: thêm điểm treo §3-**5** + câu hỏi mui soạn sẵn | `I_data_download.md:200` — 4 bảng của #5–#7 nằm trong 5 種 「本表外の内部種別」; **đã kiểm file này KHÔNG đổi giữa `788b438`↔`1100487`** nên trích dẫn hợp lệ với mốc khai trong báo cáo |
| [cao] | 配信 + CSV/ZIP: kết luận "nhóm 集計・計算系 không có gì dùng lại" | Bị code bác: `template-dynamodb.yaml:1113/1145/1177` (`DeviceAccumulated`/`DailyUsage`/`MonthlyUsageHistoryTable`), ghi bằng `Put`+TTL bởi `batch-import-rinnai-monthly-usage/app.ts:18,84` ・ `-daily-usage:18,83` ・ `-sensor-data:17,173` ・ `batch-import-noritz-hourly-usage:18,68` ・ `-sensor-data:17,81`. Viết lại: khác biệt thật = e-smart **nhận giá trị đã tính sẵn** từ Rinnai/Noritz |
| [cao] | 配信: path `InterfaceCode.php` thiếu `PointInfinity/` | Path thật `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/PointInfinity/Api/InterfaceCode.php` (2 file × 1 chỗ) |
| [vừa] | `emn_all` sai tên + **sai phân loại** | Không phải bảng 速報 mà là bảng 取込: comment DB 「EMN_30分電力量出力情報取り込みデータ」 (`CreateElectricPowerAll.php:71`); `RcvHalfHourElectricPowerCommand.php:193-194, 205` xoá-nạp lại, rồi `:449-583`(fixed_div rỗng→速報) / `:591-725`(=1→確報) đều SELECT **FROM** nó. Sửa sơ đồ + bảng §8 (đếm ❌5→❌6) |
| [vừa] | grep phủ định thiếu phạm vi | `rate(` → ghi rõ *trong `template.yaml`* (8 chỗ, đã kiểm =0). **`energy\|usage`: 0 hit là SAI** — 20 file có hit → thay bằng grep đúng: `average\|_avg`=0 ・ `eco.?point\|エコ暖房`=0 toàn `src/**/*.ts` |
| [vừa] | "e-smart 4候補" chỉ kể 2 | Liệt kê đủ 4 ở cả 6 file: Push ・ point/PI ・ nền nhận Xzilla SFTP→S3→DynamoDB ・ download/export |
| [vừa] | 3 lịch tĩnh không nói làm gì | Thêm mục đích từng lịch (nhận 8 IF Xzilla / xuất 6 CSV `/EST` / lấy lỗi thiết bị Rinnai) |
| [vừa] | 7 thuật ngữ không gloss lần nào | Thêm 1 hàng 用語 (TTL・PITR・FCM・PushCore・Tip・DR・Xzilla) vào bảng ký hiệu cả 6 file |

**Kiểm chứng sau vá** (theo bài học "vá theo KHỐI" 08-12): 0 tàn dư 8 chuỗi sai ・ fence chẵn (24/46/10) ・ heading JA↔VN khớp 3/3 cặp ・ cặp Xzilla trùng khít 324 dòng / 110 dòng bảng ・ chênh 3 dòng bảng của cặp 配信 **đã có từ HEAD** (131/128), không phải do đợt vá.

### 2.3 Quy tắc QA folder (⛔#12)
User tự dời `qa_kitagas.md` (từ `requirements/`) + `qa_batch_csvzip.md` (từ `submit_folder/2026_08_12/`) vào **`submit_folder/qa/`**; từ nay file QA mới đặt ở đó, tên = mô tả nội dung hỏi + ngày (`qa_<chủ-đề>_<YYYYMMDD>.md`). Đồng bộ: `00_INDEX` ⛔#12 ・ `CLAUDE.md` (thêm hàng, **ghi rõ thư mục này SỬA ĐƯỢC** — khác `submit_folder/<ngày>/`) ・ `README.md` ・ `self_study_plan.md:126` ・ `create-investigation-report/TEMPLATE.md` §10 ・ cặp CSV/ZIP của `new_2/` ・ memory toàn cục (`qa-files-location.md`).

### 2.4 Bảng tổng hợp
`submit_folder/2026_08_12/summary_batch_migration_ja.md`: điền 4 link Notion cho nhóm CSV/ZIP (định dạng `<td><a href="…">TênCommand</a></td>` khớp 2 dòng mẫu). Kiểm: tên cột 3 = slug URL = text link ở cả 6 dòng; bảng nguyên vẹn 47 hàng × 9 ô, `<td>` 423/423. Sửa 1 câu bị lặp nguyên vế ở ô 補足 dòng `…ConSensorHourlyValues` (đã báo user).

### 2.5 Memory `new/`
Xoá mọi dấu vết thư mục `new/` khỏi `00_INDEX` + `05_session…` mục 5.1 (ngoại lệ có chủ ý với quy tắc "không sửa file session cũ" — user chỉ đạo trực tiếp) và trỏ baseline mục 4 của `3-step-review` về `new_2/` = bản chuẩn duy nhất.

## 3. QUYẾT ĐỊNH & PHÁT HIỆN

1. **Finding của review agent có thể SAI — đã bác bỏ 1 cái trước khi vá.** Review 08-12 báo *"shell flock không có căn cứ, grep `flock` = 0"*. Thực tế `flock` có thật, nằm trong `.sh` **bên trong `eminel-mng-webap.20240909.tgz`**; giải nén ra grep thấy ngay (`10_*.sh:5-6`…). Reviewer grep repo mà không mở file nén → nếu vá theo thì biến một khẳng định ĐÚNG thành SAI. → thành **⛔#13**.
2. **Ghi chép "đã pull X" của phiên trước không đủ tin.** Working tree đứng ở `788b438` suốt 10 ngày trong khi memory ghi `460c671`. → thành **⛔#14**.
3. **Guide v1.2 lệch mốc chỉ 1 ngày sau khi chốt**: `1100487` mở thư mục `docs/eminel/4_spec/app/` — 機能仕様 của app bắt đầu được viết. §7.3 (bảng 23 section / ステータス) và các mục trích A0x/B0x/E0x phải rà lại.
4. Bảng tổng hợp 47 batch mới có **6 dòng** kết luận (4 CSV/ZIP của SYP + 2 集計 của thành viên khác); **7 dòng 配信・通知系 + Xzilla đã điều tra xong từ 08-06 nhưng chưa điền** — dữ liệu có sẵn trong `new_2/`, chỉ cần chuyển vào bảng.
5. Notion: user tự đăng, AI không thao tác (phiên này cũng không có Notion MCP — chỉ Google Drive).

## 4. Thay đổi phía repo dự án

`eminel_gw_project` `788b438` → **`1100487`** (9 commit; 2 commit mới so với mốc guide v1.2 `460c671`, đều 12/08 của hanamiju):

| Commit | Nội dung |
|---|---|
| `57cd7be` 要件fix | sửa requirement app |
| `1100487` 機能仕様着手 | **thư mục mới `docs/eminel/4_spec/app/`**: `README.md` (195 dòng) ・ `c02_グラフ.md` (133) ・ `c03_レポート.md` (228) ・ `Z_コントロールタブ構成検討.md` (95) + skill `.claude/skills/draft-app-spec/` |

Tổng diff `460c671..1100487`: 17 file, +955/−286. Requirement app bị sửa: A01・A02(−71)・A03・A04・B01・B04・**B06**・**E01(−140)**・E04・README. **Chưa đọc nội dung** các file này.

## 5. VIỆC DỞ DANG / NGÀY MAI LÀM GÌ

1. **User tự làm**: upload lại `new_2/` đã vá ・ đăng Notion.
2. **Rà guide v1.2 theo `1100487`** — ưu tiên: §7.3 bảng 23 section (E01/B06/A0x vừa đổi) + đọc `4_spec/app/` mới (đây là spec cho hạng mục 4 của kế hoạch tự học).
3. **Điền 7 dòng 配信・通知系 (#1–#4) + Xzilla (#5–#7)** vào `summary_batch_migration_ja.md` — kết luận đã có trong `new_2/`; cần quyết: có tách thành file `legacy-batch_<Command>_{ja,vi}.md` theo format mới không.
4. **Điều tra nhóm 集計・計算系** (17/19 dòng còn lại của nhóm) — nhớ: **e-smart CÓ 3 bảng history** (§2.2), giả định cũ đã bị bác.
5. **`self_study_plan.md` dòng 54 vẫn ghi "集計・計算系 — e-smart không có gì dùng lại"** → phải sửa theo phát hiện trên (CHƯA làm).
6. Findings [thấp]/[vừa] không có ghi nhận (phần còn lại trong 78) — **mất**; user quyết có chạy lại một lượt review để dựng lại danh sách không (nếu có: cho phép dùng subagent hay chạy tuần tự).
7. Việc treo cũ không đổi: trả lời vế ただし QA 独立デプロイ ・ chốt kihara Q5 (DR) → gửi `qa_kitagas.md` ・ hỏi đích `/EST` (nay có thêm căn cứ `PutLogFileCommand`) ・ theo dõi 5 QA 回答中 ・ gửi 5 câu `qa_batch_csvzip.md` ・ CLD-01/02/07, spec [G]/[I].

## 6. CHƯA KIỂM

- Nội dung `4_spec/app/` mới + 11 file requirement app vừa đổi — mới chỉ xem `--stat`.
- 3 trang QA Notion (không có Notion MCP phiên này; vẫn theo ảnh 08-04).
- Đích SFTP `/EST` — vẫn chỉ là căn cứ gián tiếp (secret ngoài repo).
- Kết quả buổi làm việc chiều 05/08 với mui (treo từ session 03, vẫn chưa có ghi nhận).
- Khoảng trống 08-07 → 08-11.
