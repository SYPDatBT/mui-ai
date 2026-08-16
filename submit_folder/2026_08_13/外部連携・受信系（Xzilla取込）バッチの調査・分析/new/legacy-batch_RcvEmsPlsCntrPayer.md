# Batch cũ — RcvEmsPlsCntrPayerCommand（Xzilla場所契約支払者マスタ受信・契約終了判定・顧客連携番号更新）

## Tóm tắt

`RcvEmsPlsCntrPayerCommand` (lệnh CLI `RcvEmsPlsCntrPayer`, IF2264) là batch trong hệ thống cũ (EMINEL コンシェルジュサーバー) nhận **CSV master 場所契約支払者**（thông tin nơi‑hợp đồng‑người thanh toán, gắn với từng EMS‑SP）từ server trung gian Xzilla. Mỗi lần chạy xử lý đúng 1 file CSV của ngày hôm nay: **xoá toàn bộ** dữ liệu cũ trong bảng `ipf_ems_pls_cntr_payers` rồi **nạp lại** chỉ các bản ghi thuộc 7 mã loại hợp đồng quy định, sau đó với mỗi EMS‑SP thu được, áp **3 điều kiện xét hợp đồng đã kết thúc hay chưa** để quyết định: nếu kết thúc → xoá các số liên kết (giữ nguyên số khách hàng) và bật cờ dừng tính mua/bán điện trên `ConCustomers`; nếu chưa → cập nhật đầy đủ các số liên kết và tắt cờ dừng tính. Cuối cùng, nếu file huỷ hợp đồng điện (IF2249, `RcvCntctCancellationCommand`) của cùng ngày cũng đã hoàn tất, batch gọi thêm 1 API thông báo hoàn tất đăng ký thông tin khách hàng — đây là điều kiện **hai chiều**, batch nào trong 2 batch chạy xong **sau** trong ngày sẽ là bên gọi API. Toàn bộ nằm trong 1 transaction; chi tiết ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Nhận CSV master 場所契約支払者 (IF2264) từ Xzilla, thay toàn bộ bảng `ipf_ems_pls_cntr_payers`, rồi xét kết thúc hợp đồng để cập nhật các số liên kết mua/bán điện và cờ dừng tính toán trên `ConCustomers`. |
| **Input** | File CSV trên server trung gian Xzilla (đường dẫn từ env `XZILLA_RELATION_SERVER_MASTER_URL`) ＋ bảng `XzillaRelationLogs`（chống trùng）＋ bảng `ipf_ems_pls_cntr_payers`（dữ liệu vừa nạp, đọc lại ngay trong cùng lần chạy）. |
| **Output** | **Xoá toàn bộ + nạp lại** bảng `ipf_ems_pls_cntr_payers` ＋ UPDATE bảng `ConCustomers`（`c061`/`c062`/`c063`/`c064`/`c065`/`c054`）＋ ghi log vào `XzillaRelationLogs` ＋ (có điều kiện) gọi API thông báo hoàn tất. |
| **Khái quát xử lý** | 1. Chọn file CSV hôm nay trên server trung gian; chống trùng qua log.<br>2. Tải CSV, ghi log "đang xử lý".<br>3. Xoá toàn bộ `ipf_ems_pls_cntr_payers`, nạp lại chỉ 7 mã hợp đồng quy định.<br>4. Với mỗi EMS‑SP: xét kết thúc hợp đồng (3 điều kiện) → cập nhật `ConCustomers`.<br>5. Ghi log "hoàn tất". Nếu IF2249 (huỷ hợp đồng điện) của hôm nay cũng đã hoàn tất, gọi API thông báo. |

## Phần 2 — Chi tiết

### Bản đồ luồng xử lý — trong 1 transaction

```
BƯỚC 1  Lấy danh sách file    → đọc dir trung gian, lọc .csv, sort theo timestamp giảm dần   §2.1
BƯỚC 2  Chọn file hôm nay     → timestamp ∈ [00:00:00, 23:59:59] của ngày hiện tại            §2.1
BƯỚC 3  Chống xử lý trùng     → tra log theo (upload_type=2, file_name) — status 0/1 → dừng   §2.2
BƯỚC 4  Tải file & ghi log    → download CSV về local, insert/update log "đang xử lý"          §2.3
BƯỚC 5  Xoá toàn bộ master cũ → deleteAll('1=1') trên ipf_ems_pls_cntr_payers                 §2.4
BƯỚC 6  Lọc & nạp lại         → chỉ giữ 7 mã hợp đồng, bulk insert theo lô                     §2.4
BƯỚC 7  Xét kết thúc hợp đồng → 3 điều kiện, gộp theo nhóm PE/PG                                §2.5
BƯỚC 8  Cập nhật khách hàng   → UPDATE ConCustomers (liên kết ／ cờ dừng tính)                  §2.5
BƯỚC 9  Ghi log hoàn tất      → update status log = 1 (completed)                              §2.6
BƯỚC 10 Gọi API (có điều kiện)→ chỉ khi IF2249 (huỷ hợp đồng) hôm nay cũng đã hoàn tất          §2.6
```

| Bước | Nội dung | Chi tiết ở |
|---|---|---|
| 1–3 | Xác định file CSV hôm nay, chống xử lý trùng qua bảng log | §2.1 · §2.2 |
| 4 | Tải file, ghi log "đang xử lý" | §2.3 |
| 5–6 | Xoá toàn bộ + nạp lại master theo 7 mã hợp đồng | §2.4 |
| 7–8 | Xét kết thúc hợp đồng, cập nhật liên kết khách hàng | §2.5 |
| 9–10 | Ghi log "hoàn tất", gọi API — điều kiện hai chiều với IF2249 | §2.6 |
| — | Cấu trúc CSV → bảng `ipf_ems_pls_cntr_payers` | §2.7 |

---

### 2.1 Xác định file CSV cần xử lý

| Mục | Nội dung |
|---|---|
| Nguồn danh sách file | Thư mục trên server trung gian, đường dẫn lấy từ env `XZILLA_RELATION_SERVER_MASTER_URL` ([:74](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L74)) |
| Điều kiện lọc file | Chỉ nhận file có tên **chứa** chuỗi `.csv` (`str_contains` — không kiểm tra đuôi chặt) ([:85](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L85)) |
| Khoá timestamp | 14 ký tự cuối của tên file (không kể `.csv`) — định dạng `yyyyMMddHHmmss` ([:87-91](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L87-L91)) |
| Cách chọn file | Sort các timestamp giảm dần (`krsort`), lấy file **đầu tiên** rơi vào khung `[hôm nay 00:00:00, hôm nay 23:59:59]` ([:95-109](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L95-L109)) |
| Không có file | Không có file nào trên dir, hoặc không có file nào của hôm nay → log rồi `commit` + `abort` (không rollback, vì chưa có gì để huỷ) ([:76-81](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L76-L81), [:111-115](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L111-L115)) |

Danh sách file lấy qua SFTP (`XzillaRelationComponent::getCsvFileLists()` → `SFTP::nlist()`, login bằng key riêng — env `XZILLA_RELATION_SERVER_HOST`/`PORT`/`USER`/`SECRETKEY_PATH`) ([XzillaRelationComponent.php:39-57](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L39-L57), [:64-77](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L64-L77)).

### 2.2 Chống xử lý trùng qua bảng log

Trước khi tải file, batch tra bảng `XzillaRelationLogs` theo `(upload_type = 2, file_name = <file đã chọn>)` ([:117-131](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L117-L131)):

| status | Ý nghĩa | Hành vi |
|---|---|---|
| `0` | Đang xử lý (*suy đoán* — không có hằng số tên riêng trong command này, suy từ comment "ステータスが処理中" đối chiếu giá trị `0`/`1`; hằng số `XZILLA_RELATION_LOGS_STAUS_PROCESSING=0` có định nghĩa ở `XzillaRelationComponent` ([:29](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L29))) | Dừng batch (`commit` + `abort`) |
| `1` | Đã hoàn tất (hằng số `XZILLA_RELATION_LOGS_STAUS_COMPLETED`) | Dừng batch (`commit` + `abort`) |
| Không có record, hoặc record khác `0`/`1` | Chưa xử lý | Tiếp tục | ([:132-140](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L132-L140)) |

`upload_type` phân biệt 2 loại file Xzilla liên quan tới batch này ([:34-36](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L34-L36)):

| Hằng số | Giá trị | Ý nghĩa |
|---|---:|---|
| `XZILLA_RELATION_LOGS_UPLOAD_TYPE_MASTER` | `2` | File master 場所契約支払者 (IF2264) — chính là file batch này xử lý |
| `XZILLA_RELATION_LOGS_UPLOAD_TYPE_CANCELLAION` | `3` | File huỷ hợp đồng điện (IF2249) — dùng ở §2.6, không phải file batch này xử lý |

### 2.3 Tải file & ghi log "đang xử lý"

- Tải CSV về `DOWNLOAD_TO_LOCAL_DIRECTORY` = `/var/data/xzilla/IF2264/` qua SFTP, tạo thư mục nếu chưa có (`mkdir(..., 0777)`) ([:30](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L30), [:144-154](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L144-L154), [XzillaRelationComponent.php:87-109](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L87-L109)).
- Ghi (insert/update) log `upload_type=2, file_name=<file>` với trạng thái "đang xử lý", lấy `xzillaRalationLogsInsertId` để dùng lại ở bước hoàn tất ([:156-165](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L156-L165), [XzillaRelationComponent.php:117-155](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L117-L155)).
- Lỗi tải file → `commit` + `abort` (như trường hợp không có file — chưa ghi gì vào DB) ([:152-153](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L152-L153)).
- Lỗi ghi log "đang xử lý" → `rollback` toàn bộ transaction ([:161-164](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L161-L164)).

> ⚠️ **Bên trong `saveXzillaRelationLogs()`, câu kiểm tra "đã có log chưa" hard‑code `upload_type = 1`** ([XzillaRelationComponent.php:124-127](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L124-L127)), trong khi record thực tế được **insert** với `upload_type` = giá trị tham số truyền vào (ở đây là `2`) ([:142](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L142)). Với batch này (`$uploadType = 2`), câu kiểm tra không bao giờ khớp đúng loại — nếu tồn tại một record `upload_type=1` **trùng tên file** (khác IF), hàm sẽ ghi đè nhầm lên record đó thay vì insert mới; nếu không trùng tên, hàm luôn rơi vào nhánh insert. Trong luồng thực tế của batch này rủi ro thấp vì đã có bước chống trùng riêng ở §2.2, nhưng đây là lỗi copy‑paste (đáng lẽ phải dùng `$uploadType` thay vì literal `1`) tồn tại sẵn trong code hệ cũ.

### 2.4 Xoá toàn bộ + nạp lại master (`bulkInsertMasterData`)

| Mục | Nội dung |
|---|---|
| Xoá dữ liệu cũ | `deleteAll('1=1')` — xoá **toàn bộ** bảng `ipf_ems_pls_cntr_payers` trước khi nạp, không phải upsert theo khoá ([:167-177](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L167-L177)) |
| Vị trí hàm nạp | [RcvEmsPlsCntrPayerCommand.php:245-363](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L245-L363) |
| Bỏ header | Dòng đầu tiên (`$i == 0`) bị skip ([:252-257](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L252-L257)) |
| Điều kiện lọc | Chỉ giữ dòng có `cntr_clsfy_code` (cột 22, index `21`) ∈ `{PE624, PE625, PE650, PE651, PE652, PG077, PG079}` — dòng khác bị bỏ qua hoàn toàn, không insert ([:318-329](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L318-L329)) |
| Thu thập EMS‑SP | Mỗi dòng giữ lại được thêm `ems_sp` vào `$emsSpNos`, sau đó khử trùng bằng `array_unique` (vì CSV có nhiều dòng cùng EMS‑SP) ([:331-332](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L331-L332), [:355-356](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L355-L356)) |
| Cách insert | Bulk insert theo lô, dùng chung 1 query object cho tới khi `$splitCount == 10` mới `execute()` ([:334-353](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L334-L353)) |

> ⚠️ **Comment ghi "10件ずつBULK INSERT" nhưng mỗi lô thực chất là 11 bản ghi.** `$query->values($values)` chạy **trước** khi kiểm tra `$splitCount == 10`, nên khi biến đếm chạm mốc `10` thì query đã tích lũy đủ 11 dòng (đếm từ `0`) rồi mới `execute()` ([:339-348](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L339-L348)) — lệch 1 so với comment, không ảnh hưởng kết quả (dữ liệu vẫn được insert đủ) nhưng cần biết khi đọc lại logic batch size.

### 2.5 Xét kết thúc hợp đồng & cập nhật khách hàng (`updateCustomerData`)

Nguyên văn spec ghi trong code ([:373-385](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L373-L385)) — 3 điều kiện xác định kết thúc hợp đồng:

| # | Điều kiện | Phạm vi xét |
|---|---|---|
| ① | サービスポイント＿適用終了年月日 (`reg_end_ymd_sp`) **≠ `99991231`** | Giá trị **lớn nhất** trong nhóm hợp đồng cùng tiền tố (`PE...` hoặc `PG...`) |
| ② | 契約終了年月日 (`cntr_end_ymd`) **≠ `99991231`** | Giá trị **lớn nhất** trong cùng nhóm |
| ③ | Hợp đồng điện (`PE624`/`PE625`) mà **thiếu** 供給地点特定番号 (`supply_point_num`) hoặc IPF使用契約番号 (`ipf_use_cntr_num`) | Chỉ khi có hợp đồng `PE624`/`PE625` |

Nếu **①, ② hoặc ③** đúng với bất kỳ nhóm nào → coi là **kết thúc hợp đồng**.

#### Xử lý theo từng EMS‑SP

```
Với mỗi ems_sp trong emsSpNos:
  1. Lấy toàn bộ record ipf_ems_pls_cntr_payers của ems_sp này,
     sort theo cntr_clsfy_code, reg_end_ymd_sp, cntr_end_ymd (asc)   [:389-398]
  2. Không có record → bỏ qua ems_sp này                             [:400-403]
  3. Gộp theo nhóm (2 ký tự đầu cntr_clsfy_code = "PE" hoặc "PG"):
     - reg_end_ymd_sp lớn nhất trong nhóm
     - cntr_end_ymd lớn nhất trong nhóm
     - customerNo   ← links_cus_num của record PG (theo dõi lớn nhất)
     - supplyPointNo, ipfContractNo ← supply_point_num / ipf_use_cntr_num
       của record PE624/PE625 (theo dõi lớn nhất)
     - receivePointNo ← supply_point_num của record PE650/651/652
       (theo dõi lớn nhất, có thể không có record này)                [:405-556]
  4. Kiểm tra 3 điều kiện ①②③ ở trên
     ĐÚNG  → supplyPointNo/ipfContractNo/receivePointNo = NULL,
             giữ nguyên customerNo, sellBuyCalcStopFlag = 1 (dừng tính)
     SAI   → cập nhật đủ 4 số liên kết, sellBuyCalcStopFlag = 0 (chạy tính)  [:558-619]
  5. UPDATE ConCustomers WHERE c001 = ems_sp AND c066 = 0
```

> Khối gộp theo nhóm (bước 3) trong code có 2 đoạn `if/else if/else` gần như trùng lặp cho `reg_end_ymd_sp` và `cntr_end_ymd`, và điều kiện nhánh đầu mỗi đoạn kiểm tra `empty($arrayPerContracts)` (toàn bộ mảng) chứ không kiểm tra riêng theo từng nhóm/field ([:422-488](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L422-L488), [:490-555](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L490-L555)) — dòng chảy đi qua nhánh khác nhau tuỳ vị trí trong loop, nhưng theo đối chiếu tay, kết quả cuối vẫn ra đúng "giá trị lớn nhất mỗi nhóm" như spec ghi ở đầu hàm. Không phát hiện sai lệch kết quả, chỉ là cách viết vòng lặp rối và dư thừa.

#### Cập nhật `ConCustomers` (`execCustomerUpdateForTerminate` / `execCustomerUpdateForDuaring`)

Model `ConCustomers` trỏ tới bảng vật lý `t_101` (`setTable('t_101')` — [ConCustomersTable.php:41](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Table/ConCustomersTable.php#L41)); các cột `c0xx` dưới đây là cột vật lý của `t_101`.

| Cột `ConCustomers` | Ý nghĩa (theo entity) | Trường hợp **kết thúc** | Trường hợp **còn hiệu lực** |
|---|---|---|---|
| `c061` (`C_PROVIDE_POINT_NUMBER`) | 供給地点特定番号 | `NULL` | `supplyPointNo` |
| `c063` (`C_SELL_BUY_SOURCE_NUMBER`) | lưu IPF使用契約番号 (`ipfContractNo`) | `NULL` | `ipfContractNo` |
| `c064` (`C_PROVIDE_ELE_POINT_NUMBER`) | lưu 受電地点特定番号 (`receivePointNo`) | `NULL` | `receivePointNo` |
| `c062` (`C_CUSTOMER_NUMBER`) | お客様番号 | **không đổi** (không có trong `execCustomerUpdateForTerminate`) | `customerNo` |
| `c065` (`C_SELL_BUY_CALC_STOP_FLAG`) | cờ dừng tính mua/bán điện (0=無効, 1=有効) | `1` | `0` |
| `c054` (`C_MODIFIED`) | thời điểm cập nhật | `now()` | `now()` |

([execCustomerUpdateForTerminate: :628-658](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L628-L658), [execCustomerUpdateForDuaring: :660-690](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L660-L690))

Cả 2 hàm đều `WHERE c001 = <ems_sp> AND c066 = 0` — chỉ cập nhật khách hàng có `c066` (`C_UPDATE_DETER_FLAG`) = `0`. Ý nghĩa cụ thể của `c066` không được xác nhận trong file này (*suy đoán* — dựa theo tên hằng số và nhãn `0=無効／1=有効` trong entity `ConCustomer`, có thể là cờ "đang bị chặn cập nhật tự động").

Lỗi ở bất kỳ bước cập nhật nào trong `updateCustomerData` → trả `false` → command `rollback` toàn bộ transaction ([:191-194](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L191-L194)).

### 2.6 Ghi log hoàn tất & gọi API — điều kiện hai chiều với IF2249

Dùng lại `xzillaRalationLogsInsertId` lưu ở §2.3, update status của record log đó thành hoàn tất ([:196-202](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L196-L202), [XzillaRelationComponent.php:162-175](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L162-L175)).

Sau đó, batch tra tiếp `XzillaRelationLogs` theo điều kiện khác ([:204-220](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L204-L220)):

| Điều kiện tra log | Giá trị |
|---|---|
| `upload_type` | `3` (`XZILLA_RELATION_LOGS_UPLOAD_TYPE_CANCELLAION` — file huỷ hợp đồng điện, IF2249) |
| `created` | ≥ hôm nay `00:00:00` |
| `modified` | ≤ hôm nay `23:59:59` |
| `status` | `1` (hoàn tất) |

**Chỉ khi** có record thoả cả 4 điều kiện trên thì mới gọi `execCustomersUpdCompleteApi()` — API thông báo hoàn tất đăng ký thông tin khách hàng ([:222-231](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L222-L231), [XzillaRelationComponent.php:182-220](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L182-L220)). Không có record thoả mãn → batch kết thúc bình thường, không gọi API — không phải lỗi. Gọi API lỗi → `rollback` toàn bộ.

Đây là điều kiện **hai chiều** với `RcvCntctCancellationCommand` (IF2249): batch đó cũng tra ngược lại log `upload_type=2` (chính batch này) trước khi gọi API của nó. Vì vậy trong 2 batch chạy trong ngày, **batch nào hoàn tất sau** sẽ là bên thực sự gọi API thông báo — không cố định batch nào luôn gọi.

Toàn bộ 10 bước nằm trong 1 transaction mở ở đầu hàm `execute()` ([:65-67](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L65-L67), commit cuối [:233-234](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L233-L234)).

### 2.7 Ánh xạ cột CSV → bảng `ipf_ems_pls_cntr_payers`

Toàn bộ 24 cột CSV (index 0-based) được map 1:1, không bỏ cột nào ([:258-283](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L258-L283)):

| Cột | Field | | Cột | Field |
|---|---|---|---|---|
| `0` | `ems_sp` | | `12` | `source_pay_cntr_num` |
| `1` | `ipf_use_place_num` | | `13` | `reg_start_ymd_pay` |
| `2` | `source_use_place_num` | | `14` | `reg_end_ymd_pay` |
| `3` | `ipf_sp_num` | | `15` | `payer_cus_meigi_num` |
| `4` | `source_sp_num` | | `16` | `source_cus_meigi_num` |
| `5` | `reg_start_ymd_sp` | | `17` | `links_cus_num` |
| `6` | `reg_end_ymd_sp` | | `18` | `oc_z_cus_identity_no` |
| `7` | `ipf_use_cntr_num` | | `19` | `supply_point_num` |
| `8` | `source_use_cntr_num` | | `20` | `sp_divcod` |
| `9` | `reg_start_ymd_use` | | `21` | `cntr_clsfy_code` |
| `10` | `reg_end_ymd_use` | | `22` | `cntr_start_ymd` |
| `11` | `ipf_pay_cntr_num` | | `23` | `cntr_end_ymd` |

Chỉ các dòng có `cntr_clsfy_code` (cột `21`) thuộc 7 giá trị nêu ở §2.4 mới được insert; các dòng khác bị loại hoàn toàn ngay từ bước nạp, không tồn tại trong bảng `ipf_ems_pls_cntr_payers` sau khi batch chạy xong.

---

## Nguồn

| Nội dung | Căn cứ |
|---|---|
| Logic chính của batch | `sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php` |
| Hàm dùng chung (SFTP, log, API) | `sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php` |
| Cấu trúc bảng `ipf_ems_pls_cntr_payers` | `sources/eminel_sv_lib-develop/src/Model/Table/IpfEmsPlsCntrPayersTable.php` |
| Cấu trúc bảng `xzilla_relation_logs` | `sources/eminel_sv_lib-develop/src/Model/Table/XzillaRelationLogsTable.php` |
| Entity + tên cột / hằng số `ConCustomers` | `sources/eminel_sv_lib-develop/src/Model/Entity/ConCustomer.php` |
| Batch liên quan (điều kiện gọi API hai chiều) | `investigate/eminel-gw/legacy-batch_RcvCntctCancellation.md` |
