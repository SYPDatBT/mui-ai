# Bảng câu hỏi QA — nhóm batch CSV/ZIPエクスポート系 (4 batch)

> **Cách dùng**: như `qa_kitagas.md` — mỗi câu gồm bản tiếng Việt (nội bộ hiểu) và khối 🇯🇵 tiếng Nhật **paste được nguyên vẹn**.

| | |
|---|---|
| Ngày lập | 2026-08-12 |
| Xuất phát | Review độc lập bộ 4 báo cáo điều tra batch CSV/ZIP (`submit_folder/2026_08_12/`, 8 file JP+VN) — 5 agent review + kiểm chứng đối kháng + phản biện |
| Đối chiếu repo | `legacy_eminel_docs` @ `ccd8f56` (= origin/main, fetch 2026-08-12) ・ `eminel_gw_project` @ `460c671` (spec [I] **không đổi** ở origin `1100487` — đã kiểm diff) |
| Số câu | 5 = 2 gửi 北ガス (qua PM mui) + 3 hỏi mui trực tiếp |
| Đường đi | SYP → PM mui Lab → (Q-01, Q-02) 北ガス *(SYP không gửi trực tiếp)* |
| Trạng thái | Đã qua phản biện độc lập 8 tiêu chí; Q-05 đã viết lại theo kết quả phản biện (tiền đề cũ về `c008` sai — xem ghi chú cuối file) |

**Quy ước tham chiếu**: câu **gửi mui** được phép dẫn đường dẫn repo `legacy_eminel_docs/...` / `eminel_gw_project/...` (mui giữ chính các repo đó). Câu **gửi 北ガス** chỉ dùng tên tài liệu hai bên cùng biết. Cả hai loại đều **không** chứa prefix workspace nội bộ SYP (`submit_folder/...`, `requirements/...`) trong khối 🇯🇵 — tài liệu điều tra dẫn theo tên file + ghi chú 「別途お渡し分」.

**Thứ tự gửi đề xuất**: ① Q-04 + Q-03 cho mui trước (vòng nội bộ nhanh; Q-04 nên chốt trước khi giao bộ báo cáo điều tra); ② Q-01 + Q-02 cho 北ガス cùng đợt ngay sau (vòng hồi đáp dài nhất, không phụ thuộc ①); ③ Q-05 gửi kèm dịp trao đổi với mui.

---
---

## Q-BATCH-01 — Tải dữ liệu quá khứ ở hệ mới: cần tải ngược tối đa bao xa? (chốt 保持期間 đang 要FIX)

**Ưu tiên**: chặn việc ・ **Gửi tới**: 北ガス (qua mui) ・ **Phản biện**: đạt, gửi nguyên trạng

**Bối cảnh điều tra**

Hệ cũ có hai tầng lưu: DB chỉ giữ ngắn (機器状態情報 8 ngày, 1時間値 14 ngày, 1日値/1日値（平均） 2 tháng), nhưng trước khi DROP partition, 4 batch CSV/ZIP xuất file ra đĩa và các ZIP tuần/tháng này **không có cơ chế xoá** — màn hình quản trị cũ chỉ phát lại các file đó, nên thực tế vận hành tải được dữ liệu từ nhiều năm trước.

Hệ mới (F-AD-09 データダウンロード) bỏ hẳn kiểu "làm file sẵn": sinh file theo yêu cầu từ DB, và DB xoá theo TTL — tức **TTL trở thành giới hạn trên của việc tải ngược** (spec I-A-07 cấm chọn kỳ trước 保持期間). Bản nháp spec [I] đặt 保持期間 24 tháng (T.B.D) — chính là 明確な未決事項 #2 đang 要FIX.

**Vì sao cần trả lời**: nếu nhu cầu thực > 24 tháng thì phải thiết kế thêm cơ chế archive dài hạn (S3) trước khi chốt spec; con số này quyết định thẳng giá trị TTL DynamoDB, chi phí lưu trữ, và kế hoạch xử lý kho ZIP đã tích luỹ trên máy chủ hiện hành khi cắt chuyển.

**Điểm thắc mắc**

1. Thực tế nghiệp vụ cần tải ngược tối đa bao xa cho từng loại dữ liệu quá khứ (機器状態情報/1時間値/1日値/1日値（平均）)? 24 tháng có đủ không?
2. Có nghĩa vụ audit / bảo hành thiết bị / quy định nội bộ nào đòi giữ quá 24 tháng không?
3. Các ZIP quá khứ đã tích luỹ trên máy chủ hiện hành: sau khi chuyển hệ có cần tiếp tục tham chiếu không — nếu có thì di chuyển sang hệ mới hay giữ tra cứu ở môi trường cũ?

**Nguồn nội bộ**: `summary_batch_migration_ja.md:59-62` ・ `eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md:14-19` (要FIX), `:34` (I-A-07), `:41-52` (24ヶ月 T.B.D) ・ `submit_folder/2026_08_12/legacy-batch_CreateCsvAndZipConDeviceStatuses_vi.md:63-71, 160-175` ・ `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:47,49,53-54`

---

### 🇯🇵 【JP】過去データダウンロードの必要遡及期間についてご確認をお願いいたします

**調査の背景**

現行EMINELの管理画面「データダウンロード」の過去データ4種（機器状態情報／1時間値／1日値／1日値（平均値））の仕組みを調査いたしました。現行システムでは、データベース本体の保持期間は短い（機器状態情報8日・1時間値14日・1日値／1日値（平均値）2ヶ月）ものの、削除前に週次・月次のZIPファイルとしてサーバー上へ退避し、退避済みZIPには削除処理が存在しないため、**実質的には数年前のデータでも取得可能**な状態と理解しております。

新システム（E-GW管理画面 データダウンロード F-AD-09）では、ファイルの作り置きは行わず、管理者が期間を指定した時点でデータベースからファイルを生成する方式を予定しております。この方式では**データベースの保持期間がそのまま遡及可能な上限**となり、現時点の機能仕様案では保持期間を24ヶ月（T.B.D）と仮置きしております。仮に24ヶ月を超える遡及が必要な場合は、長期保管（アーカイブ）の仕組みを別途設計する必要があるため、本項目の確定が仕様確定の前提となっております。

**確認したい点**

1. 過去データのダウンロードは、実務上、最大でどの程度過去まで遡る必要がありますでしょうか（データ種別により異なる場合は種別ごとにご教示ください）。**24ヶ月で十分でしょうか。**
2. 監査対応・機器保証対応など、24ヶ月を超える保存が求められる社内規程・業務要件はございますでしょうか。
3. 現行サーバーに蓄積済みの過去分ZIPファイルについて、新システム移行後も参照が必要でしょうか。必要な場合、新システムへ移行するか、現行環境側で保管を継続するか、ご意向をご教示ください。

本項目はデータベースの自動削除設定（保持期間）とストレージ費用、および移行計画に直結するため、早期のご確認をお願いしたく存じます。

**参照資料**

- 管理画面 機能仕様「I データダウンロード」—「明確な未決事項」2（各種データの保持期間）、別表①「データ保持期間」列
- 現行EMINEL 管理画面「データダウンロード」— 過去データ4種（機器状態情報／1時間値／1日値／1日値（平均値））
- 現行EMINEL設計資料「データ削除と過去データCSV作成仕様」

---
---

## Q-BATCH-02 — Ai đang dùng 4 loại file dữ liệu quá khứ, và có hệ thống nào đọc file bằng máy không? (chốt 対象データ種別 + format)

**Ưu tiên**: chặn việc ・ **Gửi tới**: 北ガス (qua mui) ・ **Phản biện**: đạt, gửi nguyên trạng

**Bối cảnh điều tra**

4 loại file quá khứ hệ cũ có format rất đặc thù của bản cài đặt hiện hành: 機器状態情報 264 cột (128+128 mã EPC ECHONET nằm ngang), 1時間値 24 cột giờ nằm ngang, 1日値 31 cột ngày nằm ngang; CSV là UTF-8 có BOM; tên file trong ZIP mã hoá Shift_JIS.

Hệ mới đang định nghĩa lại cả danh mục loại dữ liệu (要FIX #1) lẫn layout (別表② của spec [I] chuyển sang kiểu dọc: mỗi dòng một mốc thời gian với cột 値/単位). Nhánh quyết định: nếu tồn tại công cụ/hệ thống downstream parse file theo format cũ → phải giữ tương thích hoặc lập kế hoạch chuyển đổi; nếu chỉ người mở bằng Excel → được tự do thiết kế lại. Điều tra code chỉ nhìn thấy đến "màn hình cho tải ZIP", hoàn toàn không biết sau đó file đi đâu — chỉ 北ガス trả lời được.

**Điểm thắc mắc**

1. Từng loại trong 4 loại dữ liệu quá khứ: phòng ban nào dùng, cho nghiệp vụ gì, tần suất bao nhiêu? Loại nào hầu như không dùng?
2. Có quy trình đọc file bằng máy (nạp vào hệ thống khác, tool tự động tổng hợp) không? Nếu có, những điểm nào của format phải giữ nguyên (cấu trúc cột, mã ký tự, tên file)?
3. Nếu hệ mới đổi layout (ví dụ 1時間値 từ 24 cột ngang sang kiểu dọc theo mốc giờ) thì có gây trở ngại nghiệp vụ nào không?

**Nguồn nội bộ**: `submit_folder/2026_08_12/legacy-batch_CreateCsvAndZipConDeviceStatuses_vi.md:104-122` (264 cột), `:133-139` (BOM), `:179-193` (SJIS) ・ `legacy-batch_CreateCsvAndZipConSensorHourlyValues_vi.md:104-121` (24 cột ngang) ・ `eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md:52, 147-167` (format dọc 値/単位)

---

### 🇯🇵 【JP】過去データダウンロードのご利用実態（利用部署・用途・後続処理）についてご教示ください

**調査の背景**

現行EMINELの過去データ4種（機器状態情報／1時間値／1日値／1日値（平均値））は、バッチが週次・月次で作成したファイルをそのまま配布する方式であり、ファイル仕様も現行実装固有のもの（機器状態情報は264列、1時間値は24時間分を横並びの24列で持つ形式、CSVはBOM付きUTF-8、ZIP内ファイル名はShift_JISエンコード）となっております。

新システムのデータダウンロードでは、対象データ種別および列構成の見直し（例：時刻ごとの縦持ち形式への変更）を検討しております。ダウンロードしたファイルを**機械的に処理する後続の仕組みが存在する場合**は現行形式との互換性維持が制約となり、**人が閲覧する用途のみの場合**は新形式へ自由に再設計できるため、ご利用実態が対象種別・ファイル形式の設計判断の分岐点となります。

**確認したい点**

1. 過去データ4種は、それぞれどの部署・どのような業務で、どの程度の頻度でご利用でしょうか。ほとんど利用されていない種別がございましたら、あわせてご教示ください。
2. ダウンロードしたファイルを他システムへ取り込む・ツールで自動処理する等の後続処理はございますでしょうか。ある場合、維持が必要な仕様（列構成・文字コード・ZIP内ファイル名形式等）をご教示いただけますでしょうか。
3. 列構成を見直した場合（例：1時間値の24列横持ち→時刻ごとの縦持ちへの変更）、業務に支障はございますでしょうか。

本項目は、新システムのダウンロード対象データ種別およびファイル仕様の確定に必要なため、ご確認をお願いしたく存じます。

**参照資料**

- 現行EMINEL 管理画面「データダウンロード」— 過去データ4種
- 管理画面 機能仕様「I データダウンロード」— 別表①②（ダウンロードファイル種別・種別ごとのファイルデータ）

---
---

## Q-BATCH-03 — 別表① của spec [I] không có loại tương đương 機器状態情報 và 1日値（平均） — chủ ý bỏ hay chưa整理?

**Ưu tiên**: chặn việc ・ **Gửi tới**: mui ・ **Phản biện**: sửa nhẹ 参照資料 (đã áp), kèm ghi chú nội bộ về 265列

**Bối cảnh điều tra**

Đối chiếu 4 loại download quá khứ hệ cũ với 別表① của spec [I]: 1時間値/1日値 được cover bởi 「連携機器別計測値集計データ」 (giữ 24 tháng nên không cần loại "quá khứ" riêng), nhưng 2 loại còn lại **không** có loại tương đương: ① 機器状態情報 (`t_202` — dump thô 264 cột, 128+128 EPC ECHONET của node/thiết bị); ② 1日値（平均） (`s_113` — trung bình nhóm theo 機器種別×設置場所×5 thuộc tính nhóm, không có cột EMS-SP, do `CalcCommonAverageDataCommand` tính).

別表① có 「GW・連携デバイスデータ」 (E-GW台帳・接続機器台帳) trông như hậu duệ của ① nhưng chỉ là ledger snapshot, không phải time-series mức EPC. ② thì dính F-ES-12 グルーピング và nhóm batch 集計・計算系 chưa điều tra.

**Vì sao cần trả lời**: 要FIX #1 (対象データ種別) không thể chốt khi chưa rõ 2 khoảng trống này là quyết định hay sơ suất; riêng ① còn phụ thuộc câu hỏi firmware — gateway mới Aqara M300 có thu/lưu dữ liệu mức EPC tương đương `t_202` không; nếu dữ liệu nguồn không tồn tại thì loại download này tự khắc bất khả thi và cần nói rõ với khách.

> *Ghi chú nội bộ (không gửi kèm nguyên văn, nhưng nên báo mui cùng lúc): mục tham khảo của spec [I] dòng 272 ghi 「機器状態情報（265列／t_202）」 nhưng danh sách cột ngay dưới cộng lại là **264** (khớp code batch: 7+128+128+1) — đề nghị mui sửa spec để khỏi vênh số khi chuyển cho khách.*

**Điểm thắc mắc**

1. Việc 別表① không chứa 2 loại trên là chủ ý (hệ mới không cung cấp) hay chưa được xét đến?
2. Về 機器状態情報: E-GW (Aqara M300) có kế hoạch thu thập/lưu dữ liệu trạng thái thiết bị mức EPC ECHONET Lite không? Nếu không, hiểu rằng 「GW・連携デバイスデータ」 là bản thay thế thực chất — đúng không?
3. Về 1日値（平均）: việc quyết định có đưa dữ liệu trung bình nhóm (liên quan F-ES-12) vào download hay không sẽ treo lại chờ điều tra nhóm batch 集計・計算系 (`CalcCommonAverageDataCommand`…) — cách tiến hành như vậy có đúng ý mui không?

**Nguồn nội bộ**: `eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md:39-52` (別表①), `:127-169` (別表②), `:272` (265列 — vênh) ・ `submit_folder/2026_08_12/legacy-batch_CreateCsvAndZipConSensorDailyAveValues_vi.md:7, 113-115, 186-190` ・ `legacy-batch_CreateCsvAndZipConDeviceStatuses_vi.md:104-122` ・ `summary_batch_migration_ja.md:59, 61`

---

### 🇯🇵 【JP】データダウンロード仕様 別表①：「機器状態情報」「1日値（平均）」相当種別の扱いについてご確認をお願いいたします

**調査の背景**

旧システムのCSV/ZIPエクスポート系バッチ4本（`CreateCsvAndZipCon{DeviceStatuses, SensorHourlyValues, SensorDailyValues, SensorDailyAveValues}Command`）の調査が完了いたしました。旧管理画面「過去データ」4種のうち、1時間値・1日値は新仕様書（[I] データダウンロード）別表①の「連携機器別計測値集計データ」（保持期間24ヶ月）で実質的にカバーされると理解しております。一方、以下の2種は別表①に相当種別が見当たりませんでした。

- **機器状態情報**（`t_202`）: ECHONET Lite の EPC 80〜FF を横持ちした264列の生データ（ノード128列＋機器128列。`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConDeviceStatusesCommand.php:84-145`）
- **1日値（平均）**（`s_113`）: 機器種別×設置場所×グループ属性5項目ごとのグループ平均値（EMS-SP列なし）。平均値の算出は集計系バッチ `CalcCommonAverageDataCommand` が担当（`conciergesv-develop/src/Command/CalcCommonAverageDataCommand.php:1283`）

**確認したい点**

1. 上記2種が別表①に含まれていないのは、**意図的な整理（新システムでは提供しない）**でしょうか、それとも**未整理**でしょうか。要FIX事項「E-GWでダウンロード対象とするデータ種別」の確定に必要なため、ご教示いただけますでしょうか。
2. 機器状態情報について：新GW（Aqara M300）経由で ECHONET Lite EPC レベルの機器状態データを収集・保存する計画はありますでしょうか。収集しない場合、別表①の「GW・連携デバイスデータ」（E-GW台帳・接続機器台帳）が実質的な後継、という理解でよろしいでしょうか。
3. 1日値（平均）について：グループ平均データ（F-ES-12 グルーピング関連）のダウンロード要否は、集計・計算系バッチ（`CalcCommonAverageDataCommand` 等）の調査完了後に判断する、という進め方でよろしいでしょうか。

**参照資料**

- `eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md` —「明確な未決事項」1、別表①・別表②
- バッチ移行調査 総括表 `summary_batch_migration_ja.md`（別途お渡し分）— CSV/ZIPエクスポート系4行
- 調査報告書 `legacy-batch_CreateCsvAndZipConDeviceStatuses_ja.md`・`legacy-batch_CreateCsvAndZipConSensorDailyAveValues_ja.md`（別途お渡し分）

---
---

## Q-BATCH-04 — Mùng 1 hai batch hằng ngày khởi động 2 lần (flock không chặn được) — file production có bị lặp dòng thật không?

**Ưu tiên**: nên hỏi sớm (chốt trước khi giao bộ báo cáo điều tra) ・ **Gửi tới**: mui ・ **Phản biện**: sửa tiêu đề + thêm câu nhờ chuyển vận hành + sửa 参照資料 (đã áp)

**Bối cảnh điều tra**

Cron hệ cũ đặt `_day1.sh` (`15 5 1 * *`) và `_day2to31.sh` (`15 5 * * *` — tên gây hiểu nhầm, thực chất chạy **mọi** ngày) cùng nổ 05:15 mùng 1. Hai batch hằng ngày (DeviceStatuses, HourlyValues) nằm trong **cả hai** shell nên riêng mùng 1 khởi động 2 lần. `flock` chỉ khoá chính file script (`$0`) nên không chặn được 2 script khác tên chạy song song; CSV lại mở `fopen` mode `'a'` (ghi tiếp) → dữ liệu ngày đích có thể bị ghi 2 lần vào file tuần. Ở mức code, hai lần chạy trọn vẹn tất yếu ghi trùng; điều **chưa kiểm chứng** là hành vi thực tế trên môi trường thật (race khi ghi đồng thời, sự cố vận hành, cơ chế chặn ngoài repo).

**Vì sao cần trả lời**: (a) nếu kho ZIP hiện hành có lặp dòng thì mọi thảo luận "giữ/di chuyển archive cũ" (Q-BATCH-01) phải tính bước làm sạch; (b) cần chốt trước khi giao tài liệu điều tra cho khách để khỏi khẳng định quá tay một defect chưa kiểm chứng.

**Điểm thắc mắc**

1. Trên môi trường thật, dữ liệu của lần chạy mùng 1 có bị xuất trùng 2 lần vào CSV tuần không (kiểm được bằng trùng dòng trong CSV của ZIP đã tích luỹ)?
2. Đây có phải issue đã biết không? Vận hành có thao tác xử lý (lọc trùng khi dùng…) nào không?
3. Nếu có xảy ra, xin chia sẻ làm tiền đề cho việc bàn cách xử lý archive cũ khi chuyển hệ (độ tin cậy dữ liệu).

**Nguồn nội bộ**: `submit_folder/2026_08_12/legacy-batch_CreateCsvAndZipConDeviceStatuses_vi.md:42, 55-59, 73-75` ・ `legacy-batch_CreateCsvAndZipConSensorHourlyValues_vi.md:55-59, 73` ・ `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:40-41`

---

### 🇯🇵 【JP】旧システム：毎日実行のCSVエクスポートバッチが毎月1日に二重起動となる件（出力への影響は実環境未確認）

**調査の背景**

cron設定（`legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:40-41`）では、`12_CreateCsvAndDeleteData_day1.sh`（`15 5 1 * *`）と `12_CreateCsvAndDeleteData_day2to31.sh`（`15 5 * * *`）が**毎月1日の05:15に同時起動**します。`_day2to31.sh` は名称に反して日付フィールドが `*`（毎日実行）のため、両シェルに含まれる `CreateCsvAndZipConDeviceStatuses`・`CreateCsvAndZipConSensorHourlyValues` は毎月1日に限り2回実行されると読み取れます。

シェルの排他制御は `flock` で自スクリプト（`$0`）をロックする方式のため、**ファイルパスの異なる2本の同時起動は排他できません**。CSVは追記モード（`fopen(..., 'a')`）で開かれるため、対象日（1日実行分＝前月下旬のデータ）が週次CSVへ**二重に書き込まれる可能性**があると推測しております。ただしこれはコードからの推測であり、実環境では未確認です。

**確認したい点**

1. 本番環境において、毎月1日実行分のデータがCSVへ二重出力される事象は実際に発生していますでしょうか（蓄積済みZIP内のCSVの行重複でご確認いただけますでしょうか）。
2. 既知の事象として認識されている場合、運用上の対処（利用時の重複除去等）があればご教示ください。
3. 発生している場合、蓄積済み過去分アーカイブのデータ信頼性に関わるため、新システム移行時の過去データ取り扱い（移行・参照）検討の前提情報として共有いただきたく存じます。

なお、実環境の確認が運用ご担当（貴社外）への依頼となる場合は、お取り次ぎいただけますと幸いです。

**参照資料**

- `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:40-41`
- 同 `cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` 内 `12_CreateCsvAndDeleteData_day1.sh`／`12_CreateCsvAndDeleteData_day2to31.sh`（`flock -n` / `fopen(..., 'a')` の該当箇所）
- 調査報告書 `legacy-batch_CreateCsvAndZipConDeviceStatuses_ja.md`・`legacy-batch_CreateCsvAndZipConSensorHourlyValues_ja.md`（別途お渡し分、毎月1日の二重起動の節）

---
---

## Q-BATCH-05 — Cột `c008` (消費電力量遡及フラグ) của `s_102`: được 4 batch ghi nhưng không nơi nào đọc — có bên nào ngoài repo tham chiếu không?

**Ưu tiên**: dự phòng (gửi kèm dịp trao đổi mui) ・ **Gửi tới**: mui ・ **Phản biện**: ĐÃ VIẾT LẠI (tiền đề cũ "không ai đọc/ghi" sai — c008 **được ghi** bởi 4 batch; định nghĩa giá trị có trong comment migration)

**Bối cảnh điều tra**

Cột `c008` của `s_102` xuất hiện trong CSV với header 「消費電力量遡及フラグ」. Khác với mô tả trong báo cáo điều tra đã nộp (cần sửa), thực tế:

- **Định nghĩa giá trị có sẵn** trong comment migration: `1:遡及あり, 2:遡及なし` (`eminelsv-develop/config/Migrations/20230807080522_InitialMigration.php:1699`; lặp lại ở `20240418015721_ChangeToPartitionTable.php:1147, 1245`).
- **Được GHI** bởi 4 batch production qua setter `setNeedEleCompleteFlag()` (`ConSensorHourlyValue.php:194-197`): `CalcDailyAccumulatedValueCommand.php:273, 671` (logic 1/2 ở `:242-256` — 遡及あり cho ガス発電/太陽光/買電/売電/蓄電池, 遡及なし cho 人感検知回数), `CalcDailyEnergyConsumptionCommand.php:225, 523`, `CalcDailyRoomTemperatureCommand.php:499, 526`, `RcvHalfHourElectricPowerCommand.php:901, 974`.
- Nhưng **không nơi nào ĐỌC**: `getNeedEleCompleteFlag` 0 caller, không WHERE nào dùng `c008`, chỉ được dump nguyên trạng ra CSV — cột **write-only** trong phạm vi 2 repo.

Trái ngược với cờ chị em `c009` (集計遡及フラグ) có vòng đời đọc–ghi đầy đủ 1→2 (`CalcMonthlyAccumulatedValueCommand.php:220` lọc `=1`, `:213` đặt `=2`).

**Vì sao cần trả lời**: hệ mới phải làm mới bảng + luồng tính giá trị giờ (kết luận điều tra `CalcTenMinutesEnergyCommand` — `summary_batch_migration_ja.md:34`); cần quyết có tạo cờ tương đương cho việc hồi tố lượng điện hay bỏ hẳn — bỏ nhầm một cờ đang có consumer ngoài repo sẽ phá luồng hồi tố dữ liệu điện.

**Điểm thắc mắc**

1. Có process nào **ngoài repo** (tool vận hành, hệ tổng hợp khác, truy vấn tay) tham chiếu `c008` không, hay đây là cột có bên ghi mà chưa bao giờ có bên đọc?
2. Nếu không có nơi tham chiếu: hệ mới dự định không tạo cột tương đương — xin ý kiến, kèm đánh giá việc 洗い替え bằng giá trị điện chốt (tương đương Xzilla連携) có cần cờ kiểu này không.

**Nguồn nội bộ**: `legacy_eminel_docs/sources/eminelsv-develop/config/Migrations/20230807080522_InitialMigration.php:1699` ・ `eminel_sv_lib-develop/src/Model/Entity/ConSensorHourlyValue.php:57, 100, 189, 194-197` ・ `conciergesv-develop/src/Command/CalcDailyAccumulatedValueCommand.php:242-273` ・ ⚠️ báo cáo `legacy-batch_CreateCsvAndZipConSensorHourlyValues_{ja,vi}.md` mục 2.2 hàng c008 **phải sửa trước khi giao** (hiện ghi "không có code nào đọc hay ghi" — sai vế "ghi")

---

### 🇯🇵 【JP】旧システム：`s_102` の列 `c008`（消費電力量遡及フラグ）の参照元についてご確認をお願いいたします

**調査の背景**

日毎センサ情報 `s_102` の列 `c008` は、CSVヘッダ上「消費電力量遡及フラグ」と表記され、値の定義はマイグレーションのカラムコメントに現存します（`legacy_eminel_docs/sources/eminelsv-develop/config/Migrations/20230807080522_InitialMigration.php:1699` —「1:遡及あり, 2:遡及なし」）。

本列の値は日次集計系バッチが設定しています（`conciergesv-develop/src/Command/CalcDailyAccumulatedValueCommand.php:273, 671`・`CalcDailyEnergyConsumptionCommand.php:225, 523`・`CalcDailyRoomTemperatureCommand.php:499, 526`・`RcvHalfHourElectricPowerCommand.php:901, 974`）。一方、本列を**参照（読み取り）する処理が `conciergesv-develop`／`eminel_sv_lib-develop` の両リポジトリ内に見当たりませんでした**（アクセサ `getNeedEleCompleteFlag` の呼び出し0件、WHERE句での使用0件、CSVエクスポート時の単純出力のみ）。

類似列 `c009`（集計遡及フラグ）には「1＝要再集計 → 2＝反映済み」の参照・更新サイクルが実装されている（`CalcMonthlyAccumulatedValueCommand.php:220, 213`）のと対照的です。

新システムでは時間値データのテーブルと計算フローを新規に設計する必要があるため、電力量の遡及（確定値による洗い替え）に相当する仕組みの要否を判断する材料として、本列の参照元の有無を確認したい状況です。

**確認したい点**

1. `c008` を参照する処理は、リポジトリ外（運用ツール・外部集計・手動クエリ等）に存在しますでしょうか。それとも、設定側のみ実装され参照側が未実装のまま残った列でしょうか。
2. 参照実績がない場合、新システムの時間値データ設計では相当列を設けない方針としたいと考えております。確定電力量（Xzilla連携相当）による洗い替えの要否とあわせて、ご意見をいただけますでしょうか。

**参照資料**

- `legacy_eminel_docs/sources/eminelsv-develop/config/Migrations/20230807080522_InitialMigration.php:1699`
- `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorHourlyValue.php:57, 100, 189, 194-197`
- `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CalcDailyAccumulatedValueCommand.php:242-273`
- `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CalcMonthlyAccumulatedValueCommand.php:213, 220`（対照例 `c009`）

---
---

# Phụ lục — chủ đề đã cân nhắc nhưng KHÔNG đưa vào bảng hỏi

| Chủ đề | Vì sao không hỏi |
|---|---|
| Hệ mới giữ/cung cấp dữ liệu trung bình nhóm `s_113` thế nào (F-ES-12) | Phần download đã gộp vào Q-03 điểm 3; tiêu chí gom nhóm thì `qa_kitagas.md` Câu 8 **đã hỏi khách**; phần tính toán phụ thuộc `CalcCommonAverageDataCommand` thuộc nhóm 集計・計算系 **chưa điều tra** (hàng `—` trong summary) — hỏi bây giờ là hỏi non |
| Con số TTL cụ thể cho DynamoDB | Là **hệ quả** thiết kế sau khi có trả lời Q-01 của khách; hỏi mui trước khi có input nghiệp vụ là ngược quy trình (spec [I] cũng đang để 24ヶ月 T.B.D chờ chính input này) |
| Vì sao `s_102` CSV hoá ở mốc −8 ngày dù DB giữ 14 ngày (đệm 7 ngày có chủ ý?) | Tò mò lịch sử thiết kế hệ cũ; hệ mới thay toàn bộ cơ chế bằng TTL + PITR nên câu trả lời không đổi quyết định nào |
| Các suy đoán nhỏ 🔸: lý do lọc thêm `c004` ở DailyValues, lý do BOM UTF-8, lý do SJIS, tên biến `$conSensorDailyValues` trỏ `s_113` | Mức chú thích "vì sao code viết vậy", không ảnh hưởng quyết định hệ mới (khía cạnh tương thích format đã được Q-02 hỏi theo hướng nghiệp vụ); gom hỏi miệng mui khi có dịp |

# Việc kèm theo TRƯỚC khi gửi (từ kết quả review + phản biện)

1. **Sửa mô tả `c008`** trong `legacy-batch_CreateCsvAndZipConSensorHourlyValues_{ja,vi}.md` mục 2.2 (hiện ghi "không có code nào đọc hay ghi" — sai vế "ghi") **trước khi giao bộ báo cáo cho mui** — Q-03/Q-04 dẫn chính các báo cáo này. ⚠️ `submit_folder/` là bản nộp không sửa ngược → cần user quyết hình thức (bản vá mới / errata).
2. **Sửa câu lặp** ở `summary_batch_migration_ja.md:62` (「新システムでは保持期間の設計そのものをTTLで置き換える。」 ×2).
3. **Báo mui vênh 264/265**: spec [I] `I_data_download.md:272` ghi 265列 cho 機器状態情報 nhưng danh sách cột + code đều ra 264 (gộp khi gửi Q-03).
