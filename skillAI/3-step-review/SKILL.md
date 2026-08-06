---
name: 3-step-review
description: >
  Review 3 vòng cho tài liệu knowledge base của workspace onboarding E-GW (báo cáo điều tra,
  onboarding_guide, qa_kitagas…): vòng 1 XÁC THỰC dẫn chứng/code trên file gốc, vòng 2 NHẤT QUÁN
  nội bộ, vòng 3 DỄ HIỂU cho người mới đọc lần đầu. Kèm thủ tục bắt đầu ở MÁY MỚI (ôm folder sang).
  Trigger khi user gõ "3-step-review", "/3-step-review", "review 3 bước", "review 3 vòng",
  "review lại báo cáo", "review tài liệu này".
user_invocable: true
---

# 3-step-review — Review 3 vòng tài liệu knowledge base

Năm tiêu chí xuyên suốt (user đặt ra, không thương lượng): **① chi tiết của dẫn chứng ・ ② chính xác
・ ③ xác thực ・ ④ dễ hiểu cho người mới vào dự án đọc lần đầu ・ ⑤ TỰ CHỨA — tuyệt đối không bắt
người đọc tra ngược nội dung** (checklist 10 điểm ở Vòng 3; quy tắc gốc = ⛔#10 trong `memory/00_INDEX.md`).
Quy trình kế thừa tinh thần checklist `requirements/README.md` §8 và tổng quát hóa cho mọi tài liệu KB;
đúc kết từ các lần review báo cáo batch 2026-08-04 và chỉ đạo tự-chứa 2026-08-06.

**Quy ước chung**: mọi đường dẫn trong skill này tính từ **gốc workspace `eminel_gw_onboarding/`**
(thư mục chứa `AGENTS.md`), không tính từ thư mục skill. Mọi trao đổi với user và findings viết bằng
**tiếng Việt**; trích nguồn tiếng Nhật giữ nguyên văn (có thể kèm dịch).

## 0. Bắt đầu ở MÁY MỚI (làm TRƯỚC khi review bất cứ gì)

1. **Bootstrap workspace theo đúng thứ tự**: `AGENTS.md` → `CLAUDE.md` → `memory/00_INDEX.md`
   (quy tắc ⛔ 1–9) → file `memory/NN_session_*.md` có dấu ⭐ mới nhất. KHÔNG bỏ qua bước nào.
   - Thiếu `memory/` hoặc skill khác (`update-memory`, `notion-connect`) → KHÔNG dừng: báo user phần
     bị mất (bộ quy tắc ⛔ đầy đủ / cơ chế chốt phiên / kiểm trạng thái QA Notion) rồi chạy phần còn
     lại; các diễn giải ⛔ inline trong skill này là bản tối thiểu.
2. **Chọn tài liệu đích**: user nêu tên file → dùng file đó. User gõ trần "/3-step-review" → hỏi đúng
   1 câu *"Review tài liệu nào?"* kèm gợi ý mặc định = tài liệu ở mục 4. (Bước 1 và 3a làm được
   trước khi có câu trả lời; các bước sau cần tài liệu đích.)
3. **Kiểm repo nguồn**:
   a. `../sources/` cần có: 4 repo git — `eminel_gw_project`, `legacy_eminel_docs`,
      `syp-eminelstandard-backend`, `syp-eminelstandard-web-admin` — và 1 snapshot không git
      `syp-eminelstandard-app-syp-dev`. Không thấy → hỏi user đường dẫn (KHÔNG tự tìm bừa);
      câu trả lời của user **thay thế `../sources/` trong toàn bộ phiên** (kể cả trong prompt
      subagent), không sửa cứng vào skill/tài liệu, ghi vào memory khi chốt phiên.
      Thiếu hẳn repo nào → báo rõ "mục nào của tài liệu sẽ không kiểm chứng được", đừng review chay.
   b. **`git fetch` từng repo git, so HEAD với bảng 「Repo đối chiếu」 đầu tài liệu đích** (⛔#1):
      - HEAD = commit khai báo → kiểm số dòng trực tiếp.
      - Repo đã TIẾN LÊN → kiểm bằng `git show <commit-khai-báo>:<path>` để đối chiếu đúng bản
        tham chiếu, **và** ghi finding "cần đối chiếu lại với bản mới" nếu nguồn đã đổi đáng kể.
      - Khác branch (vd `gw-syp-dev`) → `git show` đúng branch+commit.
      - Fetch lỗi (mạng/quyền) → tiếp tục bằng HEAD local + `git show`, nhưng ghi rõ đầu findings:
        *"chưa fetch được origin — kết luận về độ mới của repo là 推定"*.
      - Snapshot (app): bỏ qua fetch/HEAD; tài liệu không khai mốc phiên bản cho nó → ghi chú đầu
        findings *"nguồn app là snapshot không mốc, chỉ kiểm chứng được trên nội dung hiện có"*.
      - Tài liệu đích **không có** bảng Repo đối chiếu → lấy HEAD sau fetch làm mốc phiên review
        + tự ghi 1 finding [vừa]: "tài liệu chưa khai mốc repo, đề xuất bổ sung bảng Repo đối chiếu".
4. Đọc mục **⚠️ Giới hạn** của tài liệu (nếu có) — nó khai sẵn chỗ chưa kiểm chứng được
   (trạng thái QA Notion 回答中, secret ngoài repo…) để không phí công kiểm điều bất khả.

## 1. Nguyên tắc bắt buộc khi review & sửa

1. **Bám nguyên văn** (⛔#8): trích dẫn khớp từng ký tự; tên người đầy đủ kèm phía
   ("masao takahashi (mui)"); nguồn sống (Notion) phải có ngày đọc + trạng thái.
2. **Tách 確実/推定** (⛔#3): mọi finding phải chỉ ra được bằng chứng; nghi ngờ không tái hiện được
   → ghi là nghi ngờ, không ghi là lỗi.
3. **Sửa = viết lại liền mạch** (⛔#9): không chắp mục "bổ sung/đính chính ngày X" cuối file, không
   rải mốc ngày giờ, không giữ nhãn cũ "làm vết lịch sử" — hòa thông tin mới vào đúng mục.
4. **Sửa xong — bất kể lớn nhỏ — chạy lại đủ 3 vòng** (⛔#5, quy tắc sinh từ lỗi thật: đợt 08-04
   vòng review sau-sửa bắt được 13 lỗi do chính đợt sửa để sót). Thay đổi nhỏ thì vòng 1/3 được
   **thu hẹp phạm vi vào đúng vùng sửa**, nhưng không bỏ vòng nào. Agent tự phân loại phạm vi và nói
   rõ khi báo user. Tối đa 2 lượt sửa-rồi-review-lại; sau đó còn finding [cao] chưa xử được → dừng,
   nêu cho user quyết.
5. KHÔNG sửa bất kỳ file nào trong `../sources/` khi review. KHÔNG push git khi user chưa yêu cầu.
6. **Findings lặp lại cùng loại hoặc mang tính hệ thống** (lỗ hổng của template/quy trình chứ không phải
   của riêng tài liệu) → KHÔNG vá lẻ: chuyển qua skill `analyze-change-request` để phân tích và đề xuất
   sửa GỐC (TEMPLATE/skill/⛔) rồi mới áp xuống tài liệu (⛔#11).

## 2. Ba vòng — nội dung từng vòng

Chạy đúng thứ tự 1 → 2 → 3. Mỗi vòng xuất **danh sách finding đánh số, gắn mức [cao/vừa/thấp]**,
mỗi finding gồm: **vị trí** (file:dòng hoặc §) + **trích nguyên văn câu có vấn đề** + **đề xuất câu
chữ thay thế cụ thể** (không chỉ "nên sửa").

### Vòng 1 — XÁC THỰC (dẫn chứng & code so với file gốc)

- Chọn **tối thiểu 15–20 dẫn chứng 🔍/`file:dòng` rải đều mọi mục lớn** (đừng dồn một chỗ), ưu tiên:
  con số cụ thể (250 point, 22℃, 5 phút, 17 endpoint…), câu trích nguyên văn tiếng Nhật,
  các claim then chốt đỡ cả kết luận.
- Với TỪNG dẫn chứng: **mở file thật**, xác nhận nội dung + số dòng (dung sai ±3; lệch thì ghi số
  đúng); nội dung có bị bóp méo/nói quá nguồn không.
- **Khối code fenced**: đối chiếu từng token quan trọng với file gốc. Quy ước của tài liệu:
  dòng/chỗ chỉ có `...` = ký hiệu lược của báo cáo; comment tiếng Việt = chú thích thêm — hai thứ đó
  hợp lệ, nhưng chú thích **không được sai nghĩa code** (đọc cả ngữ cảnh quanh đoạn trích).
- **Chạy lại mọi câu "grep X: 0 hit"** (case-insensitive khi hợp lý, loại `node_modules`/`.git`),
  và thử **NHIỀU dạng viết** theo ⛔#2: kana dài/ngắn (センサ↔センサー), mã ↔ tên chức năng
  (F-ES-05↔見守り通知), cách ghi số/ngày kiểu Nhật (9月↔2026/9) — khẳng định phủ định chỉ đứng được
  khi tự tái hiện.
- **Đếm lại mọi con số đếm tay** (17 endpoint, 7 loại, 10 Publisher, 6 state machine, số dòng file…).
- Soi **suy đoán viết như sự thật**: câu diễn giải vượt nguồn mà không có nhãn *推定*/🔸.
- Khi cần kiểm sâu (file nén, shell trong tgz): giải nén vào scratchpad, KHÔNG bung vào repo.

### Vòng 2 — NHẤT QUÁN (nội bộ tài liệu)

- **Bảng tóm tắt đầu file vs phần chi tiết**: soi TỪNG dòng — kết luận, nhãn, con trỏ § có khớp không.
- **Mọi tham chiếu chéo**: "§x.y", "bước N", "batch #N", "câu N bảng QA" — đích có tồn tại đúng không
  (kiểm từng cái, đừng tin số).
- **Một sự thật – một cách nói**: cùng một con số/sự kiện ở nhiều chỗ có khớp nhau không
  (chu kỳ chạy, số phút lock, vai trò một bảng DB…).
- **Tàn dư cách viết cũ**: grep các cụm nghi vấn ("bổ sung", "đính chính" sai ngữ cảnh, nhãn đã bỏ,
  số mục đã đổi, tên cột bảng đã đổi mà lời dẫn còn nhắc).
- **Cơ học markdown**: đếm cặp ``` (fence đóng đủ), khối code không nằm trong ô bảng, bảng meta/HEAD
  đầu file khớp mục Nguồn cuối file.
- Mục "Cách đọc"/mục lục mô tả cấu trúc có khớp cấu trúc thật không.
- Tài liệu thuộc loại **báo cáo điều tra** → kiểm tuân thủ cấu trúc `skillAI/create-investigation-report/TEMPLATE.md`
  (2 PHẦN, đúng thứ tự mục, KẾT LUẬN blockquote đầu file, đủ các mục bắt buộc §1–§11, mục lục anchor,
  JP↔VN khớp 1-1) — thiếu mục hoặc đảo thứ tự = finding [cao].
- Riêng tài liệu đích là `requirements/onboarding_guide.md` → chạy KÈM nguyên checklist §8-Vòng-2
  của `requirements/README.md` (đối chiếu bộ khung: đủ chương/phụ lục, 6 nguyên tắc, 6 loại box,
  bảng ảnh, mục Kiểm tra nhanh).

### Vòng 3 — DỄ HIỂU (vai người mới vào dự án, có thể mới học IT, đọc lần đầu)

- **Đọc TUẦN TỰ từ dòng 1** (kể cả bảng meta): thuật ngữ nào dùng TRƯỚC khi được giải thích?
  Chú giải đầu file có phủ đủ những gì bảng tóm tắt dùng không?
- Đường đọc nhanh (§0 → bảng tóm tắt) có tự đứng được không — người vội nắm được kết luận + việc cần làm?
- **Khối code**: mỗi khối có câu dẫn "chứng minh điều gì" chưa; cú pháp lạ (`?.`, `??`, spread,
  arrow fn, destructuring…) đã chú tại lần đầu chưa.
- **"Cách làm từng bước"**: bước nào thiếu chủ thể (ai làm, repo nào), bước nào giả định kiến thức chưa nêu.
- **Câu phải đọc 2 lần**: trích ra + đề xuất viết lại (tách câu, đảo mệnh đề, bỏ ngoặc lồng).
- **Bẫy hiểu nhầm**: nhãn/ký hiệu dễ suy ngược sai ("dùng lại" ≠ 0 công, "bỏ" ≠ mất nghiệp vụ,
  ✅=劣後…) — đã có câu chặn chưa.
- Nêu finding CÓ CHỌN LỌC — chỉ cái thật sự cản trở hiểu; ưu tiên gloss tại chỗ 3–7 chữ thay vì
  phình mục chú giải.
- **Checklist TỰ CHỨA (⛔#10 — user chốt 2026-08-06, kiểm TỪNG điểm, không thương lượng)**:
  1. Mã hiệu (CLD-xx, IF-NN, IF 4 số, SVC-xx, F-ES-xx, spec [G]/[I], mã 契約種別, tên QA…) có chú giải
     tại chỗ ở **MỖI lần xuất hiện**, nội dung gloss theo ngữ cảnh lần đó?
  2. Mọi con trỏ tham chiếu (§x, #N, "việc ngay #N", 付録, cột 関連/Liên quan) có kèm tóm tắt nội dung
     đích ngay tại chỗ?
  3. Bước làm có ghi code đến **từng layer/từng file** (đường dẫn thật, đã kiểm tồn tại)?
  4. Mỗi bước có dòng "*Vì sao*/理由" giải thích lý do chọn cách đó?
  5. Phán định có nói rõ **BỎ gì – GIỮ gì – THAY bằng gì** cho người thường hiểu ngay (cấm nhãn cụt)?
  6. Luồng xử lý có đi từ code xuống **tận database** (bảng đích: `TABLE_*` e-smart / bảng PostgreSQL hệ cũ,
     xác minh bằng grep)? Kênh dữ liệu/IF được nhắc đến có **bảng chi tiết**: nguồn gốc → trường chính
     (lấy từ interface/schema trong code — nguồn 一次, đối chiếu tài liệu khảo sát) → bảng đích → tác dụng
     nghiệp vụ 1 câu?
  7. Có **bảng đối chiếu tương quan hệ cũ ↔ hệ mới**?
  8. Luồng chính VÀ **từng batch trong phần chi tiết** có **sơ đồ ASCII trong code block** (sơ đồ luồng
     HỆ CŨ + sơ đồ luồng HỆ MỚI đề xuất), kèm **trích code then chốt 3–8 dòng** đã kiểm nguyên văn?
     (Không viết luồng thành đoạn văn đặc.)
  9. Mỗi batch/chức năng trong phần chi tiết theo **template chuẩn (kết luận trước)**: Mục đích (1–2 câu
     tiếng người thường) → **Đề xuất BỎ–GIỮ–THAY đặt ngay đầu mục + khối "Vì sao đề xuất vậy" (3–4 gạch
     lý do)** → sơ đồ luồng CŨ + trích code → chi tiết hệ cũ (bullet) → e-smart/E-GW yêu cầu → sơ đồ luồng
     MỚI → cách làm từng bước (code + Vì sao) → kiểm thử?
  10. Bố cục khoa học: heading con/bullet/bảng, đoạn ≤ ~5 dòng — viết cho NGƯỜI đọc, không phải cho máy?

### 2.4 Trình findings & duyệt

- Gộp findings cả 3 vòng (khử trùng lặp giữa các vòng, giữ đánh số theo vòng), **trình trong chat**
  — KHÔNG tạo file báo cáo review trong workspace (nháp trung gian để ở scratchpad).
- **Chờ user duyệt** (đồng ý/bỏ từng finding) rồi mới sửa tài liệu — không sửa trước khi duyệt,
  trừ khi user đã dặn "sửa luôn" từ đầu.
- Sau khi sửa: quay lại quy tắc 1.4 (chạy lại đủ 3 vòng, phạm vi thu hẹp nếu sửa nhỏ) và trình
  findings của lượt mới như lần đầu.

## 3. Cách chạy

- **Có khả năng tạo subagent** (Claude Code…): chạy **3 agent song song, mỗi agent một vòng**.
  Prompt mỗi agent = **đoạn dẫn mục 2 (định dạng finding) + nội dung vòng tương ứng** + đường dẫn
  tài liệu đích + đường dẫn repo (đã thay thế nếu user trỏ chỗ khác) + HEAD/branch kỳ vọng + lệnh:
  *"KHÔNG sửa file nào; trả findings đánh số [cao/vừa/thấp], mỗi finding gồm vị trí, trích nguyên văn,
  đề xuất câu chữ thay thế; trả lời tiếng Việt, trích tiếng Nhật giữ nguyên văn."*
  Với finding [cao] của vòng 1, có thể thêm agent **kiểm-chứng-đối-kháng**: đưa danh sách finding
  + lệnh *"tìm bằng chứng BÁC BỎ từng finding; trả CONFIRMED/REFUTED kèm dẫn chứng file:dòng"*.
- **Không có subagent**: tự chạy tuần tự 3 vòng, findings nháp ghi ra scratchpad (không ghi vào
  workspace), xong cả 3 vòng thì gộp và trình theo mục 2.4.
- Sau khi user duyệt + sửa xong + review lại đạt: **cập nhật mục 4 của chính SKILL.md này**
  (file đích, HEAD, trạng thái, điểm kiểm đặc thù) rồi chốt phiên bằng skill `/update-memory`.

## 4. Đối tượng review gần nhất (baseline để so)

⚠️ Các bảng dưới là **snapshot** để nhận diện nhanh — nếu lệch với bảng 「Repo đối chiếu」
trong chính tài liệu thì **tin tài liệu**; review xong phải cập nhật lại bảng này (mục 3).

### 4a. Bộ báo cáo batch tách 3 tập — thế hệ v4 (review gần nhất: 2026-08-06)

| | |
|---|---|
| File | **`submit_folder/2026_08_06/new/` — 6 file v4 theo `create-investigation-report/TEMPLATE.md`** (bản chuẩn hiện hành, chờ Codex review ngoài): cặp JP+VN × 3 nhóm theo 3 task Notion (外部連携・受信系（Xzilla取込） 3本 #5–#7 ・ 配信・通知系 4本 #1–#4 ・ CSV・ZIPエクスポート系 4本 #8–#11). Thế hệ trước nằm ở `submit_folder/2026_08_06/` (gốc dữ kiện đã kiểm — không sửa ngược); 2 báo cáo gộp 08-04/08-05 cũng giữ nguyên. Số batch #1–#11 xuyên suốt. LƯU Ý chủ ý (để reviewer sau khỏi báo nhầm): ① JP v4 trích query #1 theo range `:83-104` đồng bộ VN (JP thế hệ trước dùng `:89-100` — cả 2 đều đúng repo); ② câu hỏi /EST bản đầy đủ chỉ nằm ở tập Xzilla §3, 2 tập kia trỏ về ("hỏi 1 lần chung"); ③ 配信 §9 bỏ mục có ghi chú, CSV §6 viết gộp 4 batch — đều hợp lệ template |
| Cần repo | đủ 5 nguồn mục 0-3a; HEAD kỳ vọng: `eminel_gw_project@fbc0af0` (main — điều tra gốc tại `788b438`; file nhóm Xzilla/CSV trích không đổi giữa 2 commit, nhóm 配信 đã cập nhật số dòng B05/D03 theo fbc0af0) ・ `legacy_eminel_docs@ccd8f56` (main) ・ backend@`dc39aa39` (`gw-syp-dev`) ・ web-admin@`e550326` (`gw-syp-dev`) ・ app = snapshot không mốc |
| Trạng thái lần review cuối (2026-08-06, bộ v4) | 3 reviewer độc lập (1/cặp) chạy đủ 3 vòng + tuân thủ TEMPLATE v4: **Xzilla** 28 điểm spot-check + grep phủ định tái hiện 100% — 1 [cao] (path v1.2 ghi nhầm `1_product/`) + 2 [vừa] + 6 [thấp], vá hết; **配信・通知系** 25+ spot-check + 3 con số tự đếm (105/81/3) xác nhận — 2 [vừa] ("still" sót trong heading JP; rơi kết luận 集計・計算系) + 5 [thấp], vá hết; **CSV/ZIP** 22 spot-check — 4 [vừa] (rơi mục 使い続け; mã nội bộ lọt blockquote gửi khách; "still"; trỏ chéo §7→§7.6) + 4 [thấp], vá hết. Quét cuối toàn bộ 6 file: fence chẵn (16/34/46 ×2), tàn dư (`1_product/00_integrated`, " still ", mã nội bộ trong blockquote khách) = 0. Thế hệ trước (2026_08_06 gốc) từng qua: Xzilla 4-agent + 3 vòng kiểm tuân-thủ; CSV bắt 1 [cao] 前月→**前々月** |
| Điểm kiểm đặc thù nếu review lại | ① 3 trang QA Notion vẫn 回答中 (tham chiếu 08-04) — mở trang gốc trước khi trích lại; ② baseline số bước 対応ステップ mới (kiểm thử = bước cuối theo template): #1=5・#2=6・#3=5・#4=6・#5=4・#6=4・#7=6; ③ `handleControlDevice` là hàm local của `batch-start-dr/app.ts:81`, lõi thật là `business-logic/control-device.ts` (4 nhánh SERVER_TYPE) — đừng sửa ngược theo cách viết cũ; ④ các điểm treo CLD-06/CLD-07/spec [G]/[I]/SVC-03 — chốt cái nào thì mục tương ứng cập nhật; ⑤ 6 điểm lệch tài liệu khảo sát ESTA phân bổ theo tập (Xzilla 5 ・ 配信 3 ・ CSV 3 — có trùng nhau); ⑥ 質問表 đang 送付前 — khi gửi khách rồi, sửa các chỗ 「（送付前）」 |

## Liên hệ skill khác

- `create-investigation-report` — nơi sống của TEMPLATE.md v4 (nguồn sự thật duy nhất về cấu trúc báo cáo
  điều tra); Vòng 2 kiểm tuân thủ theo file đó.
- `analyze-change-request` — findings hệ thống/lặp lại đi qua đây để sửa gốc thay vì vá lẻ (⛔#11);
  yêu cầu sửa của user trong lúc review cũng vậy.
- `update-memory` — chốt phiên sau khi review/sửa xong.
- `notion-connect` — khi cần mở lại trang QA Notion kiểm trạng thái 回答中/回答済.
- `../sources/eminel_gw_project/.claude/skills/fact-check` — kiểm chứng một khẳng định đơn lẻ
  (skill của repo dự án; 3-step-review là quy trình cấp tài liệu, fact-check là cấp câu).
