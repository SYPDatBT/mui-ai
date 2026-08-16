# HashPasswordCommand（パスワードハッシュ生成・ユーティリティ）

## 概要

`HashPasswordCommand` は、旧システムの `eminelsv`（新EMINELサーバ／運用管理画面）における**手動実行のCLI**（cronスケジュールなし）である：コンソール経由でパスワードを尋ね、`Cake\Auth\DefaultPasswordHasher`（`AdminUser` entityがパスワードの保存に用いるものと同じhasher）でハッシュ化し、結果をコンソールへ出力する ― UIを経由せずに管理者パスワードを作成／リセットする必要がある場合に、ハッシュ値をあらかじめ生成し、DBへ手作業で挿入するために用いる。`syp-eminelstandard-backend`（EMINEL-smart）には、この機能は**存在せず、必要でもない**：管理者アカウントの作成は**AWS Cognito**を経由し、ハッシュ化が必要となる `password` カラムはDB上にもはや存在しない ― これは意図的なアーキテクチャの変更であり、移植時の漏れではない。

---

# 第A部 ― 旧システム

## A.1 全体概要

| 項目 | 内容 |
|---|---|
| **バッチ名** | クラス：`HashPasswordCommand`・呼び出しコマンド名：`hash_password` *(CakePHP 4 の規約からの推定)*・**実行スケジュールなし ― 手動実行のCLI**。 |
| **役割** | `AdminUser` entityのパスワード保存方式と互換性のあるパスワードのハッシュ文字列を生成する。UIを経由せずに管理者アカウントを作成／リセットする必要がある場合に、手作業で用いる。 |
| **入力** | コマンド実行時にコンソールのpromptから入力する1つのパスワード文字列 ― コマンドライン引数はなく、DB／ファイルの読み取りもない。 |
| **出力** | ハッシュ文字列をコンソール（stdout）へ出力する。DBへの書き込みなし、ファイルへの書き込みなし、メール送信なし。 |
| **処理概要** | 1. コンソール経由でパスワードを尋ねる（`$io->ask('Password?')`）。<br>2. 長さが0でなければ→`DefaultPasswordHasher::hash()` でハッシュ化し、コンソールへ出力する。<br>3. 空のままであれば→何も行わず終了する。 |

## A.2 詳細

### A.2.1 実行スケジュールとパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | **なし。** 2つのcronファイル、および `cron実行用シェルスクリプト/*.tgz` から解凍したシェルスクリプト全体（webap 20240905、mng-webap 20240909）に対してクラス名をgrepしたが ― 結果は0件である。 | ― |
| コマンドライン引数 | なし ― パスワードは対話的なpromptからのみ入力し、argumentでは渡さない（shellの履歴に残らない）。 | `HashPasswordCommand.php:20` |

### A.2.2 ハッシュアルゴリズム

- `Cake\Auth\DefaultPasswordHasher` を使用する ― CakePHPフレームワーク（`cakephp/cakephp: 4.4.*`）に属し、本ソースリポジトリ内には存在しないため、具体的なimplementationを引用することはできない。*(CakePHPの公開ドキュメントによれば ― リポジトリ内では検証できていない ― 既定では `password_hash()` とbcryptを用いる；これはフレームワークの知識に基づく推定であり、ソースを直接読んだものではない。)*
- 同じhasherが、`AdminUser` entityがパスワードをsetする際にも用いられる：`(new DefaultPasswordHasher())->hash($password)` ― `eminelsv-develop/src/Model/Entity/AdminUser.php:40`。→ **確実**（コードを直接読んで確認）：`HashPasswordCommand` の出力は、`admin_users` テーブルの `password` カラムへそのまま挿入できる（`AdminUsersTable.php:44`、`setTable('admin_users')`）― 手作業で挿入する対象であり、バッチによる自動的なデータの流れではない。
- `EminelSvLib\StaticServices\PasswordEncoder`（`eminel_sv_lib-develop/src/StaticServices/PasswordEncoder.php`）とは**同種ではない** ― Spring Securityの `StandardPasswordEncoder` を模したものであり（8バイトのsalt＋SHA-256を1024回繰り返す）、別の種類のアカウント／別の流れに用いられるもので、`eminelsv` のadmin userのものでは**ない**。同一のエコシステム内にある2つの異なるハッシュの仕組みを混同しないために挙げているにすぎない。

### A.2.3 結果の書き込み ― コンソールへの出力（`$io->out`）

- コンソールへ直接出力するのみで、どこにも保存しない ― 運用者がハッシュ値を自らコピーし、DBへ手作業で挿入する。（`HashPasswordCommand.php:22`）
- トランザクションなし、画面への出力以外のside-effectも一切ない。

### A.2.4 特記事項／リスク

- 手動実行のユーティリティCLIであり、コンソールとの対話がある（`MakeCodeMapDataCommand` と同様）― 定期実行のバッチではない。
- `password` をargumentで渡すことができない→shellの履歴からパスワードが漏れるリスクは下がるが、本コマンドを自動化／スクリプト化することもできない。
- パスワードの再入力による確認はなく、パスワードの強度チェックもない ― バリデーションは（存在するとすれば）別の場所（admin userを作成／編集するUI）にあり、本コマンドの範囲外である。

---

# 第B部 ― EMINEL-smart（新システム）との対照

## B.1 バッチ名とコード内の位置

| 仕組み | 場所 | データソース | 出力先 |
|---|---|---|---|
| 管理者アカウントの作成（「DBへ挿入するためにパスワードをハッシュ化する」という概念を完全に置き換えるもの） | `src/functions/api-admin/create-admin.ts` ― APIであり、バッチではない | requestからの `email`, `admin_name`, `role` | Cognitoの `AdminCreateUserCommand` を呼び出してuserを作成する；DynamoDBへ `Admin` のrecordを書き込む（`email`, `admin_name`, `role`, `is_deleted` はrequestから；`admin_id` はCognitoのoutputから取り出したattribute `sub`） |

| 項目 | 内容 |
|---|---|
| トリガー方法 | API Gatewayのrequest（管理画面で管理者がアカウント作成を押下する）であり、`checkRoleAdmin` を伴う ― cronバッチではない。 |

## B.2 全体概要

| 項目 | 内容 |
|---|---|
| **役割** | Cognito経由で管理者アカウントを作成／管理し、`Admin` テーブル自体にはパスワードを保存しない。 |
| **入力** | `email`, `admin_name`, `role` ― **requestにはパスワードのfieldが1つも存在せず**、旧版（passwordを直接入力する）とはまったく異なる。 |
| **出力** | DynamoDBへ `Admin` のrecordを書き込む（`email`, `admin_name`, `role`, `is_deleted` はrequestから；`admin_id` はCognitoの `AdminCreateUserCommandOutput` から取り出したattribute `sub`）― ハッシュ化すべきpasswordのfieldは存在しない。 |
| **処理概要** | 1. 呼び出し元の管理者権限をチェックする（`checkRoleAdmin`）。<br>2. inputをバリデーションする（`email`,...）。<br>3. Cognitoの `createUser(email)` を呼び出す ― パスワードのライフサイクル全体（初回設定、リセット、強度のポリシー）はCognitoが自ら管理し、本backendの範囲外である。<br>4. DynamoDBへ `Admin` のrecordを書き込む。<br>5. DBへの書き込みでエラーとなった場合→`deleteUser(email)` を呼び出し、作成したばかりのCognitoのuserを削除する（手動のrollbackであり、DBのtransactionではない）。 |

**追加の確認 ― 本backendには管理者パスワードの変更／リセットの流れが一切存在しない**：`src/` 全体に対する `ForgotPassword`／`ResetPassword`／`ChangePassword`／`AdminSetUserPassword`／`AdminResetUserPassword` のgrep → 0件。結論を裏づけるものである：管理者パスワードのライフサイクル全体（作成／変更／リセット）はすべてbackendの外側でCognitoに委ねられており、本リポジトリ内に管理者パスワードへ触れるendpointは存在しない。

---

## まとめ

なし ― 本バッチは単純な1つの動作のみであり（要求に応じて1つの文字列をハッシュ化するだけで、分岐や並列のアルゴリズムはない）、新システムがCognitoへ全面的に置き換えたことについてはファイル冒頭の概要で十分に述べている；さらに総括すべき相違点は多くない。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | メインロジック | `sources/eminelsv-develop/src/Command/HashPasswordCommand.php` |
| 旧システム | AdminUserと同じhasherであることの確認 | `sources/eminelsv-develop/src/Model/Entity/AdminUser.php:35-41` |
| 旧システム | 手作業で挿入する対象の物理テーブル（`admin_users`） | `sources/eminelsv-develop/src/Model/Table/AdminUsersTable.php:44` |
| 旧システム | 別のハッシュの仕組み（本件とは無関係） | `sources/eminel_sv_lib-develop/src/StaticServices/PasswordEncoder.php` |
| 旧システム | cron（存在しないことの確認） | `docs/02_詳細設計/10_バッチ処理/webap_cron設定_20240905.txt`, `mng-webap_cron設定_20241029.txt`, `cron実行用シェルスクリプト/eminel-webap.20240905.tgz`, `eminel-mng-webap.20240909.tgz` |
| 新システム | Cognito経由の管理者作成の流れ | `src/functions/api-admin/create-admin.ts:1-9,32-85,105-127` |
| 新システム | ローカルでのパスワードハッシュ化コード／パスワード変更の流れが存在しないことを確認するgrep | `src/` 全体に対する `bcrypt`／`hashPassword`／`hashSync`／`scrypt`／`argon2`／`ForgotPassword`／`ResetPassword`／`ChangePassword` |
