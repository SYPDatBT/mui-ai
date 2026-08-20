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

### 2.8 Đợt vá thứ năm — phiếu QA **No. 4** hemssv đã 完了 ⇒ **bảng 4 phiếu §9.4 SẠCH**

| Ô | Giá trị | Guide trước đó ghi gì |
|---|---|---|
| **No.** | **4** | *(không ghi)* |
| ステータス | **完了** | `回答中` ❌ SAI (2 chỗ: §4.2 và bảng §9.4) |
| 回答内容 | 「おおよそその認識でOKです。HEMS-SV(m2-cloud)はmui側開発範囲で…HEMS-SVの仕様等は別途共有します」 | ✅ khớp **nguyên văn, không đổi một chữ** |
| 回答者 | swan | ✅ khớp (nhưng guide ghi 「cập nhật 2026-08-04」 → đã sửa thành chốt 08-13) |
| 質問者 | Bui Trong Dat | ✅ khớp |
| 起票日時 | 2026-08-03 **17:32** | ✅ khớp (thiếu giờ) |
| 更新日時 | **2026-08-13 12:28** | *(không ghi)* |
| 質問内容 | **Empty** | — |

Không có vế `ただし` → không phát sinh việc cho SYP.

**Vá lượt 5 — 5 chỗ:**

| Chỗ | Sửa gì |
|---|---|
| **§4.2** dòng 🔍 (ba tên hemssv/conciergesv/eminelsv) | Thêm **No. 4** ・ 起票 kèm giờ ・ bỏ 「回答者 swan (cập nhật 2026-08-04)」 + 「trạng thái khi đọc (08-04): 回答中」 → **chốt 08-13 12:28**, trạng thái **完了** (kiểm 08-20) |
| **§0.3** bảng mốc kiểm | 4 → **5 phiếu**, bỏ chữ "kiểm một phần" cho nhóm phạm vi |
| **§9.4** bảng 4 QA | Hàng 4: `?` → **No. 4**, 🔸 → ✅ **完了** |
| **§9.4** câu dẫn trên bảng | *"3 phiếu đã 完了, còn 1 chưa kiểm"* → **"cả bốn đều đã 完了"**, bốn câu trả lời là **kết luận đã đóng** |
| **§9.4** đoạn dưới bảng | Bỏ hẳn ⚠️ "phiếu `?` cuối cùng rất có thể…" (không còn phiếu nào chờ) → đổi thành khối 📌 **「Nhịp làm việc của mui trên QAデータベース」** + bảng **5 phiếu × 起票/chốt**; kết luận: lập 4 phiếu trong **3 phút**, mui để **10 ngày** rồi đóng cả loạt trong **2 phút**; bài học: thấy 1 phiếu đổi trạng thái thì mở luôn phiếu cùng chủ đề |
| **§7.x** (bản thiết kế nháp admin) | 1 chỗ **sót từ lượt 4**: 「Hướng "chung với E-Smart" đã được xác nhận qua QA Notion (**còn 回答中**)」 → ✅ **chốt qua phiếu No. 3 (完了 08-13)**. Bắt được vì audit toàn văn chữ `回答中`, không phải vì grep tên phiếu |

**Trạng thái cuối của cả nhóm phiếu phạm vi (5/5 完了):**

| No. | Phiếu | Kết luận đã đóng |
|---|---|---|
| 1 | 担当範囲…とアプリ対象外 | app là **開発対象** |
| 2 | 独立デプロイ | server hướng **độc lập** (⚠️ còn chữ 「基本的には」; mức độ chưa nói) |
| 3 | 管理画面は独立か共通か | admin **chung source + chung deploy** |
| 4 | 旧EMINEL調査範囲…hemssv対象外 | phạm vi **điều tra** = conciergesv + eminelsv; **hemssv ngoài phạm vi** |
| 10 | SYP開発範囲 | bảng 担当 5 khối (mui: 7-1/7-2 · SYP: 7-3/7-4/app) |

🔸 **Nhãn giả thuyết CÒN GIỮ** (đóng phiếu không thêm thông tin nào): "m2-cloud" có phải tên hiện thực của
`GW管理クラウド` ở hệ mới hay không — §4.2 vẫn ghi **CHƯA kiểm chứng**, chưa thấy tên này trong repo docs.

Kiểm cơ học sau lượt 5: 275 heading ・ **206 link, 0 hỏng** ・ 70 fence ・ audit toàn văn `回答中`: các chỗ còn
lại đều **hợp lệ** (mô tả lịch sử ・ phiếu 「バッジ・ランク」 khác nhóm ・ bảng 3 giá trị ở Phụ lục E.2).

### 2.9 Đợt vá thứ sáu — phiếu QA **No. 5** バッジ・ランク đã 完了 (= câu 1 của `qa_kitagas.md`)

| Ô | Giá trị | Guide trước đó ghi gì |
|---|---|---|
| **No.** | **5** | *(không ghi)* |
| ステータス | **完了** | `回答中` ❌ SAI (3 chỗ) |
| 回答内容 | 「今の所、2026年スコープ外です」 | ✅ khớp **nguyên văn** |
| 回答者 | masao takahashi | ✅ khớp |
| 質問者 | Bui Trong Dat | ✅ khớp |
| 起票日時 | 2026-08-03 **17:33** | *(chỉ ghi 08-03)* |
| 更新日時 | **2026-08-13 12:28** | *(không ghi)* |

Phiếu này **khác 5 phiếu trước**: nó không thuộc nhóm "phạm vi SYP" mà là **câu 1 của bảng QA gửi khách**
`submit_folder/qa/qa_kitagas.md`, và là mục **B.1** của Phụ lục B (bảng mâu thuẫn giữa các tài liệu).

**⭐ Quyết định quan trọng nhất của lượt này: KHÔNG xoá B.1 khỏi bảng mâu thuẫn**, dù phiếu đã đóng. Hai lý do:

1. Chữ 「**今の所**」 (*hiện tại thì*) nằm trong nguyên văn — là **mốc thời điểm**, không phải kết luận vĩnh
   viễn. Cùng loại với 「基本的には」 của phiếu No. 2.
2. Đây là trả lời của **mui**, **không phải xác nhận của 北ガス** — mà người quyết phạm vi là 北ガス. Chữ trên
   giấy `A04_badge_rank.md` **vẫn** viết toàn bộ vào 「26年対応スコープ」.

⇒ Chỉ **hạ mức độ**: hàng B.1 từ 🔴 Cao → 🟠 Vừa, ghi rõ "mui đã trả lời ngoài scope 2026 nhưng 北ガス chưa
xác nhận". Đây là ranh giới đúng giữa "đã có tín hiệu" và "đã chốt" — xoá hẳn là **diễn giải vượt nguồn** (⛔#8).

**Vá lượt 6 — 4 chỗ:**

| Chỗ | Sửa gì |
|---|---|
| **§6.x** mục huy hiệu (A4) | Thêm **No. 5** + 起票 kèm giờ + **完了** chốt 08-13; dựng lại đoạn ⚠️ thành **2 gạch dè dặt** (「今の所」 ・ mui ≠ 北ガス) thay vì một câu gộp |
| **Phụ lục B** bảng mâu thuẫn, hàng **B.1** | 🔴 Cao → **🟠 Vừa**; cột nguồn ghi phiếu **No. 5, 完了 08-13, kiểm 08-20** |
| **Phụ lục B.1** phần 「Diễn biến」 | Ghi phiếu No. 5 完了; thêm kết luận **"mâu thuẫn đã ngả về phía 劣後"** + nêu rõ **vì sao chưa xoá** khỏi bảng |
| **§0.3** bảng mốc kiểm | 5 → **6 phiếu**; thêm nguyên tắc ⚠️ **「phiếu 完了 KHÔNG có nghĩa là hết dè dặt」** — đóng phiếu không thêm chữ nào vào câu trả lời, nên chữ nhượng bộ và chuyện "mui trả lời ≠ khách xác nhận" vẫn còn nguyên |

**Chưa sửa (cố ý)**: `submit_folder/qa/qa_kitagas.md` — file này là **bảng câu hỏi gửi khách**, nội dung câu hỏi
vẫn đúng nguyên trạng; trạng thái trả lời không thuộc file đó. Nếu về sau gửi lại bảng cho khách thì cân nhắc
ghi chú "câu 1 mui đã trả lời sơ bộ".

Kiểm cơ học sau lượt 6: 275 heading ・ **206 link, 0 hỏng** ・ 70 fence ・ audit toàn văn `回答中`: các chỗ còn lại đều **hợp lệ** (mô tả lịch sử ・ bảng 3 giá trị ở Phụ lục E.2).

### 2.10 Phiếu QA **No. 7** — thuộc task tái cấu trúc app, KHÔNG thuộc guide

| Ô | Giá trị |
|---|---|
| **No.** | **7** — 「「依頼: モバイルアプリ構成の変更」について確認」 |
| ステータス | **完了**, chốt **2026-08-13 12:34** |
| 回答内容 | 「**認識に相違ない**」 |
| **回答者** | ⚠️ **Empty** — Notion không ghi ai trả lời (user: *"chắc họ quên thêm vào, nhưng có câu trả lời là được"*) |
| 質問者 | Bui Trong Dat, 起票 **2026-08-03 19:22** |
| 質問内容 | **Empty** (nội dung ở body trang — **chưa đọc**) |

**Ghi vào đâu**: phiếu này **không liên quan `onboarding_guide.md`** — guide là tài liệu học về requirement,
còn đây là task tái cấu trúc source app. Đã ghi vào **`submit_folder/2026_08_18/output_schedule.md` mục 1**
(nơi chứa đề bài + cách hiểu) và `00_INDEX` khối [08-18].

**Hai điều phải giữ khi trích về sau:**
1. **Không gán tên người trả lời.** Ô 回答者 trống thật; user chấp nhận dùng câu trả lời nhưng điều đó không
   tạo ra một cái tên. Trọng lượng phiếu này **thấp hơn** các phiếu có tên (No. 1–5, No. 10).
2. **Đây là chốt phần *hiểu đề bài*, không phải chốt bản đề xuất.** 起票 08-03 19:22 = cùng ngày nhận đề bài;
   bản `CLIENT_REPORT_APP_RESTRUCTURE_ja.md` nộp 18/08 vẫn ở bước ② của lịch (mui review 17–19/8 →
   phản ánh 20–21/8 → implement 24–28/8).

🔸 **CHƯA kiểm chứng**: body phiếu chưa đọc nên chưa biết "cách hiểu" được xác nhận gồm chính xác những gì.
Nhiều khả năng trùng 3 goal + ghi chú ⚠️ ở `output_schedule.md` mục 1, nhưng **chưa đối chiếu từng câu**.

📌 Ghi chú về nhịp: phiếu này chốt **12:34**, tức **sau** cụm 6 phiếu kia (12:27–12:28) **6 phút** — vẫn cùng
một buổi dọn QA ngày 08-13, củng cố kết luận "mui dọn QA theo đợt".

### 2.11 Phiếu QA **No. 9** — định dạng 設計書 ⇒ guide có mục MỚI §7.7

| Ô | Giá trị |
|---|---|
| **No.** | **9** — 「設計書の最終成果物のファイル形式について」 |
| ステータス | **完了**, chốt **2026-08-13 12:34** |
| 回答内容 | 「**画面：excel / API：markdown**」 |
| **回答者** | ⚠️ **Empty** (như phiếu No. 7) — không gán tên ai khi trích |
| 質問者 | **Nguyen Van Tung**, 起票 **2026-08-10 17:06** |
| 質問内容 | Empty (body chưa đọc, nhưng 回答内容 đã đủ tự thân) |

**Đối chiếu trước khi sửa**: grep `設計書|成果物|excel` trên guide + `requirements/` + `memory/` → **không có
chỗ nào** nói về định dạng bản giao nộp. Tức đây là **thông tin mới hoàn toàn**, không phải sửa chỗ sai.

**Vá — 4 chỗ:**

| Chỗ | Sửa gì |
|---|---|
| **§7.7 (MỤC MỚI)** | 「設計書 — định dạng file của bản giao nộp」: bảng 2 loại (画面→Excel ・ API→markdown) + dòng 🔍 đủ định danh (kèm ghi chú 回答者 trống) + 💡 suy luận vì sao 2 định dạng khác nhau (**gắn nhãn 🔸 vì câu trả lời gốc không nêu lý do**) + ⚠️ **cấm suy rộng** sang `3_requirements`/`4_spec` |
| **Mục lục** | Thêm dòng 7.7 |
| **§7.1 bản đồ 6 tầng** | Thêm ⚠️: sáu tầng đó là các tầng **NẰM TRONG repo**; sau chúng còn tầng **設計書** = thứ **SYP giao nộp**, **không nộp bằng markdown trong repo** → trỏ §7.7 |
| **§0.3** bảng mốc kiểm | 6 → **8 phiếu** (thêm No. 7 và No. 9) |

**Vì sao đặt ở Chương 7 mà không phải chỗ khác**: Chương 7 là 「Bộ tài liệu của dự án」, và 設計書 đúng là **tầng
tiếp sau `4_spec`/機能仕様 (§7.5)**. Đặt ở đây thì người đọc thấy được **toàn bộ chuỗi tài liệu** từ
requirement → spec → 設計書, và biết chỗ nào đổi định dạng.

Kiểm cơ học sau lượt 8: **276 heading ・ 209 link, 0 hỏng ・ 70 fence** (heading và link đều tăng vì có mục mới).

### 2.12 Phiếu QA **No. 12** — phiếu ĐẦU TIÊN chưa có trả lời, và giá trị ステータス thứ tư

| Ô | Giá trị |
|---|---|
| **No.** | **12** — 「2027年劣後機能の確認」 |
| **ステータス** | 🔶 **確認中** ← **giá trị thứ tư**, guide chưa có |
| **回答内容** | ⚠️ **Empty** — chưa ai trả lời |
| 回答者 | Empty |
| 質問者 | **Nguyen Van Tung**, 起票 **2026-08-12 17:41** |
| 更新日時 | **2026-08-12 17:46** (5 phút sau khi lập, **không đổi từ đó**) |

**Hai phát hiện, cả hai đã vào guide:**

**① `確認中` ≠ `回答中`.** Bảng ステータス ở Phụ lục E.2 nay có **4 giá trị**. Ranh giới quan trọng: `回答中` là
**đã có nội dung trả lời** để đọc tham khảo (bốn phiếu No. 1–4 hồi 08-04 chính là vậy); `確認中` là **trống
hoàn toàn** — chưa ai bên mui chạm vào. Trước đây tôi mặc định "chưa xong = 回答中"; sai.

**② 🔴 NGOẠI LỆ của kết luận "mui dọn QA theo đợt" (mục 2.6/2.8).** Phiếu này lập **08-12**, tức **TRƯỚC**
đợt mui đóng 8 phiếu ngày 08-13 — mà vẫn bị để lại nguyên. **Không phải "chưa tới lượt" mà là bỏ qua có
chọn lọc.** Hệ quả hành động: các phiếu khác chỉ cần **chờ đợt dọn tiếp**; phiếu này phải **thúc**.

**Vá — 4 chỗ:**

| Chỗ | Sửa gì |
|---|---|
| **Phụ lục E.2** bảng ステータス | 3 → **4 giá trị**, thêm **確認中** ở đầu (❌ chưa có gì để dùng) + đoạn ⚠️ phân biệt 確認中 vs 回答中 |
| **Phụ lục C** danh mục T.B.D | Thêm **3 hàng #13–#15** + **bảng phân loại "kiểu bị chặn"**. Quan trọng: 12 câu cũ đều hỏi 北ガス, còn **3 câu mới nằm ở phía mui hoặc chính SYP** — #13 đã hỏi đang chờ (No. 12) ・ #14 mức độ độc lập server (No. 2 đóng mà không nói ⇒ **mở phiếu MỚI**) ・ #15 vế `ただし` (**SYP** phải trả lời) |
| **Phụ lục B.1** | Thêm khối 「Diễn biến (2026-08-12)」: No. 12 hỏi **toàn bộ danh sách 劣後 2027**, rộng hơn câu huy hiệu của No. 5; kèm ⚠️ chuyện bị bỏ qua có chọn lọc |
| **§0.3** bảng mốc kiểm | 8 → **9 phiếu**, tách rõ 8 phiếu 完了 vs **No. 12 còn 確認中** |

💡 **Giá trị lớn nhất của phiếu này**: nó biến hai việc trước đây nằm rải rác trong nhật ký (mức độ độc lập
server ・ vế `ただし`) thành **mục có số trong Phụ lục C** — tức từ nay ai đọc guide đều thấy chúng là việc
đang chặn, không phải ghi chú bên lề.

Kiểm cơ học sau lượt 9: **276 heading ・ 213 link, 0 hỏng ・ 70 fence**.

### 2.13 Phiếu QA **No. 6** — phiếu đáng giá nhất trong 10 phiếu (Comments có nội dung)

| Ô | Giá trị |
|---|---|
| **No.** | **6** — 「エラー種別（重篤／軽微）の判定条件についてご教示ください」 |
| ステータス | 🟡 **回答中** |
| 回答内容 | 「**要仕様検討中**」 — chỉ có vậy |
| 回答者 | ⚠️ **Empty** |
| 質問者 | Bui Trong Dat, 起票 **2026-08-03 17:33** |
| 更新日時 | **2026-08-19 10:43** ← **mới nhất trong cả 10 phiếu** |
| **Comments** | ⭐ **masao takahashi (mui), 08-19**: 「まだ、エラー内容を洗い出せていないですので、**結構後になる**かと思います。」 |

**Hai phát hiện, cả hai quan trọng:**

**① ⭐ Câu trả lời thật nằm ở `Comments`, không ở ô `回答内容`.** Đây là phiếu **đầu tiên** trong 10 phiếu có
Comments có nội dung. Ô `回答内容` ghi 「要仕様検討中」 — đọc riêng nó thì tưởng "đang xem xét, chờ chút".
Comment mới cho biết **chưa liệt kê được danh mục lỗi** và **「結構後になる」** (*sẽ khá muộn*) — **đó mới là
thông tin lập kế hoạch**. Kèm theo: **tên người trả lời chỉ có trong Comments** trong khi ô `回答者` trống
⇒ khi trích phải ghi *"theo comment của <tên> ngày <ngày>"*, **không** gán vào ô 回答者 (⛔#8).
→ Đã thành **bẫy ⑤** của Phụ lục E.2.

**② 🔴 Đảo một giả định của guide.** Phụ lục C **#1** — **mục chặn việc SỐ MỘT** của cả dự án — trước ghi cột
「Hỏi ai: **北ガス**」. Thực tế: **điểm nghẽn ở chính mui**, họ chưa lập được danh mục lỗi. Trước khi có danh
mục thì không thể bàn điều kiện phân loại, nên **hỏi 北ガス cũng vô nghĩa**.
Hệ quả hành động: **① không gộp câu này vào bảng QA gửi khách nữa** ② **bàn phương án làm trước phần không
phụ thuộc phân loại lỗi**, vì màn hình **C (quản lý E-GW) thuộc phạm vi 2026** mà đang bị chặn ở đây.

**Vá — 4 chỗ:**

| Chỗ | Sửa gì |
|---|---|
| **§7.4** (spec màn hình quản trị, mục ③ 重篤/軽微) | Thêm tiểu mục **⏳「Đã hỏi rồi — và mui trả lời là 'còn lâu'」**: dòng 🔍 đủ định danh phiếu No. 6 + **trích nguyên văn comment** kèm dịch + **3 điều rút ra** (nghẽn ở mui không phải 北ガス ・ đừng lên kế hoạch dựa vào đây ・ câu trả lời thật ở Comments) |
| **Phụ lục E.2** | **Bẫy ⑤ MỚI**: phải đọc cả `Comments`; tên người trả lời có thể chỉ có ở đó khi 回答者 trống |
| **Phụ lục C #1** | Thêm ⏳ "đã hỏi 08-03, mui nói còn lâu" + nguồn phiếu No. 6 (kèm nguyên văn comment) + cột "Hỏi ai" đổi từ 北ガス → **「mui trước (chưa liệt kê được danh mục lỗi), rồi 北ガス」**; và sửa câu tổng kết dưới bảng (「Cả mười hai câu đều cần 北ガス」 → nêu **#1 là ngoại lệ**) |
| **§0.3** bảng mốc kiểm | 9 → **10 phiếu**, tách 3 nhóm trạng thái: 8 phiếu 完了 ・ No. 6 `回答中` (có comment mới 08-19) ・ No. 12 `確認中` |

📌 **Nhịp đóng phiếu — nay có ĐỦ 3 kiểu**, kết luận "mui dọn theo đợt" cần đọc kèm ngoại lệ:
- **8 phiếu** đóng gọn trong 2 phút ngày 08-13 (No. 1·2·3·4·5·7·9·10)
- **No. 6**: KHÔNG nằm trong đợt đó, nhưng **vẫn đang được xử lý** — cập nhật 08-19, có comment thật
- **No. 12**: lập **trước** đợt 08-13 mà **bị để lại**, không ai chạm (mục 2.12)

Kiểm cơ học sau lượt 10: **277 heading ・ 215 link, 0 hỏng ・ 70 fence**.

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
