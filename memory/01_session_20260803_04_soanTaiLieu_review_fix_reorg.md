# SESSION 2026-08-03 → 08-04 — Soạn tài liệu học, review 13-agent, sửa toàn diện, dựng AGENTS workspace
> ⛔ TRẠNG THÁI ĐÃ LỖI THỜI (2026-08-04 chiều) — xem `02_session_20260804_qaNotion_capNhatTaiLieu_baoCaoBatch.md`
> Đọc SAU `00_INDEX.md`.

## 1. Bối cảnh & sản phẩm
- Dat soạn bộ tài liệu nhập môn E-GW cho người mới (kể cả mới học IT): `requirements/onboarding_guide.md`
  (10 chương + 7 phụ lục, ~4.000 dòng, 220+ trích dẫn nguồn) + `requirements/qa_kitagas.md` + `requirements/README.md`
  (bộ khung + checklist review 3 vòng §8; chuyển từ root vào requirements/ ngày 08-04, cuối phiên). Đối chiếu repo `eminel_gw_project` **commit `788b438` = origin/main 2026-08-03**.

## 2. Chuyện quan trọng nhất phiên: REPO LOCAL CŨ (nguồn của quy tắc #1)
- Review 13-agent (04/08) ban đầu báo "lỗi nặng": A04_badge_rank.md không tồn tại, số dòng B02 lệch 5–25,
  trạng thái section sai, "22 section" sai… → fetch origin phát hiện **local dừng ở commit 23/07, origin tới 03/08**.
  Đối chiếu lại với origin/main: TẤT CẢ các "lỗi nặng" đó đều là lỗi giả — tài liệu đúng.
- Đã `git pull` → local = `788b438`. Commit 03/08 (要件アップデート) thêm section **B06_myhome_generation** (未着手,
  tách từ B4 ngày 07-30) → repo giờ 23 section; guide đã cập nhật theo.

## 3. Các sửa nội dung ĐÃ LÀM trong guide (v1.0 → v1.1, đều đã verify với nguồn)
- **2.75人月 ≠ công số app**: đó là 劣後可能工数; app thật ≈ **11人月** (cộng dòng F-AP, 10_feature_list 119–138). Sửa 1.6.
- **❌ mâu thuẫn mới ghi nhận**: スマリモ nhận MẤY con số — business flow slide 37 nói 2 (設定温度+GW取得温度),
  v1.2 dòng 494–497 nói cơ bản CHỈ 設定温度 (pattern ② không cảm biến → 現在温度 trống). Ghi ở 3.2, phải hỏi khi làm firmware.
- Hạn **tháng 9 fix design+spec CÓ nguồn**: camp day2 dòng 148 「2026/9｜デザイン・仕様がすべてフィックス」(まずいメソッド).
- 22_decisions dòng 31 ghi nguyên văn 「**照明**アドバイス」 (nghi typo của 省エネアドバイス) — mọi chỗ nhắc đều chú ※.
- CTR-01: cấu trúc hợp đồng 1 mẹ + 3 con **CHƯA ký** (北ガス未合意・ドラフト段階) — guide 6.5 đã ghi 🔴.
- Bルート lấy cả 30分値+瞬時値, B=hiếm/C=đường chính (glossary 39, day1 96); 9 pattern liệt kê đủ; 見守り hệ cũ
  tách "tên trong nguồn" vs "điều kiện suy đoán từ hệ mới"; 優先運転 vẫn còn dòng trong 10_feature_list (126);
  mốc 2024-09-30 nguồn thật là 02_customer.md dòng 42; CTR-03 4 mục ngang hàng (bỏ chữ "nguyên nhân chính").
- Sư phạm: 0.6 = 17 thuật ngữ (thêm Webhook/MQTT); cây 5.5 thêm mũi tên 省エネモード→室温制御 + **bảng ma trận
  cấu hình × chức năng**; gloss tại chỗ DR/TagTag/Stream/エネマネAI; 💡 định nghĩa lại = diễn giải sư phạm.
- B.4 thu hẹp: chỉ B5 còn lệch file↔index (B4 đã đồng bộ trên origin).

## 4. qa_kitagas.md — trạng thái SẴN SÀNG GỬI (qua PM mui)
- 8 câu chính + 4 dự phòng (mới thêm DP3 = GW-01 thúc thời điểm cung cấp spec logic sưởi; DP4 = スケジュール刻み).
- Khối JP đã sạch đồ nội bộ (quy tắc #4); 参照資料 JP = tên tài liệu hai bên cùng biết; keigo đã soát (ご整理いただき…).
- **Q3 cố ý hỏi dẫn dắt** 「実装するという理解でよろしいでしょうか」 (vì feature list đã tính 0.75人月) — bản Việt đã khớp, có ghi chú nội bộ.
- **Q5 (DR giữ trạng thái) — PHẢI chốt nội bộ với kihara TRƯỚC khi gửi** (ghi chú nội bộ trong file).
- Ghi chú độ phủ cuối file: C.2, C.11, C.12 cố ý KHÔNG hỏi khách (cần mui định nghĩa trước / đi đường PM).

## 5. Skill đã tạo (skillAI/)
- `notion-connect` + `slack-connect`: MCP (ưu tiên) + REST fallback stdlib-only, READ-ONLY, token hỏi mỗi lần.
  Là "chân" Slack/Notion của skill `/trace-source` trong repo dự án. Script đã py_compile + smoke-test OK.
- `update-memory`: skill chốt ngày — xem SKILL.md.

## 6. Tái tổ chức workspace (08-04, Dat tự làm + AI bổ sung)
- Repo git → `../sources/` (eminel_gw_project ・ legacy_eminel_docs ・ syp-eminelstandard-app-syp-dev).
  `legacy_eminel_docs` là repo MỚI xuất hiện trong sources (thiết kế + code hệ cũ — trước đây guide 0.7 ghi "không có ở local").
- Tài liệu + assets → `requirements/`. Tạo `memory/` + `AGENTS.md` + `CLAUDE.md` (cơ chế theo OMEGA/2608_001).
- ⚠️ Hệ quả đường dẫn: link tương đối kiểu `eminel_gw_project/docs/...` trong guide giờ hiểu là `../sources/...`
  (quy ước ghi ở CLAUDE.md; chưa sửa hàng loạt ~220 trích dẫn trong guide — chấp nhận được vì quy ước đã ghi).
- Cuối phiên: README.md chuyển từ root vào `requirements/README.md` (khung đi cùng sản phẩm nó quản);
  §2 của nó thu hẹp về phạm vi requirements/, cấu trúc toàn workspace chỉ còn ở CLAUDE.md; link ở header guide
  đã trỏ cùng thư mục. Root giờ chỉ còn AGENTS.md + CLAUDE.md làm entry point.

## 7. VIỆC DỞ DANG / NGÀY MAI LÀM GÌ
1. **Chốt kihara Q5** → gửi `qa_kitagas.md` qua PM mui (quyết luôn có kèm DP3/DP4 không).
2. Theo dõi **B06** được viết → cập nhật bảng 7.3 + con số "20/23".
3. `legacy_eminel_docs` mới có ở sources → cân nhắc cập nhật guide 0.7 ("ba thư mục không có ở bản local" có thể đã lỗi thời một phần).
4. Khi 北ガス trả lời QA → chạy quy trình README §9: chuyển mâu thuẫn đã giải quyết khỏi Phụ lục B, cập nhật qa_kitagas.

## 8. CHƯA KIỂM (ghi rõ)
- Nội dung `legacy_eminel_docs` chưa được đối chiếu với chương 4 của guide (chương 4 viết từ docs cấp 2 old_eminel).
- 2 script skillAI chưa chạy với token thật (mới smoke-test offline).
- submit_folder/2026_08_04 do Dat tự chụp — AI chưa xác nhận nội dung bên trong.
