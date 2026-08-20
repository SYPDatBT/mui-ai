# SESSION 2026-08-20 — QA No.10 chốt phạm vi SYP → guide có bảng 担当 chính thức
> Đọc SAU `00_INDEX.md`. ⭐ TRẠNG THÁI MỚI NHẤT (chưa có file nào thay).

## 1. Bối cảnh & mục tiêu phiên

User (Diệu Hiền / LTDH) mang tới **ảnh chụp một trang QAデータベース Notion** mà SYP đã hỏi và mui đã
trả lời: bảng phân công 5 khối chức năng, mui đáp 「認識に相違ないです。」 (*cách hiểu không có gì sai lệch*).

Câu hỏi của user: **memory có đang nhận thức như vậy không, `onboarding_guide.md` có đang như vậy
không, nếu không thì cần sửa gì.** → phiên này là một đợt đối chiếu + vá tài liệu theo nguồn mới.

## 2. ĐÃ LÀM

### 2.1 Định danh nguồn (theo ⛔#8 — trích QA phải đủ định danh)

Ảnh đầu tiên user gửi chỉ có phần body (bảng phân công), **thiếu 回答者/ngày/kênh** → đã yêu cầu user
gửi phần property. Ảnh thứ hai đủ. Nguồn chốt:

| Ô | Giá trị |
|---|---|
| Kênh | Notion — QAデータベース dự án, trang 「**SYP開発範囲の確認**」, **No. 10** |
| ステータス | **完了** — user xác nhận 完了 ≡ 回答済 (đã trả lời xong) |
| 回答内容 | 「認識に相違ないです。」 |
| 回答者 | **swan (mui)** — cùng người trả lời QA 独立デプロイ và QA hemssv hồi 08-04 |
| 質問者 | **Nguyen Van Tung (SYP)** — *không phải* Bui Trong Dat |
| 起票日時 | 2026-08-12 16:17 |
| 更新日時 (= ngày **chốt** phiếu, xem 3.4) | **2026-08-13** 12:28 (Notion hiện "Last Thursday", user xác nhận ngày tuyệt đối) |
| 質問内容 (property) | **Empty** — nội dung câu hỏi nằm ở **body trang** |

Nội dung bảng phân công được xác nhận (căn cứ user tự lập từ 「統合要件定義書および開発費見積もりの記載」):

| 領域 | 担当 |
|---|---|
| 7-1. E-GW機能（ファームウェア） | mui Lab |
| 7-2. GW管理クラウド機能 | mui Lab |
| **7-3. EMINEL-smartサーバー機能** | **SYP** |
| **7-4. 管理画面機能** | **SYP** |
| **モバイルアプリ** | **SYP** |

### 2.2 Kết quả đối chiếu trước khi sửa

- **Auto-memory của Claude** (`~/.claude/projects/.../memory/`): **không có gì** về phạm vi SYP.
- **Memory workspace**: `00_INDEX.md` + `02_session_20260804…` có ghi 4 QA ngày 08-03/04
  (app là 開発対象 ・ server độc lập ・ admin chung source ・ conciergesv+eminelsv = phạm vi điều tra),
  nhưng **đều ở mức 回答中 / chưa chốt**, và **chưa bao giờ ghi 7-1/7-2 là của mui Lab**.
- **Guide**: đúng hướng nhưng còn treo nhãn 🔸 giả thuyết ở 2 chỗ, và **không có bảng 担当** ở đâu cả.

### 2.3 Vá guide — 6 chỗ, `+93/−13` dòng

Mốc guide: v1.3 / đối chiếu `1100487`. Repo `eminel_gw_project` kiểm `git log -1` = `1100487` (khớp, ⛔#14).

| Chỗ | Sửa gì |
|---|---|
| **§1.6** (mở đầu) | Tách rành mạch **hai câu hỏi khác nhau**: 対象範囲 (*dự án có làm gì*) vs 担当 (*ai làm*) — trộn hai cái là hiểu sai. Bảng cũ thành bảng ① |
| **§1.6 bảng ② (MỚI)** | Bảng 担当 5 hàng + dòng 🔍 đủ định danh + **3 cảnh báo cách đọc**: ① app 対象範囲 nói ❌ nhưng 担当 là SYP, không mâu thuẫn ② **GW管理クラウド là của mui Lab, KHÔNG phải SYP** (bảng ① gộp nó chung hàng với server EMINEL-smart vì v1.2 viết vậy) ③ firmware cũng của mui Lab |
| **§1.6 cuối** | Viết lại đoạn "Hai điều QA này chưa chốt" thành **bảng 3 hàng "chỗ hở hồi 08-03 → nay ra sao"**. Giữ lại ghi chú số ①④ nhầm trong câu hỏi gốc. Giữ cảnh báo v1.2 §1-2 **vẫn còn chữ 「対象外」** (kiểm lại tại `1100487`) |
| **§6.1** | Bảng 4 nhóm mã thêm **2 cột: 「Mục trong v1.2」 (7-1〜7-4) + 「担当」** → nhìn tiền tố là biết có phải việc của mình. Tách dòng 🔍 làm 2 (nguồn v1.2 cho các cột cũ / nguồn Notion cho cột 担当). Thêm cảnh báo **app dùng mã F-AP, không nằm trong 7-1〜7-4** nhưng vẫn do SYP làm |
| **§9.4** | Thêm khối **✅ "Câu trả lời chốt phạm vi SYP (2026-08-13)"** trước phần "điều rút ra". Hạ nhãn 🔸: đoạn 「関与が薄そう」 (camp 6/25) nay ghi rõ **chỉ còn giá trị lịch sử**; điểm 1 sửa thành "app là đối tượng phát triển **và SYP là bên làm**". Thêm ⚠️ **cái vẫn chưa chốt là *mức độ* độc lập của server, không còn là *ai làm gì*** |
| **§1.3 + Phụ lục E.2** | §1.3: ô SYP trong bảng 4 bên đổi từ *"dự kiến làm luôn server E-GW"* → 3 khối đã đảm nhận, kèm 1 dòng giải thích chữ 「担当想定」 trong nguyên văn `03_stakeholders.md` là cách viết **cũ** (giữ nguyên văn, không sửa nguồn). E.2: xem mục 3.2 dưới |

### 2.4 Kiểm cơ học sau khi vá

`4.457` dòng ・ `274` heading (273 slug duy nhất — trùng 1, có từ trước) ・ **0 liên kết nội bộ hỏng**
(202 link) ・ `70` dấu ``` (chẵn) ・ **mọi bảng mới khớp số cột** (kiểm bằng `awk -F'|'` trên `git diff`).

⚠️ **Bài học về chính công cụ kiểm**: checker anchor viết lần đầu báo **62 link hỏng** — SAI, do nó gộp
`\s+` thành 1 gạch, trong khi GitHub biến **mỗi** khoảng trắng quanh dấu `—` thành 1 gạch (nên slug thật
có `--`). Sửa thành `-replace '\s','-'` (không `+`) → 0 hỏng. **Cùng họ với ⛔#13: finding do tool sinh ra
phải kiểm lại trước khi vá.** Suýt đi sửa 62 link đang đúng.

### 2.5 Đợt vá thứ hai cùng ngày — phiếu QA **No. 1** cũng đã 完了

User mang tiếp ảnh property của phiếu 「**担当範囲（サーバー／管理画面）とアプリ対象外の確認**」 — chính là
QA #1 của bảng §9.4, và chính là **việc 1c** vừa ghi vào hàng đợi vài phút trước.

| Ô | Giá trị | Guide trước đó ghi gì |
|---|---|---|
| **No.** | **1** | *(không ghi)* |
| ステータス | **完了** | `回答中` ❌ **SAI** |
| 回答内容 | 「モバイルアプリは開発対象です。」 | ✅ khớp |
| 回答者 | masao takahashi | ✅ khớp |
| 質問者 | Bui Trong Dat | ✅ khớp |
| 起票日時 | 2026-08-03 **17:30** | ✅ khớp (thiếu giờ) |
| 更新日時 | **2026-08-13 12:27** | *(không ghi)* |
| 質問内容 | **Empty** | — |

**⭐ Phát hiện giá trị nhất của cả ngày** (xem mục 3.4): 更新日時 của phiếu này là **08-13 12:27**, phiếu
No. 10 là **08-13 12:28** — **cách nhau MỘT PHÚT**. Nhưng nội dung trả lời của No. 1 thì **đã đọc được
từ 08-04**. ⇒ hai điều rút ra, cả hai đã ghi vào guide:

1. **更新日時 = ngày ĐÓNG phiếu, KHÔNG phải ngày viết câu trả lời** (No. 1 lệch 10 ngày).
2. **mui dọn QA theo ĐỢT** — trạng thái đọc từ lâu là vô giá trị.

**Vá guide lượt 2 — 6 chỗ, `+40/−13` dòng:**

| Chỗ | Sửa gì |
|---|---|
| **§0.3** bảng "hai mốc kiểm" | Hàng QAデータベース: từ *"lần đọc 08-04, chưa kiểm lại"* → **"kiểm một phần 08-20, chỉ 2 phiếu No. 1 + No. 10"**; nói rõ các trạng thái 回答中 còn lại **rất có thể đã lạc hậu** |
| **§1.6** dòng 🔍 phiếu No. 1 | Thêm **No. 1** ・ 起票 kèm giờ ・ tách **2 mốc**: nội dung có từ 08-03/04, phiếu chốt **08-13 12:27** ・ trạng thái **完了** ・ thêm ⚠️ "đừng gộp hai mốc ngày" |
| **§1.6** bảng "chỗ hở → nay ra sao" | Hàng 1 viết lại: không còn là *"No. 10 đã 完了"* mà là **chính phiếu No. 1 nay 完了** ⇒ 「モバイルアプリは開発対象です」 là **kết luận cuối** |
| **§1.6** thêm 💡 | Giải thích chuyện "cách nhau một phút" + 🔸 giả thuyết 3 phiếu còn lại cũng đã 完了 |
| **§9.4** bảng 4 QA | Đổi cột `#` → **`No.`** + thêm **cột ステータス**: No. 1 = ✅ 完了 (chốt 08-13, kiểm 08-20), 3 phiếu còn lại = 🔸 **chưa kiểm lại** (08-04: 回答中), số phiếu để `?`. Bỏ câu "đều đang ở trạng thái 回答中". Thêm ⚠️ 3 phiếu `?` rất có thể đã 完了 — việc rẻ, đáng làm ngay |
| **Phụ lục E.2** | **Sửa lỗi của chính lượt 1** (xem 3.4) + dựng mục 「⚠️ Bốn cái bẫy của QAデータベース」: ① 更新日時 ≠ ngày trả lời ② mui đóng theo đợt ③ 質問内容 Empty (cả 2 phiếu đều vậy) ④ ngày hiển thị tương đối |

Kiểm cơ học sau lượt 2: `4.474` dòng ・ 274 heading ・ **205 link, 0 hỏng** ・ 70 fence (chẵn).
Đã audit toàn bộ chỗ còn chữ `回答中` — các chỗ còn lại đều là phiếu **thật sự chưa kiểm**, đúng.

### 2.6 Đợt vá thứ ba — phiếu QA **No. 2** 独立デプロイ đã 完了, và **một câu hỏi của mui đã rơi mất**

| Ô | Giá trị | Guide trước đó ghi gì |
|---|---|---|
| **No.** | **2** | *(không ghi)* |
| ステータス | **完了** | `回答中` ❌ **SAI** |
| 回答内容 | 「基本的には独立したシステムとして開発してもらう方向でお願いします。ただし既存システムを使い続けたほうがいい機能があれば教えてほしいです」 | ✅ khớp **nguyên văn, không đổi một chữ** |
| 回答者 | swan | ✅ khớp |
| 質問者 | Bui Trong Dat | ✅ khớp |
| 起票日時 | 2026-08-03 **17:31** | ✅ khớp (thiếu giờ) |
| 更新日時 | **2026-08-13 12:28** | *(không ghi)* |
| 質問内容 | **Empty** | — |

**⭐ Phát hiện quan trọng nhất (đã thành mục riêng trong guide §9.4):** ô `回答内容` **không có nội dung nào thêm**
so với bản đọc ngày 08-04 ⇒ **SYP chưa bao giờ trả lời vế `ただし`, mui tự đóng phiếu.** Đây là lời giải cho
câu hỏi (a)/(b) đặt ra lúc rà: **là (b)**. Việc số 6 của hàng đợi (treo từ 08-04 qua 5 phiên) **đã rơi mất kênh
trả lời** — nội dung thì vẫn cần cho công việc. Chi tiết + hướng gỡ: `00_INDEX` việc **6** (đã viết lại hẳn).

**Nhịp đóng phiếu của mui — nay có 3 mẫu, đủ để kết luận:**

| Phiếu | 起票 | Chốt (更新日時) |
|---|---|---|
| No. 1 担当範囲…とアプリ対象外 | 08-03 17:30 | 08-13 **12:27** |
| No. 2 独立デプロイ | 08-03 17:31 | 08-13 **12:28** |
| No. 10 SYP開発範囲 | 08-12 16:17 | 08-13 **12:28** |

⇒ **3 phiếu đóng trong 2 phút.** Dat lập No.1 và No.2 cách nhau 1 phút (17:30/17:31), mui đóng cả loạt
ngày 08-13. Củng cố bẫy ② ở mục 3.4 — và khiến 2 phiếu còn lại **rất có thể cũng đã 完了**.

**Vá guide lượt 3 — 8 chỗ:**

| Chỗ | Sửa gì |
|---|---|
| **§0.3** bảng mốc kiểm | 2 phiếu → **3 phiếu** đã kiểm (No. 1 ・ No. 2 ・ No. 10); nêu "cùng 2 phút" làm lý do các trạng thái cũ đáng ngờ |
| **§0.2** (dòng 「Dời máy chủ」) | *"cách chạy cụ thể **đang chốt** qua QA 08/2026"* → **đã chốt** qua QA 08-13 |
| **§1.2** (khối 「統合される」) | Đổi từ đoạn văn thành **2 bullet**: server = phiếu No. 2 **完了**, hướng độc lập đã chốt (kèm cảnh báo 「基本的には」 + mức độ chưa nói); 管理画面 = 🔸 **chưa kiểm lại** |
| **§8.x** (tiền đề 「同一コードベース」) | *"**có thể thay đổi** theo trả lời QA2"* → **"đã bị vượt qua"** (QA No. 2 完了); giữ 🔸 chưa kiểm repo có cập nhật chưa |
| **§9.4** bảng 4 QA | Hàng 2: `?` → **No. 2**, 🔸 → ✅ **完了** (chốt 08-13 12:28) |
| **§9.4** đoạn cảnh báo dưới bảng | Từ "ba phiếu `?`" → **hai phiếu**; thay câu "cách nhau một phút" bằng **bảng 3 phiếu × 起票/chốt** |
| **§9.4 điểm 2** | Viết lại thành **3 tầng**: ✅ đã chốt (hệ độc lập) / ⚠️ chữ 「基本的には」 vẫn nguyên, **không đọc thành "độc lập tuyệt đối"** / ❌ mức độ chưa nói, phiếu đã đóng ⇒ **phải mở phiếu QA MỚI**, chờ tiếp là vô ích |
| **§9.4 mục MỚI** 「Một câu hỏi mui đặt cho SYP đã rơi mất」 | Tách 2 vế của câu trả lời ・ nêu rõ SYP không đáp mà phiếu vẫn đóng ・ hệ quả: mất **kênh** chứ không mất **việc** ・ 💡 bài học: **đọc câu trả lời của mui phải soi xem có câu hỏi ngược lại mình không** (dấu hiệu 「ただし…」「…があれば教えてほしい」); **phiếu đóng ≠ xong việc** |

Kiểm cơ học sau lượt 3: 275 heading ・ **206 link, 0 hỏng** ・ 70 fence (chẵn) ・ audit: không còn chỗ nào
ghi phiếu No. 2 là 回答中.

### 2.7 Đợt vá thứ tư — phiếu QA **No. 3** 管理画面 đã 完了 (+ 1 chỗ NGOÀI guide)

| Ô | Giá trị | Guide trước đó ghi gì |
|---|---|---|
| **No.** | **3** | *(không ghi)* |
| ステータス | **完了** | `回答中` ❌ SAI (2 chỗ) |
| 回答内容 | 「管理画面はE-Smartと共通のソースコード、デプロイも同一（同じ操作者が使う想定）」 | ✅ khớp **nguyên văn, không đổi một chữ** |
| 回答者 | masao takahashi | ✅ khớp |
| 質問者 | Bui Trong Dat | ✅ khớp |
| 起票日時 | 2026-08-03 **17:32** | ✅ khớp (thiếu giờ) |
| 更新日時 | **2026-08-13 12:28** | *(không ghi)* |
| 質問内容 | **Empty** | — |

**Không có vế `ただし`** → khác phiếu No. 2, không phát sinh việc cho SYP.

**⭐ Điểm đáng giá nhất của lượt này: 1 chỗ nằm NGOÀI guide.**
`requirements/self_study_plan.md` **dòng 83** (Hạng mục 3 — 管理画面) còn ghi 「QA masao takahashi, 2026-08-03,
**回答中**」. Nếu chỉ rà `onboarding_guide.md` thì **sót**. ⇒ **Từ nay mỗi lần một phiếu QA đổi trạng thái phải
grep `回答中` trên CẢ `requirements/`, không chỉ guide.** (Đã grep xác nhận: sau khi sửa, `requirements/*.md`
ngoài guide còn **0 chỗ** ghi 回答中.)

**Vá lượt 4 — 6 chỗ:**

| Chỗ | Sửa gì |
|---|---|
| **§0.3** bảng mốc kiểm | 3 → **4 phiếu** đã kiểm (No. 1 ・ 2 ・ 3 ・ 10) |
| **§1.2** bullet 管理画面 | Bỏ 🔸 "chưa mở lại kiểm" → **No. 3 完了**; thêm lý do mui nêu (**cùng lớp người vận hành**) + nhấn **không kèm chữ nhượng bộ nào**, khác phiếu No. 2 |
| **§9.4** bảng 4 QA | Hàng 3: `?` → **No. 3**, 🔸 → ✅ **完了** |
| **§9.4** đoạn cảnh báo | "Hai phiếu `?`" → **một phiếu**; bảng nhịp đóng phiếu thêm hàng No. 3 + **2 nhận xét mới**: Dat lập No. 1–3 liên tiếp **từng phút** (17:30/31/32), mui **để 10 ngày rồi đóng cả loạt trong 2 phút** |
| **§9.4 điểm 3** | Viết lại: đã chốt, không nhượng bộ, **đè lên** ghi chú camp 6/25; thêm 💡 hệ quả thực tế — **thêm màn hình vào chính repo `syp-eminelstandard-web-admin`**, không repo mới / không deploy riêng |
| **§9.5-ish** (khối ghi chú camp 6/25) | *"QA Notion (回答中) nói khác"* → **"QA mới là bản đúng"**, camp 6/25 phần 管理画面 chỉ còn giá trị lịch sử; tách rõ **phần app của camp vẫn đúng** (build 2 app riêng — nền cho task tái cấu trúc app) |
| **NGOÀI GUIDE**: `self_study_plan.md:83` | 「回答中」 → phiếu **No. 3 完了**; nêu cả cặp: No. 2 = server độc lập ・ No. 3 = admin dùng chung |

Kiểm cơ học sau lượt 4: 275 heading ・ **206 link, 0 hỏng** ・ 70 fence ・ audit `管理画面は独立` không còn chỗ nào "chưa chốt".

## 3. QUYẾT ĐỊNH & PHÁT HIỆN

### 3.1 Điều quan trọng nhất: 完了 ≠ 回答中 → được phép ghi là ĐÃ CHỐT

Bốn QA hồi 08-04 đều 回答中 nên guide phải treo nhãn 🔸. QA No. 10 ở trạng thái **完了** → đây là **căn cứ
mạnh nhất hiện có** về phạm vi SYP, và là thứ mở khoá cho toàn bộ đợt vá này. Nếu nó cũng 回答中 thì
không được hạ nhãn.

### 3.2 Property ステータス của QAデータベース có **ba** giá trị, guide chỉ liệt kê hai

Guide (Phụ lục E.2) trước đây ghi ステータス chỉ có `回答中` / `回答済`. Thực tế còn **`完了`**.
→ ai grep `回答済` để tìm phiếu đã đóng sẽ **sót**. Đã sửa: bảng 3 giá trị + cột "dùng được làm căn cứ chưa";
bổ sung property **No.** và tách 起票日時 / 更新日時.

Mục này về sau (lượt vá 2) được dựng thành 「**⚠️ Bốn cái bẫy của QAデータベース**」 — nội dung cuối cùng của
nó, kể cả phần sửa lỗi 更新日時, xem **mục 3.4**. Đọc bản trong guide là đủ, đừng đọc lịch sử ở đây.

### 3.3 Lỗ hổng quy trình: đợt cập nhật guide chỉ rà git, KHÔNG rà Notion

Câu trả lời này có từ **~13/08**, tức **trước** đợt nâng guide lên v1.3 ngày 18/08 — mà đợt đó bỏ sót.
Nguyên nhân: quy trình 4 bước ngày 18/08 lấy **`git diff` của repo tài liệu** làm phạm vi, Notion nằm
ngoài phạm vi đó. **Đây là lỗ hổng quy trình, không phải lỗi của lần đó.**
→ Đề xuất chưa áp: mọi đợt cập nhật guide phải có **bước 0 = rà QAデータベース** các phiếu đổi trạng thái
sang 完了/回答済 kể từ mốc lần trước. Chưa sửa vào SKILL nào (xem mục 5).

### 3.4 ⛔ TỰ MẮC LỖI TRONG PHIÊN, ĐÃ SỬA — 更新日時 không phải ngày trả lời

Lượt vá 1 (buổi sáng) tôi viết vào Phụ lục E.2: 「更新日時 (*ngày cập nhật* — **dùng làm ngày trả lời**)」.
Lượt vá 2 (phiếu No. 1) **bác bỏ chính câu đó**: nội dung trả lời có từ 08-03/04 mà 更新日時 = 08-13,
lệch **10 ngày**. Đã sửa thành 「*ngày sửa gần nhất*」 + bẫy ① của mục 「Bốn cái bẫy」.

**Nguyên nhân**: suy từ **một** mẫu (phiếu No. 10 có 起票 08-12 → 更新 08-13, chênh 1 ngày nên hai cách
đọc trùng nhau) rồi phát biểu thành quy tắc chung. Đúng họ với ⛔#3 (không bịa nguyên nhân) — nhưng biến
thể nguy hiểm hơn: **quy nạp từ 1 mẫu vào một khẳng định về CƠ CHẾ của công cụ**.
**Bài học vận hành**: khi định viết một câu về *cách một hệ thống hoạt động* (property nghĩa là gì, cột
nào tin được), phải có **≥2 mẫu lệch nhau** hoặc tài liệu chính thức — 1 mẫu chỉ đủ để tả mẫu đó.

### 3.5 Phát hiện phụ

- **質問者 là Nguyen Van Tung**, không phải Bui Trong Dat — tức **SYP có nhiều người cùng đăng QA**.
  Hệ quả: đọc QAデータベース không được lọc theo một người hỏi duy nhất, sẽ sót phiếu.
- Câu hỏi No. 10 tự khai căn cứ là 「統合要件定義書**および開発費見積もり**」 — tức bảng **báo giá** cũng là
  nguồn phân công. Guide hiện chỉ dùng `10_feature_list.md` (bám báo giá v0.3); 🔸 **chưa kiểm** bản
  báo giá gốc có nói gì thêm về 担当 không.

## 4. Thay đổi phía repo dự án

Không pull trong phiên này. `eminel_gw_project` vẫn ở **`1100487`** (kiểm `git log -1`) — đúng mốc đối
chiếu của guide v1.3, nên mọi số dòng trích trong guide vẫn hợp lệ.
Workspace `mui-ai` HEAD trước phiên: `432867d`. Thay đổi của phiên (guide) **chưa commit** (⛔#8: không
push/commit khi user chưa yêu cầu).

## 5. VIỆC DỞ DANG / LÀM TIẾP

1. **Chưa commit** thay đổi guide (`+93/−13`). Chờ user quyết. Guide đang là **v1.3 + đợt vá 08-20** —
   🔸 chưa quyết có đánh số lên **v1.4** không (bảng meta đầu guide chưa sửa số phiên bản).
2. **Chưa chạy review 3 vòng** theo `requirements/README.md` §8 / ⛔#5. Chỉ mới kiểm cơ học (mục 2.4).
   Theo quy trình 4 bước hiệu quả của 18/08 thì bước còn thiếu là **"review CHỈ vùng sửa"** — lấy
   `git diff requirements/onboarding_guide.md` làm phạm vi, không quét lại 4.457 dòng.
3. **Chưa áp đề xuất "bước 0 = rà Notion"** (mục 3.3) vào SKILL nào. Nếu áp thì theo ⛔#11 phải đi qua
   `analyze-change-request` trước, và sửa gốc ở `skillAI/3-step-review/` chứ không vá lẻ.
4. **Chưa rà các tài liệu khác** theo bảng 担当 mới. Cần kiểm ít nhất: `requirements/README.md` ・
   `requirements/self_study_plan.md` (4 hạng mục của nó đúng khớp 7-3/7-4/app + batch — có thể chỉ cần
   thêm 1 câu dẫn nguồn) ・ `notes/guide_v13_mapping.md`.
5. **Hàng đợi cũ chưa đụng** (giữ nguyên từ `00_INDEX` mục 🎯): 5 việc còn lại của guide v1.3 (N1–N6,
   Phụ lục C thêm `GW-04`, Phụ lục D trỏ `4_spec/app/`, đọc `c02_グラフ`/`c03_レポート`) ・ điền 7 dòng
   配信・通知系 + Xzilla vào `summary_batch_migration_ja.md` ・ điều tra nhóm 集計・計算系 ・
   3 mục treo của task tái cấu trúc app (`submit_folder/2026_08_18/output_schedule.md` mục 7).

## 6. CHƯA KIỂM

- **Bản báo giá 開発費見積もり** — câu hỏi No. 10 trích nó làm căn cứ, mình chưa mở. Không biết nó có
  nói gì về 担当 mà guide đang thiếu.
- **Các phiếu QA khác trên Notion** đã đổi trạng thái sang 完了/回答済 từ 08-04 tới nay. Phiên này chỉ
  xử lý đúng **1 phiếu** user mang tới. Đặc biệt: 4 QA hồi 08-03/04 (guide §9.4) **có thể đã 完了 hết**
  mà guide vẫn ghi 回答中 — 🔸 chưa kiểm, và đây là việc đáng làm ngay vì rẻ.
- **5 trang QA 回答中** ở hàng đợi cũ (`00_INDEX` việc số 8) — chưa mở lại lần nào trong phiên này.
- Ngày `2026-08-13` lấy từ **user xác nhận bằng lời**, chưa tự thấy ngày tuyệt đối trên Notion.
