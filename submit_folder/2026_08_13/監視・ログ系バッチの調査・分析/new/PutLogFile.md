# PutLogFileCommand（ログファイル出力）

## Tóm tắt

`PutLogFileCommand` là batch cron chạy 1 lần/ngày (00:00) trên server `conciergesv`, thuộc chức năng
"アプリログ送信機能(to Xzilla)" — gom các file `.zip` log app di động (do app upload lên qua API
`GetLogFileController` và được copy sẵn vào thư mục `APP_LOG_SAVE_DIR_PATH/xzilla/`) có tên khớp ngày
cần xử lý, giải nén, validate format từng file `.tsv` bên trong (dòng đầu là header, các dòng sau phải
bắt đầu bằng ngày `YYYY/MM/DD`), rồi SFTP PUT các file `.tsv` hợp lệ ra một server ngoài thuộc hệ thống
liên kết Xzilla, sau đó dọn file/folder tạm ở local. Ở repo mới `syp-eminelstandard-backend`, không tìm
thấy Lambda hay cơ chế nào tương đương: không có biến môi trường, secret, hay code nào liên quan tới
`XZILLA_RELATION_SERVER_HOST`/`PUT_LOG_TARGET_DIR_PATH`, và các batch SFTP gần giống nhất
(`batch-export-kyutoki-*`, `batch-export-sekigaisen-rimokon`, `batch-forward-csv-from-sftp-server-to-s3`)
đều khác bản chất — chúng generate dữ liệu mới từ DB hoặc đi chiều ngược (nhận file từ 基幹 (xzilla/DWH)
vào S3), không phải đọc lại file zip log app đã có sẵn để giải nén/validate/gửi ra Xzilla. Chức năng "gửi log
app cho Xzilla" dường như chưa được port sang hệ thống mới.

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class/Command: `PutLogFileCommand` · Server: `conciergesv` · Script cron: `31_PutLogFile.sh` · Tên tiếng Nhật trong cron: "アプリログ送信機能(to Xzilla)" (chức năng gửi log app tới Xzilla). Tên lệnh CLI không được override rõ ràng trong `Application.php` (không tìm thấy đăng ký tên riêng) — theo quy ước CakePHP, tên lệnh tự sinh từ tên class (bỏ hậu tố `Command`, chuyển snake_case). |
| **Vai trò** | Đẩy log hoạt động của app di động (được app upload lên server qua API riêng) ra hệ thống liên kết ngoài "Xzilla" qua SFTP, theo lịch hàng ngày. |
| **Input** | Đọc file `.zip` có sẵn trong thư mục local `env('APP_LOG_SAVE_DIR_PATH') . 'xzilla' . DS`, lọc theo ngày filter (mặc định hôm qua) dựa trên phần ngày trong tên file. Không đọc DB. |
| **Output** | SFTP PUT các file `.tsv` (giải nén từ zip, đã validate) lên server ngoài tại `env('PUT_LOG_TARGET_DIR_PATH')`. Không ghi DB. Sau khi upload xong 1 zip: xóa folder giải nén tạm + xóa file zip local nguồn. |
| **Khái quát xử lý** | 1. Xác định ngày filter (tham số `--datetime` hoặc hôm qua). 2. Liệt kê file `.zip` local trong thư mục `xzilla`; không có file nào → alert + kết thúc sớm. 3. Kết nối SFTP bằng private key (chỉ khi có file). 4. Với mỗi zip khớp ngày filter (parse từ tên file): giải nén ra thư mục tạm hệ thống. 5. Với mỗi `.tsv` trong đó: validate format, rồi SFTP PUT nếu hợp lệ. 6. Dọn thư mục tạm + xóa zip local sau khi xử lý xong 1 zip. |

## A.2 Chi tiết

### A.2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `00 00 * * *` — 1 lần/ngày lúc 00:00, comment "#31.アプリログ送信機能(to Xzilla)" | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:119-120` |
| Tham số dòng lệnh | `--datetime` (mặc định `'now'`) — cho phép chỉ định ngày filter cần xử lý thay vì hôm qua | `sources/conciergesv-develop/src/Command/PutLogFileCommand.php:20-25` |
| Mốc thời gian tính | Nếu `--datetime` không truyền hoặc = `'now'` → lấy hôm qua (`FrozenTime::now()->subDays(1)`); ngược lại parse chuỗi truyền vào. Mốc thời gian được format `Ymd` để dùng làm filter so khớp tên file | `PutLogFileCommand.php:30-39` |

### A.2.2 Nguồn dữ liệu — file zip log app, được sinh ra bởi API khác (không phải batch này)

Batch **không tự tạo** ra file zip mà chỉ đọc file đã có sẵn. Chuỗi sinh dữ liệu thực tế:

1. App di động gọi API `GetLogFileController::index()` (route "ログ送信API") để upload file log (`.zip`), kèm `send_time`, `id` (EMS-SP), `uuid` trong request.
2. Controller lưu file vào 2 nơi cùng lúc:
   - Thư mục theo tháng: `env('APP_LOG_SAVE_DIR_PATH') . {Ym} . DS` (`GetLogFileController.php:50,53`)
   - Thư mục `xzilla`: `env('APP_LOG_SAVE_DIR_PATH') . 'xzilla' . DS` (`GetLogFileController.php:56,81`)
   - Tên file: `"{emsSp}_{sendTime:YmdHisv}_{uuid}.zip"` (`GetLogFileController.php:76`)
3. `PutLogFileCommand` sau đó `glob()` toàn bộ `*.zip` trong thư mục `xzilla` này (`PutLogFileCommand.php:50`), tách tên file theo `_` để lấy phần ngày (`substr($fileNameParts[1], 0, 8)`, tức 8 ký tự đầu của đoạn `YmdHisv`) và lọc đúng ngày filter (`PutLogFileCommand.php:66-75`).

Nguồn: `sources/conciergesv-develop/src/Controller/GetLogFileController.php:27-94`, `sources/conciergesv-develop/src/Command/PutLogFileCommand.php:49-75`.

Không có Command nào khác trong `conciergesv-develop/src/Command/` hay service dùng chung nào trong
`eminel_sv_lib-develop/src/` tạo file zip vào thư mục `xzilla` này — đã grep "xzilla" trên toàn bộ 2 cây
mã nguồn, chỉ có `GetLogFileController` (API) là nơi ghi vào thư mục đó.

### A.2.3 Validate & gửi file — kiểm tra format TSV, SFTP PUT tới Xzilla

1. Với mỗi file zip khớp ngày filter, giải nén bằng `ZipArchive` ra `sys_get_temp_dir()/{tên file không đuôi}` (`PutLogFileCommand.php:78-86`). Nếu mở zip thất bại → log `alert` "ZIPファイル解凍失敗" và bỏ qua file đó, tiếp tục file zip khác (`:83-85`).
2. Lấy toàn bộ `*.tsv` trong thư mục giải nén (`:88`).
3. Với mỗi file `.tsv`, validate bằng `validateTsvFile()` (`:94, 125-152`):
   - Đọc dòng đầu tiên và bỏ qua (coi là header, không kiểm tra) (`:135`).
   - Từ dòng thứ 2, MỌI dòng — kể cả dòng trắng, vì nhánh skip 空行 (`:139-141`) thực tế không kích hoạt (`fgets` trả `"\n"`, không rỗng theo `empty()`) — phải khớp regex `^\d{4}\/\d{2}\/\d{2}` (bắt đầu bằng ngày dạng `YYYY/MM/DD`); nếu 1 dòng bất kỳ không khớp → toàn file bị coi là không hợp lệ, dừng kiểm tra ngay (`break`); TSV chứa dòng trắng giữa file cũng bị coi là không hợp lệ (`:137-147`).
   - File không hợp lệ → log `notice` "不正な TSV ファイル" và **skip riêng file đó** (không phải toàn zip) (`:95-96`).
4. File hợp lệ → SFTP PUT lên `env('PUT_LOG_TARGET_DIR_PATH') . DS . {tên file}` (`:100`).
   - Nếu PUT thất bại: log `alert` "ファイルアップロード失敗", xóa toàn bộ thư mục giải nén tạm của zip đang xử lý, rồi **`continue 2`** — bỏ hẳn zip hiện tại (không xóa file zip local nguồn, không tiếp tục các `.tsv` còn lại trong zip đó) và chuyển sang zip kế tiếp (`:100-107`).
5. Nếu tất cả `.tsv` trong zip xử lý xong (dù có file bị skip vì không hợp lệ) mà không có lỗi PUT nào: xóa thư mục giải nén tạm + xóa file zip local nguồn (`:110-115`).

**Hằng số nghiệp vụ**: không có hằng số nào (không dùng `Configure::read`/`self::CONST`); toàn bộ tham
số kết nối/đường dẫn lấy trực tiếp từ biến môi trường — đã xác nhận không có định nghĩa liên quan trong
`config/const.php` (grep case-insensitive "xzilla"/"log_file"/"log_save" không ra kết quả).

Giá trị các biến `env()` theo từng môi trường:

| Biến | .env.dev | .env.local | .env.prod | .env.stage |
|---|---|---|---|---|
| `APP_LOG_SAVE_DIR_PATH` | `/var/data/AppOpeLog/` (dòng 47) | dòng 46 | dòng 47 | dòng 47 |
| `PUT_LOG_TARGET_DIR_PATH` | `./EMN/` (dòng 46) | `/var/www/vhost/conciergesv/tmp/EMN/` (dòng 45) | `./EMN/` (dòng 46) | `./EMN/` (dòng 46) |
| `XZILLA_RELATION_SERVER_HOST` | `localhost` (dòng 51) | `localhost` (dòng 50) | `kglip111.kitagas-aws.local` (dòng 51) | `kglip015.kitagas-aws.local` (dòng 51) |
| `XZILLA_RELATION_SERVER_PORT` | `22` (dòng 52) | `22` (dòng 51) | `52996` (dòng 52) | `52996` (dòng 52) |
| `XZILLA_SEND_SFTP_USER` | `ec2-user` (dòng 60) | `vagrant` (dòng 59) | `sftpemn2` (dòng 60) | `sftpemn2` (dòng 60) |
| `XZILLA_SEND_SFTP_SECRET_KEY_PATH` | `/var/data/key/sftpemn2_id_rsa` (dòng 59) | dòng 58 | dòng 59 | dòng 59 |

Nguồn: `sources/conciergesv-develop/config/.env.dev`, `.env.local` (kèm comment dòng 57 "# Xzilla へ
データ送信するための設定" = "cấu hình để gửi dữ liệu tới Xzilla"), `.env.prod`, `.env.stage` — số dòng
như bảng trên trong từng file.

### A.2.4 Ghi kết quả — SFTP PUT ra server ngoài + dọn file local, không ghi DB

- Đích: file `.tsv` được PUT ra thư mục `PUT_LOG_TARGET_DIR_PATH` trên server SFTP ngoài (`XZILLA_RELATION_SERVER_HOST`). Không có bảng DB đích — batch này không tương tác DB.
- Không dùng transaction DB. Đơn vị an toàn là theo **zip file**: nếu PUT 1 file trong zip lỗi, toàn bộ phần còn lại của zip đó (kể cả các `.tsv` khác chưa xử lý) bị bỏ qua bằng `continue 2`, file zip local vẫn giữ nguyên (không bị xóa) để có thể chạy lại lần sau; zip khác trong cùng lượt chạy không bị ảnh hưởng.
- Batch không tự kích hoạt batch khác, không có batch nào đọc lại kết quả của nó (đây là điểm cuối của luồng dữ liệu, đẩy ra hệ thống ngoài Xzilla).
- Cơ chế log lỗi (`$this->log(..., 'alert')`) là dùng chung toàn hệ thống: mọi Command gọi `alert` sẽ được ghi vào file `{Ymd}_alert.log` trong `LOGS` dir, và được `SendAlertLogMailCommand` quét + gửi mail cảnh báo mỗi 5 phút — đây KHÔNG phải cơ chế riêng của `PutLogFileCommand`, chỉ là 1 trong nhiều Command dùng chung cơ chế alert-mail này (`sources/conciergesv-develop/src/Command/SendAlertLogMailCommand.php:33-35` đọc `{Ymd}_alert.log`; lịch quét mỗi 5 phút theo `mng-webap_cron設定_20241029.txt:122-123`).

### A.2.5 Điểm đặc biệt / Rủi ro

- Batch đọc file input do 1 **API khác** (`GetLogFileController`) tạo ra trước đó, không tự sinh dữ liệu — khi port cần đảm bảo có luồng tương đương ghi file/dữ liệu vào "hộp thư" trước khi batch gửi đi được kích hoạt, nếu không sẽ luôn rơi vào nhánh "không có file" (`PutLogFileCommand.php:52-55`, log `alert` "指定された日に該当するファイルがありません。" rồi `return` sớm — kết thúc bình thường (không abort), nhưng vì log ở mức `alert` nên vẫn kích hoạt mail cảnh báo qua `SendAlertLogMailCommand` (A.2.4): ngày không có log app nào cũng sẽ sinh mail cảnh báo).
- Lọc file theo tên (`substr($fileNameParts[1], 0, 8)`) phụ thuộc chặt vào định dạng tên file cố định `"{emsSp}_{YmdHisv}_{uuid}.zip"` sinh ra từ `GetLogFileController.php:76` — nếu định dạng tên file đổi ở phía tạo file mà không đổi theo ở đây, filter theo ngày sẽ sai lệch hoặc không khớp được file nào.
- File zip không đúng ngày filter bị `continue` bỏ qua vĩnh viễn trong lượt chạy đó nhưng **không bị xóa** — vẫn còn trên đĩa, đợi lượt chạy đúng ngày filter của nó (hoặc chạy tay bằng `--datetime`) mới được xử lý; nghĩa là cần đảm bảo cron chạy đủ, liên tục, nếu miss 1 ngày thì cần chạy tay bù bằng tham số `--datetime` vì batch không tự "gom bù" nhiều ngày trong 1 lần chạy.
- Thư mục giải nén tạm dùng `sys_get_temp_dir()` (không phải thư mục ứng dụng riêng) — nếu 2 file zip có cùng tên (không đuôi) tồn tại đồng thời (không nên xảy ra do tên có `uuid`) có thể ghi đè lẫn nhau; rủi ro thấp do tên file có UUID.

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

> Không tìm thấy Lambda/cơ chế nào tương đương về bản chất. Bảng dưới đây là các khu vực/candidate đã
> tra trong `src/functions/` và lý do không khớp (thay cho B.1/B.2).

## Đã kiểm tra

| Khu vực / candidate | Vì sao không khớp |
|---|---|
| Toàn bộ ~140 dòng / 45 file chứa từ khóa `xzilla` trong `src/functions/api-*`, `authorizer/app.ts`, `batch-if2241-import-tagtag-kaiin/app.ts`, `batch-update-selecting-place-no/app.ts`, `give-badge-after-xzilla-link.ts`, `models/Kaiin.ts` | Toàn bộ xoay quanh cờ `is_not_data_xzilla`/`checkIsNotDataXzilla` — kiểm tra member (kaiin) có liên kết dữ liệu qua Xzilla hay không, phục vụ authorization/business logic phía app. Khác hoàn toàn bản chất "xuất log ra Xzilla qua SFTP" của `PutLogFileCommand`. |
| `src/functions/batch-export-kyutoki-accumulated`, `-daily-usage`, `-device-property`, `-device-status-history`, `-monthly-usage`, `batch-export-sekigaisen-rimokon` | Có SFTP PUT thật (`src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts`, secret `sftp_server_info_eminel`, đích `/EST`), nhưng dữ liệu được **generate mới từ DB** (query thiết bị rồi convert CSV), không đọc lại file zip log app có sẵn, không có bước giải nén/validate TSV theo header+ngày. Đích thực tế của e-smart nằm trong secret, không xác định được từ code (nghi là cùng server Xzilla/DWH — đang chờ mui xác nhận); điểm khác bản chất nằm ở dữ liệu: CSV thiết bị generate từ DB ≠ đọc lại zip log app có sẵn để giải nén/validate/gửi — chỉ trùng ở mức kỹ thuật "SFTP PUT ra ngoài". |
| `src/functions/batch-forward-csv-from-sftp-server-to-s3`, `batch-get-list-file-name-from-sftp-server`, `batch-delete-data-temp-sftp` | Đi **chiều ngược lại**: đọc file `.dat` (IF2241/DM1040/IF2242/IF2016/IF2023/IF2024/IF2029/IF2223) TỪ SFTP server của 基幹 (xzilla/DWH) VÀO S3 để import, không phải gửi log app RA Xzilla — khác hướng dữ liệu; đối tác theo docs dự án chính là xzilla/DWH (`eminel_gw_project/docs/eminel-smart/02_product_overview.md:30,64`), nhưng loại dữ liệu và chiều khác hẳn nên vẫn không phải bản port của `PutLogFileCommand`. |
| Grep trực tiếp `XZILLA_RELATION_SERVER_HOST`, `PUT_LOG_TARGET_DIR_PATH`, `APP_LOG_SAVE_DIR_PATH` trên toàn `src/` | 0 kết quả — các biến env đặc thù của `PutLogFileCommand` không tồn tại trong repo mới. |

Không có dấu hiệu nào (code, biến môi trường, tên resource trong `template.yaml`) cho thấy chức năng
"gửi log app cho Xzilla qua SFTP" đã được port sang `syp-eminelstandard-backend`. Cũng không tìm thấy
API tương đương `GetLogFileController` (nhận log zip từ app) trong `src/functions/api-*` (không thuộc
phạm vi audit batch này, nhưng liên quan trực tiếp tới nguồn dữ liệu đầu vào nếu cần port cả 2 phía).

---

## Tổng kết

Không có — bản cũ chỉ có 1 luồng xử lý (không nhánh/thuật toán song song), và hệ thống mới **không tìm
thấy gì** để đối chiếu (không phải trường hợp "thay bằng cơ chế khác") — bảng "Đã kiểm tra" ở Phần B đã
nêu đủ lý do không khớp cho từng candidate.

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/conciergesv-develop/src/Command/PutLogFileCommand.php` |
| Hệ thống cũ | Nguồn sinh file input (API nhận log từ app) | `sources/conciergesv-develop/src/Controller/GetLogFileController.php` |
| Hệ thống cũ | Cơ chế alert-mail dùng chung (cross-cutting) | `sources/conciergesv-develop/src/Command/SendAlertLogMailCommand.php:33-35` |
| Hệ thống cũ | Biến môi trường / giá trị theo môi trường | `sources/conciergesv-develop/config/.env.dev`, `.env.local`, `.env.prod`, `.env.stage` |
| Hệ thống cũ | `config/const.php` (đã grep — không có hằng số liên quan) | `sources/conciergesv-develop/config/const.php` |
| Hệ thống cũ | Lịch chạy (cron) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:119-123` |
| Hệ thống cũ | Danh sách batch (mô tả tiếng Nhật, nhóm server) | `docs/03_API仕様/04_バッチ一覧.md:89` |
| Hệ thống cũ | Thuật ngữ Xzilla / To_Xzilla | `docs/用語集.md:19,84` |
| Hệ thống cũ | Mapping docs⇔sources (xác nhận không có dòng riêng cho batch này) | `README.md:113,157,161` |
| Hệ thống cũ | Tài liệu liên quan, chưa đọc được nội dung (binary) | `docs/02_詳細設計/06_情報共通基盤連携/To_Xzilla/アプリログ送信/アプリログ送信バッチ仕様書.xlsx`, `アプリログ取得API仕様書.xlsx` |
| Hệ thống mới | Kết quả grep/khảo sát `src/functions/` (không tìm thấy tương đương) | `src/functions/batch-export-kyutoki-*`, `batch-export-sekigaisen-rimokon`, `batch-forward-csv-from-sftp-server-to-s3`, `batch-get-list-file-name-from-sftp-server`, `batch-if2241-import-tagtag-kaiin`, `batch-update-selecting-place-no`, `authorizer/app.ts`, `give-badge-after-xzilla-link.ts`, `models/Kaiin.ts` |
| Hệ thống mới | Service SFTP dùng chung (không cùng bản chất) | `src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts` |
