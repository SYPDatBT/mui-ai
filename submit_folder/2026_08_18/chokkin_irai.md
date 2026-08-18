# 直近の依頼

# 開発環境構築：こちらから始めたい

- AWSの開発環境をE-Smartとは別に用意したい
    - E-Smart：dev/stg/本番 → E-GWリリースまでにE-Smart対応が入る可能性がある
    - E-GW：dev’ → これがとりあえず欲しい
        - E-Smart devはアプリ審査で使うため別環境を作る

- BE/管理画面/モバイルアプリ GitHubブランチ戦略
    - E-GW
        - syp-gw-dev：dev’環境向け
            - syp-devから派生
            - syp-devで対応したらsyp-gw-devにも都度取り込み
        - gw-develop：すぐには必要ないが実地検証時までには必要になる見込み
    - E-Smart
        - syp-dev：dev環境向け
        - develop：stg環境向け
        - main：本番環境向け

- BE/管理画面/モバイルアプリすべて上記のブランチ戦略で進めたい
- モバイルアプリはブランチ戦略を上記で進めつつ、次のイメージでフォルダ構成も再編したい
    - rootフォルダ
        - apps：アプリ固有ソースコード層
            - e-smart-app：e-smart専用ソースコード
            - e-gw-app：e-gw専用ソースコード
        - package：全アプリ共通コード
            - theme：共通テーマ
            - ui_components：共通ウィジェットソースコード

# E-Smartリファクタ：開発環境構築後に対応

- モデル名リファクタのレビュー
- ソースコードの構成変更
    - 共通層とアプリ層を分ける
    - アプリごとにthemeを持つ
    - アプリごとにtheme色が変わる

# バックエンドのタスク一覧についての調査

- LegacyEminelには定期処理(バッチ処理)がたくさんある。それぞれのタスクの処理概要について調査して、移行後の構成にとって必要かどうか判断してほしい
    
    [](https://github.com/muilab/legacy_eminel_docs/tree/main/docs/02_%E8%A9%B3%E7%B4%B0%E8%A8%AD%E8%A8%88/10_%E3%83%90%E3%83%83%E3%83%81%E5%87%A6%E7%90%86)
    
    - EMINEL Gateway 統合要件定義書 v1.2
    - 04_バッチ一覧.md