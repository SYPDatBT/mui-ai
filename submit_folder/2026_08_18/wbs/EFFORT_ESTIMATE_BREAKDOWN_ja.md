# 工数見積もり詳細 — `syp-eminelstandard-app` リファクタリング

### Task 1 — workspace構築 ＋ E-Smartを `apps/e-smart-app` へ移動

| # | 作業内容 | 工数 (md) |
|---|---|---|
| 1.1 | ルート構造を作成：`apps/`、`packages/`、`melos.yaml`（kurashi方式のglob）、`.fvm/fvm_config.json` | 0.15 |
| 1.2 | 現行の `lib/`、`android/`、`ios/`、`pubspec.yaml`、`test/` を `apps/e-smart-app/` へ丸ごと移動、内部構造は維持 | 0.15 |
| 1.3 | `pubspec.yaml` 修正（パッケージ名 `eminel_standard_app` は維持、`packages/*` へのpath dependencyを追加） | 0.1 |
| 1.4 | 関連設定ファイルのパスを確認・修正：`analysis_options.yaml`、`.gitignore`、`.github/workflows/deploy-app.yml`（working-directory）、`android/fastlane/Fastfile`、`.vscode/launch.json` | 0.3 |
| 1.5 | 再ビルド ＋ `fvm flutter analyze`（エラー0件）＋ `flutter build apk --debug`、リファクタ前のビルドと比較しエラーが発生していないことを確認 | 0.3 |
| | **Task 1 合計** | **1** |

### Task 2 — `packages/theme`、`utils`、`ui_components` の分離

| # | 作業内容 | 工数 (md) |
|---|---|---|
| 2.1 | `packages/theme`：`light_theme.dart`、`dark_theme.dart`、`app_typography.dart`、`*_extension.dart` 系ファイル（約15個）を移動；色トークン（`SemanticColors`等）を `abstract class extends ThemeExtension` に変更し、各アプリが独自の値を提供できるようにする | 1.5 |
| 2.2 | `packages/utils`：ネットワーキング（`ApiEndpoint`/Dio/interceptors、約20ファイル）、logger、SharedPreferencesラッパー、日時/URLの純粋なユーティリティを移動 | 0.5 |
| 2.3 | `packages/ui_components`：共通widgetを移動；`L10n.of(context)` を直接呼んでいるwidgetの対応（翻訳済み文字列をconstructor経由で受け取る方式に変更）；`IconSvg`/`DayOfWeek` 等の定数が本当に「UIの語彙」なのかビジネスロジックなのかを移動前に再確認 | 1 |
| | **Task 2 合計** | **3** |

### Task 3 — `packages/features/common` の分離＋DI、共通機能ごとに分解

| # | 機能 | 具体的な作業内容 | 工数 (md) |
|---|---|---|---|
| 3.1 | ログイン／Auth | `UserUseCase` から8メソッドを分離（`getTagTagToken`、`refreshToken`、`logoutTagTag`、`logoutTagTagDemo`、`saveMobileToken`、`removeMobileToken`、`getUserInfoForStartApp`、`agreeTermsOfUse`）→ `AuthUseCase`+`AuthRepository`；state 3ファイルを修正；アプリごとの設定を分離（Keycloakのclient_id、redirect scheme） | 1 |
| 3.2 | アカウント設定 / Account settings | `UserUseCase` から5メソッドを分離（`getUserSetting`、`updateUserSetting`、`getUserDetail`、`updateAppUserInfo`、`updateDeviceOrderForDisplay`）→ `AccountUseCase`+`AccountRepository`；state 3ファイルを修正 | 0.5 |
| 3.3 | ポイント／バッジ（Point & Badge） | `PointUseCase`（3メソッド、既にクリーン）を移動 — `UserUseCase` に残っているpoint/badge関連3メソッドを一緒に分離するかどうかは別途確定が必要 | 0.5 |
| 3.4 | お知らせ（News/Tip/Survey/Contact） | 既にクリーンな4つのusecase＋対応するrepositoryを丸ごと移動 | 0.5 |
| 3.5 | 機器エラー（Device Error） | `DeviceUseCase` から5メソッドを分離 → `DeviceErrorUseCase`+`DeviceErrorRepository`；state 4ファイルを修正 | 1 |
| 3.6 | TagTag（リンクポータル）＋ App state | `external_links.dart` を分離 — 共通URL（TagTagポータル）とアプリ固有URL（ログイン/メーカー）に分類；`TagtagUrlState` を移動；`MobileAppUseCase` + `S3UseCase` を丸ごと移動 | 1 |
| 3.7 | DI wiring全体 | `providers.dart` に各グループの抽象 `UsecaseProvider` を宣言 ＋ 各アプリの `main.dart` で具体的な実装をoverride | 0.5 |
| | **Task 3 合計** | | **5** |

### Task 4 — `apps/e-gw-app` の空シェル構築

| # | 作業内容 | 工数 (md) |
|---|---|---|
| 4.1 | `flutter create` で新規プロジェクト作成、デフォルトのboilerplateを削除、`packages/*` へのpath dependencyを追加 | 0.1 |
| 4.2 | Android設定：新しい `applicationId`、`namespace`、`google-services.json` の紐付け（新規Firebase project作成待ち） | 0.2 |
| 4.3 | iOS設定：新しいbundle id、`GoogleService-Info.plist`、Info.plist scheme | 0.2 |
| 4.4 | `main.dart`：`ProviderScope` の初期化、空の `go_router` 初期化（Splash/Homeのプレースホルダー route） | 0.2 |
| 4.5 | ビルド試行 ＋ エミュレータ実行、アプリが独立して起動すること・`e-smart-app` に影響しないことを確認 | 0.2 |
| | **Task 4 合計** | **0.9** |

### Task 5 — CI/CD更新

| # | 作業内容 | 工数 (md) |
|---|---|---|
| 5.1 | `deploy-app.yml` に `app` 入力パラメータ（choice：esmart/eminel）を追加、選択されたアプリに応じて `working-directory` を修正 | 0.1 |
| 5.2 | `android/fastlane/` 内のFastlane `Fastfile`/`Appfile` をアプリごとに分離／複製（またはlaneを分ける） | 0.1 |
| 5.3 | workflowを試行実行し、選択したアプリが正しくビルドされることを確認 | 0.1 |
| | **Task 5 合計** | **0.3** |

### Task 6 — `apps/e-smart-app` のリグレッションテスト（範囲拡大）

| # | 作業内容 | 工数 (md) |
|---|---|---|
| 6.1 | 全体約30 route＋主要業務フローの詳細チェックリストを作成、各フローのinput/期待outputを明記 | 0.3 |
| 6.2 | ログイン/authフローの手動テスト（login、logout、refresh token、demo mode）— `UserUseCase` から分離したばかりのため最もリスクが高い | 1 |
| 6.3 | アカウント設定フローの手動テスト（ユーザー情報更新、通知設定） | 0.5 |
| 6.4 | ポイント/バッジフローの手動テスト（ポイント獲得、バッジ確認、ランキング） | 0.5 |
| 6.5 | お知らせフローの手動テスト（news、tip、survey、contact） | 0.5 |
| 6.6 | 機器エラーフローの手動テスト（エラー一覧、エラー詳細、dashboardでのエラー非表示） | 0.5 |
| 6.7 | 残りのE-Smart専用フローの手動テスト、ファイル移動によるエラーが発生していないことを確認（機器制御、automation、dr、integration、sensor、room_monitoring等） | 1.5 |
| 6.8 | テスト結果をリファクタ前の実際の挙動と対比し、差異があれば記録 | 0.5 |
| 6.9 | 発見された問題の記録＋対応（テスト中に見つかったバグの修正） | 1 |
| | **Task 6 合計** | **6.3** |

---

## 6つのTask全体のまとめ

| Task | 工数 (md) |
|---|---|
| 1. workspace構築＋E-Smart移動 | 1 |
| 2. theme/utils/ui_components の分離 | 3 |
| 3. features/common の分離＋DI（機能ごと） | 5 |
| 4. e-gw-app 空シェル構築 | 0.9 |
| 5. CI/CD更新 | 0.3 |
| 6. e-smart-app リグレッションテスト（範囲拡大） | 6.3 |
| **合計** | **16.5** |

---

## 実施方針

### Phase 1 — workspace基盤 ＋ クリーンな共通パッケージ

| Task | 工数 (md) |
|---|---|
| 1. workspace構築＋E-Smart移動 | 1 |
| 2. theme/utils/ui_components の分離 | 3 |
| 4. e-gw-app 空シェル構築 | 0.9 |
| 5. CI/CD更新 | 0.3 |
| **Phase 1 合計** | **5.2** |

### Phase 2 — Auth（`e-gw-app` がログインできる最小限）＋ 対応するテスト

| # | 作業内容 | 工数 (md) |
|---|---|---|
| 3.1 | ログイン / Auth | 1 |
| 3.7 | DI wiring（Auth用） | 0.5 |
| 6.1 | 全体約30 route＋主要業務フローの詳細チェックリスト作成 | 0.3 |
| 6.2 | ログイン/authフローの手動テスト（login、logout、refresh token、demo mode） | 1 |
| 6.7 | 残りのE-Smart専用フローの手動テスト、ファイル移動によるエラーが発生していないことを確認 | 1.5 |
| 6.8 | テスト結果をリファクタ前の実際の挙動と対比 | 0.5 |
| 6.9 | 発見された問題の記録＋対応 | 1 |
| | **Phase 2 合計** | **5.8** |

→ Phase 1 + Phase 2 = 11 md、2名で並行作業すれば約1週間で完了。

### Phase 3 — 残りの共通機能 ＋ 対応するテスト

| 内容 | 工数 (md) |
|---|---|
| Task 3 の残り：アカウント設定（3.2）、ポイント/バッジ（3.3）、お知らせ（3.4）、機器エラー（3.5）、TagTag＋app state（3.6） | 3.5 |
| Task 6 の残り：アカウント設定、ポイント/バッジ、お知らせ、機器エラーに対応するテスト | 2 |
| **Phase 3 合計** | **5.5** |
