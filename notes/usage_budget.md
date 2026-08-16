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
| Dịch JA 1 file (~10–20KB) | **~60k** 🔸chưa có số thật | Hiệu chỉnh sau lô dịch đầu ở P8 |
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
| 4 | Vá G8 (4 fixer, cặp ja+vn) | fable | ~310k | ⬜ **THỬ 16/08 → CHẾT VÌ TRẦN THÁNG** (4/4 agent lỗi, 148k đã tiêu, 0 file ghi ra `new/` — chạy lại nguyên khối khi trần được nâng) |
| 5 | Dịch JA 24 file (3 khối × 8 translator) | **opus** | ~1,4M opus | ⬜ |
| 6 | Kiểm sau dịch (5-6 checker) | **sonnet** | ~250k sonnet | ⬜ |
| 7 | Sửa summary 15 dòng P7-B + HTML/link (script + 1 agent kiểm) | fable | ~100k | ⬜ |
| 8 | Re-review toàn bộ new/ (7 agent theo nhóm) | fable | ~600k | ⬜ |
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
