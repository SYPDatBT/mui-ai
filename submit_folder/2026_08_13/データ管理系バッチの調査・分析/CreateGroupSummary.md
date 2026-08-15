# CreateGroupSummaryCommand（グループサマリー作成）

## Tóm tắt

`CreateGroupSummaryCommand` là batch cron chạy hàng ngày (02:10) trên server `conciergesv`: phân khúc
toàn bộ khách hàng theo tổ hợp 5 thuộc tính hộ gia đình (loại nhà, công suất máy sưởi, diện tích sàn, số
người trong gia đình, có đồng phát khí gas hay không — mỗi thuộc tính được "bucket hóa" qua `CASE WHEN`
thành nhóm ít giá trị hơn), tính **số lượng khách hàng (population)** trong mỗi phân khúc rồi lưu vào
bảng sensor-value dùng chung dưới mã `device_type=16` ("グループ母数" = số lượng nhóm — 1 device_type
chính thức, không phải hack), đồng thời lưu lại **lịch sử phân khúc của từng khách hàng theo tháng**.
Đây là dữ liệu nền cho tính năng "so sánh mức sử dụng với nhóm khách hàng tương tự" hiển thị trong app
(xác nhận qua `GetUsageController.php` — đọc lại đúng 2 bảng này để tính trung bình nhóm). Ở repo mới
`syp-eminelstandard-backend`, **không tìm thấy chức năng tương đương**: không có bảng DynamoDB nào lưu
theo tổ hợp nhóm/`device_type` đặc biệt (đã soát toàn bộ ~46 bảng trong `template-dynamodb.yaml`),
không có Lambda nào tính "average theo nhóm" (grep `average`/`Average` trên toàn `src/` ra 0 kết quả),
và cơ chế thuộc tính hộ gia đình duy nhất hiện có (`app_household_num`, `app_total_floor_area`,
`IAttributeCondition`) chỉ dùng để **lọc đối tượng nhận push notification** (targeting), không phải để
tính population/average rồi hiển thị so sánh cho user. Tính năng "so sánh mức sử dụng với nhóm tương
tự" dường như chưa được port sang hệ thống mới.

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `CreateGroupSummaryCommand` (extends `BaseCommand`) · Tên lệnh gọi: `create_group_summary` *(suy đoán theo quy ước CakePHP 4, không có override tường minh trong file)* · Script cron: `14_CreateGroupSummary.sh` · Tên tiếng Nhật trong cron: "14.グループ集計情報登録機能" (chức năng đăng ký thông tin tổng hợp nhóm). |
| **Vai trò** | Phân khúc khách hàng theo 5 thuộc tính hộ gia đình, tính population mỗi phân khúc + lưu lịch sử phân khúc từng khách hàng — dữ liệu nền cho tính năng "so sánh với nhóm tương tự" trong app. |
| **Input** | Đọc bảng khách hàng `t_101` (`ConCustomers`) qua 2 câu SQL riêng biệt (khác điều kiện lọc — xem A.2.2). Tham số dòng lệnh: `--date` (ngày tính, mặc định hôm nay), `--aggregateFlag` (cờ chạy daily/monthly, mặc định cả 2). |
| **Output** | Ghi bảng `s_113` (`ConSensorDailyAveValues`, cột theo NGÀY trong tháng) khi cờ daily active; ghi bảng `s_114` (`ConSensorMonthlyAveValues`, cột theo THÁNG trong năm) + bảng `s_151` (`ConUserGroupHistories`, 1 dòng/khách hàng/tháng) khi cờ monthly active. Toàn bộ trong 1 transaction. |
| **Khái quát xử lý** | 1. Parse + validate tham số → xác định ngày tính thật + cờ daily/monthly cần chạy (có nhánh rẽ, xem cây quyết định A.2.1).<br>2. Mở transaction.<br>3. Tính population mỗi phân khúc khách hàng (population aggregation, dùng tập khách hàng đã lọc theo range hợp lệ).<br>4. Nếu cờ daily: ghi population vào cột-theo-ngày của `s_113`.<br>5. Nếu cờ monthly: ghi population vào cột-theo-tháng của `s_114`, rồi lấy TOÀN BỘ khách hàng chưa xóa (không lọc theo range thuộc tính), ghi lịch sử phân khúc từng khách hàng vào `s_151`.<br>6. Commit nếu mọi bước OK, rollback nếu có bước lỗi. |

## A.2 Chi tiết

**Bản đồ cách tính — 4 bước, 2 luồng ghi riêng dùng chung 1 bước tính population:**

```
[--date, --aggregateFlag]
        │
        ▼
  checkValidate() ── cây quyết định (A.2.1) ── ra: ngày tính thật + cờ [daily?, monthly?]
        │
        ▼
  populationAggregation() (A.2.2) ── SQL COUNT+GROUP BY trên t_101, lọc theo range hợp lệ
        │  → mỗi dòng: (population, device_type=16, room_id=0, ngày, 5 group-attr đã bucket)
        │
        ├─ nếu cờ daily  ──▶ updateMonthlyAverage() (A.2.3) ──▶ ghi cột NGÀY vào s_113
        │
        └─ nếu cờ monthly ─▶ updateYearlyAverage() (A.2.4) ──▶ ghi cột THÁNG vào s_114
                              │
                              ▼
                          getCustomers() ── SQL khác, KHÔNG lọc theo range (chỉ lọc chưa xóa)
                              │
                              ▼
                          updateGroupHistory() (A.2.4) ──▶ ghi 1 dòng/khách hàng vào s_151
```

| Bước | Mục chi tiết |
|---|---|
| Validate tham số + cây quyết định ngày/cờ | §A.2.1 |
| Tính population theo phân khúc | §A.2.2 |
| Ghi population theo ngày (nhánh daily) | §A.2.3 |
| Ghi population theo tháng + lịch sử từng khách hàng (nhánh monthly) | §A.2.4 |

### A.2.1 Validate tham số & cây quyết định xác định ngày tính + cờ chạy

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `10 2 * * *` — hàng ngày 02:10, comment "14.グループ集計情報登録機能" | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:48-49` |
| Tham số `--aggregateFlag` | Không truyền → mặc định `[1,2]` (cả daily=`DAILY_AGGREGATION` và monthly=`MONTHLY_AGGREGATION`). Truyền → parse chuỗi `int` phân tách bởi `,`; mỗi giá trị phải là `1` hoặc `2`, sai → lỗi validate. | `CreateGroupSummaryCommand.php:376-387`; hằng số `const.php:609,611` |
| Tham số `--date` | Không truyền → hôm nay (`FrozenDate::now()`). Truyền → phải khớp regex `^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$` (`yyyy-MM-dd`), sai format → lỗi validate. | `:389-402` |

Sau khi có ngày hợp lệ (`checkDateTime`) và cờ hợp lệ, code rẽ nhánh để quyết định **ngày tính thực sự
dùng cho toàn bộ batch** (`returnDateTime`):

```
                    ┌─ cờ monthly ACTIVE? ──── CÓ ──▶ returnDateTime = checkDateTime (giữ nguyên)
                    │
ngày hợp lệ ────────┤
                    │                          CÓ ──▶ returnDateTime = checkDateTime lùi 1 tháng
                    └─ cờ monthly TẮT? ──── ngày = "01"? ──▶ ép thêm cờ monthly vào danh sách cờ
                                             │
                                             KHÔNG (ngày ≠ "01")
                                             ▼
                                       returnDateTime = '' (RỖNG — xem ⚠️ bên dưới)
```

| Nhánh | Điều kiện | Kết quả | Ý nghĩa |
|---|---|---|---|
| 1 | Cờ monthly có trong danh sách (mặc định luôn đúng vì cờ mặc định = cả 2) | `returnDateTime` = ngày đã validate, giữ nguyên | Chạy monthly thì lấy đúng tháng của ngày được chỉ định làm tháng tính |
| 2 | Cờ monthly KHÔNG có, và ngày đã validate là ngày **01** | `returnDateTime` = ngày đã validate **lùi 1 tháng**, đồng thời tự thêm `MONTHLY_AGGREGATION` vào cờ | Nếu chỉ định daily-only đúng ngày 1 đầu tháng → hệ thống tự hiểu là "cần tổng kết luôn tháng vừa xong" (tháng trước), ép chạy thêm cả monthly |
| 3 | Cờ monthly KHÔNG có, và ngày đã validate KHÁC ngày 01 | `returnDateTime` = chuỗi rỗng `''` | Xem **⚠️ Điểm bất thường** dưới đây |

Nguồn: `CreateGroupSummaryCommand.php:405-418`.

**⚠️ Điểm bất thường của hệ cũ — `returnDateTime` bị bỏ rỗng ở Nhánh 3:**

- Điều kiện tái hiện: gọi command với `--aggregateFlag=1` (chỉ daily, tắt monthly) vào bất kỳ ngày nào
  **khác ngày 1 đầu tháng** — ví dụ `--aggregateFlag=1 --date=2026-08-15`.
- Code chỉ xử lý rõ 2 trong 3 tổ hợp (monthly active; monthly tắt + ngày=01) — thiếu nhánh `else` cho
  "monthly tắt + ngày≠01" nên biến `$returnDateTime` giữ giá trị khởi tạo là chuỗi rỗng (`:405`), khiến
  `$this->dateTime = ''` được dùng xuyên suốt các bước tính sau đó (`populationAggregation()`,
  `updateMonthlyAverage()` đều gọi `FrozenDate::parse($this->dateTime)`).
- Hệ quả cụ thể *(suy đoán dựa theo hành vi công khai của CakePHP/Chronos — không xác minh được trong
  repo này vì framework không nằm trong repo)*: `FrozenDate::parse('')` nhiều khả năng trả về ngày giờ
  hiện tại (hành vi mặc định của PHP `DateTime`/Chronos khi parse chuỗi rỗng) — nghĩa là tham số `--date`
  người dùng truyền vào bị **lặng lẽ bỏ qua**, batch chạy như thể không truyền `--date`, thay vì báo lỗi
  hoặc dùng đúng giá trị đã validate.
- Không ảnh hưởng lịch cron thật (cron chạy không tham số hoặc chỉ với cờ mặc định → luôn có monthly
  active → luôn rơi vào Nhánh 1) — chỉ là rủi ro khi vận hành chạy tay bù dữ liệu với `--aggregateFlag=1`
  cho 1 ngày cụ thể không phải ngày 1.

### A.2.2 Tính population theo phân khúc khách hàng (population aggregation)

```sql
-- Sub-query: bucket hóa 4/5 thuộc tính, lọc khách hàng nằm trong "range hợp lệ"
SELECT
  customers.c001, customers.c012,
  CASE WHEN customers.c042 IN (1, 2, 3) THEN customers.c042 ELSE 201 END AS c042,
  CASE WHEN customers.c015 IN (1, 2, 3) THEN 301
       WHEN customers.c015 IN (5, 6) THEN 302
       ELSE customers.c015 END AS c015,
  CASE WHEN customers.c016 IN (1, 2) THEN 401
       WHEN customers.c016 IN (3, 4) THEN 402
       ELSE 403 END AS c016,
  CASE WHEN customers.c024 IN (1, 2) THEN customers.c024 ELSE 501 END AS c024
FROM t_101 AS customers
WHERE (
  c012 IN (1, 2) AND c042 IN (1, 2, 3, 4, 9) AND c015 IN (1, 2, 3, 4, 5, 6) AND
  c016 IN (1, 2, 3, 4, 5, 6) AND c024 IN (1, 2, 9, 10) AND c052 IS NULL)

-- Outer query: đếm population theo tổ hợp 5 thuộc tính đã bucket
SELECT COUNT(groupSub.c001) AS population,
  16 AS c001, 0 AS c002, '{ngày tính}' AS c003,
  groupSub.c012, groupSub.c042, groupSub.c015, groupSub.c016, groupSub.c024
FROM (...) AS groupSub
GROUP BY groupSub.c012, groupSub.c042, groupSub.c015, groupSub.c016, groupSub.c024
```
Nguồn: `CreateGroupSummaryCommand.php:220-264`.

| Cột `t_101` | Ý nghĩa | Cách bucket hóa (dùng làm `group_attr#`) |
|---|---|---|
| `c001` (`C_EMS_SP`) | Mã khách hàng | Không dùng để nhóm, chỉ để COUNT |
| `c012` (`C_BUILD_TYPE`) | Loại nhà | **Không bucket** — giữ giá trị gốc → `group_attr1`. WHERE giới hạn chỉ nhận giá trị 1 hoặc 2 (loại khác bị loại khỏi population hoàn toàn) |
| `c042` (`C_HEATER_POWER`) | Công suất máy sưởi | `{1,2,3}` giữ nguyên, còn lại (trong range hợp lệ `{1,2,3,4,9}`, tức chỉ có `4` và `9`) → bucket `201` → `group_attr2` |
| `c015` (`C_GROSS_FLOOR_SPACE`) | Diện tích sàn | `{1,2,3}`→`301`, `{5,6}`→`302`, còn lại (chỉ có `4`, do range hợp lệ `{1..6}`)→ giữ nguyên `4` → `group_attr3` |
| `c016` (`C_FAMILY_SIZE`) | Số người trong gia đình | `{1,2}`→`401`, `{3,4}`→`402`, còn lại (`{5,6}`, do range hợp lệ `{1..6}`)→`403` → `group_attr4` |
| `c024` (`C_GAS_COGENERATION`) | Có đồng phát khí gas | `{1,2}` giữ nguyên, còn lại (chỉ có `9,10`, do range hợp lệ `{1,2,9,10}`)→`501` → `group_attr5` |
| `c052` (`C_DELETED`) | Thời điểm xóa | Lọc `IS NULL` — chỉ tính khách hàng chưa bị xóa mềm |

**Ví dụ chạy tay** *(số liệu minh họa giả định, không phải dữ liệu thật)* — 4 khách hàng:

| Khách hàng | c012 | c042 | c015 | c016 | c024 | c052 |
|---|---|---|---|---|---|---|
| KH1 | 1 | 2 | 2 | 1 | 1 | NULL |
| KH2 | 1 | 9 | 5 | 3 | 9 | NULL |
| KH3 | 2 | 1 | 4 | 2 | 2 | NULL |
| KH4 | **3** | 1 | 1 | 1 | 1 | NULL |

- KH1 → bucket `(1, 2, 301, 401, 1)`, population = 1.
- KH2 → bucket `(1, 201, 302, 402, 501)`, population = 1.
- KH3 → bucket `(2, 1, 4, 401, 2)`, population = 1.
- **KH4 bị loại khỏi câu SQL này hoàn toàn** vì `c012=3` không nằm trong `WHERE c012 IN (1,2)` — không
  góp vào population của bất kỳ bucket nào, dù vẫn là khách hàng hợp lệ (chưa xóa). Xem hệ quả ở
  §A.2.5.

### A.2.3 Ghi population theo ngày (nhánh daily) — bảng `s_113`

- Chỉ chạy khi cờ `DAILY_AGGREGATION` active. Với mỗi dòng population đã tính ở A.2.2:
  `targetDate` = ngày 01 của tháng đang tính (`yyyy/MM/01`); `dayColumnName` = `c` + `(ngày trong tháng + 10)`
  0-pad 3 chữ số — ví dụ ngày 12 → `c022`, ngày 1 → `c011`, ngày 31 → `c041`
  (khớp hằng số cột `C_VALUE_1..C_VALUE_31` của entity `ConSensorDailyAveValue`).
- Tạo `new ConSensorDailyAveValue()` với `device_type=16` (giá trị cố định — theo
  `docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/補足資料/機器種別一覧.txt`, mã 16 =
  **"グループ母数"** = "population của nhóm" — đây là 1 mã `device_type` **chính thức**, không phải số
  ma thuật tự chế), `room_id=0` (tái dùng hằng số `DETECT_LIVING=0`, `const.php:228` — vốn là mã phòng
  dùng cho cảm biến chuyển động phòng khách, ở đây chỉ dùng làm placeholder "không theo phòng cụ thể"),
  `datetime=targetDate`, `group_attr1..5` = 5 giá trị đã bucket, `{dayColumnName}` = population count.
- `->save()` trên bảng `s_113` — PK của bảng là `(c001,c002,c003,c111,c112,c113,c114,c115)` = `(device_type,
  room_id, tháng, 5 group_attr)`, **không có cột ngày trong PK** — nghĩa là mỗi ngày trong cùng 1 tháng
  cùng ghi vào **CÙNG 1 dòng** (chỉ khác cột `{dayColumnName}` được set), tích lũy dần 31 cột ngày trong
  1 dòng/tháng/phân khúc. *(Hành vi insert-vs-update dựa vào cơ chế "check tồn tại theo PK trước khi
  save" mặc định của CakePHP ORM — không có `beforeSave`/upsert tường minh nào trong repo, đây là suy
  đoán theo kiến thức framework, không xác minh trực tiếp được vì code framework không nằm trong repo.)*
- Lỗi ở BẤT KỲ dòng nào trong loop (bắt bằng try/catch, log `alert`) → toàn bộ nhánh daily coi như thất
  bại, rollback + kết thúc batch ngay (không chạy tiếp nhánh monthly). (`:99-119,321-362`)

### A.2.4 Ghi population theo tháng + lịch sử từng khách hàng (nhánh monthly) — bảng `s_114` + `s_151`

- Chỉ chạy khi cờ `MONTHLY_AGGREGATION` active.
- **Ghi `s_114`** (`updateYearlyAverage`, tên hàm dùng từ "Yearly" nhưng bảng đích tên class chứa chữ
  "Monthly" — xem giải thích quy ước tên ở cuối mục này): `targetYear` = năm của ngày tính (kiểu `int`,
  khác `s_113` dùng `FrozenDate`); `monthColumnName` = `c` + `(tháng + 10)` 0-pad 3 chữ số — tháng 1→`c011`
  (=Tháng 1), tháng 8→`c018` (=Tháng 8), khớp hằng số `C_VALUE_JANUARY..C_VALUE_DECEMBER` của entity
  `ConSensorMonthlyAveValue`. PK bảng `s_114` = `(device_type, room_id, năm, 5 group_attr)` — cùng cơ chế
  tích lũy theo cột như `s_113`, nhưng đơn vị tích lũy là THÁNG trong 1 NĂM (thay vì NGÀY trong 1 THÁNG).
  (`CreateGroupSummaryCommand.php:272-313`)
- **Quy ước tên gây nhầm** *(không phải bug, chỉ là cách đặt tên lệch giữa 2 tầng)*: `ConSensorDailyAveValue`
  (đích của nhánh daily, bảng `s_113`) có doc comment tiếng Nhật "月毎平均センサ情報" (thông tin sensor
  trung bình THEO THÁNG), còn `ConSensorMonthlyAveValue` (đích của nhánh monthly, bảng `s_114`) có doc
  comment "年毎平均センサ情報" (thông tin sensor trung bình THEO NĂM). Tên class tiếng Anh đặt theo ĐƠN VỊ
  CỘT (daily = cột theo ngày, monthly = cột theo tháng), còn doc comment tiếng Nhật mô tả theo ĐƠN VỊ 1
  DÒNG (1 dòng = 1 tháng, hay 1 dòng = 1 năm) — 2 cách gọi tên lệch nhau 1 cấp, dễ nhầm khi đọc lướt.
- **Ghi `s_151`** (`updateGroupHistory`): sau khi ghi `s_114` thành công, gọi `getCustomers()` — câu SQL
  **KHÁC** câu ở A.2.2, chỉ lọc `WHERE c052 IS NULL` (chưa xóa), **không** lọc theo range hợp lệ của 5
  thuộc tính (`CreateGroupSummaryCommand.php:192-200`). Với MỖI khách hàng trả về, tạo 1 dòng
  `ConUserGroupHistory`: `ems_sp`=mã khách hàng, `month`=ngày 01 đầu tháng đang tính, `group_attr1..5` =
  **giá trị GỐC chưa bucket** của khách hàng (`c012,c042,c015,c016,c024` trực tiếp, không qua `CASE WHEN`
  nào — khác với A.2.2 chỉ bucket 4/5 thuộc tính). PK bảng `s_151` = `(ems_sp, month)` → mỗi khách hàng
  chỉ có đúng 1 dòng lịch sử/tháng, ghi đè nếu chạy lại đúng tháng đó *(cùng suy đoán cơ chế upsert như
  trên)*. (`:151-181,188-213`)
- Mục đích cuối của bảng `s_151`, xác nhận qua doc comment entity: "アプリのグループ平均表示のための情報。
  該当ユーザの過去月に所属したグループを保持する。" (thông tin để hiển thị trung bình nhóm trong app; giữ
  lại nhóm mà khách hàng đó thuộc về trong các tháng trước) — và xác nhận thêm bằng cách tìm nơi ĐỌC LẠI
  2 bảng `s_113`/`s_114`+`s_151`: `GetUsageController.php` (API lấy usage cho app) JOIN
  `ConUserGroupHistories` với `ConSensorMonthlyAveValues`/`ConSensorDailyAveValues` theo
  `device_type=16` + cùng tổ hợp `group_attr` (bucket hóa LẠI ngay trong câu JOIN, y hệt logic A.2.2) để
  lấy giá trị trung bình nhóm hiển thị cho khách hàng. (`GetUsageController.php:356-442,799-826`)

### A.2.5 Điểm đặc biệt / Rủi ro

- **Bất đối xứng bộ lọc khách hàng giữa 2 câu SQL** — `populationAggregation()` (A.2.2) chỉ tính population
  từ khách hàng có ĐỦ 5 thuộc tính nằm trong "range hợp lệ" (`c012 IN(1,2)` là chặt nhất); `getCustomers()`
  (A.2.4, phần `s_151`) lấy TẤT CẢ khách hàng chưa xóa, không lọc theo range đó. Hệ quả: khách hàng có
  thuộc tính "lệch" (ví dụ `c012=3`, không phải 1/2 — xem ví dụ KH4 ở A.2.2) vẫn được ghi 1 dòng lịch sử
  nhóm ở `s_151` với `group_attr1=3`, nhưng **không có bucket population nào khớp `group_attr1=3`** ở
  `s_113`/`s_114` (vì bị loại khỏi population từ đầu) → khi app join để lấy trung bình nhóm cho khách
  hàng này, kết quả sẽ rỗng/NULL (LEFT JOIN không khớp) — khách hàng có lịch sử nhóm nhưng không bao giờ
  thấy được số liệu trung bình nhóm tương ứng.
- **Cơ chế chống chạy trùng ở tầng ứng dụng** (không riêng batch này) — `BaseCommand` (class cha) tạo file
  `.lock` theo tên class trong `TMP`, kiểm tra PID còn sống hay không trước khi chạy; nếu instance trước
  còn sống thì instance mới **exit ngay, không log lỗi rõ ràng**. Cơ chế này dùng chung bởi 19 Command
  khác trong `conciergesv` (đếm thật qua grep `extends BaseCommand`), không phải riêng cho batch này —
  gồm cả nhóm `Calc*Command` (10 phút/ngày/tháng/năm), `RankingCreationCommand`,
  `WatchNotificationCommand`, `ControlDrOperationCommand`,... (`BaseCommand.php:21-38`)
- Toàn bộ 2 nhánh daily + monthly chạy trong **1 transaction PostgreSQL duy nhất** — lỗi ở bất kỳ đâu
  (kể cả 1 khách hàng lỗi khi ghi `s_151`) rollback **toàn bộ**, bao gồm cả phần population đã ghi thành
  công ở `s_113`/`s_114` trong cùng lượt chạy. (`:101-143`)

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

> Không tìm thấy Lambda/cơ chế nào tương đương về bản chất. Bảng dưới đây là các khu vực/candidate đã
> tra trong `src/functions/`, `src/layers/`, `template.yaml`, `template-dynamodb.yaml` và lý do không
> khớp (thay cho B.1/B.2).

## Đã kiểm tra

| Khu vực / candidate | Vì sao không khớp |
|---|---|
| `src/layers/common/nodejs/interfaces/IAttributeCondition.ts`, `business-logic/check-user-matches-condition-attribute.ts`, field `household_num`/`building_type`/`app_household_num`/`app_total_floor_area` trong `Kaiin.ts`/`IF2024CustomerInfo.ts` | Có đúng các thuộc tính hộ gia đình tương tự (loại nhà, diện tích, số người...), nhưng dùng để **lọc/target khách hàng nhận push notification** (`batch-send-news`, `batch-send-tip`, `batch-send-survey`, `batch-send-dr`, `batch-send-contents-to-updated-user`) — không tính population/average theo nhóm, không lưu lịch sử nhóm, không có tính năng so sánh hiển thị cho user. Khác bản chất: targeting nội dung ≠ benchmarking/so sánh. |
| `create-data-segment-for-push-notice.ts`, `split-data-to-segments.ts`, `create-data-segment.ts` | Chữ "segment" ở đây nghĩa là chia file/list user thành các lô (chunk) để xử lý qua S3/SQS — thuần kỹ thuật xử lý hàng loạt, không liên quan phân khúc khách hàng theo thuộc tính. |
| `get-ranking-by-total-badge.ts`, `api-user/get-ranking-of-user.ts`, `api-point/get-point-badge-stats.ts`, `PointBadgeStatsTable`/`UserBadgeSummaryTable` | Ranking cá nhân theo tổng điểm/badge (gamification) — không liên quan phân nhóm theo thuộc tính hộ gia đình, không tính trung bình theo nhóm. |
| `get-monthly-report-of-user.ts` (`api-dashboard`) | Báo cáo tiền hóa đơn gas/điện lấy từ API TagTag (bill_amount, latest_payment_month) — không phải so sánh usage với nhóm. |
| Toàn bộ `template-dynamodb.yaml` (~46 bảng) | Không có bảng nào tên chứa "Group"/"Segment"/"Population"; các bảng usage (`DeviceDailyUsageHistoryTable`, `DeviceMonthlyUsageHistoryTable`) chỉ key theo `tagtag_kaiin_bango` (per-user) — không có cấu trúc lưu theo tổ hợp 5 thuộc tính hay `device_type` đặc biệt như `s_113`/`s_114`. |
| Grep `average`/`Average`/`compare`/`comparison`/`population`/`GroupSummary`/`GroupAve`/`UserGroupHistory`/`SensorDailyAveValue`/`SensorMonthlyAveValue`/`device_type.*16` trên toàn `src/` | 0 kết quả liên quan nghiệp vụ (chỉ có `localeCompare` — kỹ thuật, không phải nghiệp vụ). |
| `template.yaml` — toàn bộ `ScheduleExpression` (cron) | Chỉ có 3 lịch cron trong toàn hệ thống mới (`cron(5 0-7 * * ? *)`, 2× `cron(0 8 * * ?)`) — không có lịch nào tương ứng giờ chạy 02:10 của batch cũ. |

Không có dấu hiệu nào (bảng DB, Lambda, tên resource trong `template.yaml`) cho thấy chức năng "phân
khúc khách hàng theo thuộc tính hộ gia đình → tính population/average theo nhóm → so sánh cho user" đã
được port sang `syp-eminelstandard-backend`.

---

## Tổng kết

Không có — bản cũ chỉ có 1 pipeline (không phải 2 thuật toán song song khác bản chất; nhánh
daily/monthly là 2 bước ghi khác nhau của CÙNG 1 luồng tính population, không phải 2 cách tính khác
nhau cho cùng 1 việc), và hệ thống mới **không tìm thấy gì** để đối chiếu (không phải trường hợp "thay
bằng cơ chế khác") — bảng "Đã kiểm tra" ở Phần B đã nêu đủ lý do không khớp cho từng candidate.

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/conciergesv-develop/src/Command/CreateGroupSummaryCommand.php` |
| Hệ thống cũ | Cơ chế lock chống chạy trùng (dùng chung) | `sources/conciergesv-develop/src/Command/BaseCommand.php` |
| Hệ thống cũ | Ý nghĩa cột `t_101` (khách hàng) | `sources/eminel_sv_lib-develop/src/Model/Entity/ConCustomer.php:49-79` |
| Hệ thống cũ | Bảng `s_113` — PK, tên bảng | `sources/eminel_sv_lib-develop/src/Model/Table/ConSensorDailyAveValuesTable.php:37-44`, `Entity/ConSensorDailyAveValue.php` |
| Hệ thống cũ | Bảng `s_114` — PK, tên bảng | `sources/eminel_sv_lib-develop/src/Model/Table/ConSensorMonthlyAveValuesTable.php:41-43`, `Entity/ConSensorMonthlyAveValue.php` |
| Hệ thống cũ | Bảng `s_151` — PK, tên bảng, mục đích | `sources/eminel_sv_lib-develop/src/Model/Table/ConUserGroupHistoriesTable.php:12-46`, `Entity/ConUserGroupHistory.php` |
| Hệ thống cũ | Hằng số cờ tổng hợp | `sources/conciergesv-develop/config/const.php:607-611` |
| Hệ thống cũ | Mã `device_type=16` = "グループ母数" | `docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/補足資料/機器種別一覧.txt` (decode Shift-JIS) |
| Hệ thống cũ | Hằng số `DETECT_LIVING=0` | `sources/conciergesv-develop/config/const.php:228` |
| Hệ thống cũ | Nơi đọc lại `s_113`/`s_114`/`s_151` (consumer, xác nhận mục đích) | `sources/conciergesv-develop/src/Controller/GetUsageController.php:356-442,799-826` |
| Hệ thống cũ | Lịch chạy (cron) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:48-49` |
| Hệ thống cũ | Danh sách batch (mô tả tiếng Nhật, nhóm server) | `docs/03_API仕様/04_バッチ一覧.md:74` |
| Hệ thống cũ | Tài liệu liên quan, chưa đọc được nội dung (binary) | `docs/02_詳細設計/00_データベース設計/コンシェルジュ_バッチ機能CRUD図.xlsx`, `docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/16_コンシェルジェSV_詳細設計書別紙_グルーピング.docx` |
| Hệ thống mới | Cơ chế thuộc tính hộ gia đình (khác bản chất — dùng để targeting push, không phải benchmarking) | `src/layers/common/nodejs/interfaces/IAttributeCondition.ts`, `business-logic/check-user-matches-condition-attribute.ts`, `models/Kaiin.ts`, `models/IF2024CustomerInfo.ts` |
| Hệ thống mới | Ranking cá nhân theo badge (khác bản chất) | `src/layers/common/nodejs/business-logic/get-ranking-by-total-badge.ts`, `src/functions/api-user/get-ranking-of-user.ts`, `src/functions/api-point/get-point-badge-stats.ts` |
| Hệ thống mới | Toàn bộ danh sách bảng DynamoDB (không có bảng nào tương đương) | `template-dynamodb.yaml` |
| Hệ thống mới | Lịch cron (không có lịch tương ứng 02:10) | `template.yaml` (toàn bộ `ScheduleExpression`) |
