# HashPasswordCommand（パスワードハッシュ生成・ユーティリティ）

## Tóm tắt

`HashPasswordCommand` là **CLI chạy thủ công** (không có lịch cron) trong `eminelsv`（新EMINELサーバ／
運用管理画面）của hệ thống cũ: hỏi mật khẩu qua console, hash bằng `Cake\Auth\DefaultPasswordHasher`
(cùng hasher `AdminUser` entity dùng để lưu mật khẩu), in kết quả ra console — dùng để tạo sẵn giá trị
hash, chèn tay vào DB khi cần tạo/reset mật khẩu admin mà không qua UI. Trong
`syp-eminelstandard-backend` (EMINEL-smart), chức năng này **không có, và không cần có**: việc tạo tài
khoản admin đi qua **AWS Cognito**, không còn cột `password` nào trong DB để cần hash — đây là thay đổi
kiến trúc có chủ đích, không phải thiếu sót khi port.

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `HashPasswordCommand` · Tên lệnh gọi: `hash_password` *(suy đoán theo quy ước CakePHP 4)* · **Không có lịch chạy — CLI chạy tay**. |
| **Vai trò** | Sinh chuỗi hash mật khẩu tương thích với cách `AdminUser` entity lưu mật khẩu, dùng thủ công khi cần tạo/reset tài khoản quản trị mà không qua UI. |
| **Input** | 1 chuỗi mật khẩu nhập qua prompt console lúc chạy lệnh — không tham số dòng lệnh, không đọc DB/file. |
| **Output** | In ra console (stdout) chuỗi hash. Không ghi DB, không ghi file, không gửi mail. |
| **Khái quát xử lý** | 1. Hỏi mật khẩu qua console (`$io->ask('Password?')`).<br>2. Nếu độ dài khác 0 → hash bằng `DefaultPasswordHasher::hash()` và in ra console.<br>3. Nếu để trống → không làm gì, kết thúc. |

## A.2 Chi tiết

### A.2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | **Không có.** Grep tên class trong cả 2 file cron, và trong toàn bộ shell script giải nén từ `cron実行用シェルスクリプト/*.tgz` (webap 20240905, mng-webap 20240909) — không có kết quả. | — |
| Tham số dòng lệnh | Không có — mật khẩu chỉ nhập qua prompt tương tác, không truyền qua argument (không lưu lịch sử shell). | `HashPasswordCommand.php:20` |

### A.2.2 Thuật toán hash

- Dùng `Cake\Auth\DefaultPasswordHasher` — thuộc framework CakePHP (`cakephp/cakephp: 4.4.*`), không
  nằm trong source repo này nên không trích dẫn được implementation cụ thể. *(Theo tài liệu công khai
  CakePHP — không xác minh được trong repo — mặc định dùng `password_hash()` với bcrypt; đây là suy
  đoán dựa trên kiến thức framework, không phải đọc trực tiếp từ source.)*
- Cùng hasher này được `AdminUser` entity dùng khi set mật khẩu:
  `(new DefaultPasswordHasher())->hash($password)` — `eminelsv-develop/src/Model/Entity/AdminUser.php:40`.
  → **Chắc chắn** (đọc trực tiếp code): output của `HashPasswordCommand` chèn thẳng được vào cột
  `password` của bảng `admin_users` (`AdminUsersTable.php:44`, `setTable('admin_users')`) — đích chèn
  tay thủ công, không phải luồng data tự động của batch.
- **Không cùng loại** với `EminelSvLib\StaticServices\PasswordEncoder`
  (`eminel_sv_lib-develop/src/StaticServices/PasswordEncoder.php`) — mô phỏng `StandardPasswordEncoder`
  của Spring Security (salt 8 byte + SHA-256 lặp 1024 lần), dùng cho 1 loại tài khoản/luồng khác, KHÔNG
  phải admin user của `eminelsv`. Nêu ra chỉ để tránh nhầm 2 cơ chế hash khác nhau trong cùng hệ sinh
  thái.

### A.2.3 Ghi kết quả — in ra console (`$io->out`)

- In thẳng ra console, không lưu lại đâu — người vận hành tự copy giá trị hash rồi chèn tay vào DB.
  (`HashPasswordCommand.php:22`)
- Không transaction, không side-effect nào khác ngoài in ra màn hình.

### A.2.4 Điểm đặc biệt / Rủi ro

- Utility CLI chạy tay, có tương tác console, giống `MakeCodeMapDataCommand` — không phải batch định kỳ.
- Không truyền được `password` qua argument → giảm rủi ro lộ mật khẩu qua shell history, nhưng cũng
  không thể tự động hóa/script hóa command này.
- Không có xác nhận nhập lại mật khẩu, không kiểm tra độ mạnh mật khẩu — validate (nếu có) nằm ở nơi
  khác (UI tạo/sửa admin user), ngoài phạm vi command này.

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

## B.1 Tên batch & vị trí trong code

| Cơ chế | Vị trí | Nguồn dữ liệu | Đích |
|---|---|---|---|
| Tạo tài khoản admin (thay thế hoàn toàn khái niệm "hash mật khẩu để chèn DB") | `src/functions/api-admin/create-admin.ts` — API, không phải batch | `email`, `admin_name`, `role` từ request | Gọi Cognito `AdminCreateUserCommand` tạo user; ghi record `Admin` trong DynamoDB (`email`, `admin_name`, `role`, `is_deleted` từ request; `admin_id` = attribute `sub` trích từ output Cognito) |

| Mục | Nội dung |
|---|---|
| Cách trigger | API Gateway request (admin bấm tạo tài khoản trong màn hình quản trị), có `checkRoleAdmin` — không phải batch cron. |

## B.2 Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Tạo/quản lý tài khoản admin qua Cognito, không tự lưu mật khẩu trong bảng `Admin`. |
| **Input** | `email`, `admin_name`, `role` — **không có field mật khẩu nào trong request**, khác hẳn bản cũ (nhập password trực tiếp). |
| **Output** | Ghi record `Admin` trong DynamoDB (`email`, `admin_name`, `role`, `is_deleted` từ request; `admin_id` = attribute `sub` trích từ `AdminCreateUserCommandOutput` của Cognito) — không có field password nào để hash. |
| **Khái quát xử lý** | 1. Check quyền admin người gọi (`checkRoleAdmin`).<br>2. Validate input (`email`,...).<br>3. Gọi Cognito `createUser(email)` — Cognito tự quản lý toàn bộ vòng đời mật khẩu (đặt lần đầu, reset, chính sách độ mạnh) ngoài phạm vi backend này.<br>4. Ghi record `Admin` trong DynamoDB.<br>5. Lỗi khi ghi DB → gọi `deleteUser(email)` xóa lại user Cognito vừa tạo (rollback thủ công, không phải DB transaction). |

**Xác nhận thêm — không có luồng đổi/reset mật khẩu admin nào trong backend này**: grep
`ForgotPassword`/`ResetPassword`/`ChangePassword`/`AdminSetUserPassword`/`AdminResetUserPassword` trên
toàn `src/` → 0 kết quả. Củng cố kết luận: toàn bộ vòng đời mật khẩu admin (tạo/đổi/reset) đều giao cho
Cognito xử lý phía ngoài backend, không có endpoint nào trong repo này chạm tới mật khẩu admin.

---

## Tổng kết

Không có — batch chỉ có 1 hành động đơn giản (hash 1 chuỗi theo yêu cầu, không nhánh/thuật toán song
song), và việc hệ thống mới thay hẳn bằng Cognito đã nêu đủ trong đoạn Tóm tắt đầu file; không có nhiều
điểm khác biệt cần đúc kết thêm.

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/eminelsv-develop/src/Command/HashPasswordCommand.php` |
| Hệ thống cũ | Xác nhận cùng hasher với AdminUser | `sources/eminelsv-develop/src/Model/Entity/AdminUser.php:35-41` |
| Hệ thống cũ | Bảng vật lý đích chèn tay (`admin_users`) | `sources/eminelsv-develop/src/Model/Table/AdminUsersTable.php:44` |
| Hệ thống cũ | Cơ chế hash khác (không liên quan) | `sources/eminel_sv_lib-develop/src/StaticServices/PasswordEncoder.php` |
| Hệ thống cũ | Cron (xác nhận không có) | `docs/02_詳細設計/10_バッチ処理/webap_cron設定_20240905.txt`, `mng-webap_cron設定_20241029.txt`, `cron実行用シェルスクリプト/eminel-webap.20240905.tgz`, `eminel-mng-webap.20240909.tgz` |
| Hệ thống mới | Luồng tạo admin qua Cognito | `src/functions/api-admin/create-admin.ts:1-9,32-85,105-127` |
| Hệ thống mới | Grep xác nhận không có code hash mật khẩu local / luồng đổi mật khẩu | `bcrypt`/`hashPassword`/`hashSync`/`scrypt`/`argon2`/`ForgotPassword`/`ResetPassword`/`ChangePassword` trên toàn `src/` |
