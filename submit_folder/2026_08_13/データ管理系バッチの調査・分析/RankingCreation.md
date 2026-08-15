# RankingCreationCommand（ランキング作成）

## Tóm tắt

`RankingCreationCommand` là batch chạy **1 lần/tháng** (ngày 1, ngay sau `CalcCarbonDioxideEmissionsCommand`)
trên `conciergesv`: tính **percentile phát thải CO2** (3 loại — tổng hợp/gas/điện) cho từng khách hàng,
so với các khách hàng khác **CÙNG NHÓM 5 thuộc tính hộ gia đình** (đúng nhóm đã audit ở
`CreateGroupSummaryCommand`, xem `CreateGroupSummary.md`) — nhóm quá nhỏ (≤9 người) thì fallback dùng
nhóm rộng hơn (2 thuộc tính) để percentile có ý nghĩa thống kê. Kết quả lưu vào `ConRankings` (percentile
theo từng tháng + cờ xu hướng tốt lên/xấu đi/không đổi so với tháng trước), app đọc lại qua
`GetRankingInfoController` để hiển thị "bạn thuộc top X% ít phát thải nhất trong nhóm nhà giống bạn". Ở
repo mới `syp-eminelstandard-backend`, **không có cơ chế tương đương, khác bản chất hoàn toàn**: hệ mới
CÓ 1 tính năng cũng tên "ranking" (`get-ranking-by-total-badge.ts`) nhưng thực chất là hệ **tier/level
theo ngưỡng điểm tuyệt đối** (gamification, giống XP level trong game) — chỉ đọc điểm CỦA CHÍNH user đó
rồi so với 1 bảng ngưỡng cố định (regular/bronze/silver/gold/platinum/diamond), **không hề so sánh với
bất kỳ user nào khác**, không nhóm, không percentile, không liên quan CO2/năng lượng. Cơ chế nhóm 5
thuộc tính hộ gia đình (nền tảng của batch cũ) cũng không tồn tại — đã xác nhận ở `CreateGroupSummary.md`.
Tính năng "so sánh phát thải CO2 với nhóm nhà tương tự" dường như chưa được port.

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `RankingCreationCommand` (extends `BaseCommand`) · Tên lệnh gọi thật: `rankingCreation` (ghi rõ trong docblock, không theo quy ước snake_case như các Command khác) · Script cron: `20_RankingCreation.sh` · Tên tiếng Nhật trong cron: "20.ランキング作成". |
| **Vai trò** | Tính percentile phát thải CO2 của từng khách hàng trong nhóm hộ gia đình tương tự + theo dõi xu hướng tháng-qua-tháng, phục vụ tính năng ranking hiển thị trong app. |
| **Input** | Đọc `t_101` (khách hàng), `s_104` (giá trị CO2 theo tháng, `device_type=18/19/20`), `s_151` (nhóm khách hàng theo tháng), `s_114` (population nhóm theo tháng), `s_121` chính nó (đọc lại ranking tháng trước để tính xu hướng). Tham số `--rankingtype` (**bắt buộc**, không có default — xem A.2.4), `--yearmonth` (tùy chọn, mặc định tháng trước). |
| **Output** | `INSERT`/`UPDATE` bảng `ConRankings` (`s_121`) — 1 dòng/khách hàng/năm/loại ranking, cột theo THÁNG (percentile) + cột theo THÁNG (trạng thái xu hướng). |
| **Khái quát xử lý** | 1. Validate + parse tham số (loại ranking, năm-tháng tính).<br>2. Với mỗi loại ranking (1-3 loại theo tham số): tính percentile CO2 của mọi khách hàng hợp lệ trong tháng đó (theo nhóm, có fallback nhóm rộng khi nhóm nhỏ) + so sánh với tháng trước để tính xu hướng.<br>3. Ghi kết quả: khách hàng đã có dòng `ConRankings` năm đó/loại đó → UPDATE cột tháng; chưa có → gom lại INSERT hàng loạt.<br>4. Toàn bộ trong 1 transaction (có ngoại lệ khi lỗi giữa chừng, xem A.2.4). |

## A.2 Chi tiết

**Bản đồ cách tính — phân nhóm 2 tầng + công thức percentile:**

```
Với mỗi khách hàng, mỗi loại ranking (1 CO2 tổng / 2 CO2 gas / 3 CO2 điện):

  Nhóm 5-thuộc-tính của khách hàng (từ s_151, snapshot ĐÚNG tháng đang xếp hạng)
                    │
                    ▼
       Population nhóm 5-thuộc-tính (s_114, cột tháng đang xét) > 9 người?
                    │
        ┌───────────┴────────────┐
       CÓ                      KHÔNG (≤9 người, nhóm quá nhỏ)
        │                         │
        ▼                         ▼
  RANK() ASC theo CO2       RANK() ASC theo CO2
  TRONG nhóm 5-thuộc-tính   TRONG nhóm rộng hơn (chỉ loại nhà + công suất sưởi, bỏ 3 thuộc tính còn lại)
  mẫu số = population       mẫu số = SUM population các nhóm 5-thuộc-tính có cùng 2-thuộc-tính này
  nhóm 5-thuộc-tính đó            │
        └───────────┬────────────┘
                     ▼
    percentile = GREATEST(trunc((rank − 1) / mẫu_số × 100), 1)   ← số nguyên 1-100, KHÔNG bao giờ = 0
                     │
                     ▼
    So sánh percentile tháng này với percentile CÙNG loại ranking, LƯU Ở s_121 của tháng trước
                     │
      ┌──────────────┼──────────────────┬───────────────────────┐
      ▼              ▼                  ▼                       ▼
  không có dữ    percentile trước   percentile trước >      percentile trước <
  liệu trước     == percentile nay  percentile nay (giảm)   percentile nay (tăng)
  rank_status=2  rank_status=2      rank_status=0 (tốt lên) rank_status=1 (xấu đi)
```

| Bước | Mục chi tiết |
|---|---|
| Validate tham số + xác định tháng tính | §A.2.1 |
| Câu SQL tính rank + percentile (2 tầng nhóm) | §A.2.2 |
| Cột tháng & lỗi lệch cột đã biết (`c022`↔`c023`) | §A.2.3 |
| Ghi kết quả — UPSERT `ConRankings` | §A.2.4 (phần ghi) |

### A.2.1 Tham số & xác định tháng tính

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `10 7 1 * *` — 1 lần/tháng, ngày 1 lúc 07:10 (ngay sau `19_CalcCarbonDioxideEmissions.sh` chạy 06:10 cùng ngày — dữ liệu CO2 tháng vừa xong được tính trước 1 giờ) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:65,68` |
| `--rankingtype` | **Không có default** — bắt buộc phải truyền, comma-separated, mỗi giá trị phải là `1`(tổng)/`2`(gas)/`3`(điện), sai → abort ngay. Không xác nhận được tham số cron thật gọi gì (không đọc được `.sh`), nhưng vì chỉ có 1 dòng cron (không tách theo loại như 1 số batch khác) → *(suy đoán hợp lý)* cron gọi 1 lần với cả 3 loại, ví dụ `--rankingtype=1,2,3`. | `RankingCreationCommand.php:69-82` |
| `--yearmonth` | Không truyền → tháng trước (hợp lý vì cron chạy ngày 1, "tháng trước" = tháng vừa kết thúc). Truyền → phải đúng format `yyyy-MM`, năm trong khoảng [1900,9000], tháng [1,12]. | `:85-113` |
| Tính `lastYearMonth` | Tháng NGAY TRƯỚC tháng đang xếp hạng (không phải cùng tháng năm trước) — dùng để tra `ConRankings` tháng trước nhằm tính xu hướng. | `:122-128` |

### A.2.2 Câu SQL tính rank + percentile

```sql
WITH current_rank AS (
  SELECT cus.c001 AS ems_sp,
    GREATEST(trunc((
      ( CASE WHEN all_attr.{col} > 9   -- MEMBERS_NUM_OF_SUMMARY_GROUP
             THEN RANK() OVER (PARTITION BY hist.group1..group5 ORDER BY nen.{col} ASC)
             ELSE RANK() OVER (PARTITION BY hist.group1, hist.group2 ORDER BY nen.{col} ASC)
        END - 1
      ) / CASE WHEN all_attr.{col} > 9 THEN all_attr.{col} ELSE parts_attr.{col} END
    ) * 100), 1) AS rank
  FROM t_101 cus
  LEFT JOIN s_104 nen ON cus.c001 = nen.c001                    -- giá trị CO2 theo tháng
  LEFT JOIN (SELECT ... bucket hóa 5 thuộc tính từ s_151 ...) hist ON nen.c001 = hist.c001
  LEFT JOIN s_114 all_attr ON hist.group1..5 = all_attr.c111..115   -- population nhóm 5-thuộc-tính
  LEFT JOIN (SELECT SUM(...) FROM s_114 GROUP BY c111,c112) parts_attr ON hist.group1,2 = parts_attr.c111,c112  -- fallback
  WHERE cus.c001=nen.c001 AND nen.c002=:deviceType AND nen.c003=0 AND nen.c004=:year
    AND nen.{col} IS NOT NULL AND all_attr.c001=16 AND all_attr.c002=0 AND all_attr.c003=:year
    AND cus.c052 IS NULL
)
SELECT ranking.ems_sp, ranking.rank, cur_ranking.*,
  CASE WHEN prv_ranking.{lastCol} IS NULL THEN 2
       WHEN prv_ranking.{lastCol} = ranking.rank THEN 2
       WHEN prv_ranking.{lastCol} > ranking.rank THEN 0
       ELSE 1 END rank_status
FROM current_rank ranking
LEFT JOIN s_121 prv_ranking ON ...ems_sp AND c002=:lastYear AND c003=:rankingType
LEFT JOIN s_121 cur_ranking ON ...ems_sp AND c002=:year AND c003=:rankingType
```
Nguồn: `RankingCreationCommand.php:182-265` (rút gọn, giữ nguyên logic).

| Bảng | Vai trò trong câu SQL | Đối chiếu |
|---|---|---|
| `t_101` (khách hàng) | Danh sách khách hàng chưa xóa (`c052 IS NULL`) | `ConCustomer.php` |
| `s_104` (`nen`) | Giá trị CO2 tháng đang xét, `device_type=18/19/20` = tổng/gas/điện — **không nằm trong `機器種別一覧.txt`** (tài liệu chỉ liệt kê tới mã 17; mã 18-20 chỉ xác nhận được qua code `CalcCarbonDioxideEmissionsCommand.php:185-220`, comment "機器種別18～20のCO2排出量" — tài liệu doc có thể đã lỗi thời, không cập nhật theo code) | `CalcCarbonDioxideEmissionsCommand.php:185-220`; `getDeviceTypeFromRankingType()` (`:295-308`) |
| `s_151` (`hist`, qua subquery) | Nhóm 5-thuộc-tính của khách hàng tại ĐÚNG tháng đang xếp hạng (snapshot lịch sử, không phải nhóm hiện tại) — bucket hóa **giống hệt công thức** ở `CreateGroupSummaryCommand::populationAggregation()` | `CreateGroupSummary.md` §A.2.2 |
| `s_114` (`all_attr`) | Population nhóm 5-thuộc-tính, cột tháng đang xét, `device_type=16` (population — đúng bảng/đúng cột mà nhánh monthly của `CreateGroupSummaryCommand` ghi ra) | `CreateGroupSummary.md` §A.2.4 |
| `s_114` (`parts_attr`, fallback) | Tổng population các nhóm 5-thuộc-tính có CÙNG 2 thuộc tính đầu (loại nhà + công suất sưởi), dùng khi nhóm 5-thuộc-tính ≤9 người | `RankingCreationCommand.php:220-233` |
| `s_121` (`prv_ranking`/`cur_ranking`) | Tra lại percentile tháng trước (tính xu hướng) và dòng `ConRankings` hiện có (quyết định INSERT hay UPDATE) | `ConRanking.php` |

**Ví dụ chạy tay** *(số liệu minh họa giả định)* — nhóm 5-thuộc-tính có 15 khách hàng (population=15,
>9 nên KHÔNG fallback), khách hàng X đứng thứ 3 (rank=3) khi sắp CO2 tăng dần (phát thải thấp thứ 3 —
tốt):
- `percentile = GREATEST(trunc(((3−1)/15)×100), 1) = GREATEST(trunc(13.33), 1) = GREATEST(13,1) = 13`
- Khách hàng phát thải THẤP NHẤT nhóm (rank=1): `GREATEST(trunc((0/15)×100),1) = GREATEST(0,1) = 1` —
  không bao giờ hiển thị 0%, luôn tối thiểu 1%.
- Khách hàng phát thải CAO NHẤT nhóm (rank=15): `GREATEST(trunc((14/15)×100),1) = 93` — cũng không bao
  giờ chạm đúng 100% (giới hạn toán học của công thức `(N-1)/N`, N càng lớn thì càng gần 100 nhưng không
  bao giờ bằng).

### A.2.3 ⚠️ Điểm bất thường của hệ cũ — lệch cột `c022`↔`c023` trong bảng `ConRankings`

- Quy ước cột tháng chuẩn trên các bảng sensor-value khác (`s_104`,`s_113`,`s_114`,...) là `c0(tháng+10)`
  — tháng 12 → `c022`. Nhưng bảng `ConRankings` (`s_121`) lại **BỎ TRỐNG `c022` và dùng `c023` cho tháng
  12** — xác nhận trực tiếp qua khai báo hằng số entity: `C_RANK_11='c021'` rồi NHẢY THẲNG sang
  `C_RANK_12='c023'` (`ConRanking.php:57-58`), không có `C_RANK` nào ánh xạ tới `c022` trong toàn bộ
  entity.
- Code TỰ NHẬN BIẾT lỗi này bằng 1 comment thẳng thắn trong `getRankingData()`: *"ランキング情報テーブル
  のランキング12月順位カラムがなぜかc023のため（本来、c022であるべき）、以降のカラム物理名の取得におい
  て、便宜的に13とする"* (dịch: "vì lý do nào đó cột thứ hạng tháng 12 của bảng ranking lại là c023 —
  đáng lẽ phải là c022 — nên tạm quy ước dùng số 13 khi tính tên cột vật lý về sau"). (`:174-178`)
- Workaround CHỈ áp dụng cho việc tính `$lastMonthColumn` (tra percentile THÁNG TRƯỚC từ `s_121` để so
  sánh xu hướng) — **không cần** áp dụng cho `$currentMonthColumn` (dùng để đọc `s_104`/`s_114`, các
  bảng sensor-value KHÔNG có lỗi lệch cột này, tháng 12 vẫn là `c022` bình thường ở các bảng đó). Việc
  GHI kết quả (`insertRanking()`) cũng không bị ảnh hưởng vì dùng mảng ánh xạ tường minh
  `$rankColumnName[12] = ConRanking::C_RANK_12 = 'c023'` (đã đúng sẵn), không tính theo công thức `+10`.
  (`:322-336`)
- Kết luận: đây là 1 lỗi THIẾT KẾ SCHEMA đã có từ trước (ai đó tạo bảng `ConRankings` bỏ sót/nhảy cột
  `c022`), không phải bug đang hoạt động sai — code đã vá đúng chỗ cần vá. Quan trọng khi port: **không
  nên sao chép nguyên lỗi lệch cột này** sang schema mới (không có lý do gì để giữ lại sự bất thường của
  1 lỗi migration/thiết kế cũ), chỉ cần đảm bảo layout mới nhất quán 1-12 tháng liên tục.

### A.2.4 Ghi kết quả & bất đối xứng xử lý lỗi giữa 2 bước

- **UPSERT theo `ems_sp`+`year`+`ranking_category`**: khách hàng CHƯA có dòng `ConRankings` năm đó/loại
  đó (`cur_rank_ems_sp` rỗng, xác định qua LEFT JOIN `cur_ranking` ở câu SQL) → gom vào mảng, `INSERT`
  hàng loạt 1 lần cuối; đã có dòng → `UPDATE` ngay từng dòng (không gom). (`:342-393`)
- Mỗi lần ghi chỉ set ĐÚNG 2 cột của tháng đang xử lý (rank + status) — các tháng khác trong cùng dòng
  (nếu dòng đã tồn tại từ tháng trước) giữ nguyên, không bị ghi đè.
- **⚠️ Bất đối xứng xử lý lỗi giữa 2 bước, khi chạy nhiều `--rankingtype` cùng lúc** (ví dụ `1,2,3`):
  - Nếu bước LẤY dữ liệu (`getRankingData`) lỗi ở loại ranking thứ N → `$connection->commit()` (GIỮ LẠI
    toàn bộ thay đổi của các loại ranking 1..N-1 đã xử lý xong trước đó trong CÙNG lượt chạy) rồi mới
    `abort()`. (`:135-140`)
  - Nếu bước GHI dữ liệu (`insertRanking`) lỗi ở loại ranking thứ N → `$connection->rollback()` (HỦY
    TOÀN BỘ, kể cả các loại ranking 1..N-1 đã ghi thành công trước đó trong CÙNG lượt) rồi mới `abort()`.
    (`:144-149`)
  - Hệ quả: cùng là "lỗi giữa chừng khi xử lý nhiều loại ranking", nhưng tùy lỗi xảy ra ở bước SELECT hay
    bước INSERT/UPDATE mà kết quả cuối cùng khác hẳn nhau (giữ lại vs mất hết phần đã làm) — không có
    comment giải thích đây có phải chủ ý hay không. Cần lưu ý khi port: nên chọn 1 chính sách nhất quán
    (ví dụ luôn per-type transaction riêng, hoặc luôn giữ lại phần đã thành công).

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

> Không tìm thấy Lambda/cơ chế nào tương đương về bản chất. Bảng dưới đây là candidate đã tra và lý do
> không khớp (thay cho B.1/B.2) — dù trùng tên gọi "ranking", đây là 2 tính năng khác hẳn nhau.

## Đã kiểm tra

| Khu vực / candidate | Vì sao không khớp |
|---|---|
| `get-ranking-by-total-badge.ts:3-20` + `RANKING_RANGE` (`variables/constants.ts:1724-1749`) | Không phải rank/percentile so với ai — chỉ là `switch-case` theo ngưỡng điểm CỐ ĐỊNH (regular 0-9, bronze 10-19,... diamond 50+) áp lên `totalBadge` của MỘT user. Không `ORDER BY`, không `PARTITION BY`/`GROUP BY`, không so sánh giữa các user — về bản chất là hệ "tier/level" kiểu game (XP level), không phải ranking so sánh. |
| `api-user/get-ranking-of-user.ts:9-16`, `get-badge-status-for-user.ts:9-17` | Xác nhận luồng chỉ đọc `GetItem` DynamoDB theo đúng `user_id` của người gọi — không hề query/scan user khác, càng không nhóm theo thuộc tính hộ gia đình. |
| Grep `CO2`/`carbon`/`emission`/`percentile` trên toàn `src/` | Chỉ 1 kết quả: `CO2_REDUCTION: 'co2_reduction'` (tên định danh 1 loại point-badge, không tính toán CO2 thực tế nào). |
| Grep `CalcCarbonDioxide`/`ConRanking` trên toàn repo | 0 kết quả trong code (chỉ xuất hiện trong chính các file audit `docs/legacy-batch-review/` đã viết trước). |
| Toàn bộ `ScheduleExpression` trong `template.yaml` | Chỉ 3 lịch, đều daily/hourly — không có lịch monthly (`cron(... 1 * ?)`) nào, không có logic "chỉ chạy ngày 1 hàng tháng" (`dayOfMonth`) trong `src/`. |
| `UserBadgeSummaryTable`/`PointBadgeStatsTable` | Chỉ lưu tổng điểm/badge tích lũy — không có cột percentile theo 12 tháng, không có cờ xu hướng tăng/giảm/giữ nguyên kiểu `rank_status`. |

---

## Tổng kết

Không có — bản cũ chỉ có 1 pipeline tính toán (không phải 2 thuật toán song song khác bản chất; nhánh
"nhóm 5 thuộc tính vs fallback 2 thuộc tính" là 2 NHÁNH của CÙNG 1 công thức percentile, không phải 2
cách tính khác nhau cho cùng 1 việc), và hệ thống mới **không tìm thấy gì cùng bản chất** để đối chiếu —
tính năng "ranking" trùng tên ở hệ mới là 1 hệ thống hoàn toàn khác (tier theo điểm tuyệt đối, không so
sánh giữa user, không liên quan CO2) nên không tính là "thay bằng cơ chế khác" cho CÙNG bài toán — bảng
"Đã kiểm tra" ở Phần B đã nêu đủ lý do không khớp cho từng candidate.

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/conciergesv-develop/src/Command/RankingCreationCommand.php` |
| Hệ thống cũ | Ý nghĩa cột `ConRanking` + xác nhận gap `c022` | `sources/eminel_sv_lib-develop/src/Model/Entity/ConRanking.php:44-71` |
| Hệ thống cũ | Nguồn gốc `device_type=18-20` (CO2), không có trong tài liệu chính thức | `sources/conciergesv-develop/src/Command/CalcCarbonDioxideEmissionsCommand.php:185-220`; đối chứng `docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/補足資料/機器種別一覧.txt` (chỉ liệt kê tới mã 17) |
| Hệ thống cũ | Nhóm 5-thuộc-tính & population (dùng chung logic) | `docs/legacy-batch-review/CreateGroupSummary.md` |
| Hệ thống cũ | Hằng số ngưỡng nhóm nhỏ | `sources/conciergesv-develop/config/const.php:319` |
| Hệ thống cũ | Nơi đọc lại `ConRankings` (consumer, xác nhận mục đích hiển thị) | `sources/conciergesv-develop/src/Controller/GetRankingInfoController.php:164,214,317,384` |
| Hệ thống cũ | Lịch chạy (cron) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:65,68` |
| Hệ thống cũ | Danh sách batch (mô tả tiếng Nhật, nhóm server) | `docs/03_API仕様/04_バッチ一覧.md:81` |
| Hệ thống mới | Hệ "ranking" trùng tên nhưng khác bản chất (tier theo điểm tuyệt đối) | `src/layers/common/nodejs/business-logic/get-ranking-by-total-badge.ts:3-20`, `src/layers/common/nodejs/variables/constants.ts:1724-1749` (`RANKING_RANGE`) |
| Hệ thống mới | API đọc ranking (xác nhận chỉ đọc dữ liệu của chính user gọi) | `src/functions/api-user/get-ranking-of-user.ts:9-16`, `src/layers/common/nodejs/business-logic/get-badge-status-for-user.ts:9-17` |
| Hệ thống mới | Bảng point/badge (xác nhận không có percentile/xu hướng) | `UserBadgeSummaryTable`, `PointBadgeStatsTable` (`template-dynamodb.yaml`, đã audit ở `DeleteData.md`) |
| Hệ thống mới | Đối chứng không có lịch monthly nào | `template.yaml` (toàn bộ `ScheduleExpression`) |
