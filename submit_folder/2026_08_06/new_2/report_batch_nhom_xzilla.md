# Báo cáo điều tra: nhóm 外部連携・受信系（Xzilla取込） (3 batch #5–#7) — có cần port sang hệ mới không?
| | |
|---|---|
| Đối tượng | 3 batch trong `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` (đều thuộc `conciergesv`): #5 `RcvCntctCancellationCommand` (IF2249) ・ #6 `RcvEmsPlsCntrPayerCommand` (IF2264) ・ #7 `RcvHalfHourElectricPowerCommand` (IF1156) |
| Phạm vi đối chiếu | `legacy_eminel_docs`@`ccd8f56` ・ `eminel_gw_project`@`fbc0af0` (điều tra tại `788b438` — không ảnh hưởng nhóm này, §11) ・ `syp-eminelstandard-backend`@`dc39aa39` ・ `syp-eminelstandard-web-admin`@`e550326` (2 repo sau: branch `gw-syp-dev`) — đều = origin 2026-08-06 |
| Ngày / người lập | Điều tra 2026-08-04 ・ lập 2026-08-06 ・ Bui Trong Dat (SYP) + AI hỗ trợ |
| Phân tập | 11 batch = 3 tập theo 3 task Notion; số #1–#11 xuyên suốt; 2 tập kia: 配信・通知系 (#1–#4)・CSV・ZIPエクスポート系 (#8–#11); bản JP cùng thư mục: `旧EMINELバッチ移行判定報告書_外部連携・受信系（Xzilla取込）3本.md` (khớp 1-1) |

| Mã | Nghĩa |
|---|---|
| 確実 / *推定* / 🔸 | kiểm chứng trên code/tài liệu / suy đoán có căn cứ, chưa chốt / giả thuyết chưa kiểm chứng (= ※推定（未確認） bản JP) |
| 🔍 + path | grep X: 0 hit = tìm toàn backend không ra; `...` = ký hiệu lược code; mọi path ghi đầy đủ từ tên repo (gốc `sources/`); trong sơ đồ được rút `file:dòng` — path đầy đủ ở dòng 🔍 kèm ngay cạnh |
| e-smart | = ESTA = EMINEL-Smart; `hemssv` (hệ cũ) ≠ HEMS-SV (m2-cloud, mui làm mới) |
| IF-01 | kênh liên kết MỚI E-GW⇔Xzilla — dòng 1 IF一覧 統合要件 v1.2 §4-1, qua 北ガスクラウド, chưa chốt (≠ IF 4 số hệ cũ) |
| CLD-07 / SVC-03 ・ F-ES-10 / F-ES-01 | vấn đề mở: vào/ra + 認証 IF-01 (~10 mục) / lưu trữ + backup chưa định nghĩa ・ mã chức năng server 統合要件 v1.2: Xzilla連携 / グラフ |
| 回答中 | QA Notion chưa chốt (tham chiếu 2026-08-04 — mở trang gốc trước khi trích lại) |

**Mục lục**: KẾT LUẬN ・ I: §1 Vì sao ・ §2 Chỗ xử lý ・ §3 Cần xác nhận ・ §4 Dễ hiểu sai ・ §5 Việc tiếp theo ・ II: §6 Từng batch ・ §7 Luồng chung ・ §8 Đối chiếu dữ liệu ・ §9 Phương án ・ §10 QA ・ §11 Căn cứ
## KẾT LUẬN
> **#5 `RcvCntctCancellationCommand` (nhận hủy hợp đồng điện, IF2249): BỎ BATCH — GIỮ NGHIỆP VỤ.** Cờ "dừng tính 買電売電" (điện mua vào/bán ra) vẫn bắt buộc (#7 cần) → gộp vào luồng nhận Xzilla sẵn có của e-smart, không dựng batch riêng. (*推定*)
>
> **#6 `RcvEmsPlsCntrPayerCommand` (nhận master người trả tiền, IF2264): BỎ BATCH — GIỮ DỮ LIỆU + TRI THỨC.** Dữ liệu payer nhận qua 3 kênh hợp đồng đang chạy hằng ngày (IF2023/IF2024/DM1040); spec 契約終了判定 3 điều kiện trích ra giữ. (*推定*)
>
> **#7 `RcvHalfHourElectricPowerCommand` (nhận điện 30 phút, IF1156): TẠO MỚI** theo pattern import e-smart — yêu cầu minh văn scope 2026; nặng nghiệp vụ nhất trong 11 batch. (確実)
>
> Có **4 điểm cần xác nhận trước khi chốt** (→ §3): IF-01/CLD-07 ・ luồng 解約 trong IF-01 ・ nhịp cấp 30分値 ・ đích SFTP `/EST`.

*(Nhãn chứng phần dữ kiện; đề xuất là phán đoán để review. Chưa ước công số — 1 batch = 1 task Notion khi tách, §5.)*

## PHẦN I — BÁO CÁO
### §1 Vì sao kết luận như vậy
| | Hệ cũ (`conciergesv`) | Hệ mới (e-smart / E-GW) |
|---|---|---|
| Nhận Xzilla | CSV qua SFTP vào 中間サーバ, cron 5–10 phút/lượt | SFTP → S3 → DynamoDB, mỗi giờ 0–7h JST — 8 kênh IF đang chạy (§7.3) |
| Stack | PHP 8.0 / CakePHP 4.4 + PostgreSQL | TypeScript / Lambda (Node.js 24) + DynamoDB; Step Functions + EventBridge Scheduler |
| 3 IF nhóm này | IF2249・IF2264・IF1156 chạy ổn định | KHÔNG tồn tại (grep 0 hit — §7.5); nền nhận + hậu xử lý có sẵn |
| Kênh thay thế | — | IF-01 — chưa chốt (CLD-07) |

| Xử lý cốt lõi (hệ cũ) | Còn cần? |
|---|---|
| Nhận SFTP mỗi 5–10 phút (cả 3) | ❌ kiến trúc — "gần real-time" là sản phẩm cron cũ; dùng cửa sổ 0–7h sẵn có (riêng 30分値: §3-3) |
| #5 Lọc 契約種別 PE624/625 | ✅ giữ làm điều kiện lọc loại file mới trong IF-01 (§6.1 bước 2, 4) |
| #5 Bật cờ dừng tính (`t_101.c065=1`) | ✅ GIỮ — thành hậu xử lý ④; #7 đọc khi tính (§6.1 bước 3) |
| #6 5 phút xóa-toàn-bộ-nạp-lại (memory_limit 4096M) | ❌ — điển hình 「いけてない」; thay bằng cập nhật theo chuyến file qua 3 kênh sẵn có |
| #6 Chỉ nạp 契約種別 đối tượng (PE624/625/650/651/652・PG077/079) + dữ liệu payer | ✅ — cần cho グルーピング (必須 2026); nhận qua IF2023/IF2024/DM1040, mở rộng theo IF-01 nếu thiếu (§6.2 bước 2) |
| #6 契約終了判定 3 điều kiện | ✅ GIỮ — trích comment code thành 1 trang spec (§6.2 bước 1, làm ngay được) |
| #7 Nhận 30分値, tách 速報 (đổ đè) / 確報 (tích lũy) | ✅ — 2 bảng DynamoDB mới đúng theo cách tách này (§6.3 bước 3) |
| #7 Gộp 2×30分→1時間 + bảng điều kiện 買電/売電 theo cấu hình nhà | ✅ GIỮ LOGIC (không port PHP) — map lại theo 9 pattern lắp đặt E-GW (§6.3 bước 4) |
### §2 Hệ mới xử lý ở đâu
| Việc | Nơi thực hiện | Loại |
|---|---|---|
| Nhận file Xzilla | `syp-eminelstandard-backend/src/functions/batch-get-list-file-name-from-sftp-server/` → `syp-eminelstandard-backend/src/functions/batch-forward-csv-from-sftp-server-to-s3/` → 8 handler `batch-ifXXXX-import-*` | SẴN CÓ (`syp-eminelstandard-backend/src/statemachine/batch_run_sequentially.asl.json`, 0–7h — §7.3) |
| #5 解約 + cờ dừng tính | +1 loại file vào luồng trên + hậu xử lý thứ 4 (④) cạnh 3 hậu xử lý hiện có | CHƯA CÓ — theo pattern sẵn có (chờ IF-01) |
| #6 dữ liệu payer | `syp-eminelstandard-backend/src/functions/batch-if2023-import-contract-info/`・`syp-eminelstandard-backend/src/functions/batch-if2024-import-user-info/`・`syp-eminelstandard-backend/src/functions/batch-dm1040-import-user-contract-list/` (lọc 支払者: `syp-eminelstandard-backend/src/functions/batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63`) | SẴN CÓ — chỉ mở rộng trường (chờ IF-01) |
| #6 契約終了判定 | hậu xử lý mới áp spec trích từ code cũ | CHƯA CÓ |
| #7 30分値 + tính 買電売電 | handler mới + cặp bảng 速報/確報 mới (`syp-eminelstandard-backend/template-dynamodb.yaml`) + Lambda tính | CHƯA CÓ — nặng nhất nhóm |
| Chiều gửi → 基幹 | `upload-data-backup-to-sftp.ts` → `/EST` (6 CSV thiết bị, 8:00) | SẴN CÓ (đích 🔸 — §3-4) |

- Sơ đồ luồng đầy đủ: §7.3. Tư tưởng: cũ = cron dày; mới = 3 lịch tĩnh + one-shot động, **không polling mỗi phút** (grep `rate(`: 0 hit — §7.1).
### §3 Cần xác nhận trước khi chốt
| # | Điểm treo | Hệ cũ | Hệ mới / kế hoạch | Mức |
|---|---|---|---|---|
| 1 | Vào/ra + 認証 của IF-01 (CLD-07, gồm chiều xuất 「EMINELデータの共有」) | 3 IF ổn định | chưa chốt — cả 3 batch phụ thuộc | 🔴 |
| 2 | IF-01 có luồng 解約 không | IF2249 cấp CSV mỗi 5 phút | chưa biết — không có thì phải nêu yêu cầu NGAY | 🔴 |
| 3 | Nhịp cấp 30分値 | 10 phút/lượt | e-smart chỉ quen 0–7h — "gần real-time" là yêu cầu MỚI với 北ガス | 🔴 |
| 4 | Đích SFTP `/EST` | (không có chiều gửi) | 6 CSV/ngày 8:00; 🔸 nghi Xzilla/DWH, địa chỉ trong secret | 🟡 |

**Câu chữ soạn sẵn**:
> **Hỏi mui (QAデータベース) — #4**:
> 「e-smart が毎日 8:00 に機器データ CSV 6種（給湯器系5種＋赤外線リモコン）を SFTP の `/EST` フォルダへアップロードしていますが（`upload-data-backup-to-sftp.ts`）、この宛先は Xzilla もしくは DWH（分析用データ基盤）という理解で合っていますか。接続先が secret 管理のためコードから確認できず、ご確認をお願いしたいです。該当する場合、F-ES-10「EMINELデータの共有」の既存実装として扱いたいと考えています。」

> **Hỏi khách qua PM mui — #2・#3** (gửi cùng đợt thảo luận CLD-07):
> 「新アーキテクチャの IF-01（北ガスクラウドAPI — Xzillaデータ連携）について2点ご相談です。①電力契約の解約情報のデータフローは IF-01 に含まれますか（旧 IF2249 相当 — 解約時の買電売電計算停止に必要）。②電力30分値の提供周期はどの程度を想定できますか（旧システムは10分毎。準リアルタイム提供は新規要素のため、可否を確認したいです）。」

### §4 Dễ hiểu sai
| Hiểu sai | Đúng |
|---|---|
| Bỏ #5/#6 = mất nghiệp vụ/dữ liệu | chỉ bỏ code PHP + batch 5 phút; cờ dừng tính (#5), dữ liệu + spec 契約終了判定 (#6) đều giữ, chạy trên luồng sẵn có |
| IF-01 là một IF 4 số cũ | IF-01 = dòng 1 IF一覧 kiến trúc MỚI (統合要件 v1.2 §4-1), chưa chốt (CLD-07) |
| "Dùng lại e-smart" = 0 công | QA độc lập deploy 回答中 (*cơ bản hệ độc lập*) → vẫn phải dựng lại môi trường chạy |
| Task Xzilla = 3 batch nhận | phải thêm chiều GỬI `/EST` (đã có 1 luồng chạy hằng ngày — §7.6) |
### §5 Việc tiếp theo
| # | Nội dung | Phụ trách |
|---|---|---|
| 1 | Bám CLD-07/IF-01; trong lúc chờ làm ngay: trích spec 契約終了判定 (§6.2 bước 1) + bảng đối chiếu 4 trường payer (§6.2 bước 2) | SYP |
| 2 | Gửi câu hỏi `/EST` (§3) | SYP → QAデータベース |
| 3 | Gửi câu hỏi IF-01: luồng 解約 + nhịp 30分値 (§3) | SYP → PM mui → 北ガス |
| 4 | Góp 「既存システムを使い続けたほうがいい機能」 vào QA 独立デプロイ: ứng viên nhóm này = luồng nhận Xzilla SFTP→S3→DynamoDB (trả lời 2 vế, chung 3 tập: ①hệ cũ — không có ・ ②e-smart — 4 ứng viên) | SYP → Notion |

> **Phương châm** (合宿 Day3 — 「バッチ群…作り直す前提」, 1 batch = 1 task): kênh nhận mới cắm vào luồng SFTP→S3→DynamoDB sẵn có; chỉ nhịp dày hơn 0–7h (duy nhất 30分値) mới khai lịch riêng (§9).

## PHẦN II — CHI TIẾT KỸ THUẬT
### §6 Từng batch
#### §6.1 #5 `RcvCntctCancellationCommand` — nhận 解約 điện (IF2249)
**Mục đích**: đồng bộ hủy hợp đồng điện từ Xzilla — lưu thông tin hủy + ngừng tính 買電売電 cho khách đã hủy + gọi 顧客情報登録完了通知API khi đủ dữ liệu ngày.

**Phán định** (*推定*): **BỎ BATCH — GIỮ NGHIỆP VỤ** — bỏ code PHP + kiến trúc batch 5 phút; giữ nghiệp vụ bật cờ dừng tính; thực hiện = +1 loại file +1 hậu xử lý trên luồng sẵn có; flow thủ công (vô hiệu GW trên 管理画面) không cover dừng tính. ・ *Vì sao*: IF2249 không tồn tại (grep 0 hit — §7.5) nhưng nền nhận 8 IF + chỗ đặt hậu xử lý có sẵn; phương châm làm lại (§7.1); cờ là tiền đề của #7.

**Flow cũ** (確実) — cron `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:107-108`, nhịp 5 phút ・ 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php:30, 99-113, 193-217, 242-243, 306-334`:
```
cron */5' ──▶ SFTP CSV 解約 hôm nay → lọc 契約種別 PE624/625 (:242-243) → upsert ipf_cntct_cancellations
          → bật cờ t_101.c065=1 (:306-334) → nếu IF2264 hôm nay đã nhập xong → gọi 顧客情報登録完了通知API (:193-217)
```
Trích code (điều kiện lọc) — 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php:242-245`:
```php
// 契約種別が'PE624'または'PE625'以外は、登録しない
if ($line[58] != 'PE624' && $line[58] != 'PE625') {
    continue;
}
```
**Hệ mới / E-GW**: e-smart không có IF2249 (確実); E-GW không yêu cầu luồng 解約 tự động — vô hiệu GW sau 解約 = thao tác thủ công trên 管理画面; IF-01 treo (CLD-07). 🔍 `eminel_gw_project/docs/eminel/1_product/11_business_process/readme.md:938-941, 945-952` ・ `eminel_gw_project/docs/eminel/2_management/20_open_issues.md:181-182`

**Flow mới + bước**:
```
IF-01 (chờ CLD-07) ──▶ luồng nhận sẵn có (§7.3) +1 loại file ──▶ handler mới ──▶ bảng 解約 mới
                    └▶ hậu xử lý ④: bật cờ dừng tính trên bảng hộ ──▶ #7 đọc khi tính 買電売電
```
Cũ: batch riêng 5 phút → `ipf_cntct_cancellations` + cờ `t_101.c065` ↔ Mới: +1 loại file trên luồng 8 IF sẵn có → bảng 解約 mới + cờ trên bảng hộ (hậu xử lý thứ 4 ④).
1. Khi CLD-07/IF-01 định hình: xác nhận có luồng 解約 không; **không có → nêu yêu cầu bổ sung ngay** (CLD-07/QAデータベース). — *Vì sao*: thiếu thì không ai bật cờ, #7 tính sai khách đã hủy.
2. Có luồng: thêm 1 IF vào luồng sẵn có, KHÔNG dựng batch 5 phút — sửa `syp-eminelstandard-backend/src/functions/batch-get-list-file-name-from-sftp-server/app.ts` (`DEFAULT_FOLDER_CSV`/`DEFAULT_FILE_NAME_METADATA`) + `syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts` (`LIST_COL_*`) + interface `syp-eminelstandard-backend/src/layers/common/nodejs/interfaces/` (mẫu `syp-eminelstandard-backend/src/layers/common/nodejs/interfaces/IDataIF2016.ts`) + `syp-eminelstandard-backend/src/statemachine/batch_run_sequentially.asl.json` (thêm nhánh Map) + handler mới theo mẫu `syp-eminelstandard-backend/src/functions/batch-if2016-import-service-point-no/`. — *Vì sao*: thừa hưởng chống tải trùng/chống chồng/chia gói 50 000 dòng.
3. Cờ dừng tính = **hậu xử lý ④** cạnh 3 hậu xử lý hiện có (`syp-eminelstandard-backend/src/functions/batch-send-contents-to-updated-user/`・`syp-eminelstandard-backend/src/functions/batch-update-selecting-place-no/`・`syp-eminelstandard-backend/src/functions/batch-remove-integration-expired/`). — *Vì sao*: đúng chỗ chuẩn nghiệp vụ phái sinh sau import; nhịp 0–7h đủ (*推定* — QA A-4).
4. Kiểm thử: CSV giả ± PE624/625; xác nhận cờ phản ánh vào tính 買電売電 của #7. — *Vì sao*: 2 rủi ro = lọc sai loại + cờ không truyền tới #7.
#### §6.2 #6 `RcvEmsPlsCntrPayerCommand` — nhận master 支払者 (IF2264)
**Mục đích**: giữ bản sao master 支払者 khớp với 基幹 + áp 契約終了判定 để cập nhật số liên kết/cờ dừng tính.

**Phán định** (*推定*): **BỎ BATCH — GIỮ DỮ LIỆU + TRI THỨC** — bỏ kiểu "5 phút xóa hết nạp lại"; dữ liệu payer nhận qua IF2023/IF2024/DM1040 sẵn có (mở rộng theo IF-01 nếu thiếu — bước 2); 契約終了判定 3 điều kiện trích thành spec (bước 1); nhịp 0–7h đủ (*推定* — QA A-4). ・ *Vì sao*: IF2264 không tồn tại (grep 0 hit — §7.5) nhưng 3 kênh hợp đồng đã nhận hằng ngày (DM1040 lọc sẵn 支払者); full-reload 4096M là điển hình 「いけてない」 (§7.1); E-GW không yêu cầu "payer" riêng — nhu cầu thật = グルーピング; spec chỉ nằm trong comment code sắp bỏ.

**Flow cũ** (確実) — cron `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:105-106`, nhịp 5 phút, memory_limit 4096M (:63) ・ 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php:63, 170-177, 245-363, 371-626`:
```
cron */5' ──▶ DELETE toàn bộ ipf_ems_pls_cntr_payers (:170-177) → nạp lại CSV, chỉ 契約種別 PE624/625/650/651/652・PG077/079 (:319-329)
          → áp 契約終了判定 3 điều kiện (comment :373-385) → cập nhật t_101 (số liên kết + cờ dừng tính)
```
Trích comment spec (= "1 trang spec" của bước 1) — 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php:373-385`:
```php
/*
 * ＜契約終了判定の仕様について＞
 * 契約終了を判定するポイントは以下の３つ
 * 　① サービスポイント＿適用終了年月日が99991231以外
 * 　② 契約終了年月日が99991231以外
 * 　③ 契約種別が電気（PE624またはPE625）の場合に供給地点特定番号またはIPF使用契約番号がNULL
 * ...
 */
```
(`99991231` = trị "chưa có ngày kết thúc"; dòng 380–384 lược bằng `...`.)

**Hệ mới / E-GW**: e-smart không có IF2264 (確実), đã import 契約/顧客 qua IF2023/2024/DM1040 (§7.4); E-GW không có chức năng payer riêng (đã grep docs/eminel) — gần nhất F-ES-10 phần 顧客情報・契約情報取得; グルーピング cần 建物種別 (lấy từ Xzilla — :619) + 料金メニュー/アンペア数. 🔍 `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:415, 619, 692-696`

**Flow mới + bước**:
```
IF2023/IF2024/DM1040 (đang chạy) ──▶ TABLE_KAIIN・TABLE_IF2023_USE_CNTR_INFO・TABLE_IF2024_CUSTOMER_INFO
   + mở rộng trường theo IF-01 (nếu thiếu 4 trường payer) ──▶ hậu xử lý mới: áp spec 契約終了判定
```
Cũ: 5 phút full-reload → `ipf_ems_pls_cntr_payers` (1 bảng riêng) ↔ Mới: 0 bảng riêng — 3 kênh sẵn có → `TABLE_KAIIN`・`TABLE_IF2023_USE_CNTR_INFO`・`TABLE_IF2024_CUSTOMER_INFO` + hậu xử lý áp spec.
1. **Trích spec 契約終了判定 3 điều kiện** từ comment (`legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php:373-385`) — làm ngay, không chờ IF-01. — *Vì sao*: không trích thì mất theo code; việc duy nhất của #6 không phụ thuộc IF-01.
2. Khi IF-01 định hình: đối chiếu 4 trường payer (供給地点特定番号・IPF使用契約番号・受電地点特定番号・お客様番号) với IF2023 (`syp-eminelstandard-backend/src/functions/batch-if2023-import-contract-info/`)・IF2024 (`syp-eminelstandard-backend/src/functions/batch-if2024-import-user-info/`)・DM1040 (`syp-eminelstandard-backend/src/functions/batch-dm1040-import-user-contract-list/`; lọc 支払者: `syp-eminelstandard-backend/src/functions/batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63`); thiếu mới xin bổ sung IF-01, không xin kênh payer riêng. — *Vì sao*: thu hẹp tối đa phạm vi đàm phán IF-01.
3. Implement phần thiếu = mở rộng handler hiện có (`syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts` cột + interface + handler); áp spec (bước 1) làm hậu xử lý sau import. — *Vì sao*: cập nhật theo chuyến file, không lặp lại full-reload 4096M.
4. Kiểm thử: 3 điều kiện × thỏa/không thỏa; so cờ/số liên kết với chạy tay logic cũ. — *Vì sao*: chỉ đối chiếu logic cũ mới chứng minh spec trích không méo.
#### §6.3 #7 `RcvHalfHourElectricPowerCommand` — nhận 電力30分値 (IF1156)
**Mục đích**: nhập 電力30分値 từ Xzilla, tính 買電/売電 theo giờ từng hộ — nguồn nuôi biểu đồ/レポート; quan trọng + nặng nhất nhóm.

**Phán định** (確実 — yêu cầu minh văn + e-smart chắc chắn không có): **TẠO MỚI** — nặng nghiệp vụ nhất trong 11 batch. ・ *Vì sao*: yêu cầu minh văn scope 2026 「電力30分値はCルート（Xzilla経由）で取得する」; e-smart không có đường Xzilla 30分値 (grep 0 hit — §7.5), điện/gas đi TagTag API; code PHP không chạy trên Lambda/TypeScript — chỉ kế thừa logic.

**Flow cũ** (確実) — cron `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:109-110`, nhịp 10 phút ・ 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php:107-122, 192-233, 449-583, 591-725, 734-1050` (rẽ nhánh 875–893):
```
cron */10' ──▶ 速報値: xóa-nạp lại emn_all/emn_fast_electric_powers (:449-583) ・ 確報値 (fixed_div=1): ghi bổ sung emn_confirm_electric_powers (:591-725)
           → gộp 2×30分→1時間値, rẽ nhánh theo cấu hình nhà (:875-893) → ghi s_102 → đồ thị/report
```
Trích code (rẽ nhánh 売電) — 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php:875-882`:
```php
// 【売電量算出条件①】GWからの計測データによる売電量算出条件
$calcFromGw = $record['has_solar_cell'] == 1;
// 【売電量算出条件②】Xzillaからの30分電力量データによる売電量算出条件
$calcFromXzilla = (
    $record['has_solar_cell'] != 1 &&
    $record['gas_cogeneration'] == 1 &&
    !empty($record['juden_point_number'])
);
```
Rẽ nhánh: 太陽光 → 売電 từ số liệu GW (batch tích lũy ngày đảm nhận — ngoài nhóm); コージェネ + 受電地点特定番号 → từ số liệu Xzilla.

**Hệ mới / E-GW**: e-smart không có (確実 — grep 0 hit), điện/gas qua TagTag API (`eminel_gw_project/docs/eminel-smart/02_product_overview.md:119`); E-GW cần minh văn 2026 (統合要件 mục 3-2), F-ES-10 định nghĩa 速報値・確報値, nuôi グラフ (F-ES-01)/グルーピング・レポート, hàng 「連携テスト(Xzilla/TagTag)」 không ✅ = 今期. 🔍 `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:84, 692-696` ・ `eminel_gw_project/docs/eminel/1_product/10_feature_list.md:148`

**Flow mới + bước**:
```
IF-01 30分値 (bước 1) ──▶ SFTP→S3→handler mới (bước 2; ScheduleV2 riêng nếu nhịp cao — §9) ──▶ bảng 速報/確報 mới (bước 3)
   ──▶ Lambda tính: 2×30分→1時間 + điều kiện 買電/売電 map 9 pattern (bước 4) + cờ #5 ──▶ nhóm batch 集計 (bước 5)
```
Cũ: 10 phút/lượt → 速報 2 bảng (`emn_all`/`emn_fast_electric_powers`) + 確報 1 bảng (`emn_confirm_electric_powers`) → `s_102` ↔ Mới: 2 bảng 速報/確報 mới → Lambda tính (map 9 pattern) → nhóm batch 集計.
1. Chốt IF-01 phần 30分値: format file, nhịp cấp (cũ: 10 phút), 認証 (CLD-07). — *Vì sao*: bước 2–3 đổ theo 3 tham số; nhịp gắt nhất, cần 北ガス đồng ý (§3).
2. Dựng đường nhận theo §7.3: `syp-eminelstandard-backend/src/functions/batch-get-list-file-name-from-sftp-server/` → `syp-eminelstandard-backend/src/functions/batch-forward-csv-from-sftp-server-to-s3/` → handler mới; nhịp > 0–7h → `ScheduleV2` riêng trong `syp-eminelstandard-backend/template.yaml`, KHÔNG nhét `BatchRunSequentially` (§9). — *Vì sao*: chuỗi 8 IF tuần tự có khóa — luồng nhịp cao làm nghẽn; lịch riêng cô lập sự cố.
3. Bảng DynamoDB mới (`syp-eminelstandard-backend/template-dynamodb.yaml`): tách 速報 (đổ đè) / 確報 (tích lũy) — tương đương `emn_fast`/`emn_confirm_electric_powers`; TTL theo 保持期間 (SVC-03). — *Vì sao*: 2 tính chất ngược nhau; hệ cũ cũng tách vì vậy (:449-583 / :591-725).
4. Kế thừa logic (KHÔNG port PHP): gộp 2×30分→1時間値 + bảng điều kiện 買電/売電 (:875-893), **map lại theo 9 pattern lắp đặt E-GW** (統合要件 v1.2 mục 3-5). — *Vì sao*: logic đã chạy thương mại nhiều năm; tổ hợp thiết bị E-GW khác → có thể thêm nhánh.
5. Nối đầu ra sang nhóm batch 集計 + áp cờ dừng tính từ #5 (§6.1). — *Vì sao*: #7 chỉ là cửa nhập; cờ phải áp ngay tại bước tính.
6. Kiểm thử: dữ liệu giả phủ các nhánh (太陽光/コージェネ/thường, 速報→確報 ghi đè, thiếu cặp 30 phút); đối chiếu kết quả giờ với chạy tay logic cũ. — *Vì sao*: nhánh cấu hình nhà là phần phức tạp nhất (:734-1050).
### §7 Luồng/hạ tầng chung
#### §7.1 Nền batch + tiền đề
- Phương châm 合宿 Day3 (2026-06-25): batch hiện hành 「いけてない」 → làm lại không bê nguyên, 1 batch = 1 task, バッチボーン trước 結合フェーズ (tháng 9); "dùng lại" = dùng cơ chế/codebase e-smart. 🔍 `eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:35, 51, 99-103, 147-149`
- QA độc lập deploy (swan (mui), 回答中): *cơ bản hệ độc lập* → dùng lại ≠ 0 công (§4).
- Chưa có commit E-GW trên `gw-syp-dev` (web-admin: `git log origin/main..gw-syp-dev` rỗng; backend: 15 commit gần nhất thuần e-smart). *推定*: viết thêm vào codebase e-smart — suy từ QA 管理画面 (masao takahashi (mui), 回答中 — trả lời tạm: hướng chung source), chưa thành văn; "chung source" ≠ "chung môi trường chạy".
- 3 lịch tĩnh (`ScheduleV2`, `Asia/Tokyo` — `syp-eminelstandard-backend/template.yaml:9-11`): ① `BatchRunSequentiallyStateMachine`, `cron(5 0-7 * * ? *)` = :05 mỗi giờ 0–7h JST (`syp-eminelstandard-backend/template.yaml:853-888`, cron 881–882) — luồng nhận nhóm này; ② `BatchMigrationIntegratedDataStateMachine`, `cron(0 8 * * ?)` (`syp-eminelstandard-backend/template.yaml:2205-2240`, cron 2233) — chiều `/EST`; ③ `BatchGetErrorDeviceInfoOfRinnaiStateMachine`, 8:00 (`syp-eminelstandard-backend/template.yaml:2966-2980`). Còn lại: lịch tạo động EventBridge Scheduler, đa số one-shot (`syp-eminelstandard-backend/src/layers/common/nodejs/services/put-schedule.ts:18-33`); ngoại lệ automation rule — lịch tuần/rule, không tự xóa (`syp-eminelstandard-backend/src/functions/api-automation/common.ts:115, 167-175`); **không polling mỗi phút** (grep `rate(`: 0 hit).
- Scope 6/10 (決定ログ): 必須 = 暖房機能/暖房制御/照明アドバイス※/ポイント連携/グルーピング・レポート; 劣後 (→2027/4~) = 複合制御・DR・ダッシュボード・バッジ (※nghi 誤記 của 省エネアドバイス — *推定*; 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md:30-31`) ・ Phạm vi SYP (QA 調査範囲, swan (mui), 回答中): `conciergesv`/`eminelsv` = đối tượng điều tra, không phát triển tiếp; GW đi qua HEMS-SV (m2-cloud), spec chia sẻ sau (B-2, §10).
#### §7.2 Luồng nhận hệ cũ
🔍 `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:1-37` (flock trong `.sh` thuộc `eminel-mng-webap.20240909.tgz` cùng thư mục):
```
Xzilla ──SFTP (5–10 phút/lượt)──▶ [đĩa 中間サーバ] ──▶ 3 PHP Command (cron + flock) ──▶ [PostgreSQL]
                                                        · RcvCntctCancellation…  ──▶ ipf_cntct_cancellations + cờ t_101.c065
                                                        · RcvEmsPlsCntrPayer…    ──▶ ipf_ems_pls_cntr_payers + t_101
                                                        · RcvHalfHourElectric…   ──▶ emn_all/emn_fast/emn_confirm + s_102
```
Cũ: SFTP → đĩa 中間サーバ → 3 PHP Command (cron 5–10 phút + flock) → PostgreSQL ↔ Mới: SFTP → S3 → 8 handler Lambda → DynamoDB, cửa sổ 0–7h, chống trùng asl (5–38) + `CsvDownloadHistory` (§7.3).
#### §7.3 Luồng nhận e-smart (確実)
```
Xzilla ──SFTP──▶ [SFTP server: 8 thư mục IF + END/*.dat]     (.dat = danh sách file đã chốt của "chuyến hàng")
                   │
                   │ ① batch-get-list-file-name-from-sftp-server/
                   │    · đọc .dat lấy danh sách file (app.ts:52-66)
                   │    · chống tải trùng: bảng CsvDownloadHistory (app.ts:69-87)
                   ▼
                 [S3] file chia gói 50 000 dòng               ② batch-forward-csv-from-sftp-server-to-s3/ (app.ts:56-64)
                   ▼
                 ③ 8 handler batch-ifXXXX-import-* ──ghi transaction──▶ [DynamoDB]
                   ·  IF2241 → DM1040 → IF2242 (TUẦN TỰ)  ──────────▶ TABLE_KAIIN (bảng hội viên)
                   ·  IF2016/2023/2024/2029/2223 (SONG SONG) ───────▶ bảng riêng từng kênh (TABLE_IF2016_SERVICE_POINT_NO_INFO…)
                   ▼
                 ④ 3 hậu xử lý ①②③ (nghiệp vụ phái sinh sau import)
  ⏰ Lịch: cron(5 0-7 * * ? *) = phút :05 mỗi giờ 0–7h JST — state machine batch_run_sequentially.asl.json
```
Mới ↔ Cũ: S3 thay đĩa 中間サーバ; 8 handler + 3 hậu xử lý thay PHP Command lẻ; khối asl (5–38) + `CsvDownloadHistory` thay flock; cửa sổ 0–7h thay cron 5–10 phút.
- Điều phối `syp-eminelstandard-backend/src/statemachine/batch_run_sequentially.asl.json`: chống chạy chồng (5–38) → dọn temp → list → 8 forward song song → import → 3 hậu xử lý; danh mục 8 thư mục IF trong code — 🔍 `syp-eminelstandard-backend/src/functions/batch-get-list-file-name-from-sftp-server/app.ts:149-169`; đọc `.dat` (52–66); chống tải trùng `CsvDownloadHistory` (69–87 — vai trò thật: bảng lệch §11); chia gói 50 000 dòng lên S3 — 🔍 `syp-eminelstandard-backend/src/functions/batch-forward-csv-from-sftp-server-to-s3/app.ts:56-64`.
- Điểm đến: IF2241/IF2242/DM1040 → `TABLE_KAIIN` (nên phải tuần tự); 5 kênh còn lại bảng riêng, song song (asl 493–794) — chi tiết từng IF: §7.4.
- Lock 5 phút khi merge hội viên "fake" (`UPDATE_LOCK_TTL_MINUTES = 5`, ghi `TABLE_KAIIN_UPDATING`, TTL tự hết hạn — 🔍 `syp-eminelstandard-backend/src/functions/batch-if2241-import-tagtag-kaiin/app.ts:69, 102-111`); 39 API handler kiểm qua `syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/check-kaiin-updating.ts:10-15`.
- 3 hậu xử lý: ① phát lại nội dung cho hội viên mới (`syp-eminelstandard-backend/src/functions/batch-send-contents-to-updated-user/app.ts:79-132`); ② đổi nơi-ở-đang-chọn + badge 「ゆーぬっく」 (YUNUKKU, `PG003`, 「ゆーぬっく２４ネオ」 `syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts:1065`; `syp-eminelstandard-backend/src/functions/batch-update-selecting-place-no/app.ts:89-143, 283-296` + `syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts:1909`; thao tác `TABLE_KAIIN`+`TABLE_IF2023_USE_CNTR_INFO`); ③ xóa liên kết/thiết bị khi hết hợp đồng gas (`syp-eminelstandard-backend/src/functions/batch-remove-integration-expired/app.ts:44-79` — đọc `TABLE_IF2023_USE_CNTR_INFO`, xóa `TABLE_KAIIN`/`TABLE_MUI_DEVICE`/`TABLE_MUI_SENSOR`).
#### §7.4 Bảng chi tiết 8 kênh IF
Trường từ enum `LIST_COL_*` (`syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts:468-565`, interface `syp-eminelstandard-backend/src/layers/common/nodejs/interfaces/IData*.ts` — nguồn 一次); nguồn 基幹 theo `eminel_gw_project/docs/eminel-smart/02_product_overview.md:68-75` (đối chiếu `eminel_gw_project/docs/eminel-smart/03_backend_models.md:90-97`; vênh thì theo code — §11); "x/y cột" = trích x trong y cột code dùng:

| IF | Nguồn 基幹 | Trường chính (code) | Bảng đích | Tác dụng |
|---|---|---|---|---|
| IF2241 | `TAG_KAIIN` | 5/11: `kaiinBango` (khóa), `custShikibetsuBango`, `status`, `loginId`, `yubinBango` | `TABLE_KAIIN` (tài liệu: 「KaiinTable + 16関連」 :73) | xương sống danh tính hội viên — merge app ↔ khách 北ガス; IF2242/DM1040 chờ kênh này (直列) |
| DM1040 | `MRT_TAGTAGAPI` | 5/14: `roles` (lọc 支払者), `kaiinbango`, `oc_z_customer_no`, `oc_j_supply_place_no`, `curd_flg` | `TABLE_KAIIN` — `list_contract` | danh sách hợp đồng từng hội viên; vai trò payer có sẵn (§6.2) |
| IF2242 | `tag_kaiinzokusei` | 3/3: `kaiinBango`, `zokuseiId`, `kaitouCd` | `TABLE_KAIIN` — `list_zokusei` | thuộc tính hội viên — targeting nội dung |
| IF2016 | `ipf_sp_history` | 5/7: `source_sp_num` (PK), `reg_start_ymd`/`reg_end_ymd`, `cis_use_cntr_num`, `use_type_code` | `TABLE_IF2016_SERVICE_POINT_NO_INFO` | master 供給地点 — nối địa điểm ↔ hợp đồng |
| IF2023 | `ipf_use_cntr_history` | 6/14: `source_use_cntr_num` (PK), `reg_start_ymd`, `cntr_clsfy_code` (mã PE/PG mà #5/#6 lọc), `cntr_start_ymd`/`cntr_end_ymd`, `cntr_watt` | `TABLE_IF2023_USE_CNTR_INFO` | hợp đồng + loại/thời hạn — hậu xử lý ③ đọc để biết hết hạn |
| IF2024 | `ipf_cus_meigi` | 5/8: `source_cus_meigi_num` (PK), `links_cus_num`, `sex`, `birth_yyyy`, `household_num` | `TABLE_IF2024_CUSTOMER_INFO` | nhân khẩu khách — targeting/thống kê hộ |
| IF2029 | `ipf_bld` | 4/5: `source_bldno` (ghi thành `bld_no` — `syp-eminelstandard-backend/src/functions/batch-if2029-import-building-info/app.ts:30`), `bld_divcod_1` (建物種別), `bld_use_type`, `newbldno_area` | `TABLE_IF2029_BUILDING_INFO` | thông tin tòa nhà — nguồn 建物種別 cho グルーピング (§6.2) |
| IF2223 | `lnk_ot_pgedgkk` | CSV 130+ cột (`eminel_gw_project/docs/eminel-smart/02_product_overview.md:72`), code dùng 13; tiêu biểu: `oc_z_gas_sp_no` (→PK `gas_sp_no`), `oc_j_gkiki_clsfy_code`＋`oc_h_estkk_mno` (ghép SK `equipment_code` — `syp-eminelstandard-backend/src/functions/batch-if2223-import-equipment/app.ts:49`), `oc_z_kiki_hinmok_code`, `oc_z_remove_date` | `TABLE_IF2223_EQUIPMENT` | thiết bị gas tại nhà khách — nền chức năng thiết bị |
#### §7.5 Ba IF cũ KHÔNG tồn tại trong e-smart (確実)
Grep toàn backend `IF1156`・`IF2249`・`IF2264`・`30分`・`HalfHour`・`half_hour`・`速報`・`確報`・`electric_power`・`cntct` = **0 hit**. (`ElectricPower` chỉ 1 chỗ — `syp-eminelstandard-backend/src/layers/common/nodejs/services/daikin.ts:73`, không liên quan; `payer` chỉ là hằng lọc 支払者 của DM1040 — `syp-eminelstandard-backend/src/functions/batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63`.)
#### §7.6 Chiều GỬI `/EST` (確実)
```
[dữ liệu thiết bị trong ngày] ──▶ BatchMigrationIntegratedDataStateMachine (8:00 — template.yaml:2215-2226)
        ──▶ 6 CSV (5 loại 給湯器 + remote hồng ngoại) ──SFTP, tài khoản upload riêng──▶ [/EST]  đích = Xzilla/DWH? 🔸 hỏi mui
```
Cũ: không có chiều gửi tương đương ↔ Mới: 1 luồng, 6 CSV/ngày (5 給湯器 + 1 remote hồng ngoại), 8:00.
- 🔍 `syp-eminelstandard-backend/src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57` — `pathExport = '/EST'`, cùng SFTP server, user upload riêng (`username_for_upload`/`private_key_for_upload`). 🔸 đích nghi là Xzilla/DWH — secret ngoài code, hỏi mui (§3); nếu đúng = hiện thực sẵn có của 「EMINELデータの共有」 (F-ES-10 — `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:696`).
- Lập danh mục task Xzilla phải thêm chiều xuất này (§4). Camp day3 dòng 126 đoán ESTA có sẵn đường gửi アプリログ — đã kiểm: KHÔNG có (chỉ download cho admin).
### §8 Đối chiếu dữ liệu cũ ↔ mới
| Dữ liệu hệ cũ (PostgreSQL) | Hệ mới (DynamoDB) / kế hoạch | Trạng thái |
|---|---|---|
| `ipf_cntct_cancellations` (#5) | bảng 解約 mới theo IF-01, vào luồng nhận sẵn có (§6.1 bước 2) | ❌ |
| cờ + số liên kết trên `t_101` (`c065`… — #5/#6) | cờ trên bảng hộ E-GW qua hậu xử lý ④ (§6.1 bước 3) + hậu xử lý 契約終了判定 (§6.2 bước 3) | ❌ |
| `ipf_ems_pls_cntr_payers` (#6) | KHÔNG bảng riêng — nằm trong `TABLE_KAIIN`+`TABLE_IF2023_USE_CNTR_INFO`/`TABLE_IF2024_CUSTOMER_INFO`, mở rộng theo IF-01 (§6.2 bước 2) | ⚠️ |
| `emn_all`/`emn_fast_electric_powers` (速報 — #7) | bảng 速報 mới (`syp-eminelstandard-backend/template-dynamodb.yaml` — §6.3 bước 3) | ❌ |
| `emn_confirm_electric_powers` (確報 — #7) | bảng 確報 mới, tách riêng (§6.3 bước 3) | ❌ |
| `s_102` (kết quả giờ — #7) | đầu ra Lambda tính mới → nhóm batch 集計 (§6.3 bước 5) | ❌ |

**Đếm**: ✅ 0 ・ ⚠️ 1 ・ ❌ 5 — đúng hiện trạng 3 IF chưa tồn tại; chỉ dữ liệu payer có chỗ chứa sẵn (phân tán 3 bảng). Cơ chế: đường nhận SFTP→đĩa + cron 5–10 phút → SFTP→S3→DynamoDB 0–7h (`syp-eminelstandard-backend/src/statemachine/batch_run_sequentially.asl.json`); chống trùng `flock` → khối asl (5–38) + `CsvDownloadHistory`; lịch cron cố định (`/etc/cron.d/eminel-mng-webap`) → 3 `ScheduleV2` + one-shot động (§7.1).
### §9 Phương án lịch chạy cho #7
| Tiêu chí | A. Nhét vào `BatchRunSequentially` | B. `ScheduleV2` riêng trong `syp-eminelstandard-backend/template.yaml` |
|---|---|---|
| Điều kiện | nhịp 30分値 lọt cửa sổ 0–7h mỗi giờ | nhịp dày hơn 0–7h |
| Rủi ro | chuỗi 8 IF tuần tự có khóa — luồng nhịp cao làm nghẽn | tự lo chống trùng cho luồng riêng |
| Cô lập sự cố | lây cả chuỗi import 基幹 | cô lập được |

Căn cứ (§6.3 bước 2): nhịp > 0–7h → **chọn B**. Xem xét lại khi 北ガス chốt nhịp thực tế (§3-3) — nhịp thưa thì A đủ.
### §10 QA
Đối tượng: A = khách (北ガス) qua PM mui ・ B = mui trực tiếp ・ C = bên bàn giao hệ cũ (nếu có kênh) ・ D = team app: không có (nhóm không đụng app).

| # | Câu hỏi | Vì sao | Mức |
|---|---|---|---|
| A-1 | Vào/ra + 認証 IF-01 (= chốt CLD-07, gồm chiều xuất) | cả 3 batch phụ thuộc | 🔴 |
| A-2 | IF-01 có luồng 解約 không (§3) | không có → #7 mất cờ dừng tính | 🔴 |
| A-3 | Nhịp cấp 30分値 (§3) | quyết định §9 | 🔴 |
| A-4 | 0–7h có đủ cho giải ước / master payer không | *推定* trong phán định #5/#6 | 🟡 |
| B-1 | Đích `/EST` = Xzilla/DWH? (§3) | xác định hiện thực sẵn có của F-ES-10; ảnh hưởng danh mục task | 🟡 |
| B-2 | Spec HEMS-SV (m2-cloud) | ranh giới phạm vi SYP; mui hẹn chia sẻ sau | 🟢 |
| C-1 | Ngữ nghĩa 4 trường payer + spec 契約終了判定 trích từ comment có đúng vận hành thật | spec chỉ dựa comment code — giảm rủi ro hiểu sai | 🟡 |

Thứ tự: A-1 → A-2/A-3/A-4 (hỏi gộp cùng đợt) → §6.1 bước 2–3・§6.2 bước 2–3・§6.3 toàn bộ; B-1 độc lập, gửi ngay; C-1 trước khi chốt spec #6 (riêng bước 1 trích spec: làm ngay).
### §11 Căn cứ & độ chắc chắn
| Nội dung | Nguồn |
|---|---|
| Hành vi 3 batch cũ | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/` (3 file Rcv*); `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md`; cron `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/*.txt` |
| Hiện trạng e-smart + chưa có commit E-GW | `syp-eminelstandard-backend`@`dc39aa39`: `template*.yaml`, `syp-eminelstandard-backend/src/functions/**`, `syp-eminelstandard-backend/src/layers/common/nodejs/**`, `syp-eminelstandard-backend/src/statemachine/*.asl.json` ・ `syp-eminelstandard-web-admin`@`e550326`: `git log origin/main..gw-syp-dev` rỗng; backend 15 commit gần nhất thuần e-smart |
| Yêu cầu/phương châm/scope/vấn đề mở | `eminel_gw_project/docs/eminel/`: 統合要件 v1.2 (3-2, F-ES-01/10), `10_feature_list.md`, `11_business_process/readme.md`, `22_decisions.md`, `20_open_issues.md` (CLD-07, SVC-03), camp Day3 |
| Tài liệu khảo sát ESTA (có lệch — bảng dưới) | `eminel_gw_project/docs/eminel-smart/` (6 file) |
| 3 QA Notion (回答中, 2026-08-04) | 独立デプロイ (swan)・調査範囲 (swan)・管理画面 (masao takahashi) |

| Mức | Nội dung |
|---|---|
| ✅ 確実 | không có 3 IF (grep 0 hit); luồng 8 IF + `TABLE_*` + lock 5 phút + 3 hậu xử lý; `/EST` tồn tại (6 CSV, 8:00); hành vi 3 batch cũ; yêu cầu 30分値 minh văn 2026; chưa có commit E-GW; không có đường gửi app log |
| ⚠️ *推定* | phán định #5/#6; viết thêm vào codebase e-smart; nhịp 0–7h đủ cho giải ước/payer (QA A-4); 照明アドバイス nghi 誤記 của 省エネアドバイス |
| ❓ chưa xác minh | đích `/EST` (🔸, secret); nội dung IF-01 (CLD-07); 3 QA Notion đều 回答中 |

788b438 → fbc0af0 (6 commit): chỉ đổi `eminel_gw_project/docs/eminel/3_requirements/app/` (13 file) + 1 dòng skill — file nhóm này trích không đổi, xác nhận 2026-08-06 (tập 配信・通知系 trích 2 file app bị sửa — B05/D03 — số dòng cập nhật trong tập đó).

**Lệch tài liệu khảo sát ESTA ↔ code** (5 điểm nhóm này; điểm 6 — số Push — thuộc tập 配信・通知系):

| Tài liệu ghi | Code thực tế |
|---|---|
| Import 基幹 「日次・深夜〜早朝」 (`eminel_gw_project/docs/eminel-smart/02_product_overview.md:30, 63-64`) | `cron(5 0-7 * * ? *)` — mỗi giờ 0–7h JST (§7.1) |
| Lock merge 「6分」 (`eminel_gw_project/docs/eminel-smart/02_product_overview.md:73, 78`) | `UPDATE_LOCK_TTL_MINUTES = 5` (§7.3) |
| `CsvDownloadHistory` = lịch sử admin download (`eminel_gw_project/docs/eminel-smart/03_backend_models.md:107`) | lịch sử tải TỪ SFTP về (chống tải trùng) — không liên quan admin (§7.3) |
| 「自動化ルール実行（毎分）」 (`eminel_gw_project/docs/eminel-smart/02_product_overview.md:85`) | không mỗi phút — lịch tuần/rule tạo động (§7.1; grep `rate(`: 0 hit) |
| Runtime 「Node.js 20.x, arm64」 (`eminel_gw_project/docs/eminel-smart/02_product_overview.md:49`) | `Runtime: nodejs24.x` (`syp-eminelstandard-backend/template.yaml:181`; CompatibleRuntimes layer chung vẫn nodejs20.x — dòng 3163) |
