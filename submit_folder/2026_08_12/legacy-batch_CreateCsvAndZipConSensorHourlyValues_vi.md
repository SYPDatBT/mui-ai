# Điều tra batch hệ cũ — CreateCsvAndZipConSensorHourlyValuesCommand (sinh CSV/ZIP giá trị cảm biến theo giờ)

> ## Kết luận
>
> **Phán định: không cần giữ batch（バッチとしては不要）— hệ mới thay bằng F-AD-09（データダウンロード / tải dữ liệu）.**
>
> - **Batch này làm gì**: biến partition 8-ngày-trước của bảng giá trị cảm biến theo giờ `s_102` (một bản ghi = một ngày, 24 giờ nằm ngang) thành CSV theo từng hộ, thứ Hai nén ZIP thư mục tuần-trước-nữa — di tản dữ liệu ra file trước khi hết hạn lưu **14 ngày** trong DB.
> - **Vì sao bỏ được**: hệ mới không "làm sẵn file định kỳ" — khi quản trị viên chọn khoảng thời gian, `api-download` khởi động bất đồng bộ `batch-download` Lambda sinh ZIP rồi phát qua URL ký sẵn của S3; việc lưu giữ do DynamoDB TTL + PITR đảm nhận → cơ chế "xuất file trước khi DROP" tự nó không còn cần. *(Căn cứ: điều tra backend e-smart `api-download`/`batch-download` — ngoài phạm vi tài liệu này.)*
> - **Riêng batch này**: DB giữ `s_102` 14 ngày nhưng CSV hoá vẫn ở mốc −8 ngày → file luôn có trước lúc DROP 7 ngày; đó là chủ ý hay khuôn code chép lại thì code lẫn tài liệu thiết kế đều không ghi. Hệ mới thay toàn bộ thiết kế thời hạn lưu bằng TTL.
> - **Điểm treo (要FIX ở spec [I])**: 保持期間 (thời hạn lưu) và 対象データ種別 (loại dữ liệu download) của E-GW chưa chốt — bộ câu hỏi ở `qa_batch_csvzip.md` (cùng thư mục).
>
> Bảng phán định đầy đủ (47 batch): `summary_batch_migration_ja.md` (cùng thư mục), dòng `CreateCsvAndZipConSensorHourlyValuesCommand`.

**Khối tiếng Nhật để đăng Notion** (paste nguyên vẹn):

```
役割：日毎センサ情報（s_102）の8日前パーティションを契約者ごとにCSV化し、月曜に前々週分をZIP圧縮（24時間分が横持ち）。

判定：バッチとしては不要（新システムでは F-AD-09 データダウンロードで代替）。

理由：新システムは「定期的にファイルを作り置き」しない。管理者が期間を指定した時点で api-download が batch-download Lambda を非同期起動してZIPを生成し、S3経由の署名付きURLで配布する方式。DB側の保持は DynamoDB TTL、バックアップは PITR が担うため、「退避してからDROP」という仕組み自体が不要。

補足：s_102 のDB保持は14日だがCSV化は8日前に行われるため、結果として DROP の7日前にファイルが出来上がる（それが意図的な設計かはコード・設計書に記述が無く不明）。新システムでは保持期間の設計そのものを TTL で置き換える。

残論点：E-GWの保持期間・対象データ種別は spec [I]（データダウンロード機能仕様）で要FIX。
```

## Tổng quan

`CreateCsvAndZipConSensorHourlyValuesCommand` là batch của hệ cũ (máy chủ concierge của EMINEL), chạy **05:15 mỗi ngày**. Nó đọc **partition theo ngày của 8 ngày trước** trong bảng thông tin cảm biến theo ngày (「日毎センサ情報」) `s_102`, rồi ghi ra **mỗi hộ (EMS-SP) một file CSV** vào thư mục theo tuần.

Mỗi ngày batch ghi thêm dữ liệu của "8 ngày trước" vào thư mục tuần tương ứng. **Chỉ vào thứ Hai**, nó mới nén thư mục đã ghi xong thành ZIP rồi xoá cả thư mục. Đặc điểm dữ liệu: **một bản ghi = một ngày, và 24 giờ nằm ngang thành 24 cột** (00時台 → 23時台). Bộ khung xử lý giống hệt batch trạng thái thiết bị (`CreateCsvAndZipConDeviceStatusesCommand`), chỉ khác bảng đích và danh sách cột.

**Vị trí của 4 batch** (tên gọi dễ nhầm nên nói trước):

| Batch | Bảng | Tên model trong code | 1 bản ghi = | Mỗi ô giá trị = | Chu kỳ chạy |
|---|---|---|---|---|---|
| DeviceStatuses | `t_202` | 機器状態情報 | 1 lần thu thập | — | hằng ngày 05:15 |
| **HourlyValues (tài liệu này)** | `s_102` | 日毎センサ情報 | **1 NGÀY** | **1 GIỜ (24 cột)** | hằng ngày 05:15 |
| DailyValues | `s_103` | 月毎センサ情報 | 1 THÁNG | 1 NGÀY (31 cột) | mùng 1 hằng tháng, 05:15 |
| DailyAveValues | `s_113` | 月毎平均センサ情報 | 1 THÁNG | 1 NGÀY, trung bình (31 cột) | mùng 1 hằng tháng, 05:15 |

⚠️ **Tên gọi dễ gây nhầm**: "1時間値" nói về **đơn vị của giá trị** (mỗi ô = 1 giờ), **không** nói về chu kỳ chạy. Việc tên bảng (`s_102` = "theo ngày") và tên batch (Hourly = "theo giờ") trông ngược nhau là vì: tên batch chỉ **đơn vị giá trị xuất ra**, còn tên model chỉ **khoảng thời gian mà một bản ghi đại diện**.

> 📖 **Partition (phân mảnh)**: bảng lớn được chia thành nhiều bảng con theo thời gian — ở đây mỗi ngày một bảng `s_102_YYYYMMDD`. Muốn xoá dữ liệu cũ chỉ cần **DROP** (lệnh SQL xoá nguyên một bảng) bảng con đó.
>
> 📖 **EMS-SP**: mã số định danh một hộ ký hợp đồng dịch vụ EMINEL (`EMS-SP-NO`).

> **Phạm vi tài liệu này**: chỉ điều tra hành vi hệ cũ. Tài liệu **không** chứa: thiết kế thay thế cho E-GW, các bước chuyển đổi, bảng đối chiếu cũ↔mới. Phán định giữ/bỏ: khối **Kết luận** đầu tài liệu.

## Phần 1 — Tổng quan

| Mục | Nội dung |
|---|---|
| **Vai trò** | Biến giá trị cảm biến theo giờ sắp hết hạn lưu trong DB (**14 ngày**) thành **file CSV → ZIP trước khi bị xoá**. **Chỉ chép nguyên dữ liệu, không tính toán/tổng hợp gì** (chi tiết 2.5). |
| **Đầu vào** | Partition theo ngày `s_102_YYYYMMDD` của bảng `s_102` (ngày đích = ngày chạy − 8 ngày). ⚠️ Code **truyền thẳng tên partition làm alias** — `TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName)` (`…Command.php:39, 41`) — **chứ không đi qua** lớp `ConSensorHourlyValuesTable` / entity `ConSensorHourlyValue` của thư viện dùng chung (nơi định nghĩa bảng vật lý `s_102`, mô tả model 「日毎センサ情報」: `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Table/ConSensorHourlyValuesTable.php:41`). Tên cột **viết cứng** trong Command (`:108-113`).<br>*(Entity = lớp code đại diện cho một dòng dữ liệu; alias = tên gọi mà ORM dùng để trỏ tới bảng.)* |
| **Đầu ra** | File CSV/ZIP trên ổ đĩa máy chủ.<br>・CSV: `{CON_SENSOR_HOURLY_VALUES_CSV_FILES_PATH}/{đầu tuần}_{cuối tuần}/{EMS-SP}_{đầu tuần}_{cuối tuần}_1時間値.csv`<br>・ZIP: chỉ thứ Hai, nén cả thư mục thành `{đầu tuần}_{cuối tuần}.zip` |
| **Tóm tắt xử lý** | 1. Xác định ngày đích T = ngày chạy − 8, kiểm tra partition `s_102_{T:Ymd}` có tồn tại không (không có thì ghi log alert rồi kết thúc).<br>2. Lấy **danh sách EMS-SP** có trong partition đó.<br>3. Với từng hộ, mở CSV ở chế độ ghi tiếp; chỉ lần đầu mới ghi BOM UTF-8 và dòng tiêu đề 36 cột.<br>4. Đọc toàn bộ bản ghi theo trang 4.000 dòng, chỉ định dạng lại cột ngày giờ rồi ghi từng dòng.<br>5. **Chỉ khi ngày chạy là thứ Hai**: nén CSV thành ZIP và xoá cả thư mục. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy và ngày đích

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `15 5 * * *` (shell hằng ngày) **và** `15 5 1 * *` (shell mùng 1) — batch này nằm trong **cả hai** shell nên chạy 05:15 mỗi ngày. ※ Chuyện xảy ra vào mùng 1: xem khối "Mùng 1 có gì đặc biệt" ngay dưới bảng | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:40-41` (tiêu đề mục `#12.DBデータ削除` ở `:39`) |
| Lệnh chạy | `sudo -u apache php /var/www/vhost/conciergesv/bin/cake.php CreateCsvAndZipConSensorHourlyValues` (chạy dưới user `apache`) | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` — bên trong `12_CreateCsvAndDeleteData_day2to31.sh` (file `_day1.sh` cũng có dòng y hệt) |
| Tham số | `--datetime` (mặc định `'now'`) | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorHourlyValuesCommand.php:28, 36` |
| **Ngày đích T** | `thời điểm chạy − 8 ngày` → tên partition `s_102_{T:Ymd}` | cùng file `:39` |
| Khoảng thời gian của thư mục | **Thứ Hai → Chủ nhật** của tuần chứa T (`startOfWeek()` / `endOfWeek()`) | cùng file `:56-58` |
| Thời điểm nén ZIP | **Chỉ khi ngày chạy là thứ Hai** (`isMonday()`); đối tượng là thư mục của tuần chứa T = **tuần trước nữa** so với ngày chạy | cùng file `:137-145` |

⚠️ Comment trong code (cùng file `:136`「先週の CSV ファイル」= "CSV của tuần trước") ghi **sai** — thực tế nén thư mục của **tuần trước nữa**. (Batch trạng thái thiết bị cũng có đúng comment này.)

Ví dụ cụ thể: chạy thứ Hai 09/09 → T = 01/09 (Chủ nhật) → thư mục bị nén là `20240826_20240901`. Vì T rơi đúng vào ngày cuối của thư mục ấy, lúc nén **luôn đủ trọn 7 ngày**.

**Đọc dòng cron thế nào**: 5 trường là `phút giờ ngày-trong-tháng tháng thứ`. `15 5 * * *` = 05:15 **mọi ngày**; `15 5 1 * *` = 05:15 **chỉ mùng 1**.

**Mùng 1 có gì đặc biệt** — 3 điểm:

1. Tên file `…day2to31.sh` **gây hiểu nhầm**: trường ngày của nó là `*`, tức chạy **mọi ngày 1–31**, không phải "từ ngày 2".
2. Vì vậy **riêng mùng 1 batch chạy 2 lần** (`_day1.sh` và `_day2to31.sh` cùng nổ lúc 05:15).
3. `flock` **không chặn** được cú 2 lần đó (lý do ở đoạn dưới). 🔸 CSV mở chế độ ghi tiếp nên **có thể** ghi lặp dữ liệu — *suy đoán, chưa kiểm chứng trên môi trường thật; cần thì hỏi mui*.

**Bao lâu sau khi thành file thì dữ liệu bị xoá khỏi DB?**

| Batch | Ghi ra file vào | DB bị DROP vào | Khoảng đệm |
|---|---|---|---|
| DeviceStatuses (`t_202`, giữ 8 ngày) | dữ liệu ngày D → D+8 | D+9 | 1 ngày |
| **HourlyValues (`s_102`, giữ 14 ngày — tài liệu này)** | **D+8** | **D+15** | **7 ngày** |
| DailyValues / DailyAveValues (`s_103`/`s_113`) | tháng trước nữa | cùng tháng đó, cùng một lần chạy | 0 |

`s_102` được giữ lâu hơn `t_202` (14 ngày so với 8 ngày) nhưng việc CSV hoá vẫn làm ở mốc "8 ngày trước", nên kết quả là file có trước lúc xoá 7 ngày. 🔸 Đó có phải chủ ý thiết kế hay không thì code và tài liệu thiết kế đều không nói.

> Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:49` (`$this->dropDailyTable('s_102', $dateTimeForDay, 14);`), ngày bị xoá tính ở `:85` (`$dateTime->subDays($keepDays + 1)`). `t_202` ở `:47`; `s_103`/`s_113` ở `:53, 54` và `:110`.

**Chống chạy chồng và hành vi khi lỗi**: shell dùng `flock -n` để chặn chạy chồng. Nhưng thứ bị khoá là **chính file script đang chạy** (`exec {my_fd}< "$0"` — `$0` là đường dẫn của chính script). Vì thế nó chỉ chặn được "một shell tự chạy chồng lên mình", **không chặn được trường hợp mùng 1 khi `_day1.sh` và `_day2to31.sh` cùng khởi động**. Kèm theo, `set -eu` khiến hễ một lệnh lỗi là dừng cả shell, nên sinh CSV lỗi thì không bao giờ tới `DeleteData`.

> Nguồn: cùng file tgz, `12_CreateCsvAndDeleteData_day2to31.sh` (`flock -n ${my_fd}` / `set -eu` / `trap error_handler ERR`)
> Chủ ý thiết kế được ghi thẳng trong `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:29-32` mục 補足1 (câu trích ở `:32`): 「CSV作成が失敗した場合はDBのデータを消去するコマンドは実施されない。」 — *nếu tạo CSV thất bại thì lệnh xoá dữ liệu DB sẽ không được thực hiện*.

### 2.2 Lấy dữ liệu

Batch không viết SQL trực tiếp mà đọc qua **ORM** của CakePHP — lớp trung gian cho phép thao tác DB bằng code đối tượng thay vì viết SQL tay. Khối dưới chứng minh 2 điều: ⓪ ORM được trỏ thẳng vào **bảng con của ngày đích**, và ①② dữ liệu được đọc theo từng hộ, chia trang 4.000 dòng.

```php
// ⓪ Ghép tên partition từ ngày đích rồi trỏ ORM vào đúng bảng con đó
$partitionTableName    = 's_102_' . $dateTime->subDays(8)->format('Ymd');
$conSensorHourlyValues = TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName);

// ① Danh sách EMS-SP có trong partition đích
$c001Values = $conSensorHourlyValues->find()
    ->select(['c001'])
    ->distinct(['c001'])
    ->all();

// ② Với từng hộ, lấy toàn bộ bản ghi theo trang 4.000 dòng
$targetDatas = $conSensorHourlyValues->find()
    ->where(['c001' => $c001Value->c001])
    ->limit($pageSize)      // $pageSize = 4000
    ->page($page)
    ->all();
```
Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorHourlyValuesCommand.php:39, 41` (⓪) · `:49-52` (①) · `:98-102` (②) · `:55` (`$pageSize = 4000`).

**Vì sao không lọc theo ngày**: bản thân bảng đích đã là `s_102_YYYYMMDD` — **mỗi partition đúng một ngày** — nên chọn xong bảng là ngày đã cố định.

**Ánh xạ cột CSV ↔ cột DB** (suy ra từ việc `$columnNames` và `$headers` xếp cùng thứ tự). Cột **Tên cột CSV** giữ nguyên tiếng Nhật vì đây chính là chuỗi in ra ở dòng tiêu đề file CSV; cột **Ý nghĩa** là phần dịch/giải thích:

| Tên cột CSV | Cột DB | Ý nghĩa |
|---|---|---|
| EMS-SP | `c001` | Mã hộ (EMS-SP-NO) |
| 機器種別 | `c002` | Mã loại thiết bị |
| 設置場所 | `c003` | Mã vị trí lắp đặt |
| 対象年月日 | `c004` | **Ngày** mà bản ghi này đại diện (**kiểu ngày giờ → có định dạng lại**) |
| 消費電力量遡及フラグ | `c008` | Cờ hồi tố (*hồi tố = tính lại và ghi đè số liệu của kỳ đã chốt*) cho **lượng điện tiêu thụ**; hằng số `C_NEED_ELE_COMPLETE_FLAG` (`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorHourlyValue.php:57`, có mặt trong mảng `_accessible` ở `:100`). 🔸 Trong toàn bộ `conciergesv-develop/src` và `eminel_sv_lib-develop/src` **không có đoạn code nào đọc hay ghi hằng số này**, nên ý nghĩa từng giá trị chưa kiểm chứng được — cần hỏi mui |
| 集計遡及フラグ | `c009` | **Cờ công việc** báo cho tầng tổng hợp bên trên biết dữ liệu quá khứ đã được tính lại: **1 = cần tổng hợp lại → 2 = tầng trên đã phản ánh xong**. Hằng số `C_NEED_AGG_COMPLETE_FLAG` (cùng file `:58`); chuyển trạng thái ở `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CalcMonthlyAccumulatedValueCommand.php:220` (lọc `= 1`) rồi `:213` (đặt `= 2`). ※ Ở `:267` và `:282` cùng file cờ cũng được đặt `= 1` nhưng trên **`ConSensorDailyValue`** — tức `c009` của `s_103`, không phải `s_102` |
| グループ属性1〜5 | `c111`–`c115` | 5 thuộc tính dùng để gom nhóm (so sánh với hộ khác) |
| 00時台〜23時台 | `c011`–`c034` | **24 giờ trong ngày nằm ngang thành 24 cột** |
| 更新日時 | `c041` | Thời điểm cập nhật bản ghi (**kiểu ngày giờ → có định dạng lại**) |

> Nguồn: cùng file `:84-90` (tiêu đề CSV 36 cột) · `:108-113` (36 tên cột DB).
> Cách cộng số cột: 6 + 5 + 24 + 1 = **36 cột**.

**Điểm cần lưu ý về cấu trúc dữ liệu**: `s_102` là "một bản ghi = một hộ · một thiết bị · một ngày", và 24 giá trị theo giờ nằm **ngang (24 cột)** chứ không phải dọc (24 dòng). Khi chuyển sang hệ mới, việc giữ nguyên kiểu ngang này hay đổi sang kiểu dọc theo mốc giờ sẽ dẫn tới hai thiết kế khác nhau.

### 2.3 Logic sinh CSV

```
① Xác định thư mục đầu ra:  {CON_SENSOR_HOURLY_VALUES_CSV_FILES_PATH}/{đầu tuần Ymd}_{cuối tuần Ymd}
   └ Chưa có thì mkdir (quyền 0777; tạm đặt umask = 0 — bộ lọc quyền mặc định của Linux —
     rồi trả lại giá trị cũ)

② Lặp theo từng hộ:
   Tên file = {EMS-SP}_{đầu tuần Ymd}_{cuối tuần Ymd}_1時間値.csv
   fopen(..., 'a')  ← chế độ GHI TIẾP (batch chạy mỗi ngày, dồn vào cùng thư mục tuần)

   ├ Chỉ khi file mới tạo, hoặc kích thước = 0:
   │    Ghi BOM UTF-8 (\xEF\xBB\xBF) — 3 byte đánh dấu đầu file, báo cho phần mềm đọc
   │       biết đây là UTF-8
   │       (🔸 code chỉ ghi comment "UTF-8 BOM 形式"; nói đây là để Excel không lỗi font
   │          là suy đoán)
   │    Ghi dòng tiêu đề 36 cột
   │
   └ Đọc theo trang 4.000 dòng, ghi từng bản ghi:
        Chỉ c004 (ngày đích) và c041 (thời điểm cập nhật)
            → định dạng 'Y-m-d H:i:s.v' + 3 ký tự đầu của múi giờ
            → ra chuỗi dạng: 2024-09-02 05:15:00.123 +09 (`.v` là phần mili-giây)
        Các cột còn lại ghi nguyên giá trị

③ Chỉ khi ngày chạy là thứ Hai: nén *.csv trong thư mục thành ZIP (xem 2.4)
```
Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorHourlyValuesCommand.php:56-65` (①) · `:68-82` (tên file và BOM ở ②, comment ở `:81`) · `:116-132` (ghi dòng và định dạng ngày giờ) · `:137-145` (③).

**Hằng số nghiệp vụ · biến môi trường**:

| Tên | Giá trị | Nguồn |
|---|---|---|
| `CON_SENSOR_HOURLY_VALUES_CSV_FILES_PATH` | `/var/data/ConSensorHourlyValues/` | `legacy_eminel_docs/sources/conciergesv-develop/config/.env.prod:63` (các file `.env.dev` / `.env.stage` / `.env.local` cùng giá trị) |
| `$pageSize` | 4000 (comment trong code: "một lần xử lý bao nhiêu bản ghi; vagrant tối đa 4000") | `…/CreateCsvAndZipConSensorHourlyValuesCommand.php:54-55` |
| Độ lệch ngày đích | 8 ngày | cùng file `:39` |

### 2.4 Nơi ghi ra và việc nén ZIP

**Cấu trúc thư mục**:

```
/var/data/ConSensorHourlyValues/            ← chạy nhiều lần thì các ZIP tuần xếp cạnh nhau
│                                              (bản cũ KHÔNG bị xoá)
├── 20240902_20240908/                      ← thư mục tuần (thứ Hai → Chủ nhật)
│   ├── 00000000001_20240902_20240908_1時間値.csv
│   ├── 00000000002_20240902_20240908_1時間値.csv
│   └── …(bao nhiêu hộ thì bấy nhiêu CSV)
└── 20240826_20240901.zip                   ← thư mục tuần liền trước nó: đã nén vào đúng thứ Hai
    │                                          ghi xong dữ liệu cuối tuần đó (thư mục bị xoá)
    └─ bên trong: 00000000001_20240826_20240901_1時間値.csv.zip
                  …(bao nhiêu hộ thì bấy nhiêu ZIP con)
```

※ EMS-SP được kiểm tra **tối thiểu 11 chữ số** (`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Table/EmsSpNosTable.php:69` — `minLength('ems_sp_no', 11, …)`, thông báo lỗi 「有効な11桁の数字を入力してください」; **không có** rule `maxLength`). Màn hình quản trị cắt đúng 11 ký tự đầu tên file để lọc (`legacy_eminel_docs/sources/eminelsv-develop/src/Controller/DownloadController.php:338`) nên thực dụng coi như 11 chữ số.

**Các bước nén** (dùng chung trait `CreateZipsTrait::createZip` — *trait = khối code dùng chung giữa nhiều lớp trong PHP*):

```
① Nén từng CSV thành ZIP riêng → {tên file}.csv.zip
   └ Tên file bên trong ZIP đổi sang SJIS — bảng mã chữ Nhật cũ của Windows
      ← 🔸 code không có comment giải thích; suy đoán là để phần mềm giải nén
         trên Windows không làm hỏng tên file tiếng Nhật
② Xoá (unlink) các CSV gốc
③ Gộp toàn bộ ZIP con vào một ZIP của cả thư mục → {thư mục tuần}.zip
④ exec("rm -rf {thư mục tuần}") xoá luôn thư mục
   └ Mỗi bước nếu lỗi đều ghi log alert và ném Exception (không chấp nhận thành công một nửa)
→ Sau bước ④ trên đĩa chỉ còn MỘT file {tuần}.zip. KHÔNG mất dữ liệu — mọi CSV nằm
   trong ZIP đó (2 lớp: ZIP thư mục ⊃ ZIP từng CSV)
```
Nguồn: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateZipsTrait.php:23-72` (`rm -rf` ở `:64`; nó chỉ xoá thư mục tuần, các file `.zip` ở tầng trên vẫn còn).

**Ai dùng file sinh ra**: chức năng tải "dữ liệu quá khứ" của màn hình quản trị cũ `eminelsv`. Lựa chọn `previous_hour_value` (tên hiển thị 「1時間値（過去データ）」) trỏ vào thư mục đầu ra của batch này.

> Nguồn: `legacy_eminel_docs/sources/eminelsv-develop/src/Controller/DownloadController.php:73` (tên hiển thị) · `:418` (`'previous_hour_value' => env('HOUR_VALUE_DIRECTORY')`) · `legacy_eminel_docs/sources/eminelsv-develop/config/.env.prod:86` (`HOUR_VALUE_DIRECTORY = "/var/data/ConSensorHourlyValues/"` — trùng đúng đường dẫn phía batch).
> Màn hình quản trị chỉ lọc các ZIP có sẵn theo ngày và EMS-SP rồi đóng gói lại để trả về (cùng file `:236` `createPreviousDataZip()` — một hàm dùng chung cho cả 4 lựa chọn; quét bằng `RecursiveDirectoryIterator` ở `:298`, lọc theo ngày ở `:277-282`). Điểm quan trọng: **nó không dựng lại dữ liệu từ DB, mà chỉ phát lại file do batch này tạo ra**.

### 2.5 Xác nhận: batch này không tính toán/tổng hợp

Batch không tính toán hay tổng hợp giá trị nào — giá trị theo giờ đã được batch tổng hợp khác ghi sẵn vào `s_102`, batch này chỉ chép sang CSV. Vì vậy điểm cần bàn khi chuyển hệ thu về: **dữ liệu quá thời hạn lưu (14 ngày) thì giữ lại bằng cách nào.**

> Phán định (có giữ batch không, hệ mới thay bằng gì) nằm ở bảng tổng hợp `summary_batch_migration_ja.md` (cùng thư mục), dòng của batch này. Kết luận: **"không cần giữ batch"** — hệ mới dùng F-AD-09.
