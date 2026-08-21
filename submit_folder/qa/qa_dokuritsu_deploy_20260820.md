# QA — Trả lời vế `ただし` của phiếu No. 2, kèm một câu hỏi lại

> **Ghi thêm vào BODY của chính phiếu No. 2** 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」 — đặt **ngay dưới câu hỏi gốc**, kèm **ngày**. **Không lập phiếu mới.**
> Người nhận: **mui**. Không đi qua 北ガス.

| | |
|---|---|
| Ngày soạn | 2026-08-20 |
| Đăng ở đâu | **Body** phiếu **No. 2**, ngay dưới câu hỏi gốc, mở đầu bằng dòng ngày *(user chốt 08-20)* |
| Vì sao không lập phiếu mới | Câu hỏi `ただし` là của chính phiếu No. 2. Ghi đúng chỗ thì mạch hội thoại nằm một nơi; lập phiếu mới sẽ tách làm hai chỗ. Phiếu ở `完了` **vẫn sửa/ghi thêm được** — `完了` chỉ nghĩa là mui coi việc trao đổi đã xong |
| Vì sao phải có dòng ngày | Body phiếu vốn là câu hỏi viết ngày **08-05**. Phần thêm vào ngày **08-20** mà không ghi ngày thì người đọc sau **không phân biệt được đâu là câu hỏi gốc, đâu là phần bổ sung** |
| Nguồn nội dung phần trả lời | `submit_folder/2026_08_04/report_batch_3nhom_doichieu_esmart_egw.md` dòng 103 (danh sách) + dòng 115 (tiền đề "dùng lại ≠ 0 công") |
| Phạm vi câu hỏi lại | **Chỉ một câu**: bốn chức năng đó **bê sang E-GW chạy độc lập**, hay **làm package dùng chung**? |

---

## 1. Bối cảnh

Câu trả lời của phiếu **No. 2** có **hai vế**:

> 「基本的には独立したシステムとして開発してもらう方向でお願いします。**ただし既存システムを使い続けたほうがいい機能があれば教えてほしいです**」

- **Vế đầu** = mui trả lời SYP → đã rõ: làm server E-GW thành hệ độc lập.
- **Vế sau (`ただし`)** = **mui hỏi ngược lại SYP** → SYP **chưa trả lời**. Phiếu được mui đóng ngày 13/08 mà ô `回答内容` không có thêm nội dung nào.

⇒ Comment này **trả lời vế đó**, và hỏi lại **đúng một câu** — câu mà nếu không hỏi thì không lập kế hoạch được.

---

## 2. Bản tiếng Việt — để đọc và duyệt trước khi đăng

### Phần trả lời

**Lưu ý cách hiểu**: chữ 「既存システム」 (*hệ hiện hữu*) có thể chỉ **hệ EMINEL cũ** hoặc **EMINEL-smart (ESTA) đang chạy**. Thay vì hỏi lại cho rõ (mất thêm một vòng), trả lời **cả hai** và nói rõ mình hiểu là cả hai.

**① Hệ EMINEL cũ (旧EMINEL): không có chức năng nào nên dùng tiếp nguyên trạng.**
Kết luận từ đợt điều tra 11 batch hệ cũ — chúng gắn chặt vào cấu trúc DB và cách vận hành cũ, dựng lại theo kiến trúc mới rẻ hơn là bê sang.

**② EMINEL-smart (ESTA) đang chạy: 4 chức năng nên dùng tiếp.**

| # | Chức năng | Vì sao nên dùng tiếp |
|---|---|---|
| 1 | **Hạ tầng Push (FCM)** — bảng lưu token thiết bị + các luồng gửi thông báo | Đã chạy thật, đầy đủ. Hệ cũ dùng server trung gian riêng + hàng đợi DB + cron mỗi phút — dựng lại kiến trúc đó không có lợi |
| 2 | **Hạ tầng điểm / huy hiệu + liên kết PointInfinity** | Phần gọi sang PointInfinity đã có. Việc còn lại là quy tắc tính điểm của E-GW, không phải hạ tầng |
| 3 | **Luồng nhận dữ liệu Xzilla: SFTP → S3 → DynamoDB** | Đường nhận đã có và đang chạy. Thêm loại dữ liệu mới thì thêm handler theo đúng pattern đó |
| 4 | **Cơ chế tải / xuất dữ liệu của màn hình quản trị** | Màn hình quản trị đã chốt là **dùng chung** với EMINEL-smart, nên phần này đương nhiên nối tiếp |

⚠️ **Tiền đề phải nói rõ, kẻo bị hiểu là "miễn phí"**: "dùng tiếp" ở đây nghĩa là **dùng lại code / cơ chế / pattern**. Nếu deploy độc lập thì **vẫn phải dựng lại môi trường chạy** (project riêng, bảng riêng, credential riêng). Tức **"dùng lại" ≠ "0 công"** — chỉ là rẻ hơn viết mới.

### Phần hỏi lại — đúng một câu

> **Bốn chức năng ở trên: bê sang E-GW để chạy độc lập, hay làm thành package dùng chung giữa hai hệ?**

Đây là câu quyết định trực tiếp khối lượng công, vì hai cách làm khác nhau hẳn:

| Cách | Nghĩa | Đánh đổi |
|---|---|---|
| **Bê sang E-GW chạy độc lập** | Copy code sang, E-GW tự giữ bản của mình | Hai hệ hoàn toàn không ảnh hưởng nhau, nhưng **sửa lỗi phải sửa hai nơi** |
| **Làm package dùng chung** | Tách phần chung thành package, hai hệ cùng dùng | Sửa một nơi ăn cả hai, nhưng **phải quản version và kiểm ảnh hưởng chéo** |

*(Không nêu ước lượng công của từng cách trong comment — đó là việc cần dev thẩm định, và mui vốn nắm rõ hơn về định hướng nền tảng.)*

---

## 3. 🇯🇵 【JP】Khối gửi mui — dán nguyên vẹn vào **body** phiếu No. 2, dưới câu hỏi gốc

```
────────────────────────────────
【2026/08/20 SYP追記】
「ただし既存システムを使い続けたほうがいい機能があれば教えてほしいです」への回答
────────────────────────────────

お世話になっております。SYPです。

ご回答いただいた「ただし既存システムを使い続けたほうがいい機能があれば教えて
ほしいです」について、調査結果をご報告いたします。あわせて1点ご教示いただき
たく存じます。

────────────────────────────────
1. 「既存システムを使い続けたほうがいい機能」のご報告
────────────────────────────────

「既存システム」は旧EMINELとEMINEL-smart（ESTA）の双方を指すものと解釈し、
両方についてご報告いたします。

■ 旧EMINEL：そのまま使い続けるべき機能はございません。

旧バッチ11本の調査結果に基づく判断です。いずれも旧DB構造・旧運用手順に強く
依存しており、新アーキテクチャで作り直すほうが移植よりも合理的と考えます。

■ EMINEL-smart（ESTA）：以下4点は使い続けることを推奨いたします。

(1) Push基盤（FCM）
    デバイストークン管理テーブルおよび通知配信の各フローが既に稼働しております。
    旧EMINELは中継サーバー＋DBキュー＋毎分cronの構成であり、この構成を新たに
    作り直す利点は乏しいと考えます。

(2) ポイント・バッジ基盤およびPoint Infinity連携
    Point Infinityへの連携部分は既に実装済みです。E-GW側で新たに必要となるのは
    付与ルールであり、基盤そのものではないと認識しております。

(3) Xzillaデータ受信フロー（SFTP → S3 → DynamoDB）
    受信経路が既に稼働しております。新しいデータ種別への対応は、同じパターンで
    ハンドラーを追加する形が最も確実と考えます。

(4) 管理画面のデータダウンロード・エクスポート機構
    管理画面はEMINEL-smartと共通のソースコード・共通デプロイとのご回答を
    いただいておりますので、本機構はそのまま継続する前提で認識しております。

【前提のご確認】
上記の「使い続ける」は、コード・仕組み・パターンの再利用を指しております。
独立デプロイとなる場合、実行環境（プロジェクト・テーブル・認証情報等）は
新環境に構築し直す必要があるため、「再利用」＝「工数ゼロ」ではない点を
前提として認識しております。この認識に相違がございましたらご指摘ください。

────────────────────────────────
2. ご教示いただきたい点
────────────────────────────────

上記4機能について、下記のいずれを想定されておりますでしょうか。

　a. E-GW側へ移植し、E-GWとして独立して動作させる
　b. 共通パッケージとして切り出し、両システムで共有する

工数および実装方針に直接影響いたしますため、ご教示いただけますと幸いです。

以上、よろしくお願いいたします。
```

---

## 4. Kiểm trước khi đăng

- [x] Không chứa mã quản lý nội bộ (`CLD-xx` / `GW-xx` / `F-ES-xx`) — đã rà
- [x] Không chứa đường dẫn repo hay tên file nội bộ
- [x] Không chứa ký hiệu trạng thái nội bộ (🔴 / 🔸 / mức [cao])
- [x] Không xin lại thứ mui đã cung cấp
- [x] Tiếng Nhật keigo, ngôi SYP
- [x] Chỉ hỏi **một** câu — không nhồi thêm câu về repo / library như bản nháp trước
- [x] Khối JP có **dòng ngày `【2026/08/20 SYP追記】`** ở đầu — để phân biệt với câu hỏi gốc viết ngày 08-05
- [ ] **Người duyệt đọc mục 2 (bản tiếng Việt) và xác nhận** ← chờ
- [ ] **Dán khối JP mục 3 vào body phiếu No. 2, ngay dưới câu hỏi gốc** ← chờ

## 5. Sau khi đăng

Cập nhật `memory/00_INDEX.md`: đóng Phụ lục C **#15** (đã trả lời), chuyển **#14** sang *"đã hỏi lại, đang chờ"*. Ghi ngày đăng vào đây để lần sau biết đã gửi khi nào.
