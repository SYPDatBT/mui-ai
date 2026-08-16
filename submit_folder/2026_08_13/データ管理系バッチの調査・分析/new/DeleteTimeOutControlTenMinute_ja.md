# DeleteTimeOutControlTenMinuteCommand（10分タイムアウト制御レコード削除）

## 概要

`DeleteTimeOutControlTenMinuteCommand` は、`conciergesv` 上で**10分ごと**に実行されるcronバッチであり、`DeleteTimeOutControlOneMinuteCommand`（調査済み、`DeleteTimeOutControlOneMinute.md` 参照）と同系統である。`Instructions` キュー内の別の4種類の指示（遠隔再起動、プロパティマップ更新、GW設定ファイル更新、暖房制御パラメータ更新 ― 10分を過ぎても処理が完了していないもの）を引き続き削除し、さらに毎時ちょうど0分に実行される分岐を内部に入れ子で持ち、ファームウェア更新指示のみを個別に削除する（タイムアウトは60分。ファームウェア更新には時間がかかるため、明らかに長く設定されている）。同様に、サーバーとGW間のポーリングベース制御モデルに対するセーフティネットである。新リポジトリ `syp-eminelstandard-backend` においては、**調査済みの姉妹バッチとまったく同じ結論**となる：機器制御のアーキテクチャがメーカークラウドAPIの同期呼び出しへ完全に切り替わり、タイムアウト／削除の対象となる指示キューが存在しないため、同等の仕組みは不要であり、また存在しない ― 証拠の詳細は `DeleteTimeOutControlOneMinute.md` を参照。

---

# 第A部 ― 旧システム

## A.1 概要

| 項目 | 内容 |
|---|---|
| **バッチ名** | クラス: `DeleteTimeOutControlTenMinuteCommand`（`Command` を直接 extends）・実際の呼び出しコマンド: `cake.php DeleteTimeOutControlTenMinute` *(tgz `eminel-mng-webap.20240909` の `12_DeleteTimeOutControlTenMinute.sh` にて観察。CakePHPは両方の形式を受け付ける)* ・cronスクリプト: `12_DeleteTimeOutControlTenMinute.sh` ・cronグループは「12.DBデータ削除」と同一。 |
| **役割** | タイムアウトしたGW制御指示を `Instructions` キューから削除するセーフティネット。対象は5種類の指示（タイムアウト10分の4種類＋タイムアウト60分の1種類）― `DeleteTimeOutControlOneMinuteCommand` と同じ仕組みだが、担当する指示の種類が異なる。 |
| **Input** | `Instructions` テーブルを読み取る ― 2つの個別の絞り込み条件（A.2.2参照）。引数 `--datetime`（デフォルト `now`）。 |
| **Output** | 条件に一致する行を1件ずつ `DELETE` する。指示種別のグループごとに個別のトランザクションで実行する。新規データの書き込みは行わない。 |
| **処理概要** | 1. 現在の分（`--datetime`）がちょうど0であれば → ファームウェア削除分岐（タイムアウト60分）を先に追加実行する。<br>2. 残り4種類の指示を削除する分岐（タイムアウト10分）は、条件なしで常に実行する。<br>3. 各分岐：個別のトランザクションを開始し、タイムアウトした指示を検索して1行ずつ削除する；1行でもエラーが発生 → その分岐をrollbackし、その分岐を停止する（2つのトランザクションは独立しているため、もう一方の分岐には影響しない）。 |

## A.2 詳細

### A.2.1 実行スケジュールと毎時／10分の入れ子分岐構造

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `*/10 * * * *` ― 10分ごと | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:43` |
| ファームウェア分岐（60分）の実行条件 | `(--datetime)->minute === 0` の場合のみ実行 ― すなわち毎正時に当たるcron実行回のみ（`:00`、`:10` は `:00` でない限り該当しない） | `DeleteTimeOutControlTenMinuteCommand.php:40-42` |
| 10分分岐の実行条件 | 条件なしで、cron実行のたびに常に実行 | `:44` |

cronは `*/10`（すなわち `:00,:10,:20,:30,:40,:50` の各分）で実行されるため、ファームウェア分岐は毎時 `:00` の回にのみ一致する ― つまり、クラス名は「TenMinute」であるものの、**ファームウェアのタイムアウトは1時間に1回チェックされる**。これはバグではなく、`*/10` のcron実行を共用して2つの異なる実行頻度を1つのCommandにまとめ、ファームウェア専用のcron行を追加せずに済ませるための意図的な設計である。

### A.2.2 2つの絞り込み条件グループ ― タイムアウトと指示種別が大きく異なる

| 分岐 | `instruction_type` | 各種別の意味 | タイムアウト | 出典 |
|---|---|---|---|---|
| `deleteInstructionsPerTenMinute` | `IN (3, 4, 6, 7)` | 3=`INSTRUCTION_TYPE_REBOOT`（遠隔再起動）、4=`INSTRUCTION_TYPE_PROPERTYMAP`（プロパティマップ更新）、6=`INSTRUCTION_TYPE_CONFIGURE`（GW設定ファイル更新）、7=`INSTRUCTION_TYPE_HEAT_CONTROL`（暖房制御パラメータ更新） | `instruction_date < (--datetime − 10分)` | `:53-70`；定数は `sources/hemssv-develop/config/const.php:57,59,63,65` |
| `deleteInstructionsPer60Minutes` | `IN (5)`（`IN` の形式で記述されているが値は1つのみ） | 5=`INSTRUCTION_TYPE_FIRMWARE`（ファームウェア更新） | `instruction_date < (--datetime − 60分)` | `:95-109`；定数は `const.php:61` |

`DeleteTimeOutControlOneMinute.md`（§A.2.2）で確認済みのものと同じ通常のライフサイクルである：必要に応じてサーバーが `Instructions` に指示を書き込む → GWが定期的にポーリングして取得する（`InstructionController.php:77`、`instruction_type` ごとのswitchは `:206-239`）→ GWが処理し、結果を報告する → サーバーが自ら指示を削除する（同様のパターンとして、PROPERTYMAPは `:798-821`、FIRMWAREは `:996-1019`、CONFIGUREは `:1154-1177`、HEAT_CONTROLは `:1312-1335`、REBOOTは `:1470-1493` ― 別ファイルで引用した種別1と同じ find+delete-on-complete の組み合わせである）。2つの `DeleteTimeOutControl*MinuteCommand` バッチは、この通常のライフサイクルでは自動削除が間に合わなかった指示のみを削除するものである。

**なぜファームウェアには明らかに長いタイムアウトが必要なのか（10分に対して60分）** *(業務の性質に基づく合理的な推測であり、コード中に直接裏付けるコメントはない)*：GW／機器のファームウェア更新は、他の単純な設定・制御指示に比べて時間がかかることが多い（ファイルのダウンロード、フラッシュへの書き込み、再起動）― そのため、「タイムアウトとみなす」しきい値をより長くし、正常に処理中の指示を誤って削除しないようにする必要がある。

### A.2.3 トランザクションとエラー処理

- 2つの分岐は**独立した2つのトランザクション**を使用する（各分岐がそれぞれ `begin()`／`commit()`／`rollback()` を行う。複数のステップで1つのトランザクションを共有する `DeleteDataCommand` とは大きく異なる）― ファームウェア分岐でのエラー（発生する場合、:00分のみ）は10分分岐に影響せず、その逆も同様である。（`:59-86,101-125`）
- `DeleteTimeOutControlOneMinuteCommand` と同じパターンである：`foreach`＋`delete()` で1行ずつ削除し、リストが空の場合はrollback（無害）＋ログ出力を行ってreturnする。1行でもエラーが発生した場合はその分岐全体をrollbackして即座に停止する（同じ分岐内の残りの行は削除しない）。
- 別ファイルで述べたものと同じリスクがある：絞り込み条件が `instruction_status` をチェックしないため、GWが処理途中の指示（タイムアウトの時間内に完了報告が間に合わなかったもの）も、本当に停止した指示と同様に削除されうる。

### A.2.4 特記事項／リスク

- `BaseCommand` を extends していない → PHP層でのPIDロックがない（姉妹バッチと同様）。ただし、cronのシェルラッパー `12_DeleteTimeOutControlTenMinute.sh` に多重起動を防ぐ `flock -n` があり ― 重複実行のリスクは運用層で防止されている。
- `instruction_type = 2`（`INSTRUCTION_TYPE_DEVICE_LIST` ― 機器一覧の要求）は、**調査済みの2つのタイムアウトCommandのいずれのバッチによっても削除されない**（1分: 種別1のみ；10分: 種別3,4,6,7＋種別5を個別に）― *(種別2に対する別の削除の仕組みがあるのか、それとも他の業務上の理由で削除が不要なのかは検証できていない ― 調査対象の2バッチの範囲外である)*。
- 「2つの異なる実行頻度を1つのCommandにまとめる」こと（10分＋60分を `minute===0` のチェックによって入れ子にしている）により、クラス名（`...TenMinuteCommand`）が実際の挙動を十分に反映していない（内部に60分の頻度がもう1つ隠れている）― コードを開かずに名前だけを読むと誤解を招きやすく、移植の際にファームウェア部分を見落とさないよう注意が必要である。

---

# 第B部 ― EMINEL-smart（新システム）との対照

> 結論は `DeleteTimeOutControlOneMinute.md` と同一である ― 証拠の全体は繰り返さず、本バッチが扱う5種類の指示すべてに正しく適用されることのみを確認する。

## 確認済み

| 領域／候補 | 結果 |
|---|---|
| 実際の機器制御モデル（すべての指示種別に共通で適用され、reboot/firmware/config/heat-control に限らない） | **同期PUSHであり、ポーリングではない** ― `DeleteTimeOutControlOneMinute.md` のPart Bで確認済み：`src/functions/api-device/control-device.ts:91-425`、`src/functions/batch-execute-automation/app.ts:153-159`、`src/layers/common/nodejs/business-logic/control-device.ts:226-793`。旧 `Instructions` キューのような「指示種別」（`instruction_type`）による区別はない ― すべての制御操作はメーカークラウドAPIを直接呼び出しており、指示種別ごとのキューという概念自体が存在しない。 |
| 「GWの再起動／設定／ファームウェア指示キュー＋タイムアウト削除」に相当するテーブル／Lambda | 見つからない ― 別ファイルで述べたものと同じ証拠である（`src/functions/`、`src/layers/common/nodejs/business-logic/` に対する `Instruction`／`PendingCommand`／`DeviceCommand`／`ControlQueue`／`timeout`／`stale`／`pending` のgrepは、いずれも関連する結果が0件）。問いの本質がまったく同じ（同じ `Instructions` テーブル、廃止された同じポーリングの仕組みで、異なるのは `instruction_type` のみ）であるため、検索手順は繰り返していない。 |
| 新システムにおける「GW／機器のリモートファームウェア更新」の概念 | **E-GWの要件には引き続き存在し、配信経路が変わっただけ** ― 本バッチの5つの `instruction_type` が対応する5つの機能（再起動・プロパティマップ・ファームウェアOTA・設定ファイル・暖房制御パラメータ）は、いずれも `00_integrated_requirements_v1.2.md` にある：F-GW-11〜13（:382-384）、F-MC-07/08（:399-400）、8-2項の配信には type 3,4,5,6,7 と1対1で対応する5項目がすべて列挙されている（:563-569）、配信経路は「すべてEMINEL-smartサーバー → GW管理クラウド → E-GW」（:571）；配信の仕組みはDBポーリングのキューではなく、GW管理クラウド経由のMQTT push である（mui Labの既存資産 ― feature_list :35,:77 はmuiが主管）― したがってDBのタイムアウト削除バッチを移植する必要はなく、指示のタイムアウト／未達のセマンティクスはGW管理クラウドに属する。さらに、e-smartには現時点でリモートファームウェア更新（`infraredRemoteService` 経由の `update_firmware`／`check_update_firmware` ― `src/functions/api-device/update-firmware.ts:22`、`check-update-firmware.ts:8`）が同期呼び出しのモデルですでに存在しており ― キューが不要であることの追加の裏付けとなる。 |

---

## まとめ

`DeleteTimeOutControlOneMinute.md` でまとめた結論をそのまま適用する ― 詳細は繰り返さず、本バッチ固有の相違点のみを挙げる：

- 旧システムの本バッチは、`Instructions` の7種類の指示のうち5種類を扱う（種別1は専用の別バッチがあるため対象外、種別2は誰が削除するのか不明）― 「ポーリングキューにはタイムアウトしたゴミの削除が必要」という同じ根本課題に対し、全種別で共通の1つのタイムアウトではなく、タイムアウトごとに分割している（設定／制御指示は10分、ファームウェアは60分）― これは同一バッチ内の2つの「分岐」ではあるが、**本質的に異なる2つのアルゴリズムではない**（いずれも `instruction_date` としきい値を比較する同じ計算式である）。そのため複雑な決定木の形にまとめる必要はなく ― 異なるのはしきい値の数値と、適用される `instruction_type` の集合のみである。
- 新システム：姉妹バッチと同じ理由で消滅する ― メーカークラウドAPIの同期呼び出しへ完全に移行しており、タイムアウト／削除を必要とする指示キューは、どの種別（reboot/config/firmware/heat-control）にも存在しない。DBポーリングキューという課題自体がなくなっている；5種類の指示の配信はGW管理クラウド経由のMQTT（F-MC-08）へ移り、配信の信頼性および未達の指示についてはそちらが責任を負う ― EMINEL-smartサーバーの範囲外である。

**移植時の結論**：`DeleteTimeOutControlTenMinuteCommand` を新システムへ持ち込む必要はない。`instruction_type IN (3,4,6,7)` を削除する部分（10分）であっても、ファームウェア `instruction_type=5` を削除する部分（60分、同一Command内に入れ子）であっても同様である ― どちらも `Instructions` キューのゴミを削除するバッチであるが、そのキューは現行の同期pushアーキテクチャには存在しない。本バッチを（いかなる形であれ）再度追加することは、削除対象となるキューテーブルが存在しないため冗長となる。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | メインロジック | `sources/conciergesv-develop/src/Command/DeleteTimeOutControlTenMinuteCommand.php` |
| 旧システム | 姉妹バッチ（調査済み、ライフサイクルの前提を共有） | `DeleteTimeOutControlOneMinute.md`、`sources/conciergesv-develop/src/Command/DeleteTimeOutControlOneMinuteCommand.php` |
| 旧システム | 各 `instruction_type` の意味（hemssv経由でクロス確認） | `sources/hemssv-develop/config/const.php:57,59,61,63,65` |
| 旧システム | 各指示種別の処理ライフサイクル（ポーリングによるdispatch＋完了時の自動削除） | `sources/hemssv-develop/src/Controller/InstructionController.php:77,206-239,798-821,996-1019,1154-1177,1312-1335,1470-1493` |
| 旧システム | `Instruction` のカラムの意味 | `sources/eminel_sv_lib-develop/src/Model/Entity/Instruction.php` |
| 旧システム | 実行用cronスクリプト（実際の呼び出しコマンド＋多重起動を防ぐ `flock -n`） | `docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` → `eminel-mng-webap/12_DeleteTimeOutControlTenMinute.sh` |
| 旧システム | 実行スケジュール（cron） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:43` |
| 旧システム | バッチ一覧（日本語の説明、サーバーのグループ） | `docs/03_API仕様/04_バッチ一覧.md:79` |
| 新システム | 5つの配信機能に関するE-GW要件＋GW管理クラウド経由のMQTT配信経路 | `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:34,380-384,395,399-400,563-571`、`docs/eminel/1_product/10_feature_list.md:35,77` |
| 新システム | 証拠の全体（繰り返さず、姉妹バッチのファイルを参照） | `DeleteTimeOutControlOneMinute.md`（Part B）、`src/functions/api-device/control-device.ts:91-425`、`src/functions/batch-execute-automation/app.ts:153-159`、`src/layers/common/nodejs/business-logic/control-device.ts:226-793` |
