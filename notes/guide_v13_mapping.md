# MAPPING sửa `onboarding_guide.md` v1.2 → v1.3

| | |
|---|---|
| Mốc guide hiện tại | `eminel_gw_project` @ `460c671` (2026-08-06) |
| Mốc đích | `1100487` (2026-08-12) — origin/main, không có commit nào mới hơn (fetch 2026-08-18) |
| Hai commit phải phản ánh | `57cd7be` 「要件fix」 (12/08, 10 file requirement, +82/−284) ・ `1100487` 「機能仕様着手」 (mở tầng `4_spec/app/`) |
| Bối cảnh commit `57cd7be` | Phản ánh **kết quả review của 北ガス từ slide đối khách, ngày 2026-08-07** (ghi ở dòng `経緯` của A03/A04/B01/B06) |
| Trạng thái | ✅ Bước 1 (mapping) · ✅ Bước 2 (review mapping — mục F) · ✅ Bước 3 (sửa — guide lên **v1.3**) · ✅ Bước 4 (review vùng sửa — mục G) |

**Quy ước**: 🔴 = đảo kết luận / sai sự thật (bắt buộc sửa) ・ 🟡 = số liệu, số dòng, mốc trôi ・ 🟢 = bổ sung nội dung mới ・ 🔸 = suy đoán, CHƯA kiểm chứng (phải ghi rõ nhãn trong guide).

---

## A. Nhóm 🔴 — guide đang nói ngược với repo

### M1 — §7.3, tiểu mục 「B6 マイホーム発電制御」 (guide dòng 2761–2797) — VIẾT LẠI CẢ TIỂU MỤC

| Guide đang ghi | Sự thật @`1100487` |
|---|---|
| 「PVの発電量が閾値に達したとき、…発電を停止するよう促す案内を受けられる」 (dòng 2769, trích B06 dòng 40) | Câu này **đã bị xoá**. 要件概要 nay: 「PVの発電量に応じて、マイホーム発電…の発電を**自動で制御できる**」 (B06:31) |
| Sơ đồ: App báo → **NGƯỜI DÙNG tự tắt** (dòng 2771–2777) | Requirement app nay = **cài ngưỡng**: ① ngưỡng DỪNG ② ngưỡng CHẠY LẠI ③ xem lại ngưỡng đã cài (B06:41–43) |
| Bảng 3 ranh giới: 「**Gợi ý** dừng khi PV vượt ngưỡng → B6」 (dòng 2787) | 「PV発電量の**閾値設定・閾値によるマイホーム発電の自動制御**はB6」 (B04:110 ・ B06:51–53) |
| Khối 🔴 "chỗ chưa quyết": 「F-GW-07の閾値到達時の挙動は、案内…どまりの想定で良いか」 + đoạn phân tích "nếu là tự động dừng thì phải bổ sung 3 cụm requirement" (dòng 2789–2794) | **Câu hỏi ĐÃ ĐÓNG.** `経緯` B06:8: 「先方確認（2026-08-07）でアプリ側の要件は発電制御の**閾値設定と確定**。手動での制御・Push通知は**対象外**」 |
| 「Kèm hai thứ chưa có *(bảng 「備考と出典」, dòng 47)*」 (dòng 2796) | Bảng 「備考と出典」 của B06 **đã bị xoá sạch**. Ba câu treo nay nằm ở 要確認事項 (B06:74–79): ① エネファーム có phải đối tượng điều khiển không (`GW-04`, hỏi 北ガス; nếu CÓ thì vướng ràng buộc lớp EL + phải kiểm chứng kỹ thuật) ② ngưỡng dùng chung cho コレモ/エネファーム hay tách theo từng máy ③ dải giá trị・giá trị mặc định・đơn vị của ngưỡng (`GW-07`) |
| 「section trẻ nhất… 97 dòng, chỉ dài hơn C4 センサー情報 = 94 dòng」 (dòng 2762) | B06 nay **94 dòng = bằng C4**; file ngắn nhất bộ tài liệu nay là **E01 (80 dòng)** |

**Hành động**: viết lại tiểu mục — đổi sơ đồ ASCII sang luồng tự động, đổi bảng ranh giới, thay khối 🔴 bằng "câu hỏi cũ đã đóng 07/08 + ba câu treo mới", sửa số dòng. Giữ box 📖 giải thích *vì sao phải dừng máy phát khi PV dư* (vẫn đúng). Ghi rõ **mốc đóng: 先方確認 2026-08-07, phản ánh vào repo 2026-08-12**.

### M2 — §6.4 (dòng 2504–2514) + Phụ lục B.1 (dòng 3803–3813): 「A04 trên repo cũng chưa được sửa」

| Guide đang ghi | Sự thật @`1100487` |
|---|---|
| 「A04 trên repo cũng **chưa được sửa**」 (dòng 2514) | **Sai.** A04 đã sửa 12/08: `経緯` A04:8 nay thêm 「／先方レビューの結果をスライドから反映（2026-08-07）」 |
| Trích nguyên văn 経緯 dòng 8 = 「…分離して新設（2026-07-27）」 (dòng 2510) | Nguyên văn nay **dài hơn** — phải trích đủ cả vế 08-07 |
| 「A04…dòng **35–75**」 (dòng 2504 ・ 3805) | Phạm vi nay là **35–71** (「それ以降スコープ」 lùi xuống dòng 73) |
| Nghi ngờ 「**sót khi tách file**」 (dòng 2506 ・ 3807) | Mâu thuẫn **vẫn còn** (A04 vẫn để toàn bộ trong 26年スコープ, それ以降 = 「なし」 A04:73–75) nhưng căn cứ phải đổi: file đã được **rà lại sau review của khách** mà vẫn giữ nguyên phạm vi ⇒ 🔸 giả thuyết "sót khi tách" **yếu đi**, nghiêng sang "slide phạm vi và requirement chưa đồng bộ" |
| — | **MỚI**: 要確認事項 「バッジの内容・要否…確認先＝北ガス」 **đã bị gỡ** (A04:99–107 nay đều 「なし」) — phía viết requirement coi nội dung badge đã chốt, trong khi QA Notion vẫn 回答中 |

**Hành động**: sửa cả hai chỗ cho khớp; giữ kết luận "vẫn phải hỏi" nhưng đổi căn cứ + gắn nhãn 🔸 cho phần suy đoán. Ghi thêm: nội dung A04 đã đổi bản chất — **ランク nay lên theo SỐ BADGE, không phải số điểm** (A04:24, 41), badge gắn với 省エネアドバイス (không còn 省エネ行動).

### M3 — §7.3 dòng 2667: 「Thực tế: 21/23 file đang là レビュー中」

Đếm lại trên đĩa @`1100487`: **23/23 file** đều `状態 = レビュー中` (E01 và E04 vừa lên từ 「ドラフト済（レビュー待ち）」 trong commit `57cd7be`).
⇒ Sửa số + sửa câu dòng 2666 (thang `状態` vẫn có bậc 「ドラフト済（レビュー待ち）」 nhưng **hiện không file nào ở bậc đó**).
**Kéo theo Phụ lục B.4** (đã kiểm bước 2): dòng **3851** liệt kê cùng thang → thêm ghi chú "23/23 nay đều レビュー中"; dòng **3856** ghi 「*(kiểm ngày 2026-08-12, commit `460c671`)*」 → đổi mốc. Hai ví dụ B5/D3 (`状態` レビュー中 ↔ index ステータス レビュー前) **kiểm lại vẫn đúng nguyên** @`1100487`, giữ nguyên.

---

## B. Nhóm 🟡 — mốc, số liệu, phạm vi trích trôi

### M4 — Mốc đối chiếu: **9 vị trí** nhắc `460c671` (⚠️ bước 2 phát hiện — bản mapping đầu chỉ ghi 1 vị trí)
Phiên bản 1.2 → **1.3** ・ ngày cập nhật → **2026-08-18** ・ mốc → **`1100487` (2026-08-12)**. Phải sửa ĐỦ 9 chỗ, thiếu 1 chỗ là tài liệu tự mâu thuẫn (⛔#10):

| Dòng | Ngữ cảnh |
|---|---|
| 10 | Bảng meta đầu guide — hàng 「Đối chiếu với repo」 |
| 13 | Câu ⚠️ "số dòng trong mọi trích dẫn ứng với `460c671`" |
| 201 | §0.3 quy ước trích dẫn — bảng mốc kiểm |
| 396 | §0.7④ tiêu đề "chụp lại thời điểm 2026-08-06" (xem M5) |
| 637 | §1.7 dòng thời gian — hàng 2026-08-06 「mốc repo mà tài liệu này đối chiếu」 |
| 2820 | §7.3 bảng đợt sửa — nhãn "(= commit mà guide đối chiếu)" (xem M6) |
| 3248 | Chương 9 — "Bản cập nhật này đối chiếu repo ngày 2026-08-06" |
| 3856 | Phụ lục B.4 — "(kiểm ngày 2026-08-12, commit `460c671`)" (xem M3) |
| 4230 | Bảng meta cuối tài liệu |

### M5 — §0.7 ④ (dòng 396–402)
Tiêu đề 「Tài liệu này chụp lại thời điểm 2026-08-06 (commit `460c671`)」 → đổi mốc; danh sách "ba đợt sửa nội dung liên tiếp" (08-03 / 08-05 / 08-06) → **thêm đợt thứ tư 08-12 `57cd7be`** (10 file, phản ánh review 北ガス 07/08) + mốc `1100487` (mở `4_spec/app/`).

### M6 — §7.3, bảng 「sang tháng 8, nội dung cũng bị sửa mạnh」 (dòng 2814–2820)
**Câu dẫn dòng 2814** hiện ghi 「**15 file bị đụng trong ba đợt liên tiếp**」 → đếm lại union 4 đợt (8 commit từ `9dc5e34` đến `1100487`) = **20 file** (19 requirement + `README.md`) trong **bốn đợt**.
Thêm **1 hàng**: `2026-08-12 (57cd7be 要件fix)` — 10 file A01–A04・B01・B04・B06・E01・E04・README; phản ánh review 北ガス từ slide 08-07: nhiều mục 検討事項/要確認事項 bị đóng về 「なし」, E01 cắt −124 dòng, B01 đổi danh sách thiết bị, B6 chuyển sang tự động. Nhãn "(= commit mà guide đối chiếu)" hiện gắn ở hàng 2026-08-06 (dòng 2820) → **chuyển xuống hàng mới**.

### M7 — §7.3 dòng 2684 (mục 「判断に迷うポイント」)
「⚠️ KHÔNG phải file nào cũng có: B02 không có, B03/B06/A04 có」 → cấu trúc vẫn đúng (13/23 file có mục này), nhưng **A04 và B06 nay đều ghi 「なし」** ⇒ thêm nửa câu, tránh người đọc mở ra tưởng mất nội dung.

### M8 — §7.1, bảng 「Ý nghĩa cách đánh số」 (dòng 2618–2626)
Hàng `4_spec` — 「Bạn đọc khi nào: **Khi code màn hình quản trị**」 → nay `4_spec/` có **cả app** ⇒ sửa thành "màn hình quản trị **và app**".

### M9 — §0.4 「Đã làm được đến đâu?」 (dòng 253–259)
Thêm 1 hàng: 「Spec (機能仕様) mobile app | 🔵 **Vừa khởi động 2026-08-12** —索引 30 doc, mới có 2 bản nháp (c02 グラフ・c03 レポート)」.
Kiểm lại: trích 「dòng 24–74」 và 「C1–C5 ở dòng 52–56」 của `3_requirements/app/README.md` (guide dòng 265) — **vẫn đúng nguyên si** @`1100487`, không sửa.

---

## C. Nhóm 🟢 — nội dung mới phải bổ sung

### M10 — MỤC MỚI trong Chương 7: 「機能仕様 app — tầng vừa mở」 (chèn sau §7.3, trước §7.4 spec quản trị)

Nguồn: `docs/eminel/4_spec/app/README.md` (195 dòng) + `c02_グラフ.md` + `c03_レポート.md` + `Z_コントロールタブ構成検討.md`; kèm skill mới `.claude/skills/draft-app-spec/SKILL.md`.

Nội dung cần có (đủ để người mới dùng được, theo ⛔#10 tự chứa):
1. **Vị trí**: 要件 (What, `3_requirements/app/`) → **機能仕様 (màn hình hiện gì, bấm thì xảy ra gì)** → デザインラフ. Quan hệ với requirement **không phải 1:1**.
2. **Cách đặt tên & 5 ký hiệu tab**: `a` マイページ ・ `b` コントロール(tên tạm) ・ `c` エネルギー(tên tạm) ・ `d` お知らせ ・ `e` ngoài tab/xuyên suốt; tên file `<tab><số>_<tên>.md`, số `01` = trang chủ của tab. Cách gọi khi trao đổi: 「仕様b02」 ↔ 「要件B02」.
3. **Kế hoạch 30 doc** (hub 4 ・ chức năng 21 ・ ngoài tab 5): a 7 ・ b 11 ・ c 4 ・ d 3 ・ e 5. **Đã viết 2** (c02 グラフ, c03 レポート — 「ドラフト済（レビュー待ち）」), 28 còn 「未着手」.
4. **Hai section requirement KHÔNG có spec**: E2 アプリログ ・ E4 非機能 (không có màn hình).
5. **Thang trạng thái spec (5 bậc)**: 未着手 → ドラフト作成中 → ドラフト済（レビュー待ち）→ レビュー中 → fix済 — **khác** thang `状態` của requirement, đừng lẫn (nối sang Phụ lục B.4).
6. **Kỷ luật viết**: 表示 cấm chép lại requirement ・ mỗi màn hình phải tính trạng thái 0 bản ghi + lỗi ・ 検討事項 (nội bộ) và 確認事項 (hỏi khách) **loại trừ nhau**, chốt xong dồn về `2_management/22_decisions.md` ・ câu 要確認事項 ở requirement mà thuộc mức spec thì **chuyển hẳn** sang `確認事項` của spec.
7. **Quy tắc ưu tiên nguồn**: 要件 là chuẩn; hệ hiện hành chỉ để lấp chi tiết; **要件 vs 現行 xung đột thì 要件 thắng, không lập thành điểm tranh luận**; trong requirement mà mục con chọi mục cha thì lấy **mục con cụ thể hơn**.
8. ⚠️ **Điểm đáng chú ý cho người mới**: nguồn ưu tiên số 2 là **comment trong file pptx đối khách** (`EMINEL-Gateway_要件.pptx`, bản chính ở OneDrive) — tức **có luận điểm không nằm trong repo**; nối thẳng với §0.7① (repo là tài liệu cấp 2).
9. **Nguyên tắc xếp tab**: xếp theo *nội dung là thông tin gì*, không xếp theo "được gửi tới / có chưa đọc-đã đọc"; e04 システムエラー là spec dùng chung, không nhân bản vào từng doc.

### M11 — Phụ lục A (dòng 3706): mục từ 「マルチセンサー」
Thêm ghi chú: **B01 (12/08) đã gỡ マルチセンサー khỏi danh sách thiết bị Wi-SUN HAN đăng ký được**, thay bằng 温湿度センサー / **人感センサー** (mục mới, **định nghĩa để trống trong repo**), đồng thời thêm nhóm 「Web API連携機器 = 給湯器リモコン」. Nhưng 統合要件 v1.2 **vẫn giữ** マルチセンサー (dòng 166 bảng phương thức kết nối, dòng 193 `IF-08 マルチセンサーI/F`, bảng pattern dòng 136/151) và `11_business_process/readme.md` vẫn dùng (dòng 38, 588, 620) ⇒ **mâu thuẫn tài liệu mới**, xem M12.

### M12 — Phụ lục B: thêm mục 「B.5 — マルチセンサー còn hay không」 *(mục mới, cần user duyệt)*
Ba tài liệu lệch nhau: `B01_setup_devices.md` (12/08) không còn đăng ký マルチセンサー ↔ `00_integrated_requirements_v1.2.md` giữ nguyên cả interface lẫn bảng pattern ↔ `11_business_process/readme.md` vẫn mô tả 「マルチセンサーで人感を検知」.
🔸 **Giả thuyết (CHƯA kiểm chứng)**: マルチセンサー bị tách đôi thành 温湿度センサー + 人感センサー theo hướng dùng thiết bị Aqara (W100/FP2/P1) đã bàn ở trại tập trung (`minutes/20260623_egw_camp_day1.md` dòng 92: 「当初マルチセンサー想定 → Aqara（W100・FP2・P1）」). **Phải hỏi 北ガス/mui**, không tự kết luận.

### M13 — §5.4 (dòng 1789), ghi chú về màn hình エラー履歴
Guide đang viết: yêu cầu "không cần xem lỗi quá khứ" **đang được 北ガス tái xét**, slide 28 vẫn còn flow エラー履歴.
Bổ sung diễn biến 12/08: **E01 bị cắt −124 dòng**, bỏ hẳn cụm requirement 一覧・履歴・**未読/既読** và cụm 操作の抑止; nay chỉ còn 1 cụm 「エラー共通」 3 mục (hiển thị lỗi ・ lúc nào cũng xem được lỗi chưa xử lý ・ xem chi tiết: nội dung/thiết bị/nơi liên hệ) ⇒ nghiêng hẳn về phương án **không làm màn hình lịch sử lỗi**. Ghi kèm: spec `e04_システムエラー.md` (chưa viết) sẽ là nơi chốt.

---

## D. Đã xét — KHÔNG cần sửa (ghi lại để bước review khỏi quét lại)

| Chỗ | Vì sao không đụng |
|---|---|
| §7.3 bảng 23 section (dòng 2712–2735) | Cột ステータス/劣後 lấy từ slide đối khách — `57cd7be` **không đụng**; chỉ dòng B6 đổi phần mô tả trong README, không đổi trạng thái |
| §9 dòng 3263 (phân bố 未掲載6/ドラフト作成中1/ドラフト作成4/レビュー前6/レビュー中1) | Đây là thang **ステータス đối khách**, không đổi |
| §0.7 ② (dòng 370–382) — 3 thư mục `input/` `tasks/` `scripts/` không có | Kiểm lại @`1100487`: **vẫn không có**; câu cảnh báo về `tasks/app_requirements_plan.md` vẫn đúng |
| §0.4 dòng 265 (trích README dòng 24–74, C1–C5 dòng 52–56) | Số dòng **không trôi** |
| §5.2 onboarding (dòng 1640–1660) | Nguồn là `11_business_process/readme.md`, không phải B01 — file nguồn không đổi |
| §5.5 / §5.6 (B2 sưởi, B3 lạnh) | `57cd7be` **không đụng** B02/B03 |
| Phụ lục B.4 (dòng 3851) | Mô tả thang đo + ví dụ B5 — vẫn đúng (chỉ liên đới M3) |
| §8.3 (dòng 3086/3089 — `GW-04`, `GW-07`) | Hai mã vấn đề vẫn mở, mức không đổi |
| Nội dung A01/A02/A03 bị dọn (システム情報, 獲得ルート, 付与率 傾斜, 退会導線…) | Guide **chưa từng trích** những chỗ này — grep 0 kết quả ⇒ không sinh lỗi |
| Phụ lục C (12 T.B.D) | Không mục nào lấy nguồn từ 10 file vừa sửa. *(Cân nhắc thêm `GW-04` エネファーム vì nay nó chặn spec b05 — để user quyết, chưa làm)* |

---

## E. Phát hiện Ở NGUỒN (không phải lỗi guide — ghi để hỏi / theo dõi)

| # | Phát hiện | Vị trí |
|---|---|---|
| N1 | **A04 tự mâu thuẫn (2 chỗ)**: ① 要件概要 vẫn ghi 「獲得**ポイント数**に応じてランクが上がる」 trong khi 用語集 + requirement đã đổi sang 「獲得**バッジ数**」 ② câu mở đầu 要件概要 vẫn là 「**省エネ行動**の達成が…」 trong khi gạch đầu dòng + requirement đã đổi sang 「**省エネアドバイス**の達成」 | ① `A04_badge_rank.md`:30 ↔ :24, :41 ② :28 ↔ :32, :58 |
| N2 | **E01 đánh số nhảy cóc**: requirement liệt kê 1 → 3 → 4 (thiếu số 2) | `E01_system_error.md`:37–39 |
| N3 | **`4_spec/app/README.md` ghi 「要件24セクション」 và 「残る22セクション」** trong khi index requirement chỉ có **23** (A1–A4・B1–B6・C1–C5・D1–D4・E1–E4) ⇒ lệch 1 | `4_spec/app/README.md`:97 |
| N4 | **B01 có mục từ 「人感センサー」 với định nghĩa TRỐNG**; 「Web API連携機器」 định nghĩa vòng ("給湯器リモコン" = chính tên nó) | `B01_setup_devices.md`:36–38 |
| N5 | **A04 関連項目 thêm hàng 「省エネアドバイス（C5）」 nhưng ô nội dung để trống** | `A04_badge_rank.md`:82 |
| N6 | B01 bỏ 2 câu 要確認事項 (「GW交換時の再認証をアプリから行うか」, cách nhập liệu khi đăng ký thiết bị) mà **không thấy dấu vết chuyển đi đâu** — `22_decisions.md` chưa có | `B01_setup_devices.md`:157–163 |

⇒ N1–N6 là ứng viên cho đợt QA kế tiếp gửi mui/北ガス (gộp với 4 câu đang chờ ở `submit_folder/qa/qa_review_20260813_20260817.md`). **Chưa hỏi — chờ user quyết.**

---

## F. Bước 2 — Review mapping (đã chạy, kết quả)

**Cách kiểm**: mở lại từng số dòng đã trích — cả phía guide lẫn phía repo `1100487` — đọc đúng dòng đó trên đĩa, so từng chữ. Không dùng lại trí nhớ của bước 1.

**5 lỗi của bản mapping đầu, đã sửa:**

| # | Lỗi | Sửa thành |
|---|---|---|
| R1 | M4 chỉ ghi 1 vị trí phải đổi mốc (bảng đầu guide) | Thực tế **9 vị trí** nhắc `460c671` (dòng 10, 13, 201, 396, 637, 2820, 3248, 3856, 4230) — đã lập bảng đủ |
| R2 | M3 bỏ sót ảnh hưởng sang Phụ lục B.4 | Thêm dòng 3851 (thang `状態`) + dòng 3856 (mốc kiểm) |
| R3 | M6 bỏ sót câu dẫn dòng 2814 「15 file trong ba đợt」 | Đếm union 4 đợt = **20 file / bốn đợt** (`git diff --name-only 9dc5e34^..1100487`) |
| R4 | Trích sai dòng nguồn: A04 định nghĩa ランク ghi 「:21」 | Dòng 21 là header bảng; ランク ở **:24** |
| R5 | Trích sai dòng nguồn: N1 「A04:28」, N2 「E01:29–35」 | Bullet ポイント数 ở **A04:30**; chỗ nhảy số ở **E01:37–39** |

**Đã kiểm và ĐÚNG (không phải sửa)**: B06 :8/:31/:41–43/:51–53/:74–79 ・ A04 :41/:73–75/:82/:99–107 và phạm vi 26年スコープ = 35–71 ・ B01 :36–38/:157–163 ・ B04 :110 ・ A04 :32/:58 (省エネアドバイス) ・ guide §7.1 hàng `4_spec` = dòng 2618 ・ Phụ lục A マルチセンサー = 3706 ・ §0.4 bảng = 253–259 ・ README app dòng 24–74 & 52–56 không trôi ・ `input/`,`tasks/`,`scripts/` vẫn vắng mặt.

**Phạm vi quét đã dùng (để lần sau kiểm lại được, dùng chung cho cả bước 4)**: grep guide theo 5 chùm từ khoá — ① B6/PV/発電/F-GW-07/コレモ/エネファーム ② バッジ/ランク/huy hiệu/xếp hạng ③ マルチセンサー/Wi-SUN HAN/温湿度/人感/ECHONET/初期化 ④ TagTag/システム情報/端末一覧/パスワード/退会/獲得ルート/付与率 ⑤ システムエラー/未読/既読/履歴/非機能/ドラフト済/レビュー中/21-23/4_spec/機能仕様.

---

## G. Bước 3 (sửa) + Bước 4 (review vùng sửa) — kết quả

### G1. Đã sửa gì

Guide lên **v1.3**, mốc đối chiếu **`1100487` (2026-08-12)**. Diff: **+194 / −49 dòng**, 47 khối thay đổi, guide dài 4.232 → 4.437 dòng.
13/13 mục M1–M13 của mapping đã áp. Điểm đáng chú ý về cấu trúc: mục mới về tầng spec app được chèn thành **§7.5**, đẩy 「Bản thiết kế nháp」 thành **§7.6** — chọn vị trí này thay vì chèn ngay sau §7.3 để **không phá 3 liên kết `#74-…`** đang có ở Phụ lục G; anchor `#75-…` cũ (Bản thiết kế nháp) chỉ được nhắc trong Mục lục nên đổi an toàn.
Phụ lục B có thêm **B.5** (マルチセンサー), B.4 đổi tên thành 「ba thang đo」 và cập nhật cả 2 liên kết trỏ tới nó.

### G2. Cách review (chỉ vùng sửa, không đọc lại cả guide)

1. Lấy `git diff` của workspace làm **phạm vi duy nhất** — 47 khối, đọc hết từng khối.
2. Với mọi trích dẫn **mới hoặc bị sửa số dòng**: mở đúng dòng đó trên repo `1100487`, so từng chữ.
3. Chạy kiểm cơ học toàn file (rẻ, không tốn đọc): `check_links.py` — dựng slug từ 270 heading rồi đối chiếu mọi liên kết `](#…)`.

### G3. Ba lỗi do chính đợt sửa sinh ra — đã vá

| # | Lỗi | Vá thế nào |
|---|---|---|
| R-a | §7.3 vẫn giới thiệu Phụ lục B.4 là 「bảng **hai** thang」 trong khi B.4 nay có ba | Đổi thành 「bảng ba thang」 |
| R-b | Hai liên kết mới trỏ tới tiểu mục ①/④ của §0.7 bằng anchor tự chế — guide vốn có quy ước trỏ về **mục cha** `#07-giới-hạn-của-tài-liệu-này` | Trỏ về mục cha, đúng tiền lệ sẵn có |
| R-c | Câu mở đầu Phụ lục B vẫn đếm 「**Ba** mâu thuẫn」 sau khi thêm B.5 | Đổi thành 「Bốn mâu thuẫn (B.5 là mục mới)」 |

### G4. Kết quả kiểm cơ học (sau khi vá)

- **270 heading · 0 liên kết hỏng** (mọi `](#…)` đều trỏ tới heading có thật).
- **70 dấu ``` — chẵn**, không vỡ khối code.
- Không còn `460c671` nào đứng ở vai trò "mốc đối chiếu"; các chỗ còn giữ đều là **mốc lịch sử** (đợt sửa 08-06 và lệnh `git show 460c671`) — đúng chủ đích.

### G5. Trích dẫn mới đã kiểm lại tận nguồn

`B06`:8, 31, 41–43, 51–54, 74–79 ・ `A04`:8, 24, 30, 32, 41, 58, 73–75, 99–107 ・ `B01`:25–38, 75–82 ・ `B04`:110 ・ `E01` (−124 dòng, cụm còn lại) ・ `4_spec/app/README.md`:3, 5, 71–76, 86–145, 88, 145, 147–151 ・ `00_integrated_requirements_v1.2.md`:136, 151, 166, 193 ・ `11_business_process/readme.md`:38, 588, 620 ・ `minutes/20260623_egw_camp_day1.md`:92 ・ `3_requirements/app/README.md`:24–74, 52–56, 64 (D3 vẫn レビュー前).

### G6. Việc CHƯA làm (nằm ngoài mapping, chờ user quyết)

1. **6 phát hiện ở nguồn N1–N6** (mục E) — chưa hỏi mui/北ガス.
2. **Phụ lục C** chưa thêm dòng `GW-04` エネファーム, dù nay nó chặn spec `b05` (mapping mục D đã ghi là "để user quyết").
3. **Phụ lục D — Bản đồ tra cứu** chưa có dòng nào trỏ tới `4_spec/app/`.
4. `requirements/README.md` (bộ khung tài liệu) và `self_study_plan.md` chưa được rà theo tầng spec app mới.
5. Memory (`memory/00_INDEX.md` mục 🎯 + file session) chưa cập nhật đợt này.
