# Điều tra batch hệ cũ — CreateCsvAndZipConSensorDailyValuesCommand (sinh CSV/ZIP giá trị cảm biến theo ngày)

## Tổng quan

`CreateCsvAndZipConSensorDailyValuesCommand` là batch của hệ cũ (máy chủ concierge của EMINEL), **chỉ chạy vào mùng 1 hằng tháng lúc 05:15**. Nó đọc partition theo tháng của **tháng trước nữa** trong bảng thông tin cảm biến theo tháng (「月毎センサ情報」) `s_103`, ghi ra **mỗi hộ (EMS-SP) một file CSV**, rồi **lần chạy nào cũng nén ZIP** và xoá cả thư mục.

Một bản ghi = một tháng, với **31 ngày nằm ngang thành 31 cột** (「1日」→「31日」). Ngay trong cùng shell đó, batch `DeleteDataCommand` chạy sau sẽ **DROP đúng partition tháng trước nữa vừa được export** — nên batch này là "bản sao lưu cuối cùng ngay trước khi dữ liệu biến mất".

**Vị trí của 4 batch** (tên gọi dễ nhầm nên nói trước):

| Batch | Bảng | Tên model trong code | 1 bản ghi = | Mỗi ô giá trị = | Chu kỳ chạy |
|---|---|---|---|---|---|
| DeviceStatuses | `t_202` | 機器状態情報 | 1 lần thu thập | — | hằng ngày 05:15 |
| HourlyValues | `s_102` | 日毎センサ情報 | 1 NGÀY | 1 GIỜ (24 cột) | hằng ngày 05:15 |
| **DailyValues (tài liệu này)** | `s_103` | 月毎センサ情報 | **1 THÁNG** | **1 NGÀY (31 cột)** | mùng 1 hằng tháng, 05:15 |
| DailyAveValues | `s_113` | 月毎平均センサ情報 | 1 THÁNG | 1 NGÀY, trung bình (31 cột) | mùng 1 hằng tháng, 05:15 |

⚠️ **Tên gọi dễ gây nhầm**: "1日値" nói về **đơn vị của giá trị** (mỗi ô = 1 ngày), **không** nói về chu kỳ chạy — batch này chạy **mỗi tháng 1 lần**.

> 📖 **Partition (phân mảnh)**: bảng lớn được chia thành nhiều bảng con theo thời gian — ở đây mỗi tháng một bảng `s_103_YYYYMM`. Muốn xoá dữ liệu cũ chỉ cần **DROP** (lệnh SQL xoá nguyên một bảng) bảng con đó.
>
> 📖 **"Tháng trước nữa" (前々月)**: nếu chạy ngày 01/03 thì tháng đích là **tháng 1**, không phải tháng 2. Lý do ở mục 2.1.
>
> 📖 **EMS-SP**: mã số định danh một hộ ký hợp đồng dịch vụ EMINEL (`EMS-SP-NO`).

> **Phạm vi tài liệu này**: chỉ điều tra hành vi hệ cũ. Tài liệu **không** chứa: thiết kế thay thế cho E-GW, các bước chuyển đổi, bảng đối chiếu cũ↔mới.
> **Kết luận đã chốt ở bảng tổng hợp** (nêu ở đây để khỏi phải tra ngược): **"không cần giữ batch"** — hệ mới dùng **F-AD-09 (tải dữ liệu: sinh file tại thời điểm quản trị viên chọn khoảng thời gian)**, thay vì làm sẵn file định kỳ. Căn cứ đầy đủ ở `requirements/summary_batch_migration_ja.md`, dòng `CreateCsvAndZipConSensorDailyValuesCommand`.

## Phần 1 — Tổng quan

| Mục | Nội dung |
|---|---|
| **Vai trò** | Biến dữ liệu cảm biến theo tháng sắp bị xoá khỏi DB (giữ **2 tháng**) thành **file CSV → ZIP ngay trước khi mất**. **Chỉ chép nguyên dữ liệu, không tính toán/tổng hợp gì** (chi tiết 2.5). |
| **Đầu vào** | Partition theo tháng `s_103_YYYYMM` của bảng `s_103` (tháng đích = tháng chứa "ngày chạy − 32 ngày" = **tháng trước nữa**). ⚠️ Code **truyền thẳng tên partition làm alias** — `TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName)` (`…Command.php:39, 41`) — **chứ không đi qua** lớp `ConSensorDailyValuesTable` / entity `ConSensorDailyValue` của thư viện dùng chung (nơi định nghĩa bảng vật lý `s_103`, mô tả model 「月毎センサ情報」: `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Table/ConSensorDailyValuesTable.php:41`). Tên cột **viết cứng** trong Command (`:110-115`).<br>*(Entity = lớp code đại diện cho một dòng dữ liệu; alias = tên gọi mà ORM dùng để trỏ tới bảng.)* |
| **Đầu ra** | File CSV/ZIP trên ổ đĩa máy chủ.<br>・CSV: `{CON_SENSOR_DAILY_VALUES_CSV_FILES_PATH}/{đầu tháng}_{cuối tháng}/{EMS-SP}_{đầu tháng}_{cuối tháng}_1日値.csv`<br>・ZIP: **mỗi lần chạy**, nén cả thư mục thành `{đầu tháng}_{cuối tháng}.zip` |
| **Tóm tắt xử lý** | 1. Xác định tháng đích M = tháng chứa (ngày chạy − 32 ngày), kiểm tra partition `s_103_{M:Ym}` có tồn tại không (không có thì ghi log alert rồi kết thúc).<br>2. Lấy **danh sách EMS-SP** có trong partition đó.<br>3. Với từng hộ, mở CSV ở chế độ ghi tiếp; chỉ lần đầu mới ghi BOM UTF-8 và dòng tiêu đề 42 cột.<br>4. Chỉ đọc những bản ghi có cột 対象年月 (`c004`) **đúng bằng ngày mùng 1 của tháng đích**, theo trang 4.000 dòng; định dạng lại các cột ngày giờ rồi ghi ra.<br>5. **Không xét thứ trong tuần — luôn luôn** nén ZIP rồi xoá cả thư mục. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy và tháng đích

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `15 5 1 * *` — **chỉ mùng 1 hằng tháng, 05:15**. Chỉ nằm trong shell mùng 1 `12_CreateCsvAndDeleteData_day1.sh`, **không có** trong shell hằng ngày `_day2to31.sh` | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:41` (tiêu đề mục `#12.DBデータ削除` ở `:39`) |
| Lệnh chạy | `sudo -u apache php /var/www/vhost/conciergesv/bin/cake.php CreateCsvAndZipConSensorDailyValues` (chạy dưới user `apache`) | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` — bên trong `12_CreateCsvAndDeleteData_day1.sh` |
| Tham số | `--datetime` (mặc định `'now'`) | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand.php:28, 36` |
| **Tháng đích M** | `tháng chứa (thời điểm chạy − 32 ngày)` → tên partition `s_103_{M:Ym}` | cùng file `:39` |
| Khoảng thời gian của thư mục | **Đầu tháng → cuối tháng** của M (`startOfMonth()` / `endOfMonth()`) | cùng file `:56-58` |
| Thời điểm nén ZIP | **Mỗi lần chạy** (không xét thứ trong tuần) | cùng file `:138-144` |

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
| **DailyValues (`s_103`, giữ 2 tháng — tài liệu này)** | **tháng trước nữa** | **cùng tháng trước nữa đó** | **0 — cùng một lần chạy** |

Nói cách khác: hai batch hằng ngày ghi file xong còn được vài ngày mới xoá; batch này ghi file xong là xoá ngay trong cùng một shell.

> Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:53` (`$this->dropMonthlyTable('s_103', $dateTimeForMonth, 2);`) · cùng file `:110` (`$targetDateForDrop = $dateTime->subMonths($keepMonths);` → lùi 2 tháng so với ngày chạy). `t_202` ở `:47`, `s_102` ở `:49`, cách tính ngày xoá ở `:85`.

**Chống chạy chồng và an toàn khi lỗi**: shell dùng `flock -n` để chặn chạy chồng. Thứ bị khoá là **chính file script đang chạy** (`exec {my_fd}< "$0"`), nhưng **với batch này thế là đủ** — nó chỉ nằm trong `_day1.sh`, không như hai batch hằng ngày (nằm trong cả 2 shell nên mùng 1 vẫn chạy 2 lần). Kèm theo, `set -eu` khiến hễ một lệnh lỗi là dừng cả shell: nếu bước sinh CSV/ZIP hỏng thì không bao giờ chạy tới `DeleteData` — **dù không có ngày đệm, tình huống "DROP khi chưa kịp thành file" vẫn không xảy ra.**

> Nguồn: cùng file tgz, `12_CreateCsvAndDeleteData_day1.sh` (`flock -n ${my_fd}` / `set -eu` / `trap error_handler ERR`; thứ tự chạy trong shell: DeviceStatuses → HourlyValues → **batch này** → DailyAveValues → `DeleteData` → `DeleteLogicalDeletedDevices`, tức batch này đứng **trước** `DeleteData`)
> Chủ ý thiết kế được ghi thẳng trong `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:29-32` mục 補足1 (câu trích ở `:32`): 「CSV作成が失敗した場合はDBのデータを消去するコマンドは実施されない。」 — *nếu tạo CSV thất bại thì lệnh xoá dữ liệu DB sẽ không được thực hiện*.

### 2.2 Lấy dữ liệu

Batch không viết SQL trực tiếp mà đọc qua **ORM** của CakePHP — lớp trung gian cho phép thao tác DB bằng code đối tượng thay vì viết SQL tay. Khối dưới chứng minh 2 điều: ⓪ ORM được trỏ thẳng vào **bảng con của tháng đích**, và ①② dữ liệu được đọc theo từng hộ, chia trang 4.000 dòng.

```php
// ⓪ Ghép tên partition từ tháng đích rồi trỏ ORM vào đúng bảng con đó
$partitionTableName   = 's_103_' . $dateTime->subDays(32)->format('Ym');
$conSensorDailyValues = TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName);

// ① Danh sách EMS-SP có trong partition đích
$c001Values = $conSensorDailyValues->find()
    ->select(['c001'])
    ->distinct(['c001'])
    ->all();

// ② Với từng hộ, chỉ lấy bản ghi của tháng đích, theo trang 4.000 dòng
$targetDatas = $conSensorDailyValues->find()
    ->where([
        'c001' => $c001Value->c001,
        'c004' => $prevMonthStart->format('Ymd')   // lọc theo ngày đầu tháng đích
    ])
    ->limit($pageSize)      // $pageSize = 4000
    ->page($page)
    ->all();
```
Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand.php:39, 41` (⓪) · `:49-52` (①) · `:97-104` (②) · `:55` (`$pageSize = 4000`).

**Khác biệt so với batch chạy hằng ngày**: hai batch kia chỉ lọc theo `c001`, còn batch này **lọc thêm `c004` (tháng đích)**. Có thể hiểu là phòng trường hợp partition tháng lẫn bản ghi của tháng khác (🔸 *suy đoán — trong code không có comment giải thích; cần thì hỏi mui*).

**Ánh xạ cột CSV ↔ cột DB** (suy ra từ việc `$columnNames` và `$headers` xếp cùng thứ tự). Cột **Tên cột CSV** giữ nguyên tiếng Nhật vì đây chính là chuỗi in ra ở dòng tiêu đề file CSV; cột **Ý nghĩa** là phần dịch/giải thích:

| Tên cột CSV | Cột DB | Ý nghĩa |
|---|---|---|
| EMS-SP | `c001` | Mã hộ (EMS-SP-NO) |
| 機器種別 | `c002` | Mã loại thiết bị |
| 設置場所 | `c003` | Mã vị trí lắp đặt |
| 対象年月 | `c004` | **Tháng** mà bản ghi này đại diện (**kiểu ngày giờ → có định dạng lại**) |
| 集計遡及フラグ | `c009` | **Cờ công việc** báo cho tầng tổng hợp bên trên biết giá trị tổng hợp của kỳ quá khứ đã bị **tính lại hồi tố** (*hồi tố = tính lại và ghi đè số liệu của kỳ đã chốt*) nên cần chạy lại (1 = cần tổng hợp lại). Hằng số `C_NEED_AGG_COMPLETE_FLAG` — `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorDailyValue.php:63`; nơi đặt cờ: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CalcMonthlyAccumulatedValueCommand.php:267, 282` |
| グループ属性1〜5 | `c111`–`c115` | 5 thuộc tính dùng để gom nhóm (so sánh với hộ khác) |
| 1日〜31日 | `c011`–`c041` | **31 ngày trong tháng nằm ngang thành 31 cột** |
| 更新日時 | `c051` | Thời điểm cập nhật bản ghi (**kiểu ngày giờ → có định dạng lại**) |

> Nguồn: cùng file `:84-89` (tiêu đề CSV 42 cột) · `:110-115` (42 tên cột DB).
> Cách cộng số cột: 5 + 5 + 31 + 1 = **42 cột**.

**Lưu ý về cấu trúc dữ liệu**: 31 cột luôn tồn tại cố định, nên với tháng có 30 ngày trở xuống thì các cột cuối bỏ trống. Kiểu "nằm ngang" này cùng tư tưởng thiết kế với bảng giá trị theo giờ (`s_102`, 24 cột).

### 2.3 Logic sinh CSV

```
① Xác định thư mục đầu ra:  {CON_SENSOR_DAILY_VALUES_CSV_FILES_PATH}/{đầu tháng Ymd}_{cuối tháng Ymd}
   └ Chưa có thì mkdir (quyền 0777; tạm đặt umask = 0 — bộ lọc quyền mặc định của Linux —
     rồi trả lại giá trị cũ)

② Lặp theo từng hộ:
   Tên file = {EMS-SP}_{đầu tháng Ymd}_{cuối tháng Ymd}_1日値.csv
   fopen(..., 'a')  ← chế độ GHI TIẾP
      ※ Batch chỉ chạy 1 lần/tháng và cuối mỗi lần chạy thư mục đã bị xoá, nên trên thực tế
        file luôn được tạo mới. Cách viết "ghi tiếp + kiểm tra BOM" giống hệt hai batch
        chạy hằng ngày (🔸 suy đoán: dùng chung khuôn code — trong code không có comment).
        ⚠️ Lưu ý khi chạy lại thủ công bằng `--datetime`: nếu file cũ vẫn còn, dữ liệu sẽ bị
        ghi nối thêm chứ không ghi đè

   ├ Chỉ khi file mới tạo, hoặc kích thước = 0:
   │    Ghi BOM UTF-8 (\xEF\xBB\xBF) — 3 byte đánh dấu đầu file, báo cho phần mềm đọc
   │       biết đây là UTF-8
   │       (🔸 code chỉ ghi comment "UTF-8 BOM 形式"; nói đây là để Excel không lỗi font
   │          là suy đoán)
   │    Ghi dòng tiêu đề 42 cột
   │
   └ Đọc theo trang 4.000 dòng các bản ghi của tháng đích, ghi từng dòng:
        Chỉ c004 (tháng đích) và c051 (thời điểm cập nhật)
            → định dạng 'Y-m-d H:i:s.v' + 3 ký tự đầu của múi giờ
            → ra chuỗi dạng: 2024-07-01 05:15:00.123 +09 (`.v` là phần mili-giây)
        Các cột còn lại ghi nguyên giá trị

③ Không xét thứ trong tuần — luôn nén *.csv trong thư mục thành ZIP (xem 2.4)
```
Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand.php:56-65` (①) · `:68-82` (tên file và BOM ở ②, comment ở `:81`) · `:118-130` (ghi dòng và định dạng ngày giờ) · `:138-144` (③).

**Hằng số nghiệp vụ · biến môi trường**:

| Tên | Giá trị | Nguồn |
|---|---|---|
| `CON_SENSOR_DAILY_VALUES_CSV_FILES_PATH` | `/var/data/ConSensorDailyValues/` | `legacy_eminel_docs/sources/conciergesv-develop/config/.env.prod:64` (các file `.env.dev` / `.env.stage` / `.env.local` cùng giá trị) |
| `$pageSize` | 4000 (comment trong code: "một lần xử lý bao nhiêu bản ghi; vagrant tối đa 4000") | `…/CreateCsvAndZipConSensorDailyValuesCommand.php:54-55` |
| Độ lệch tháng đích | 32 ngày (con số được chọn để chắc chắn rơi vào tháng trước nữa) | cùng file `:39` |

### 2.4 Nơi ghi ra và việc nén ZIP

**Cấu trúc thư mục**:

```
/var/data/ConSensorDailyValues/             ← chạy nhiều lần thì các ZIP tháng xếp cạnh nhau
│                                               (bản cũ KHÔNG bị xoá)
├── 20240601_20240630.zip
└── 20240701_20240731.zip                   ← ZIP của cả thư mục tháng (thư mục bị xoá mỗi lần chạy)
    └─ bên trong: 00000000001_20240701_20240731_1日値.csv.zip
                  00000000002_20240701_20240731_1日値.csv.zip
                  …(bao nhiêu hộ thì bấy nhiêu ZIP con)
```

※ EMS-SP được kiểm tra **tối thiểu 11 chữ số** (`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Table/EmsSpNosTable.php:69` — `minLength('ems_sp_no', 11, …)`, thông báo lỗi 「有効な11桁の数字を入力してください」; **không có** rule `maxLength`). Con số này quyết định cách màn hình quản trị cắt tên file để lọc (`legacy_eminel_docs/sources/eminelsv-develop/src/Controller/DownloadController.php:338`).

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
→ Sau bước ④ trên đĩa chỉ còn MỘT file {tháng}.zip. KHÔNG mất dữ liệu — mọi CSV nằm
   trong ZIP đó (2 lớp: ZIP thư mục ⊃ ZIP từng CSV)
```
Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateZipsTrait.php:23-72` (`rm -rf` ở `:64`; nó chỉ xoá thư mục tháng, các file `.zip` ở tầng trên vẫn còn). **Khác batch hằng ngày ở chỗ không xét thứ Hai — lần chạy nào cũng nén.**

**Ai dùng file sinh ra**: chức năng tải "dữ liệu quá khứ" của màn hình quản trị cũ `eminelsv`. Lựa chọn `previous_day_value` (tên hiển thị 「1日値（過去データ）」) trỏ vào thư mục đầu ra của batch này.

> Nguồn: `legacy_eminel_docs/sources/eminelsv-develop/src/Controller/DownloadController.php:74` (tên hiển thị) · `:415` (`'previous_day_value' => env('DAY_VALUE_DIRECTORY')`) · `legacy_eminel_docs/sources/eminelsv-develop/config/.env.prod:80` (`DAY_VALUE_DIRECTORY = "/var/data/ConSensorDailyValues/"` — trùng đúng đường dẫn phía batch).
> Màn hình quản trị chỉ lọc các ZIP có sẵn theo ngày và EMS-SP rồi đóng gói lại để trả về (cùng file `:236` `createPreviousDataZip()` — một hàm dùng chung cho cả 4 lựa chọn; quét đệ quy từ thư mục gốc bằng `RecursiveDirectoryIterator` ở `:298`, lọc theo ngày trong tên file ở `:277-282` — tức **giả định các ZIP tháng cũ vẫn còn tích luỹ ở đó**). Điểm quan trọng: **nó không dựng lại dữ liệu từ DB, mà chỉ phát lại file do batch này tạo ra**.

### 2.5 Xác nhận: batch này không tính toán/tổng hợp

Batch không tính toán hay tổng hợp giá trị nào — giá trị theo ngày đã được batch tổng hợp khác ghi sẵn vào `s_103`, batch này chỉ chép sang CSV. Vì vậy điểm cần bàn khi chuyển hệ thu về: **dữ liệu quá thời hạn lưu (2 tháng) thì giữ lại bằng cách nào.**

> Phán định (có giữ batch không, hệ mới thay bằng gì) nằm ở bảng tổng hợp `requirements/summary_batch_migration_ja.md`, dòng của batch này. Kết luận: **"không cần giữ batch"** — hệ mới dùng F-AD-09.
