# Báo cáo điều tra: nhóm CSV・ZIPエクスポート系 (4 batch #8–#11) — có cần port sang hệ mới không?
| | |
|---|---|
| Đối tượng | 4 batch `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConDeviceStatuses / ConSensorHourlyValues / ConSensorDailyValues / ConSensorDailyAveValuesCommand` (#8–#11), nhóm CSV/ZIP trong `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md`, chạy trên `conciergesv` |
| Phạm vi | `legacy_eminel_docs`@`ccd8f56` ・ `eminel_gw_project`@`fbc0af0` (điều tra tại `788b438`; tài liệu nhóm này trích không đổi giữa 2 commit — §11) ・ `syp-eminelstandard-backend`@`dc39aa39` ・ `syp-eminelstandard-web-admin`@`e550326` (branch `gw-syp-dev`, = origin 2026-08-06) |
| Ngày / người | Điều tra 2026-08-04 ・ lập 2026-08-06 ・ Bui Trong Dat (SYP) + AI |
| Phân tập / liên quan | 1/3 tập bộ 11 batch (số #1–#11 xuyên suốt, chung JP–VN); 2 tập kia: 配信・通知系 (#1–#4), 外部連携・受信系 (#5–#7) ・ bản JP: `旧EMINELバッチ移行判定報告書_CSV・ZIPエクスポート系4本.md` (khớp 1-1) |

**Ký hiệu**:
| Mã | Nghĩa |
|---|---|
| spec [I] / 別表① | Spec download màn quản trị `eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md` (DRAFT) / bảng phụ lục ① — danh mục loại file cho tải |
| SVC-03 | Vấn đề mở: yêu cầu 性能・可用性・運用・移行 chưa ghi (`eminel_gw_project/docs/eminel/2_management/20_open_issues.md:86`; gồm 保持期間/backup — dòng 87) |
| F-ES-10 | 「Xzilla連携」 trong 統合要件 v1.2 |
| t_202/s_102/s_103/s_113 | 機器状態/時間値/日値/日平均値 ・ EMS-SP-NO = mã điểm lắp đặt (≈ hộ) |
| 質問表 / QAデータベース | Bảng câu hỏi gửi khách `mui-ai/requirements/qa_kitagas.md` / kênh QA nội bộ với mui (Notion) |
| 確実 / *推定* / 🔸 | Đã kiểm trên code / suy đoán có căn cứ / giả thuyết chưa kiểm ・ trong code `...` = lược |

Mục lục: KẾT LUẬN ・ I: §1 Vì sao ・ §2 Nơi xử lý mới ・ §3 Cần xác nhận ・ §4 Dễ hiểu sai ・ §5 Việc tiếp ・ II: §6 Chi tiết ・ §7 Hạ tầng ・ §8 Đối chiếu ・ §9 A/B ・ §10 QA ・ §11 Căn cứ
## KẾT LUẬN
> **BỎ CẢ 4 BATCH (#8–#11) — GIỮ NHU CẦU "vận hành lấy được dữ liệu ra file".**
> Bản chất 4 batch = **backup-trước-khi-xóa** (sơ tán CSV/ZIP rồi xóa partition), sinh từ chính sách giữ 8–14 ngày của DB cũ; spec [I] yêu cầu **giữ 24ヶ月 (T.B.D), tải bất kỳ lúc nào** — tiền đề cũ biến mất.
> **THAY bằng**: retention mới — DynamoDB TTL + sơ tán S3 khi cần, chờ spec [I] + SVC-03 chốt — kết hợp 2 đường xuất sẵn có (admin download 17 endpoint / SFTP `/EST`). Có **5 điểm cần xác nhận** trước khi chốt (→ §3).
# PHẦN I — BÁO CÁO
## 1. Vì sao kết luận như vậy
| Khía cạnh | Hệ cũ | Hệ mới |
|---|---|---|
| Kỳ hạn giữ hạt mịn | **8–14 ngày tùy bảng** (`t_202` 8, `s_102` 14 — `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:47-50`) | Spec [I]: **24ヶ月 (T.B.D)**, TTL dọn |
| "Cứu" dữ liệu trước khi xóa | 4 batch export CSV → ZIP → đĩa server | Không cần — DB giữ suốt kỳ hạn; backup = PITR |
| Vận hành lấy file | Tải ZIP đổ sẵn qua màn quản trị cũ (`eminelsv`) | Sinh khi yêu cầu (17 EP + presigned URL); định kỳ → pattern SFTP |

**6 xử lý cốt lõi → còn cần?**
| # | Xử lý | Còn cần? | Vì sao |
|---|---|---|---|
| 1 | Export partition ra CSV (`t_202`/`s_102`/`s_103`/`s_113`) | ❌ | dữ liệu nằm DynamoDB suốt kỳ hạn |
| 2 | Nén ZIP tuần/tháng đổ sẵn | ❌ | ZIP on-demand (`BatchDownloadFunction` → JSZip → S3) |
| 3 | Xóa partition sau backup (`DeleteData`) | ❌ | TTL tự xóa |
| 4 | Van an toàn `set -eu` (CSV hỏng → không xóa) | ❌ (có tương đương) | vai trò chuyển sang PITR |
| 5 | Vận hành lấy dữ liệu ra file | ✅ | cơ chế download sẵn, chỉ thêm loại E-GW |
| 6 | File đổ sẵn định kỳ (thói quen) | ⚠️ tùy khách | [I] chưa quyết — nếu cần: pattern `/EST` (§9-B) |
## 2. Hệ mới xử lý ở đâu
| Việc cũ | Hệ mới (path) | Loại |
|---|---|---|
| Admin tải CSV/ZIP | `syp-eminelstandard-backend/src/functions/api-download/app.ts` → `syp-eminelstandard-backend/src/functions/batch-download/` → S3 `BUCKET_DOWNLOAD` → presigned URL; màn `syp-eminelstandard-web-admin/pages/other/data-management/index.vue` | CÓ SẴN — thêm loại (§6.5-3) |
| Giữ/xóa theo kỳ hạn | TTL trong `syp-eminelstandard-backend/template-dynamodb.yaml` (bảng đo E-GW dựng mới) | PHẢI KHAI THÊM (§6.5-2) |
| Backup | PITR (bật sẵn) | CÓ SẴN |
| File định kỳ (nếu muốn) | Pattern `syp-eminelstandard-backend/src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts` + `ScheduleV2` mới | CHƯA CÓ — chỉ làm nếu chốt cần (§9-B) |

Luồng dữ liệu — **Cũ**: cron 05:15 → **4** Command → partition `t_202`/`s_102`/`s_103`/`s_113` (PostgreSQL) → CSV → ZIP → đĩa server → DeleteData → DeleteLogicalDeletedDevices **↔ Mới**: admin → api-download (**17** endpoint) → BatchDownloadFunction → ZIP → S3 BUCKET_DOWNLOAD → presigned URL **600s** (+ nhánh `/EST`: **6** CSV thiết bị, 8:00); kỳ hạn = TTL, backup = PITR (sơ đồ: §6.3/§6.5).
- Tư tưởng: cũ = "backup để xóa" (DB chật); mới = "giữ lâu + tải khi cần". Bẫy tên: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZip…` = bước đầu quy trình XÓA (cron mục 「#12.DBデータ削除」); `CsvDownloadHistory` = chiều NHẬN (chống tải trùng SFTP), không phải lịch sử admin download (§11).
## 3. Điểm cần xác nhận trước khi chốt
| # | Điểm treo | Hệ cũ | Hệ mới / kế hoạch | Mức |
|---|---|---|---|---|
| 1 | Kỳ hạn giữ | 8–14 ngày (+2 tháng bảng tháng) | Spec [I] 24ヶ月 nhưng toàn bộ T.B.D (`eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md:43-52`) | 🔴 |
| 2 | SVC-03 | — | Chưa có phương án → chưa chốt TTL/sơ tán S3 | 🔴 |
| 3 | Thói quen file định kỳ | ZIP tuần/tháng đổ sẵn | On-demand mặc định; định kỳ = mục chưa quyết của [I] | 🟡 |
| 4 | Đích SFTP `/EST` | — | Trong secret, chưa xác nhận Xzilla/DWH (🔸) | 🟡 |
| 5 | Format cột CSV | Cột cũ (đã trích vào [I] mục 現行EMINEL) | Khuyến nghị giữ tương thích (*推定* thói quen) | 🟡 |

Gửi khách qua PM — đề xuất thêm vào 質問表 (nội bộ = chốt spec [I] + SVC-03; khối gửi khách không chứa mã nội bộ):
> 「新システムにおける計測データ・各種履歴の**保持期間**について、管理画面のデータダウンロード仕様では**24ヶ月（未確定）**とされています。この値で確定してよいでしょうか。あわせて、保持期間・バックアップを含む**運用要件全般**の方針のご提示をお願いいたします。」
> 「現行システムでは週次／月次で ZIP ファイルが自動作成・保管される運用ですが、新システムでは**必要時に管理画面からダウンロードする方式**を基本と考えています。従来どおり**定期的にファイルが作成・保管される運用**の継続をご希望でしょうか（ご希望の場合は定期エクスポート機能を追加実装します）。」（tiền đề: khách đã xem mô tả/demo cơ chế mới）

Hỏi mui (QAデータベース; chung tập 外部連携・受信系, hỏi 1 lần — bản đầy đủ ở §3 tập đó):
> 「SFTP `/EST` フォルダの宛先は Xzilla/DWH でしょうか（接続先が secret 管理のためコードから確認できず）。」
## 4. Điểm dễ bị hiểu sai
| Hiểu sai | Đúng phải là |
|---|---|
| "4 batch = chức năng download cho vận hành" | Backup-trước-khi-xóa; tải file chỉ là hệ quả (§6.1) |
| "Bỏ 4 batch = mất khả năng lấy dữ liệu" | Nhu cầu GIỮ, chuyển sang download on-demand sẵn có + tùy chọn định kỳ (§9) |
| "`CsvDownloadHistory` = lịch sử admin download" | Chiều NHẬN — chống tải trùng SFTP; tài liệu khảo sát ESTA ghi lệch (§11) |
| "#10/#11 backup partition tháng trước" | **Tháng trước nữa (前々月)** — 05:15 ngày 1 −32 ngày luôn rơi tháng −2, khớp kỳ hạn xóa 2 tháng (§6.3) |
## 5. Việc tiếp theo
| # | Nội dung | Phụ trách |
|---|---|---|
| 1 | Nêu chốt spec [I] + SVC-03 khi review [I]; đề xuất thêm câu vào 質問表 (§3) | SYP (+PM) |
| 2 | Hỏi mui đích `/EST` (§3; chung tập Xzilla) | SYP |
| 3 | Sau #1: thiết kế retention — TTL trong `syp-eminelstandard-backend/template-dynamodb.yaml`, cân nhắc S3 theo dung lượng nhóm 集計 | SYP Dev |
| 4 | Mở rộng download cho loại E-GW (4 lớp — §6.5-3) | SYP Dev |
| 5 | Nếu khách muốn file định kỳ: batch export pattern `/EST` (§9-B) | SYP Dev |
| 6 | Task Notion: ghi 4 batch = "bỏ, thay bằng retention + download/export" — không đếm vào ~46本 | SYP + PM |
| 7 | Trả lời vế QA 独立デプロイ *"既存システムを使い続けたほうがいい機能"*: ① 旧EMINEL: không batch nào đáng giữ nguyên trạng; ② e-smart: 4 ứng viên (chung 3 tập) — nhóm này góp cơ chế download/export (§7.2/§7.3) | SYP (QAデータベース) |
> **Phương châm**: *Port nhu cầu, đừng port giải pháp* — cơ chế sinh từ ràng buộc đã mất (DB chật → backup rồi xóa) bỏ cùng ràng buộc; mang sang chỉ nhu cầu (lấy file) + van an toàn tương đương (PITR thay `set -eu`).
# PHẦN II — CHI TIẾT KỸ THUẬT
## 6. Chi tiết 4 batch (#8–#11, gộp — chỉ khác bảng dữ liệu + chu kỳ)
**6.1 Mục đích**: sơ tán dữ liệu hạt mịn ra CSV/ZIP **trước khi xóa partition** — DB chỉ giữ 8–14 ngày mà vận hành vẫn truy được số cũ. KHÔNG phải chức năng download.

**6.2 Phán định** (確実 về hướng, chi tiết chờ T.B.D): **BỎ cả 4 — GIỮ nhu cầu — THAY bằng retention mới + 2 đường xuất sẵn.**
- BỎ: cơ chế backup-trước-xóa (4 batch + 2 shell + `DeleteDataCommand`); GIỮ: lấy dữ liệu ra file → download theo spec [I] (cột: §6.5-5); THAY: kỳ hạn = TTL (+S3 — §6.5-2), lấy file = ① on-demand (+② định kỳ nếu khách muốn — §9).
- Vì sao: ① cơ chế mất lý do khi kỳ hạn đổi; ② [I] đòi 24ヶ月 + tải mọi lúc (§6.4); ③ e-smart không có backup-rồi-xóa nhưng 2 đường xuất hoàn chỉnh (§7.2/§7.3).

**6.3 Flow hệ cũ** (確実):
| # | Class | Bảng | Partition | Chu kỳ / shell |
|---|---|---|---|---|
| 8 | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConDeviceStatusesCommand` | `t_202` | đủ 8 ngày (NGÀY) | 05:15 hằng ngày (`day2to31.sh`) + ngày 1 (`day1.sh`); thứ Hai ZIP tuần |
| 9 | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorHourlyValuesCommand` | `s_102` | đủ 8 ngày (NGÀY) | như #8 |
| 10 | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand` | `s_103` | **前々月** (THÁNG, ~2 tháng) | 05:15 ngày 1 (`day1.sh`), ZIP luôn |
| 11 | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyAveValuesCommand` | `s_113` | **前々月** — 1 file toàn hệ | 05:15 ngày 1 (`day1.sh`), ZIP luôn |

`--datetime` default `'now'` (`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand.php:28`); CSV chia theo EMS-SP-NO (#11: 1 file); ZIP `ZipArchive`, tên SJIS (`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateZipsTrait.php:23-72`); 2 shell đều chạy `DeleteData` → `DeleteLogicalDeletedDevices` ở cuối (mở shell thật trong tgz xác nhận).
```
cron 05:15 (mục #12.DBデータ削除 — cron 39–41): hằng ngày day2to31.sh(#8/#9) / ngày 1 day1.sh(#8–#11 cả 4)
  ※ ngày 1 CẢ HAI shell cùng chạy 05:15 (cron day2to31 = 15 5 * * *, không loại trừ ngày 1)
  → CreateCsvAndZip*Command: đọc partition (t_202/s_102: 8 ngày trước ・ s_103/s_113: 前々月 ~2 tháng)
  → sinh CSV (theo EMS-SP-NO; #11 gộp 1 file) → đĩa server (CON_DEVICE_CSV_FILES_PATH — …DeviceStatusesCommand.php:58)
  → nén ZIP (#8/#9 ZIP tuần chỉ thứ Hai — isMonday :182)
  → DeleteData DROP partition quá hạn (#8/#9: 9/15 ngày tuổi = keepDays+1 — :85, đã export từ trước; #10/#11: đúng partition vừa export, hạn 2 tháng — :110-112) → DeleteLogicalDeletedDevices
  ※ set -eu: CSV lỗi → KHÔNG xóa (van an toàn) → vận hành tải file qua màn quản trị cũ (eminelsv)
```
**Cũ 1 dòng**: cron 05:15 → 4 Command → partition `t_202`/`s_102`/`s_103`/`s_113` → CSV (chia theo EMS-SP-NO) → ZIP → đĩa server → DeleteData → DeleteLogicalDeletedDevices. *(Path đầy đủ các file viết tắt trong sơ đồ: bảng nguồn §11.)*

Code then chốt — partition cả 4 file **cùng dòng 39** + kỳ hạn phía xóa:
```php
$partitionTableName = 't_202_' . $dateTime->subDays(8)->format('Ymd');   // #8: NGÀY, 8 ngày trước   (mỗi CreateCsvAndZip*Command.php:39)
$partitionTableName = 's_102_' . $dateTime->subDays(8)->format('Ymd');   // #9: NGÀY, 8 ngày trước
$partitionTableName = 's_103_' . $dateTime->subDays(32)->format('Ym');   // #10: THÁNG — luôn rơi 前々月
$partitionTableName = 's_113_' . $dateTime->subDays(32)->format('Ym');   // #11: THÁNG — luôn rơi 前々月
// --- DeleteDataCommand.php:46-50 (bảng tháng s_103/s_113: dòng 53–54, 2 tháng) ---
// 日単位削除処理
$this->dropDailyTable('t_202', $dateTimeForDay, 8);    // xóa sau 8 ngày
$this->dropDailyTable('s_101', $dateTimeForDay, 8);
$this->dropDailyTable('s_102', $dateTimeForDay, 14);   // xóa sau 14 NGÀY (khác t_202!)
$this->dropDailyTable('s_112', $dateTimeForDay, 8);
```
*(Vì sao 前々月: default `'now'` + chạy 05:15 ngày 1 → −32 ngày luôn vào tháng −2, vd 01/08−32d=30/06→`s_103_202606`; khớp `dropMonthlyTable(…,2)`=`subMonths(2)` — `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:110-112`.)*

| Bất thường | Hành vi | Nguồn |
|---|---|---|
| CSV lỗi giữa chừng | `set -eu` dừng → không xóa | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:26-37`, 補足1 「CSV作成後に問題なければデータを消去」 |
| Partition không tồn tại | Log alert rồi thoát | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConDeviceStatusesCommand.php:42-45` |
| Không phải thứ Hai (#8/#9) | Bỏ qua ZIP tuần | cùng file `:182` (`isMonday`) |

**6.4 Hệ mới có gì / E-GW yêu cầu** (確実):
- e-smart KHÔNG có backup-rồi-xóa; 2 đường xuất sẵn (①②, code §7.2/§7.3); `CsvDownloadHistory` = chiều nhận; backup = PITR, kỳ hạn = TTL (`syp-eminelstandard-backend/template-dynamodb.yaml`).
- Spec [I]: loại kế thừa E-Smart (顧客情報, アクセスログ, ポイント履歴… — đều 🔴T.B.D) + 3 loại E-GW mới: GW・連携デバイスデータ, 連携デバイスエラー履歴, **連携機器別計測値集計データ (10分/1時間/1日/1ヶ月値)**; **保持期間 24ヶ月 (T.B.D)**; SVC-03 chưa định nghĩa — 🔍 `eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md:16-19, 43-52, 200-204`・`eminel_gw_project/docs/eminel/2_management/20_open_issues.md:87`.

**6.5 Flow hệ mới đề xuất**:
```
[đường ①] admin (pages/other/data-management/index.vue + form-download-data-management.vue) → POST api-download (17 EP — app.ts:23-46) → invoke bất đồng bộ ('Event' — download-user-info.ts:17-25)
  → batch-download (5120MB/900s — template.yaml:475-493) → đọc DynamoDB (vd TABLE_KAIIN — :579)
  → CSV → JSZip (:563-568) → S3 BUCKET_DOWNLOAD (template.yaml:233) → presigned URL 600s (get-presigned-url-for-download.ts:67)
[đường ② — §9-B] ScheduleV2 (mẫu BatchMigrationIntegratedData — template.yaml:2205-2240) → CSV → SFTP /EST (mẫu upload-data-backup-to-sftp.ts)
※ cả 2 đường không có bước xóa — kỳ hạn do TTL, hết công đoạn "sơ tán trước khi xóa" (§8)
```
**Mới 1 dòng**: admin → api-download (17 endpoint) → BatchDownloadFunction → ZIP → S3 BUCKET_DOWNLOAD → presigned URL 600s; nhánh `/EST`: 6 CSV thiết bị, 8:00 hằng ngày. *(Path đầy đủ: bảng nguồn §11.)*

Các bước (SYP, `gw-syp-dev`):
1. Chốt spec [I] + SVC-03 khi review [I] (câu 質問表 đã soạn §3) — *Vì sao*: mọi giá trị thiết kế sau phụ thuộc.
2. Retention: khai TTL trong `syp-eminelstandard-backend/template-dynamodb.yaml`; quá tốn → sơ tán S3 (theo dung lượng nhóm 集計) — *Vì sao*: TTL là tiền đề bỏ backup-trước-xóa.
3. Mở rộng download 4 lớp: `syp-eminelstandard-backend/src/functions/api-download/app.ts` + handler ủy thác (mẫu `syp-eminelstandard-backend/src/functions/api-download/download-user-info.ts`); handler `syp-eminelstandard-backend/src/functions/batch-download/` (mẫu `syp-eminelstandard-backend/src/functions/batch-download/download-user-info.ts`); `syp-eminelstandard-backend/template.yaml` thêm env `TABLE_*` vào `BatchDownloadFunction` (475–493); web-admin `DOWNLOAD_DATA_MANAGEMENT_TYPE` (`syp-eminelstandard-web-admin/constants/common.ts:614-622`) + `syp-eminelstandard-web-admin/pages/other/data-management/index.vue` + `syp-eminelstandard-web-admin/components/data-management/form-download-data-management.vue` + `syp-eminelstandard-web-admin/components/data-management/list-download-data-management.vue` — *Vì sao*: 17 EP/7 loại cùng 1 pattern.
4. Nếu khách chốt muốn file định kỳ: batch export theo ② (mẫu `syp-eminelstandard-backend/src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts` + 1 `ScheduleV2`) — *Vì sao*: [I] chưa chốt nhu cầu, chưa chốt chưa làm (§9).
5. Format cột: giữ tương thích cũ (*推定* thói quen); danh mục cột đã trích vào [I] (`DownloadController::getCsvHeadersOnSelection()`) — không lập task trích lại.
6. Task Notion: ghi "bỏ, thay bằng retention + download/export" — *Vì sao*: tránh đếm nhầm vào ~46本.

Kiểm thử: end-to-end ① (form → sinh → `BUCKET_DOWNLOAD` → presigned URL 600s); so cột với 現行EMINEL trong [I]; biên TTL (quá hạn mất, trong hạn tải được); ② cùng khuôn 6 loại CSV hiện hữu.
## 7. Hạ tầng chung
**7.1 Nền + tiền đề**:
| | Hệ cũ | e-smart |
|---|---|---|
| Ngôn ngữ | PHP 8.0 / CakePHP 4.4 | TypeScript / SAM + Lambda (Node.js 24 — `syp-eminelstandard-backend/template.yaml:181`) |
| DB | PostgreSQL (partition) | DynamoDB (PITR bật sẵn) |
| Batch | cron server + shell flock | Step Functions + EventBridge Scheduler |
| Nhận file | SFTP → đĩa | SFTP → S3 → DynamoDB |

3 lịch tĩnh (`ScheduleV2`, `Asia/Tokyo` — `syp-eminelstandard-backend/template.yaml:9-11`): ① `BatchRunSequentially` `cron(5 0-7 * * ? *)` (853–888); ② `BatchMigrationIntegratedData` `cron(0 8 * * ?)` (2205–2240) — **đường ② `/EST` chạy trong đây**; ③ `BatchGetErrorDeviceInfoOfRinnai` (2966–2980); còn lại: one-shot động (`syp-eminelstandard-backend/src/layers/common/nodejs/services/put-schedule.ts:18-33`), ngoại lệ automation rule (`syp-eminelstandard-backend/src/functions/api-automation/common.ts:115, 167-175`), không polling phút (grep `rate(`: 0 hit). Day3: batch cũ 「いけてない」 — làm lại, 1 batch = 1 task, バッチボーン trước, 結合 tháng 9 (🔍 `eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:35, 51, 99-103, 147-149`); QA 独立デプロイ (swan, 回答中): hướng độc lập → "dùng lại" ≠ 0 công; `gw-syp-dev` chưa có commit E-GW; *推定*: viết thêm vào codebase e-smart (từ QA 管理画面 chung source — masao takahashi, 回答中).

**7.2 Đường ①** (確実) — router 17 endpoint (🔍 `syp-eminelstandard-backend/src/functions/api-download/app.ts:23-46`) + 7 loại web-admin (🔍 `syp-eminelstandard-web-admin/constants/common.ts:614-622`):
```ts
const APIs = {
  POST: {
    ...                                    // entry đầu (download_list_device_error_mst) đã lược
  [`/${END_POINT}/download_list_dr`]: downloadListDr, ...
  [`/${END_POINT}/download_access_log`]: downloadAccessLog,
  [`/${END_POINT}/download_user_info`]: downloadUserInfo,
  [`/${END_POINT}/download_gas_equipment_data`]: downloadGasEquipmentData, ...
// --- syp-eminelstandard-web-admin/constants/common.ts:614-622 ---
export const DOWNLOAD_DATA_MANAGEMENT_TYPE = {
  USER_INFO: 'user_info',            ACCESS_LOG: 'access_log',
  MUI_SENSOR_HISTORY: 'mui_sensor_history', GAS_DEVICE_HISTORY: 'gas_device_history',
  POINT_AWARD_HISTORY: 'point_award_history', BADGE_EARNED_HISTORY: 'badge_earned_history',
  GAS_DEVICE_RAW_HISTORY: 'gas_device_raw_history',
}
```
- Loại nặng: invoke bất đồng bộ `BatchDownloadFunction` (`'Event'` — `syp-eminelstandard-backend/src/functions/api-download/download-user-info.ts:17-25`; `syp-eminelstandard-backend/template.yaml:475-493`, 5120MB/900s); đọc DynamoDB (env `TABLE_*` — 483–492; 顧客情報 = `TABLE_KAIIN` — `syp-eminelstandard-backend/src/functions/batch-download/download-user-info.ts:579, 590`) → JSZip (563–568) → S3 `BUCKET_DOWNLOAD` (:233) → presigned URL 600s (`syp-eminelstandard-backend/src/functions/api-s3/get-presigned-url-for-download.ts:67`).
- ⚠️ `CsvDownloadHistory` = chiều NHẬN (`syp-eminelstandard-backend/src/layers/common/nodejs/models/CsvDownloadHistory.ts:1-6`; ghi tại `syp-eminelstandard-backend/src/functions/batch-forward-csv-from-sftp-server-to-s3/app.ts:80-93`).

**7.3 Đường ② `/EST`** (確実; đích 🔸): 6 loại CSV thiết bị (5 給湯器 + remote hồng ngoại), 8:00 hằng ngày, tài khoản upload riêng — 🔍 `syp-eminelstandard-backend/src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57`・`syp-eminelstandard-backend/template.yaml:2215-2226`; tiền lệ §9-B; đích chưa xác nhận (§10-B1). Chi tiết: tập 外部連携・受信系 **§7.6** (chiều gửi `/EST` — code + F-ES-10); luồng nhận §7.3, bảng 8 kênh IF §7.4 tập đó.
## 8. Đối chiếu dữ liệu cũ ↔ mới
| Bảng cũ | Kỳ hạn cũ | Loại 別表① liên quan | Hệ mới đã có bảng? |
|---|---|---|---|
| `t_202` | 8 ngày | GW・連携デバイスデータ (🔴T.B.D) | ❌ dựng mới (§6.5-2/3) |
| `s_102` | 14 ngày | 集計データ・1時間値 (🔴T.B.D) | ❌ dựng mới, phối hợp nhóm 集計 |
| `s_103` | 2 tháng | 集計データ・1日値 (🔴T.B.D) | ❌ dựng mới, phối hợp nhóm 集計 |
| `s_113` | 2 tháng | không có mục riêng trong 別表① | ❌ chờ chốt loại ở [I] |
| **Đếm** | — | — | **0/4 có sẵn (❌×4)** — khớp "không tài sản đo đạc dùng lại; e-smart không tính sẵn 集計 (`syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`)" |

| Cơ chế | Hệ cũ | Hệ mới | Trạng thái |
|---|---|---|---|
| Nơi lưu | Partition PostgreSQL | Bảng DynamoDB (dựng mới) | ❌ |
| Kỳ hạn | 8–14 ngày (+2 tháng) — `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:47-50, 53-54` | [I] 24ヶ月 + TTL | ⚠️ T.B.D |
| Lấy file | Sinh SẴN → đĩa → màn cũ | Sinh KHI CẦN (①) / định kỳ (②) | ✅ sẵn, thêm loại |
| Xóa | DROP sau backup (`set -eu` van) | TTL tự xóa | ✅ chuẩn DynamoDB |
| Backup | File sơ tán kiêm backup | PITR + chờ SVC-03 | ⚠️ |
| **Đếm** | — | — | **✅2 ・ ⚠️2 ・ ❌1** — việc phải làm dồn vào bảng dữ liệu + kỳ hạn, không phải cơ chế xuất |
## 9. Phương án A/B
| Tiêu chí | **A — chỉ mở rộng admin download** | **B — A + batch export định kỳ (`/EST`)** |
|---|---|---|
| Đáp ứng lấy file | ✅ đủ | ✅ đủ + giữ thói quen file đổ sẵn |
| Khối lượng thêm | 4 lớp theo pattern (§6.5-3) | + 1 batch + 1 `ScheduleV2` + chốt nơi đổ |
| Phụ thuộc treo | Spec [I] | [I] + đích `/EST` + khách xác nhận muốn |
| Vận hành khách | Đổi thói quen: bấm tải | Giữ nguyên |

Chọn **A trước** (ít phụ thuộc; "file định kỳ" chưa xác nhận là yêu cầu). Chuyển **B** khi: khách muốn giữ (câu §3) hoặc [I] chốt yêu cầu định kỳ.
## 10. Danh sách QA (theo đối tượng; D-team app: không liên quan — bỏ)
| # | Đối tượng | Câu hỏi | Vì sao | Mức |
|---|---|---|---|---|
| A1 | Khách/PM | Chốt [I]: 24ヶ月 + loại dữ liệu; kèm SVC-03 (văn bản §3, đề xuất vào 質問表) | Mọi thiết kế retention đứng sau | 🔴 |
| A2 | Khách/PM | Muốn giữ thói quen ZIP định kỳ? (văn bản §3) | Quyết A/B (§9); mục chưa quyết của [I] | 🟡 |
| A3 | Khách/PM | 7 loại kế thừa E-Smart: loại nào áp cho E-GW? (別表① đều 🔴T.B.D) | Phạm vi bước 3 | 🟡 |
| B1 | mui | Đích `/EST` = Xzilla/DWH? (rút gọn §3; bản đầy đủ ở tập Xzilla §3 — hỏi 1 lần chung 2 tập) | Tiền đề pattern ② (§9-B); liên quan F-ES-10 chiều gửi | 🟡 |
| B2 | mui *(SYP trả lời)* | Vế 使い続け của QA 独立デプロイ: ① 旧EMINEL không có; ② e-smart 4 ứng viên — nhóm này: download/export (§7.2/§7.3) | mui đang chờ; giúp chốt dùng chung (§5-7) | 🟡 |
| C1 | Bàn giao hệ cũ | Format cột CSV cũ có ràng buộc nghiệp vụ (hệ nào đọc file)? | Quyết mức tương thích bước 5 — hiện là *推定* | 🟡 |
```
A1 [I]+SVC-03 (🔴) ─→ bước 2 retention → bước 3 mở rộng download
A2 + B1 ─→ quyết A/B (§9) → (B) bước 4 export        C1 ─→ bước 5 tương thích cột
```
## 11. Căn cứ & độ chắc chắn
| Nội dung | Nguồn |
|---|---|
| Hệ cũ: partition/default now/thư mục xuất/isMonday/partition-thiếu; kỳ hạn xóa (8/14 ngày, 2 tháng, keepDays+1) | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZip*Command.php:39` (×4); `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand.php:28`; `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConDeviceStatusesCommand.php:58, 182, 42-45`; `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:46-50, 53-54, 85, 110-112` |
| ZIP+SJIS; cron+shell (`set -eu`, DeleteLogicalDeletedDevices) | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateZipsTrait.php:23-72`; `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:39-41`; `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:26-37`; shell trong `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` |
| Đường ① | `syp-eminelstandard-backend/src/functions/api-download/app.ts:23-46`; `syp-eminelstandard-backend/src/functions/api-download/download-user-info.ts:17-25`; `syp-eminelstandard-backend/template.yaml:233, 475-493`; `syp-eminelstandard-backend/src/functions/batch-download/download-user-info.ts:563-568, 579, 590`; `syp-eminelstandard-backend/src/functions/api-s3/get-presigned-url-for-download.ts:67`; web-admin `syp-eminelstandard-web-admin/constants/common.ts:614-622` + `syp-eminelstandard-web-admin/pages/other/data-management/` + `syp-eminelstandard-web-admin/components/data-management/*` |
| Đường ② + nền lịch | `syp-eminelstandard-backend/src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57`; `syp-eminelstandard-backend/template.yaml:9-11, 853-888, 2205-2240, 2215-2226, 2966-2980`; `syp-eminelstandard-backend/src/layers/common/nodejs/services/put-schedule.ts:18-33`; `syp-eminelstandard-backend/src/functions/api-automation/common.ts:115, 167-175` |
| E-GW yêu cầu; không 集計 sẵn; Day3 | `eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md:16-19, 43-52, 200-204`; `eminel_gw_project/docs/eminel/2_management/20_open_issues.md:86-87`; `syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`; `eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:35, 51, 99-103, 147-149` |

- ✅ 確実: toàn bộ hành vi hệ cũ (§6.3 — code + shell thật); "e-smart không có backup-rồi-xóa, có 2 đường xuất" (§7 — soi code `gw-syp-dev`); nội dung [I]/SVC-03 tại commit ở meta.
- ⚠️ *推定*/🔸: (a) giữ tương thích cột — thói quen (§6.5-5); (b) 🔸 đích `/EST` = Xzilla/DWH (§7.3); (c) viết thêm vào codebase e-smart (§7.1).
- ❓ Chưa xác minh: [I] DRAFT (loại + 24ヶ月 đều T.B.D); SVC-03 chưa định nghĩa; dung lượng (chờ nhóm 集計); khách có muốn file định kỳ; 3 trang QA Notion (独立デプロイ — swan; 調査範囲 — swan; 管理画面 — masao takahashi) đều 回答中, tham chiếu 2026-08-04 qua ảnh — trích lại phải mở trang gốc. Cập nhật 788b438→fbc0af0 (6 commit) chỉ đổi `3_requirements/app/` + 1 dòng skill — tài liệu nhóm này trích không đổi (xác nhận 2026-08-06).

| Tài liệu khảo sát ESTA ghi | Code thực tế |
|---|---|
| `CsvDownloadHistory` = lịch sử download (`eminel_gw_project/docs/eminel-smart/03_backend_models.md:107`) | Chiều NHẬN — chống tải trùng SFTP (§7.2) |
| 自動化ルール mỗi phút (`eminel_gw_project/docs/eminel-smart/02_product_overview.md:85`) | Lịch tuần tạo động theo rule (§7.1; grep `rate(`: 0 hit) |
| Node.js 20.x (`eminel_gw_project/docs/eminel-smart/02_product_overview.md:49`) | `nodejs24.x` (`syp-eminelstandard-backend/template.yaml:181`; CompatibleRuntimes vẫn 20 — :3163) |
