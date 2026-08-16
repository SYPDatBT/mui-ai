# MakeCodeMapDataCommand（コードマップデータをCSVから生成・ファイル出力）

## 概要

`MakeCodeMapDataCommand` は、旧システムの `eminelsv`（新EMINELサーバ／運用管理画面）における**手動実行のCLI**（cronスケジュールなし）である：コマンドライン引数で渡された1つのCSVファイルを読み込み、データを2次元のmap `[コード分類][コードID] = コード名` にまとめ、PHPの `serialize()` を行ったうえで1つのファイル（既定では `config/code_map_data.txt`）へ書き出す ― DBの読み書きなし、メール送信なし、外部APIの呼び出しなし。`syp-eminelstandard-backend`（EMINEL-smart）には、**同等の機能は見つからなかった**：任意のCSVをカラム位置に基づいて読み取り、汎用的なコード／名称のmapを構築してファイルへ出力するバッチもAPIも存在しない ― 新システムは「コード／名称の管理」という課題をまったく異なる方向で扱っている（第B部参照）。

---

# 第A部 ― 旧システム

## A.1 全体概要

| 項目 | 内容 |
|---|---|
| **バッチ名** | クラス：`MakeCodeMapDataCommand`・呼び出しコマンド名：`make_code_map_data` *(CakePHP 4 の規約からの推定であり、ファイル内に明示的なoverrideはない)*・**実行スケジュールなし ― 手動実行のCLI**。 |
| **役割** | 「コード」（コード＋名称、分類ごと）の一覧を含む1つのCSVファイルを、serialize済みの1つのmapファイルへ変換する。コード→名称の参照用データとして用いる。 |
| **入力** | コマンドライン引数 `INPUT_FILE`（必須）を通じて1つのCSVファイルを読み込む。DBの読み取りなし、外部APIの呼び出しなし。 |
| **出力** | PHPの `serialize()` 文字列を含む1つのファイルを書き出す ― パスは引数 `OUTPUT_FILE`（任意）から取り、既定は `config/code_map_data.txt`。DBへの書き込みなし、メール送信なし。 |
| **処理概要** | 1. `INPUT_FILE` のCSVファイルを開き、エラーであれば `abort` する。<br>2. 先頭行（ヘッダー）を読み飛ばす。<br>3. 残りの各行について：7列目（`row[6]`）をコード分類、4列目（`row[3]`）をコードID、5列目（`row[4]`）をコード名として取得し、`$mapData[コード分類][コードID] = コード名` にまとめる。<br>4. 出力ファイルのパスを決定する（引数または既定値）。<br>5. 出力ファイルが既に存在する場合→コンソール経由で上書きの確認を求める；ディレクトリである場合→`abort`；上書きしない場合→そのまま終了する。<br>6. `serialize($mapData)` を行い、出力ファイルへ上書きする。書き込みエラーであれば `abort` する。<br>7. 成功メッセージを表示する。 |

## A.2 詳細

### A.2.1 実行スケジュールとパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | **なし。** 2つのcron設定ファイル（`webap_cron設定_20240905.txt`, `mng-webap_cron設定_20241029.txt`）、`cron設定概要.txt`、および `cron実行用シェルスクリプト/*.tgz` から解凍したシェルスクリプト全体に対してクラス名をgrepしたが ― いずれも結果は0件である；`cron設定一覧.xlsx` のみはバイナリであり読み取れていない（残された制約）。 | ― |
| コマンドライン引数 | `INPUT_FILE`（必須）― 入力元のCSV。<br>`OUTPUT_FILE`（任意）― 出力先ファイル。既定は `CONFIG . DS . 'code_map_data.txt'`。 | `MakeCodeMapDataCommand.php:18-23,43` |

### A.2.2 入力CSVのフォーマット（コードの読み取り方に基づく。カラムを説明するコメントはない）

| カラム（0始まりのindex） | コード内での役割 | 備考 |
|---|---|---|
| 先頭行 | 完全に読み飛ばされる（`fgetcsv` を1回呼び出すが結果は使用しない） | ヘッダーとみなす |
| `row[3]` | `codeId` ― mapの内側のキー | *(意味の推定 ― 変数名のみで、ヘッダーはない)* |
| `row[4]` | `codeName` ― 値（表示名） | *(変数名に基づく推定)* |
| `row[6]` | `codeCategory` ― mapの外側のグループキー | *(変数名に基づく推定)* |
| `row[0],[1],[2],[5],...` | 未使用 | ― |

出典：`MakeCodeMapDataCommand.php:32-41`。

**実例 ― リポジトリ内に存在する出力ファイル `config/code_map_data.txt` の先頭からの抜粋** *(入力CSVはリポジトリに残っていないが、出力ファイルにはserialize済みの実データが含まれる。以下の「調査済み」の項を参照)*：

```
code_map_data.txt の先頭（PHP serialize文字列、1,686カテゴリ）:
a:1686:{s:4:"0006";a:9:{i:1;s:39:"センターポーリング毎日検針";i:2;s:12:"随時検針";...}
        s:7:"C011320";a:8:{i:1;s:18:"一般ガス事業";i:2;s:27:"ＬＰＧ一般ガス事業";...}...}

→ つまり構築時の $mapData は次の形:
[
  "0006"    => [1 => "センターポーリング毎日検針", 2 => "随時検針", 3 => "周期検針", ...],
  "C011320" => [1 => "一般ガス事業", 2 => "ＬＰＧ一般ガス事業", ...],
]

→ serialize($mapData) を code_map_data.txt に書き込む（PHP serialize文字列、JSONではない）
```

**元のCSVがどの種類のコードであったかを特定するための調査済みの内容 ― 入力CSVはリポジトリに残っていないが、実際の出力ファイルが部分的に答えを与えている：**
- `eminelsv-develop` における `ls config/` → 出力ファイルそのものである `code_map_data.txt`（2,781,482バイト、serialize済みの実データ）が既定のパスに存在する ― バッチが実際に実行されたことの証拠である；内容は基幹系（Xzilla-系）のコード表である：ガス事業種別（`C011320`, `0010001`）、都道府県（`K101900`）、開栓／閉栓／撤去（`K001280`〜`K001282`）、検針（`0006`）、電池電圧（`0033`）、延べ床面積の区分（`004`：「～70m2」…「151m2～」）― requirement v1.2 の619行目にあるグルーピング属性の区分とちょうど一致する。
- `legacy_eminel_docs` 全体（`docs/` と `sources/` の両方）に対する `**/*.csv` のGlob → 結果0件であり、直接照合できるサンプルCSVファイルは存在しない。
- `docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/補足資料/機器種別一覧.txt` ― そのまま読むとエンコーディングエラー（Shift-JIS）となるため、デコードし直した（codepage 932）：17個の `機器種別`（device_type）コードの一覧であり → 1コードにつき日本語名1つ、**「category」の階層がない** → 本バッチが必要とする3カラムの構造と一致せず、本バッチの入力CSVでは**ない**ことを確認した。
- `14_コンシェルジェSV_詳細設計書別紙_EPC一覧.docx` および `.xlsx`（残っている中で最も名前が近いもの）― いずれもバイナリファイルであり、内容は読み取れていない。

### A.2.3 mapの構築ロジック（CSVの1行ごと）

1. DBの読み書きなし、トランザクションなし、`config/const.php` の定数も一切使用しない。
2. 入力全体をRAM（`$mapData`）へ読み込んでから1回で書き出す ― ストリーミングは行わない。（`MakeCodeMapDataCommand.php:35-41,54`）
3. データエラーの処理を行わない（カラムが欠けた行、associative arrayであるためキーが重複すると自動的に上書きされる）― バリデーションも警告ログもない。

### A.2.4 結果の書き込み ― `code_map_data.txt` ファイル

- パスは任意指定または既定の `config/code_map_data.txt` であり、内容は `$mapData` のPHP `serialize()` 文字列である（PHP独自のフォーマットであり、JSON/CSVではない）。（`MakeCodeMapDataCommand.php:43,54`）
- **出力先ファイルが既に存在する場合**、コンソール経由で上書きの確認を求める；非対話で実行したい場合は、`OUTPUT_FILE` をまだ存在しないパスへ向けるか、あらかじめ回答をstdinへpipeする。（`MakeCodeMapDataCommand.php:44-52`）
- 実際の出力ファイル（2,781,482バイト、serialize済みの実データ）が既定のパスでリポジトリ内にそのまま存在する ― バッチは実際に実行されたことがある。`sources/eminelsv-develop` 全体に対する `code_map_data`／`codeMapData`／`CODE_MAP` の文字列のgrep、および `sources/` 上の `*.php` 全体に対する `unserialize` のgrep ― このファイルを読み返している箇所は見つからなかった。*(推定：リポジトリ外で消費されている可能性、あるいは1回限りの運用支援／移行ツールであり、runtimeのconsumerが存在しない可能性がある)*。

### A.2.5 特記事項／リスク

- 手動実行のユーティリティCLIであり、コンソールとの対話がある（`HashPasswordCommand` と同様）― 定期実行のバッチとはまったく性格が異なる。
- 出力フォーマットがPHPの `serialize()` である ― parserを書き直すか、移植時にJSONへ全面的に変更しない限り、Node.js/TypeScriptへは移植できない。
- 実際の出力ファイルから、入力CSVが基幹系のコード表（ガス事業種別・都道府県・開閉栓・検針・延べ床面積区分…）であることが分かる；E-GWではこの種のコードは既にe-smartのmaster機構（`AttributeMasterTable` のseed＋API）で管理されている ― 残る論点は、E-GW向けに追加すべきcategoryがあるかどうかである。

---

# 第B部 ― EMINEL-smart（新システム）との対照

## 確認済み（同じ本質を持つものは見つからなかったため、B.1/B.2の表はない）

| 調査した領域／candidate | 一致しない理由 |
|---|---|
| `src/` 全体に対する `code.?map` / `code_map_data` / `codeMapData` / `CODE_MAP` / `serialize` / `mapData` のgrep | 関連する結果は0件。`code.?map` の2件の一致は、Arrayの `.map()`（`services/noritz.ts:386`）と、建物分類のinterface `CntrClsfyCodeMap`（`business-logic/get-building-type-of-contract.ts:18`）のみであり ― 業務的な意味での「code map」ではない。 |
| `resource/database/master/*.json` ＋ `resource/database/master/0000000.sh` | `aws dynamodb batch-write-item` 用の `PutRequest` ペイロードをあらかじめ含む手書きのJSONファイルであり、静的なseedである。いかなるCSVからも生成されていない（`0000000.sh:4-19`）。 |
| `src/functions/api-device-master/*` | 既存の `DeviceMaster` テーブルに対するget/updateのCRUDのみであり（`app.ts:9-17`）、CSVのimportはない。 |
| `src/functions/batch-common-read-csv/app.ts`（`if20*-import-*`, `dm1040-import-*` の各バッチで共用） | 実際にCSVを読み込むが、Xzillaのファイル種別ごとに**固定のカラム名**の一覧に従ってマッピングし（`LIST_COL_IF2016`,...`app.ts:24-121`）、S3へJSON形式で書き出す ― 旧バッチの、**カラム位置に基づく**汎用的な読み取り機構とは異なる。これは具体的な業務データ（契約／顧客／機器）のimportであり、code-mapを生成するツールではない。 |
| `src/functions/api-device/import-device-error-master.ts` | 特定の1種類のmaster（機器エラー）について、固定の日本語カラム名に従ってCSVを読み取り、**DBへ書き込む** ― ファイルは出力せず、旧バッチ（CSVを読み込み→ファイルを出力し、DBには触れない）とは本質が異なる。 |

**結論：** EMINEL-smartには「任意のCSV → カラム位置に基づき、複数のカテゴリに対して汎用的にコード／名称のmapを構築 → ファイルへ出力」という処理をそのまま行うものは存在しない。新システムは「コード／名称の管理」をまったく異なる方向で扱っている：具体的なmasterの種類ごとに（例えば `device-error-master`）専用のCRUD API一式（＋固定スキーマによるCSV import）を構築し、DynamoDBへ直接書き込む ― `MakeCodeMapDataCommand` のような、CSVを読み取ってファイルを出力する汎用ツールは存在しない。

---

## まとめ

なし ― 旧版は処理フローが1つのみであり（分岐や並列のアルゴリズムはない）、新システムには対照すべき**同じ本質を持つものが見つからない**（「別の仕組みで置き換えられた」というケースではない）― 第B部末尾の「結論」で十分に総括されている。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | メインロジック | `sources/eminelsv-develop/src/Command/MakeCodeMapDataCommand.php` |
| 旧システム | cron（存在しないことの確認） | `docs/02_詳細設計/10_バッチ処理/webap_cron設定_20240905.txt`, `mng-webap_cron設定_20241029.txt`, `cron設定概要.txt`, `cron実行用シェルスクリプト/*.tgz`（解凍してシェルスクリプトを確認済み；`cron設定一覧.xlsx` はバイナリで読み取れていない） |
| 旧システム | 実際の出力ファイル（serialize済みのデータ） | `sources/eminelsv-develop/config/code_map_data.txt`；延べ床面積の区分との照合：`eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:619` |
| 旧システム | 確認済みの関連資料（一致しないもの） | `docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/補足資料/機器種別一覧.txt` |
| 旧システム | 読み取れていない関連資料（バイナリ） | `14_コンシェルジェSV_詳細設計書別紙_EPC一覧.docx` / `.xlsx` |
| 新システム | 確認した最も近い候補 | `src/functions/api-device/import-device-error-master.ts`, `src/functions/batch-common-read-csv/app.ts`, `src/functions/api-device-master/*`, `resource/database/master/0000000.sh` |
