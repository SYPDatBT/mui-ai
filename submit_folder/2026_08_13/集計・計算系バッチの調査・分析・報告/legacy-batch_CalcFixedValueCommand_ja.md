# 旧バッチ ― CalcFixedValueCommand（確定値再集計機能）

## 要約

`CalcFixedValueCommand`は、旧システム（EMINELコンシェルジュサーバー）における**手動実行**バッチ（cronスケジュールなし）であり、コマンドライン引数で指定された1件または複数の世帯について、**日次の買電量合計（買電量）**を月次集計テーブル`s_103`へ（記録／上書き）するために用いられる。データソースは、他の時間別集計バッチのようにECHONETセンサー（`t_202`）ではなく、`emn_confirm_electric_powers`テーブルである――これは外部ソース「Xzilla」（情報共通基盤連携）からCSV経由で他のバッチ（`RcvHalfHourElectricPowerCommand`）が事前に取り込んだ、30分単位の**確定済み（確定）**買電データである。本バッチはDBの読み書きのみを行い、外部APIの呼び出し、メール送信、CSV出力は一切行わない。パラメータ、SQL文、計算式、および書き込み／トランザクション機構の詳細は第2部に記載する。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | Xzillaからの確定済み（確定）電力データをもとに、日次の買電量（系統からの購入電力）合計を月次集計テーブルへ記録／上書きする――システムの自動時間集計チェーン（ECHONET）は現状、売電（電力販売）のみを計算し買電を計算しないため、本バッチが買電を月次テーブルへ書き込む唯一の経路となっている。運用担当者が指定する世帯＋月（任意でさらに日）単位で手動実行する。 |
| **Input** | DBの読み取りのみ。**外部APIは呼び出さず、CSVも自ら読み込まない**（Xzillaのcsvは`RcvHalfHourElectricPowerCommand`が事前にDBへ取り込み済み）：`t_101`（世帯一覧、5つのグループ属性を使用）＋`emn_confirm_electric_powers`（確定済みの買電データ、30分単位／日ごと）。コマンドライン引数：`--emssp`（必須、複数世帯はカンマ区切り）、`--yearmonth`（必須）、`--day`（任意）。 |
| **Output** | **DBへの書き込みのみ**――データが返却された世帯・日ごとに、`s_103`（エンティティ`ConSensorDailyValue`、共通ライブラリ`EminelSvLib`経由）へ1レコードを（新規INSERTとして）書き込む：`device_type = BUY_ELECTRIC(11)`、対応する日付カラム1つ（`c011`〜`c041`）＋グループ属性カラム5つをセットする。メール送信・CSV出力は行わない。 |
| **処理概要** | 1. `--emssp`／`--yearmonth`／`--day`パラメータを読み取り、フォーマットをバリデーションし、世帯リストを分割する。<br>2. 各世帯について：`emn_confirm_electric_powers`と`t_101`を結合してクエリし、確定済みの買電データを取得する――`--day`が指定されていなければ月全体分、指定されていればその1日分のみ。<br>3. 返却された日ごとの各行について：その日の48個の30分値を合算して日次合計を1つ算出する。<br>4. 各日について：新規レコードを作成し、日付カラム＝直前に算出した合計値＋`t_101`から取得した5つのグループ属性をセットして、`s_103`へ保存する。<br>5. 1世帯分の処理はすべて専用のトランザクション内で行う。その世帯のいずれかのステップでエラーが発生した場合→その世帯のトランザクションをロールバックし、コマンド全体を停止する（`abort()`）。リスト内の残りの世帯は処理されない。 |

## 第2部 ― 詳細

### 2.1 起動パラメータとバリデーション

| パラメータ | 必須 | フォーマット | 備考 |
|---|---|---|---|
| `--emssp` | あり | 世帯コードのリスト、カンマ区切り、各コードは数値である必要がある | 空、または数値でない要素が含まれる場合→`checkValidate`は`false`を返す |
| `--yearmonth` | あり | `YYYY-MM` | 空、またはフォーマット誤りの場合→`false` |
| `--day` | なし | `DD`（`--yearmonth`と組み合わせて`YYYY-MM-DD`が暦上有効であること） | 指定された場合、その日がその月に存在しない場合（`checkdate`）→`false` |

出典：`CalcFixedValueCommand.php:48-55`（`buildOptionParser`）、`:289-345`（`checkValidate`）。

`checkValidate`が`false`を返した場合、`execute()`は冒頭で直ちに`$io->abort('failed checkValidate')`を呼び出し、いずれの世帯も処理しない（`CalcFixedValueCommand.php:74-78`）。

有効な場合：`$this->emssps` = `--emssp`から分割された世帯コードの配列；`$this->yearmonth` = `YYYY`と`MM`を連結した値（`-`を除去）；`--day`が指定されていれば`$this->day` = 渡された日の値（`CalcFixedValueCommand.php:296-341`）。

### 2.2 世帯ごとのループとトランザクション

```
foreach (emssps as emssp):
    emsspの確定済み買電データを取得する（2.3）
    データ取得でエラー → resultCode=false、トランザクションは開始しない
    データ取得がOKの場合：
        トランザクション開始
        各日をs_103へ書き込む（2.4/2.5）
        すべての書き込みがOK → コミット
        いずれかの日で書き込みエラー → ロールバック
    resultCode=falseの場合 → この世帯の時点で直ちにコマンド全体をabort()する
```
出典：`CalcFixedValueCommand.php:81-87`（`execute`）、`:98-122`（`recalculation`）。

各世帯は個別のトランザクションを持つ（`--emssp`のリスト全体で1つの共通トランザクションではない）。ある世帯が失敗すると、`abort()`が直ちにコマンドを停止する――リスト内でまだ処理されていない後続の世帯はスキップされるが、それ以前に処理済みでコミットに成功した世帯の結果はそのまま保持される。

### 2.3 確定済み買電データ取得SQL

`--day`が指定されているかどうかにより選択される2つの分岐がある――構造は同じで、日付の絞り込み条件のみが異なる：

```sql
SELECT
    customer.c001 as "c001", customer.c012 as "c012", customer.c015 as "c015",
    customer.c016 as "c016", customer.c024 as "c024", customer.c042 as "c042",
    confirm.ymd as "ymd",
    COALESCE(confirm.kwh_0000_0030, 0) + COALESCE(confirm.kwh_0030_0100, 0) + ... （48個の30分カラム、00:00〜24:00）
        AS total
FROM emn_confirm_electric_powers AS confirm
    INNER JOIN t_101 AS customer
        ON confirm.spl_pw_spt_srno = customer.c001 AND customer.c052 IS NULL
WHERE (
    confirm.spl_pw_spt_srno = :emssp AND
    confirm.lct_ctgr = '1' AND
    -- --dayなしの分岐:
    confirm.ymd >= :fromdate AND confirm.ymd < :todate    -- fromdate = yearmonth+"01", todate = fromdate + 1ヶ月
    -- --dayありの分岐:
    -- confirm.ymd = :date                                -- date = yearmonth + day
);
```
出典：`CalcFixedValueCommand.php:182-212`（月の分岐）、`:231-260`（日の分岐）。

**SQL文で使用するカラムの意味：**

| テーブル | カラム | 意味 | 備考 |
|---|---|---|---|
| `t_101` | `c001` | 世帯コード（EMS-SP） | 結合キー |
| `t_101` | `c052` | 論理削除日時 | `IS NULL` = 世帯が有効であることを示す |
| `t_101` | `c012` | 建物区分（建物種別：集合住宅(1)／戸建て(2)） | → `GroupAttr1` |
| `t_101` | `c042` | 暖房熱源（暖房熱源：13A(1)／LPG(2)／電気(3)／灯油(4)／その他(9)） | → `GroupAttr2` |
| `t_101` | `c015` | 延床面積（延床面積、6段階） | → `GroupAttr3` |
| `t_101` | `c016` | 家族人数（世帯人数、1〜6） | → `GroupAttr4` |
| `t_101` | `c024` | ガスコージェネレーション（コージェネレーション種別：コレモ(1)／エネファーム(2)／その他(9)／なし(10)） | → `GroupAttr5` |
| `emn_confirm_electric_powers` | `spl_pw_spt_srno` | 世帯コード（EMS-SP） | 結合キー、コメント："EMS-SP" |
| `emn_confirm_electric_powers` | `lct_ctgr` | 供給_受電区分 | `= '1'`で絞り込み |
| `emn_confirm_electric_powers` | `ymd` | 年月日（8桁文字列） | 月の範囲、または特定の1日で絞り込み |
| `emn_confirm_electric_powers` | `kwh_0000_0030`〜`kwh_2330_2400` | 1日の30分単位ごとのkWh、48カラム | ⭐ 主たる計算対象値 |

カラムコメントの出典：`sources/eminelsv-develop/config/Migrations/20240410003631_CreateElectricPowerConfirm.php`（テーブルコメント："EMN_30分電力量確定値出力情報取り込みデータ"）、`20230807080522_InitialMigration.php`（`t_101`のカラムコメント）。

該当行が1件も返却されない場合（その世帯にその月／日の確定済み電力データが存在しない場合）、書き込みステップ（2.4）はその世帯について一度も実行されない――`s_103`には何も書き込まれないが、処理は成功とみなされる（エラーとはカウントされない）。

### 2.4 日次合計の計算式

上記SQLから返却された日ごとの各行について：

```
total(日) = Σ（その日の48個のkwh_HHMM_HHMMカラム）、COALESCEによりnullは0とする
```
この合算はSQL文の中で行われており（`COALESCE(..., 0) + COALESCE(..., 0) + ...`）、PHPコード側では計算しない。出典：`CalcFixedValueCommand.php:186-202`（月の分岐）、`:236-251`（日の分岐）。

### 2.5 書き込み結果 ― 出力先テーブル `s_103`

- エンティティ：`ConSensorDailyValue`（共通ライブラリ`EminelSvLib`、物理テーブル名`s_103`、コード内での呼称"月毎センサ情報"）。主キー：`(c001, c002, c003, c004)` = （世帯コード、機器種別、位置、年月――常にその月の01日）。
- SQL結果の日ごとの各行について：**新規エンティティ**を作成し、以下をセットする：

| エンティティのフィールド | セットする値 | 出典 |
|---|---|---|
| `c001`（EmsSp） | `rowData['c001']` | `:139` |
| `c002`（DeviceType） | `BUY_ELECTRIC`（定数 = `11`） | `:140` |
| `c003`（RoomId） | `0` | `:141` |
| `c004`（Datetime） | `rowData['ymd']`が属する月の01日 | `:133-134,142` |
| `c009`（NeedAggCompleteFlag） | `2` | `:143` |
| `c111`〜`c115`（GroupAttr1〜5） | 世帯の`c012, c042, c015, c016, c024`（対応順：建物区分、暖房熱源、延床面積、家族人数、ガスコージェネレーション） | `:144-148` |
| 対応する日付カラム（`c011`〜`c041`、= `c0` + (日+10)） | `rowData['total']`（2.4で算出した合計） | `:135,149` |
| `c051`（Modified） | 現在時刻 | `:150` |
- `save()`を呼び出して新規エンティティを`s_103`へ書き込む（**新規レコードのinsert**操作であり、書き込み前に主キーで既存レコードを読み込んで更新する処理は行わない）。
- いずれかの日の行で`save()`が例外をスローした場合：EMS-SP＋日付を付してエラーをログに記録し、その時点で直ちに`false`を返す――同一呼び出し内の残りの日（月全体を処理している場合）はそれ以降書き込まれない。

出典：`CalcFixedValueCommand.php:130-165`（`updatePurchasedElectricityData`）、エンティティ`sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorDailyValue.php`、テーブル`sources/eminel_sv_lib-develop/src/Model/Table/ConSensorDailyValuesTable.php`。

### 2.6 関連する定数とデータソース

| 定数／テーブル | 値／役割 | 出典 |
|---|---|---|
| `BUY_ELECTRIC` | `11`――`s_103.c002`に書き込む機器種別コード | `const.php:192` |
| `emn_confirm_electric_powers` | "EMN_30分電力量確定値出力情報取り込みデータ"――Xzillaから取り込まれた、**確定済み（確定）**の30分電力データ | `20240410003631_CreateElectricPowerConfirm.php:75` |
| `emn_fast_electric_powers` | "EMN_30分電力量速報値出力情報取り込みデータ"――同じくXzilla由来の**速報（速報値）**30分電力データ。別テーブルであり、本バッチはこのテーブルを読み込まない | `20240410002142_CreateElectricPowerFast.php:75` |
| 上記2テーブルへXzillaデータを取り込むバッチ | `RcvHalfHourElectricPowerCommand`――Xzilla中継サーバーからCSVを取得し、`emn_confirm_electric_powers`／`emn_fast_electric_powers`／`emn_all_electric_powers`へinsertする | `sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php` |
| 実行スケジュール（cron） | なし――cron一覧（`mng-webap_cron設定_20241029.txt`、`webap_cron設定_20240905.txt`、`cron設定一覧.xlsx`）に`CalcFixedValueCommand`は見つからない | ― |
