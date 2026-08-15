# SendAlertLogMailCommand（アラートログメール送信）

## Tóm tắt

`SendAlertLogMailCommand` là batch chạy mỗi 5 phút trong hệ thống cũ (`conciergesv`, nhóm `mng-webap`),
đọc file log cấp `alert` mà các batch/xử lý khác trong cùng repo ghi ra khi thất bại, lọc tối đa 10
dòng mới nhất trong 5 phút gần nhất, gửi 1 email cảnh báo qua `mb_send_mail()`. Trong
`syp-eminelstandard-backend` (EMINEL-smart), chức năng này **đã có, tương đương — và bao phủ rộng hơn**,
nhưng bằng kiến trúc hoàn toàn khác: **CloudWatch Logs Subscription Filter (event-driven) + SNS** thay
cho cron quét file + gửi mail trực tiếp, áp dụng cho gần như mọi batch Lambda + Step Functions, có thêm
bước lọc nhiễu và phân loại tiêu đề mail mà bản cũ không có.

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `SendAlertLogMailCommand` · Script cron: `32_SendAlertLogMail.sh` · Tên tiếng Nhật trong cron: `32 アラートメール送信`. |
| **Vai trò** | Gom log cấp `alert` do các batch/xử lý khác ghi ra khi lỗi nghiêm trọng, gửi email cho người vận hành — cơ chế cảnh báo tập trung cho toàn `conciergesv`. |
| **Input** | Đọc file log `{Ymd}_alert.log` trong `LOGS` (và file ngày hôm trước nếu chạy ngay sau 0h). Không đọc DB, không gọi API ngoài. Có option `--datetime` (mặc định `now`). |
| **Output** | Gửi email qua `mb_send_mail()` tới các địa chỉ trong env `ALERT_LOG_MAIL_TO`. Không ghi DB, không ghi file. |
| **Khái quát xử lý** | 1. Xác định mốc thời gian xử lý.<br>2. Xác định file log cần đọc (hôm nay, cộng thêm hôm trước nếu vừa qua 0h).<br>3. Nếu cả 2 file không tồn tại → dừng.<br>4. Đọc + nối nội dung 2 file (nếu có).<br>5. Lọc dòng có timestamp trong `[mốc − 5 phút, mốc]` và chứa `'alert:'`, quét từ cuối lên, tối đa 10 dòng.<br>6. Không có dòng khớp → dừng.<br>7. Gửi 1 email chứa các dòng tìm được tới toàn bộ địa chỉ hợp lệ. |

## A.2 Chi tiết

### A.2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `*/5 * * * *` — mỗi 5 phút | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:122-123` |
| Tham số dòng lệnh | `--datetime` (tùy chọn, mặc định `'now'`) — mốc "thời điểm chạy batch", dùng để test/chạy lại. | `SendAlertLogMailCommand.php:26,31` |
| Xử lý mốc nửa đêm | Nếu `(mốc − 5 phút)` khác ngày với mốc → đọc thêm file `_alert.log` ngày hôm trước, nếu tồn tại. | `SendAlertLogMailCommand.php:40-48` |

### A.2.2 Nguồn dữ liệu — file log `{Ymd}_alert.log`

- File này **không do `SendAlertLogMailCommand` ghi ra** — CakePHP Log scope `alert` ghi tự động, cấu
  hình sẵn ở `config/app.php:427-434`: mọi lời gọi log level `alert` trong toàn ứng dụng
  (`Log::write('alert', ...)`/`$this->log($msg, 'alert')`) được `FileLog` ghi vào
  `{ngày hiện tại Ymd}_alert.log` trong `LOGS`.
- **Cập nhật độ chính xác** (lần audit trước chỉ grep chuỗi `'alert'` có dấu nháy, bỏ sót cách gọi qua
  hằng số PSR-3 `LogLevel::ALERT`): grep cả 2 cách gọi (`'alert'` VÀ `LogLevel::ALERT`) trên toàn
  `conciergesv-develop/src` ra **34 file**, không phải 8 như ghi trước đây — gồm hầu hết nhóm
  `Calc*Command` (10 phút/ngày/tháng/năm), `Delete*Command`, `CreateCsvAndZip*Command`,
  `RcvCntctCancellationCommand`, `RankingCreationCommand`, `CreateGroupSummaryCommand`,
  `CreateTablePartitionCommand`, `WatchNotificationCommand` (xem `WatchNotification.md`), `PutLogFileCommand`,
  `CreateZipsTrait`, và chính `SendAlertLogMailCommand`. Tức là cơ chế cảnh báo `alert` bao phủ **gần
  như toàn bộ batch nghiệp vụ chính của `conciergesv`**, không chỉ nhóm xóa/CSV/Xzilla như tài liệu yêu
  cầu ban đầu mô tả — tài liệu yêu cầu (mục dưới) có thể đã lỗi thời hoặc chỉ mô tả phạm vi tối thiểu lúc
  viết, thực tế code đã mở rộng thêm nhiều Command khác.
- Định dạng dòng được nhận diện: timestamp `YYYY-MM-DD HH:MM:SS` ở đầu dòng + chứa `'alert:'`.
  (`SendAlertLogMailCommand.php:81-87,162-168`)

**Tài liệu yêu cầu nghiệp vụ liên quan** (`docs/02_詳細設計/09_アラート/アプリケーションベース/
システムアラート/`, 2 file `.txt` bị lỗi encoding khi đọc thẳng, đã decode Shift-JIS/codepage 932):

- `北ガスEMINELシステムアラートメールの要件概要.txt` — khớp hoàn toàn với code: người nhận cấu hình
  qua env, hỗ trợ nhiều địa chỉ; tiêu đề `EMINELシステムアラート`; tần suất 5 phút/lần; tối đa 10
  dòng/mail. Tài liệu còn ghi rõ 2 mục "đang xem xét bổ sung" (積算バッチの失敗 = lỗi batch tích lũy,
  lỗi nghiêm trọng do thiếu dữ liệu user). Sau khi grep lại đầy đủ hơn (34 file, xem trên) — mục "lỗi
  batch tích lũy" **đã được code hóa**: nhóm `Calc*Command` (10 phút/ngày/tháng/năm) đều gọi log
  `alert` khi lỗi. Mục "lỗi nghiêm trọng do thiếu dữ liệu user" **vẫn chưa xác nhận được** — không có
  Command nào tên gợi ý rõ điều này trong danh sách 34 file.
- `斉藤メモ.txt` — mô tả thuật toán chi tiết (dò từng phút lùi dần tối đa 5 phút, dừng khi đủ 10 dòng
  hoặc hết 5 phút); code hiện tại hiện thực cùng ý tưởng bằng so sánh khoảng thời gian trực tiếp, đơn
  giản và tương đương kết quả.

### A.2.3 Logic lọc & giới hạn log (`sliceRecentAlertLogs`)

1. Quét ngược từ dòng cuối file lên (log mới nhất trước).
2. Bỏ dòng nếu: không parse được timestamp, HOẶC timestamp ngoài `[mốc − 5 phút, mốc]`.
3. Trong số còn lại, chỉ giữ dòng chứa `'alert:'`.
4. Dừng khi đủ 10 dòng (giới hạn cứng, literal trong code). (`SendAlertLogMailCommand.php:64,72-96`)
5. Không dùng hằng số nào từ `config/const.php` — mọi tham số là literal trong code.

### A.2.4 Ghi kết quả — gửi mail qua `mb_send_mail()`

- Người gửi: env `ALERT_LOG_MAIL_FROM`. Người nhận: env `ALERT_LOG_MAIL_TO` (phân tách `,`, validate
  từng địa chỉ; không hợp lệ bị loại + ghi log `alert`; hết địa chỉ hợp lệ → `RuntimeException`).
  (`SendAlertLogMailCommand.php:98-133`)
- Tiêu đề cố định `"EMINELシステムアラート"`; nội dung `"アラート内訳:\n\n"` + các dòng log.
  (`SendAlertLogMailCommand.php:69,144-146`)
- `mb_send_mail()` (PHP native, qua sendmail/SMTP hệ thống) — không queue, không retry, không
  transaction. Lỗi 1 địa chỉ → ghi log `alert`, tiếp tục gửi địa chỉ còn lại. (`SendAlertLogMailCommand.php:151-155`)

### A.2.5 Điểm đặc biệt / Rủi ro

- **Mắt xích cuối của 1 cross-cutting concern** (logging cấp `alert`) trải trên nhiều Command khác —
  muốn port đúng chức năng phải xác định toàn bộ nơi phát sinh log `alert` ở hệ thống mới trước, không
  chỉ port riêng file này.
- Batch chạy trễ/bỏ lỡ 1 lần (server down >5 phút) → log trong khoảng bị bỏ lỡ **không được gửi mail
  bù**, vì cửa sổ quét chỉ nhìn lùi đúng 5 phút, không theo dõi "đã gửi tới đâu".
- Gửi mail bằng `mb_send_mail()` — phụ thuộc mail server cấu hình ở OS, không dùng dịch vụ mail ngoài
  (SES, SendGrid...) — điểm cần đổi hẳn cách làm khi port sang serverless.

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

## B.1 Tên batch & vị trí trong code

| Cơ chế | Vị trí (Lambda) | State Machine / trigger | Nguồn dữ liệu | Đích |
|---|---|---|---|---|
| Tổng hợp & thông báo lỗi log | `src/functions/push-notification-error-log/app.ts` | **Không phải batch cron** — Lambda giám sát, trigger bởi `AWS::Logs::SubscriptionFilter` gắn trên log group của gần như mọi Lambda `batch-*` + `LogGroupStateMachine` (Step Functions) | CloudWatch Logs (log event của các Lambda/state machine khác) | `PublishCommand` tới `AWS::SNS::Topic` (`SnsTopic`) |

| Mục | Nội dung |
|---|---|
| Cách trigger | `AWS::Logs::SubscriptionFilter` — CloudWatch gọi Lambda ngay khi có dòng log mới khớp `FilterPattern` (event-driven, không phải cron/polling). Ví dụ: `template.yaml:334-340` (state machine), `template.yaml:1040-1046` (1 batch cụ thể). |
| Phạm vi bao phủ (đếm thật, không ước lượng) | Grep `FilterPattern:` trong `template.yaml`: **77 resource** dùng `FilterPattern: 'ERROR'` (gắn trên từng Lambda `batch-*` riêng lẻ), **1 resource** dùng `FilterPattern: 'error'` (gắn trên `LogGroupStateMachine`, log group chung của mọi Step Functions execution) — tổng 78 subscription filter, tất cả trỏ `DestinationArn` về cùng 1 `PushNotificationErrorLogFunction`. |
| Helper log lỗi dùng trong nhiều batch | `src/layers/common/nodejs/business-logic/log-error-batch.ts` — `logErrorBatch()`, dùng ví dụ ở `batch-common-read-csv/app.ts:1,151` (gọi trước khi `throw`, để Lambda runtime tự log "ERROR..." khớp filter pattern). |

## B.2 Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Nhận log lỗi từ CloudWatch (mọi batch/state machine có gắn subscription filter), lọc nhiễu, phân loại, gửi thông báo cho vận hành qua SNS. |
| **Input** | Payload log event từ CloudWatch Logs (gzip + base64), decode → JSON gồm `logGroup`, `logStream`, `logEvents[]`. |
| **Output** | `PublishCommand` tới `AWS::SNS::Topic` (`SnsTopic`, `template.yaml:306-309`) — subscriber thật (email/khác) **không thấy khai báo trong `template.yaml` này**, khả năng quản lý ngoài IaC. *(suy đoán, chưa xác minh được subscriber thật)* |
| **Khái quát xử lý** | 1. Nhận & decode log event từ CloudWatch.<br>2. Loại bỏ log khớp `retryErrors` (16 loại lỗi tạm thời/network — `ResourceNotFoundException`, `RequestTimeout`, `SlowDown`,...) và `ignoredErrors` (`'Global error listener:'`).<br>3. Phân nhóm còn lại theo `logGroup`: `STATE_MACHINE_ERROR` (nếu log group chứa `'LogGroupStateMachine'`) / `DEVICE_ERROR_MASTER_NOT_FOUND` (nếu message chứa message code tương ứng) / `ERROR` (còn lại, mặc định).<br>4. Với mỗi nhóm có nội dung, publish 1 message SNS riêng, tiêu đề theo nhóm (`MAIL_SUBJECT_NOTIFICATION.*`, `constants.ts:215-219`: `ERROR`="バッチ停止エラーの通知", `STATE_MACHINE_ERROR`="ステートマシン停止エラーの通知", `DEVICE_ERROR_MASTER_NOT_FOUND`="機器エラーマスタ未存在通知"). |

**So với bản cũ**: có thêm bước lọc nhiễu (bản cũ gửi mọi dòng `alert:` không phân biệt loại lỗi), phân
loại theo 3 tiêu đề riêng (bản cũ 1 tiêu đề cố định `EMINELシステムアラート`), phạm vi bao phủ theo
**từng Lambda riêng** qua subscription filter (bản cũ giới hạn ở 34 Command tự ghi log `alert`, phải sửa
code mỗi khi thêm 1 nguồn cảnh báo mới — hệ thống mới chỉ cần thêm 1 `SubscriptionFilter` trong IaC),
không giới hạn số dòng/mail (bản cũ cứng 10 dòng).

---

## Tổng kết

**Không phải bản port trực tiếp cùng cơ chế — mà là thay hẳn cách "phát hiện + báo lỗi" bằng 1 lớp hạ
tầng khác về chất, đồng thời mở rộng phạm vi bao phủ:**

- **Cách phát hiện nguồn lỗi**: bản cũ là **opt-in thủ công trong code** — mỗi Command muốn được cảnh
  báo phải tự gọi `$this->log($msg, 'alert')` (34 Command đã làm vậy, đếm thật qua grep, xem A.2.2);
  quên gọi = im lặng không báo. Bản mới là **opt-out qua hạ tầng** — mọi Lambda `batch-*` + state
  machine đã có sẵn `AWS::Logs::SubscriptionFilter` trỏ về cùng 1 Lambda giám sát (78 filter, đếm thật
  qua grep `FilterPattern:` trong `template.yaml`, xem B.1) — chỉ cần Lambda tự log ra `"ERROR..."` khớp
  pattern là được bắt, không cần biết tới khái niệm "alert log" nào cả.
- **Chu kỳ phát hiện**: bản cũ là cron quét file mỗi 5 phút (có cửa sổ mù nếu server down >5 phút, xem
  A.2.5); bản mới event-driven theo từng dòng log thật, không có khái niệm "cửa sổ quét".
- **Xử lý trước khi báo**: bản cũ gửi thẳng, không lọc theo loại lỗi; bản mới có bước loại bỏ lỗi tạm
  thời/network (`retryErrors`, 16 loại) trước khi báo — giảm nhiễu mà bản cũ không làm được vì chỉ đơn
  giản là gom dòng log, không phân tích nội dung lỗi.
- **Định tuyến thông báo**: bản cũ 1 tiêu đề mail cố định cho mọi loại lỗi; bản mới phân 3 nhóm
  (`ERROR`/`STATE_MACHINE_ERROR`/`DEVICE_ERROR_MASTER_NOT_FOUND`) với tiêu đề riêng từng nhóm.

**Đánh đổi — được gì, mất gì, và phần chưa xác minh được:**

- Được: phạm vi bao phủ rộng hơn nhiều (78 Lambda/state machine so với 34 Command), không cần sửa code
  ứng dụng để thêm 1 nguồn cảnh báo mới (chỉ cần thêm resource IaC), không còn giới hạn cứng 10 dòng/mail.
- Mất/khác: kênh nhận tin đổi từ email trực tiếp (`ALERT_LOG_MAIL_TO` khai báo rõ trong `.env`) sang SNS
  — **subscriber thật của `SnsTopic` không thấy khai báo trong `template.yaml` đã đọc** *(suy đoán: có
  thể cấu hình ngoài IaC hoặc ở service khác chưa đọc tới — chưa xác minh được ai/kênh nào thực sự nhận
  được thông báo cuối cùng)*, khác bản cũ nêu rõ ràng người nhận ngay trong code.
- Cơ chế "mất log nếu batch chạy trễ" ở bản cũ (server down >5 phút → khoảng đó không được gửi bù)
  **không còn áp dụng theo cùng cách** ở bản mới vì không dựa vào quét file theo chu kỳ nữa — nhưng rủi
  ro tương đương ở tầng CloudWatch/Lambda (throttle, lỗi invoke Lambda giám sát) chưa được xác minh trong
  phạm vi audit này.

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/conciergesv-develop/src/Command/SendAlertLogMailCommand.php` |
| Hệ thống cũ | Cấu hình Log scope `alert` | `sources/conciergesv-develop/config/app.php:427-434` |
| Hệ thống cũ | Env mail from/to | `sources/conciergesv-develop/config/.env.prod:73,76` |
| Hệ thống cũ | Lịch chạy (cron) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:122-123` |
| Hệ thống cũ | Tài liệu yêu cầu nghiệp vụ | `docs/02_詳細設計/09_アラート/アプリケーションベース/システムアラート/北ガスEMINELシステムアラートメールの要件概要.txt`, `.../斉藤メモ.txt` |
| Hệ thống mới | Logic Lambda tổng hợp | `src/functions/push-notification-error-log/app.ts` |
| Hệ thống mới | Subscription filter (ví dụ + đếm tổng) | `template.yaml:334-340`, `:1040-1046`, đếm `FilterPattern:` toàn file |
| Hệ thống mới | SNS Topic | `template.yaml:306-309` |
| Hệ thống mới | Tiêu đề mail theo nhóm | `src/layers/common/nodejs/variables/constants.ts:215-219` |
| Hệ thống mới | Helper log lỗi dùng trong batch | `src/layers/common/nodejs/business-logic/log-error-batch.ts` |
