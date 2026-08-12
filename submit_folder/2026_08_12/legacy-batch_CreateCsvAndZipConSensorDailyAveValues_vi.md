# Điều tra batch hệ cũ — CreateCsvAndZipConSensorDailyAveValuesCommand (sinh CSV/ZIP giá trị trung bình theo ngày)

## Tổng quan

`CreateCsvAndZipConSensorDailyAveValuesCommand` là batch của hệ cũ (máy chủ concierge của EMINEL), **chỉ chạy vào mùng 1 hằng tháng lúc 05:15**. Nó đọc partition theo tháng của **tháng trước nữa** trong bảng thông tin cảm biến trung bình theo tháng (「月毎平均センサ情報」) `s_113`, ghi ra **đúng một file CSV**, rồi **lần chạy nào cũng nén ZIP** và xoá cả thư mục.

Điểm khác biệt quyết định so với 3 batch còn lại: **không chia file theo hộ (EMS-SP)**. Lý do là `s_113` không chứa số liệu của từng hộ mà chứa **giá trị trung bình** gộp theo "loại thiết bị × vị trí lắp × thuộc tính nhóm" — bảng này thậm chí không có cột EMS-SP.

**Vị trí của 4 batch** (tên gọi dễ nhầm nên nói trước):

| Batch | Bảng | Tên model trong code | 1 bản ghi = | Mỗi ô giá trị = | Chu kỳ chạy |
|---|---|---|---|---|---|
| DeviceStatuses | `t_202` | 機器状態情報 | 1 lần thu thập | — | hằng ngày 05:15 |
| HourlyValues | `s_102` | 日毎センサ情報 | 1 NGÀY | 1 GIỜ (24 cột) | hằng ngày 05:15 |
| DailyValues | `s_103` | 月毎センサ情報 | 1 THÁNG | 1 NGÀY (31 cột) | mùng 1 hằng tháng, 05:15 |
| **DailyAveValues (tài liệu này)** | `s_113` | 月毎平均センサ情報 | **1 THÁNG** | **1 NGÀY, trung bình (31 cột)** | mùng 1 hằng tháng, 05:15 |

⚠️ **Hai điều dễ nhầm ở tên gọi**: ① tên có chữ "giá trị trung bình" nhưng **batch này không tính trung bình** (một batch tổng hợp khác đã ghi sẵn vào `s_113`); ② "1日平均値" nói về **đơn vị của giá trị** (mỗi ô = 1 ngày), **không** phải chu kỳ chạy — batch này chạy **mỗi tháng 1 lần**.

> 📖 **Partition (phân mảnh)**: bảng lớn được chia thành nhiều bảng con theo thời gian — ở đây mỗi tháng một bảng `s_113_YYYYMM`. Muốn xoá dữ liệu cũ chỉ cần **DROP** (lệnh SQL xoá nguyên một bảng) bảng con đó.
>
> 📖 **"Tháng trước nữa" (前々月)**: nếu chạy ngày 01/03 thì tháng đích là **tháng 1**, không phải tháng 2. Lý do ở mục 2.1.

> **Phạm vi tài liệu này**: chỉ điều tra hành vi hệ cũ. Tài liệu **không** chứa: thiết kế thay thế cho E-GW, các bước chuyển đổi, bảng đối chiếu cũ↔mới.
> **Kết luận đã chốt ở bảng tổng hợp** (nêu ở đây để khỏi phải tra ngược): **"không cần giữ batch"** — hệ mới dùng **F-AD-09 (tải dữ liệu: sinh file tại thời điểm quản trị viên chọn khoảng thời gian)**, thay vì làm sẵn file định kỳ. Căn cứ đầy đủ ở `requirements/summary_batch_migration_ja.md`, dòng `CreateCsvAndZipConSensorDailyAveValuesCommand`.

## Phần 1 — Tổng quan

| Mục | Nội dung |
|---|---|
| **Vai trò** | Biến dữ liệu trung bình theo tháng sắp bị xoá khỏi DB (giữ **2 tháng**) thành **file CSV → ZIP ngay trước khi mất**. **Chỉ chép nguyên dữ liệu, không tính toán/tổng hợp gì** (chi tiết 2.5). |
| **Đầu vào** | Partition theo tháng `s_113_YYYYMM` của bảng `s_113` (tháng đích = tháng chứa "ngày chạy − 32 ngày" = **tháng trước nữa**). ⚠️ Code **truyền thẳng tên partition làm alias** — `TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName)` (`…Command.php:39, 41`) — **chứ không đi qua** lớp `ConSensorDailyAveValuesTable` / entity `ConSensorDailyAveValue` của thư viện dùng chung (nơi định nghĩa bảng vật lý `s_113`, mô tả model 「月毎平均センサ情報」: `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Table/ConSensorDailyAveValuesTable.php:41`). Tên cột **viết cứng** trong Command (`:102-107`).<br>*(Entity = lớp code đại diện cho một dòng dữ liệu; alias = tên gọi mà ORM dùng để trỏ tới bảng.)* |
| **Đầu ra** | File CSV/ZIP trên ổ đĩa máy chủ.<br>・CSV: `{CON_SENSOR_DAILY_AVE_VALUES_CSV_FILES_PATH}/{đầu tháng}_{cuối tháng}/{đầu tháng}_{cuối tháng}_1日平均値.csv` — **chỉ 1 file**<br>・ZIP: **mỗi lần chạy**, nén cả thư mục thành `{đầu tháng}_{cuối tháng}.zip` |
| **Tóm tắt xử lý** | 1. Xác định tháng đích M = tháng chứa (ngày chạy − 32 ngày), kiểm tra partition `s_113_{M:Ym}` có tồn tại không (không có thì ghi log alert rồi kết thúc).<br>2. **Không lặp theo hộ** — mở đúng một file CSV; chỉ lần đầu mới ghi BOM UTF-8 và dòng tiêu đề 40 cột.<br>3. Chỉ đọc những bản ghi có cột 対象年月 (`c003`) **đúng bằng ngày mùng 1 của tháng đích**, theo trang 4.000 dòng; định dạng lại các cột ngày giờ rồi ghi ra.<br>4. **Không xét thứ trong tuần — luôn luôn** nén ZIP rồi xoá cả thư mục. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy và tháng đích

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `15 5 1 * *` — **chỉ mùng 1 hằng tháng, 05:15**. Chỉ nằm trong shell mùng 1 `12_CreateCsvAndDeleteData_day1.sh`, **không có** trong shell hằng ngày `_day2to31.sh` | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:41` (tiêu đề mục `#12.DBデータ削除` ở `:39`) |
| Lệnh chạy | `sudo -u apache php /var/www/vhost/conciergesv/bin/cake.php CreateCsvAndZipConSensorDailyAveValues` (chạy dưới user `apache`) | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` — bên trong `12_CreateCsvAndDeleteData_day1.sh` (chạy cuối cùng trong 4 batch CSV) |
| Tham số | `--datetime` (mặc định `'now'`) | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyAveValuesCommand.php:28, 36` |
| **Tháng đích M** | `tháng chứa (thời điểm chạy − 32 ngày)` → tên partition `s_113_{M:Ym}` | cùng file `:39` |
| Khoảng thời gian của thư mục | **Đầu tháng → cuối tháng** của M (`startOfMonth()` / `endOfMonth()`) | cùng file `:50-52` |
| Thời điểm nén ZIP | **Mỗi lần chạy** (không xét thứ trong tuần) | cùng file `:129-135` |

**Đọc dòng cron thế nào**: 5 trường là `phút giờ ngày-trong-tháng tháng thứ`. `15 5 1 * *` = 05:15 **chỉ mùng 1**.

**Vì sao "32 ngày trước" luôn rơi vào tháng trước nữa**: batch chỉ chạy vào **mùng 1**. Lùi 32 ngày từ mùng 1 thì **chắc chắn vượt qua trọn vẹn tháng liền trước** và rơi vào tháng trước nữa.

```
Chạy 2026-03-01 − 32 ngày → 2026-01-28  → tháng đích = tháng 1/2026 (tháng trước nữa)
Chạy 2026-05-01 − 32 ngày → 2026-03-30  → tháng đích = tháng 3/2026 (tháng trước nữa)
Chạy 2026-01-01 − 32 ngày → 2025-11-30  → tháng đích = tháng 11/2025 (tháng trước nữa)
※ Tháng liền trước dài 28/29/30 hay 31 ngày đều vậy: lùi 32 ngày từ mùng 1 luôn vượt qua nó
```

**Bao lâu sau khi thành file thì dữ liệu bị xoá khỏi DB?**

| Batch | Ghi ra file vào | DB bị DROP vào | Khoảng đệm |
|---|---|---|---|
| DeviceStatuses (`t_202`, giữ 8 ngày) | dữ liệu ngày D → D+8 | D+9 | 1 ngày |
| HourlyValues (`s_102`, giữ 14 ngày) | D+8 | D+15 | 7 ngày |
| **DailyAveValues (`s_113`, giữ 2 tháng — tài liệu này)** | **tháng trước nữa** | **cùng tháng trước nữa đó** | **0 — cùng một lần chạy** |

Việc **"export tháng trước nữa → DROP chính tháng đó" diễn ra trong cùng một lần chạy** hoàn toàn giống batch `CreateCsvAndZipConSensorDailyValues` (`s_103`): cùng lấy tháng trước nữa, cùng nén ZIP mọi lần chạy, và cùng bị DROP ngay trong lần chạy đó.

> Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:54` (`$this->dropMonthlyTable('s_113', $dateTimeForMonth, 2);`) · cùng file `:110` (`$targetDateForDrop = $dateTime->subMonths($keepMonths);`). `t_202` ở `:47`, `s_102` ở `:49`, cách tính ngày xoá ở `:85`.

**Chống chạy chồng và an toàn khi lỗi**: shell dùng `flock -n` để chặn chạy chồng. Thứ bị khoá là **chính file script đang chạy** (`exec {my_fd}< "$0"`), nhưng **với batch này thế là đủ** — nó chỉ nằm trong `_day1.sh`, không như hai batch hằng ngày (nằm trong cả 2 shell nên mùng 1 vẫn chạy 2 lần). Kèm theo, `set -eu` khiến hễ một lệnh lỗi là dừng cả shell: nếu bước sinh CSV/ZIP hỏng thì không bao giờ chạy tới `DeleteData` — **dù không có ngày đệm, tình huống "DROP khi chưa kịp thành file" vẫn không xảy ra.**

> Nguồn: cùng file tgz, `12_CreateCsvAndDeleteData_day1.sh` (`flock -n ${my_fd}` / `set -eu` / `trap error_handler ERR`; thứ tự chạy trong shell: DeviceStatuses → HourlyValues → DailyValues → **batch này** → `DeleteData` → `DeleteLogicalDeletedDevices`, tức batch này đứng **trước** `DeleteData`)
> Chủ ý thiết kế được ghi thẳng trong `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:29-32` mục 補足1 (câu trích ở `:32`): 「CSV作成が失敗した場合はDBのデータを消去するコマンドは実施されない。」 — *nếu tạo CSV thất bại thì lệnh xoá dữ liệu DB sẽ không được thực hiện*.

### 2.2 Lấy dữ liệu

Batch không viết SQL trực tiếp mà đọc qua **ORM** của CakePHP — lớp trung gian cho phép thao tác DB bằng code đối tượng thay vì viết SQL tay. **Không có bước lấy danh sách hộ (`distinct('c001')`)** — đây là khác biệt cấu trúc so với 3 batch còn lại.

```php
// ⓪ Ghép tên partition từ tháng đích rồi trỏ ORM vào đúng bảng con đó
$partitionTableName   = 's_113_' . $dateTime->subDays(32)->format('Ym');
$conSensorDailyValues = TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName);

// ① Lấy bản ghi của tháng đích theo trang 4.000 dòng (không chia theo hộ)
$targetDatas = $conSensorDailyValues->find()
    ->where([
        'c003' => $prevMonthStart->format('Ymd')   // lọc theo ngày đầu tháng đích
    ])
    ->limit($pageSize)      // $pageSize = 4000
    ->page($page)
    ->all();
```
Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyAveValuesCommand.php:39, 41` (⓪) · `:90-96` (①) · `:48-49` (`$pageSize = 4000`).

> Ghi chú: tên biến là `$conSensorDailyValues` nhưng bảng thực sự được lấy là `s_113` (giá trị trung bình) — xem cùng file `:39, 41`. Nhiều khả năng là do dùng chung khuôn code từ batch xử lý `s_103` (🔸 *suy đoán — trong code không có giải thích; cần thì hỏi mui*). Đọc code cần chú ý để khỏi nhầm.

**Ánh xạ cột CSV ↔ cột DB** (suy ra từ việc `$columnNames` và `$headers` xếp cùng thứ tự). Cột **Tên cột CSV** giữ nguyên tiếng Nhật vì đây chính là chuỗi in ra ở dòng tiêu đề file CSV; cột **Ý nghĩa** là phần dịch/giải thích:

| Tên cột CSV | Cột DB | Ý nghĩa |
|---|---|---|
| 機器種別 | `c001` | Mã loại thiết bị ⚠️ **khác nghĩa với `c001` của 3 bảng kia (EMS-SP)** |
| 設置場所 | `c002` | Mã vị trí lắp đặt |
| 対象年月 | `c003` | **Tháng** mà bản ghi này đại diện (**kiểu ngày giờ → có định dạng lại**) |
| グループ属性1〜5 | `c111`–`c115` | 5 thuộc tính dùng để gom nhóm (so sánh với hộ khác) |
| 1日〜31日 | `c011`–`c041` | **31 ngày trong tháng nằm ngang thành 31 cột**, chứa giá trị trung bình |
| 更新日時 | `c051` | Thời điểm cập nhật bản ghi (**kiểu ngày giờ → có định dạng lại**) |

> Nguồn: cùng file `:77-82` (tiêu đề CSV 40 cột) · `:102-107` (40 tên cột DB).
> Cách cộng số cột: 3 + 5 + 31 + 1 = **40 cột**.

Ý nghĩa của số hiệu cột khác nhau giữa các bảng: ở `s_113`, `c001` là "loại thiết bị" và `c003` là "tháng đích"; còn ở `s_103` / `s_102` / `t_202`, `c001` là "EMS-SP (mã hộ)" và `c003` là "vị trí lắp đặt" hoặc "loại giao tiếp". Khi lập bảng ánh xạ dữ liệu xuyên nhiều bảng lúc chuyển hệ, **phải tra định nghĩa của từng bảng, không được suy theo số hiệu cột**.

**Ý nghĩa của việc đây là bảng "trung bình"**: `s_113` không giữ số đo của từng hộ mà giữ giá trị trung bình đã gộp theo tổ hợp loại thiết bị · vị trí lắp · thuộc tính nhóm. Đây chính là dữ liệu nền cho phần "so sánh với hộ khác" trên app và đường trung bình trong báo cáo. Vì vậy bảng không có cột EMS-SP, và CSV cũng không chia theo hộ.

### 2.3 Logic sinh CSV

```
① Xác định thư mục đầu ra:  {CON_SENSOR_DAILY_AVE_VALUES_CSV_FILES_PATH}/{đầu tháng Ymd}_{cuối tháng Ymd}
   └ Chưa có thì mkdir (quyền 0777; tạm đặt umask = 0 — bộ lọc quyền mặc định của Linux —
     rồi trả lại giá trị cũ)

② Tạo đúng MỘT file CSV (không lặp theo hộ):
   Tên file = {đầu tháng Ymd}_{cuối tháng Ymd}_1日平均値.csv   ← không có EMS-SP trong tên
   fopen(..., 'a')  ← chế độ ghi tiếp

   ├ Chỉ khi file mới tạo, hoặc kích thước = 0:
   │    Ghi BOM UTF-8 (\xEF\xBB\xBF) — 3 byte đánh dấu đầu file, báo cho phần mềm đọc
   │       biết đây là UTF-8
   │       (🔸 code chỉ ghi comment "UTF-8 BOM 形式"; nói đây là để Excel không lỗi font
   │          là suy đoán)
   │    Ghi dòng tiêu đề 40 cột
   │
   └ Đọc theo trang 4.000 dòng các bản ghi của tháng đích, ghi từng dòng:
        Chỉ c003 (tháng đích) và c051 (thời điểm cập nhật)
            → định dạng 'Y-m-d H:i:s.v' + 3 ký tự đầu của múi giờ
            → ra chuỗi dạng: 2024-07-01 05:15:00.123 +09 (`.v` là phần mili-giây)
        Các cột còn lại ghi nguyên giá trị

③ Không xét thứ trong tuần — luôn nén *.csv trong thư mục thành ZIP (xem 2.4)
```
Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyAveValuesCommand.php:50-59` (①) · `:62-85` (tên file và BOM ở ②, comment ở `:74`) · `:110-122` (ghi dòng và định dạng ngày giờ) · `:129-135` (③).

**Hằng số nghiệp vụ · biến môi trường**:

| Tên | Giá trị | Nguồn |
|---|---|---|
| `CON_SENSOR_DAILY_AVE_VALUES_CSV_FILES_PATH` | `/var/data/ConSensorDailyAveValues/` | `legacy_eminel_docs/sources/conciergesv-develop/config/.env.prod:65` (các file `.env.dev` / `.env.stage` / `.env.local` cùng giá trị) |
| `$pageSize` | 4000 (comment trong code: "một lần xử lý bao nhiêu bản ghi; vagrant tối đa 4000") | `…/CreateCsvAndZipConSensorDailyAveValuesCommand.php:48-49` |
| Độ lệch tháng đích | 32 ngày (con số được chọn để chắc chắn rơi vào tháng trước nữa) | cùng file `:39` |

### 2.4 Nơi ghi ra và việc nén ZIP

**Cấu trúc thư mục**:

```
/var/data/ConSensorDailyAveValues/          ← chạy nhiều lần thì các ZIP tháng xếp cạnh nhau
│                                               (bản cũ KHÔNG bị xoá)
├── 20240601_20240630.zip
└── 20240701_20240731.zip                   ← ZIP của cả thư mục tháng (thư mục bị xoá mỗi lần chạy)
    └─ bên trong: 20240701_20240731_1日平均値.csv.zip     ← chỉ 1 file
```

**Các bước nén** (dùng chung trait `CreateZipsTrait::createZip` — *trait = khối code dùng chung giữa nhiều lớp trong PHP*):

```
① Nén từng CSV thành ZIP riêng → {tên file}.csv.zip
   └ Tên file bên trong ZIP đổi sang SJIS — bảng mã chữ Nhật cũ của Windows
      ← 🔸 code không có comment giải thích; suy đoán là để phần mềm giải nén
         trên Windows không làm hỏng tên file tiếng Nhật
② Xoá (unlink) các CSV gốc
③ Gộp toàn bộ ZIP con vào một ZIP của cả thư mục → {thư mục tháng}.zip
④ exec("rm -rf {thư mục tháng}") xoá luôn thư mục
   └ Mỗi bước nếu lỗi đều ghi log alert và ném Exception (không chấp nhận thành công một nửa)
→ Sau bước ④ trên đĩa chỉ còn MỘT file {tháng}.zip. KHÔNG mất dữ liệu — vì chỉ có 1 CSV
   nên bên trong đúng 1 ZIP con (2 lớp: ZIP thư mục ⊃ ZIP từng CSV)
```
Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateZipsTrait.php:23-72` (`rm -rf` ở `:64`; nó chỉ xoá thư mục tháng, các file `.zip` ở tầng trên vẫn còn). **Khác batch hằng ngày ở chỗ không xét thứ Hai — lần chạy nào cũng nén.**

**Ai dùng file sinh ra**: chức năng tải "dữ liệu quá khứ" của màn hình quản trị cũ `eminelsv`. Lựa chọn `previous_day_ave` (tên hiển thị 「1日値（平均値）」) trỏ vào thư mục đầu ra của batch này.

> Nguồn: `legacy_eminel_docs/sources/eminelsv-develop/src/Controller/DownloadController.php:75` (tên hiển thị) · `:416` (`'previous_day_ave' => env('DAY_VALUE_AVE_DIRECTORY')`) · `legacy_eminel_docs/sources/eminelsv-develop/config/.env.prod:82` (`DAY_VALUE_AVE_DIRECTORY = "/var/data/ConSensorDailyAveValues/"` — trùng đúng đường dẫn phía batch).
> Màn hình quản trị chỉ lọc các ZIP có sẵn theo ngày rồi đóng gói lại để trả về (cùng file `:236` `createPreviousDataZip()` — một hàm dùng chung cho cả 4 lựa chọn; quét đệ quy từ thư mục gốc bằng `RecursiveDirectoryIterator` ở `:298`, lọc theo ngày trong tên file ở `:277-282` — tức **giả định các ZIP tháng cũ vẫn còn tích luỹ ở đó**). Điểm quan trọng: **nó không dựng lại dữ liệu từ DB, mà chỉ phát lại file do batch này tạo ra**.

### 2.5 Xác nhận: batch này không tính trung bình

Tên có chữ "giá trị trung bình" nhưng batch **không tính trung bình**. Giá trị trung bình do batch tổng hợp `CalcCommonAverageDataCommand` ghi sẵn vào `s_113` (`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CalcCommonAverageDataCommand.php:1283` chỉ định bảng đích `EminelSvLib.ConSensorDailyAveValues`; lệnh lưu ở cùng file `:468, 1013`); batch này chỉ chép sang CSV. Vì vậy điểm cần bàn khi chuyển hệ thu về: **dữ liệu quá thời hạn lưu (2 tháng) thì giữ lại bằng cách nào.**

> Phán định (có giữ batch không, hệ mới thay bằng gì) nằm ở bảng tổng hợp `requirements/summary_batch_migration_ja.md`, dòng của batch này. Kết luận: **"không cần giữ batch"** — hệ mới dùng F-AD-09.
