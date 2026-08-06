# SESSION 2026-08-04 (phiên 2, chiều) — 5 QA Notion đầu tiên vào tài liệu + báo cáo phán định 11 batch legacy
> ⛔ TRẠNG THÁI ĐÃ LỖI THỜI (2026-08-05) — xem `03_session_20260805_soanBaoCaoBatchJP_review2luot.md`.
> Đọc SAU `00_INDEX.md`. ⭐ TRẠNG THÁI MỚI NHẤT (chưa có file nào thay).

## 1. Bối cảnh & mục tiêu phiên

- **QAデータベース Notion đã hoạt động**: Dat đăng câu hỏi 2026-08-03 (17:30–17:33), mui trả lời trong ngày 08-03→08-04. Phiên này đọc 5 trang QA đầu (qua ảnh chụp user dán — chưa có MCP/token Notion) → cập nhật bộ tài liệu `requirements/`.
- Task mới từ user: phán định 11 batch hệ cũ (3 nhóm 配信・通知系/Xzilla取込/CSV・ZIP) — có sẵn trong e-smart không, E-GW cần không → báo cáo vào `submit_folder/2026_08_04/`.
- User dặn (phải nhớ): **KHÔNG push gì lên git khi chưa được yêu cầu.**

## 2. ĐÃ LÀM

### 2a. Cập nhật tài liệu theo 5 QA (đều 回答中 lúc đọc 2026-08-04)

Nội dung 5 QA + nguyên văn: xem **bảng ở guide 9.4** (nguồn sự thật trong workspace). Tóm một dòng mỗi cái:
1. App là 開発対象 (takahashi) — ngược chữ 対象外 của v1.2 §1-2, xác nhận "bẫy lớn" ở guide 1.6.
2. Server E-GW: 基本的には hướng hệ độc lập; mui nhờ báo "chức năng nên dùng tiếp hệ hiện hữu" (swan).
3. 管理画面: chung source + chung deploy với E-Smart (takahashi).
4. Điều tra hệ cũ: conciergesv+eminelsv = phạm vi điều tra SYP (không phải phạm vi phát triển); HEMS-SV(m2-cloud) do mui làm, GW giao tiếp qua đó, spec chia sẻ sau (swan).
5. Badge/rank: 「今の所、2026年スコープ外です」 (takahashi) — chính là **câu 1 qa_kitagas đã được đăng lên Notion**.

Chỗ sửa (15 vị trí + fix sau review): `onboarding_guide.md` — header; 1.2 (note 統合される); 1.6 (khối xác nhận QA1 + chú số ①=③); bảng component 2.2; đáp án C1; **4.2 tiểu mục mới** hemssv/conciergesv/eminelsv + 🔸m2-cloud; 6.x + B.1 (badge trả lời tạm); **8.4** (sửa gloss eminelsv + ❌ mâu thuẫn CLD-01内訳 vs QA4 + note CLD-02); **9.4 tiểu mục mới** (bảng 4 QA + 4 điều rút ra); 7.5; E.2 (giới thiệu QAデータベース + gloss property); 0.4; 0.2 + README §5 (thêm ký hiệu **🔸 giả thuyết**); 9.5. `qa_kitagas.md` — header hàng Diễn biến + blockquote đầu câu 1.

### 2b. Review §8 sau sửa (workflow 14 agent) — 21 findings, đã xử lý HẾT

- 10 confirmed (kiểm chứng đối kháng) + 8 tự thẩm hợp lệ + 3 trùng. Lỗi đáng nhớ đã mắc → thành quy tắc ⛔#8 mới trong 00_INDEX: diễn giải vượt nguyên văn ("không chung component" trong khi swan chỉ nói 「基本的には…方向」+ vế ただし), attribution tên trần ("takahashi" ≠ 高橋 北ガス — phải ghi "masao takahashi (mui)"), thiếu ngày đọc trạng thái 回答中.

### 2c. Báo cáo batch (submit): `submit_folder/2026_08_04/report_batch_3nhom_doichieu_esmart_egw.md`

- Điều tra bằng 4 agent song song: code 11 Command + cron (`legacy_eminel_docs`), khảo sát ESTA (`eminel_gw_project/docs/eminel-smart/` — 6 file), yêu cầu E-GW (`docs/eminel`), app Flutter ESTA. Sau đó 2 agent review (30+ trích dẫn khớp; 18 finding logic đã sửa).
- **Tối 04/08**: user clone thêm `syp-eminelstandard-backend` (@`dc39aa39`) + `syp-eminelstandard-web-admin` (@`e550326`), đều branch `gw-syp-dev` → 4 agent điều tra code trực tiếp → **báo cáo VIẾT LẠI toàn bộ thành bản liền mạch** (user chỉnh cách làm: không chắp mục "bổ sung", không mốc ngày giờ — thành quy tắc ⛔#9) → review 3 vòng + vá toàn bộ finding.
- **Nâng chuẩn lần cuối theo yêu cầu user**: chỗ "e-smart đã có" phải **dán trích đoạn code thật + giải thích từng nhóm code** (16 khối fenced — vòng 1 xác nhận 16/16 khớp nguyên văn, kiểm tới tận shell trong tgz); chỗ "tạo mới/bỏ" phải có mục **"Cách làm từng bước"**; §1 chia **3 bảng theo nhóm, tóm tắt từng batch (11 dòng)** rồi mới vào chi tiết. Đã review 3 vòng lần cuối + vá hết finding (gloss cho người mới, nhất quán bảng↔chi tiết).
- Kết luận chính: #1 エコ暖房ポイント = dùng lại hạ tầng point/PI e-smart + tạo mới logic phán định; #2 advice = tạo mới (判定式 đã trích ở spec [G] G-C-05); #3 push = bỏ bản cũ, dùng hạ tầng FCM e-smart; #4 DR = không code 2026 nhưng **2026 phải chốt GW có giữ trạng thái không** (câu 5 QA); #5/#6 Xzilla 解約/支払者 = không port nguyên, gộp luồng 統合インポート e-smart (*推定*, chờ IF-01/CLD-07); #7 電力30分値 = **tạo mới, 必須 2026, nặng nhất**; #8–11 CSV/ZIP = bỏ (bản chất backup-để-xóa), thay bằng retention mới + admin download [I].

## 3. QUYẾT ĐỊNH & PHÁT HIỆN

- **Cấu trúc memory: giữ PHẲNG, không chia folder layer** (user chốt cuối phiên). Ngưỡng ngoại lệ ~8–10
  file session → tạo `memory/archive/` cho file ⛔ lỗi thời — quy ước đã ghi vào `skillAI/update-memory/SKILL.md`.

- **❌ mới ghi nhận**: chú thích 内訳 CLD-01 (`eminelsv`＝GW管理クラウド実装分) mâu thuẫn QA4 (`eminelsv`＝màn hình quản trị vận hành; GW giao tiếp = `hemssv`); bộ source đã nhận **không có hemssv**. Ghi ở guide 8.4.
- **Từ code backend e-smart (tối 04/08)**: PI連携 **có thật** trong backend (gọi thẳng PointInfinity, form Shift_JIS + XML — cùng họ giao thức hệ cũ, rollback khi PI lỗi); **5 điểm tài liệu khảo sát `docs/eminel-smart/` lệch code** (500件/batch không có ・ import chạy mỗi-giờ 0–7h chứ không 日次 ・ lock 5 phút không phải 6 ・ `CsvDownloadHistory` thuộc chiều NHẬN ・ automation không chạy 毎分); branch `gw-syp-dev` cả 2 repo **chưa có commit E-GW nào**; backend có **chiều xuất SFTP `/EST`** (6 batch export CSV thiết bị hằng ngày 8h) — 🔸 đích có phải Xzilla/DWH chưa xác nhận; cơ chế lịch one-shot EventBridge = lời giải sẵn cho yêu cầu [G] G-A-02.
- 🔸 CHƯA kiểm chứng: "m2-cloud" = tên hiện thực của GW管理クラウド?; "SYP làm app" (từ ngữ cảnh QA1); các mục *推定* trong báo cáo batch (đề xuất #5/#6); đích `/EST`.
- Phát hiện nhỏ: A03 ghi エコ暖房ポイント hiện hành là 「12〜3月」 nhưng code + cron hệ cũ chạy **hàng tháng quanh năm** (không điều kiện mùa) — đã ghi vào báo cáo, cần nêu khi chốt spec.
- 04_バッチ一覧 ghi 「11種Publisher」 nhưng thực tế 10 Publisher + 1 file option.

## 4. Thay đổi phía repo dự án

- `git fetch` cả 5: `eminel_gw_project` = `788b438` (= origin/main, không đổi so với phiên 1); `legacy_eminel_docs` = `ccd8f56`; `syp-eminelstandard-backend` = `dc39aa39` và `-web-admin` = `e550326` (đều branch `gw-syp-dev`, user clone tối 04/08); `syp-eminelstandard-app-syp-dev` là **snapshot không phải git repo**. Không commit/push gì.

### 2d. Skill mới: `skillAI/3-step-review/` (cuối phiên)

- User sẽ ôm folder sang máy khác để tự review báo cáo batch → đã đóng gói quy trình review thành skill:
  3 vòng (xác thực dẫn chứng/code ・ nhất quán nội bộ ・ dễ hiểu người mới) + 4 tiêu chí + thủ tục
  bắt đầu ở máy mới (bootstrap, kiểm 5 repo, git fetch/so HEAD, xử lý khi repo tiến lên) + bảng baseline
  lần review cuối của báo cáo batch (kể cả 4 điểm kiểm đặc thù khi review lại). Đã đăng ký vào CLAUDE.md.
- Skill đã được đổi tên theo user (`review-3-buoc` → **`3-step-review`**) và **tự review bằng 2 agent**
  (đối chiếu yêu cầu + đóng vai AI máy mới) → viết lại theo findings: bỏ mâu thuẫn với ⛔#5 (sửa nhỏ vẫn
  đủ 3 vòng, chỉ thu hẹp phạm vi), thêm: chọn tài liệu đích mặc định, mục 2.4 trình findings trong chat +
  chờ user duyệt, fallback (fetch lỗi / thiếu repo / thiếu bảng Repo đối chiếu / snapshot không mốc),
  ⛔#2 grep nhiều dạng viết, mẫu prompt subagent đầy đủ, lệnh tự cập nhật baseline mục 4 sau mỗi lần review.
  Đồng thời sửa CLAUDE.md mục SOURCES (bổ sung backend + web-admin, ghi rõ app là snapshot không git).

## 5. VIỆC DỞ DANG / TIẾP THEO

0. **(User chủ trì) Review lại báo cáo batch trên máy khác** — phiên mới chạy `/3-step-review` theo SKILL.md.
1. **Trả lời vế ただし của QA 独立デプロイ trên Notion** (việc SYP chủ động): 2 vế — hệ cũ: không batch nào đáng dùng tiếp nguyên trạng; ESTA: push/point-PI/Xzilla-import/data-export. Chi tiết + lưu ý xác nhận nghĩa 「既存システム」: báo cáo §1.
2. **Theo dõi 5 trang QA (đều 回答中)** — khi chuyển 回答済: cập nhật các chỗ đã đánh dấu trong guide (grep "回答中") + B.1 theo README §9; nếu CLD-01内訳 không được sửa → cân nhắc thêm mục Phụ lục B.
3. **Hỏi mui xác nhận đích luồng export SFTP `/EST`** của backend e-smart (≒ 「EMINELデータの共有」 F-ES-10? — báo cáo §6#3).
4. Kế thừa phiên 1: chốt kihara Q5 (DR/GW有状態 — giờ càng gấp vì báo cáo batch cũng treo vào đó, §6#1) → gửi `qa_kitagas.md`; theo dõi B06; cân nhắc cập nhật guide 0.7 (legacy_eminel_docs đã có local).
5. Khi IF-01/CLD-07 có spec: rà lại nhóm Xzilla (§4 báo cáo), gồm cả chiều xuất; cân nhắc thêm câu QA về 保持期間/loại dữ liệu download khi review spec [I] (§6#6).

## 6. CHƯA KIỂM

- 5 trang QA chỉ đọc qua **ảnh chụp** user dán — chưa có URL trang, chưa xác nhận lại trực tiếp trên Notion (guide đã ghi quy tắc "mở trang gốc trước khi trích lại").
- Đích SFTP `/EST` (secret ngoài repo); tên thương mại chính xác của hợp đồng ゆ抜く/YUNUKKU (PG003 — app ghi 「ゆうナビ24ネオ」).
- Kế thừa phiên 1: nội dung `legacy_eminel_docs` chưa đối chiếu với chương 4 guide; 2 script skillAI chưa chạy token thật.
