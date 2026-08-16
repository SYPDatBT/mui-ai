# Batch cũ — PublishRegularEcoMissionsCommand（省エネアドバイス発行バッチ）

## Tóm tắt

`PublishRegularEcoMissionsCommand` không phải 1 batch làm 1 việc, mà là **bộ dispatcher chạy 1 trong 19 "kịch bản" khác nhau** tuỳ vào tham số `--eco-mission-id` (1-19) được truyền vào — mỗi kịch bản có **lịch cron riêng** (tổng 19 dòng cron gọi cùng 1 command với 19 giá trị id khác nhau) và được xử lý bởi 1 trong 10 class "Publisher" con. Mỗi lần chạy: xác định danh sách EMS-SP thoả điều kiện riêng của mission đó (ví dụ: nhiệt độ cài đặt cao, chưa bật ECO mode, vẫn để sưởi chạy, giá gas/điện cao hơn trung bình nhóm, v.v.), rồi ghi 1 bản ghi "nhiệm vụ" (`ConEcoMissions`) + đăng ký Push cho từng EMS-SP đó (ghi `PushMessages`/`PushMessageDestinations` hẹn +1 phút; `DispatchPushMessagesCommand` gửi thật). Đây chính là nghiệp vụ `[F-ES-03] 省エネアドバイス` (lời khuyên tiết kiệm năng lượng) trong yêu cầu E-GW. Chi tiết từng mission ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Dispatcher — theo `--eco-mission-id`, chạy 1 trong 10 loại logic xét điều kiện khách hàng, rồi phát hành "nhiệm vụ tiết kiệm năng lượng" (kèm điểm, link) và Push notification. |
| **Input** | Tuỳ mission: `ConCustomers` (`t_101`), `ConDeviceStatuses` (`t_202`), `ConSensorMonthlyValues`/`ConSensorHourlyValues`, `ConGroupHistories`/`ConSensorMonthlyAveValues` (giá trị trung bình nhóm), `EmsSpNos` (ngày đăng ký) ＋ master nội dung mission `ConRegularEcoMissions` (19 dòng, seed sẵn). |
| **Output** | Insert `ConEcoMissions` (1 bản ghi/lần phát, hoặc nhiều bản ghi nếu cùng lúc có nhiều "năm kỷ niệm" khác nhau) ＋ `ConEcoMissionDestinations` (1 dòng/EMS-SP) ＋ `PushMessages` + `PushMessageDestinations` (Push tới từng device token, hoặc 1 topic FCM chung cho mission id=1). |
| **Khái quát xử lý** | 1. Cron gọi command với `--eco-mission-id=N` theo lịch riêng của N.<br>2. Command switch theo N, gọi đúng Publisher.<br>3. Publisher chạy query riêng lấy danh sách EMS-SP thoả điều kiện (các Publisher ORM phân trang theo lô 100-500; riêng 2 Publisher `OverGas*` chạy 1 câu SQL lấy toàn bộ).<br>4. Ghi `ConEcoMissions` (dùng chung 1 bản ghi cho cả lô) + `ConEcoMissionDestinations` cho từng EMS-SP + `PushMessages`/`PushMessageDestinations`. |

## Phần 2 — Chi tiết

### Bản đồ dispatch — 19 mission ID, 10 Publisher, lịch cron riêng từng ID

```
COMMAND: PublishRegularEcoMissions --eco-mission-id=N --datetime=... [--dry-run]
  N=1        → EcoMissionPublisher::publishEcoMissionToAllEmsSps()      §2.2 · §2.3
  N=2,3      → Co2ReducedPublisher                                       §2.2 · §2.4
  N=4,5,6    → OverGasElectricUsageOverAvgPublisher (device_type=3)      §2.2 · §2.5
  N=7,8,9,10 → OverGasElectricUsageOverAvgWinterPublisher                §2.2 · §2.5
  N=11,12    → OverGasElectricUsageOverAvgPublisher (device_type=5)      §2.2 · §2.5
  N=13       → SetHighTempPublisher                                      §2.2 · §2.6
  N=14       → EcoModeNotSetPublisher                                    §2.2 · §2.6
  N=15       → SetHighTempInSleepPublisher                               §2.2 · §2.6
  N=16       → SetHighTempInAbsencePublisher                             §2.2 · §2.6
  N=17,18    → StillRunningHeaterMissionPublisher                        §2.2 · §2.7
  N=19       → StartContractAnniversaryPublisher                        §2.2 · §2.8
```

| Nhóm ID | Class xử lý | Chi tiết ở |
|---|---|---|
| 1 | `EcoMissionPublisher` (broadcast toàn bộ, không xét điều kiện) | §2.3 |
| 2, 3 | `Co2ReducedPublisher` | §2.4 |
| 4-6, 7-10, 11-12 | `OverGasElectricUsageOverAvgPublisher` / `...WinterPublisher` | §2.5 |
| 13-16 | `SetHighTempPublisher` / `EcoModeNotSetPublisher` / `SetHighTempInSleepPublisher` / `SetHighTempInAbsencePublisher` | §2.6 |
| 17, 18 | `StillRunningHeaterMissionPublisher` | §2.7 |
| 19 | `StartContractAnniversaryPublisher` | §2.8 |
| — | Cấu trúc bản ghi ghi ra DB | §2.9 |

---

### 2.1 Cơ chế dispatch & tham số chạy

| Tham số | Ý nghĩa |
|---|---|
| `--eco-mission-id` (bắt buộc) | Chọn 1 trong 19 kịch bản ([:60-135](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMissionsCommand.php#L60-L135)) |
| `--datetime` (mặc định `now`) | Mốc thời gian dùng để tính "tháng trước", "ngày hôm qua" v.v. tuỳ Publisher |
| `--dry-run` | Không ghi DB — chỉ ghi danh sách EMS-SP sẽ nhận vào file log (`LOGS/<timestamp>_eco_mission.log`) |
| `$allowDuplicateExec = true` | **Ghi đè** cơ chế lock-file chống chạy trùng của `BaseCommand` ([:37](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMissionsCommand.php#L37), [BaseCommand.php:15](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/BaseCommand.php#L15)) — cần thiết vì lock file đặt tên theo **tên class**, nếu không override thì cron gọi cùng command với 19 `--eco-mission-id` khác nhau gần nhau sẽ tự chặn nhau |

### 2.2 Lịch chạy cron đầy đủ 19 ID

Tổng hợp từ `mng-webap_cron設定_20241029.txt` (định dạng `phút giờ ngày tháng thứ`):

| ID | Lịch chạy (giờ Nhật) | Class xử lý | Nội dung (rút gọn từ `title`) | Điểm |
|---|---|---|---|---:|
| 1 | Ngày 15 hàng tháng, 20:00 | `EcoMissionPublisher` (broadcast) | "Đã xem giá tiền mới nhất chưa?" | 20 |
| 2 | Ngày 1 hàng tháng, 20:00 | `Co2ReducedPublisher::publishToReduced` | "Xem lượng giảm CO2 tháng trước" (đã giảm) | 40 |
| 3 | Ngày 1 hàng tháng, 20:00 | `Co2ReducedPublisher::publishToNotReduced` | "Xem lượng giảm CO2 tháng trước" (chưa giảm) | 20 |
| 4 | 5/7, 18:00 | `OverGasElectricUsageOverAvgPublisher` (gas nước nóng) | Mẹo tiết kiệm nước nóng #1 | 10 |
| 5 | 5/8, 18:00 | như trên | Mẹo tiết kiệm nước nóng #2 | 10 |
| 6 | 5/9, 18:00 | như trên | Mẹo tiết kiệm nước nóng #3 | 10 |
| 7 | 5/3, 5/11, 18:00 | `OverGasElectricUsageOverAvgWinterPublisher` | Mẹo tiết kiệm nước nóng (mùa đông) #1 | 10 |
| 8 | 5/4, 5/12, 18:00 | như trên | #2 | 10 |
| 9 | 5/1, 5/5, 18:00 | như trên | #3 | 10 |
| 10 | 5/2, 18:00 | như trên | #4 | 10 |
| 11 | 9/5, 18:00 | `OverGasElectricUsageOverAvgPublisher` (điện) | Mẹo tiết kiệm điện #1 | 10 |
| 12 | 9/10, 18:00 | như trên | #2 | 10 |
| 13 | Ngày 9, các tháng 1,2,3,4,11,12, 18:00 | `SetHighTempPublisher` | "Xem lại nhiệt độ cài đặt" | 20 |
| 14 | Ngày 20, các tháng 1,2,3,4,11,12, 18:00 | `EcoModeNotSetPublisher` | "Đặt ECO mode chưa?" | 20 |
| 15 | Ngày 11, các tháng 1,2,3,4,11,12, 18:00 | `SetHighTempInSleepPublisher` | "Xem lại nhiệt độ khi ngủ" | 20 |
| 16 | Ngày 18, các tháng 1,2,3,4,11,12, 18:00 | `SetHighTempInAbsencePublisher` | "Đã đặt mode ra ngoài chưa?" | 20 |
| 17 | 3/5, 18:00 | `StillRunningHeaterMissionPublisher` | "Sắp tắt sưởi chưa?" (lần 1) | 20 |
| 18 | 14/5, 18:00 | như trên | "Nửa số người dùng đã tắt sưởi" (lần 2, giọng thúc hơn) | 20 |
| 19 | Ngày 2 hàng tháng, 18:00 | `StartContractAnniversaryPublisher` | "Cảm ơn đã dùng EMINEL %%YEARS%% năm" | 100 |

> Nguồn: [mng-webap_cron設定_20241029.txt:84-102](e:/Projects/mui/legacy_eminel_docs-main/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt#L84-L102), nội dung/điểm từ [ConRegularEcoMissionsSeed.php:24-301](e:/Projects/mui/legacy_eminel_docs-main/sources/eminelsv-develop/config/Seeds/ConRegularEcoMissionsSeed.php#L24-L301).

### 2.3 ID 1 — Broadcast toàn bộ (không xét điều kiện)

Khác hẳn 18 ID còn lại: `EcoMissionPublisher::publishEcoMissionToAllEmsSps()` không lọc khách hàng, chỉ tạo **1 bản ghi `ConEcoMissions`** (`distribute_scope=ALL`) rồi gửi Push qua **1 FCM topic chung `all_ems_sp`** ([:60-82](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php#L60-L82)) — **không** tạo bản ghi `ConEcoMissionDestinations` cho từng EMS-SP (xem ⚠️①).

### 2.4 ID 2, 3 — Nhắc lượng giảm CO2 (`Co2ReducedPublisher`)

| Mục | Nội dung |
|---|---|
| Dữ liệu xét | `ConSensorMonthlyValues` loại `device_type=18` (`TOTAL_CO2_EMISSIONS`), `room_id=0`, 2 năm liên tiếp (QUAN SÁT: nhánh tính năm tài chính là nhánh chết — `$lastMonth->year >= 4` luôn true ([:73](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/Co2ReducedPublisher.php#L73)) nên thực tế luôn so theo năm dương lịch của tháng trước và năm liền trước; nếu ý đồ là 年度 mốc tháng 4 thì đây là bug hệ cũ, cần lưu ý khi port sang E-GW) ([:83-91](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/Co2ReducedPublisher.php#L83-L91)) |
| Điều kiện "đã giảm" | Giá trị CO2 tháng trước (năm nay) `<` giá trị cùng tháng năm ngoái ([:104-115](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/Co2ReducedPublisher.php#L104-L115)) |
| Trường hợp thiếu dữ liệu | ID 2 ("đã giảm"): thiếu dữ liệu → không tính vào "đã giảm" → bị loại. ID 3 ("chưa giảm"): thiếu dữ liệu vẫn được coi là "chưa giảm" và **vẫn phát mission** (comment `#308` trong code xác nhận đây là chủ ý) ([:122-127](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/Co2ReducedPublisher.php#L122-L127)) |
| Đối tượng | Chỉ khách hàng đăng ký (`EmsSpNos.create_datetime`) trước mốc "1 năm trước, đầu tháng sau" — đảm bảo đã có đủ dữ liệu 1 năm để so sánh ([:78-82](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/Co2ReducedPublisher.php#L78-L82)) |

### 2.5 ID 4-12 — Nước nóng/điện dùng nhiều hơn trung bình nhóm

3 Publisher dùng chung 1 kiểu SQL (join `ConGroupHistories` + `ConSensorMonthlyAveValues` để lấy giá trị trung bình nhóm), khác nhau ở device_type và điều kiện lọc thêm:

| Publisher | Device type | Điều kiện thêm | Mùa áp dụng |
|---|---|---|---|
| `OverGasElectricUsageOverAvgPublisher(deviceType=3)` — ID 4-6 | `3` (nước nóng) | Không có điều kiện tách sưởi/nước nóng | Mùa hè (7-9) |
| `OverGasElectricUsageOverAvgWinterPublisher` — ID 7-10 | `3` (nước nóng) | **Chỉ áp dụng hộ đã tách sưởi/nước nóng**: `heater_ctrl_mode=AT` (tự động), nguồn nhiệt nước nóng ∈{13A,LPG,dầu}, nguồn nhiệt nước nóng = nguồn nhiệt sưởi, ≠ nguồn nhiệt tan tuyết (`c044` 融雪熱源) ([:89-97](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/OverGasElectricUsageOverAvgWinterPublisher.php#L89-L97) — 4 trong 6 điều kiện `separate_calc_target` của `CalcTenMinutesEnergyCommand`; không có 2 điều kiện `c023` loại hợp đồng gas và `c052 IS NULL`) | Mùa đông (1,2,3,4,5,11,12) |
| `OverGasElectricUsageOverAvgPublisher(deviceType=5)` — ID 11-12 | `5` (tiêu thụ điện) | Không có điều kiện thêm | Tháng 5, 10 |

Điều kiện chung cho cả 3: giá trị tháng trước của khách hàng **≥** giá trị trung bình nhóm cùng tháng ([:86-91](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/OverGasElectricUsageOverAvgPublisher.php#L86-L91)), nhóm phải có **≥ 10 hộ** mới tính trung bình (`ConSensorMonthlyAveParams.$col > 9`, [:83](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/OverGasElectricUsageOverAvgPublisher.php#L83)), và nhóm phải nằm trong các mã thuộc tính hợp lệ (`ConGroupHistories.c111-c115`, [:92-96](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/OverGasElectricUsageOverAvgPublisher.php#L92-L96)) — đúng cơ chế nhóm hóa `[F-ES-12] グルーピング` trong yêu cầu E-GW.

### 2.6 ID 13-16 — Xem lại cài đặt nhiệt độ/sưởi

| ID | Publisher | Điều kiện | Nguồn dữ liệu |
|---|---|---|---|
| 13 | `SetHighTempPublisher` | Nhiệt độ cài đặt **mode ở nhà** (HS 開始種別=`33`) trong ngày mùng 9 của tháng (00:00 ngày 9 → 00:00 ngày 10; batch chạy 18:00 ngày 9 nên thực tế là dữ liệu 00:00-18:00 ngày 9), trung bình **≥ 23°C** ([:37, :85](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/SetHighTempPublisher.php#L37-L85)) | `ConDeviceStatuses` EPC `A1`, chỉ hộ `heater_ctrl_mode=AT` |
| 14 | `EcoModeNotSetPublisher` | Nhiệt độ cài đặt **ECO mode**: có bản ghi trong khung 12:00-12:10 ngày 20 với giá trị = `0` (chưa cài) ([:36-57](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/EcoModeNotSetPublisher.php#L36-L57)) | `ConDeviceStatuses` EPC `A7` |
| 15 | `SetHighTempInSleepPublisher` | Nhiệt độ cài đặt **mode ngủ** (HS開始種別=`31`) hôm trước **≥ 20°C** ([:36-81](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/SetHighTempInSleepPublisher.php#L36-L81)) | `ConDeviceStatuses` EPC `A1` |
| 16 | `SetHighTempInAbsencePublisher` | Nhiệt độ phòng khách (12h-14h) trung bình **≥ 20°C** trong 2 tuần liên tiếp **và** phát hiện chuyển động (人感) trong cùng khung 12h-14h của cả 14 ngày đều = `0` ([:35-98](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/SetHighTempInAbsencePublisher.php#L35-L98)) | `ConSensorHourlyValues` (device_type `6`=nhiệt độ phòng, `14`=phát hiện chuyển động) |

3/4 (ID 13, 14, 15) yêu cầu `heater_ctrl_mode=AT` và dùng field EPC thô từ `ConDeviceStatuses` (`t_202`, bảng ECHONET raw, cùng bảng dùng ở `CalcTenMinutesEnergyCommand`); riêng ID 16 không lọc AT và dùng bảng tổng hợp giờ `ConSensorHourlyValues` (`s_102`).

### 2.7 ID 17, 18 — Vẫn còn để sưởi chạy (`StillRunningHeaterMissionPublisher`)

Điều kiện: thiết bị `device_id=1001` có bản ghi EPC `80` (trạng thái ON/OFF) = `30` (ON) trong khung **12:00-14:10 hôm trước** ([:34-53](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/StillRunningHeaterMissionPublisher.php#L34-L53)). **ID 17 và ID 18 dùng chung y nguyên điều kiện này**, chỉ khác ngày chạy (3/5 và 14/5) và nội dung thông báo — khách hàng còn để sưởi ON tới giữa tháng 5 sẽ nhận **cả 2** mission riêng biệt, không có cơ chế loại trừ đã nhận ID 17 rồi thì bỏ qua ID 18.

### 2.8 ID 19 — Kỷ niệm ngày dùng EMINEL (`StartContractAnniversaryPublisher`)

- Lấy `EmsSpNos.create_datetime` có **tháng** khớp tháng chạy hiện tại (không so ngày, chỉ so tháng) ([:39-41](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/StartContractAnniversaryPublisher.php#L39-L41)).
- Số năm = năm hiện tại − năm đăng ký. **Bỏ qua khách hàng năm đầu** (`years === 0`) ([:54-57](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/StartContractAnniversaryPublisher.php#L54-L57)).
- Khác mọi ID khác: vì số năm dùng khác nhau giữa các khách hàng, code tạo **nhiều bản ghi `ConEcoMissions` riêng trong cùng 1 lần chạy** — mỗi giá trị `years` khác nhau có 1 bản ghi riêng (title/message thay `%%YEARS%%` bằng số năm cụ thể; map này khởi tạo lại theo từng trang phân trang 100 bản ghi nên cùng `years` có thể có nhiều bản ghi khi >100 khách/tháng), rồi mới gọi `saveToEmsSps` riêng cho từng nhóm năm ([:59-83](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/StartContractAnniversaryPublisher.php#L59-L83)).

### 2.9 Cấu trúc dữ liệu ghi ra

| Bảng | Vai trò |
|---|---|
| `ConEcoMissions` | 1 bản ghi/lần phát (hoặc /nhóm năm ở ID 19) — copy `title`/`message`/`page_id`/`link_url`/`image_url`/`points` từ `ConRegularEcoMissions`, `start_at = now`, `end_at = now + 30 ngày` ([ConEcoMissionsTable.php:156-173](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Table/ConEcoMissionsTable.php#L156-L173)) |
| `ConEcoMissionDestinations` | 1 dòng/EMS-SP thoả điều kiện — app đọc bảng này để hiển thị "nhiệm vụ của tôi" cho mission `EMS_SP` (mission `ALL` được query riêng, không cần destination). **ID 1 không tạo dòng nào ở bảng này lúc phát** (xem §2.3, ⚠️①) |
| `PushMessages` | 1 bản ghi/lần phát, `data.kind=ECO_MISSION` |
| `PushMessageDestinations` | 1 dòng/device token đã đăng ký của EMS-SP đó (nếu EMS-SP không có token nào — chưa cài app/chưa đăng nhập — thì **không** có dòng Push, nhưng `ConEcoMissionDestinations` vẫn được tạo, nên "nhiệm vụ" vẫn hiển thị khi khách hàng mở app sau, chỉ là không có Push lúc phát) |
| `page_id` (trong `ConRegularEcoMissions`) | Deep-link khi tap mission: `ReportRankingPageId`, `ChartsGasUsagePageId`, `ChartsElectricityUsagePageId`, `HeaterTemperaturePageId`, `HeaterSchedulePageId`, `HeaterPowerPageId`, `PointsPageId` |

---

### ⚠️ Điểm cần chú ý

**① ID 1 không tạo `ConEcoMissionDestinations` lúc phát — nhưng vẫn hiển thị trong danh sách nhiệm vụ.** Toàn bộ 18 ID khác đều tạo `ConEcoMissionDestinations` cho từng EMS-SP thoả điều kiện. Riêng ID 1 chỉ gửi Push qua topic chung, **không** ghi bảng này lúc phát — tuy vậy ID 1 **vẫn** xuất hiện trong danh sách nhiệm vụ: API `GetEcoMissions` query riêng nhóm `distribute_scope=ALL` (không cần destination) rồi merge với nhóm `EMS_SP` ([GetEcoMissionsController.php:66-111](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/GetEcoMissionsController.php#L66-L111)); dòng `ConEcoMissionDestinations` của ID 1 chỉ được tạo khi user đọc/hoàn thành mission ([SetEcoMissionController.php:115-125](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/SetEcoMissionController.php#L115-L125)). Điểm cần chú ý thật sự: số liệu "đã phát cho bao nhiêu người" của ID 1 không đếm được từ `ConEcoMissionDestinations`.

**② Không có cơ chế chống trùng giữa các mission khác nhau cho cùng 1 tình huống.** ID 17 và 18 kiểm tra đúng 1 điều kiện giống nhau (sưởi ON buổi 12-14h hôm trước) nhưng chạy 2 lần cách nhau 11 ngày trong tháng 5 — khách hàng chưa tắt sưởi vào cả 2 thời điểm đó nhận 2 nhiệm vụ riêng (khác nội dung nhắc nhở, có vẻ là chủ ý tăng dần mức độ thúc đẩy, không phải lỗi — nhưng cần biết khi đối chiếu số liệu "đã gửi bao nhiêu mission" theo khách hàng).

**③ `allowDuplicateExec = true` là bắt buộc, không phải tuỳ chọn.** Vì lock file của `BaseCommand` đặt tên theo **tên class**, mà 19 lịch cron đều gọi cùng 1 class `PublishRegularEcoMissionsCommand` (chỉ khác `--eco-mission-id`) — nếu không override, 2 mission chạy trùng giờ (ví dụ nhiều ID cùng chạy 18:00 các ngày khác nhau nhưng có thể chồng thời gian thực thi) sẽ tự chặn nhau dù đang xử lý 2 mission hoàn toàn độc lập.

---

## Nguồn

| Nội dung | Căn cứ |
|---|---|
| Dispatcher chính | `sources/conciergesv-develop/src/Command/PublishRegularEcoMissionsCommand.php` |
| Base class publisher + lock file | `sources/conciergesv-develop/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php`, `sources/conciergesv-develop/src/Command/BaseCommand.php` |
| 9 Publisher cụ thể | `sources/conciergesv-develop/src/Command/PublishRegularEcoMission/*.php` |
| Lịch cron 19 ID | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:84-102` |
| Nội dung/điểm 19 mission (master data) | `sources/eminelsv-develop/config/Seeds/ConRegularEcoMissionsSeed.php` |
| Cấu trúc bảng `ConEcoMissions` | `sources/eminel_sv_lib-develop/src/Model/Table/ConEcoMissionsTable.php`, `src/Model/Entity/ConEcoMission.php` |
| Cấu trúc `PushMessageDestinations` | `sources/eminel_sv_lib-develop/src/Model/Table/PushMessageDestinationsTable.php` |
