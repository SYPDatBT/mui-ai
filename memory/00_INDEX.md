# MEMORY INDEX — Onboarding dự án EMINEL Gateway (E-GW)

## ⛔ QUY TẮC VẬN HÀNH — BẮT BUỘC, ĐỌC & TUÂN THỦ TRƯỚC MỌI VIỆC
> Sinh ra từ lỗi thật đã mắc trong workspace này. Vi phạm = lỗi nghiêm trọng. Áp dụng MỌI phiên, MỌI task.

1. **`git fetch` + so `origin/main` TRƯỚC khi fact-check trích dẫn.** (Lỗi đã mắc 08-04: repo local cũ 11 ngày
   → review kết luận nhầm "file A04 không tồn tại", "số dòng B02 lệch hàng loạt" — thực ra tài liệu ĐÚNG,
   local SAI. Suýt bắt sửa hàng loạt chỗ không sai.)
2. **Grep tài liệu Nhật phải thử NHIỀU dạng viết.** (Lỗi đã mắc 08-04: grep "9月" sót "2026/9" trong bảng
   lịch trại tập trung → kết luận nhầm "hạn tháng 9 không có nguồn"; nguồn nằm ở day2 dòng 148.)
   Cùng lý do: tìm theo CẢ mã lẫn tên (F-ES-05 ↔ 見守り通知), センサ ↔ センサー.
3. **Tách QUAN SÁT khỏi SUY ĐOÁN; không bịa nguyên nhân.** Suy đoán gắn nhãn "🔸giả thuyết — CHƯA kiểm chứng".
   Trong guide, box 💡 = diễn giải sư phạm, KHÔNG phải căn cứ — đừng trích 💡 làm bằng chứng với ai.
4. **Khối tiếng Nhật gửi khách phải SẠCH đồ nội bộ**: không CLD-xx/GW-xx, không đường dẫn repo, không 🔴,
   không xin thứ khách ĐÃ cung cấp (kiểm `old_eminel/00_sources.md` trước khi xin tài liệu).
5. **Sửa tài liệu xong PHẢI chạy review theo `requirements/README.md` §8 (3 vòng)** — kể cả "sửa nhỏ". Đợt 08-04 vòng review
   sau-sửa bắt được 13 lỗi do chính đợt sửa để sót (tàn dư "22 section", câu dẫn "Hai câu" khi đã 4 câu…).
6. **Đường dẫn khi fact-check**: `eminel_gw_project/...` trong tài liệu = `<SOURCES>/eminel_gw_project/...`
   (mặc định `../sources/`). Số dòng ứng với **commit ghi ở bảng meta đầu guide** (dòng 10) — đọc ở đó,
   đừng nhớ theo memory. Tài liệu khác (báo cáo điều tra) khai mốc riêng ở bảng 「Repo đối chiếu」 của chính nó.
7. **CẤM ghi token** (Notion/Slack/API) vào memory, log, output — hỏi user mỗi lần.
8. **Trích QA/Notion phải bám NGUYÊN VĂN + đủ định danh.** (Lỗi đã mắc 08-04: biến 「基本的には独立…方向」+vế ただし
   thành "không chung component" — diễn giải vượt nguồn; ghi "takahashi" trần gây nhầm với 高橋 phía 北ガス.)
   Chuẩn: nguyên văn trong 「」, người trả lời ghi đầy đủ "masao takahashi (mui)"/"swan (mui)", kèm ngày đọc
   trạng thái (回答中 là dữ liệu sống). KHÔNG push git khi user chưa yêu cầu (user dặn 08-04).
9. **Tài liệu knowledge base: cập nhật = VIẾT LẠI liền mạch, không chắp vá.** (User chỉnh 08-04 khi làm báo cáo
   batch.) Không thêm mục "bổ sung ngày X" cuối file, không rải mốc ngày giờ cập nhật, không giữ "nhãn cũ làm
   vết lịch sử" — thông tin mới thì reformat toàn bộ (hoặc ít nhất phần sửa) như viết mới với hiểu biết hiện tại,
   rồi chạy review 3 vòng (chi tiết dẫn chứng ・ chính xác ・ xác thực ・ dễ hiểu cho người mới đọc lần đầu).
10. **Tài liệu TỰ CHỨA — TUYỆT ĐỐI không bắt người đọc tra ngược; viết cho NGƯỜI, không phải cho máy.**
   (User chỉ đạo 08-06 khi tách báo cáo batch 3 tập.) Cụ thể: mã hiệu (CLD-xx/IF-NN/IF-4số/SVC-xx/spec…)
   chú giải tại chỗ MỖI lần xuất hiện theo ngữ cảnh lần đó; con trỏ §/#N kèm tóm tắt nội dung đích; bước làm
   ghi code đến từng layer/file (path đã kiểm tồn tại) + dòng "Vì sao/理由"; phán định nói rõ BỎ gì–GIỮ gì–
   THAY bằng gì; luồng xử lý đi từ code xuống tận bảng DB (grep `TABLE_*` xác minh, không đoán) và vẽ SƠ ĐỒ
   ASCII trong code block thay vì đoạn văn; kênh dữ liệu/IF nhắc đến phải có bảng chi tiết nguồn →
   trường chính (từ interface/schema trong code) → bảng đích → tác dụng nghiệp vụ; có bảng đối chiếu hệ cũ↔mới; **mỗi batch trong phần chi tiết theo
   template chuẩn (kết luận trước)**: Mục đích (1–2 câu) → Đề xuất BỎ–GIỮ–THAY đặt ngay đầu mục + khối
   "Vì sao đề xuất vậy" (3–4 gạch lý do) → sơ đồ luồng CŨ + trích code then chốt 3–8 dòng → chi tiết (bullet)
   → yêu cầu E-GW → sơ đồ luồng MỚI → cách làm từng bước (code + Vì sao) → kiểm thử;
   bố cục khoa học (heading/bullet/bảng, đoạn ≤5 dòng). Checklist 10 điểm nằm trong skill `3-step-review`
   Vòng 3; cấu trúc đầy đủ = `skillAI/create-investigation-report/TEMPLATE.md`. Áp cho CẢ bản JP lẫn VN.
11. **User gửi yêu cầu sửa/feedback → BẮT BUỘC đi qua skill `analyze-change-request` TRƯỚC khi sửa**:
   trích nguyên văn yêu cầu → phân loại (fix cục bộ / triệu chứng hệ thống / đổi thiết kế / mâu thuẫn)
   → tổng quát hóa thành quy tắc → tranh biện đa agent (MINIMAL vs HOLISTIC vs CRITIC, brainstorm chéo)
   → ĐỀ XUẤT giải pháp tổng thể cho user duyệt → thực thi nguyên khối (sửa gốc template/skill trước, áp
   xuống tài liệu sau). **Đồng thuận ngay + vá ngay = lỗi quy trình.** (Bài học 08-06: chuỗi vá đuổi theo
   từng yêu cầu tạo tài liệu "nồi lẩu", phải đập làm lại từ đầu theo template mẫu.)
12. **MỌI file QA sống ở `submit_folder/qa/` — tên file = mô tả nội dung hỏi + NGÀY THÁNG.** (User chỉ đạo 08-13,
   đã tự tay dời `qa_kitagas.md` từ `requirements/` và `qa_batch_csvzip.md` từ `submit_folder/2026_08_12/` vào đó.)
   Quy ước tên: `qa_<chủ-đề>_<YYYYMMDD>.md` — ví dụ `qa_batch_shukei_20260815.md`. **Không** rải file QA theo
   thư mục ngày nộp như tài liệu điều tra, **không** để trong `requirements/`. Hai file cũ giữ nguyên tên
   (chưa có ngày) vì đã bị nhiều tài liệu trích dẫn — quy ước ngày áp cho file TẠO MỚI từ 08-13.
13. **grep phủ định phải MỞ CẢ FILE NÉN** (`.tgz`/`.zip`/`.tar.gz`): giải nén ra thư mục tạm rồi grep, đừng
   grep repo trần rồi kết luận "0 hit". (Lỗi đã mắc: review 08-12 báo *"shell flock không có căn cứ, grep
   `flock` = 0"*; thực tế `flock` nằm trong `.sh` **bên trong** `cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz`
   — 08-13 giải nén thấy ngay. Suýt vá một khẳng định ĐÚNG thành SAI.) Hệ quả của ⛔#2, và: **finding do agent
   review sinh ra vẫn phải kiểm chứng lại trên nguồn trước khi vá** — agent sai thì vá làm hỏng tài liệu đúng.
14. **Trước khi tin số dòng/nội dung trên đĩa: `git log -1` chính repo đó.** Ghi chép "đã pull X" của phiên
   trước KHÔNG đủ tin. (Phát hiện 08-13: working tree `eminel_gw_project` đứng ở `788b438` suốt từ 03/08 trong
   khi memory ghi đã pull `fbc0af0`→`460c671`; reflog chỉ có 1 lần merge. Các phiên đó đọc bằng
   `git show <commit>:<path>` nên kết luận vẫn đúng — nhưng ai tin ghi chép mà đọc thẳng file trên đĩa thì sai.)
15. **Việc NẶNG (fan-out nhiều agent / phase dài) phải SỐNG SÓT được qua sập trần usage — phòng thủ 2 lớp,
   tự làm không đợi user nhắc.** ① **Chốt memory TRƯỚC khi phóng**: cập nhật 🎯 của 00_INDEX + file session ⭐
   (đã xong gì ・ đang chạy gì ・ kết quả nằm ở file/journal nào — đường dẫn cụ thể ・ bước tiếp theo đánh số),
   đủ để phiên mới bootstrap là tiếp tục ngay. ② **CHIA việc thành KHỐI NHỎ TỰ-HOÀN-CHỈNH**: mỗi khối xong là
   kết quả nằm trên ĐĨA + memory nhích theo, rồi mới sang khối sau — không dồn thành một lượt chạy dài mà kết quả
   chỉ có khi TẤT CẢ xong; khối chưa chạy phải chạy-lại-được độc lập (script/prompt lưu sẵn ra file, ghi rõ
   khối nào xong khối nào chưa); sập giữa chừng = mất tối đa 1 khối. Kết quả trung gian (findings, verdict)
   không bao giờ sống trong chat. **Định lượng (user chốt 08-16): TRƯỚC khi phóng phải ƯỚC LƯỢNG token theo
   `notes/usage_budget.md` (đơn giá hiệu chỉnh từ số thật) — ước lượng > 20% ngân sách gói Max 20x
   (= ~600k token/khối theo giả định 3M/cửa sổ 5h) → BẮT BUỘC chia khối; chạy xong ghi số thật vào ledger
   của file đó để hiệu chỉnh dần.** (Lỗi suýt mắc 08-16: trần chi tiêu tháng sập GIỮA lúc 3 workflow ~30 agent
   đang chạy — P2 một lượt 2,21M token ≈ 74% cửa sổ; vòng đối kháng chết nửa chừng; may user vừa yêu cầu chốt
   memory vài phút trước nên không mất gì. Cùng họ với bài học 78 findings 08-12 chỉ nằm trong chat → MẤT.)

---

## 🎯 TIẾN ĐỘ — HỎI "LÀM ĐẾN ĐÂU / HÔM NAY LÀM GÌ" LÀ ĐỌC Ở ĐÂY
> Cập nhật lần cuối: **2026-08-17 — ✅ ĐỢT REVIEW TÀI LIỆU TEAM `2026_08_13/` HOÀN TẤT TOÀN BỘ (P0→P9) + P10 mặt phẳng copy-paste**. Bàn giao sẵn sàng: vá 43/43 batch+module ・ dịch JA 24/24 ・ re-review ⛔#5 ĐẠT ・ `review_summary.md` chốt đủ 7 mục ・ **`new/batch_decision.md` có ở CẢ 7 nhóm có xlsx** (commit `b59f1b1`) ・ 4 câu QA ở `submit_folder/qa/qa_review_20260813_20260817.md` **chờ user gửi PM mui** ・ SKILL + 4 file "app snapshot" đã sửa. **VIỆC CÒN LẠI = user gửi QA + member cập nhật 13 sheet xlsx + thay 2 file md của G3** (mục 7-A `review_summary.md`).

**[08-17] ✅ ĐỢT REVIEW `2026_08_13/` — KẾT QUẢ CUỐI:**
- Verdict 43/43: 妥当 6 ・ 妥当だが根拠不足 19 ・ 要修正 14 ・ 要業務確認 4 ・ 189 findings ・ đối kháng mọi [cao]+要修正 = **0 REFUTED**.
- Bản sửa nằm ở `new/` từng thư mục nhóm (file gốc + xlsx không đụng): 43/43 batch có bản vá, 24 file dịch JA mới, 3 nhóm có `new/batch_decision.md` (G1 7 sheet ・ G2 3 ・ G4 3), `submit_folder/2026_08_13/new/summary_batch_migration_ja.md` sửa 15 mục.
- 4 câu QA gộp từ 9 mục 要業務確認 (theo nhóm batch, có dẫn chứng file:dòng + khối JP paste được): `submit_folder/qa/qa_review_20260813_20260817.md` — **CHƯA GỬI**.
- Chi phí: fable ~3,3M ・ opus ~2,7M ・ sonnet ~0,9M — ledger + đơn giá hiệu chỉnh ở `notes/usage_budget.md` §2/§4 (dịch JA thật ~120k/file, checker ~144k/agent).
- Phát hiện đã áp vào workspace: **repo app là git thật** `syp-eminelstandard-app@41ee385` (`syp-dev`) — CLAUDE.md/README/SKILL/self_study_plan đã sửa; SKILL `3-step-review` mục 4a = baseline đợt này.
- **[17/08 chiều] Quy ước mới về `new/batch_decision.md` (user chốt sau tranh biện ⛔#11 3 lập trường), commit `b59f1b1`**: **mọi nhóm có xlsx đều có file này** — 修正版 (G1/G2/G4 thay ô; **G3 đặc thù**: ô xlsx chỉ trỏ TÊN FILE nên thêm dòng 「レビュー結果」 ngoài xlsx, hành động của member là **thay 2 file md `current-eminelsmart_DistributeMonthlyEcoPoints{,_ja}.md`, KHÔNG sửa ô**) và レビュー確認版 trùng khít bản gốc (G5/G6/G7 — 0 sheet 要修正, để phân biệt "đã review" với "chưa review"). Mỗi file thêm dòng 【メンバーの作業】 tiếng Nhật + verdict từng sheet + mã QA-0x. **Đính chính bản nộp: có 6 sheet 根拠不足 (không phải 5) có sẵn văn bản JP** — 4 câu thay thế (G1 CalcYearlyRoomTemperature ・ G2 CreateGroupSummary ・ G2 RankingCreation ・ G5 SendAlertLogMail) + 2 câu nối thêm (G1 CalcDailyAverageData ・ CalcWeeklySavingReportEffect); tất cả nay nằm ở mục 付録【提案・未適用】 của file nhóm. Sửa kèm: verdict QA-04 (`DistributeMonthlyEcoPoints` 根拠不足→**要修正**) ・ meta 7 file trỏ `../batch_decision.xlsx` ・ bỏ cặp 「」 thừa ở ô G4 RcvCntctCancellation ・ đồng bộ `review_summary` (P8/§3.G6/7-A1/7-A2) + `review_plan` §4.3,P8 + SKILL 4a.

**[08-16] Diễn biến đợt review (giữ để tra ngược):**
- Đối tượng: 75 file điều tra + 43 sheet phán định (`batch_decision.xlsx`) + summary 47 dòng trong `submit_folder/2026_08_13/`. Plan = `review_plan_20260813.md` (user duyệt 16/08); kết quả tích lũy = `review_summary.md`; mốc bàn giao = commit local `312d6d0`.
- ✅ P0 (commit mốc ・ 5 repo khớp origin ・ convert 7 xlsx→`batch_decision.md` 43/43 sheet 0 lỗi) ・ ✅ P1 G8 app C1–C5 (12 findings, 1 [cao] CONFIRMED 2/2; C5 sạch; bảng nhu cầu dữ liệu app → `app_data_needs_ref.md`) ・ ✅ P6 G6 CSV/ZIP (妥当2・根拠不足1・**要業務確認1**: s_113 平均 liên hộ không có đích trong 別表① — câu hỏi JP chờ gộp).
- ✅ P2/P3/P4/P5 (39 batch) + P7 XONG, gom đủ vào `review_summary.md`: tổng **189 findings**, **43/43 verdict: 妥当6・根拠不足19・要修正14・要業務確認4**; đối kháng đầy đủ mọi [cao]+要修正 = **0 REFUTED** (§3c). P7: summary 08_13 chỉ điền mới, KHÔNG đè dòng SYP; 10 lệch + 15 dòng summary cần sửa (§3b).
- ✅ P8 vá xong **NHÓM G1** (18/18 batch → 36 file `new/` + `new/batch_decision.md` G1/G2/G4) — **commit local `f5a299b`**. Còn (theo thứ tự, chi tiết file ⭐ mục 5 items 1e+1f+4b): vá G4+G5 → G3 → G2+G7 → G8 → dịch JA 24 file → sửa summary (15 dòng P7-B + lỗi HTML/link) → re-review `new/` → gộp 9 câu 要業務確認 trình user → commit cuối + SKILL mục 4 + 4 file "app snapshot" + chốt memory. Fixspec + tư liệu: `C:\Users\a\.claude\projects\d--SYP-Home-mui-eminelGW\handoff_20260816\`.
- Quy ước user chốt: file gốc member không đụng ・ bản sửa/dịch vào `new/` từng folder ・ xlsx không sửa ・ JA ngắn gọn y phong cách member, chỉ review TÍNH CHÍNH XÁC ・ truy luồng data đến tận bảng (đã vào SKILL `3-step-review` #7 + Vòng 1).
- Phát hiện phiên: repo app là **git thật** `syp-eminelstandard-app@41ee385` (syp-dev) — CLAUDE.md/README/SKILL/self_study_plan ghi "snapshot" là LỖI THỜI, P8 sửa ・ spec [I]:200 nội bộ là **5 loại** không phải 4 bảng ・ header C0x còn レビュー中 nhưng README ghi レビュー済, `tasks/app_requirements_plan.md` không tồn tại trong repo.

**[08-13] Trạng thái mới nhất:**
- **`eminel_gw_project` = `1100487`** (working tree đã pull thật, kiểm bằng `git log -1`). So với mốc guide v1.2 (`460c671`): **thư mục `docs/eminel/4_spec/app/` MỚI xuất hiện** — 機能仕様 app bắt đầu được viết (`README` 195 dòng ・ `c02_グラフ` ・ `c03_レポート` ・ `Z_コントロールタブ構成検討`) + 11 file requirement app bị sửa (A01–A04, B01, B04, **B06**, **E01 −140 dòng**, E04, README). → **guide v1.2 đã lệch mốc, phải rà §7.3 + các mục trích A0x/B0x/E0x.** 3 repo còn lại không đổi.
- **`new_2/` ĐÃ VÁ XONG** (6 file, +71/−49) — user upload lại. Vá theo KHỐI: 4 [cao] + nhóm [vừa] (xem file ⭐ mục 2.2), mỗi finding kiểm lại trên code trước khi sửa. Kiểm chứng sau vá: 0 tàn dư ・ fence chẵn ・ heading JA↔VN khớp 3/3 cặp ・ cặp Xzilla trùng khít 324 dòng.
  ⚠️ **Danh sách chi tiết 78 findings của 08-12 đã MẤT** (không lưu ra đĩa) — chỉ vá được phần có ghi nhận trong memory; phần [thấp] còn lại chưa dựng lại được.
- **1 finding của review agent đã bị BÁC BỎ** khi kiểm lại: "shell flock không có căn cứ" là SAI (flock nằm trong `.sh` bên trong file `.tgz`) → thành ⛔#13.
- **3 tập báo cáo batch ĐÃ NỘP cả 3** (hạn 14/08). Bản chuẩn duy nhất = `submit_folder/2026_08_06/new_2/`. (Thư mục `new/`: user đã xoá 08-13 — xem như chưa từng tồn tại.)
- **Bảng tổng hợp 47 batch** `submit_folder/2026_08_12/summary_batch_migration_ja.md`: **6/47 dòng có kết luận** — 4 dòng CSV/ZIP của SYP (đã có link Notion) + 2 dòng 集計 của thành viên khác. **7 dòng 配信・通知系 + Xzilla đã điều tra xong từ 08-06 nhưng CHƯA điền.**
- **Mọi file QA nay ở `submit_folder/qa/`** (⛔#12) — `qa_kitagas.md` ・ `qa_batch_csvzip.md`.
- **[08-12] Guide → v1.2** (đối chiếu `460c671`): viết lại §5.5 (設定値運転 bị gỡ → 室温制御の有無 + 温度レベル), §5.6, §7.3 (bảng 23 section + mục B6), Phụ lục B.3/B.4, §0.3. Review 6 agent = 142 findings, phần guide vá hết.
- **[08-12] Bộ 4 batch `CSV/ZIPエクスポート系` theo FORMAT MỚI** → `submit_folder/2026_08_12/` (8 file JP+VN). Format user chỉ đạo, khác TEMPLATE v4: **1 batch = 1 file, chỉ điều tra hệ CŨ**; phán định để ở bảng tổng hợp. Mẫu: `legacy-batch_CalcTenMinutesSensor_ja.md` của thành viên khác.
- **3 phát hiện lật giả định (08-12, đã áp vào `new_2/` ngày 08-13)**: ① hệ cũ CÓ chiều gửi SFTP Xzilla (`PutLogFileCommand`, cron 00:00) ② spec [I] còn giữ 4 bảng của batch #5–#7 làm loại download nội bộ ③ **e-smart CÓ 3 bảng tích luỹ `DeviceAccumulated/DailyUsage/MonthlyUsageHistoryTable`** → "集計・計算系 không có gì dùng lại" đã bị bác.
- **Bài học vá tài liệu**: vá theo FILE làm vỡ nhất quán → **vá theo KHỐI** (1 bản chuẩn/khối → áp đồng loạt → `grep -c`/`diff` chứng minh). Chi tiết `05_session…` mục 8.3.
- Bộ skill: `create-investigation-report` (TEMPLATE v4) ・ `analyze-change-request` (⛔#11) ・ `3-step-review` ・ `notion-connect` ・ `slack-connect` ・ `update-memory`.
- `requirements/self_study_plan.md`: 4 hạng mục — **hạng mục 1 mới xong bước 1** (§8-3 F-ES của v1.2).

**Đã xong (tích lũy):** bộ tài liệu học v1.1 (10 chương + 7 phụ lục, đối chiếu `788b438`, đã qua review nhiều vòng)
・ `qa_kitagas.md` (8+4 câu; **câu 1 đã đăng QAデータベース Notion, có trả lời tạm của mui: badge ngoài scope 2026, 回答中**)
・ **5 QA Notion đầu tiên (08-03→04) đã đọc & cập nhật vào guide/qa_kitagas + review §8 xong** — nội dung 5 QA: bảng ở guide 9.4
・ **báo cáo phán định 11 batch legacy (3 nhóm) vs e-smart/E-GW**: `submit_folder/2026_08_04/report_batch_3nhom_doichieu_esmart_egw.md`
— tối 04/08 nâng cấp: user clone `syp-eminelstandard-backend` (@dc39aa39) + `-web-admin` (@e550326), đều branch
`gw-syp-dev` (chưa có commit E-GW nào); điều tra code trực tiếp → báo cáo **viết lại hoàn chỉnh** (quy tắc ⛔#9),
mọi kết luận e-smart đã kiểm trên code; phát hiện **5 điểm tài liệu khảo sát `docs/eminel-smart/` lệch code**
(xem mục Giới hạn của báo cáo). Chuẩn cuối của báo cáo (user đặt): tóm tắt từng batch theo 3 nhóm ở đầu ・
chỗ "e-smart đã có" dán **trích code thật + giải thích từng nhóm** (16 khối, review xác nhận 16/16) ・
chỗ "tạo mới/bỏ" có **"Cách làm từng bước"** ・ đã qua nhiều lượt review 3 vòng, findings vá hết
・ **skill mới `skillAI/3-step-review/`** (quy trình review 3 vòng + thủ tục máy mới; đã tự review 2 agent
và viết lại; CLAUDE.md mục SOURCES đã cập nhật 4 repo git + 1 snapshot)
・ 3 skill cũ + workspace AGENTS folder (phiên 1)
・ **[08-05] Bản tiếng Nhật báo cáo batch cho mui**: `submit_folder/2026_08_05/旧EMINELバッチ移行判定報告書_3グループ11本.md` — bố cục 結論先出し, bỏ khối code (thay 🔍 ref), 対応ステップ đánh số khớp bản VN để đọc song song; review 2 lượt `3-step-review` (8+3 agent), vá 46 findings; **phát hiện 6 điểm nội dung bản VN còn dính** (ゆ抜く→ゆーぬっく, Node 20→24, 4/19 cron thông năm, DR schedule lúc 配信完了, #6 chỉ 7 loại 契約種別, emn_confirm append-only — chi tiết session 03 mục 3); 付録A = 6 điểm lệch tài liệu khảo sát.

**Việc tiếp theo (theo thứ tự):**
-1. ✅ **XONG 17/08: đợt review team `2026_08_13/`** (P0→P9 + bổ sung mặt phẳng copy-paste — xem khối [08-17] trên). Việc còn lại **không thuộc AI**: ① user gửi 4 câu QA (`submit_folder/qa/qa_review_20260813_20260817.md`) qua PM mui; ② member cập nhật **13 sheet** `batch_decision.xlsx` theo `new/batch_decision.md` (G1 7 ・ G2 3 ・ G4 3) **và thay 2 file md của G3** (`current-eminelsmart_DistributeMonthlyEcoPoints{,_ja}.md` — nhóm này KHÔNG đụng xlsx), tùy chọn thêm **6 câu 付録【提案・未適用】** cho sheet 根拠不足; ③ member điền URL Notion còn thiếu ở summary dòng 63/66.
0. ✅ Xong 08-13: vá `new_2/` (user upload lại) ・ pull `1100487` ・ ⛔#12 QA folder ・ 4 link Notion vào bảng tổng hợp.
1. **Rà `onboarding_guide.md` v1.2 theo `1100487`** — §7.3 bảng 23 section (E01/B06/A0x vừa đổi) + **đọc `docs/eminel/4_spec/app/` MỚI** (chính là nguồn cho hạng mục 4 của kế hoạch tự học).
2. **Điền 7 dòng 配信・通知系 (#1–#4) + Xzilla (#5–#7) vào `summary_batch_migration_ja.md`** — kết luận đã có sẵn trong `new_2/`; cần quyết: có tách thành file `legacy-batch_<Command>_{ja,vi}.md` theo format mới không.
3. **Điều tra nhóm 集計・計算系** (17/19 dòng còn lại của nhóm; SYP còn ~30/43 batch chưa điều tra). ⚠️ Giả định cũ "e-smart không có gì dùng lại" **đã bị bác** — e-smart CÓ 3 bảng history (`template-dynamodb.yaml:1113/1145/1177`), ghi bởi 5 batch `batch-import-rinnai/noritz-*`. Dùng skill `create-investigation-report`.
4. **`requirements/self_study_plan.md`** — hạng mục 1 tiếp bước 2–6; **sửa dòng 54** ("集計・計算系 — e-smart không có gì dùng lại") theo phát hiện trên (CHƯA làm).
5. Findings [thấp]/[vừa] còn lại của 78 (đã mất danh sách) — user quyết có chạy lại một lượt review để dựng lại không.
6. **Trả lời vế ただし của QA 独立デプロイ trên Notion** — danh sách "chức năng nên dùng tiếp": hệ cũ = không có;
   ESTA = push/point-PI/Xzilla-import/data-export (xem báo cáo batch §1; xác nhận trước nghĩa 「既存システム」).
7. Chốt nội bộ với **kihara** về Q5 (GW giữ trạng thái DR — báo cáo batch #4 cũng treo vào đây) → gửi `qa_kitagas.md`
   qua PM mui (quyết kèm Dự phòng 3/4 không).
8. **Theo dõi 5 trang QA đang 回答中** → khi 回答済: cập nhật các chỗ đánh dấu trong guide (grep "回答中") + B.1 theo README §9.
9. Hỏi mui xác nhận **đích của luồng export SFTP `/EST`** trong backend e-smart (≒「EMINELデータの共有」 F-ES-10?) — xem báo cáo batch §6.
10. Khi **IF-01/CLD-07** (định nghĩa 入出力 Xzilla) có spec → rà lại nhóm Xzilla của báo cáo batch (§4, gồm cả
   chiều xuất); khi review **spec [I]** → nêu 保持期間/loại dữ liệu download (**chưa có trong bảng QA — cân nhắc
   thêm câu hỏi**); danh sách việc-cần-xác-nhận đầy đủ: bảng §6 của báo cáo batch (8 mục).
11. **B06 マイホーム発電**: phần cập nhật guide §7.3 ✅ đã làm ở v1.2 (đã có mục B6). Còn lại: rà các mục guide trích **B04/B05/C01–C03** theo `1100487` (B04/B06 vừa bị sửa tiếp ngày 12/08); cân nhắc bổ sung guide 0.7 (`legacy_eminel_docs` đã có local).
12. Bối cảnh: hạn **tháng 9/2026 fix design+spec** vẫn treo trên 23/23 section chưa chốt + 10/10 spec admin DRAFT;
   3 vấn đề chặn SYP = CLD-01 / CLD-02 / GW-01.

---

> Folder ký ức để agent KHÔNG quên giữa các phiên. Đọc theo thứ tự khi bắt đầu lại.
> Cập nhật bằng skill `skillAI/update-memory/` cuối mỗi ngày làm việc.

| File (trong `memory/`) | Nội dung |
|---|---|
| `00_INDEX.md` | File này — QUY TẮC + tiến độ + địa chỉ (ĐỌC ĐẦU TIÊN) |
| `01_session_20260803_04_soanTaiLieu_review_fix_reorg.md` | [2026-08-03→04 sáng] Soạn guide v1.0 → review 13 agent → phát hiện repo local cũ & pull `788b438` → sửa toàn diện v1.1 → qa 8+4 câu → skill notion/slack → tái tổ chức AGENTS folder |
| `02_session_20260804_qaNotion_capNhatTaiLieu_baoCaoBatch.md` | [2026-08-04 chiều→tối] 5 QA Notion đầu → cập nhật guide/qa_kitagas + review §8 (21 findings) → báo cáo phán định 11 batch (điều tra cả code backend/web-admin e-smart, viết lại nhiều lượt theo chuẩn: trích code + cách làm từng bước + tóm tắt 3 nhóm) → skill `3-step-review` → quy tắc ⛔#8, ⛔#9 |
| `03_session_20260805_soanBaoCaoBatchJP_review2luot.md` | [2026-08-05 sáng→trưa] Soạn bản tiếng Nhật báo cáo batch cho mui (`submit_folder/2026_08_05/`) → review 2 lượt 3-step-review (8+3 agent, 46 findings vá hết) → 6 điểm nội dung bản VN còn dính + F-ES-10=Xzilla連携 + B06 đã được viết ở `788b438` |
| `04_session_20260806_tach3tap_templateV4_boSkillMoi.md` | [2026-08-06] Pull `fbc0af0` + phân tích 6 commit (app 13 file) → tách báo cáo thành **3 tập × JP+VN**, 3 thế hệ (`2026_08_06/` → `new/` v4 → **`new_2/` bản dùng**) → review độc lập bắt 2 lỗi [cao] (前々月, path bịa) → **bộ skill mới** `create-investigation-report` (TEMPLATE v4) + `analyze-change-request` (⛔#11) + sửa `3-step-review` → `requirements/self_study_plan.md` |
| `05_session_20260812_guideV12_review6agent.md` | [2026-08-12] Pull `460c671` → **guide v1.2** (viết lại §5.5 mô hình sưởi mới, §5.6, §7.3 + mục B6, Phụ lục B.3/B.4) → **review 6 agent** (3 vòng guide + 3 cặp `new_2/`) = 142 findings, guide vá hết / `new_2/` chờ quyết → **3 phát hiện lật giả định**: hệ cũ có chiều gửi SFTP Xzilla ・ spec [I] giữ 4 bảng batch #5–#7 ・ e-smart CÓ bảng tích luỹ `TABLE_DEVICE_*_HISTORY` |
| `06_session_20260813_pullSpecApp_vaNew2_ruleQA.md` | [2026-08-13] Pull **`1100487`** — `4_spec/app/` (機能仕様 app) xuất hiện + 11 file requirement app đổi → **guide v1.2 lệch mốc** ・ **vá `new_2/` để nộp lại** (6 file, 4 [cao] + nhóm [vừa]; danh sách 78 findings gốc đã mất) ・ **bác bỏ 1 finding sai** (flock nằm trong `.tgz`) → ⛔#13 ・ phát hiện working tree cũ 10 ngày → ⛔#14 ・ **⛔#12 mọi file QA về `submit_folder/qa/`** ・ điền 4 link Notion vào bảng tổng hợp (6/47 dòng) |
| ⭐ `07_session_20260816_reviewTaiLieuTeam_p0p1p6.md` | [2026-08-16→17] **Đợt review tài liệu team `2026_08_13/` — HOÀN TẤT P0→P9** (bàn giao sẵn sàng; QA chờ user gửi). Chi tiết gốc: (75 file + 43 sheet phán định): plan duyệt → **P0–P7 XONG** (mốc `312d6d0`; 189 findings; 43/43 verdict 妥当6・根拠不足19・要修正14・要業務確認4; đối kháng 0 REFUTED; P7: 10 lệch + 15 dòng summary cần sửa) → **P8 vá xong G1** 18/18 batch → `new/` + commit **`f5a299b`** ・ hàng đợi còn lại + handoff `handoff_20260816/` + 9 câu 要業務確認: mục 5 items 1e/1f/4b ・ SKILL +#7 & truy-bảng ・ cơ chế ước lượng token `notes/usage_budget.md` (⛔#15) ・ app repo = git thật `41ee385` ・ spec [I]:200 = 5 loại |
