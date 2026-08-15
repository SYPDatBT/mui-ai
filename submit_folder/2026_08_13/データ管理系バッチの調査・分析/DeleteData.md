# DeleteDataCommand（データ削除）

## Tóm tắt

`DeleteDataCommand` là batch cron chạy hàng ngày (05:15, qua wrapper shell script cùng bước export CSV
— `12_CreateCsvAndDeleteData_day1.sh`/`_day2to31.sh`) trên server `conciergesv`: dọn dữ liệu cũ theo 2
cơ chế khác nhau — (1) **DROP partition con** đã hết hạn của ĐÚNG 10 bảng PostgreSQL partitioned mà
`CreateTablePartitionCommand` tạo trước (batch này là cặp đôi "dọn sau" — xem `CreateTablePartition.md`),
và (2) **DELETE hàng loạt theo điều kiện thời gian** trên 3 bảng KHÔNG partition (lịch sử điều khiển
thiết bị giữ 13 tháng, lịch sử phân khúc nhóm khách hàng giữ 24 tháng, điểm tiết kiệm năng lượng giữ 2
năm tài chính). Ở repo mới `syp-eminelstandard-backend`, phần (1) đã có kết luận ở `CreateTablePartition.md`
(DynamoDB TTL thay thế toàn bộ, không cần batch) — phần (2) **không có cơ chế tương đương cho cả 3
bảng**: 2 khái niệm (lịch sử điều khiển thiết bị, lịch sử phân khúc nhóm) không tồn tại dữ liệu tương
ứng để cần xóa; khái niệm còn lại (điểm tiết kiệm năng lượng) có bảng lưu trữ gần giống
(`PointBadgeStatsTable`) nhưng **không có TTL và không có batch xóa nào** — lịch sử điểm/badge ở hệ
thống mới đang được giữ vô thời hạn, khác hẳn chính sách giữ 2 năm tài chính của bản cũ.

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `DeleteDataCommand` (extends `Command` — **không** extends `BaseCommand`, khác với batch cặp đôi `CreateTablePartitionCommand`, xem A.2.4) · Tên lệnh gọi: `delete_data` *(suy đoán theo quy ước CakePHP 4)* · Script cron: `12_CreateCsvAndDeleteData_day1.sh` (ngày 1 đầu tháng) / `12_CreateCsvAndDeleteData_day2to31.sh` (các ngày còn lại) · Tên tiếng Nhật trong cron: "12.DBデータ削除". |
| **Vai trò** | Bảo trì hạ tầng DB + tuân thủ chính sách giữ dữ liệu (retention policy) — xóa dữ liệu cũ hơn ngưỡng cho phép trên 10 bảng partitioned + 3 bảng thường. |
| **Input** | Không đọc dữ liệu để tính toán — chỉ dùng tham số dòng lệnh `--datetime` (mặc định `now`) làm mốc thời gian tham chiếu để tính "cũ hơn bao lâu". |
| **Output** | `DROP TABLE` 10 bảng partition con (nếu tồn tại và đã tới hạn); `DELETE` hàng loạt trên 3 bảng thường (nếu có bản ghi tới hạn). Không ghi dữ liệu mới. |
| **Khái quát xử lý** | 1. Từ `--datetime`, chuẩn hóa 3 mốc mốc thời gian: đầu-ngày, đầu-tháng, đầu-năm (giờ:phút:giây = 0).<br>2. Xóa 4 partition con cấp NGÀY đã cũ (t_202, s_101, s_102, s_112).<br>3. Xóa 3 partition con cấp THÁNG đã cũ (s_103, s_113, s_105) + 2 bảng thường xóa theo tháng (`ConDeviceControls`, `ConUserGroupHistories`).<br>4. Xóa 3 partition con cấp NĂM đã cũ (s_104, s_114, s_121).<br>5. Xóa `ConEcoPoints` theo năm TÀI CHÍNH (không phải năm dương lịch).<br>6. Log 1 dòng `notice` duy nhất khi xong — KHÔNG log riêng từng bước, KHÔNG try/catch bước nào (xem A.2.4). |

## A.2 Chi tiết

### A.2.1 Chuẩn hóa mốc thời gian & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `15 5 * * *` (ngày 2-31) và `15 5 1 * *` (riêng ngày 1) — cùng chạy 05:15, tách 2 script vì lý do chưa đọc được (nội dung `.sh` không có trong repo tài liệu) — *suy đoán*: ngày 1 có thêm bước xuất CSV tổng kết tháng trước, nhưng KHÔNG xác nhận được trực tiếp | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:39-41` |
| Tham số `--datetime` | Mặc định `'now'`. Không có validate format riêng — dùng trực tiếp `FrozenTime::parse()`. | `DeleteDataCommand.php:23-29,35` |
| 3 mốc chuẩn hóa | `dateTimeForDay` = ngày đã cho, giờ 00:00:00. `dateTimeForMonth` = ngày 01 của tháng đã cho, 00:00:00. `dateTimeForYear` = 01/01 của năm đã cho, 00:00:00. | `:37-44` |

**Suy ra script cron `CreateCsvAndDeleteData` gọi CHUNG với các Command xuất CSV** *(suy đoán, dựa vào
tên script + xác nhận gián tiếp)*: không có cron entry riêng nào cho các Command `CreateCsvAndZip*` ở
CẢ 2 file cron (`webap_cron設定_*.txt`, `mng-webap_cron設定_*.txt` — đã grep, 0 kết quả) — nghĩa là các
Command đó chỉ có thể được gọi từ trong chính wrapper `12_CreateCsvAndDeleteData_*.sh` này (không đọc
được nội dung `.sh` để xác nhận trực tiếp thứ tự gọi). Khớp với mapping đã xác nhận ở `README.md:159`:
mục docs "08_データ削除と過去データCSV作成" ↔ CHÍNH XÁC 2 nhóm Command này (`DeleteDataCommand` +
`CreateCsvAndZip*Command`).

### A.2.2 DROP partition con đã cũ — 10 bảng, đối chứng trực tiếp với `CreateTablePartitionCommand`

Cùng 10 bảng, cùng cơ chế `CREATE TABLE ... PARTITION OF` mà `CreateTablePartitionCommand` tạo trước
(xem `CreateTablePartition.md`) — batch này chỉ đổi chiều: tính tên partition con ở 1 mốc quá khứ (theo
số ngày/tháng/năm cần giữ), kiểm tra `listTables()` có bảng đó không, có thì `DROP TABLE`.

| Hàm | Bảng cha | Giữ lại (tham số) | Mốc bị xóa (tính từ mốc chuẩn hóa) | Số kỳ thực tế còn giữ sau khi xóa |
|---|---|---|---|---|
| `dropDailyTable('t_202',...,8)` | 機器状態情報 | `keepDays=8` | `dateTimeForDay − (8+1)` ngày | **9 ngày** (lệch +1 so với tên tham số) |
| `dropDailyTable('s_101',...,8)` | 差分センサ情報 | `keepDays=8` | `− 9` ngày | **9 ngày** |
| `dropDailyTable('s_102',...,14)` | 日毎センサ情報(giờ) | `keepDays=14` | `− 15` ngày | **15 ngày** |
| `dropDailyTable('s_112',...,8)` | 日毎平均センサ情報(giờ) | `keepDays=8` | `− 9` ngày | **9 ngày** |
| `dropMonthlyTable('s_103',...,2)` | 月毎センサ情報(ngày) | `keepMonths=2` | `− 2` tháng (KHÔNG +1) | **2 tháng** (đúng bằng tham số) |
| `dropMonthlyTable('s_113',...,2)` | 月毎平均センサ情報(ngày) | `keepMonths=2` | `− 2` tháng | **2 tháng** |
| `dropMonthlyTable('s_105',...,14)` | 週間省エネレポート情報 | `keepMonths=14` | `− 14` tháng | **14 tháng** |
| `dropAnnuallyTable('s_104',...,3)` | 年毎センサ情報(tháng) | `keepYears=3` | `− 3` năm (KHÔNG +1) | **3 năm** (đúng bằng tham số) |
| `dropAnnuallyTable('s_114',...,3)` | 年毎平均センサ情報(tháng) | `keepYears=3` | `− 3` năm | **3 năm** |
| `dropAnnuallyTable('s_121',...,3)` | ランキング情報 | `keepYears=3` | `− 3` năm | **3 năm** |

Nguồn: `DeleteDataCommand.php:47-62,82-93,107-118,178-189`.

**⚠️ Điểm bất thường của hệ cũ — lệch +1 chỉ ở cấp NGÀY, không nhất quán giữa 3 hàm `drop*Table`:**

- `dropDailyTable()` tính mốc xóa bằng `subDays($keepDays + 1)` (`:85`) — CỘNG THÊM 1 trước khi trừ.
- `dropMonthlyTable()` tính mốc xóa bằng `subMonths($keepMonths)` (`:110`) — KHÔNG cộng thêm.
- `dropAnnuallyTable()` tính mốc xóa bằng `subYears($keepYears)` (`:181`) — KHÔNG cộng thêm.
- Hệ quả: tham số `keepDays=8` thực chất giữ **9 ngày** dữ liệu, nhưng `keepMonths=2`/`keepYears=3` giữ
  ĐÚNG **2 tháng**/**3 năm** như tên gọi — cùng 1 họ hàm "giữ lại N kỳ" nhưng công thức lệch nhau 1 đơn
  vị giữa cấp ngày và cấp tháng/năm. Không rõ đây là chủ ý (bù 1 ngày do giờ chạy 05:15 chưa hết ngày đó)
  hay sai sót copy code giữa 3 hàm — không tìm thấy comment giải thích trong code, và tài liệu spec liên
  quan (`データの保存期間_20240618_朴.xlsx`, `削除処理仕様書_朴_20240819.xlsx`) là file binary chưa đọc
  được nội dung. Ai port batch này cần hỏi lại nghiệp vụ số kỳ giữ THẬT được yêu cầu là bao nhiêu, không
  nên suy ra thẳng từ tên tham số `keepX`.

### A.2.3 DELETE hàng loạt theo điều kiện thời gian — 3 bảng thường (không partition)

| Hàm | Bảng | Ý nghĩa | Điều kiện xóa | Nguồn |
|---|---|---|---|---|
| `deleteConDeviceControls` | `ConDeviceControls` | デバイス制御履歴 — lịch sử lệnh điều khiển thiết bị | `created < (đầu tháng hiện tại − 13 tháng)` | `:126-141`, cột `C_CREATED='c004'` (`Entity/ConDeviceControl.php:30`) |
| `deleteConUserGroupHistories` | `ConUserGroupHistories` (bảng `s_151`) | グループ履歴 — lịch sử phân khúc nhóm khách hàng theo tháng (xem `CreateGroupSummary.md`) | `month < (đầu tháng hiện tại − 24 tháng)` | `:149-164`, cột `C_MONTH='c002'` |
| `deleteConEcoPoints` | `ConEcoPoints` | 省エネポイント — điểm tiết kiệm năng lượng | `year <= (năm tài chính hiện tại − ECO_POINTS_SAVE_TIME)` | `:201-224`, hằng số `ECO_POINTS_SAVE_TIME=2` (`const.php:723`) |

- 2 hàm đầu: gọi `exists([điều kiện])` trước, chỉ `deleteAll([điều kiện])` nếu có ít nhất 1 bản ghi khớp
  — 2 lượt query cho mỗi lần xóa (kiểm tra + xóa), không phải tối ưu nhất nhưng an toàn (không xóa khi
  không có gì, tránh lock/log thừa).
- `deleteConEcoPoints` dùng **năm tài chính Nhật (bắt đầu tháng 4)**, không phải năm dương lịch: nếu
  tháng hiện tại < 4 (tháng 1-3), năm tài chính = năm dương lịch − 1 (`:207-211`). Ví dụ chạy tay: hôm
  nay là 2026-02-15 → năm tài chính hiện tại = 2025 (vì tháng 2 < 4) → `deleteTargetYear = 2025 − 2 =
  2023` → xóa toàn bộ `ConEcoPoints` có `year <= 2023`, giữ lại năm tài chính 2024 và 2025.
- Toán tử xóa `<=` (không phải `<`) ở `deleteConEcoPoints` — khác 2 hàm trước dùng `<` — nghĩa là năm
  ĐÚNG BẰNG `deleteTargetYear` cũng bị xóa, không được giữ lại; 2 hàm `ConDeviceControls`/
  `ConUserGroupHistories` thì mốc đúng bằng ngưỡng vẫn được GIỮ (chỉ xóa nếu nhỏ hơn hẳn).

### A.2.4 Điểm đặc biệt / Rủi ro

- **Không có try/catch ở bất kỳ bước xóa nào** (khác hẳn `CreateTablePartitionCommand` — mỗi `CREATE
  TABLE` ở batch tạo được cô lập bằng try/catch riêng, lỗi 1 bảng không ảnh hưởng bảng khác). Ở batch
  xóa này, TOÀN BỘ 11 bước gọi liên tiếp trong `execute()` (`:47-65`) không có bất kỳ xử lý lỗi nào — 1
  lỗi ở bước đầu (ví dụ `DROP TABLE` bị chặn do có ràng buộc phụ thuộc) sẽ ném exception ra ngoài, dừng
  TOÀN BỘ các bước xóa còn lại trong cùng lượt chạy (kể cả 3 bảng thường hoàn toàn không liên quan tới
  bảng bị lỗi ở bước đầu). Không có log `alert` nào báo lỗi cụ thể bước nào thất bại — chỉ có 1 dòng
  `notice` báo thành công ở cuối, nên khi lỗi xảy ra, dòng log thành công đó đơn giản là KHÔNG xuất hiện,
  không có thông tin chẩn đoán nào khác trong chính command này.
- **Không extends `BaseCommand`** — khác với `CreateTablePartitionCommand` (và 18 Command khác), batch
  này KHÔNG có cơ chế lock PID chống chạy trùng. *(suy đoán: có thể vì mọi phép xóa ở đây đều tự nhiên
  an toàn khi chạy trùng — `DROP TABLE` có kiểm tra tồn tại trước, `deleteAll` theo điều kiện thời gian
  cố định trong ngày không đổi giữa 2 lần chạy gần nhau — nên không cần lock; nhưng đây chỉ là suy đoán
  về lý do, không xác nhận được chủ ý thật của tác giả).*
- Phụ thuộc trực tiếp vào output của `CreateTablePartitionCommand` (batch tạo phải chạy trước và đúng
  tên partition, nếu không `in_array($partitionName, $tables)` sẽ luôn `false` và không xóa được gì —
  không phải lỗi, chỉ là không hoạt động — nên rất khó nhận ra bằng log nếu 2 batch lệch tên bảng).
- Việc DROP hẳn 1 bảng partition (thay vì archive) là KHÔNG HỒI PHỤC được nếu không có bước export CSV
  trước đó thành công (xem A.2.1 — phụ thuộc vào wrapper `.sh` chưa đọc được nội dung để xác nhận thứ tự
  chạy CSV-trước-hay-sau-delete).

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

> Phần DROP partition (10 bảng) đã có kết luận đầy đủ ở `CreateTablePartition.md` — DynamoDB TTL thay
> thế toàn bộ cặp đôi tạo/xóa partition, không cần batch nào tương đương. Phần dưới đây CHỈ đối chiếu 3
> bảng DELETE-theo-điều-kiện ở A.2.3 (`ConDeviceControls`, `ConUserGroupHistories`, `ConEcoPoints`).
> Không có candidate nào đủ "cùng bản chất" (có dữ liệu tương đương VÀ có cơ chế retention tương đương)
> để lập B.1/B.2 — dùng bảng "Đã kiểm tra" thay thế.

## Đã kiểm tra

| Khái niệm cũ | Khu vực / candidate đã tra | Kết quả |
|---|---|---|
| `ConDeviceControls` (lịch sử điều khiển thiết bị, giữ 13 tháng) | `template-dynamodb.yaml` (toàn bộ), `src/layers/common/nodejs/models/DeviceControl.ts`, `batch-execute-automation`, `batch-control-device-and-push-notice-sensor`, `batch-end-dr` | Không có bảng lưu LỊCH SỬ điều khiển. `AutomationTable` chỉ lưu cấu hình automation (không có timestamp lịch sử). `DeviceControl` chỉ là interface payload tạm dùng lúc thực thi lệnh, không persist. → Dữ liệu cần xóa ở bản cũ **không tồn tại** ở hệ thống mới (không phải vấn đề retention, mà là chưa lưu trữ lịch sử này). |
| `ConUserGroupHistories` (lịch sử phân khúc nhóm, giữ 24 tháng) | Grep `UserGroupHistory`/`GroupSummary`/`GroupAve`/`population`/`compare` trên toàn `src/` | 0 kết quả — khớp kết luận đã có ở `CreateGroupSummary.md` (tính năng "so sánh với nhóm tương tự" chưa port). Không có dữ liệu này để cần retention. |
| `ConEcoPoints` (điểm tiết kiệm năng lượng, giữ 2 năm tài chính) | `PointBadgeStatsTable` (`template-dynamodb.yaml:1012-1047`), `PointBadgeMasterTable` (`:1049-1061`), `UserBadgeSummaryTable` (`:1445-1457`), `src/functions/give-point-to-point-infinity/app.ts` | `PointBadgeStatsTable` là bảng gần giống nhất — lưu lịch sử nhận điểm/badge theo `user_id`+`received_month`/`received_at` (GSI `gsi_received_month`). Nhưng: **không có `TimeToLiveSpecification`** (khác các bảng usage đã có TTL như `DeviceMonthlyUsageHistoryTable:1202-1204`), **không dùng khái niệm năm tài chính**, và grep `delete`/`cleanup`/`purge`/`retention` trên `src/functions/`, `src/statemachine/` không ra Lambda nào xóa point/badge theo lịch. → Có lưu trữ dữ liệu tương tự, nhưng **thiếu hẳn cơ chế retention** — khác bản chất phần đang audit (retention), không phải phần storage. |

---

## Tổng kết

**Phần DROP partition (10 bảng) — đã kết luận ở `CreateTablePartition.md`, không lặp lại ở đây; chỉ nhắc
điểm liên quan trực tiếp**: `CreateTablePartitionCommand` cô lập lỗi từng operation bằng try/catch riêng,
còn `DeleteDataCommand` (batch đang audit) hoàn toàn KHÔNG có try/catch nào (A.2.4) — 2 batch cùng vận
hành 1 cơ chế PostgreSQL partitioning duy nhất nhưng lại có mức độ chịu lỗi khác hẳn nhau; ở hệ thống
mới, cả sự bất đối xứng này biến mất cùng với toàn bộ cơ chế partition (DynamoDB TTL không cần try/catch
vì không có bước "xóa chủ động" nào để lỗi).

**Phần DELETE theo điều kiện thời gian (3 bảng) — đây là phát hiện MỚI của audit này, chưa từng nêu ở
file khác:**

- 2/3 khái niệm (`ConDeviceControls`, `ConUserGroupHistories`) không có dữ liệu tương ứng ở hệ thống mới
  để cần lo retention — không phải "thiếu cơ chế xóa", mà là bản thân TÍNH NĂNG lưu trữ dữ liệu đó chưa
  tồn tại (lịch sử điều khiển thiết bị chỉ xử lý real-time, không persist; tính năng so sánh nhóm chưa
  port — đã xác nhận ở `CreateGroupSummary.md`).
- 1/3 khái niệm (`ConEcoPoints` → `PointBadgeStatsTable`) là trường hợp khác hẳn và đáng chú ý nhất:
  **dữ liệu TƯƠNG ỨNG CÓ tồn tại** (lịch sử điểm/badge), nhưng **cơ chế retention thì KHÔNG** — không
  TTL, không batch xóa. Nghĩa là ở khía cạnh này, hệ thống mới không "thay bằng cơ chế khác về chất" mà
  đơn giản là **chưa có cơ chế nào cả** — lịch sử điểm/badge đang được giữ vô thời hạn, trong khi bản cũ
  có chủ đích giữ đúng 2 năm tài chính (`ECO_POINTS_SAVE_TIME=2`, `const.php:723`). Đây là 1 gap thật
  cần lưu ý khi nghiệp vụ mới xác nhận lại có cần giới hạn thời gian lưu trữ điểm/badge hay không, chứ
  không thể tự suy ra "chắc không cần vì DynamoDB rẻ hơn lưu trữ" — đó là quyết định nghiệp vụ, không
  phải kỹ thuật.

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/conciergesv-develop/src/Command/DeleteDataCommand.php` |
| Hệ thống cũ | Ý nghĩa cột `ConDeviceControl` | `sources/eminel_sv_lib-develop/src/Model/Entity/ConDeviceControl.php:30` |
| Hệ thống cũ | Ý nghĩa cột `ConUserGroupHistory` (đã audit ở `CreateGroupSummary.md`) | `sources/eminel_sv_lib-develop/src/Model/Entity/ConUserGroupHistory.php` |
| Hệ thống cũ | Ý nghĩa cột `ConEcoPoint` | `sources/eminel_sv_lib-develop/src/Model/Entity/ConEcoPoint.php:35` |
| Hệ thống cũ | Hằng số retention năm tài chính | `sources/conciergesv-develop/config/const.php:723` |
| Hệ thống cũ | Lịch chạy (cron), xác nhận không có cron riêng cho `CreateCsvAndZip*` | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:39-41` (toàn file đã grep) |
| Hệ thống cũ | Mapping docs⇔sources xác nhận cặp `DeleteDataCommand`+`CreateCsvAndZip*Command` | `README.md:159` |
| Hệ thống cũ | Danh sách batch (mô tả tiếng Nhật, nhóm server) | `docs/03_API仕様/04_バッチ一覧.md:76` |
| Hệ thống cũ | Batch cặp đôi "tạo trước" (đối chứng 10 bảng partition) | `docs/legacy-batch-review/CreateTablePartition.md` |
| Hệ thống cũ | Tài liệu spec retention/CSV, chưa đọc được nội dung (binary) | `docs/02_詳細設計/08_データ削除と過去データCSV作成/{データの保存期間_20240618_朴.xlsx,データ削除と過去データCSV作成仕様.xlsx,データ削除仕様書/削除処理仕様書_朴_20240819.xlsx,データ削除仕様書/過去データCSV作成仕様書_20240708.xlsx}` |
| Hệ thống mới | Candidate gần nhất cho `ConEcoPoints` (có storage, thiếu retention) | `template-dynamodb.yaml:1012-1047` (`PointBadgeStatsTable`), `:1049-1061` (`PointBadgeMasterTable`), `:1445-1457` (`UserBadgeSummaryTable`) |
| Hệ thống mới | Đối chứng bảng CÓ TTL (để thấy `PointBadgeStatsTable` không có) | `template-dynamodb.yaml:1202-1204` (`DeviceMonthlyUsageHistoryTable`) |
| Hệ thống mới | Xác nhận không lưu lịch sử điều khiển thiết bị | `src/layers/common/nodejs/models/DeviceControl.ts` |
| Hệ thống mới | Xác nhận không có tính năng nhóm khách hàng (đã audit) | `docs/legacy-batch-review/CreateGroupSummary.md` |
