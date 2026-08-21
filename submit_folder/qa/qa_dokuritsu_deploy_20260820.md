# QA — Server E-GW độc lập: trả lời vế `ただし` + hỏi mức độ độc lập

> Phiếu QA **mới** để lập trên QAデータベース (Notion). Gộp 2 việc của Phụ lục C guide: **#15** (trả lời câu mui đã hỏi SYP) + **#14** (hỏi lại phần mui chưa nói).
> Người nhận: **mui**. Không đi qua 北ガス.

| | |
|---|---|
| Ngày soạn | 2026-08-20 |
| Lý do lập phiếu mới | Phiếu cũ **No. 2** 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」 đã ở trạng thái **完了** (chốt 2026-08-13) ⇒ không trả lời vào đó được nữa |
| Nguồn nội dung vế trả lời | `submit_folder/2026_08_04/report_batch_3nhom_doichieu_esmart_egw.md` dòng 103 (danh sách) + dòng 115 (tiền đề "dùng lại ≠ 0 công") |
| Cách viết vế hỏi | **Cách ⓐ** — hỏi thẳng, không nêu phương án kèm ước lượng công *(vì ước lượng công là việc của dev, người soạn phiếu không tự thẩm định được)* |

---

## 1. Bối cảnh — vì sao lập phiếu này

Câu trả lời của phiếu **No. 2** có **hai vế**:

> 「基本的には独立したシステムとして開発してもらう方向でお願いします。**ただし既存システムを使い続けたほうがいい機能があれば教えてほしいです**」

- **Vế đầu** = mui trả lời SYP → đã rõ: làm server E-GW thành hệ độc lập.
- **Vế sau (`ただし`)** = **mui hỏi ngược lại SYP** → **SYP chưa bao giờ trả lời**, và phiếu đã bị đóng ngày 13/08.

Đồng thời câu trả lời **không nói mức độ độc lập** (chung library/source hay không). Phiếu đã đóng nên chờ thêm là vô ích.

⇒ Phiếu này làm **hai việc cùng lúc**: trả lời phần SYP nợ, và hỏi phần còn thiếu. Hai việc đi cùng nhau có lý: **danh sách chức năng muốn dùng lại chính là lý do cần biết mức độ độc lập** — muốn dùng lại hạ tầng Push của EMINEL-smart thì phải biết được phép chung tới đâu.

---

## 2. Bản tiếng Việt — để đọc và duyệt trước khi gửi

### Vế 1 — Trả lời câu 「既存システムを使い続けたほうがいい機能」

**Lưu ý cách hiểu**: chữ 「既存システム」 (*hệ hiện hữu*) có thể chỉ **hệ EMINEL cũ** hoặc **EMINEL-smart (ESTA) đang chạy**. Thay vì hỏi lại cho rõ (mất thêm một vòng), phiếu trả lời **cả hai**, và nói rõ mình hiểu là cả hai.

**① Hệ EMINEL cũ (旧EMINEL): không có chức năng nào nên dùng tiếp nguyên trạng.**
Kết luận từ đợt điều tra 11 batch của hệ cũ. Các batch đó gắn chặt vào cấu trúc DB và cách vận hành cũ, dựng lại theo kiến trúc mới rẻ hơn là bê sang.

**② EMINEL-smart (ESTA) đang chạy: 4 chức năng nên dùng tiếp.**

| # | Chức năng | Vì sao nên dùng tiếp |
|---|---|---|
| 1 | **Hạ tầng Push (FCM)** — gồm bảng lưu token thiết bị và các luồng gửi thông báo | Đã chạy thật, đầy đủ. Hệ cũ dùng server trung gian riêng + hàng đợi trong DB + cron mỗi phút — dựng lại kiến trúc đó không có lợi |
| 2 | **Hạ tầng điểm / huy hiệu + liên kết PointInfinity** | Phần gọi sang PointInfinity đã có. Việc còn lại là quy tắc tính điểm của E-GW, không phải hạ tầng |
| 3 | **Luồng nhận dữ liệu Xzilla: SFTP → S3 → DynamoDB** | Đường nhận đã có sẵn và đang chạy. Thêm loại dữ liệu mới thì thêm handler theo đúng pattern đó |
| 4 | **Cơ chế tải / xuất dữ liệu của màn hình quản trị** | Màn hình quản trị đã chốt là **dùng chung** với EMINEL-smart, nên phần này đương nhiên nối tiếp |

⚠️ **Tiền đề phải nói rõ, kẻo bị hiểu là "miễn phí"**: ở đây **"dùng tiếp" nghĩa là dùng lại code / cơ chế / pattern**. Nếu chốt là **deploy độc lập** thì **vẫn phải dựng lại môi trường chạy** trên hạ tầng mới (project riêng, bảng riêng, credential riêng). Tức **"dùng lại" ≠ "0 công"** — chỉ là rẻ hơn viết mới.

### Vế 2 — Hỏi mức độ độc lập

Câu trả lời trước ghi 「**基本的には**独立したシステムとして」 (*về cơ bản là hệ độc lập*). SYP hiểu là đã chốt hướng độc lập. Nhưng để lập kế hoạch thì cần biết **độc lập đến mức nào**, cụ thể:

1. **Source code** — hai hệ dùng **chung repository** hay **tách repository riêng**?
2. **Thư viện / thành phần dùng chung** — có được **chia sẻ library chung** giữa hai hệ không, hay mỗi hệ tự giữ bản của mình?
3. **Bốn chức năng ở vế 1** — "dùng tiếp" ở đây mui hình dung là **gọi sang hệ đang chạy**, hay là **bê code sang dựng lại trên môi trường E-GW**?

Câu 3 là câu quan trọng nhất, vì nó quyết định trực tiếp khối lượng công.

---

## 3. 🇯🇵 【JP】Khối gửi mui — dán nguyên vẹn

### Tiêu đề phiếu

```
EMINEL-smartサーバーの独立範囲について（「既存システムを使い続けたほうがいい機能」の回答を含む）
```

### Nội dung

```
お世話になっております。SYPです。

「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」にてご回答いただいた
「ただし既存システムを使い続けたほうがいい機能があれば教えてほしいです」について、
調査結果をご報告いたします。あわせて、独立の範囲について1点ご教示いただきたく、
本チケットを起票いたしました。

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
2. 独立の範囲についてのご質問
────────────────────────────────

「基本的には独立したシステムとして開発してもらう方向で」とのご回答をいただき、
独立の方向性は承知いたしました。実装計画を立てるにあたり、その範囲について
以下3点をご教示いただけますでしょうか。

(1) ソースコードは、EMINEL-smartと同一リポジトリとするか、
    別リポジトリに分離するか、いずれの想定でしょうか。

(2) 共通ライブラリ・共通コンポーネントを両システム間で共有することは
    可能でしょうか。それとも各システムで個別に保持する想定でしょうか。

(3) 上記1でご報告した4機能について、「使い続ける」とは
    　a. 稼働中のEMINEL-smart側の機能を呼び出す形
    　b. コードを移植しE-GW環境上に構築し直す形
    のいずれを想定されておりますでしょうか。

(3)が工数に最も影響いたしますため、可能でしたら優先的にご教示いただけますと
幸いです。

以上、よろしくお願いいたします。
```

---

## 4. Kiểm trước khi gửi

- [x] Không chứa mã quản lý nội bộ (`CLD-xx` / `GW-xx` / `F-ES-xx`) — đã rà
- [x] Không chứa đường dẫn repo hay tên file nội bộ
- [x] Không chứa ký hiệu trạng thái nội bộ (🔴 / 🔸 / mức [cao])
- [x] Không xin lại thứ mui đã cung cấp
- [x] Tiếng Nhật keigo, ngôi SYP
- [ ] **Người duyệt đọc mục 2 (bản tiếng Việt) và xác nhận** ← chờ
- [ ] **Lập phiếu trên QAデータベース và dán khối JP mục 3** ← chờ

## 5. Sau khi gửi

Ghi lại **số phiếu** Notion cấp vào file này, rồi cập nhật `memory/00_INDEX.md`: đóng việc **#15**, chuyển **#14** từ *"phải mở phiếu mới"* sang *"đã hỏi, đang chờ"*.
