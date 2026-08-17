# batch_decision（Markdown版・修正版）

> **【メンバーの作業】要修正シート（7件）の新しい結論文を、xlsx の該当セルへ貼り付けてください（下表からコピーできます）。**

> **BẢN ĐÃ SỬA THEO REVIEW 16–17/08** — sheet 要修正 đã thay câu kết luận (đã qua đối kháng); các sheet khác giữ nguyên văn. Sheet đã sửa: CalcTenMinutesSensorCommand、CalcDailyAccumulatedValueCommand、CalcDailyEnergyConsumptionCommand、CalcDailyRoomTemperatureCommand、CalcMonthlyAccumulatedValueCommand、CalcYearlyAccumulatedValueCommand、CalcWeeklySavingReportUsingCommand. Bản gốc trung thực với xlsx: `../batch_decision.md`.

> **Verdict 19/19 sheet**: **要修正 7** (7 sheet nêu trên — đã thay câu, dán thẳng vào xlsx được) ・ **妥当だが根拠不足 12** (giữ nguyên văn; kết luận của member đúng nhưng chưa dẫn đủ căn cứ). Trong nhóm 根拠不足: 3 sheet có sẵn văn bản JP đề xuất **chưa áp** — `CalcYearlyRoomTemperatureCommand` (câu thay thế) ・ `CalcDailyAverageDataCommand` và `CalcWeeklySavingReportEffectCommand` (câu nối thêm vào cuối câu hiện tại) — xem 付録 cuối file; 9 sheet còn lại không có văn bản soạn sẵn (lý do ở `../../review_summary.md` §3.G1) ・ `CalcCarbonDioxideEmissionsCommand` có câu hỏi nghiệp vụ **QA-01②** (`../../../qa/qa_review_20260813_20260817.md` — **CHƯA GỬI**). Nhóm không có sheet 妥当 hay 要業務確認.

> Bản Markdown convert máy móc 1-1 từ `../batch_decision.xlsx` (thư mục nhóm) — nội dung convert giữ nguyên từng ô (không dịch); riêng câu kết luận các sheet nêu ở ghi chú trên đã thay theo review. Ngày convert: 2026-08-16 ・ số sheet: 19.

## 1. CalcTenMinutesSensorCommand

| Batch | CalcTenMinutesSensorCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcTenMinutesSensor_ja.md |
| 現行のEminel Smartシステムの調査結果： | 10分値の人感検知差分を算出する再利用可能なバッチは存在しません（Eminel Smartではmuiセンサーが人感をイベント（motion=1）として送信するため、積算カウンタの差分算出が不要な方式）。ただし関連ロジックとして、batch-receive-data-infrared-remote がmotionイベントを InfraredRemoteDataTable に取り込み（motion=1時は見守り系Push通知フラグを設定）、API get-motion-detect-data-for-user が30分単位の検知回数集計を行っています。新システムで必要な人感10分値グラフ（F-ES-01）・見守り通知（F-ES-05）について、既存イベント方式の流用か、10分値集計の新規追加か（マルチセンサーI/F IF-08 が旧システム同様に積算値を返す場合は差分ロジックの新設）の設計判断が必要です。 |

## 2. CalcTenMinutesEnergyCommand

| Batch | CalcTenMinutesEnergyCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcTenMinutesEnergy_ja.md |
| 現行のEminel Smartシステムの調査結果： | current-eminelsmart_CalcTenMinutesEnergy_ja.md |

## 3. CalcDailyAccumulatedValueCommand

| Batch | CalcDailyAccumulatedValueCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcDailyAccumulatedValueCommand_ja.md<br>legacy-batch_CalcDailyAccumulatedValueCommand.md |
| 現行のEminel Smartシステムの調査結果： | 本バッチの「生の積算値（t_202）から1時間値を差分算出するロジック」そのものは、現行Eminel Smartには存在しない。ただしEminel Smart側には積算系データの受け皿として DeviceAccumulatedHistoryTable／DeviceDailyUsageHistoryTable／DeviceMonthlyUsageHistoryTable（template-dynamodb.yaml:1113/1145/1177）が存在し、batch-import-rinnai-sensor-data／batch-import-noritz-sensor-data／batch-import-rinnai-daily-usage／batch-import-noritz-hourly-usage／batch-import-rinnai-monthly-usage の5本のLambdaが、リンナイ／ノーリツ側で算出済みの使用量データをそのまま取り込む構成である（サーバー側での差分計算は行わない）。太陽光発電・ガス発電・売買電・蓄電池・人感の1時間値に相当するデータ・算出ロジックはどちらにも存在しないため、E-GWのグラフ（F-ES-01）・リアルタイムモニタ（F-ES-15）が必要とする1時間値・1日値・1月値（消費電力量＝太陽光発電電力量＋ガス発電電力量＋蓄電池放電量−蓄電池充電量＋買電量−売電量）をどこで生成するか（GWからの送信値／Xzillaの電力30分値／サーバー側での新規実装）の設計判断が別途必要。 |

## 4. CalcDailyAverageDataCommand

| Batch | CalcDailyAverageDataCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcDailyAverageData_ja.md<br>legacy-batch_CalcDailyAverageData.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 5. CalcDailyEnergyConsumptionCommand

| Batch | CalcDailyEnergyConsumptionCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcDailyEnergyConsumption_ja.md<br>legacy-batch_CalcDailyEnergyConsumption.md |
| 現行のEminel Smartシステムの調査結果： | Eminel Smart側に、本バッチをそのまま再利用できるバッチは存在しません。ただし関連する仕組みとして、Rinnai/Noritzクラウドから算出済みの時間・日・月の使用量データを取り込むLambda（batch-import-rinnai-*／batch-import-noritz-*）と、その格納先3テーブル（DeviceAccumulatedHistoryTable／DeviceDailyUsageHistoryTable／DeviceMonthlyUsageHistoryTable）が存在します（ガスの時間値は算出済みで受領するため、本バッチのガス10分値→時間値集約に相当する処理は不要になる可能性があります）。一方、本バッチの消費電力量算出（太陽光発電＋ガス発電＋蓄電池放電−蓄電池充電＋買電−売電）に相当するロジックはEminel Smart側に存在せず、統合要件v1.2（F-ES-01:582行、F-ES-15）では同一の計算式による算出が26年スコープで要求されているため、新システム側で新規に実装する必要があります（本バッチの計算式が参照実装となります）。 |

## 6. CalcDailyRoomTemperatureCommand

| Batch | CalcDailyRoomTemperatureCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcDailyRoomTemperature_ja.md<br>legacy-batch_CalcDailyRoomTemperature.md |
| 現行のEminel Smartシステムの調査結果： | 本バッチと同等の1時間平均室温を算出するバッチ・ロジックは、現行Eminel Smartには存在しません（backend内に平均算出処理は無し）。ただし、室温・湿度データの取り込み・提供パイプラインは既に存在します：muiセンサーのSENSOR_AUTO_REPORTイベント（temperature／humidity／motion）をbatch-receive-data-infrared-remoteが受信してInfraredRemoteDataTableへ生値のまま保存し、get-temp-and-humid-for-user APIが時系列データとしてアプリへ返却しています（集計なし）。新システムの要件F-ES-01（室温グラフ：時刻別/日別/月別、日値・月値は平均値あり）を満たすには、この生値を集計する処理（本バッチの1時間平均算出に相当）を新規に設計・実装する必要があります。 |

## 7. CalcMonthlyAccumulatedValueCommand

| Batch | CalcMonthlyAccumulatedValueCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcMonthlyAccumulatedValueCommand_ja.md<br>legacy-batch_CalcMonthlyAccumulatedValueCommand.md |
| 現行のEminel Smartシステムの調査結果： | 旧CalcMonthlyAccumulatedValueCommandのように時間値（s_102）から日値を集計して月次行（s_103）を組み立てるバッチ、および同等の集計ロジックはEminel Smartには存在しません。ただし月次使用量データの受け皿と取込フローは存在します。DeviceMonthlyUsageHistoryTable（template-dynamodb.yaml 1177行）に、メーカー側で集計済みの前月分使用量（給湯・追いだきガス使用量等）をbatch-import-rinnai-monthly-usageが格納しています（日値はDeviceDailyUsageHistoryTable＋batch-import-rinnai-daily-usage／batch-import-noritz-hourly-usage）。したがってガス機器系の月値はメーカー連携で取得済みの値を利用可能ですが、電力系（消費電力・売買電・蓄電池・発電）の月次集計に相当する仕組みは存在せず、新システムの月値グラフ・レポート（F-ES-01／F-ES-02、26年スコープ）に必要な電力系月値の生成手段（Xzilla電力30分値からの集計、TagTagとの分担範囲を含む）は新規に検討が必要です。 |

## 8. CalcMonthlyAverageDataCommand

| Batch | CalcMonthlyAverageDataCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcMonthlyAverageData_ja.md<br>legacy-batch_CalcMonthlyAverageData.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 9. CalcMonthlyAverageSetTemperatureCommand

| Batch | CalcMonthlyAverageSetTemperatureCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcMonthlyAverageSetTemperatureCommand_ja.md<br>legacy-batch_CalcMonthlyAverageSetTemperatureCommand.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 10. CalcMonthlyRoomTemperatureCommand

| Batch | CalcMonthlyRoomTemperatureCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcMonthlyRoomTemperature_ja.md<br>legacy-batch_CalcMonthlyRoomTemperature.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 11. CalcYearlyAccumulatedValueCommand

| Batch | CalcYearlyAccumulatedValueCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcYearlyAccumulatedValueCommand_ja.md<br>legacy-batch_CalcYearlyAccumulatedValueCommand.md |
| 現行のEminel Smartシステムの調査結果： | 本バッチと同名の年次集計バッチ、および日別値から月別・年別値を算出する集計ロジックはEminel Smartに存在しません。ただし関連する仕組みとして、機器の積算値・日別・月別使用量を保持する3テーブル（DeviceAccumulatedHistoryTable／DeviceDailyUsageHistoryTable／DeviceMonthlyUsageHistoryTable）が存在し、batch-import-rinnai-*／batch-import-noritz-*のLambdaがリンナイ・ノーリツ算出済みの値をそのまま取り込んでいます。年単位のテーブルおよび年次集計ロジックは存在しないため、新アプリのC1グラフ（月値・当年／前年比較）およびC2年間レポートに必要な年間データの供給元（メーカー提供値で賄うか、月別値から年間分を集計する処理を新設するか）は別途検討が必要です。 |

## 12. CalcYearlyAverageDataCommand

| Batch | CalcYearlyAverageDataCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcYearlyAverageData_ja.md<br>legacy-batch_CalcYearlyAverageData.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 13. CalcYearlyPresetTemperatureCommand

| Batch | CalcYearlyPresetTemperatureCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcYearlyPresetTemperature_ja.md<br>legacy-batch_CalcYearlyPresetTemperature.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 14. CalcYearlyRoomTemperatureCommand

| Batch | CalcYearlyRoomTemperatureCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcYearlyRoomTemperature_ja.md<br>legacy-batch_CalcYearlyRoomTemperature.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 15. CalcCommonAverageDataCommand

| Batch | CalcCommonAverageDataCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcCommonAverageData_ja.md<br>legacy-batch_CalcCommonAverageData.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 16. CalcFixedValueCommand

| Batch | CalcFixedValueCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcFixedValueCommand_ja.md<br>legacy-batch_CalcFixedValueCommand.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 17. CalcCarbonDioxideEmissionsCommand

| Batch | CalcCarbonDioxideEmissionsCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcCarbonDioxideEmissions_ja.md<br>legacy-batch_CalcCarbonDioxideEmissions.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 18. CalcWeeklySavingReportEffectCommand

| Batch | CalcWeeklySavingReportEffectCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcWeeklySavingReportEffect_ja.md<br>legacy-batch_CalcWeeklySavingReportEffect.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 19. CalcWeeklySavingReportUsingCommand

| Batch | CalcWeeklySavingReportUsingCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CalcWeeklySavingReportUsing_ja.md<br>legacy-batch_CalcWeeklySavingReportUsing.md |
| 現行のEminel Smartシステムの調査結果： | 現行Eminel Smartには、週間使用量を集計する再利用可能なバッチ・同等の週間集計ロジックは存在しません（weekly／先週／先々週／7日間で該当なし）。ただし、Rinnai・Noritz連携のインポートバッチ（batch-import-rinnai-daily-usage等）が日次・月次の使用量実績をDeviceDailyUsageHistoryTable／DeviceMonthlyUsageHistoryTable／DeviceAccumulatedHistoryTableに保持しており、週間集計（日次値7日分の合算）の材料になり得ます。なお、新システムでは週間レポート（F-ES-02：先々週との比較・日ごとの使用量表示、26年スコープ）が要件化されており、週間データの生成主体（TagTag連携か自前実装か）は統合要件上TBDのため、本バッチのロジック（7日分合算・先々週シフト・欠損チェック）は移行設計の参照対象として保持を推奨します。 |

---

## 付録：妥当だが根拠不足のシートに対する補足文【提案・未適用】

> ⚠️ **Đây KHÔNG phải câu đã chốt.** Verdict 妥当だが根拠不足 nghĩa là **kết luận của member đúng nhưng chưa dẫn đủ căn cứ** — theo quy ước đợt review, chỉ sheet 要修正 mới thay câu, nên 3 mục dưới đây **cố ý chưa được áp** vào bảng phía trên. Member tự cân nhắc dùng hay không khi cập nhật xlsx; nếu dùng thì đây là phát ngôn của member trước khách, hãy đọc lại lý do ở `../../review_summary.md` §3.G1 trước khi quyết. Chú ý phân biệt **câu thay thế** (dùng thay cả ô) với **câu nối thêm** (viết tiếp sau câu hiện tại, không xoá câu cũ).

**1. CalcYearlyRoomTemperatureCommand** — câu **THAY THẾ** đề xuất (JP, dùng thay cả ô 現行のEminel Smartシステムの調査結果：):

> 再利用可能なバッチ、または同等の集計ロジック（室温の月次平均算出）は存在しません。ただし、E-smartには赤外線リモコン経由の室温・湿度の生データ受信（batch-receive-data-infrared-remote → InfraredRemoteDataTable）とアプリ向け取得API（get-temp-and-humid-for-user）が存在します。新システム要件（F-ES-01：室温グラフ用データ生成 時刻別/日別/月別、26年スコープ）では本バッチ相当の月次平均値が引き続き必要であり、Rinnai/Noritzのように集計済み値が提供される仕組みは無いため、集計ロジックの新規実装が必要です。

**2. CalcDailyAverageDataCommand** — câu **NỐI THÊM** đề xuất (JP, viết tiếp ngay sau câu hiện tại 「再利用可能なバッチ、または同等のロジックは存在しません。」):

> （src/functions・template-dynamodb.yamlに平均値・グルーピング関連の実装は無いことを確認済み。ただし新要件ではグラフ月値の「よく似た世帯の平均」およびレポートのランキングが26年スコープに含まれるため（F-ES-02／F-ES-12）、グルーピング＋平均値算出パイプラインの新規実装が必要。なお本バッチの時間値粒度の他世帯平均は新要件では不要——時間値グラフは平均・比較を表示しない。）

**3. CalcWeeklySavingReportEffectCommand** — câu **NỐI THÊM** đề xuất (JP, viết tiếp ngay sau câu hiện tại 「再利用可能なバッチ、または同等のロジックは存在しません。」):

> ただし、新要件（統合要件v1.2 F-ES-02）ではレポートの省エネ効果について『現行コンシェルジェサーバーの計算方法を踏襲』と明記されており、その計算式は本バッチの計算式と一致する。E-smartに同等ロジックがないため、本バッチの計算式・業務定数（基準温度24℃、Q値1.6、床面積区分、ガス単価、補正係数0.7等）を踏襲元として新規実装（またはTagTag連携：統合要件のTBD 案1/案2）が必要。
