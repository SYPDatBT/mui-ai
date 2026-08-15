# Batch cũ — RcvCntctCancellationCommand（Xzilla接点データ（電気解約）受信・買電売電計算停止フラグ設定）

## Tóm tắt

`RcvCntctCancellationCommand` (lệnh CLI `RcvCntctCancellation`, IF2249) là batch trong hệ thống cũ (EMINEL コンシェルジュサーバー) nhận **CSV huỷ hợp đồng điện** từ server trung gian Xzilla (mỗi lần chạy xử lý đúng 1 file CSV của ngày hôm nay), lọc ra các bản ghi thuộc loại hợp đồng điện `PE624`/`PE625`, upsert vào bảng `ipf_cntct_cancellations`, rồi chạy một câu UPDATE để đặt **cờ dừng tính toán mua/bán điện** (`t_101.c065 = 1`) cho các khách hàng đã huỷ hợp đồng và đến hạn xử lý (`work_schedule_ymd <= hôm nay`). Cuối cùng, nếu file master người thanh toán (IF2264) của cùng ngày cũng đã nhận xong, batch gọi thêm 1 API thông báo hoàn tất đăng ký thông tin khách hàng. Toàn bộ xử lý nằm trong 1 transaction; chi tiết ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Nhận CSV huỷ hợp đồng điện (IF2249) từ Xzilla, lưu vào DB và đặt cờ dừng tính toán mua/bán điện cho khách hàng đã huỷ. |
| **Input** | File CSV trên server trung gian Xzilla (đường dẫn từ env `XZILLA_RELATION_SERVER_CANCELLATION_URL`) ＋ bảng `XzillaRelationLogs`（log trạng thái xử lý file, dùng để chống trùng）＋ bảng `ipf_cntct_cancellations`（bản ghi huỷ hợp đồng đã lưu trước đó, dùng để phân biệt update/insert）. |
| **Output** | Upsert vào bảng `ipf_cntct_cancellations` ＋ UPDATE bảng `t_101`（cờ `c065`, thời điểm `c054`）＋ ghi log vào `XzillaRelationLogs` ＋ (có điều kiện) gọi API thông báo hoàn tất đăng ký thông tin khách hàng. |
| **Khái quát xử lý** | 1. Lấy danh sách file trên server trung gian, chọn file CSV có timestamp là hôm nay.<br>2. Kiểm tra log — nếu file đã "đang xử lý" hoặc "đã hoàn tất" thì dừng (chống trùng).<br>3. Tải file CSV về local, ghi log "đang xử lý".<br>4. Đọc CSV, lọc chỉ giữ loại hợp đồng `PE624`/`PE625`, upsert theo khoá `ipf_use_cntr_num`.<br>5. UPDATE cờ dừng tính toán mua/bán điện trên `t_101` cho các hợp đồng đã đến hạn huỷ.<br>6. Ghi log "hoàn tất". Nếu IF2264 (master người thanh toán) của hôm nay cũng đã hoàn tất, gọi API thông báo. |

## Phần 2 — Chi tiết

### Bản đồ luồng xử lý — 8 bước, trong 1 transaction

```
BƯỚC 1  Lấy danh sách file    → đọc dir trung gian, lọc .csv, sort theo timestamp giảm dần   §2.1
BƯỚC 2  Chọn file hôm nay     → timestamp ∈ [00:00:00, 23:59:59] của ngày hiện tại            §2.1
BƯỚC 3  Chống xử lý trùng     → tra log theo (upload_type=3, file_name) — status 0/1 → dừng   §2.2
BƯỚC 4  Tải file & ghi log    → download CSV về local, insert/update log "đang xử lý"          §2.3
BƯỚC 5  Lọc & upsert          → chỉ giữ PE624/PE625, upsert theo ipf_use_cntr_num              §2.4
BƯỚC 6  Đặt cờ dừng tính toán → UPDATE t_101 SET c065=1 cho hợp đồng đã đến hạn huỷ             §2.5
BƯỚC 7  Ghi log hoàn tất      → update status log = 1 (completed)                              §2.6
BƯỚC 8  Gọi API (có điều kiện)→ chỉ khi IF2264 (payer) hôm nay cũng đã hoàn tất                 §2.7
```

| Bước | Nội dung | Chi tiết ở |
|---|---|---|
| 1–2 | Lấy danh sách file trung gian, xác định file CSV của hôm nay | §2.1 |
| 3 | Chống xử lý trùng qua bảng log | §2.2 |
| 4 | Tải file, ghi log "đang xử lý" | §2.3 |
| 5 | Lọc theo loại hợp đồng, upsert dữ liệu huỷ hợp đồng | §2.4 |
| 6 | Đặt cờ dừng tính toán mua/bán điện | §2.5 |
| 7 | Ghi log "hoàn tất" | §2.6 |
| 8 | Gọi API thông báo — có điều kiện phụ thuộc IF2264 | §2.7 |
| — | Cấu trúc dữ liệu ghi ra `ipf_cntct_cancellations` | §2.8 |

---

### 2.1 Xác định file CSV cần xử lý

| Mục | Nội dung |
|---|---|
| Nguồn danh sách file | Thư mục trên server trung gian, đường dẫn lấy từ env `XZILLA_RELATION_SERVER_CANCELLATION_URL` ([:72](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L72)) |
| Điều kiện lọc file | Chỉ nhận file có đuôi `.csv` ([:83](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L83)) |
| Khoá timestamp | 14 ký tự cuối của tên file (không kể `.csv`) — định dạng `yyyyMMddHHmmss` ([:85-89](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L85-L89)) |
| Cách chọn file | Sort các timestamp giảm dần (`krsort`), lấy file **đầu tiên** rơi vào khung `[hôm nay 00:00:00, hôm nay 23:59:59]` — tức file mới nhất trong ngày ([:92-107](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L92-L107)) |
| Không có file | Không có file nào trên dir, hoặc không có file nào của hôm nay → log rồi `commit` + `abort` (không rollback, vì chưa có gì để huỷ) ([:74-79](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L74-L79), [:109-113](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L109-L113)) |

Batch chỉ xử lý **đúng 1 file** mỗi lần chạy (file mới nhất của hôm nay) — khác với `CalcTenMinutesEnergyCommand` (không có cơ chế bù nhiều cửa sổ chưa xử lý).

### 2.2 Chống xử lý trùng qua bảng log

Trước khi tải file, batch tra bảng `XzillaRelationLogs` theo `(upload_type = 3, file_name = <file đã chọn>)` ([:118-124](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L118-L124)):

| status | Ý nghĩa | Hành vi |
|---|---|---|
| `0` | Đang xử lý (*suy đoán* — không có hằng số tên riêng, suy từ comment "ステータスが処理中" đối chiếu giá trị `0`/`1`) | Dừng batch (`commit` + `abort`) |
| `1` | Đã hoàn tất (hằng số `XZILLA_RELATION_LOGS_STAUS_COMPLETED`) | Dừng batch (`commit` + `abort`) |
| Không có record, hoặc record khác `0`/`1` | Chưa xử lý | Tiếp tục |

`upload_type` trên bảng log phân biệt 2 loại file Xzilla mà batch này quan tâm ([:33-36](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L33-L36)):

| Hằng số | Giá trị | Ý nghĩa |
|---|---:|---|
| `XZILLA_RELATION_LOGS_UPLOAD_TYPE_MASTER` | `2` | File master người thanh toán hợp đồng theo địa điểm (IF2264) — dùng ở §2.7, không phải file batch này xử lý |
| `XZILLA_RELATION_LOGS_UPLOAD_TYPE_CANCELLAION` | `3` | File huỷ hợp đồng (IF2249) — chính là file batch này xử lý |

### 2.3 Tải file & ghi log "đang xử lý"

- Tải CSV về `DOWNLOAD_TO_LOCAL_DIRECTORY` = `/var/data/xzilla/IF2249/` ([:30](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L30), [:146-153](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L146-L153)). Comment trong code ghi rõ: muốn giữ nguyên CSV cũ để kiểm tra thì phải comment-out bước tải này ([:145](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L145)) — tức file local **bị ghi đè** ở lần chạy kế tiếp.
- Ghi (insert/update) log `upload_type=3, file_name=<file>` với trạng thái "đang xử lý" trước khi upsert dữ liệu, lấy `xzillaRalationLogsInsertId` để dùng lại ở bước hoàn tất ([:158-164](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L158-L164)).
- Lỗi ở bước tải/ghi log → `rollback` toàn bộ transaction ([:150-153](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L150-L153), [:160-163](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L160-L163)).

### 2.4 Lọc theo loại hợp đồng & upsert (`bulkInsertCancellationData`)

| Mục | Nội dung |
|---|---|
| Vị trí | [RcvCntctCancellationCommand.php:229-298](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L229-L298) |
| Bỏ header | Dòng đầu tiên (`$i == 0`) bị skip ([:238-241](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L238-L241)) |
| Điều kiện lọc | Chỉ giữ dòng có cột 59 (index `58`) = `'PE624'` hoặc `'PE625'` (loại hợp đồng điện) — dòng khác bị bỏ qua ([:242-245](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L242-L245)) |
| Khoá đối chiếu update/insert | So khớp theo `ipf_use_cntr_num` (cột 57, index `56`) với bảng `ipf_cntct_cancellations` hiện có ([:247-249](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L247-L249)) |
| Nếu lỗi khi tra record | Log lỗi rồi `continue` sang dòng CSV kế tiếp — **không** làm fail cả batch ([:250-253](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L250-L253)) |
| Nếu lỗi khi save (update hoặc insert) | Trả `false` ngay — làm fail cả batch, dẫn tới rollback ([:268-273](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L268-L273), [:288-294](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L288-L294)) |

Ánh xạ cột CSV → field bảng `ipf_cntct_cancellations` (7 cột được dùng, không rõ tổng số cột của file — không có định nghĩa interface để đối chiếu):

| Cột CSV (index 0-based) | Field | Ghi chú |
|---|---|---|
| `0` | `ipf_cntct_num` | |
| `27` | `work_schedule_ymd` | Ngày dự kiến thực hiện huỷ — dùng để so `<= hôm nay` ở §2.5 |
| `36` | `work_progress_code` | Mã tiến độ công việc — dùng để loại trừ `'9'` ở §2.5 |
| `53` | `create_datetime` | |
| `54` | `update_datetime` | |
| `56` | `ipf_use_cntr_num` | Khoá đối chiếu update/insert; cũng là khoá join sang `t_101.c063` ở §2.5 |
| `58` | `cntr_clsfy_code` | Loại hợp đồng — điều kiện lọc `PE624`/`PE625` |

### 2.5 Đặt cờ dừng tính toán mua/bán điện (`updateCalculationStopFlag`)

Một câu SQL UPDATE duy nhất trên `t_101`, join với `ipf_cntct_cancellations` theo `ipf_use_cntr_num = c063` ([RcvCntctCancellationCommand.php:306-334](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L306-L334)):

```sql
UPDATE t_101 SET c065 = 1, c054 = :update_time
   FROM ( SELECT cancel.ipf_use_cntr_num AS ipf_num, customer.c066
            FROM ipf_cntct_cancellations AS cancel
            INNER JOIN t_101 AS customer
                    ON cancel.ipf_use_cntr_num = customer.c063
           WHERE work_schedule_ymd <= :now
             AND work_progress_code NOT IN ('9')
             AND c066 = 0
        ) AS haishi
 WHERE c063 = haishi.ipf_num
```

| Điều kiện đồng thời | Ý nghĩa |
|---|---|
| `work_schedule_ymd <= hôm nay` | Đã đến hoặc qua ngày dự kiến huỷ hợp đồng |
| `work_progress_code NOT IN ('9')` | Loại trừ trạng thái tiến độ mã `9` (*suy đoán* — không rõ nghĩa cụ thể của mã `9`, không có chú giải trong code) |
| `c066 = 0` | Chưa bị đặt cờ liên quan trước đó — tránh cập nhật lại record đã xử lý (*suy đoán* — ý nghĩa cụ thể của `c066` không được xác nhận trong file này) |

Kết quả: `t_101.c065 = 1` (cờ dừng tính toán mua/bán điện) và `t_101.c054` (thời điểm cập nhật) được set cho toàn bộ khách hàng thoả 3 điều kiện trên, trong **một lần UPDATE** (không lặp theo từng dòng CSV).

### 2.6 Ghi log "hoàn tất"

Dùng lại `xzillaRalationLogsInsertId` lưu ở §2.3, update status của record log đó thành hoàn tất (`XZILLA_RELATION_LOGS_STAUS_COMPLETED = 1`) ([:185-188](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L185-L188)). Lỗi ở bước này → rollback toàn bộ.

### 2.7 Gọi API thông báo — điều kiện phụ thuộc IF2264 (payer master)

Sau khi hoàn tất phần huỷ hợp đồng, batch tra tiếp bảng `XzillaRelationLogs` theo điều kiện khác ([:193-206](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L193-L206)):

| Điều kiện tra log | Giá trị |
|---|---|
| `upload_type` | `2` (`XZILLA_RELATION_LOGS_UPLOAD_TYPE_MASTER` — file master người thanh toán, IF2264) |
| `created` | Trong khung hôm nay `00:00:00`〜`23:59:59` |
| `status` | `1` (hoàn tất) |

**Chỉ khi** có record thoả cả 3 điều kiện trên (nghĩa là: batch nhận IF2264 của hôm nay cũng đã chạy xong) thì mới gọi `execCustomersUpdCompleteApi()` — API thông báo hoàn tất đăng ký thông tin khách hàng ([:208-217](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L208-L217)). Nếu không có record thoả mãn, batch kết thúc bình thường mà **không** gọi API này — không phải lỗi, chỉ là chưa đủ điều kiện. Gọi API lỗi → rollback toàn bộ transaction ([:213-216](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L213-L216)).

Đây là điểm phụ thuộc trực tiếp vào batch #6 (`RcvEmsPlsCntrPayerCommand`, IF2264) — batch đó phải chạy và hoàn tất **trước** trong ngày để bước này của batch #5 có hiệu lực.

### 2.8 Toàn bộ transaction

Toàn bộ 8 bước nằm trong 1 transaction mở ở đầu hàm `execute()` ([:64-65](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L64-L65)):

| Trường hợp | Hành vi |
|---|---|
| Không có file / không có file hôm nay / file đã xử lý (§2.1, §2.2) | `commit` (không có gì để huỷ) rồi `abort` |
| Lỗi ở bất kỳ bước tải file, upsert, update cờ, ghi log hoàn tất, gọi API (§2.3–§2.7) | `rollback` toàn bộ rồi `abort` |
| Toàn bộ 8 bước thành công | `commit` ở cuối ([:220](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L220)) |

---

## Nguồn

| Nội dung | Căn cứ |
|---|---|
| Logic hệ cũ | `sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php` |
| Hằng số (đường dẫn local, loại file, status log) | Định nghĩa ngay trong class này ([:29-36](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L29-L36)) — không có file hằng số legacy dùng chung như `config/const.php` |
