# DeleteTimeOutControlTenMinuteCommand（10分タイムアウト制御レコード削除）

## Tóm tắt

`DeleteTimeOutControlTenMinuteCommand` là batch cron chạy **mỗi 10 phút** trên `conciergesv` — cùng họ
với `DeleteTimeOutControlOneMinuteCommand` (đã audit, xem `DeleteTimeOutControlOneMinute.md`), dọn tiếp
4 loại lệnh khác trong hàng đợi `Instructions` (khởi động lại từ xa, cập nhật property map, cập nhật
file cấu hình GW, cập nhật tham số điều khiển sưởi — quá 10 phút chưa xử lý xong) và LỒNG THÊM 1 nhánh
chạy mỗi giờ đúng phút 0 để dọn riêng lệnh cập nhật firmware (timeout 60 phút, dài hơn hẳn vì cập nhật
firmware tốn thời gian). Cùng là safety-net cho mô hình polling-based control giữa server và GW. Ở repo
mới `syp-eminelstandard-backend`, **kết luận giống hệt batch anh em đã audit**: không cần và không có cơ
chế tương đương, vì kiến trúc điều khiển thiết bị đã đổi hẳn sang gọi API cloud hãng đồng bộ, không còn
hàng đợi lệnh nào để timeout/dọn — xem chi tiết bằng chứng ở `DeleteTimeOutControlOneMinute.md`.

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `DeleteTimeOutControlTenMinuteCommand` (extends `Command` trực tiếp) · Lệnh gọi thực tế: `cake.php DeleteTimeOutControlTenMinute` *(quan sát trong `12_DeleteTimeOutControlTenMinute.sh` của tgz `eminel-mng-webap.20240909`; CakePHP chấp nhận cả hai dạng)* · Script cron: `12_DeleteTimeOutControlTenMinute.sh` · Cùng nhóm cron "12.DBデータ削除". |
| **Vai trò** | Safety-net dọn lệnh điều khiển GW bị timeout khỏi hàng đợi `Instructions`, cho 5 loại lệnh (4 loại timeout 10 phút + 1 loại timeout 60 phút) — cùng cơ chế với `DeleteTimeOutControlOneMinuteCommand` nhưng khác loại lệnh phụ trách. |
| **Input** | Đọc bảng `Instructions` — 2 điều kiện lọc riêng (xem A.2.2). Tham số `--datetime` (mặc định `now`). |
| **Output** | `DELETE` từng dòng khớp điều kiện, mỗi nhóm loại lệnh trong 1 transaction riêng. Không ghi dữ liệu mới. |
| **Khái quát xử lý** | 1. Nếu phút hiện tại (`--datetime`) đúng bằng 0 → chạy thêm nhánh dọn firmware (timeout 60 phút) TRƯỚC.<br>2. Luôn chạy nhánh dọn 4 loại lệnh còn lại (timeout 10 phút) — không điều kiện.<br>3. Mỗi nhánh: mở transaction riêng, tìm lệnh timeout, xóa từng dòng; lỗi 1 dòng → rollback nhánh đó, dừng nhánh đó (không ảnh hưởng nhánh kia vì 2 transaction độc lập). |

## A.2 Chi tiết

### A.2.1 Lịch chạy & cấu trúc lồng nhánh giờ/10-phút

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `*/10 * * * *` — mỗi 10 phút | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:43` |
| Điều kiện chạy nhánh firmware (60 phút) | Chỉ chạy khi `(--datetime)->minute === 0` — tức đúng vào các lượt cron rơi vào đầu giờ (`:00`, `:10` không tính trừ khi là `:00`) | `DeleteTimeOutControlTenMinuteCommand.php:40-42` |
| Điều kiện chạy nhánh 10 phút | Luôn chạy, không điều kiện, mỗi lượt cron | `:44` |

Vì cron chạy `*/10` (tức các phút `:00,:10,:20,:30,:40,:50`), nhánh firmware chỉ trùng đúng lượt `:00`
mỗi giờ — nghĩa là **firmware timeout được kiểm tra 1 lần/giờ**, dù class tên gọi là "TenMinute". Đây
không phải bug — là thiết kế cố ý gộp chung 2 tần suất khác nhau vào 1 Command để tận dụng chung 1 lượt
cron `*/10`, tránh phải khai thêm 1 dòng cron riêng cho firmware.

### A.2.2 2 nhóm điều kiện lọc, khác hẳn timeout & loại lệnh

| Nhánh | `instruction_type` | Ý nghĩa từng loại | Timeout | Nguồn |
|---|---|---|---|---|
| `deleteInstructionsPerTenMinute` | `IN (3, 4, 6, 7)` | 3=`INSTRUCTION_TYPE_REBOOT` (khởi động lại từ xa), 4=`INSTRUCTION_TYPE_PROPERTYMAP` (cập nhật property map), 6=`INSTRUCTION_TYPE_CONFIGURE` (cập nhật file cấu hình GW), 7=`INSTRUCTION_TYPE_HEAT_CONTROL` (cập nhật tham số điều khiển sưởi) | `instruction_date < (--datetime − 10 phút)` | `:53-70`; hằng số `sources/hemssv-develop/config/const.php:57,59,63,65` |
| `deleteInstructionsPer60Minutes` | `IN (5)` (viết dạng `IN` nhưng chỉ 1 giá trị) | 5=`INSTRUCTION_TYPE_FIRMWARE` (cập nhật firmware) | `instruction_date < (--datetime − 60 phút)` | `:95-109`; hằng số `const.php:61` |

Cùng vòng đời bình thường như đã xác nhận ở `DeleteTimeOutControlOneMinute.md` (§A.2.2): server ghi lệnh
vào `Instructions` khi cần → GW poll định kỳ lấy về (`InstructionController.php:77`, switch theo từng
`instruction_type` tại `:206-239`) → GW xử lý, báo kết quả → server tự xóa lệnh (mẫu tương tự
`:798-821` cho PROPERTYMAP, `:996-1019` cho FIRMWARE, `:1154-1177` cho CONFIGURE, `:1312-1335` cho
HEAT_CONTROL, `:1470-1493` cho REBOOT — cùng cặp find+delete-on-complete như loại 1 đã trích ở file kia).
2 batch `DeleteTimeOutControl*MinuteCommand` chỉ là dọn phần lệnh KHÔNG được vòng đời bình thường này tự
xóa kịp.

**Vì sao firmware cần timeout dài hơn hẳn (60 phút so với 10 phút)** *(suy đoán hợp lý dựa vào bản chất
nghiệp vụ, không có comment xác nhận trực tiếp trong code)*: cập nhật firmware cho GW/thiết bị thường
mất nhiều thời gian hơn (tải file, ghi flash, khởi động lại) so với các lệnh cấu hình/điều khiển đơn
giản khác — nên ngưỡng "coi là timeout" phải dài hơn để không xóa nhầm lệnh đang xử lý bình thường.

### A.2.3 Giao dịch & xử lý lỗi

- 2 nhánh dùng **2 transaction ĐỘC LẬP** (mỗi nhánh tự `begin()`/`commit()`/`rollback()` riêng, khác
  hẳn `DeleteDataCommand` dùng chung 1 transaction cho nhiều bước) — lỗi ở nhánh firmware (nếu có, chỉ
  xảy ra vào phút :00) không ảnh hưởng nhánh 10-phút và ngược lại. (`:59-86,101-125`)
- Cùng pattern với `DeleteTimeOutControlOneMinuteCommand`: xóa từng dòng bằng `foreach`+`delete()`, danh
  sách rỗng thì rollback (vô hại)+log rồi return, lỗi 1 dòng thì rollback TOÀN BỘ nhánh đó + dừng ngay
  (không xóa tiếp các dòng còn lại trong CÙNG nhánh).
- Cùng rủi ro đã nêu ở file kia: điều kiện lọc không kiểm tra `instruction_status`, nên lệnh GW đang xử
  lý dở (chưa kịp báo hoàn tất trong khung timeout) vẫn có thể bị xóa như lệnh chết thật sự.

### A.2.4 Điểm đặc biệt / Rủi ro

- Không extends `BaseCommand` → không có lock PID ở tầng PHP (giống batch anh em), nhưng shell wrapper
  cron `12_DeleteTimeOutControlTenMinute.sh` có `flock -n` chống đa khởi động — rủi ro chạy trùng đã
  được chặn ở tầng vận hành.
- `instruction_type = 2` (`INSTRUCTION_TYPE_DEVICE_LIST` — yêu cầu danh sách thiết bị) **không được dọn
  bởi bất kỳ batch nào trong cả 2 Command timeout đã audit** (1-phút: chỉ loại 1; 10-phút: loại 3,4,6,7
  + loại 5 riêng) — *(chưa xác minh được có cơ chế dọn nào khác cho loại 2, hay loại này không cần dọn
  vì lý do nghiệp vụ khác — ngoài phạm vi 2 batch đang audit)*.
- Việc "gộp 2 tần suất khác nhau vào 1 Command" (10 phút + 60 phút lồng nhau qua kiểm tra `minute===0`)
  khiến tên class (`...TenMinuteCommand`) không phản ánh đầy đủ hành vi thật (còn ẩn 1 tần suất 60 phút
  bên trong) — dễ gây hiểu lầm nếu chỉ đọc tên mà không mở code, cần lưu ý khi port để không bỏ sót phần
  firmware.

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

> Cùng kết luận với `DeleteTimeOutControlOneMinute.md` — không lặp lại toàn bộ bằng chứng, chỉ xác nhận
> áp dụng đúng cho cả 5 loại lệnh của batch này.

## Đã kiểm tra

| Khu vực / candidate | Kết quả |
|---|---|
| Mô hình điều khiển thiết bị thật (áp dụng chung mọi loại lệnh, không riêng gì reboot/firmware/config/heat-control) | **PUSH đồng bộ, không polling** — đã xác nhận ở `DeleteTimeOutControlOneMinute.md` Phần B: `src/functions/api-device/control-device.ts:91-425`, `src/functions/batch-execute-automation/app.ts:153-159`, `src/layers/common/nodejs/business-logic/control-device.ts:226-793`. Không phân biệt theo "loại lệnh" như hàng đợi `Instructions` cũ (`instruction_type`) — mọi thao tác điều khiển đều gọi thẳng API cloud hãng, không có khái niệm hàng đợi theo loại lệnh nào cả. |
| Bảng/Lambda tương đương "hàng đợi lệnh reboot/cấu hình/firmware GW + dọn timeout" | Không tìm thấy — cùng bằng chứng đã nêu ở file kia (grep `Instruction`/`PendingCommand`/`DeviceCommand`/`ControlQueue`/`timeout`/`stale`/`pending` trên `src/functions/`, `src/layers/common/nodejs/business-logic/` đều 0 kết quả liên quan). Không áp dụng lại quy trình tìm kiếm vì bản chất câu hỏi giống hệt (cùng bảng `Instructions`, cùng cơ chế polling bị loại bỏ, chỉ khác `instruction_type`). |
| Khái niệm "cập nhật firmware GW/thiết bị từ xa" ở hệ mới | **Vẫn tồn tại trong requirement E-GW, chỉ đổi đường giao** — cả 5 chức năng mà 5 `instruction_type` của batch này phục vụ (再起動・プロパティマップ・ファームウェアOTA・設定ファイル・暖房制御パラメータ) đều có trong `00_integrated_requirements_v1.2.md`: F-GW-11〜13 (:382-384), F-MC-07/08 (:399-400), mục 8-2 配信 liệt kê đủ 5 hạng mục khớp 1-1 với type 3,4,5,6,7 (:563-569), 配信経路 「すべてEMINEL-smartサーバー → GW管理クラウド → E-GW」 (:571); cơ chế giao là MQTT push qua GW管理クラウド (tài sản sẵn có của mui Lab — feature_list :35,:77 do mui chủ trì) thay vì hàng đợi DB polling — nên batch dọn timeout DB không cần port, còn semantics timeout/未達 của chỉ thị thuộc về GW管理クラウド. Ngoài ra e-smart hiện đã có remote firmware update (`update_firmware`/`check_update_firmware` qua `infraredRemoteService` — `src/functions/api-device/update-firmware.ts:22`, `check-update-firmware.ts:8`) theo mô hình gọi đồng bộ — thêm dẫn chứng cho việc không cần hàng đợi. |

---

## Tổng kết

Áp dụng lại đúng kết luận đã đúc kết ở `DeleteTimeOutControlOneMinute.md` — không lặp lại chi tiết, chỉ
nêu điểm khác biệt riêng của batch này:

- Bản cũ ở đây quản lý 5/7 loại lệnh trong `Instructions` (thiếu loại 1 đã có batch riêng, và loại 2
  không rõ ai dọn) — cùng 1 bài toán gốc "hàng đợi polling cần dọn rác timeout" nhưng chia nhỏ theo
  timeout khác nhau (10 phút cho lệnh cấu hình/điều khiển, 60 phút cho firmware) thay vì 1 timeout chung
  cho tất cả — đây LÀ 2 "nhánh" trong cùng 1 batch, nhưng **không phải 2 thuật toán khác bản chất** (đều
  cùng công thức so sánh `instruction_date` với ngưỡng), nên không cần đúc kết dạng cây quyết định phức
  tạp — chỉ khác con số ngưỡng và tập `instruction_type` áp dụng.
- Bản mới: cùng 1 lý do biến mất như batch anh em — chuyển hẳn sang gọi API cloud hãng đồng bộ, không
  còn hàng đợi lệnh nào theo BẤT KỲ loại nào (reboot/config/firmware/heat-control) để cần timeout/dọn.
  Bài toán hàng đợi DB polling không còn; việc giao 5 loại chỉ thị chuyển sang MQTT qua GW管理クラウド
  (F-MC-08), nơi chịu trách nhiệm về độ tin cậy giao/chỉ thị chưa giao — ngoài phạm vi EMINEL-smartサーバー.

**Kết luận khi port**: không cần đưa `DeleteTimeOutControlTenMinuteCommand` vào hệ thống mới, dù là
phần dọn `instruction_type IN (3,4,6,7)` (10 phút) hay phần dọn firmware `instruction_type=5` (60 phút,
lồng trong cùng Command) — cả 2 đều là batch dọn rác cho hàng đợi `Instructions`, mà hàng đợi đó không
tồn tại trong kiến trúc push-đồng-bộ hiện tại. Thêm lại batch này (dưới bất kỳ hình thức nào) sẽ dư
thừa, vì không có bảng hàng đợi nào để nó dọn.

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/conciergesv-develop/src/Command/DeleteTimeOutControlTenMinuteCommand.php` |
| Hệ thống cũ | Batch anh em (đã audit đầy đủ, dùng chung bối cảnh vòng đời) | `DeleteTimeOutControlOneMinute.md`, `sources/conciergesv-develop/src/Command/DeleteTimeOutControlOneMinuteCommand.php` |
| Hệ thống cũ | Ý nghĩa các `instruction_type` (xác nhận chéo qua hemssv) | `sources/hemssv-develop/config/const.php:57,59,61,63,65` |
| Hệ thống cũ | Vòng đời xử lý từng loại lệnh (dispatch theo poll + tự xóa khi hoàn tất) | `sources/hemssv-develop/src/Controller/InstructionController.php:77,206-239,798-821,996-1019,1154-1177,1312-1335,1470-1493` |
| Hệ thống cũ | Ý nghĩa cột `Instruction` | `sources/eminel_sv_lib-develop/src/Model/Entity/Instruction.php` |
| Hệ thống cũ | Script cron thực thi (lệnh gọi thực tế + `flock -n` chống đa khởi động) | `docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` → `eminel-mng-webap/12_DeleteTimeOutControlTenMinute.sh` |
| Hệ thống cũ | Lịch chạy (cron) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:43` |
| Hệ thống cũ | Danh sách batch (mô tả tiếng Nhật, nhóm server) | `docs/03_API仕様/04_バッチ一覧.md:79` |
| Hệ thống mới | Requirement E-GW về 5 chức năng配信 + đường giao MQTT qua GW管理クラウド | `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:34,380-384,395,399-400,563-571`, `docs/eminel/1_product/10_feature_list.md:35,77` |
| Hệ thống mới | Bằng chứng đầy đủ (không lặp lại, tham chiếu file batch anh em) | `DeleteTimeOutControlOneMinute.md` (Phần B), `src/functions/api-device/control-device.ts:91-425`, `src/functions/batch-execute-automation/app.ts:153-159`, `src/layers/common/nodejs/business-logic/control-device.ts:226-793` |
