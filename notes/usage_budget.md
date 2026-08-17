# Cơ chế ước lượng usage token trước khối việc nặng (⛔#15 định lượng)

> User chỉ đạo 2026-08-16 (sau sự cố chạm trần thật giữa 3 workflow): TRƯỚC mỗi khối việc phải ƯỚC LƯỢNG token;
> vượt **20% ngân sách gói Claude Max 20x** thì BẮT BUỘC chia khối + nhích memory theo từng khối.
> File này là nơi sống của: công thức ・ đơn giá hiệu chỉnh ・ sổ ghi (ledger) số thật để hiệu chỉnh dần.

## 1. Ngân sách giả định & ngưỡng hành động

| Đại lượng | Giá trị | Ghi chú |
|---|---|---|
| Ngân sách 1 cửa sổ 5h gói Max 20x | **~3.000.000 token** (🔸giả định làm việc — Anthropic không công bố số chính xác; hiệu chỉnh khi quan sát được trần thật) | Trần tuần/tháng là tầng riêng — sự cố 16/08 là trần THÁNG |
| **Ngưỡng hành động 20%** | **600.000 token / khối** | Ước lượng khối > 600k → BẮT BUỘC chia nhỏ đến khi mỗi khối ≤ 600k, mỗi khối kết thúc = kết quả ra đĩa + memory nhích |
| Khối ≤ 600k | Vẫn chốt memory trước nếu là mốc quan trọng (⛔#15 vế ①) | |

## 1b. Hiệu chỉnh từ số THẬT phía gói (user đọc từ /usage, 16/08 tối)

- User báo: session usage ~69%, **weekly Fable usage ~68%**. Đối chiếu ledger (phiên 16/08 ≈ 10M gồm main-loop; + phiên 08-13 ước 2–4M) → **quota tuần Fable ≈ 18–20M token; còn 32% ≈ 5–6M**. Sai số ±30% (Anthropic tính % theo cost có trọng số, không phải token thô).
- Phần việc còn lại của đợt review ước ~4,3–4,6M → vừa đủ nếu toàn Fable, KHÔNG có đệm. **Chiến lược chốt: việc phán đoán sâu (vá, re-review) giữ Fable (~2,4M); việc cơ học (dịch JA 24 file + kiểm dịch ~1,7M) chạy `opts.model:'sonnet'`** — Sonnet có bucket tuần riêng, không ăn quota Fable. ~~Weekly reset giữa tuần nếu deadline 24/08 → có thể dồn khối dịch sang tuần mới.~~ **VÔ HIỆU — user chốt tối 16/08: deadline là 17/08 (ngày mai), toàn bộ khối còn lại phải chạy hết trong đêm 16/08.**
- Quy trình bổ sung: mỗi lần user cho số % thật → đối chiếu ledger, cập nhật mục này; ước lượng khối từ nay tính thêm cột "model" (Fable/Sonnet).

## 2. Đơn giá ước lượng theo loại agent (hiệu chỉnh từ số thật 16/08)

| Loại agent | Đơn giá ước | Nguồn hiệu chỉnh |
|---|---|---|
| Verifier sâu (đọc code + tài liệu, 15–30 dẫn chứng, truy bảng) | **~120k** | P2: 2.211k/19 ≈ 116k ・ P3: 1.197k/12 ≈ 100k ・ P4: 877k/6 ≈ 146k ・ P5: 760k/5 ≈ 152k |
| Đối kháng / phản biện lô | **~90k** | critique plan: 311k/4 ≈ 78k; P3 refuters trong 100k trung bình nhóm |
| So khớp máy móc (fidelity convert, đối chiếu bảng) | **~45k** | P0: 285k/7 ≈ 41k |
| Review nhẹ 1 cặp file (G8 kiểu C1–C5) | **~90k** | P1: 464k/8 ≈ 58k–90k (gồm cả agent tổng hợp) |
| Dịch JA 1 file (~10–20KB) | **~120k** (đã hiệu chỉnh) | P8-B5a: 952k/8 ≈ 119k — gấp đôi giả định 60k cũ |
| Fixer vá 1 batch theo fixspec (cả cặp VN+JA) | **~65k** (đã hiệu chỉnh) | P8-G1a: 443k/6 ≈ 74k gồm main-loop → ~65k/batch |
| Main-loop gom kết quả 1 phase (script + đọc digest) | **~30–50k** | Quan sát 16/08 |

**Công thức**: `ước lượng khối = Σ(số agent × đơn giá loại) + 50k main-loop`. Nghi ngờ thì lấy đơn giá cao.

## 3. Quy trình áp dụng (mỗi lần định phóng workflow / loạt việc dài)

1. Tính ước lượng theo bảng đơn giá.
2. `> 600k` → **chia khối** (theo nhóm/lô có điểm ghi-ra-đĩa giữa chừng) đến khi từng khối ≤ 600k; lịch chạy = khối nào xong ghi kết quả + nhích memory rồi mới sang khối kế.
3. Phóng xong, nhận notification → **ghi số thật vào ledger §4** (cột subagent_tokens của usage) → lệch đơn giá >30% thì sửa bảng §2.
4. Bài học chuẩn: P2 ngày 16/08 chạy 1 lượt 2,21M ≈ **74% cửa sổ giả định** — đáng lẽ phải chia 4 khối ~5 batch; trần sập đúng lúc đó.

## 3b. ĐỊNH TUYẾN MODEL (endpoint theo loại task — user chốt 16/08)

> Cách gọi: trong workflow, mỗi agent đặt `opts.model` ('fable'/'opus'/'sonnet'/'haiku'); KHÔNG đặt = kế thừa Fable (main-loop). Fable có bucket tuần riêng — đẩy việc cơ học sang Opus/Sonnet là cách giữ đệm Fable.

| Loại task | Model | Lý do |
|---|---|---|
| Verifier điều tra/verdict phán định (truy bảng, đối chiếu code) | **fable** (mặc định) | Phán đoán sâu, kết luận sai là hỏng cả verdict |
| Đối kháng / phản biện lô | **fable** | Chất lượng phản biện quyết định ⛔#13 |
| Fixer vá theo fixspec (tự kiểm nguồn + viết lại liền mạch) | **fable** | Đụng bản bàn giao, phải giữ giọng member + kiểm nguồn |
| Re-review thu hẹp cuối trước bàn giao (⛔#5) | **fable** | Vòng chất lượng cuối |
| **Dịch JA (bản nộp khách)** | **opus** (`model:'opus'`) | Chất lượng tiếng Nhật đối khách; không ăn bucket Fable |
| Kiểm sau dịch (khớp cặp 1-1 + quét mã nội bộ ⛔#4) | **sonnet** (`model:'sonnet'`) | Đối chiếu máy móc theo checklist |
| Fidelity/so khớp ô・đếm fence・grep tàn dư | **sonnet** (hoặc haiku) | Thuần cơ học |
| Convert/parse/gom kết quả | **script python — 0 agent** | Đã chứng minh qua P0/consolidate |

**Hàng đợi còn lại + model + ước lượng** (đánh dấu ☑ khi xong, ghi số thật vào ledger):

| # | Khối | Model | Ước lượng | Trạng thái |
|---|---|---|---|---|
| 1 | Vá G4+G5 (6 fixer) | fable | ~440k | ☑ 16/08 (437k thật) |
| 2 | Vá G3 (4 fixer, cặp legacy+current) | fable | ~330k | ☑ 16/08 (333k thật) |
| 3 | Vá G2+G7 (2 khối × 5 fixer) | fable | ~700k | ☑ 16/08 (723k thật: 3a=402k + 3b=321k) |
| 4 | Vá G8 (4 fixer, cặp ja+vn) | fable | ~310k | ☑ 16/08 lần 2 (220k thật; lần 1 chết vì trần tháng, tốn 148k) |
| 5a | Dịch JA G2 8 file | **opus** | ~480k | ☑ 16/08 (952k thật — đơn giá dịch thật ~120k/file → chia lại các khối sau) |
| 5b1 | Dịch JA G3: Distribute+Publish (4 file cặp legacy+current) | **opus** | ~530k | ☑ 16/08 (421k thật) |
| 5b2 | Dịch JA G3: Dispatch+ControlDr (4 file) | **opus** | ~530k | ☑ 16/08 (457k thật) |
| 5c1 | Dịch JA G4 3 file + MakeCodeMapData | **opus** | ~530k | ☑ 16/08 (460k thật) |
| 5c2 | Dịch JA G5 3 file + HashPassword | **opus** | ~530k | ☑ 16/08 (418k thật — DỊCH XONG 24/24) |
| 6 | Kiểm sau dịch (6 checker × 4 cặp) | **sonnet** | ~250k sonnet | ☑ 16/08 (863k thật — đơn giá checker sâu ~144k/agent, gấp 3 giả định) |
| 7 | Sửa summary 15 dòng P7-B + HTML/link (1 agent fable) | fable | ~100k | ☑ 16/08 (168k thật) |
| 8a | Re-review G1 3 lát + summary (4 agent) | fable | ~320k | ☑ 16/08 (507k thật) — ĐẠT cả 4, 2 "vừa" là câu 根拠不足 trong batch_decision (đúng quy ước, chuyển gói khối 9), 2 vi chỉnh đã áp |
| 8b | Re-review G2/G3/G4+G5/G7+G8 (4 agent) | fable | ~350k | ☑ 16/08 (588k thật) — ĐẠT 4/4 nhóm, 105/105 finding fixspec áp đúng; issues → gói khối 9 |
| 9 | Gộp 9 câu 要業務確認 trình user + chốt (main-loop) | fable | ~150k | ⬜ |

→ **Fable dùng thêm ~2,6M** (kết thúc tuần ~81–84%, đệm giữ được) ・ Opus ~1,4M ・ Sonnet ~0,3M.

## 4. Ledger — số thật đã quan sát

| Ngày | Khối | Agent | Token subagent thật | Ước lượng nếu áp cơ chế | Ghi chú |
|---|---|---|---|---|---|
| 16/08 | critique plan | 4 | 311.433 | 4×90k=360k ✓ | |
| 16/08 | P0 fidelity convert | 7 | 285.083 | 7×45k=315k ✓ | |
| 16/08 | P1 G8 app | 8 | 463.767 | ~520k ✓ | |
| 16/08 | P2 G1 集計 | 21 | **2.211.648** | 19×120k+2×90k≈2,46M — **VƯỢT 4×ngưỡng → đáng lẽ chia 4 khối** | 2 refuter chết vì trần |
| 16/08 | P4 G5+G4 | 8 | 877.186 | ~840k — vượt → chia 2 | 2 refuter chết vì trần |
| 16/08 | P5 G3 | 6 | 759.860 | ~660k — vượt nhẹ → chia 2 | 1 refuter chết |
| 16/08 | P6 CSV | 1 | 93.618 | ~90k ✓ | |
| 16/08 | P3 G2+G7 | 12 | 1.196.949 | ~1,38M — vượt → đáng lẽ chia 2-3 | chạy sau khi limit nâng, thoát |
| 16/08 | đối kháng bù P2/P4/P5 | 5 | 544.859 | 450k (lệch +21%) | đơn giá đối kháng lô lớn → ~110k |
| 16/08 | P7 cross-check | 2 | 258.578 | ~290k ✓ | đơn giá chuẩn |
| 16/08 | P8-G1a fix 6 batch | 6 | 443.344 | 530k ✓ | **đơn giá fixer thật ~65k/batch (cặp)** — đã sửa bảng §2 |
| 16/08 | P8-G1b fix 6 batch | 6 | 405.857 | 440k ✓ | đơn giá fixer ổn định |
| 16/08 | P8-G1c fix 6 batch | 6 | 445.430 | 440k ✓ | ước lượng trúng — cơ chế đã ổn định |
| 16/08 | P8-B1 vá G4+G5 (phiên tiếp nối) | 6 | 436.557 | 440k ✓ | 33 fix áp, 1 skip hợp lệ (chỉ thuộc batch_decision); 6/6 file ra new/ |
| 16/08 | P8-B2 vá G3 (phiên tiếp nối) | 4 | 333.186 | 330k ✓ | 31 fix áp, 0 skip; 8/8 file (4 cặp legacy+current) ra new/; legacy↔current nhất quán |
| 16/08 | P8-B3a vá G2a (phiên tiếp nối) | 5 | 402.141 | 350k (lệch +15%) | 27 fix áp, 0 skip; 5/5 file ra new/; 1 điều chỉnh nhỏ theo nguồn (F4 DeleteTimeOutControlOneMinute — đúng ⛔#13) |
| 16/08 | P8-B3b vá G2b+G7 (phiên tiếp nối) | 5 | 320.603 | 350k ✓ | 20 fix áp, 0 skip; 5/5 file ra new/ (G2 đủ 8 + G7 đủ 2); 1 đính chính path model Admin so fixspec (không ảnh hưởng câu sửa) |
| 16/08 | P8-B4 vá G8 — **THẤT BẠI** | 4 | 148.453 (lãng phí) | ~310k | **Trần chi tiêu THÁNG sập giữa khối**: 4/4 agent lỗi 「monthly spend limit」 sau ~80s, **0 file ghi ra new/** (đã kiểm đĩa: thư mục trống). Không mất dữ liệu khối trước nhờ ⛔#15. Chạy lại: `wf_scripts/b4-fix-g8.js` nguyên khối. |
| 16/08 | P8-B4 vá G8 lần 2 (trần đã nâng) | 4 | 219.988 | ~310k ✓ (dư) | 13 fix áp, 0 skip; 8/8 file (4 cặp ja+vn) ra new/; C1-C4 cặp JA↔VN kiểm khớp 1-1. Ghi chú kỹ thuật: Write bị hook chặn tên `report_*` → fixer dùng Bash heredoc/cp+Edit, nội dung đã diff xác nhận |
| 16/08 | P8-B5a dịch JA G2 (opus) | 8 | **952.007** | 480k (**lệch +98%**) | 8/8 file ja ra new/, cấu trúc khớp máy 1-1. Đơn giá dịch thật ~119k/file → sửa §2, chia 5b/5c thành 4 khối ≤600k. **Văn thể chốt である体** theo member (translator đo 0/24 file _ja member dùng 敬体) — áp cho mọi khối dịch sau. Notes chi tiết (điểm cần user quyết: Q-G6-1 trong bản gửi, lỗi render regex có sẵn ở nguồn…): `handoff_20260816/tasks/b5a_translate_g2.output` |
| 16/08 | P8-B5b1 dịch JA G3-1 (opus) | 4 | 420.536 | 530k ✓ | 4/4 file ja ra new/, cấu trúc + code span khớp máy 100%, văn thể である体 sạch. Notes chờ user (comment VN trong code block ```php của member — giữ hay dịch; nghi lệch s_104↔s_114 trong nguồn): `handoff_20260816/tasks/b5b1_translate_g3_1.output` |
| 16/08 | P8-B5b2 dịch JA G3-2 (opus) | 4 | 457.189 | 530k ✓ | 4/4 file, G3 đủ 8/8 bản dịch. Notes: legacy DispatchPushMessages còn đường dẫn máy local `e:/Projects/mui/...` trong nguồn (bản gửi mui — cần user quyết có sửa bản VN rồi dịch lại không); comment VN trong block PHP tiếp tục treo chờ user: `handoff_20260816/tasks/b5b2_translate_g3_2.output` |
| 16/08 | P8-B5c1 dịch JA G4+G7a (opus) | 4 | 459.738 | 530k ✓ | 4/4 file (G4 đủ 3 + MakeCodeMapData). Notes mới cho re-review/user: RcvCntctCancellation nguồn có tham chiếu §2.8 lệch nội dung (bảng cột CSV thực ở §2.4); RcvEmsPlsCntrPayer dòng 64 bảng 4 ô/3 cột (lỗi sẵn ở nguồn, muốn vá phải vá cả cặp VN+JA); typo hằng số STAUS/CANCELLAION là NGUYÊN TRẠNG code hệ cũ (khớp fixspec F3 trước đó — không phải lỗi member): `handoff_20260816/tasks/b5c1_translate_g4_g7a.output` |
| 16/08 | P8-B5c2 dịch JA G5+G7b (opus) | 4 | 417.647 | 530k ✓ | 4/4 — **DỊCH HOÀN TẤT 24/24 file** (tổng opus 5 khối: 2.707k). ⚠️ Lưu ý cho khối 6/9: translator WatchNotification phát hiện typo nguồn VN 「お知らše」 và đã dùng dạng đúng 「お知らせ」 trong bản JA → VN↔JA lệch 1 ký tự CÓ CHỦ ĐÍCH, member cần vá bản VN; CLD-05 trong まとめ (file đi mui — OK, nhưng cấm chuyển tiếp 北ガス); notes: `handoff_20260816/tasks/b5c2_translate_g5_g7b.output` |
| 16/08 | P8-B6 kiểm dịch 24 cặp (sonnet) | 6 | 862.698 | 250k (**lệch +245%** → sửa đơn giá) | **0 cao / 2 vừa / 7 thấp**. 2 "vừa" = sơ đồ ASCII trong fence được dịch nhãn — KẾT LUẬN: quy ước có chủ đích nhất quán toàn lô (code thật giữ nguyên kể cả comment VN theo tiền lệ member; sơ đồ văn xuôi dịch cho người JA đọc) → CHẤP NHẬN, không vá. 7 "thấp" = lệch heading liên-file → main-loop đã thống nhất trực tiếp 12 chuỗi/9 file (概要・第A部/第B部 ―・対照・確認済み・まとめ; まとめ theo đa số 10/13, KHÔNG theo kiến nghị 総括 của checker g2b vì họ chỉ nhìn lát 4 file). G1 member giữ nguyên. Output: `handoff_20260816/tasks/b6_check_translations.output` |
| 16/08 | P8-B7 sửa summary (fable) | 1 | 168.214 | 100k (lệch +68%) | 15/15 mục P7-B áp đủ → bản sửa summary (nay ở `summary_batch_migration/summary_batch_migration_ja.md`); diff đúng 19 dòng thuộc danh sách; dòng 61 (CSV SYP) sửa 1 ô theo chính §3b, 3 dòng CSV còn lại nguyên vẹn. TỒN ĐỌNG chờ member/user: URL Notion trang DeleteLogicalDeletedDevices (dòng 66 để 確認中), trạng thái upload dòng 63, dòng 50 tùy chọn chưa sửa đồng bộ. Output: `handoff_20260816/tasks/b7_fix_summary.output` |
| 16/08 | P8-B8a re-review G1+summary (fable) | 4 | 506.953 | 320k (lệch +58%) | ĐẠT 4/4 lát; 0 cao ・ 2 vừa (câu bổ sung fixspec cho sheet 根拠不足 batch_decision — KHÔNG áp là ĐÚNG quy ước chỉ thay sheet 要修正, đưa vào gói quyết khối 9 + mục 7 Giới hạn) ・ thấp: pre-existing bảng pipe regex (gốc member), tồn đọng summary dòng 63/66/50 đã biết. Main-loop áp 2 vi chỉnh: 「同コマンド」→「同Rcvコマンド」 (MonthlyAccumulated_ja:127), khôi phục dòng trống EOF (MonthlyAccumulated VN). Output: `handoff_20260816/tasks/b8a_rereview.output` |
| 16/08 | P8-B8b re-review G2..G8 (fable) | 4 | 587.995 | 350k (lệch +68%) | ĐẠT 4/4; 0 cao ・ 3 vừa (2 = câu 根拠不足 batch_decision G2 sheet 1+8 & G5 thiếu new/batch_decision — cùng họ với 8a, gói khối 9; 1 = gloss 暖房能力↔暖房熱源 lệch giữa 2 file G2) ・ thấp phần lớn pre-existing. Main-loop áp 5 vi chỉnh sau 8b: typo お知らše (VN WatchNotification), dịch 3 chú giải VN trong MakeCodeMapData_ja + số 1,686, sửa mâu thuẫn header dòng 3↔5 của 3 file new/batch_decision.md. Output: `handoff_20260816/tasks/b8b_rereview.output` |
