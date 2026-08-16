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
