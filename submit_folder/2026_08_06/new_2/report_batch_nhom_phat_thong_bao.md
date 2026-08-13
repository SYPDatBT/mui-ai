# Báo cáo điều tra: nhóm 配信・通知系 (4 batch #1–#4) — có cần port sang hệ mới không?

| | |
|---|---|
| Đối tượng | 4 batch 配信・通知系 (`legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md`, server `conciergesv`): điểm エコ暖房 (#1), 省エネアドバイス (#2), push (#3), DR (#4) |
| Phạm vi | `legacy_eminel_docs`@`ccd8f56` ・ `eminel_gw_project`@`fbc0af0` ・ `syp-eminelstandard-backend`@`dc39aa39` ・ `syp-eminelstandard-web-admin`@`e550326` (branch `gw-syp-dev`) ・ `syp-eminelstandard-app-syp-dev` (snapshot). Điều tra tại `788b438`; 08-06 đối chiếu `fbc0af0` — chỉ lệch `eminel_gw_project/docs/eminel/3_requirements/app/`, đã cập nhật số dòng B05/D03, kết luận không đổi. Điều tra 2026-08-04 ・ lập 2026-08-06 |
| Vị trí | 1/3 tập (11 batch, số #1–#11 xuyên suốt, chung JP/VN); 2 tập kia: 外部連携・受信系 (#5–#7), CSV・ZIP (#8–#11) |
**Ký hiệu**:

| Ký hiệu | Nghĩa |
|---|---|
| e-smart = ESTA = EMINEL-Smart | 1 hệ 3 tên; hemssv (server GW hệ cũ) ≠ HEMS-SV (m2-cloud, mui làm — trùng tên); PI = PointInfinity (hệ điểm 北ガス); TagTag = nền tảng hội viên 北ガス |
| 必須 / 劣後 / 回答中 | bắt buộc 2026 / lùi 2027/4~ / QA đang trả lời |
| F-ES-xx ・ A03, B05, D03 ・ CLD-xx ・ [G] | mã chức năng 統合要件 v1.2 ・ section yêu cầu app (Point/DR/PUSH通知) ・ vấn đề mở (CLD-05 見守り; CLD-06 gom advice 15種→7種) ・ spec màn quản trị 省エネアドバイス |
| Bảng QA / QAデータベース ・ 確実 / *推定* / grep 0 hit | `qa_kitagas.md` gửi khách ("câu N") / QA nội bộ mui (Notion) ・ kiểm chứng trực tiếp / suy đoán có căn cứ / tìm toàn code không ra |
| `...` / comment trong khối code | ký hiệu lược bớt / chú thích của báo cáo — không phải code gốc |
| Viết tắt hạ tầng / dịch vụ | **TTL** = hạn tự xóa bản ghi của DynamoDB ・ **PITR** = Point-In-Time Recovery, backup liên tục cho phép khôi phục về thời điểm bất kỳ ・ **FCM** = Firebase Cloud Messaging, dịch vụ đẩy thông báo của Google ・ **PushCore** = server trung gian đẩy push của hệ cũ ・ **Tip** = nội dung mẹo hiển thị trong app ESTA ・ **DR** = デマンドレスポンス, điều tiết giảm nhu cầu điện khi lưới căng ・ **Xzilla** (クジラ) = nền liên kết dữ liệu phía 北ガス (cấp/nhận hợp đồng, người trả tiền, điện 30 phút… qua SFTP) |
**Mục lục**: [KẾT LUẬN](#ket-luan) ─ I: [§1](#s1) [§2](#s2) [§3](#s3) [§4](#s4) [§5](#s5) ─ II: [§6](#s6) ([#1](#s6-1) [#2](#s6-2) [#3](#s6-3) [#4](#s6-4)) [§7](#s7) [§8](#s8) [§9](#s9) [§10](#s10) [§11](#s11)

## KẾT LUẬN <a id="ket-luan"></a>
> **#1 エコ暖房ポイント** — DÙNG LẠI hạ tầng point/badge + PI連携; TẠO MỚI duy nhất phần phán định từ dữ liệu đo.
> **#2 省エネアドバイス** — TẠO MỚI engine phán định + lịch phát admin đặt; "đường ra" dùng Tip pattern sẵn có.
> **#3 Push mỗi phút** — BỎ BATCH + PushCore, GIỮ NGHIỆP VỤ — chạy bằng hạ tầng FCM gửi thẳng của e-smart.
> **#4 DR** — 2026 KHÔNG code (chỉ chốt 1 câu hỏi DR); 2027 tạo mới trên khung DR e-smart; không kế thừa mẹo "giả dạng app user".
>
> **5 điểm cần xác nhận trước khi chốt** (→ [§3](#s3)).
# PHẦN I — BÁO CÁO
## §1. Vì sao kết luận như vậy <a id="s1"></a>
Phương châm (合宿 Day3, 2026-06-25): batch hiện hành 「いけてない」 — làm lại, không port PHP; "dùng lại" = dùng cơ chế/hạ tầng e-smart ([§7](#s7)).

| | Hệ cũ (`conciergesv`) | e-smart |
|---|---|---|
| Chạy nền | cron cố định (mỗi phút ~ tháng) | 3 lịch tĩnh + one-shot động; không polling mỗi phút (grep `rate(` trong `syp-eminelstandard-backend/template.yaml`: 0 hit) |
| Push | hàng đợi DB + PushCore → FCM (*推定*) | firebase-admin gửi thẳng FCM, chia lô S3 |
| DR | ghi lệnh DB, GW poll — "giả dạng app user" | server gọi thẳng cloud hãng; lưu & khôi phục trạng thái trước DR |
| Nền | PHP 8.0 / CakePHP 4.4 / PostgreSQL | TypeScript / Lambda (Node.js 24 — `syp-eminelstandard-backend/template.yaml:181`) / DynamoDB |

| Batch | Xử lý cốt lõi cũ | Còn cần? | Vì sao |
|---|---|---|---|
| #1 | Query hộ nhiệt độ **cài đặt** TB tháng ≤22.0℃ (`s_104`) | ✅ GIỮ logic | 必須 2026 (F-ES-04) — viết lại thành Lambda đọc dữ liệu GW |
| #1 | Chống cấp trùng theo khóa lý do | ✅ có sẵn | `pointBadgeStatsSk` cùng vai trò |
| #1 | Cộng điểm + gọi PI cùng transaction, rollback | ✅ có sẵn | `givePointBadgeForUser` + Lambda PI đúng pattern |
| #1 | cron ngày 1 hàng tháng | ❌ | thay bằng 1 `ScheduleV2` tĩnh |
| #2 | 19 dòng cron cố định theo mùa | ❌ | [G] đòi lịch admin chỉnh được |
| #2 | 10 Publisher phán định từng loại | ✅ GIỮ nghiệp vụ | engine tạo mới; 判定式 đã trích vào [G] |
| #2 | Ghi advice + đăng ký push | ✅ có sẵn | Tip pattern đủ targeting + push + point |
| #3 | Hàng đợi DB + cron mỗi phút | ❌ | e-smart chia lô S3, phát theo sự kiện |
| #3 | Server trung gian PushCore | ❌ | firebase-admin gửi thẳng |
| #3 | Quản lý token + loại token hỏng | ✅ có sẵn | `TABLE_MOBILE_TOKEN_MANAGEMENT` + tự xóa lúc gửi |
| #4 | Ghi `instructions` giả dạng app user | ❌ tuyệt đối bỏ | mẹo lách GW cũ — kiến trúc mới hết tiền đề |
| #4 | GW poll qua `hemssv` | ❌ | 2027 lệnh qua HEMS-SV |
| #4 | Khung sự kiện DR | ✅ có sẵn | model + màn quản trị + push + điểm đủ; chỉ thêm nhánh "qua E-GW" |
Ngoài phạm vi — **đọc thận trọng**: monthly report của app không được tính sẵn mà forward thẳng sang TagTag API, không lưu (🔍 `syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`). **Không suy ra được từ đó rằng nhóm 集計・計算系 không có gì dùng lại**: e-smart CÓ 3 bảng lịch sử tích luỹ — `DeviceAccumulatedHistoryTable`・`DeviceDailyUsageHistoryTable`・`DeviceMonthlyUsageHistoryTable` (🔍 `syp-eminelstandard-backend/template-dynamodb.yaml:1113, 1145, 1177`), được ghi bằng `Put` kèm TTL bởi `batch-import-rinnai-monthly-usage/app.ts:18, 84`・`batch-import-rinnai-daily-usage/app.ts:18, 83`・`batch-import-noritz-hourly-usage/app.ts:18, 68`・`batch-import-rinnai-sensor-data/app.ts:17, 173`・`batch-import-noritz-sensor-data/app.ts:17, 81`. Khác biệt thật nằm ở chỗ khác: e-smart **nhận giá trị đã tính sẵn** từ Rinnai/Noritz, chưa tự tính từ số đo thô. 🔸 *Giả thuyết — CHƯA kiểm chứng*: dùng lại được đến đâu phải điều tra riêng khi vào nhóm 集計・計算系.
## §2. Hệ mới xử lý ở đâu <a id="s2"></a>

| Việc | Nơi | Loại |
|---|---|---|
| Cấp điểm/badge + chống trùng + rollback | `syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/give-point-badge-for-user.ts:57` | hàm chung — CÓ SẴN |
| Gọi PI | `syp-eminelstandard-backend/src/functions/give-point-to-point-infinity/` (+ cùng cấp `get-point-quantity-from-point-infinity/`) | Lambda — CÓ SẴN |
| Phán định エコ暖房 từ dữ liệu GW | — | CHƯA CÓ ([§6.1](#s6-1)) |
| Phát nội dung → push | `syp-eminelstandard-backend/src/functions/` (`batch-send-*` → `batch-push-notice/`) | batch — CÓ SẴN |
| Đăng ký token | `syp-eminelstandard-backend/src/functions/api-user/save-mobile-token.ts` (route: `syp-eminelstandard-backend/src/functions/api-user/app.ts:58`) | API — CÓ SẴN |
| Engine advice | — | CHƯA CÓ ([§6.2](#s6-2)) |
| Sự kiện DR | `syp-eminelstandard-backend/src/functions/` (`api-dr/`・`batch-send-dr*`・`batch-start-dr/`・`batch-end-dr/`) | API+batch — CÓ SẴN |
| Điều khiển qua E-GW | — | CHƯA CÓ — 2027, nhánh mới `syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/control-device.ts` ([§6.4](#s6-4)) |
```
nội dung (point/advice/DR/news…) ──one-shot──▶ batch phát ──▶ preprocessing chia lô 10 000 → S3
    ──▶ batch-push-notice (100 song song) ──firebase-admin──▶ FCM ──▶ app (target_screen)
```
Tư tưởng: cũ = lịch cố định + quét hàng đợi; mới = sự kiện sinh lịch, chạy xong tự xóa. **Bẫy đặt tên** (tự đếm @`dc39aa39`): `syp-eminelstandard-backend/src/functions/` **105** thư mục, **81** tên `batch-*`, nhưng lịch tĩnh `ScheduleV2` chỉ **3** — đừng suy từ tên `batch-` ra "chạy theo lịch cố định".
## §3. Điểm cần xác nhận trước khi chốt <a id="s3"></a>

| # | Điểm treo | Hệ cũ | Hệ mới/kế hoạch | Mức |
|---|---|---|---|---|
| 1 | DR: GW giữ trạng thái? (án A server phát lệnh / án B GW tự kết thúc) — ràng firmware 2026 | GW poll, không giữ | chưa quyết — câu 5 | 🔴 |
| 2 | ポイント 必須 (6/10) vs ✅劣後 (機能一覧) + giá trị điểm E-GW | 250pt, 22℃ | chưa chốt — câu 2 | 🔴 |
| 3 | Mùa cấp điểm: code quanh năm, A03 ghi 「12〜3月」 | quanh năm (確実) | nêu khi chốt A03 | 🟡 |
| 4 | Gom advice 15種→7種 (CLD-06) + lịch/判定式 [G] | 19 loại, cron cố định | câu Dự phòng 1; CLD-06 未動 | 🟡 |
| 5 | 見守り (CLD-05) | có trong hệ cũ | chưa quyết — câu 3 | 🟡 |
**Câu chữ soạn sẵn** (câu 2/3/5, Dự phòng 1 đã trong bảng QA; đây là phần thêm):
> **(Nội bộ kihara — trước khi gửi câu 5)**: 「DR終了方式について、サーバー主導（A案）とGW自律終了（B案）のどちらを前提に質問5を送るか、ファームウェア側の制約を整理させてください。GWがDR状態を保持する場合のメモリ・再起動時の挙動に制約はありますか？」
>
> **(Hỏi mui — khi chốt deploy độc lập)**: 「独立デプロイとなった場合、Push基盤のFirebaseプロジェクトとPointInfinity接続（credential）は共用できますか、それともE-GW用に新設すべきでしょうか？（QA『旧Eminel基盤継承＋独立デプロイ』のただし書きへの回答と併せて確認したい）」
>
> **(Khi review A03 — điểm 3)**: 「現行のエコ暖房ポイントは、コード上は通年・毎月実行で季節条件がありません（A03の記載『12〜3月』と食い違い）。E-GWではどちらを正としますか？」
## §4. Điểm dễ bị hiểu sai <a id="s4"></a>

| Hiểu sai | Đúng |
|---|---|
| "e-smart có point → #1 xong" | mới 2/3: PI + sổ có; **phán định từ dữ liệu đo chưa có** (grep `energy|usage` trong `src/functions/give-point-to-point-infinity/`・`get-point-quantity-from-point-infinity/`・`business-logic/give-point-badge-for-user.ts`: 0 hit) |
| "Tip = advice engine" | Tip = admin soạn tay + targeting tĩnh — engine phải tạo mới |
| "tên `batch-*` = chạy theo lịch" | 81/105 tên `batch-*` nhưng chỉ 3 lịch tĩnh ([§2](#s2)) |
| "#4 = bỏ DR" | 2026 chỉ hoãn code; **câu 5 KHÔNG hoãn được** — ràng firmware 2026 |
## §5. Việc tiếp theo <a id="s5"></a>

| # | Việc | Phụ trách |
|---|---|---|
| 1 | Chốt kihara 終了方式 A/B → gửi câu 5 (gấp nhất) | SYP+PM |
| 2 | Trả lời QA 独立デプロイ vế ただし: ① hệ cũ không batch nào đáng giữ; ② e-smart 4 ứng viên (Push ・ point/PI ・ nền nhận Xzilla SFTP→S3→DynamoDB ・ cơ chế download/export) — nhóm này góp: Push + point/PI. ⚠️ Xác nhận trước 「既存システム」 chỉ hệ nào | SYP |
| 3 | Rà 通知種別 hệ cũ → bảng mapping (nguồn mới + `target_screen`) cho D03 | SYP (+app) |
| 4 | Rà 判定式 [G] G-C-05: mỗi式 cần dữ liệu gì, lấy từ đâu (GW/TagTag/Xzilla) | SYP |
| 5 | Tách task Notion: #3 "bỏ, thay batch-push-notice", #4 "2026 không code" — khỏi đếm vào ~46本 | SYP+PM |
> **Phương châm**: bỏ batch ≠ bỏ nghiệp vụ — nghiệp vụ chuyển vào hạ tầng e-smart; code mới thật chỉ ở phần "phán định" e-smart chưa có.
# PHẦN II — CHI TIẾT KỸ THUẬT
*(Trong sơ đồ/bảng chật, tên file được rút gọn — path đầy đủ ghi tại dòng 🔍 gần nhất hoặc [§11](#s11).)*
## §6. Chi tiết từng batch <a id="s6"></a>
### 6.1 #1 `DistributeMonthlyEcoPointsCommand` — cấp エコ暖房ポイント hàng tháng <a id="s6-1"></a>
**Mục đích**: thưởng điểm hàng tháng cho hộ có nhiệt độ sưởi cài đặt TB tháng ≤22℃.
**Phán định**: BỎ = code PHP cũ ・ GIỮ = ①PI連携 + ②luồng cấp point tập trung ・ TẠO MỚI = duy nhất ③phán định từ dữ liệu đo.
**Vì sao**: ①② có sẵn trên code (cùng khuôn batch cũ); ③ không tồn tại (grep `average|_avg` toàn `syp-eminelstandard-backend/src/**/*.ts`: 0 hit ・ `eco.?point|エコ暖房`: 0 hit (riêng `energy|usage` thì CÓ hit — là các batch nhập/xuất giá trị Rinnai/Noritz đã tính sẵn, không phải logic phán định)); phương châm không port; khớp dự đoán Day3.
**Flow cũ** (確実) — bảng: `ConCustomers`・`ConSensorMonthlyValues`(`s_104`)・`ConEcoPoints`(`s_141`)・`ConPointLinkLogs` (`fetchTable` :48-51); PI cùng transaction :116-188:
```
cron 17:00 ngày 1 hàng tháng (cron :113-114) ▼ DistributeMonthlyEcoPointsCommand
    ├─ đọc s_104 …hộ nhiệt độ CÀI ĐẶT TB tháng trước ≤22.0℃   ├─ đọc ConPointLinkLogs …loại đã nhận (chống trùng)
    ├─ ghi s_141 …+250pt năm tài chính (mốc tháng 4) + ghi ConPointLinkLogs …lịch sử
    └─ gọi PointInfinity API …CÙNG transaction; lỗi → hoàn tác khách đó, chạy tiếp khách sau
```
🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php:83-104` ・ cron: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:113-114`:
```php
->matching('ConSensorMonthlyValues', fn(Query $q) => $q
    ->where(['...C_DEVICE_TYPE' => ROOM_TEMP_SETTING,                 // nhiệt độ CÀI ĐẶT
             '...' . $sensorMonthlyValuesColName . ' <=' => 22.0, ])) // TB tháng trước ≤ 22.0℃
->notMatching('ConPointLinkLogs', fn(Query $q) => $q
    ->where(['reason' => $pointLinkReason]))            // 'monthly_eco_points_YYYYMM' — chống cấp trùng
```

| Hằng số / bất thường | Giá trị |
|---|---|
| Điểm / ngưỡng / khóa chống trùng | `BENEFIT_POINTS = 250` (:33); ≤22.0℃ nhiệt độ **cài đặt**; `monthly_eco_points_YYYYMM` (= tháng trước) |
| PI lỗi | rollback riêng khách đó, tiếp tục khách sau |
| ⚠️ Mùa | chạy **quanh năm** — lệch A03 「12〜3月」 ([§3](#s3)-3) |
**e-smart**: ① PI連携 CÓ SẴN (確実) — `syp-eminelstandard-backend/src/functions/give-point-to-point-infinity/app.ts` (khai báo `syp-eminelstandard-backend/template.yaml:3282`, secret :3289); cùng họ giao thức hệ cũ (CP932 form + XML, `if0200.do`/IF0200 — `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/PointInfinity/PointInfinity.php:39, 65-71, 85-98`・`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/PointInfinity/Api/InterfaceCode.php:20`; "IF0200" không có trong backend); tra số dư `syp-eminelstandard-backend/src/functions/get-point-quantity-from-point-infinity/app.ts` (GET+`<ZNDK>` :32, 79; secret `syp-eminelstandard-backend/template.yaml:2629`):
```ts
const fuyoRiyuSjisArray = Encoding.convert(fuyoRiyuUnicodeArray, {  // :35-39 — FUYO_RIYU encode Shift_JIS
  to: 'SJIS', from: 'UNICODE', });
const regex = /<SYORI_STS>(.*?)<\/SYORI_STS>/;                      // :50 — parse XML
if (!syoriStsValue || syoriStsValue !== '000') { ... return false; } // :56 — '000' = thành công
headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=Shift_JIS' },  // :96 (POST — :92)
```
② Luồng cấp tập trung CÓ SẴN (確実) — `syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/give-point-badge-for-user.ts`: chống trùng :69 (`TABLE_POINT_BADGE_STATS`); transaction + `TABLE_USER_BADGE_SUMMARY`; 伝票 = counter `TABLE_SYSTEM_STATS` (:390-409, tên bảng :392); nơi gọi: login tháng đầu, `syp-eminelstandard-backend/src/functions/api-tip/read-tip.ts:68`, `syp-eminelstandard-backend/src/functions/api-survey/answer-survey.ts:346`, `syp-eminelstandard-backend/src/functions/batch-end-dr/app.ts:86`, liên kết thiết bị, import hội viên, checklist:
```ts
export const givePointBadgeForUser = async (      // :57 — MỌI nơi cấp điểm đều gọi
  userId: string,
  pointBadgeStatsSk: string,                      // khóa chống trùng: 'login#2026-08', 'dr#<id>'…
// Rollback transaction items if there is an error // :296-303 — PI lỗi → hoàn tác DynamoDB
  await writeOneTransaction(transactionRollbackItems);
```
③ CHƯA CÓ (確実): phán định từ dữ liệu đo — grep `energy|usage` trong `src/functions/give-point-to-point-infinity/`・`get-point-quantity-from-point-infinity/`・`business-logic/give-point-badge-for-user.ts`: 0 hit.
**E-GW**: F-ES-04 + F-ES-09; 必須 2026 (6/10) nhưng 機能一覧 ✅劣後 ([§3](#s3)-2). 🔍 `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:409, 414, 675-691`・`eminel_gw_project/docs/eminel/2_management/22_decisions.md:31`・`eminel_gw_project/docs/eminel/1_product/10_feature_list.md:93, 95`・`eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:125`・`eminel_gw_project/docs/eminel/3_requirements/app/A03_point.md:48-102`
```
GW đo ──HEMS-SV──▶ bảng TB-tháng-theo-hộ (MỚI, như s_104 — phối hợp nhóm 集計) ▼ ScheduleV2 tĩnh ngày 1 (MỚI)
Lambda phán định (MỚI — ③) ──▶ givePointBadgeForUser('eco_heating#YYYYMM') (② — 3 bảng TABLE_*)
    ──▶ give-point-to-point-infinity (①) ──POST──▶ PI …lỗi → rollback
```
**Cũ ↔ Mới**: `s_104` → `s_141` + `ConPointLinkLogs`, 1 batch PHP làm cả phán định + cấp + gọi PI ↔ bảng TB-tháng MỚI → `TABLE_POINT_BADGE_STATS`/`TABLE_USER_BADGE_SUMMARY`/`TABLE_SYSTEM_STATS` + Lambda PI riêng; chống trùng (`pointBadgeStatsSk`) và rollback dùng sẵn — **chỉ viết mới tầng phán định**.
Luồng data — Cũ: `s_104` → lọc ≤22℃ → +250pt `s_141` + log `ConPointLinkLogs` → PI ↔ Mới: bảng TB-tháng (mới) → Lambda phán định → `TABLE_POINT_BADGE_STATS`・`TABLE_USER_BADGE_SUMMARY`・`TABLE_SYSTEM_STATS` → PI.
1. Chốt spec qua QA/A03: 250?, 22℃?, mùa?, 必須/劣後 (câu 2) — *tham số ③ nằm hết đây*.
2. Chờ spec HEMS-SV; thiết kế bảng TB tháng (phối hợp nhóm 集計) — *thiếu đầu vào thì bước 3 bí*.
3. Lambda phán định mới (`syp-eminelstandard-backend/src/functions/`, lệ `batch-*`); thêm FUYO_RIYU vào `syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts` (mẫu :1756-1762) — *phần mới chỉ là lớp mỏng*.
4. Thêm 1 `ScheduleV2` tĩnh (`syp-eminelstandard-backend/template.yaml`) — *chu kỳ cố định, không cần one-shot*.
5. Test: chạy 2 lần không trùng; PI lỗi → rollback; đối chiếu query cũ (テスト=mui/実装=SYP) — *2 rủi ro: trùng + lệch sổ*.
### 6.2 #2 `PublishRegularEcoMissionsCommand` — phát 省エネアドバイス định kỳ <a id="s6-2"></a>
**Mục đích**: chọn hộ theo điều kiện, gửi lời khuyên tiết kiệm phù hợp (19 loại).
**Phán định**: BỎ = batch + 19 cron + code 10 Publisher (判定式 giữ qua bản trích [G]) ・ GIỮ = "đường ra" Tip pattern ・ TẠO MỚI = engine + lịch admin đặt (G-A-02).
**Vì sao**: e-smart không có engine (grep 0 hit); [G] đòi lịch admin chỉnh — cron chết không đáp ứng; đường ra sẵn; 判定式 đã trích, bỏ code không mất.
**Flow cũ** (確実) — 1 command + option `--eco-mission-id` (folder 11 file, 1 là option class — 「11種Publisher」 đếm cả nó); bảng (`legacy_eminel_docs/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php:7-13, 30-34`): `ConEcoMissions`・`ConEcoMissionDestinations`・`ConRegularEcoMissions`・`PushMessages`・`PushMessageDestinations`; *19 loại → 10 Publisher; 15 = 「約15種」 CLD-06 → án 7種+エコ暖房*:
```
19 dòng cron (cron :84-102) …15 theo mùa, 4 (id 1/2/3/19) thông năm ▼ --eco-mission-id 1..19 ──▶ 10 Publisher
    ├─ phán định điều kiện từng loại (quá TB, quên hẹn giờ, tỷ lệ sưởi, kỷ niệm hợp đồng…)
    ├─ ghi ConEcoMissions + ConEcoMissionDestinations   └─ ghi PushMessages + PushMessageDestinations (hẹn +1 phút)
         ▼  gửi thật do #3 (§6.3) quét mỗi phút
```
🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php:142-150` (+ `legacy_eminel_docs/sources/conciergesv-develop/src/Command/PublishRegularEcoMissionsCommand.php:54-140`, `legacy_eminel_docs/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php:60-82, 112-152`) ・ cron: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:84-102`:
```php
foreach ($this->PushMessageDestinations->createByEmsSp($emsSp) as $pd) {
    $pd->schedule = FrozenTime::now()->addMinutes(1);   // push hẹn PHÁT SAU 1 PHÚT
    ...
$this->ConEcoMissionDestinations->saveManyOrFail($ecoMissionDestinations);
$this->PushMessageDestinations->saveManyOrFail($pushMessageDestinations);
```
**e-smart**: KHÔNG có engine (確実) — grep `advice|アドバイス|mission|ミッション|判定`: 0 hit thật (đều `permission`). Gần nhất = Tip (`syp-eminelstandard-backend/src/layers/common/nodejs/models/Tip.ts:4-22`): targeting 3 kiểu tĩnh (`syp-eminelstandard-backend/src/functions/batch-send-tip-preprocessing/app.ts:43-50`); điểm khi đọc `syp-eminelstandard-backend/src/functions/api-tip/read-tip.ts:68` (`TABLE_TIP_STATS`/`TABLE_TIP_USER_ACTION`); không hàm nào đọc dữ liệu năng lượng (grep `energy|usage` trong `api-tip`: 0 hit):
```ts
export interface Tip {
  target_type?: string;          // ALL / thuộc tính / CSV — KHÔNG có "theo dữ liệu năng lượng"
  body_tip?: IBodyTipItem[];     // nội dung admin soạn
  send_time?: number;            // giờ phát admin đặt (one-shot §7)
  point_quantity?: number;       // điểm khi đọc
  push_notice_flag?: boolean; ...
```
**E-GW**: scope 2026 (F-ES-03 必須); [G] đòi lịch admin chỉnh; 15種→7種 chưa chốt (CLD-06); 判定式 T.B.D (G-C-05 — đã trích vào [G]). 🔍 `eminel_gw_project/docs/eminel/4_spec/admin/G_energy_advice.md:18-19, 28-29, 47`・`eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:632-647`・`eminel_gw_project/docs/eminel/2_management/20_open_issues.md:176-177`
```
[web-admin] tạo advice + lịch định kỳ (G-A-02, UI MỚI) ──put-schedule.ts──▶ BatchJudgeAdvice (MỚI, per loại)
    ──▶ BatchSendAdvice (MỚI — mẫu batch-send-tip; ghi bảng Advice MỚI) ──one-shot──▶ BatchPushNotice (§6.3) ──▶ FCM
```
**Cũ ↔ Mới**: 19 dòng cron cố định → 10 Publisher → `ConEcoMissions`(+`ConEcoMissionDestinations`) + `PushMessages`(+`PushMessageDestinations`) ↔ lịch admin tự đặt (G-A-02) → BatchJudgeAdvice → BatchSendAdvice (bảng `Advice` MỚI) → BatchPushNotice — **đường ra tái dùng, tầng judgment làm mới**.
Luồng data — Cũ: 19 cron → 10 Publisher → `ConEcoMissions`+`ConEcoMissionDestinations` & `PushMessages`+`push_message_destinations` (hẹn +1 phút) → #3 gửi ↔ Mới: lịch admin → `BatchJudgeAdvice` → bảng `Advice` (mới) → `BatchPushNotice` → FCM.
1. Chờ/thúc CLD-06 (câu Dự phòng 1); rà 判定式 [G] G-C-05 → map đầu vào + nguồn (GW/TagTag/Xzilla) — *bảng quyết khối lượng*.
2. Model `Advice` phỏng `Tip` (`syp-eminelstandard-backend/src/layers/common/nodejs/models/` + `interfaces/`), giữ target/point/push + thêm điều kiện + lịch — *cùng khuôn thì đường phát dùng lại*.
3. Skeleton: `BatchJudgeAdvice`→`BatchSendAdvice`→`BatchPushNotice` (mẫu `syp-eminelstandard-backend/src/statemachine/batch-send-tip.asl.json`・`batch-push-notice-tip-new.asl.json` + `syp-eminelstandard-backend/template.yaml`; nối theo `syp-eminelstandard-backend/src/functions/api-news/common.ts:207-209`); judgment trả rỗng — *test đường phát trước, kịp tháng 9*.
4. UI theo `syp-eminelstandard-web-admin/components/tip/tip-form.vue` + khối đặt lịch (mới) — *UI phần lớn có sẵn*.
5. Mỗi loại 1 Lambda judgment → ghi advice + enqueue push — *khớp 1 batch = 1 task*.
6. Test: bộ dữ liệu biên đúng/sai ngưỡng, trước 結合フェーズ — *sai biên = phát nhầm/sót*.
### 6.3 #3 `DispatchPushMessagesCommand` — gửi push mỗi phút <a id="s6-3"></a>
**Mục đích**: "cửa gửi" chung — mọi thông báo hệ cũ đều qua đây tới máy user.
**Phán định**: BỎ = batch + hàng đợi DB + cron mỗi phút + PushCore ・ GIỮ = nghiệp vụ gửi push ・ THAY = hạ tầng FCM e-smart; deploy độc lập thì dựng lại stack đó.
**Vì sao**: e-smart đủ bộ (FCM+token+fan-out); D03: 「全要件がESTA既存のため【新規】なし」; kiến trúc cũ ngược nguyên tắc "không polling"; PushCore không có code trong repo.
**Flow cũ** (確実) — bảng `PushMessageDestinations` (:14, 40); retry `legacy_eminel_docs/sources/conciergesv-develop/config/push_message.php:4-14`:
```
cron mỗi phút (cron :79-80) ▼ DispatchPushMessagesCommand
    ├─ đọc push_message_destinations …đến hạn, 500 bản ghi/trang
    ├─ validate: đúng MỘT trong device_token / FCM topic (sai → STATUS_INVALID)
    └─ POST ──▶ PushCore (localhost:54650 /v2/send-messages) ──▶ FCM (*推定*) …retry 3 phút × 5 lần
```
🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php:65-79` (toàn thân :51-177)・`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/StaticServices/PushMessageService.php:26, 36-39` ・ cron: `mng-webap_cron設定_20241029.txt:79-80` (path đủ ở §6.1):
```php
$limit = 500;                                        // :65 — 500 bản ghi/trang
$query = $this->PushMessageDestinations->find()      // :68 — lấy bản ghi đến hạn
    ...
    ->where(['status' => PushMessageDestination::STATUS_SCHEDULED, 'schedule >=' => $startAt, 'schedule <=' => $endAt])
$this->apiUrl = $this->getPushCoreHost() . '/v2/send-messages';        // PushMessageService :26
return Configure::read('PushCore.Api.host', 'http://localhost:54650'); // :38
```
**e-smart**: CÓ ĐẦY ĐỦ (確実). ① Token — `syp-eminelstandard-backend/src/layers/common/nodejs/models/MobileTokenManagement.ts` (nguyên văn; bảng `TABLE_MOBILE_TOKEN_MANAGEMENT`; API `user/save_mobile_token` — `syp-eminelstandard-backend/src/functions/api-user/save-mobile-token.ts`, route `syp-eminelstandard-backend/src/functions/api-user/app.ts:58`):
```ts
export interface MobileTokenManagement {
  user_id: string;
  mobile_token: string;   // token FCM — app đăng ký qua user/save_mobile_token
}
```
② FCM trực tiếp + tự dọn token — 🔍 `syp-eminelstandard-backend/src/layers/common/nodejs/services/push-notification-firebase.ts:87-97`:
```ts
await firebaseAdmin.messaging().send(notificationMessage);   // gửi từng token
if (errorCode === 'messaging/invalid-registration-token' ||
    errorCode === 'messaging/registration-token-not-registered' || ...) {
  await removeMobileTokenInvalid(mobileToken);               // token chết → xóa
```
③ Fan-out — 🔍 `syp-eminelstandard-backend/src/functions/batch-push-notice/app.ts:17-34`; lô 10 000 (`syp-eminelstandard-backend/src/functions/batch-push-notice-tip-new-preprocessing/app.ts:53`); 100 song song (hằng `syp-eminelstandard-backend/src/layers/common/nodejs/services/push-notice-to-user.ts:21`); opt-in `TABLE_USER_SETTING` (cùng file :35-60, env :19); `target_screen` khớp app (`syp-eminelstandard-app-syp-dev/lib/presentation/pages/main/bottom_navigation_view.dart:473-528`; token :101-111); 6 state machine: survey/news/tip/DR-new/DR-start/DR-end (`syp-eminelstandard-backend/template.yaml:510/685/815/1889/1927/1965`):
```ts
const dataPushNotice: IDataPushNotice = await getDataJSONFromS3(
  BUCKET_TEMPORARY as string, `${targetFileTemp}_${segmentIndex}.json`); // đọc 1 LÔ từ S3
  target_screen: dataPushNotice?.data?.target_screen,   // app điều hướng khi bấm
const promisesPushNoticeForUser = listTargetUser.map((targetUser) =>
  pushNoticeToUser(targetUser.user_id, dataPushNoticeForUser));
await Promise.allSettled(promisesPushNoticeForUser);    // song song, chờ hết
```
**E-GW**: D03 (file: レビュー中; slide khách: レビュー前 — `eminel_gw_project/docs/eminel/3_requirements/app/README.md:64`): 踏襲元 = ESTA Push基盤＋現行（通知種別の網羅）, 「全要件がESTA既存のため【新規】なし」. 🔍 `eminel_gw_project/docs/eminel/3_requirements/app/D03_push.md:5, 7, 29-31, 81-83`
```
Batch phát xong (6 hệ) ──one-shot──▶ preprocessing chia lô 10 000 → S3 ──▶ batch-push-notice (100 song song)
    ── opt-in: TABLE_USER_SETTING ── token: TABLE_MOBILE_TOKEN_MANAGEMENT ──▶ FCM ──▶ app …token chết tự xóa
```
**Cũ ↔ Mới**: hàng đợi DB `push_message_destinations` → PushCore → FCM, cron quét mỗi phút ↔ S3 (lô 10 000) → batch-push-notice (100 song song) → FCM trực tiếp, kích hoạt one-shot — **bỏ hàng đợi DB + PushCore + polling**.
Luồng data — Cũ: `push_message_destinations` (cron mỗi phút, 500/trang) → PushCore → FCM ↔ Mới: 6 state machine → lô 10 000 JSON trên S3 (`BUCKET_TEMPORARY`) → `batch-push-notice` (100 song song; token `TABLE_MOBILE_TOKEN_MANAGEMENT`, opt-in `TABLE_USER_SETTING`) → FCM.
1. Đưa "Push 基盤 (FCM)" vào trả lời QA 独立デプロイ ([§5](#s5)-2, [§10](#s10)-B2) — *quyết tách Firebase hay không*.
2. Rà 通知種別 (vế 「＋現行」 D03): 19 advice, DR, 見守り (CLD-05), report… → map nguồn mới + `target_screen` — *D03 không chốt nổi nếu thiếu*.
3. Nếu độc lập: Firebase riêng + bảng token + API save_mobile_token — *pattern đủ, chỉ cấu hình + credential*.
4. KHÔNG lập task port — ghi "bỏ, thay batch-push-notice" trên Notion — *khỏi méo ~46本*.
5. Test: token thật; token chết tự xóa; giới hạn 4096 byte (`syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts:223`) — *3 kiểu sự cố push*.
### 6.4 #4 `ControlDrOperationCommand` — điều khiển chỉ lệnh DR <a id="s6-4"></a>
**Mục đích**: khi có DR, server tự vận hành máy sưởi các hộ tham gia.
**Phán định**: 2026 KHÔNG code (chỉ bước 1) ・ BỎ = toàn bộ kiểu cũ (cron mỗi phút, `instructions`, GW poll, giả dạng) ・ 2027 = tạo mới trên khung DR e-smart, thêm nhánh qua GW.
**Vì sao**: DR = 劣後 2027/4~ (6/10; B05: 26年スコープ=なし); khung DR sẵn — thêm 1 nhánh là xong; "giả dạng" hết tiền đề ở kiến trúc mới; riêng câu 5 ràng firmware 2026.
**Flow cũ** (確実) — bảng (`fetchTable` :56-61): `ConDrOperations`・`ConDevices`・`ConDeviceControls`・`ConDeviceStatuses`・`HemsGws`・`Instructions`; ghi `instructions` từ :210 (`ems_sp_no`・`node_id`・`eoj`):
```
cron mỗi phút (cron :76-77) ▼ ControlDrOperationCommand (2 phase; né xung đột 5 phút/hộ)
    ├─ đọc ConDrOperations + hems_gws + t_201 (ConDevices)   ├─ ghi ConDeviceControls
    └─ ghi instructions (宅外制御指示 — ECHONET; EPC 80/B0) ※GIẢ DẠNG thao tác app user
         ▼  GW poll qua hemssv → điều khiển thiết bị
```
🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php:171-172` ・ cron: `mng-webap_cron設定_20241029.txt:76-77` (path đủ ở §6.1):
```php
// 暖房制御ユニットとユーザのアプリ端末の情報を取得
// ユーザのアプリ端末からの操作のように見せかけないとゲートウェイが指令を無視する
```
**e-smart**: CÓ KHUNG DR KHÁC KIỂU (確実). ① Model — `syp-eminelstandard-backend/src/layers/common/nodejs/models/Dr.ts:5-30`・`syp-eminelstandard-backend/src/layers/common/nodejs/models/DrUserAction.ts:1-14` (bảng: `TABLE_DR` — `syp-eminelstandard-backend/src/functions/api-dr/create-dr.ts`; `TABLE_DR_USER_ACTION` — `batch-start-dr`; `TABLE_DR_STATS` — `batch-send-dr-complete`):
```ts
export interface Dr {
  implement_start_time?: number;   // start/end → one-shot
  target_type?: string;  control_setting: IControlSetting[];  // targeting như news/tip; điều khiển gì trên thiết bị nào
  push_notice_new_dr?: IPushNotice;    // 3 mốc push ・ has_badge / point_quantity ...
export interface DrUserAction {
  pre_control_status?: { device_id: string; server_type: string; ... // trạng thái TRƯỚC DR — để khôi phục
```
② Start/end — 🔍 `syp-eminelstandard-backend/src/functions/batch-start-dr/app.ts:55-65`・`syp-eminelstandard-backend/src/functions/batch-end-dr/app.ts:82-94`; lưu `pre_control_status` :212; khôi phục :96-190; thiết bị Rinnai/Noritz/Daikin/MUI hồng ngoại (:139-188) — đều cloud hãng, không qua GW; lõi `controlDevice` (`syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/control-device.ts`, 4 nhánh `SERVER_TYPE`) do `handleControlDevice` (`batch-start-dr/app.ts:81`) gọi; lịch 2 tầng: PHÁT khi admin tạo/sửa (`syp-eminelstandard-backend/src/functions/api-dr/create-dr.ts:111`・`syp-eminelstandard-backend/src/functions/api-dr/update-dr.ts:149`), start/end khi phát xong (`syp-eminelstandard-backend/src/functions/batch-send-dr-complete/app.ts:127-143`); web-admin đủ màn DR (`syp-eminelstandard-web-admin/pages/distribution-management/dr/` + `syp-eminelstandard-web-admin/components/dr/dr-form.vue` — 1881 dòng):
```ts
handleControlDevice(drUserAction.user_id, drInfo.control_setting, drId)   // start: điều khiển từng user
const pointBadgeStatsSK = `dr#${drId}`;                                   // end: trả điểm người đi tới cùng
await givePointBadgeForUser(userId, pointBadgeStatsSK, ...);              // rồi khôi phục theo pre_control_status
```
**E-GW**: F-ES-07/08 + F-AD-08 — 劣後 2027/4~; tương lai: server chủ động, lệnh qua HEMS-SV; 終了方式 A/B chưa chốt — câu 5. 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md:30-31`・`eminel_gw_project/docs/eminel/3_requirements/app/B05_dr.md:8, 32-34`・`eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:113-122` (~17項目)
**Flow mới (2027 — 2026 KHÔNG implement) + bước**:
```
[web-admin] dr-form.vue ─ api-dr/create-dr.ts:111・update-dr.ts:149 → TABLE_DR + one-shot PHÁT
    ▼ BatchSendDr ─ phát xong → batch-send-dr-complete:127-143 đăng ký start/end (TABLE_DR_STATS)
batch-start-dr ─ handleControlDevice → controlDevice ─ 4 nhánh sẵn + nhánh MỚI 2027 "qua E-GW" (API HEMS-SV) ─ lưu pre_control_status (TABLE_DR_USER_ACTION)
batch-end-dr ─ cấp điểm ('dr#<id>') + khôi phục theo pre_control_status
```
**Cũ ↔ Mới**: `ConDrOperations` + `hems_gws` + `t_201` → ghi `instructions` (giả dạng thao tác app user), GW poll qua `hemssv` ↔ `TABLE_DR`/`TABLE_DR_USER_ACTION`/`TABLE_DR_STATS`, server chủ động điều khiển thiết bị (2027 thêm nhánh qua HEMS-SV) — **bỏ hẳn cơ chế giả dạng + poll**.
Luồng data — Cũ: `ConDrOperations` → (cron mỗi phút) `instructions` [giả dạng app user] → GW poll `hemssv` → thiết bị ↔ Mới: `TABLE_DR` → phát → one-shot start/end → `controlDevice` (4 nhánh + 1 nhánh E-GW 2027) → thiết bị; trạng thái lưu/khôi phục tại `TABLE_DR_USER_ACTION.pre_control_status`.
1. (2026 — duy nhất) Chốt kihara → câu 5 (văn bản [§3](#s3)) — *firmware 2026 không chờ được*.
2. (2027) Dùng lại trọn lớp sự kiện DR (model + màn admin + targeting + push + điểm) — *không phụ thuộc cách điều khiển*.
3. (2027) Thêm nhánh `SERVER_TYPE` "qua E-GW" trong `controlDevice`, gọi API HEMS-SV — *ngang hàng 4 nhánh = đổi nhỏ nhất*.
4. (2027) Map `pre_control_status` cho thiết bị qua GW — *phụ thuộc bước 1*.
5. (2027) Tách task theo Day3 (~17項目) — *tránh "nhồi 1 batch"*.
6. Test (2027): hỗn hợp nhánh cũ/mới, giải ước giữa chừng, khôi phục — *chỗ dễ vỡ nhất*.
## §7. Hạ tầng chung & tiền đề <a id="s7"></a>
**Nền lịch**: 3 lịch tĩnh (`ScheduleV2`, `Asia/Tokyo` — `syp-eminelstandard-backend/template.yaml:9-11`): ① `BatchRunSequentially` `cron(5 0-7 * * ? *)` (:853-888, cron :881-882) — chuỗi nhận 8 kênh IF Xzilla; ② `BatchMigrationIntegratedData` `cron(0 8 * * ?)` (:2205-2240, :2233) — xuất 6 CSV thiết bị lên SFTP `/EST`; ③ `BatchGetErrorDeviceInfoOfRinnai` 8:00 (:2966-2980) — lấy thông tin lỗi thiết bị Rinnai. Còn lại đều lịch động — 🔍 `syp-eminelstandard-backend/src/layers/common/nodejs/services/put-schedule.ts:18-33` (build `syp-eminelstandard-backend/src/layers/common/nodejs/utils/date-utils.ts:117`); ví dụ: `syp-eminelstandard-backend/src/functions/api-news/common.ts:207-209`, `syp-eminelstandard-backend/src/functions/batch-send-news-complete/app.ts:72-80`; automation mỗi rule 1 lịch tuần (`syp-eminelstandard-backend/src/functions/api-automation/common.ts:115`); không polling (grep `rate(` trong `syp-eminelstandard-backend/template.yaml`: 0 hit). 💡 G-A-02 đã có lời giải sẵn = pattern này:
```ts
return await scheduler.createSchedule({
  ScheduleExpression: scheduleExpression,          // vd cron(30 14 15 8 ? 2026) — một thời điểm
  Target: { Arn: resourceArn, ..., Input: JSON.stringify(inputData) },
  ActionAfterCompletion: isDeleteAfterCompletion
    ? ActionAfterCompletion.DELETE : ActionAfterCompletion.NONE, ...  // chạy xong TỰ XÓA
```

| Kênh | Nguồn phát sinh | Bảng đích | Tác dụng |
|---|---|---|---|
| Token FCM | app đăng ký `user/save_mobile_token` (`api-user/save-mobile-token.ts`) | `TABLE_MOBILE_TOKEN_MANAGEMENT` | địa chỉ push; token chết tự xóa |
| Cờ nhận push | user đặt trong app | `TABLE_USER_SETTING` | lọc opt-in lúc gửi (`syp-eminelstandard-backend/src/layers/common/nodejs/services/push-notice-to-user.ts:19, 35-60`) |
| Point/badge | mọi sự kiện gọi `givePointBadgeForUser` | `TABLE_POINT_BADGE_STATS`・`TABLE_USER_BADGE_SUMMARY`・`TABLE_SYSTEM_STATS` | sổ + chống trùng + 伝票; đồng bộ PI |
| Trạng thái đọc Tip | `api-tip/read-tip.ts:68` | `TABLE_TIP_STATS`・`TABLE_TIP_USER_ACTION` | đã đọc + điểm khi đọc — "đường ra" #2 tái dùng |
| Sự kiện DR | admin tạo/sửa (`api-dr/create-dr.ts`) | `TABLE_DR`・`TABLE_DR_USER_ACTION` (`pre_control_status`)・`TABLE_DR_STATS` | sự kiện + tham gia + khôi phục + thống kê |
**Tiền đề** (chung 3 tập):
- Day3: làm lại, 1 batch = 1 task, バッチボーン trước, chạy thật trước 結合フェーズ (tháng 9); batch/外部連携 giao SYP. 🔍 `eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:35, 51, 99-103, 147-149`
- Deploy: QA 独立デプロイ (swan, 回答中) tạm *hướng độc lập* → "dùng lại" ≠ 0 công; `gw-syp-dev` chưa có commit E-GW (web-admin: `git log origin/main..gw-syp-dev` rỗng; backend: 15 commit gần nhất thuần e-smart). 🔸 Khả năng viết thêm vào codebase e-smart — suy từ QA 管理画面 (masao takahashi, 回答中), chưa thành văn; "chung source" ≠ "chung môi trường". Phạm vi SYP: QA 調査範囲 (swan, 回答中) — `conciergesv`/`eminelsv` chỉ là đối tượng điều tra; GW giao tiếp qua HEMS-SV, spec sau.
- Scope 6/10 (決定ログ): 必須 = 暖房/暖房制御/照明アドバイス※/ポイント連携/グルーピング・レポート; 劣後 = 複合制御・DR・ダッシュボード・バッジ等; ※nghi lỗi ghi 省エネアドバイス (*推定*). 機能一覧: ✅ = lùi được 2027, trống = 必須. 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md:30-31`. Chủ thể bước §6 = SYP, branch `gw-syp-dev`; nhân sự: swan, masao takahashi (mui — QA), kihara (mui — firmware GW).

| | Hệ cũ | e-smart |
|---|---|---|
| Ngôn ngữ | PHP 8.0 / CakePHP 4.4 | TypeScript / SAM + Lambda (Node.js 24 — `syp-eminelstandard-backend/template.yaml:181`) |
| DB | PostgreSQL (partition ngày/tháng) | DynamoDB (PITR bật) |
| Batch | cron server + shell flock | Step Functions + EventBridge Scheduler |
| Nhận file | SFTP về đĩa | SFTP → S3 → DynamoDB |
🔍 `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:1-37`・`syp-eminelstandard-backend/template.yaml`・`eminel_gw_project/docs/eminel-smart/02_product_overview.md:48-53`
## §8. Đối chiếu dữ liệu cũ ↔ mới <a id="s8"></a>

| Dữ liệu | Hệ cũ (PostgreSQL) | Hệ mới (DynamoDB) | Trạng thái |
|---|---|---|---|
| TB tháng cảm biến | `s_104` (`ConSensorMonthlyValues`) | bảng TB-tháng — [§6.1](#s6-1) bước 2 | ❌ phải tạo |
| Sổ điểm | `s_141` (`ConEcoPoints` — dồn năm tài chính) | `TABLE_POINT_BADGE_STATS` (per sự kiện) + `TABLE_USER_BADGE_SUMMARY` | ⚠️ khác bản chất |
| Lịch sử cấp/chống trùng | `ConPointLinkLogs` (khóa `reason`) | `pointBadgeStatsSk` trong `TABLE_POINT_BADGE_STATS` | ✅ có |
| Số 伝票 PI | — (không ghi nhận) | counter `TABLE_SYSTEM_STATS` (:390-409) | ✅ có |
| Advice + đích nhận | `ConEcoMissions` + `ConEcoMissionDestinations` (+`ConRegularEcoMissions`) | model `Advice` — [§6.2](#s6-2); gần nhất Tip | ❌ phải tạo |
| Hàng đợi push | `PushMessages` + `push_message_destinations` | không có — lô JSON S3 (`BUCKET_TEMPORARY`) dùng xong bỏ | ⚠️ khác bản chất |
| Token | device_token/topic theo bản ghi hàng đợi | `TABLE_MOBILE_TOKEN_MANAGEMENT` | ✅ có |
| Cờ nhận push | — (chưa xác minh) | `TABLE_USER_SETTING` (:19, 35-60) | ✅ có |
| Chỉ lệnh DR | `ConDrOperations` + `instructions` | `TABLE_DR`+`TABLE_DR_USER_ACTION`+`TABLE_DR_STATS`; server gọi thẳng | ⚠️ khác bản chất |
| Trạng thái trước DR | — (không ghi nhận) | `DrUserAction.pre_control_status` | ✅ có |
**Đếm**: ✅ 5 ・ ⚠️ 3 ・ ❌ 2.

| Cơ chế | Hệ cũ | Hệ mới |
|---|---|---|
| Đường push | hàng đợi DB, cron mỗi phút, 500/trang → PushCore → FCM (*推定*) | lô 10 000 → S3 → `batch-push-notice`, 100 song song, FCM trực tiếp |
| Token / cờ nhận | token theo bản ghi hàng đợi / — | `TABLE_MOBILE_TOKEN_MANAGEMENT` (API save_mobile_token) / `TABLE_USER_SETTING` (:19, 35-60) |
| Sổ điểm | `s_141` + `ConPointLinkLogs` | `TABLE_POINT_BADGE_STATS`+`TABLE_USER_BADGE_SUMMARY`+`TABLE_SYSTEM_STATS` |
| PI連携 | `PointInfinity.php` (CP932+XML) | `give-point-to-point-infinity` (Shift_JIS+XML — cùng họ) |
| Advice | 19 cron + 10 Publisher → `ConEcoMissions`/`PushMessage*` | chưa có (#2 tạo mới); gần nhất Tip + one-shot |
| DR | `ConDrOperations` → `instructions` → GW poll (`hemssv`) | `TABLE_DR`/`TABLE_DR_USER_ACTION`/`TABLE_DR_STATS` → server gọi `controlDevice` |
| Kích hoạt | cron cố định `/etc/cron.d/eminel-mng-webap` | 3 `ScheduleV2` + one-shot động ([§7](#s7)) |
## §9. Lựa chọn thiết kế <a id="s9"></a>
Không có phương án A/B/C cấp báo cáo; 終了方式 A/B của DR là câu hỏi khách quyết ([§3](#s3)-1, [§10](#s10)-A1).
## §10. QA theo đối tượng <a id="s10"></a>
**A = khách 北ガス qua PM** (câu 2/3/5・Dự phòng 1 đã trong bảng QA, chưa gửi) ・ **B = mui**:

| # | Câu hỏi | Vì sao | Mức |
|---|---|---|---|
| A1 | Câu 5: GW giữ trạng thái DR? (án A/B) | ràng firmware 2026 ([§6.4](#s6-4) bước 1) | 🔴 |
| A2 | Câu 2: ポイント 必須 hay 劣後? + giá trị điểm | mâu thuẫn 6/10 vs 機能一覧; scope #1 | 🔴 |
| A3 | Dự phòng 1: gom 15種→7種 (CLD-06) | quyết số Lambda + danh mục #2 | 🟡 |
| A4 | Câu 3: 見守り (CLD-05)? | quyết 通知種別 | 🟡 |
| A5 | (khi review A03 — soạn sẵn [§3](#s3)) mùa 12〜3月 hay quanh năm? | code quanh năm vs A03 | 🟡 |
| B1 | (nội bộ, trước A1) kihara: ràng buộc firmware nếu GW giữ trạng thái DR? | câu 5 cần tiền đề kỹ thuật | 🔴 |
| B2 | Deploy độc lập: Firebase + credential PI chung hay tách? (kèm trả lời ただし 2 vế) | quyết [§6.3](#s6-3) bước 3 | 🟡 |
| B3 | D03: file レビュー中 vs slide レビュー前 — bên nào chuẩn? | độ tin căn cứ "全要件ESTA既存" | 🟢 |
**C. Bên bàn giao**: C1 — ý nghĩa nghiệp vụ 19 advice (chỉ khi [G] không đủ lúc map 判定式) 🟢. **D. Team app**: D1 — `target_screen` cho từng 通知種別 (D03, [§6.3](#s6-3) bước 2) 🟡.
```
B1 (kihara) ──▶ A1 (câu 5 DR)  ★gấp nhất — firmware 2026      A2 ──▶ chốt A03 ──▶ A5 cùng dịp
A3 (CLD-06) ──▶ §6.2 bước 2–5      B2 ──▶ §6.3 bước 3 (khi chốt độc lập)      A4 + D1 ──▶ bảng 通知種別 cho D03 ──▶ (C1 nếu cần)
```
## §11. Căn cứ & độ chắc chắn <a id="s11"></a>

| Nội dung | Nguồn (path đầy đủ) |
|---|---|
| 4 batch cũ | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/`: `DistributeMonthlyEcoPointsCommand.php` (:33, 48-51, 83-104, 116-188), `PublishRegularEcoMissionsCommand.php` (:54-140) + `PublishRegularEcoMission/EcoMissionPublisher.php` (:7-13, 30-34, 60-82, 112-152), `DispatchPushMessagesCommand.php` (:14, 40, 51-177), `ControlDrOperationCommand.php` (:56-61, 171-172, 210~); `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/PointInfinity/PointInfinity.php:39, 65-71, 85-98`・`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/PointInfinity/Api/InterfaceCode.php:20`・`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/StaticServices/PushMessageService.php:26, 36-39`; `legacy_eminel_docs/sources/conciergesv-develop/config/push_message.php:4-14`; cron: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt` #1 :113-114, #2 :84-102, #3 :79-80, #4 :76-77 |
| Point/PI mới | `syp-eminelstandard-backend/src/functions/give-point-to-point-infinity/app.ts` (:15, 35-39, 50, 56, 92, 96; khai báo `syp-eminelstandard-backend/template.yaml:3282`), `syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/give-point-badge-for-user.ts` (:57, 69, 296-303, 390-409), `syp-eminelstandard-backend/src/functions/get-point-quantity-from-point-infinity/app.ts` (:32, 79) |
| Push mới | `syp-eminelstandard-backend/src/layers/common/nodejs/models/MobileTokenManagement.ts`, `…/services/push-notification-firebase.ts:87-97`, `…/services/push-notice-to-user.ts:19, 21, 35-60`, `syp-eminelstandard-backend/src/functions/batch-push-notice/app.ts:17-34`, `…/batch-push-notice-tip-new-preprocessing/app.ts:53`, `…/api-user/save-mobile-token.ts` + `…/api-user/app.ts:58`, `syp-eminelstandard-app-syp-dev/lib/presentation/pages/main/bottom_navigation_view.dart:101-111, 473-528` |
| DR mới | `syp-eminelstandard-backend/src/layers/common/nodejs/models/Dr.ts:5-30`, `…/models/DrUserAction.ts:1-14`, `…/business-logic/control-device.ts`, `syp-eminelstandard-backend/src/functions/batch-start-dr/app.ts:55-65, 81, 212`, `…/batch-end-dr/app.ts:82-94, 96-190, 139-188`, `…/batch-send-dr-complete/app.ts:127-143`, `…/api-dr/create-dr.ts:111`, `…/api-dr/update-dr.ts:149`, `syp-eminelstandard-web-admin/pages/distribution-management/dr/` + `syp-eminelstandard-web-admin/components/dr/dr-form.vue` |
| Nền lịch | `syp-eminelstandard-backend/template.yaml:9-11, 181, 853-888, 2205-2240, 2966-2980`, `syp-eminelstandard-backend/src/layers/common/nodejs/services/put-schedule.ts:18-33`, `…/utils/date-utils.ts:117`, `syp-eminelstandard-backend/src/functions/api-news/common.ts:207-209`, `…/batch-send-news-complete/app.ts:72-80`, `…/api-automation/common.ts:115, 167-175` |
| Yêu cầu E-GW | `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` (:409, 414, 632-647, 675-691), `…/1_product/10_feature_list.md:93, 95`, `…/2_management/22_decisions.md:30-31`, `…/2_management/20_open_issues.md:176-177`, `…/2_management/minutes/20260625_egw_camp_day3.md` (:35, 51, 99-103, 113-122, 125, 147-149), `…/3_requirements/app/A03_point.md:48-102`, `…/app/B05_dr.md:8, 32-34`, `…/app/D03_push.md:5, 7, 29-31, 81-83`, `…/app/README.md:64`, `…/4_spec/admin/G_energy_advice.md:18-19, 28-29, 47` (`…` = `eminel_gw_project/docs/eminel`) |
| Số đếm §2 | tự đếm `syp-eminelstandard-backend`@`dc39aa39`: 105 thư mục `syp-eminelstandard-backend/src/functions/`, 81 `batch-*`, 3 `Type: ScheduleV2` trong `syp-eminelstandard-backend/template.yaml` (template-api/dynamodb: 0) |

| Mức | Nội dung |
|---|---|
| ✅ 確実 | mọi khẳng định e-smart có/không (soi code); hành vi 4 batch cũ; cron :84-102 (15 mùa + 4 thông năm id 1/2/3/19); Node.js 24; lịch DR 2 tầng; các `TABLE_*`; số dòng B05/D03 theo `fbc0af0`; số đếm 105/81/3 |
| ⚠️ *推定* | (1) PushCore→FCM (code không trong repo); (2) 「照明アドバイス」= lỗi ghi 省エネアドバイス; (3) 🔸 viết thêm vào codebase e-smart (suy từ QA 管理画面, chưa thành văn) |
| ❓ Chưa xác minh | (1) 3 QA Notion 回答中 (08-04, qua ảnh — trích lại phải mở gốc); (2) D03/B05 状態 file vs slide; (3) điểm/ngưỡng/mùa E-GW (A03 要確認); (4) cờ nhận push hệ cũ; (5) kết cục CLD-05/06 |
Commit: điều tra tại `788b438`, 08-06 đối chiếu `fbc0af0` (6 commit chỉ sửa `eminel_gw_project/docs/eminel/3_requirements/app/` 13 file + 1 dòng skill) — B05/D03 cập nhật số dòng, **kết luận không đổi**; app snapshot nên số dòng app có thể trôi.
**Lệch tài liệu ESTA ↔ code** (file: `eminel_gw_project/docs/eminel-smart/02_product_overview.md`; 3/6 điểm thuộc nhóm; 3 điểm kia: nhịp import 基幹 mỗi-giờ + lock 5分 → tập 外部連携・受信系; `CsvDownloadHistory` → tập 外部連携・受信系 + CSV・ZIP):

| Tài liệu ghi | Code thực tế |
|---|---|
| Push 「最大500件/バッチ」 (:121) | không có số 500 (đó là phân trang hệ CŨ); lô 10 000, 100 song song ([§6.3](#s6-3)) |
| 「自動化ルール実行（毎分）」 (:85) | không mỗi phút — mỗi rule 1 lịch tuần động ([§7](#s7)) |
| Node.js 20.x (:49) | `nodejs24.x` (`syp-eminelstandard-backend/template.yaml:181`; layer CompatibleRuntimes vẫn 20.x — :3163) |
