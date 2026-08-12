# SESSION 2026-08-12 — Guide v1.2 theo `460c671` ・ review 6 agent ・ bộ 4 batch CSV/ZIP format mới (8 file)
> Đọc SAU `00_INDEX.md`. ⭐ TRẠNG THÁI MỚI NHẤT.
> Phiên có **2 đợt**: đợt 1 = guide v1.2 + review `new_2/` (mục 1–7 dưới); đợt 2 = bộ báo cáo 4 batch CSV/ZIP theo **format mới** (mục 8).

## 1. Bối cảnh

- Khoảng trống 08-07 → 08-11 **không có ghi nhận nào** trong workspace (file cuối bị đụng: 08-06 21:44). 3 tập báo cáo batch: user xác nhận **đã nộp cả 3**.
- Việc chọn cho ngày: ① cập nhật guide theo commit mới ② review độc lập `new_2/` ③ bắt đầu kế hoạch tự học.

## 2. Repo

- `eminel_gw_project`: `fbc0af0` → **`460c671`** (commit 08-06 18:10 của hanamiju, chỉ sửa `app/E02_app_log.md` + `E03_help.md`: 状態 ドラフト済（レビュー待ち）→ レビュー中, cắt 検討事項・関連項目). Không tài liệu nào của workspace trích E02/E03.
- 3 repo còn lại không đổi: `ccd8f56` / `dc39aa39` / `e550326`.
- **Mốc git ≠ mốc `経緯`**: B03 đổi điều kiện 基本制御 ở commit `f2a3dab` (**08-05**) nhưng dòng `経緯` của B03 vẫn ghi 2026-07-23. Khi cần mốc chắc chắn → `git log`, không tin `経緯`.
- Ba đợt sửa tháng 8 (15 file): 08-03 `9dc5e34` (chỉ B2) ・ 08-05 5 commit (B01/B02/B03/B06/C05/D01–D04/README/B05/A01/A02) ・ 08-06 `460c671` (E02/E03).

## 3. `onboarding_guide.md` → v1.2 (đối chiếu `460c671`)

Thay đổi thực chất (không chỉ số dòng):

| Vùng | Nội dung |
|---|---|
| §5.5 | **設定値運転 bị gỡ khỏi requirement** → trục mới 「室温制御の有無」 + khái niệm mới **温度レベル** (không có trong 用語集, chỉ 3 lần trong B02, chính người viết đang hỏi ngược 北ガス ở dòng 239). Thêm: 3 câu "mô hình hiện hành" ở đầu mục, bảng đối chiếu cũ↔mới, bảng "3 nhóm quy tắc đã bị xoá" + câu chặn *bị xoá ≠ nay làm được* |
| §5.6 | 基本制御 đổi điều kiện 在宅モード中 → **冷房スケジュール中** (08-05). ⚠️ 「実施検討中」 của 外気温補正 **chỉ bỏ ở ô 用語集**, vẫn còn ở cây (B03:28) và bảng 備考 (B03:104) → **vẫn đang cân nhắc** |
| §7.3 | Bảng index đổi mô hình (bỏ 状態 → 内容・スコープ/ステータス/劣後 lấy từ slide đối khách). Bảng 23 section viết lại; **ステータス có 6 giá trị** (B2 = レビュー中); thêm mục **B6 マイホーム発電制御**; bảng 3 đợt sửa tháng 8 |
| Phụ lục B.3 | D04 đã xoá khối 要確認事項 (CLD-05) — dấu vết chỉ còn ở `経緯` dòng 8 và bảng 参照 dòng 20; CLD-05 vẫn 🔴 trong open_issues |
| Phụ lục B.4 | Viết lại: **hai thang trạng thái song song** (状態 nội bộ ↔ ステータス đối khách), **cùng dùng chữ 「レビュー中」 nhưng khác nghĩa** — không phải mâu thuẫn |
| §0.3 | Thêm bảng **hai mốc kiểm**: repo = `460c671` (kiểm 08-12) ・ QA Notion = lần đọc 08-04, **chưa kiểm lại** |

Đồng bộ ngoài guide: `requirements/README.md` (mốc + ngày) ・ `CLAUDE.md` (v1.2) ・ `00_INDEX.md` ⛔#6 (bỏ commit hardcode, trỏ bảng meta guide).

## 4. Review 6 agent (⛔#5) — 142 findings, 15 [cao]

### 4.1 Guide (3 vòng, 44 findings / 6+5+4 [cao])
Lỗi do chính đợt sửa hôm nay, **đã vá hết**: bảng gloss ghi "Năm giá trị" trong khi index có **sáu** (thiếu đúng 「レビュー中」 của B2 — lan sang §9.2/§9.5) ・ "gặp 設定値運転 ở hai chỗ" trong khi repo chỉ còn **1 hit** (B02:59) ・ §5.6 không hoà giải với khối trích v1.2 vẫn ghi 在宅モード中 ・ con trỏ chết 「xem 要確認事項 ở dưới」 ・ 温度レベル bị nhét vào bảng trích 用語集 (không thuộc bảng đó) ・ gán sai ngày cho đợt sửa B3 ・ tàn dư `788b438`/`2026-08-03` ở 2 chỗ ・ "B6 ngắn nhất" (sai — C04 94 dòng < B06 97) ・ **7 chỗ vi phạm ⛔#9** (「Cập nhật 2026-08-03」×3, 「Bổ sung…」, heading 「Cập nhật từ QA…」, 「mới thêm…」, và câu tự nhắc "bản guide trước").
Sau vá: fence 68 chẵn ・ 94 anchor / 0 hỏng ・ 0 tàn dư ・ 4.232 dòng.

### 4.2 `new_2/` (3 cặp JP+VN, 78 findings / 4 [cao]) — **CHƯA VÁ, chờ user quyết**
- **[cao] Xzilla V1-1 — "hệ cũ không có chiều gửi" là SAI**: `conciergesv-develop/src/Command/PutLogFileCommand.php:42-44, 100` PUT file `.tsv` app-log lên **cùng SFTP server Xzilla** (`XZILLA_RELATION_SERVER_HOST` + `XZILLA_SEND_SFTP_USER`), cron `00 00 * * *` (`mng-webap_cron設定_20241029.txt:120`). Thuộc nhóm 監視・ログ系 nên ngoài 11 batch → **căn cứ gián tiếp mạnh cho giả thuyết đích `/EST` = Xzilla**.
- **[cao] Xzilla V1-2**: `4_spec/admin/I_data_download.md:200` liệt kê `ipf_ems_pls_cntr_payers`/`ipf_cntct_cancellations`/`emn_all_electric_powers`/`emn_fast_electric_powers` trong 5 「本表外の内部種別」 của màn tải dữ liệu → **4 bảng của 3 batch này đang là nguồn download nội bộ của 管理画面**, 「E-GWでダウンロード対象とするデータ種別」 còn 要FIX → phải thêm QA.
- **[cao] 配信 V1-2 — kết luận về nhóm 集計・計算系 bị code bác bỏ**: e-smart CÓ bảng tích luỹ `TABLE_DEVICE_{MONTHLY,DAILY,ACCUMULATED}_*_HISTORY` (`template-dynamodb.yaml:105-111`, ghi bởi `batch-import-rinnai-monthly-usage` ・ `batch-import-rinnai-sensor-data` ・ `batch-import-noritz-sensor-data`); chỉ **monthly report trang chủ** là proxy TagTag. Thế hệ 1 có chữ rào 「見込み」, bản rút gọn cắt mất → phỏng đoán thành khẳng định (⛔#3).
- **[cao] 配信 V1-1**: path `InterfaceCode.php` ở §6.1 thiếu `PointInfinity/` (§11 của chính file đã đúng) — đợt chuẩn hoá 08-06 chỉ sửa một chỗ.
- Nhóm [vừa] đáng vá: "shell flock" không có căn cứ (grep `flock` = 0; nguồn nói cơ chế chống trùng nằm ở **PHP** — `cron設定概要.txt:3, 36`) ・ grep phủ định mất điều kiện phạm vi (`energy|usage`, `rate(`) ・ `emn_all` sai tên + sai phân loại ・ "e-smart 4候補" chỉ liệt kê 2 ・ mất mô tả 3 lịch tĩnh làm gì ・ TTL/PITR/DR/FCM/Tip/PushCore/Xzilla không gloss lần nào.
- **Không finding nào lật phán định**: cả 11 batch giữ nguyên kết luận.

## 5. QUYẾT ĐỊNH & PHÁT HIỆN

1. **Thư mục `submit_folder/2026_08_06/new/` (thế hệ 2 v4) KHÔNG còn trên đĩa** — chỉ còn thế hệ 1 (`2026_08_06/*.md`) và `new_2/`. Chưa rõ cố ý hay nhầm; **baseline mục 4 của skill `3-step-review` đang trỏ vào `new/`** → phải sửa khi user xác nhận.
2. **Dự đoán "集計・計算系 = e-smart không có gì dùng lại" phải xem lại trước khi điều tra** (mục 0b của 00_INDEX và `self_study_plan.md` đang ghi theo dự đoán cũ).
3. Bài học quy trình: guide sửa "từ giữa ra" — thân bài kỹ nhưng **vỏ (bảng meta, bảng chú giải, phụ lục) không được rà lại**; 5/6 finding [cao] của vòng 2 thuộc loại này.
4. Bài học ⛔#8/⛔#2: mọi câu "grep X: 0 hit" phải ghi **phạm vi grep**; bỏ phạm vi là nói quá nguồn (3 lần mắc trong 1 ngày, ở 2 tài liệu khác nhau).

## 6. VIỆC TIẾP THEO

1. **Quyết định về `new_2/`**: vá 4 [cao] + nhóm [vừa] vào bản đã nộp, hay chỉ áp bài học cho tập sau? (đã có sẵn câu chữ thay thế cho từng finding)
2. Xác nhận số phận thư mục `new/` → sửa baseline `3-step-review` mục 4.
3. **Điều tra nhóm 集計・計算系** — trước khi bắt đầu: kiểm lại 3 bảng `TABLE_DEVICE_*_HISTORY` để biết thực sự dùng lại được gì.
4. Cập nhật `self_study_plan.md` + 00_INDEX mục 0b theo phát hiện #2.
5. Kiểm 3 trang QA Notion (vẫn theo ảnh 08-04) — guide đã khai rõ "chưa kiểm lại" ở §0.3.
6. Việc treo cũ: trả lời vế ただし QA 独立デプロイ ・ chốt kihara Q5 (DR) → gửi `qa_kitagas.md` ・ hỏi đích `/EST` (**nay có căn cứ mới từ `PutLogFileCommand`**) ・ theo dõi CLD-01/02/07, spec [G]/[I].
7. Tự học: hạng mục 1 mới xong bước 1 (§8-3 F-ES của v1.2) — còn 業務フロー ・ feature_list ・ 22_decisions/20_open_issues ・ eminel-smart ・ code backend.

## 8. ĐỢT 2 — Bộ 4 batch CSV/ZIP theo FORMAT MỚI (`submit_folder/2026_08_12/`, 8 file)

### 8.1 Format mới — user chỉ đạo, khác TEMPLATE v4
Mẫu do thành viên khác upload Notion: `legacy-batch_CalcTenMinutesSensor_ja.md`. Đặc điểm: **1 batch = 1 file**, **chỉ điều tra hệ CŨ**, mọi khẳng định kèm đường dẫn đầy đủ từ tên repo. Bố cục: 概要 → Part 1 概要 (bảng 役割/Input/Output/処理概要) → Part 2 詳細 (2.1 スケジュール ・ 2.2 データ取得 ・ 2.3 ロジック ・ 2.4 出力先 ・ 2.5 確認).
**Bỏ hẳn** so với v4: sơ đồ luồng hệ mới, cách làm từng bước, kiểm thử, bảng QA, đối chiếu cũ↔mới. Phán định hệ mới **không** nằm trong file mà ở `requirements/summary_batch_migration_ja.md`.
User chốt: ① tên file `legacy-batch_<Command bỏ hậu tố>_{ja,vi}.md` ② **GIỮ full path repo** trong trích dẫn (dù ⛔#4 — vì mui dùng chính repo đó) ③ phán định giữ trong bảng tổng hợp + thêm dòng ghi nguồn.

### 8.2 Kết quả điều tra 4 batch (đã kiểm code, 91/91 trích dẫn đúng ở review lượt 1)
| Batch | Bảng | Lịch | Đặc điểm |
|---|---|---|---|
| `…ConDeviceStatuses` | `t_202` | hằng ngày 05:15 | 264 cột (128 EPC node + 128 EPC thiết bị); ZIP **chỉ thứ Hai** |
| `…ConSensorHourlyValues` | `s_102` | hằng ngày 05:15 | 36 cột, **24 giờ ngang**; ZIP chỉ thứ Hai |
| `…ConSensorDailyValues` | `s_103` | **chỉ mùng 1** | 42 cột, **31 ngày ngang**; ZIP mỗi lần chạy |
| `…ConSensorDailyAveValues` | `s_113` | **chỉ mùng 1** | 40 cột, **1 file duy nhất** (bảng trung bình theo nhóm, KHÔNG có cột EMS-SP) |

**5 phát hiện đáng giữ:**
1. **Tên shell `12_CreateCsvAndDeleteData_day2to31.sh` đánh lừa**: cron dòng `:40` để day-of-month = **`*`** → chạy MỌI ngày. Nên **mùng 1 hai batch hằng ngày chạy 2 lần** (cả `_day1.sh` lẫn `_day2to31.sh` nổ 05:15). `flock` khoá `exec {my_fd}< "$0"` = **chính file script** nên KHÔNG chặn được. 🔸 khả năng ghi lặp CSV (chưa kiểm runtime) → nên hỏi mui.
2. **Tên đọc ngược trực giác**: `s_103` (batch "Daily") = 月毎センサ情報, bảng THEO THÁNG; `s_102` (batch "Hourly") = 日毎センサ情報, bảng THEO NGÀY. Tên batch chỉ *đơn vị giá trị*, tên model chỉ *khoảng thời gian 1 bản ghi*.
3. **`c001` khác nghĩa giữa các bảng**: ở `s_113` là 機器種別, ở 3 bảng kia là EMS-SP → ánh xạ xuyên bảng không được suy theo số hiệu cột.
4. **Hai kiểu quan hệ export↔DROP**: `t_202` đệm 1 ngày (D+8 / D+9) ・ `s_102` đệm 7 ngày (D+8 / D+15) ・ `s_103`/`s_113` **đệm 0** (export tháng trước nữa rồi DROP đúng tháng đó, cùng một lần chạy). Chỉ nhờ `set -eu` mà không xảy ra "xoá trước khi kịp thành file" — chủ ý này ghi thẳng ở `cron設定概要.txt:29-32` 補足1.
5. **4 batch ↔ 4 mục download của màn quản trị cũ khớp 1-1**, hai bên trỏ **cùng đường dẫn** `/var/data/...`; `createPreviousDataZip()` (`DownloadController.php:236`) chỉ **phát lại file batch đã tạo**, không dựng lại từ DB → đây là căn cứ nghiệp vụ cho phán định "bỏ batch".
6. **`c008` không có code nào đọc/ghi**: `C_NEED_ELE_COMPLETE_FLAG` chỉ 2 hit khai báo → ngữ nghĩa giá trị **chưa kiểm chứng được**, phải hỏi mui. Ngữ nghĩa 1→2 chỉ đúng cho **`c009`** (`C_NEED_AGG_COMPLETE_FLAG`, chuyển ở `CalcMonthlyAccumulatedValueCommand.php:220`→`:213`).

**Phán định (điền vào summary, 4 dòng `CSV/ZIPエクスポート系`)**: cả 4 = **`バッチとしては不要`**, chức năng hệ mới = **F-AD-09 データダウンロード**. Căn cứ: e-smart không tạo file định kỳ mà `api-download` → `batch-download` (invoke async `InvocationType: 'Event'`) → ZIP → S3 → presigned URL; lưu trữ do DynamoDB TTL + PITR. Cột `調査結果詳細リンク` để trống (user tự điền Notion).

### 8.3 Review 2 lượt × 3 vòng = 107 findings — BÀI HỌC QUY TRÌNH QUAN TRỌNG
- Lượt 1: 57 findings (7+13+21+16 tuỳ vòng). Vá xong → lượt 2: **50 findings, 14 [cao]**.
- **Nguyên nhân gốc của lượt 2: tôi vá THEO FILE.** Sửa xong file này sang file khác → mọi khối mới chỉ áp vào 2 file "ngày", 4 file "tháng" bị bỏ lại thế hệ trước. Phân bố findings: `DailyValues` 12/21, `DailyAveValues` 9/21, `DeviceStatuses` 5/21. Sinh ra 4 thứ tự mở đầu khác nhau, 2 quy ước 🔸, BOM lúc suy đoán lúc khẳng định, và **3 lỗi sai sự thật mới** (c008 nhận bằng chứng của c009 ・ 2 file tháng vẫn nói "qua thư viện dùng chung" ・ thiếu `sudo -u apache`).
- **Cách làm đúng (đã áp dụng ở đợt vá cuối): vá THEO KHỐI.** Chọn 1 file làm bản chuẩn cho mỗi khối → **viết lại toàn bộ 8 file theo một khuôn** → chứng minh đồng nhất bằng `grep -c` từng khối + `diff` tập trích dẫn. Kết quả kiểm cuối: 10/10 khối chuẩn có mặt đúng số lần ở cả 8 file ・ fence chẵn ・ JA↔VI trùng số heading (9/9) và số hàng bảng ・ **tập trích dẫn `file:dòng` khớp 100%** ・ 0 tàn dư ・ JA sạch đồ nội bộ ・ bảng summary 47 hàng 0 lỗi HTML.
- ⚠️ Skill `3-step-review` giới hạn **2 lượt sửa-rồi-review**; đợt vá cuối này là lượt 2 → **hết quota, không review lại nữa** (user chốt: tự diff thay vì chạy agent).

## 7. CHƯA KIỂM

- Kết quả buổi làm việc chiều 05/08 với mui (session 03 để lại, vẫn chưa có ghi nhận).
- 3 trang QA Notion: session này **không có Notion MCP** (chỉ Google Drive) → chưa mở lại được.
- Đích SFTP `/EST` (secret ngoài repo) — có căn cứ gián tiếp mới nhưng chưa xác nhận.
- 6 ngày 08-07 → 08-11: user đã làm gì, không có dữ liệu.
