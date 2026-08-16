# Batch cũ — CalcDailyAccumulatedValueCommand（日毎積算値データ算出機能）

## Tóm tắt

`CalcDailyAccumulatedValueCommand` là batch chạy **1 lần/giờ** trong hệ thống cũ (EMINEL コンシェルジュサーバー). Batch tính **hiệu số tích lũy theo từng GIỜ** (endValue − startValue giữa 2 lần đọc biên giờ) cho 6 loại thiết bị: gas cogeneration (ガス発電電力量), pin mặt trời (太陽光発電電力量), mua/bán điện (買電量/売電量), xả/sạc pin lưu trữ (蓄電池放電量/充電量), và số lần phát hiện người (人感検知回数) tính lại ở granularity giờ. Tên class ghi "Daily/日毎" vì bảng đích lưu 1 dòng = 1 ngày × 24 cột giờ — đó là đơn vị lưu trữ, còn đơn vị tính là giờ.

Batch chỉ đọc/ghi DB — không gọi API ngoài, không đọc/xuất file CSV, không gửi mail. Kết quả ghi vào `s_102` để các batch tháng/năm tổng hợp tiếp. Chi tiết lịch chạy, công thức từng loại thiết bị và cơ chế bù dữ liệu thiếu trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Từ số đọc **tích lũy** ECHONET, tính **hiệu số theo từng GIỜ** cho 6 loại thiết bị (gas cogeneration, pin mặt trời, mua/bán điện, xả/sạc pin lưu trữ, và tính lại 人感 ở granularity giờ), ghi vào đúng 1 cột giờ trong dòng "ngày" tương ứng của mỗi hộ. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc CSV**: `t_101`（danh sách hộ, gồm cấu hình loại cogeneration/có-pin-mặt-trời/mã điểm điện）＋ `t_202`（bản ghi trạng thái thiết bị thô ECHONET, đã được ingest từ trước）. |
| **Output** | **Chỉ ghi DB** — 1 cột giờ/loại thiết bị mỗi lần chạy, upsert vào `s_102`（1 dòng/ngày × 24 cột giờ）. Có thể ghi thêm nhiều cột cùng lúc khi cơ chế tái tính (bù thiếu) kích hoạt. Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Đọc `--type`（bắt buộc）và `--datetime`（tùy chọn, mặc định = giờ liền trước hiện tại）, validate.<br>2. Với mỗi `type`: lấy danh sách hộ chưa xóa logic.<br>3. Với mỗi hộ: đọc 2 cửa sổ biên giờ `[T,T+1h)` và `[T+1h,T+2h)`, lấy bản ghi sớm nhất mỗi cửa sổ, áp dụng 1 trong 6 công thức chuẩn hóa hex tùy loại thiết bị.<br>4. Tính hiệu số cuối trừ đầu, làm tròn 4 chữ số thập phân.<br>5. Upsert 1 cột giờ vào dòng-ngày tương ứng trong `s_102`.<br>6. Kiểm tra cột giờ liền trước có NULL không; nếu có, dò ngược tìm mốc có dữ liệu gần nhất, rồi chia đều bù các giờ trống. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung |
|---|---|
| Lịch chạy (cron) | `17 * * * *` — 1 lần/giờ, phút 17 |
| Command thực thi | `php cake.php CalcDailyAccumulatedValue --type=<...> [--datetime=<...>]` |
| `--type` | Bắt buộc — nhiều giá trị phân tách bằng dấu phẩy, mỗi giá trị nằm trong nhóm loại thiết bị hợp lệ: `GAS_POWER`, `SOLAR_GENERATION`, `SALE_ELECTRIC`, `BATTERY_DISCHARGE`, `DETECT_CNT` |
| `--datetime` mặc định | `hiện tại − 1 giờ` |
| `--datetime` khi truyền tay | Format `yyyy-MM-ddTHH:00:00+09:00` |
| Cửa sổ tính | Bắt đầu = `datetime` · Kết thúc = `datetime + 1h` · ghi vào cột giờ tương ứng |

`BUY_ELECTRIC` và `BATTERY_CHARGE` không nằm trong nhóm loại thiết bị hợp lệ ở trên, nên không truyền trực tiếp qua `--type` — 2 loại này chỉ được xử lý gián tiếp như thành phần mở rộng của `SALE_ELECTRIC`/`BATTERY_DISCHARGE` (xem [2.9](#29-hằng-số-nghiệp-vụ-liên-quan)).

### 2.2 Chọn hộ xử lý

Danh sách hộ cần xử lý cho mỗi loại thiết bị được lấy bằng cách nối bảng danh sách hộ (`t_101`) với bảng giá trị theo giờ đã ghi trước đó (`s_102`).

Kết quả nối bảng với `s_102` không được dùng để lọc bớt hộ nào — danh sách trả về là **mọi hộ chưa xóa logic (còn hiệu lực)**, trừ khi loại thiết bị là `SALE_ELECTRIC` (bán điện) thì loại thêm các hộ đã tắt tính năng bán điện. Khi loại thiết bị là `DETECT_CNT` (人感), bước gộp nhóm ở cuối câu truy vấn loại bỏ các dòng trùng có thể sinh ra do không phân biệt theo phòng. Việc "hộ này giờ này đã có giá trị hay chưa" chỉ được kiểm tra ở bước sau (dựa vào dữ liệu đo có tồn tại hay không), không phải ở bước chọn hộ này.

### 2.3 Sáu loại thiết bị & công thức chuẩn hóa

Với mỗi loại thiết bị, batch chọn đúng mã lớp thiết bị (EOJ) và thuộc tính (EPC) cần đọc từ dữ liệu thô, rồi áp dụng công thức chuẩn hóa hex sang giá trị thực:

| `type` | Tên nghiệp vụ | EOJ (class) | EPC dùng | Công thức |
|---|---|---|---|---|
| `GAS_POWER` (8) | ガス発電電力量 | `027F%`（コレモ, khi `customer.c024=1`）hoặc `027C%`（エネファーム, khi `c024=2`） | `0xC5` | `hexdec(chuỗi) / 1000` → kWh |
| `SOLAR_GENERATION` (9) | 太陽光発電電力量 | `0279%` | `0xE1` | `hexdec(chuỗi) / 1000` → kWh |
| `SALE_ELECTRIC` (10) / `BUY_ELECTRIC` (11) | 売電量 / 買電量 | `0288%` | `0xD3,0xD7,0xE0,0xE1,0xE3` (4-5 trường cùng lúc) | Xem [2.3.1](#231-nhánh-rẽ-của-sale_electricbuy_electric) |
| `BATTERY_DISCHARGE` (12) | 蓄電池（放電量） | `027D%` | `0xA9` | `hexdec(chuỗi) / 1000` → kWh |
| `BATTERY_CHARGE` (13) | 蓄電池（充電量） | `027D%`（cùng EOJ với discharge） | `0xA8` | `hexdec(chuỗi) / 1000` → kWh |
| `DETECT_LIVING` (0) / `DETECT_OTHER` (1), dưới `DETECT_CNT` (14) | 人感検知回数 | `0F45%` | `0xEC` / `0xED` | `hexdec(8 ký tự đầu)` → số lần |

Ghi chú thêm về cách đọc:

- `BATTERY_DISCHARGE`/`BATTERY_CHARGE` dùng chung EOJ, đọc cùng lúc trong 1 câu truy vấn — hệ thống gọi công thức tính hiệu 2 lần trên cùng bộ dữ liệu thô (1 cho xả, 1 cho sạc).
- `DETECT_LIVING`/`DETECT_OTHER` đọc thẳng từ dữ liệu thô ở granularity GIỜ trong batch này (độc lập với batch 10-phút xử lý cùng chỉ số ở granularity nhỏ hơn).
- EOJ của `GAS_POWER` được chọn theo cấu hình loại cogeneration của hộ trong master data, không suy ra từ dữ liệu đo.

#### 2.3.1 Nhánh rẽ của `SALE_ELECTRIC`/`BUY_ELECTRIC`

Công thức dùng 5 thuộc tính (EPC) cùng lúc để quy đổi giá trị đọc thô sang kWh thực:

```text
coefficient    = hexdec(0xD3)                              # hệ số quy đổi, 6 chữ số
numberDigits   = hexdec(0xD7)                               # số chữ số hợp lệ (1~8)
forwardValue   = hexdec(0xE0)                               # giá trị đo chiều thuận (mua)
reverseValue   = hexdec(0xE3)                               # giá trị đo chiều nghịch (bán)
unit           = tra bảng theo giá trị hex của 0xE1          # ví dụ 0x03→0.001, 0x0A→10, ...

BUY_ELECTRIC  = forwardValue × coefficient × unit    (nếu numberDigits ≥ số chữ số của forwardValue)
```

Với `SALE_ELECTRIC`, có 3 nhánh dựa trên master data của hộ (có pin mặt trời hay không, loại cogeneration, mã tiếp nhận điểm cung cấp điện):

| Điều kiện | Kết quả |
|---|---|
| Không có pin mặt trời **VÀ** dùng cogeneration loại COREMO **VÀ** có mã tiếp nhận điểm cung cấp điện | Không tính, không ghi giá trị |
| Có pin mặt trời | `= reverseValue × coefficient × unit` (nếu đủ chữ số hợp lệ) |
| Còn lại | `= 0` |

Comment trong code mô tả điều kiện dòng đầu là "mã điểm tiếp nhận điện chưa có giá trị (NULL)", nhưng code thực tế kiểm tra ngược lại — chỉ áp dụng khi mã điểm tiếp nhận điện ĐÃ có giá trị.

Trong cấu hình loại thiết bị, `BUY_ELECTRIC` (mua điện) đã bị loại khỏi danh sách thiết bị chạy cùng `SALE_ELECTRIC` — dòng cấu hình cũ (chạy cả 2 cùng lúc) đã bị comment lại, chỉ còn dòng chạy riêng `SALE_ELECTRIC`. Với cấu hình này, batch chỉ tính `SALE_ELECTRIC`, không tính `BUY_ELECTRIC`, dù công thức tính vẫn còn đầy đủ trong code.

### 2.4 Cách đọc 2 cửa sổ biên giờ (start/end)

Với mỗi hộ và mỗi loại thiết bị, batch đọc dữ liệu thô hai lần:

```text
Đọc 1 (đầu giờ):  trong khoảng [T, T+1h)      lấy bản ghi sớm nhất
Đọc 2 (cuối giờ): trong khoảng [T+1h, T+2h)   lấy bản ghi sớm nhất
```

trong đó `T` là giờ đang tính (mặc định = giờ liền trước thời điểm chạy):

```text
giá trị "đầu giờ T"  = bản ghi sớm nhất trong khoảng [T, T+1h)
giá trị "cuối giờ T" = bản ghi sớm nhất trong khoảng [T+1h, T+2h)

hourValue(T) = floor((giá_trị_cuối − giá_trị_đầu) × 10000) / 10000
```

### 2.5 Công thức tính hiệu

```text
hourValue = floor((endValue − startValue) × 10000) / 10000
```

Không có bước chặn giá trị âm trong công thức này cho `GAS_POWER`/`SOLAR_GENERATION`/`BATTERY_DISCHARGE`/`BATTERY_CHARGE`/`SALE_ELECTRIC`/`BUY_ELECTRIC` — hiệu số âm được tính và ghi thẳng vào `s_102` như một giá trị bình thường. Với `DETECT_LIVING`/`DETECT_OTHER`, có bước kiểm tra riêng: loại 2 giá trị đặc biệt `FFFFFFFF`/`FFFFFFFE` (cảm biến chưa gắn/không phản hồi) thành `null`; comment trong code còn có ý định loại thêm giá trị ngoài dải hợp lệ (`0` ~ `999999999`), nhưng điều kiện thực tế dùng `&&` tự mâu thuẫn nên nhánh lọc dải không bao giờ kích hoạt — lọc dải không hoạt động. Bước này không kiểm tra dấu của hiệu số.

### 2.6 Ghi 1 cột giờ vào bảng "ngày" (`s_102`)

`s_102` có khóa chính ghép 4 cột: (mã hộ, loại thiết bị, vị trí, ngày). Mỗi lần chạy, batch chỉ set 1 cột giờ tương ứng rồi lưu — luôn tạo bản ghi mới rồi lưu theo khóa chính, không đọc dòng cũ lên để sửa. Vì khóa chính theo ngày (không theo giờ), 24 lần chạy trong một ngày đều nhắm vào cùng một dòng nhưng set cột khác nhau mỗi lần.

Các trường của `s_102`:

| Trường | Ý nghĩa | Khi nào được set |
|---|---|---|
| `c001`~`c004` | Khóa chính (mã hộ, loại thiết bị, vị trí, ngày) | Mỗi lần ghi |
| `c008` | Cờ cần tính lại tổng tiêu thụ điện (消費電力量) | `= 1` khi ghi giá trị mới; `= 2` khi ghi qua cơ chế bù thiếu cho 人感 |
| `c009` | Cờ cần tổng hợp lên tháng | `= 2` khi ghi giờ hiện tại; `= 1` khi bù dữ liệu cho ngày cũ |
| `c111`~`c115` | 5 thuộc tính nhóm: loại nhà, nguồn nhiệt sưởi (暖房熱源: 13A/LPG/điện/dầu hỏa/khác), diện tích sàn, số người, loại cogeneration | Copy từ danh sách hộ vào mỗi dòng |
| `c011`~`c034` | 24 cột giá trị theo giờ (00時台~23時台) | 1 cột/lần chạy |

### 2.7 Tái tính khi phát hiện giờ trước bị NULL (bù thiếu)

Sau khi ghi giờ hiện tại, batch luôn kiểm tra cột giờ liền trước của dòng-ngày hôm nay có bị bỏ trống (NULL) không. Nếu có, chạy các bước sau:

```text
1. Dò ngược từng giờ, từng ngày để tìm giờ gần nhất có giá trị khác NULL
   → dừng khi:
     (a) tìm thấy 1 giờ có giá trị, hoặc
     (b) gặp một ngày mà s_102 hoàn toàn chưa có dòng nào
2. Đọc lại toàn bộ chuỗi tích lũy thô từ dữ liệu gốc
   trong khoảng [mốc tìm được, giờ hiện tại − 1h]
3. Với mỗi khoảng trống liên tục, tính giá trị trung bình:
   giá trị mỗi giờ = floor((hiệu số của cả khoảng) / số giờ trống × 10000) / 10000
4. Ghi giá trị trung bình đó vào tất cả các giờ trống,
   mỗi bản ghi vẫn set đủ các cờ/thuộc tính nhóm như một dòng bình thường
```

Không có hằng số nào giới hạn số ngày dò ngược ở bước 1 cho batch này.

### 2.8 Chuỗi tổng hợp tiếp theo

Batch này là mắt xích đầu tiên trong một chuỗi các batch dùng chung cấu trúc "1 dòng, N cột theo đơn vị thời gian":

```
t_202 (raw ECHONET, tích lũy)
   │  CalcDailyAccumulatedValueCommand  (☚ batch đang phân tích — chạy 1 lần/giờ)
   ▼
s_102  "ConSensorHourlyValues"   1 dòng/ngày   × 24 cột giờ (c011~c034)
   │  batch tổng hợp tháng (chạy 1 lần/ngày)
   ▼
s_103  "ConSensorDailyValues"    1 dòng/tháng  × 31 cột ngày
   │  batch tổng hợp năm (chạy 1 lần/tháng)
   ▼
s_104  "ConSensorMonthlyValues"  1 dòng/năm    × 12 cột tháng
```

Danh sách loại thiết bị được tổng hợp lên tháng/năm không chứa `DETECT_CNT` (人感) — 人感 dừng lại ở mức ngày, không lên tháng/năm.

Một batch khác cùng họ — `CalcDailyEnergyConsumptionCommand` — đọc 5 cột giờ mà batch này ghi vào `s_102` (type 8, 9, 10, 12, 13: gas phát điện, mặt trời, xả pin, sạc pin, và một phần bán điện; cột 買電 type 11 do luồng khác cấp) làm input để ráp công thức tổng tiêu thụ điện (`消費電力量`). Chi tiết công thức và batch phụ thuộc thứ hai (`RcvHalfHourElectricPowerCommand`, nguồn của 買電/một phần 売電) nằm ở tài liệu `legacy-batch_CalcDailyEnergyConsumption.md` trong cùng bộ tài liệu này.

### 2.9 Hằng số nghiệp vụ liên quan

Mỗi loại thiết bị chính khi chạy sẽ mở rộng ra các loại thiết bị con cần tính: `GAS_POWER`/`SOLAR_GENERATION` chỉ tính chính nó; `BATTERY_DISCHARGE` tính luôn cả `BATTERY_CHARGE`; `DETECT_CNT` tính cả 2 phòng (`DETECT_LIVING`, `DETECT_OTHER`); riêng `SALE_ELECTRIC` **không** mở rộng ra `BUY_ELECTRIC` (xem [2.3.1](#231-nhánh-rẽ-của-sale_electricbuy_electric)).

| Hằng số | Giá trị |
|---|---|
| `GAS_POWER` / `SOLAR_GENERATION` / `SALE_ELECTRIC` / `BUY_ELECTRIC` / `BATTERY_DISCHARGE` / `BATTERY_CHARGE` / `DETECT_CNT` | `8 / 9 / 10 / 11 / 12 / 13 / 14` |
| `DETECT_LIVING` / `DETECT_OTHER` | `0 / 1` |
| Trần chữ số làm tròn | `floor(value × 10000) / 10000` — 4 chữ số thập phân |
| Ngưỡng số đọc 人感 tối đa | `999999999` |
| Đơn vị điện lượng | Tra theo giá trị hex của thuộc tính đơn vị (`0xE1`) |
| Giới hạn bù thiếu | Không định nghĩa cho batch này |

Danh sách loại thiết bị tổng hợp lên tháng/năm là tập lớn hơn, còn gồm cả gas tổng/nước nóng/sưởi và `POWER_CONSUMPTION` — nguồn từ các batch khác, ngoài phạm vi tài liệu này.

---

## Căn cứ của tài liệu

| Nội dung | Căn cứ |
|---|---|
| Toàn bộ logic (mục 2.1–2.9) | `sources/conciergesv-develop/src/Command/CalcDailyAccumulatedValueCommand.php` (đọc toàn văn) |
| Hằng số nghiệp vụ | `sources/conciergesv-develop/config/const.php` |
| Lịch chạy cron | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt` |
| Entity đích | `sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorHourlyValue.php` |
| Batch phụ thuộc phía sau (tháng/năm, ráp 消費電力量) | Xem tài liệu riêng `legacy-batch_CalcDailyEnergyConsumption.md` |
