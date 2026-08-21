# Báo cáo ngày 2026-08-20 — Rà 10 phiếu QAデータベース và cập nhật bộ tài liệu

> ⚠️ **FILE NỘI BỘ, TIẾNG VIỆT.** Không nộp cho mui / 北ガス. Nếu cần bản gửi mui thì soạn riêng bằng tiếng Nhật keigo, sạch ký hiệu nội bộ.

| | |
|---|---|
| Người làm | LTDH |
| Ngày | 2026-08-20 |
| Việc | Đối chiếu **10 phiếu QAデータベース (Notion)** với 2 tài liệu nội bộ, sửa mọi chỗ lệch |
| Tài liệu bị sửa | `requirements/onboarding_guide.md` ・ `requirements/self_study_plan.md` ・ `memory/00_INDEX.md` ・ `memory/09_session_…md` ・ `submit_folder/2026_08_18/output_schedule.md` |
| Khối lượng | **11 commit**, `+817 / −46` dòng (riêng guide `286` dòng thay đổi) |
| Mốc repo tài liệu dự án | `eminel_gw_project` = `1100487` (không pull trong ngày, đã kiểm `git log -1`) |

---

## 1. Kết luận trước — ba điều quan trọng nhất của cả ngày

**① Phạm vi đối ứng của SYP nay là chuyện ĐÃ CHỐT, không còn là phỏng đoán.**
mui xác nhận bảng phân công 5 khối. Trước hôm nay, tài liệu học vẫn treo nhãn *"🔸 giả thuyết — chưa kiểm chứng"* ở chỗ này.

| Khối chức năng | 担当 (đảm nhận) |
|---|---|
| 7-1. E-GW機能（ファームウェア） — phần mềm chạy trong gateway | **mui Lab** |
| 7-2. GW管理クラウド機能 — tầng cloud trông coi thiết bị | **mui Lab** |
| **7-3. EMINEL-smartサーバー機能** — server nghiệp vụ | **SYP** |
| **7-4. 管理画面機能** — màn hình quản trị | **SYP** |
| **モバイルアプリ** — app điện thoại | **SYP** |

⚠️ **Chỗ dễ hiểu sai nhất**: `GW管理クラウド` là của **mui Lab**, KHÔNG phải SYP. Tài liệu yêu cầu tích hợp (`統合要件定義書 v1.2`) mục 1-2 gộp nó chung một dòng với server EMINEL-smart (「EMINEL-smartサーバー（**GW管理クラウド含む**）」), nên đọc nhanh là tưởng cùng một chủ. Hai bảng đó trả lời hai câu khác nhau:

| Thuật ngữ | Đọc là | Trả lời câu hỏi |
|---|---|---|
| **対象範囲** (*taishō han'i*) | phạm vi đối tượng | **Dự án có làm cái đó không?** |
| **担当** (*tantō*) | đảm nhận / phụ trách | **Trong những cái có làm, ai làm?** |

**② Mục chặn việc SỐ MỘT của dự án hoá ra nghẽn ở mui, không phải ở 北ガス.**
Điều kiện phân loại lỗi 重篤 (*nặng*) / 軽微 (*nhẹ*) — thứ đang chặn **hai màn hình mới hoàn toàn** — đã được hỏi từ 03/08. Phía mui trả lời rằng **họ còn chưa liệt kê được danh mục lỗi**, và sẽ 「結構後になる」 (*khá muộn*). Chi tiết ở mục 4-②.

**③ Có một câu hỏi mui đặt cho SYP đã rơi mất.**
Phiếu No. 2 kèm vế `ただし` = mui hỏi ngược lại SYP. SYP không trả lời, mui vẫn đóng phiếu ngày 13/08. Mất **kênh** trả lời, không mất **việc**. Chi tiết ở mục 5-①.

---

## 2. Mười phiếu QA đã rà — trạng thái và kết luận

| No. | Tiêu đề phiếu | ステータス | Kết luận |
|---|---|---|---|
| **1** | 担当範囲（サーバー／管理画面）とアプリ対象外の確認 | ✅ 完了 | Mobile app **là** đối tượng phát triển |
| **2** | 旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認 | ✅ 完了 | Server E-GW làm thành **hệ độc lập** với E-Smart |
| **3** | 管理画面は独立か共通か（切替モード追加）の確認 | ✅ 完了 | Admin **chung source code + chung deploy** với E-Smart |
| **4** | 旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認 | ✅ 完了 | Phạm vi **điều tra** = `conciergesv` + `eminelsv`; `hemssv` ngoài phạm vi |
| **5** | バッジ・ランクは2026年度対応スコープでしょうか | ✅ 完了 | 「今の所、2026年スコープ外です」 |
| **6** | エラー種別（重篤／軽微）の判定条件についてご教示ください | 🟡 **回答中** | 「要仕様検討中」 + comment: **còn lâu** |
| **7** | 「依頼: モバイルアプリ構成の変更」について確認 | ✅ 完了 | Cách **hiểu đề bài** tái cấu trúc app là đúng |
| **9** | 設計書の最終成果物のファイル形式について | ✅ 完了 | 画面 → **Excel** ・ API → **markdown** |
| **10** | SYP開発範囲の確認 | ✅ 完了 | Bảng 担当 5 khối ở mục 1-① |
| **12** | 2027年劣後機能の確認 | 🔶 **確認中** | **Chưa có câu trả lời nào** |

*(Bảng trên là 10 phiếu của đợt rà đầu. Cuối buổi rà thêm **No. 8** — chốt cách gắn `GW-ID` ↔ `TagTag ID`, bỏ `EMS-SP番号` — và **No. 14** — thời hạn truy ngược 24 tháng. **No. 11 và No. 13 không tồn tại** trên QAデータベース, có vẻ đã bị xoá. ⇒ **đã rà hết dãy: 12 phiếu**.)*

### Nhịp làm việc của mui trên QAデータベース

Chi tiết này đáng ghi vì nó quyết định **nên chờ hay nên thúc**:

| Phiếu | 起票 (lập phiếu) | Chốt / cập nhật gần nhất |
|---|---|---|
| No. 1 | 08-03 **17:30** | 08-13 **12:27** |
| No. 2 | 08-03 **17:31** | 08-13 **12:28** |
| No. 3 | 08-03 **17:32** | 08-13 **12:28** |
| No. 4 | 08-03 **17:32** | 08-13 **12:28** |
| No. 5 | 08-03 **17:33** | 08-13 **12:28** |
| No. 7 | 08-03 19:22 | 08-13 **12:34** |
| No. 9 | 08-10 17:06 | 08-13 **12:34** |
| No. 10 | 08-12 16:17 | 08-13 **12:28** |
| **No. 6** | 08-03 17:33 | **08-19 10:43** ← ngoài đợt, **vẫn đang xử lý** |
| **No. 12** | 08-12 17:41 | **08-12 17:46** ← lập trước đợt mà **bị để lại** |

```
08-03 chiều   SYP lập 5 phiếu liên tiếp từng phút (17:30 → 17:33)
                          │
                     (10 ngày im lặng)
                          │
08-13 12:27–12:34   mui đóng CẢ TÁM phiếu trong 7 phút
                          │
                          ├── No. 6  → KHÔNG đóng, nhưng 08-19 có comment thật
                          └── No. 12 → KHÔNG đóng, không ai chạm tới
```

⇒ **mui dọn QA theo đợt**, không trả lời rải rác. Ba kiểu ứng xử khác nhau:
- Phiếu bình thường → **chờ đợt dọn tiếp** là được.
- **No. 6** → đang được xử lý thật, nhưng mui nói còn lâu.
- **No. 12** → lập **trước** đợt 08-13 mà vẫn bị bỏ ⇒ **bỏ qua có chọn lọc, phải thúc**.

---

## 3. Những chỗ tài liệu đang SAI hoặc thiếu — đã sửa hết

### 3.1 `onboarding_guide.md`

| Mục | Trước | Sau |
|---|---|---|
| §0.2 | *"cách chạy cụ thể **đang chốt** qua QA 08/2026"* | Đã chốt qua QA 08-13 |
| §0.3 bảng mốc kiểm | QAデータベース: *"lần đọc 08-04, **chưa kiểm lại**"* | Kiểm 08-20, **10 phiếu**, tách 3 nhóm trạng thái |
| §1.2 | Hai trả lời *"đều còn 回答中 — chưa chốt"* | Tách 2 bullet: server = No. 2 完了 ・ admin = No. 3 完了 |
| §1.3 | SYP *"**dự kiến** làm luôn server E-GW"* | 3 khối đã đảm nhận (giữ nguyên văn 「担当想定」 của nguồn, kèm chú là cách viết cũ) |
| **§1.6** | Chỉ có 1 bảng 対象範囲 | Tách **bảng ① 対象範囲** + **bảng ② 担当 (MỚI)** + 3 cảnh báo cách đọc |
| §1.6 cuối | *"vế hỏi kèm **chưa được trả lời**"* | Bảng "chỗ hở hồi 08-03 → nay ra sao" |
| §4.2 | Phiếu hemssv: *"trạng thái khi đọc (08-04): 回答中"* | **No. 4**, 完了, chốt 08-13 12:28 |
| **§6.1** | Bảng 4 nhóm mã, không có cột 担当 | Thêm **2 cột: 「Mục trong v1.2」 (7-1〜7-4) + 「担当」**; ghi rõ app dùng mã **F-AP**, ngoài 7-1〜7-4 nhưng vẫn SYP làm |
| §6.x huy hiệu (A4) | *"trả lời tạm… 回答中"* | **No. 5** 完了, kèm 2 điều dè dặt phải giữ |
| §7.1 bản đồ 6 tầng | Chỉ 6 tầng trong repo | Thêm cảnh báo: sau 6 tầng còn **設計書** = thứ SYP **giao nộp** |
| **§7.4③** (lỗi 重篤/軽微) | Chỉ nói "điều kiện chưa có" | Thêm mục **⏳「Đã hỏi rồi — và mui trả lời là còn lâu」** |
| **§7.7** | *(không có)* | **MỤC MỚI**: 設計書 — định dạng file bản giao nộp |
| §7.x (nháp admin) | *"đã xác nhận qua QA Notion (**còn 回答中**)"* | Chốt qua phiếu No. 3 |
| §8.x | *"Tiền đề 「同一コードベース」 **có thể thay đổi** theo QA2"* | **"đã bị vượt qua"** |
| **§9.4** | 4 phiếu, không có cột trạng thái, nhãn 🔸 giả thuyết | Cột `No.` + cột **ステータス** (cả 4 完了) ・ khối ✅ chốt phạm vi ・ điểm 2 viết lại 3 tầng ・ **mục mới về vế `ただし` bị rơi** |
| **Phụ lục B.1** | 🔴 Cao, *"回答中, đọc 08-04"* | **🟠 Vừa**, No. 5 完了 + khối diễn biến No. 12 |
| **Phụ lục C** | 12 mục, *"cả 12 đều cần 北ガス"* | **15 mục** + bảng phân loại "kiểu bị chặn"; #1 sửa thành **"mui trước, rồi 北ガス"** |
| **Phụ lục E.2** | ステータス có 2 giá trị | **4 giá trị** + mục 「**5 cái bẫy của QAデータベース**」 |

### 3.2 Ngoài guide

| File | Sửa |
|---|---|
| `requirements/self_study_plan.md` dòng 83 | 管理画面 *"QA masao takahashi, 08-03, **回答中**"* → phiếu **No. 3, 完了** |
| `submit_folder/2026_08_18/output_schedule.md` mục 1 | Thêm khối ✅ cách hiểu đề bài đã được xác nhận (phiếu No. 7) |

📌 **Bài học quy trình**: chỗ ở `self_study_plan.md` **chỉ bắt được vì rà cả thư mục `requirements/`**, không chỉ guide. Từ nay mỗi lần một phiếu QA đổi trạng thái phải `grep 回答中` trên **cả `requirements/`**.

---

## 4. Kết luận nghiệp vụ mới — và những chỗ KHÔNG được đọc quá

### ① Server E-GW: độc lập — nhưng chỉ chốt một nửa

| | Nội dung |
|---|---|
| ✅ **Đã chốt** | Làm server E-GW thành **hệ độc lập** với E-Smart hiện hành |
| ⚠️ **Phải giữ** | Chữ 「**基本的には**」 (*về cơ bản là*) còn nguyên trong nguyên văn — là chữ nhượng bộ. **Không nói với dev là "độc lập tuyệt đối"** |
| ❌ **Chưa ai nói** | Độc lập **đến mức nào** (chung library/source hay không). Phiếu **đã đóng mà vẫn không nói** ⇒ **chờ tiếp là vô ích**, muốn biết phải mở phiếu QA mới |

### ② Phân loại lỗi 重篤/軽微 — nghẽn ở mui, và "còn lâu"

Phiếu No. 6, ô `回答内容` chỉ ghi 「要仕様検討中」. Nhưng trong phần **Comments**:

> masao takahashi (mui), 2026-08-19:
> 「まだ、エラー内容を洗い出せていないですので、**結構後になる**かと思います。」
> *"Bên chúng tôi còn chưa liệt kê ra được các nội dung lỗi, nên tôi nghĩ việc này sẽ khá muộn."*

**Ba điều rút ra:**
1. Điểm nghẽn **ở chính mui**, không phải 北ガス — chưa có danh mục lỗi thì không bàn được điều kiện phân loại. ⇒ **Không gộp câu này vào bảng QA gửi khách nữa.**
2. **Đừng lên kế hoạch dựa vào chỗ này.** Màn hình **C (quản lý E-GW) thuộc phạm vi 2026** mà đang bị chặn ở đây ⇒ cần bàn phương án **làm trước phần không phụ thuộc phân loại lỗi**.
3. Câu trả lời thực chất nằm ở **Comments**, không ở ô `回答内容`.

### ③ Huy hiệu / xếp hạng — đã ngả về 劣後 nhưng chưa xoá khỏi bảng mâu thuẫn

Phiếu No. 5 完了 với nội dung 「今の所、2026年スコープ外です」. Mục B.1 chỉ **hạ mức 🔴 → 🟠**, **không xoá**, vì:
1. Chữ 「**今の所**」 (*hiện tại thì*) là mốc thời điểm, không phải kết luận vĩnh viễn.
2. Đây là trả lời của **mui**, không phải xác nhận của **北ガス** — mà người quyết phạm vi là 北ガス.
3. File `A04_badge_rank.md` **vẫn** viết toàn bộ huy hiệu vào 「26年対応スコープ」 — chữ trên giấy còn vênh.

### ④ Định dạng bản giao nộp 設計書

| Loại tài liệu thiết kế | Định dạng nộp |
|---|---|
| **画面** (màn hình) | **Excel** |
| **API** | **markdown** |

⚠️ **Không suy rộng**: câu trả lời chỉ nói về **設計書**. Hai tầng `3_requirements` và `4_spec` vẫn là **markdown trong repo git**, không đổi.

---

## 5. Việc phát sinh — 3 mục mới trong danh mục chặn việc

Phụ lục C của guide trước có 12 mục, **tất cả đều hỏi 北ガス**. Ba mục mới thì không:

| # | Việc | Kiểu bị chặn | Ai phải hành động |
|---|---|---|---|
| **13** | Danh sách chức năng lùi sang 2027 (劣後) | Đã hỏi (phiếu No. 12), **đang chờ** — mà phiếu bị bỏ qua có chọn lọc | **Thúc mui** |
| **14** | Mức độ độc lập của server E-GW | Đã hỏi, phiếu **đã đóng** mà câu trả lời **không chứa thông tin cần** | **Mở phiếu QA mới** — chờ phiếu cũ là vô ích |
| **15** | Chức năng nào của hệ hiện hữu nên dùng tiếp | mui hỏi SYP (vế `ただし`), **SYP chưa trả lời**, phiếu đã đóng mất kênh | **SYP** — chính mình |

### ① Chi tiết mục #15 — câu hỏi mui đặt cho SYP đã rơi mất

Câu trả lời phiếu No. 2 có **hai vế**. Vế sau là mui hỏi ngược lại:

> 「**ただし**既存システムを使い続けたほうがいい機能があれば教えてほしいです」
> *"Nhưng nếu có chức năng nào nên tiếp tục dùng của hệ hiện hữu thì cho chúng tôi biết."*

Kiểm ô `回答内容` ngày 20/08: **không có nội dung nào thêm** so với bản đọc 04/08 ⇒ SYP chưa bao giờ trả lời, mui tự đóng phiếu. Việc này treo trong hàng đợi từ 04/08 qua **5 phiên làm việc** rồi rơi.

**Nội dung trả lời thì đã soạn xong từ lâu**, nằm ở `submit_folder/2026_08_04/report_batch_3nhom_doichieu_esmart_egw.md` **dòng 103** (bản tiếng Nhật: `2026_08_05/旧EMINELバッチ移行判定報告書_3グループ11本.md` §2.2-1):

- **① Hệ CŨ (旧EMINEL)**: không có batch nào đáng dùng tiếp nguyên trạng.
- **② Hệ ĐANG CHẠY (e-smart / ESTA)**: **4 ứng viên** — hạ tầng Push (FCM) ・ hạ tầng point/badge + liên kết PointInfinity ・ luồng nhận Xzilla (SFTP → S3 → DynamoDB) ・ cơ chế admin download/export.
- **Tiền đề kèm theo** (cùng báo cáo, dòng 115): "dùng lại" = dùng lại **code/cơ chế/pattern**; nếu deploy độc lập thì **vẫn phải dựng lại môi trường chạy** ⇒ "dùng lại" **≠ 0 công**.

**Cần quyết kênh**: ⓐ mở **phiếu QA mới** (nên gộp chung với mục #14 vì cùng chủ đề "server độc lập"), hay ⓑ nêu khi trình thiết kế.
Cách gỡ điểm treo cũ *"chưa biết 「既存システム」 ý chỉ hệ nào"*: **trả lời luôn cả hai vế**, mở đầu bằng một câu *"chúng tôi hiểu 「既存システム」 gồm cả hai nên xin trả lời cả hai"* — khỏi mất thêm một vòng hỏi lại.

---

## 6. Phát hiện về cách dùng QAデータベース — 5 cái bẫy

Đã ghi thành mục riêng trong Phụ lục E.2 của guide. Đây là phần dùng lại được cho mọi lần trích QA về sau.

**Ô `ステータス` có BỐN giá trị, không phải hai:**

| Giá trị | Nghĩa | Dùng làm căn cứ được chưa? |
|---|---|---|
| **確認中** | Phiếu mới lập, **chưa ai trả lời** (ô `回答内容` trống) | ❌ Không có gì để dùng |
| **回答中** | **Đã có nội dung** nhưng phiếu chưa đóng | ❌ Chưa — còn có thể bị bổ sung hoặc đổi |
| **回答済** | Đã trả lời xong | ✅ Được |
| **完了** | Đã đóng phiếu — **cùng nghĩa 回答済** | ✅ Được |

⚠️ Guide trước chỉ liệt kê `回答中` / `回答済` ⇒ **ai lọc theo `回答済` để tìm phiếu đã đóng sẽ SÓT** toàn bộ phiếu ghi `完了`.

**Năm cái bẫy:**

1. **`更新日時` KHÔNG phải ngày viết câu trả lời** — là ngày sửa gần nhất, thường chỉ là lúc *đổi trạng thái*. Phiếu No. 1: nội dung trả lời có từ 03/08 nhưng `更新日時` = 13/08, **lệch 10 ngày**. Khi trích phải ghi cả hai mốc.
2. **mui đóng phiếu theo ĐỢT** ⇒ trạng thái đọc từ lâu là vô giá trị; thấy một phiếu vừa đổi thì mở luôn các phiếu cùng chủ đề.
3. **`質問内容` có thể để trống** dù câu hỏi vẫn tồn tại — nội dung thật nằm ở **body trang**. Cả 10 phiếu hôm nay đều trống ô này. Thấy Empty **đừng kết luận "phiếu rỗng"**.
4. **Ngày hiển thị kiểu tương đối** ("Last Thursday 12:28 PM") — trỏ chuột lấy ngày tuyệt đối trước khi trích.
5. ⭐ **PHẢI ĐỌC CẢ PHẦN `Comments`** — câu trả lời thực chất có thể nằm ở đó (đúng ca phiếu No. 6). Và **tên người trả lời có thể chỉ có trong Comments** khi ô `回答者` trống ⇒ khi trích ghi *"theo comment của X ngày Y"*, không gán vào ô `回答者`.

⚠️ **Nguyên tắc bao trùm: phiếu `完了` KHÔNG có nghĩa là hết dè dặt.** Đóng phiếu **không thêm chữ nào** vào câu trả lời, nên các chữ nhượng bộ (「基本的には」「今の所」) và chuyện "mui trả lời ≠ 北ガス xác nhận" vẫn còn nguyên.

**Ba phiếu có ô `回答者` để trống**: No. 7 ・ No. 9 ・ No. 6. Theo xác nhận trong ngày: phía mui quên điền, vẫn dùng được câu trả lời — nhưng **không gán tên ai** khi trích, và trọng lượng thấp hơn phiếu có tên.

---

## 7. Việc còn treo sau ngày hôm nay

| # | Việc | Ghi chú |
|---|---|---|
| 1 | **Chạy review vùng sửa** của guide | Bắt buộc theo quy trình nội bộ (3 vòng). Phạm vi = `git diff 432867d..HEAD -- requirements/onboarding_guide.md`, không quét lại 4.400 dòng |
| 2 | Quyết guide có đánh số lên **v1.4** không | Hiện là "v1.3 + đợt vá 20/08"; bảng meta đầu guide chưa sửa số |
| 3 | ~~Mở phiếu No. 8 và No. 11~~ | ✅ **Xong cuối buổi**: No. 8 và No. 14 đã rà; **No. 11 và No. 13 không tồn tại** (đã bị xoá) ⇒ hết dãy |
| 4 | Ba mục #13–#15 của Phụ lục C | Xem mục 5 |
| 5 | Bàn phương án làm màn hình **C** không phụ thuộc phân loại lỗi | Vì mui nói "còn lâu" mà C thuộc phạm vi 2026 |

⏰ **Nhắc việc có hạn, không thuộc phạm vi báo cáo này**: cửa sổ phản ánh feedback cho bản báo cáo tái cấu trúc source app là **20–21/08**, tuần implement bắt đầu **24/08**.

---

## 8. Danh sách commit

| Commit | Nội dung |
|---|---|
| `67475b9` | Phạm vi SYP chốt theo QA No. 10 → guide có bảng 担当 |
| `f0f684c` | Phiếu No. 1 完了 |
| `173d257` | Phiếu No. 2 完了 → chốt hướng server độc lập |
| `d3ef0b0` | Phiếu No. 3 完了 → chốt admin dùng chung |
| `1f24763` | Thêm quy tắc nội bộ ⛔#0b (cách trả lời) |
| `e7dd5a7` | Phiếu No. 4 完了 → bảng 4 phiếu §9.4 sạch |
| `eb097b0` | Phiếu No. 5 完了 → hạ B.1 xuống 🟠, không xoá |
| `b4bd90a` | Phiếu No. 7 → cách hiểu đề bài app đã được xác nhận |
| `6b2ddd8` | Phiếu No. 9 → guide có mục mới §7.7 |
| `6f0b074` | Phiếu No. 12 `確認中` → Phụ lục C thêm 3 mục |
| `2f952a2` | Phiếu No. 6 → câu trả lời ở Comments, đảo giả định Phụ lục C #1 |

**Kiểm cơ học sau mỗi lượt vá** (guide): 277 heading ・ **215 liên kết nội bộ, 0 hỏng** ・ 70 dấu ``` (chẵn) ・ mọi bảng khớp số cột ・ audit toàn văn chữ `回答中` (các chỗ còn lại đều là mô tả lịch sử, hợp lệ).

⚠️ Hai lỗi tự phát hiện và tự sửa trong ngày, ghi lại để không tái diễn:
1. Script kiểm liên kết viết lần đầu báo **62 link hỏng** — SAI, do quy tắc sinh anchor. Suýt sửa 62 liên kết đang đúng.
2. Câu 「`更新日時` dùng làm ngày trả lời」 viết ở lượt đầu là **SAI** — quy nạp từ **một** mẫu. Phiếu No. 1 (lệch 10 ngày) bác bỏ nó. **Bài học: câu nói về cơ chế của một hệ thống cần ≥2 mẫu lệch nhau mới được viết.**
