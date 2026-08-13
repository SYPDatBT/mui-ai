# 旧EMINELシステム 47バッチ → 新システム（E-GW / EMINEL-smart）移行調査 総括

<table style="width:100%; border-collapse:collapse; table-layout:fixed;">
<colgroup>
<col style="width:6%">
<col style="width:10%">
<col style="width:14%">
<col style="width:5%">
<col style="width:13%">
<col style="width:13%">
<col style="width:12%">
<col style="width:20%">
<col style="width:7%">
</colgroup>
<thead>
<tr>
<th>サーバー</th>
<th>機能グループ</th>
<th>バッチ名</th>
<th>担当</th>
<th>業務機能（旧システム）</th>
<th>新システムでの対応機能</th>
<th>結論</th>
<th>補足</th>
<th>調査結果詳細リンク</th>
</tr>
</thead>
<tbody>
<tr><td><code>hemssv</code></td><td>GW通信</td><td><code>DlLimitManagerCommand</code></td><td>mui</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>hemssv</code></td><td>GW通信</td><td><code>DlUlControllerCommand</code></td><td>mui</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>hemssv</code></td><td>GW通信</td><td><code>ErrorDeviceMailSendCommand</code></td><td>mui</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>hemssv</code></td><td>GW通信</td><td><code>LogDeleteCommand</code></td><td>mui</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcTenMinutesSensorCommand</code></td><td>SYP</td><td>10分ごとの人感センサー集計（2部屋分）</td><td>F-ES-01（人感センサーグラフ）・F-ES-05（ただいま／見守り通知）</td><td>新規追加が必要</td><td>新システムには同等の計算ロジックが存在しない。10分単位の動体検知ロジックがない</td><td><a href="https://app.notion.com/p/muilab/CalcTenMinutesSensorCommand-3b32d31d0e4080e9a14ce015f7f808a0?v=39e2d31d0e40806380d7000cdacf7c44&source=copy_link">CalcTenMinutesSensorCommand</a></td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcTenMinutesEnergyCommand</code></td><td>SYP</td><td>10分ごとのガス使用量集計（合計／給湯／暖房）</td><td>F-ES-01（ガスグラフ）・F-ES-02（レポート）・F-ES-13（欠損データ処理）・F-ES-15（リアルタイム）</td><td>新規追加が必要</td><td>現行のEMINEL-smartバックエンドはRinnai/Noritzが計算済みの値を受け取るだけで、生の積算値から自前で差分計算した実績がない — 修正対象となる既存バッチが存在せず、新規にテーブルと計算フローを作る必要がある。</td><td><a href="https://app.notion.com/p/muilab/CalcTenMinutesEnergyCommand-3b32d31d0e4080e4ac15ccf6291d8c1a?v=39e2d31d0e40806380d7000cdacf7c44&source=copy_link">CalcTenMinutesEnergyCommand</a></td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcDailyAccumulatedValueCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcDailyAverageDataCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcDailyEnergyConsumptionCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcDailyRoomTemperatureCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcMonthlyAccumulatedValueCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcMonthlyAverageDataCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcMonthlyAverageSetTemperatureCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcMonthlyRoomTemperatureCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcYearlyAccumulatedValueCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcYearlyAverageDataCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcYearlyPresetTemperatureCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcYearlyRoomTemperatureCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcCommonAverageDataCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcFixedValueCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcCarbonDioxideEmissionsCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcWeeklySavingReportEffectCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>集計・計算系</td><td><code>CalcWeeklySavingReportUsingCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>配信・通知系</td><td><code>DistributeMonthlyEcoPointsCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>配信・通知系</td><td><code>PublishRegularEcoMissionsCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>配信・通知系</td><td><code>DispatchPushMessagesCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>配信・通知系</td><td><code>ControlDrOperationCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>外部連携・受信系 (Xzilla取込)</td><td><code>RcvCntctCancellationCommand</code> (IF2249)</td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>外部連携・受信系 (Xzilla取込)</td><td><code>RcvEmsPlsCntrPayerCommand</code> (IF2264)</td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>外部連携・受信系 (Xzilla取込)</td><td><code>RcvHalfHourElectricPowerCommand</code> (IF1156)</td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>CSV/ZIPエクスポート系</td><td><code>CreateCsvAndZipConDeviceStatusesCommand</code></td><td>SYP</td><td>機器状態情報（<code>t_202</code>）の8日前パーティションを契約者ごとにCSV化し、月曜に<strong>前々週分</strong>をZIP圧縮（保持期間切れ前の退避）</td><td>F-AD-09（データダウンロード）</td><td>バッチとしては不要</td><td>新システムは「定期的にファイルを作り置き」しない。管理者が期間を指定した時点で <code>api-download</code> が <code>batch-download</code> Lambda を非同期起動しZIPを生成、S3経由の署名付きURLで配布する方式。DB側の保持は DynamoDB TTL、バックアップはPITRが担うため「退避してからDROP」の仕組み自体が不要。ただしE-GWの保持期間・対象データ種別は spec [I]（データダウンロード 機能仕様）で要FIX。<strong>根拠：e-smart backend の <code>api-download</code> / <code>batch-download</code> 調査分（本行の判定は旧システム調査書の範囲外）</strong></td><td><a href="https://app.notion.com/p/muilab/CreateCsvAndZipConDeviceStatusesCommand-3b92d31d0e4080579bf7dfa547263f60?v=39e2d31d0e40806380d7000cdacf7c44&source=copy_link">CreateCsvAndZipConDeviceStatusesCommand</a></td></tr>
<tr><td><code>conciergesv</code></td><td>CSV/ZIPエクスポート系</td><td><code>CreateCsvAndZipConSensorDailyValuesCommand</code></td><td>SYP</td><td>月毎センサ情報（<code>s_103</code>）の前々月パーティションを契約者ごとにCSV化し毎回ZIP圧縮（31日分が横持ち）</td><td>F-AD-09（データダウンロード）</td><td>バッチとしては不要</td><td>同上。本バッチは同一シェル内で「前々月をCSV/ZIP化 → 同じ前々月をDROP」を連続実行しており、退避と削除が一体。新システムにはこの前提（月次パーティションのDROP）自体が無い</td><td><a href="https://app.notion.com/p/muilab/CreateCsvAndZipConSensorDailyValuesCommand-3b92d31d0e4080c6922afbe485a0e681?v=39e2d31d0e40806380d7000cdacf7c44&source=copy_link">CreateCsvAndZipConSensorDailyValuesCommand</a></td></tr>
<tr><td><code>conciergesv</code></td><td>CSV/ZIPエクスポート系</td><td><code>CreateCsvAndZipConSensorDailyAveValuesCommand</code></td><td>SYP</td><td>月毎平均センサ情報（<code>s_113</code>）の前々月パーティションをCSV1本にまとめ毎回ZIP圧縮（EMS-SP列を持たないグループ平均値）</td><td>F-AD-09（データダウンロード）</td><td>バッチとしては不要</td><td>同上。移行時の論点は「保持期間（2か月）を超えたデータをどう残すか」であり、CSV出力ロジックの再現ではない（平均値の算出は本バッチではなく集計系バッチ <code>CalcCommonAverageDataCommand</code> が担うため、グループ平均データ自体を新システムでどう保持・提供するかは spec 側の論点）</td><td><a href="https://app.notion.com/p/muilab/CreateCsvAndZipConSensorDailyAveValuesCommand-3b92d31d0e40802a9f3ef9a95ac21f72?v=39e2d31d0e40806380d7000cdacf7c44&source=copy_link">CreateCsvAndZipConSensorDailyAveValuesCommand</a></td></tr>
<tr><td><code>conciergesv</code></td><td>CSV/ZIPエクスポート系</td><td><code>CreateCsvAndZipConSensorHourlyValuesCommand</code></td><td>SYP</td><td>日毎センサ情報（<code>s_102</code>）の8日前パーティションを契約者ごとにCSV化し、月曜に<strong>前々週分</strong>をZIP圧縮（24時間分が横持ち）</td><td>F-AD-09（データダウンロード）</td><td>バッチとしては不要</td><td>同上。<code>s_102</code> のDB保持は14日だがCSV化は8日前に行われるため、結果として DROP の7日前にファイルが出来上がる（それが意図的な設計かはコード・設計書に記述が無く不明）。新システムでは保持期間の設計そのものをTTLで置き換える</td><td><a href="https://app.notion.com/p/muilab/CreateCsvAndZipConSensorHourlyValuesCommand-3b92d31d0e408077bfb1ef797f594cc1?v=39e2d31d0e40806380d7000cdacf7c44&source=copy_link">CreateCsvAndZipConSensorHourlyValuesCommand</a></td></tr>
<tr><td><code>conciergesv</code></td><td>データ管理系</td><td><code>CreateGroupSummaryCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>データ管理系</td><td><code>CreateTablePartitionCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>データ管理系</td><td><code>DeleteDataCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>データ管理系</td><td><code>DeleteLogicalDeletedDevicesCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>データ管理系</td><td><code>DeleteTimeOutControlOneMinuteCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>データ管理系</td><td><code>DeleteTimeOutControlTenMinuteCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>データ管理系</td><td><code>TerminateOutdatedDeviceControlJobsCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>データ管理系</td><td><code>RankingCreationCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>監視・ログ系</td><td><code>SendAlertLogMailCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>監視・ログ系</td><td><code>WatchNotificationCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>conciergesv</code></td><td>監視・ログ系</td><td><code>PutLogFileCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>eminelsv</code></td><td>管理画面</td><td><code>MakeCodeMapDataCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><code>eminelsv</code></td><td>管理画面</td><td><code>HashPasswordCommand</code></td><td>SYP</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
</tbody>
</table>
