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

Bốn tiêu chí xuyên suốt (user đặt ra, không thương lượng): **① chi tiết của dẫn chứng ・ ② chính xác
・ ③ xác thực ・ ④ dễ hiểu cho người mới vào dự án đọc lần đầu.** Quy trình kế thừa tinh thần checklist
`requirements/README.md` §8 và tổng quát hóa cho mọi tài liệu KB; đúc kết từ các lần review báo cáo
batch 2026-08-04.

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

### 4a. Bản tiếng Nhật báo cáo batch (review gần nhất: 2026-08-05)

| | |
|---|---|
| File | `submit_folder/2026_08_05/旧EMINELバッチ移行判定報告書_3グループ11本.md` — bản JP cho mui của báo cáo batch: cùng nội dung phán định với bản VN, bố cục 結論先出し, không dán khối code (chỉ 🔍 ref), 対応ステップ đánh số khớp bản VN |
| Cần repo | như bản VN (bảng 4b) — cùng 5 nguồn, cùng HEAD kỳ vọng |
| Trạng thái lần review cuối (2026-08-05) | Lượt 1: workflow 8 agent (5 xác thực + 2 nhất quán/fidelity-VN + 1 văn phong JP) → 33 findings sau dedup, vá hết (2 [cao]: ゆ抜く→「ゆーぬっく」 theo `backend constants.ts:1065`; bỏ vế 「共通デプロイ」 vượt nguồn khỏi 要旨 QA 管理画面). Lượt 2 thu hẹp: 3 agent → 13 findings nhỏ, vá hết; grep tàn dư 0 hit. Fidelity với bản VN: 11 phán định + toàn bộ con số khớp 100% |
| Điểm kiểm đặc thù nếu review lại | ① 4 điểm của bảng 4b áp dụng y nguyên; ② JP đã sửa 6 điểm nội dung mà **bản VN còn dính** (ゆ抜く→ゆーぬっく ・ Node 20→nodejs24.x + 付録A=6点 ・ 4/19 cron advice thông năm ・ DR start/end schedule đăng ký lúc 配信完了 chứ không phải lúc admin tạo ・ #6 chỉ nạp lại 7 loại 契約種別 ・ emn_confirm append-only) — so JP↔VN thấy lệch các chỗ này thì **JP đúng**; ③ 質問表 đang 送付前 — khi đã gửi khách, sửa các chỗ 「（送付前）」; ④ F-ES-10 tên chính thức = 「Xzilla連携」 (v1.2:415) |

### 4b. Báo cáo batch bản VN (review gần nhất: 2026-08-04)

| | |
|---|---|
| File | `submit_folder/2026_08_04/report_batch_3nhom_doichieu_esmart_egw.md` |
| Cần repo | đủ 5 nguồn ở mục 0-3a; HEAD kỳ vọng: `eminel_gw_project@788b438` (main) ・ `legacy_eminel_docs@ccd8f56` (main) ・ backend@`dc39aa39` (`gw-syp-dev`) ・ web-admin@`e550326` (`gw-syp-dev`) ・ app = snapshot không mốc |
| Trạng thái lần review cuối (2026-08-04) | Vòng 1: 16/16 khối code khớp nguyên văn (kiểm tới shell trong `10_バッチ処理/…tgz`); vòng 2–3: findings đã vá hết. Các grep-0-hit lần đó tái hiện được nhưng **không lưu vết lệnh** — lần review sau tự chạy lại từ đầu |
| Điểm kiểm đặc thù nếu review lại | ① 3 trang QA Notion trích trong §7 đang 回答中 — mở trang gốc xem đã 回答済 chưa, nội dung đổi → sửa §1/§2 liên quan; ② branch `gw-syp-dev` 2 repo e-smart lúc đó CHƯA có commit E-GW — có commit mới thì §2 "bắt đầu từ 0" phải viết lại; ③ các điểm treo CLD-06/CLD-07/[I]/SVC-03 — chốt cái nào thì mục tương ứng cập nhật theo; ④ 5 điểm tài-liệu-khảo-sát-lệch-code ở mục Giới hạn — nếu `docs/eminel-smart/` được sửa thì bảng đổi theo |

## Liên hệ skill khác

- `update-memory` — chốt phiên sau khi review/sửa xong.
- `notion-connect` — khi cần mở lại trang QA Notion kiểm trạng thái 回答中/回答済.
- `../sources/eminel_gw_project/.claude/skills/fact-check` — kiểm chứng một khẳng định đơn lẻ
  (skill của repo dự án; 3-step-review là quy trình cấp tài liệu, fact-check là cấp câu).
