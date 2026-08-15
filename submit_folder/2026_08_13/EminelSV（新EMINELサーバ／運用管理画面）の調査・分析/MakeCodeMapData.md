# MakeCodeMapDataCommand（コードマップデータをCSVから生成・ファイル出力）

## Tóm tắt

`MakeCodeMapDataCommand` là **CLI chạy thủ công** (không có lịch cron) trong `eminelsv`（新EMINELサー
バ／運用管理画面）của hệ thống cũ: đọc 1 file CSV truyền qua tham số dòng lệnh, gom dữ liệu thành map 2
chiều `[mã_loại][mã_code] = tên_code`, `serialize()` bằng PHP rồi ghi ra 1 file (mặc định
`config/code_map_data.txt`) — không đọc/ghi DB, không gửi mail, không gọi API ngoài. Trong
`syp-eminelstandard-backend` (EMINEL-smart), **không tìm thấy chức năng tương đương**: không có batch,
không có API nào đọc 1 CSV bất kỳ theo vị trí cột để dựng map mã/tên generic rồi xuất ra file — hệ
thống mới xử lý bài toán "quản lý mã/tên" theo hướng hoàn toàn khác (xem Phần B).

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `MakeCodeMapDataCommand` · Tên lệnh gọi: `make_code_map_data` *(suy đoán theo quy ước CakePHP 4, không có override tường minh trong file)* · **Không có lịch chạy — CLI chạy tay**. |
| **Vai trò** | Chuyển 1 file CSV chứa danh sách "code" (mã + tên, phân theo loại) thành 1 file map đã serialize, dùng làm dữ liệu tra cứu code→tên. |
| **Input** | Đọc 1 file CSV qua tham số dòng lệnh `INPUT_FILE` (bắt buộc). Không đọc DB, không gọi API ngoài. |
| **Output** | Ghi 1 file chứa chuỗi PHP `serialize()` — đường dẫn từ tham số `OUTPUT_FILE` (tùy chọn), mặc định `config/code_map_data.txt`. Không ghi DB, không gửi mail. |
| **Khái quát xử lý** | 1. Mở file CSV ở `INPUT_FILE`, lỗi thì `abort`.<br>2. Bỏ qua dòng đầu (header).<br>3. Với mỗi dòng còn lại: lấy cột 7 (`row[6]`) làm mã loại, cột 4 (`row[3]`) làm mã code, cột 5 (`row[4]`) làm tên code; gom vào `$mapData[mã_loại][mã_code] = tên_code`.<br>4. Xác định đường dẫn file output (tham số hoặc mặc định).<br>5. Nếu file output đã tồn tại → hỏi xác nhận ghi đè qua console; là thư mục → abort; không ghi đè → dừng êm.<br>6. `serialize($mapData)` và ghi đè file output; lỗi ghi thì `abort`.<br>7. In thông báo thành công. |

## A.2 Chi tiết

### A.2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | **Không có.** Grep tên class trong cả 2 file cron (`webap_cron設定_20240905.txt`, `mng-webap_cron設定_20241029.txt`) — không có kết quả. | — |
| Tham số dòng lệnh | `INPUT_FILE` (bắt buộc) — CSV nguồn.<br>`OUTPUT_FILE` (tùy chọn) — file đích, mặc định `CONFIG . DS . 'code_map_data.txt'`. | `MakeCodeMapDataCommand.php:18-23,43` |

### A.2.2 Định dạng CSV input (theo cách code đọc, không có comment mô tả cột)

| Cột (index 0-based) | Vai trò trong code | Ghi chú |
|---|---|---|
| Dòng đầu tiên | Bị bỏ qua hoàn toàn (`fgetcsv` gọi 1 lần không dùng kết quả) | Coi là header |
| `row[3]` | `codeId` — khóa con trong map | *(suy đoán ý nghĩa — chỉ có tên biến, không có header)* |
| `row[4]` | `codeName` — giá trị (tên hiển thị) | *(suy đoán, dựa theo tên biến)* |
| `row[6]` | `codeCategory` — khóa nhóm ngoài của map | *(suy đoán, dựa theo tên biến)* |
| `row[0],[1],[2],[5],...` | Không dùng | — |

Nguồn: `MakeCodeMapDataCommand.php:32-41`.

**Ví dụ minh họa cách map được dựng** *(số liệu giả định để minh họa cơ chế, không phải dữ liệu thật —
không có CSV mẫu nào trong repo để lấy ví dụ thật, xem phần "đã tra" dưới đây)*:

```
CSV input (dòng đầu là header, bị bỏ qua):
col0,col1,col2,codeId,codeName,col5,codeCategory
  x ,  x , x , "01" , "Bật"  ,  x ,  "10"
  x ,  x , x , "02" , "Tắt"  ,  x ,  "10"
  x ,  x , x , "01" , "Nóng" ,  x ,  "20"

→ $mapData sau khi xử lý:
[
  "10" => ["01" => "Bật", "02" => "Tắt"],
  "20" => ["01" => "Nóng"],
]

→ serialize($mapData) ghi vào code_map_data.txt (chuỗi PHP serialize, không phải JSON)
```

**Đã tra cả 2 phía để xác định CSV gốc là loại code nào, không xác định được:**
- Glob `**/*.csv` trên toàn `legacy_eminel_docs` (cả `docs/` và `sources/`) → 0 kết quả, không có file
  CSV mẫu nào để đối chiếu trực tiếp.
- `docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/補足資料/機器種別一覧.txt` — đọc
  thẳng bị lỗi encoding (Shift-JIS), đã decode lại (codepage 932): là danh sách 17 mã `機器種別`
  (device_type) → 1 tên tiếng Nhật/mã, **không có tầng "category"** → cấu trúc không khớp 3 cột mà
  batch này cần, xác nhận **không phải** CSV input của batch này.
- `14_コンシェルジェSV_詳細設計書別紙_EPC一覧.docx` và `.xlsx` (tên gần giống nhất còn lại) — vẫn là
  file binary, chưa đọc được nội dung.

### A.2.3 Logic dựng map (per dòng CSV)

1. Không đọc/ghi DB, không transaction, không dùng hằng số nào từ `config/const.php`.
2. Toàn bộ input nạp vào RAM (`$mapData`) trước khi ghi 1 lần — không streaming.
   (`MakeCodeMapDataCommand.php:35-41,54`)
3. Không xử lý lỗi dữ liệu (dòng thiếu cột, trùng khóa tự ghi đè do là associative array) — không
   validate/log cảnh báo.

### A.2.4 Ghi kết quả — file `code_map_data.txt`

- Đường dẫn tùy chỉnh hoặc mặc định `config/code_map_data.txt`, nội dung là chuỗi PHP `serialize()`
  của `$mapData` (định dạng riêng của PHP, không phải JSON/CSV). (`MakeCodeMapDataCommand.php:43,54`)
- Có hỏi xác nhận qua console nếu file đích đã tồn tại — chỉ chạy được ở môi trường có TTY tương tác,
  không tự động hóa được nếu không có cờ bỏ qua prompt. (`MakeCodeMapDataCommand.php:44-52`)
- Grep toàn bộ `sources/eminelsv-develop` và chuỗi `code_map_data`/`codeMapData`/`CODE_MAP` trên toàn
  `sources/` — không tìm thấy chỗ nào đọc lại file này. *(suy đoán: có thể tiêu thụ ngoài repo, hoặc là
  công cụ hỗ trợ vận hành/migrate 1 lần, không có consumer runtime)*.

### A.2.5 Điểm đặc biệt / Rủi ro

- Utility CLI chạy tay, có tương tác console (giống `HashPasswordCommand`) — khác hẳn batch định kỳ.
- Định dạng output PHP `serialize()` — không portable sang Node.js/TypeScript nếu không viết lại
  parser, hoặc đổi hẳn sang JSON khi port.
- Chưa xác định được ý nghĩa nghiệp vụ thật của CSV input — cần hỏi người nắm nghiệp vụ trước khi
  quyết định port.

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

## Đã kiểm tra (không tìm thấy gì cùng bản chất, nên không có bảng B.1/B.2)

| Khu vực/candidate đã tra | Vì sao không khớp |
|---|---|
| Grep `code.?map` / `code_map_data` / `codeMapData` / `CODE_MAP` / `serialize` / `mapData` trên toàn `src/` | Không có kết quả liên quan. 2 trùng khớp `code.?map` chỉ là `.map()` của Array (`services/noritz.ts:386`) và 1 interface phân loại tòa nhà `CntrClsfyCodeMap` (`business-logic/get-building-type-of-contract.ts:18`) — không phải "code map" theo nghĩa nghiệp vụ. |
| `resource/database/master/*.json` + `resource/database/master/0000000.sh` | File JSON viết tay chứa sẵn payload `PutRequest` để `aws dynamodb batch-write-item` — seed tĩnh, không sinh từ CSV nào (`0000000.sh:4-19`). |
| `src/functions/api-device-master/*` | Chỉ CRUD get/update trên bảng `DeviceMaster` có sẵn (`app.ts:9-17`), không có import CSV. |
| `src/functions/batch-common-read-csv/app.ts` (dùng chung bởi các batch `if20*-import-*`, `dm1040-import-*`) | Đọc CSV thật nhưng map theo danh sách **tên cột cố định** cho từng loại file Xzilla (`LIST_COL_IF2016`,...`app.ts:24-121`), ghi ra S3 dạng JSON — khác cơ chế đọc **theo vị trí cột** generic của batch cũ. Đây là import dữ liệu nghiệp vụ cụ thể (hợp đồng/khách hàng/thiết bị), không phải công cụ sinh code-map. |
| `src/functions/api-device/import-device-error-master.ts` | Đọc CSV theo tên cột tiếng Nhật cố định cho 1 loại master cụ thể (lỗi thiết bị), **ghi vào DB** — không xuất file, khác bản chất với batch cũ (đọc CSV → xuất file, không đụng DB). |

**Kết luận:** không có gì trong EMINEL-smart làm đúng việc "CSV bất kỳ → build map mã/tên theo vị trí
cột, generic cho nhiều danh mục → xuất ra file". Hệ thống mới xử lý "quản lý mã/tên" theo hướng khác
hẳn: build riêng 1 bộ API CRUD (+import CSV theo schema cố định) cho từng loại master cụ thể (ví dụ
`device-error-master`), ghi thẳng vào DynamoDB — không có công cụ generic đọc-CSV-xuất-file như
`MakeCodeMapDataCommand`.

---

## Tổng kết

Không có — bản cũ chỉ có 1 luồng xử lý (không nhánh/thuật toán song song), và hệ thống mới **không tìm
thấy gì cùng bản chất** để đối chiếu (không phải trường hợp "thay bằng cơ chế khác") — đoạn "Kết luận"
cuối Phần B đã đúc kết đủ.

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/eminelsv-develop/src/Command/MakeCodeMapDataCommand.php` |
| Hệ thống cũ | Cron (xác nhận không có) | `docs/02_詳細設計/10_バッチ処理/webap_cron設定_20240905.txt`, `mng-webap_cron設定_20241029.txt` |
| Hệ thống cũ | Tài liệu liên quan đã đọc (không khớp) | `docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/補足資料/機器種別一覧.txt` |
| Hệ thống cũ | Tài liệu liên quan chưa đọc được (binary) | `14_コンシェルジェSV_詳細設計書別紙_EPC一覧.docx` / `.xlsx` |
| Hệ thống mới | Ứng viên gần nhất đã kiểm tra | `src/functions/api-device/import-device-error-master.ts`, `src/functions/batch-common-read-csv/app.ts`, `src/functions/api-device-master/*`, `resource/database/master/0000000.sh` |
