# SESSION 2026-08-18 — Rà & cập nhật `onboarding_guide.md` lên **v1.3** theo mốc `1100487`
> Đọc SAU `00_INDEX.md`. ⭐ TRẠNG THÁI MỚI NHẤT (chưa có file nào thay).
> ⚡ PHIÊN MỚI ĐỌC NHANH: việc kế tiếp = **mục 5**. Vết đầy đủ của đợt sửa (mapping + 2 lượt review) = `notes/guide_v13_mapping.md`.

## 1. Bối cảnh & mục tiêu phiên

Đợt review tài liệu team `2026_08_13/` đã đóng từ 17/08, phần còn lại thuộc user/member (gửi QA, cập nhật xlsx). Trong lúc chờ mui trả lời, user chọn quay lại **việc số 1 của hàng đợi: rà `onboarding_guide.md` theo mốc repo mới**.

**Quy trình user chốt (4 bước, chạy tuần tự trong main loop — KHÔNG phóng agent/workflow để tiết kiệm token):**
`rà + mapping toàn bộ chỗ cần sửa` → `review lại chính bản mapping` → `sửa` → `review CHỈ vùng đã sửa (không quét lại cả guide)`.

## 2. ĐÃ LÀM (kèm dẫn chứng)

1. **Fetch 5 nguồn** (⛔#1). Phát hiện **máy này đang cũ**: `eminel_gw_project` local `460c671` trong khi origin/main `1100487` — memory ghi `1100487` là trạng thái của **máy cũ** (`C:\Users\a\...`), không phải máy đang dùng. Đã `git pull --ff-only` → local = `1100487`. 4 nguồn còn lại khớp origin (`legacy_eminel_docs@ccd8f56` ・ backend@`dc39aa39` ・ web-admin@`e550326`); thư mục app trên máy này tên `syp-eminelstandard-app-syp-dev` và **KHÔNG phải git** (khác máy cũ — xem mục 6).
2. **Xác định phần lệch**: giữa `460c671..1100487` có **2 commit** — `57cd7be` 「要件fix」 (12/08, 10 file requirement, +82/−284, phản ánh **北ガス review slide đối khách ngày 08-07**) và `1100487` 「機能仕様着手」 (mở thư mục **`docs/eminel/4_spec/app/`** + skill `draft-app-spec`).
3. **Bước 1 — mapping** → `notes/guide_v13_mapping.md`: **13 mục phải sửa** (M1–M13: 3 mục 🔴 đảo kết luận ・ 6 mục 🟡 mốc/số liệu ・ 4 mục 🟢 bổ sung) + bảng **"đã xét, KHÔNG cần sửa"** (10 chỗ, để lần sau khỏi quét lại) + **6 phát hiện ở nguồn N1–N6**.
4. **Bước 2 — review mapping** (mục F của file mapping): mở lại đúng từng dòng đã trích trên đĩa, so từng chữ → **bắt 5 lỗi của chính bản mapping**: ① mốc `460c671` không chỉ ở đầu guide mà nằm **9 chỗ** ② sót ảnh hưởng sang Phụ lục B.4 ③ sót câu 「15 file/ba đợt」 (đúng: **20 file/bốn đợt**, `git diff --name-only 9dc5e34^..1100487`) ④⑤ trích sai 2 số dòng nguồn (A04 ランク `:21`→`:24`; E01 nhảy số `:29–35`→`:37–39`).
5. **Bước 3 — sửa**: guide **v1.2 → v1.3**, mốc đối chiếu `1100487` (2026-08-12), **+194/−49 dòng** (4.232 → 4.377 dòng). 13/13 mục đã áp. Ba thay đổi lớn nhất:
   - **§7.3 tiểu mục B6 viết lại toàn bộ**: từ "app chỉ GỢI Ý, người dùng tự tắt" → **"tự động điều khiển, app chỉ cài ngưỡng (dừng + chạy lại + xem lại)"**; câu 要確認事項 cũ về `F-GW-07` đã đóng (`経緯` B06:8 — 先方確認 08-07, 手動制御・Push = 対象外), thay bằng **3 câu treo mới** (エネファーム `GW-04` ・ ngưỡng chung hay theo máy ・ dải/mặc định/đơn vị `GW-07`).
   - **§7.5 MỚI 「機能仕様 app — tầng vừa mở」**: 5 ký hiệu tab a–e, kế hoạch **30 doc (mới viết 2: c02 グラフ・c03 レポート)**, thang trạng thái **thứ ba**, 4 kỷ luật viết, quy tắc 要件 thắng 現行, và cảnh báo **nguồn ưu tiên #2 là comment trong pptx đối khách — nằm NGOÀI repo**.
   - **Phụ lục B.5 MỚI** 「マルチセンサー còn tồn tại hay đã bị tách đôi」 + Phụ lục A thêm 2 mục từ (人感センサー ・ Web API連携機器).
   Vị trí chèn: mục mới thành **§7.5**, đẩy 「Bản thiết kế nháp」 → **§7.6** — chọn thế để **không phá 3 anchor `#74-…`** đang được Phụ lục G dùng.
6. **Bước 4 — review vùng sửa** (mục G của file mapping): lấy `git diff` làm phạm vi duy nhất (47 khối), mọi trích dẫn mới đều mở lại đúng dòng trên repo `1100487`; chạy thêm kiểm cơ học `check_links.py` (dựng slug 270 heading, đối chiếu mọi `](#…)`). → **3 lỗi do chính đợt sửa sinh ra, đã vá**: §7.3 còn gọi B.4 là "bảng hai thang" ・ 2 liên kết dùng anchor tự chế cho tiểu mục ①/④ của §0.7 (guide vốn có quy ước trỏ mục cha) ・ Phụ lục B còn đếm "Ba mâu thuẫn". Sau khi vá: **270 heading · 0 liên kết hỏng · 70 dấu ``` (chẵn)**.

## 3. QUYẾT ĐỊNH & PHÁT HIỆN

1. **Quy trình 4 bước của user tỏ ra hiệu quả và rẻ**: bước 2 (review chính bản mapping) bắt 5 lỗi *trước khi* chúng kịp đi vào guide; bước 4 giới hạn phạm vi bằng `git diff` nên không phải đọc lại 4.377 dòng. **Nên tái dùng cho mọi đợt cập nhật tài liệu lớn.**
2. **Bài học nội dung**: requirement app có thể **đảo nghĩa hoàn toàn trong 5 ngày** (B6). Trích requirement mà không kiểm dòng `経緯` = báo cáo đúng cái đã bị bỏ. Đã viết thẳng bài học này vào guide §7.3.
3. **Tầng tài liệu thứ tư đã mở** (`4_spec/app/`) ⇒ từ nay một chức năng app có tài liệu ở **hai tầng**; và **thang trạng thái thứ ba** ra đời (thang spec app dùng chung chữ 「ドラフト済（レビュー待ち）」 với thang requirement) — Phụ lục B.4 đã đổi tên thành 「ba thang đo」.
4. **Kỷ luật mới của tầng spec đáng nhớ khi đọc requirement**: câu 要確認事項 ở requirement mà thuộc mức spec thì bị **CHUYỂN HẲN** sang `確認事項` bên spec, không để lại bản sao ⇒ thấy 要確認事項 "biến mất" thì **tìm sang tầng spec trước khi kết luận là bỏ quên**.
5. 🔸 **Giả thuyết CHƯA kiểm chứng (đã ghi nhãn trong guide)**: ① マルチセンサー bị tách đôi thành 温湿度センサー + 人感センサー theo hướng dùng Aqara (căn cứ gián tiếp: `minutes/20260623_egw_camp_day1.md`:92) ② mâu thuẫn phạm vi huy hiệu (A04) nhiều khả năng là **slide phạm vi ↔ requirement chưa đồng bộ**, chứ không phải "sót khi tách file" như guide từng ngờ — vì A04 **đã được rà lại sau review 08-07** mà vẫn giữ nguyên phạm vi 2026.
6. **6 phát hiện ở nguồn (N1–N6)** — không phải lỗi guide, là lỗi/điểm mờ của chính repo `1100487`; đã liệt kê ở mục E của file mapping, **chưa hỏi mui/北ガス**. Đáng chú ý nhất: A04 mâu thuẫn nội bộ (要件概要 ghi 獲得ポイント数, requirement ghi 獲得バッジ数, mà bảng 備考 còn ghi rõ 「資料（獲得ポイント数基準）に従い記載」); E01 cắt requirement nhưng **để lại 6 hàng 備考と出典**, trong đó 2 hàng trỏ tới requirement đã bị xoá; B01 bảng 備考 vẫn ghi 「入力方法は要確認事項参照」 trong khi 要確認事項 đã bị dọn về 「なし」.

## 4. Thay đổi phía repo dự án

- `eminel_gw_project`: **local đã pull `460c671` → `1100487`** (2 commit: `57cd7be`, `1100487`). Đây là **thay đổi trạng thái máy này**, không phải commit mới trên origin — origin đứng ở `1100487` từ 12/08, fetch 18/08 không có gì mới hơn.
- 4 nguồn còn lại: không đổi.

## 5. VIỆC DỞ DANG / TIẾP THEO LÀM GÌ

0. ⚠️ **MỚI — đề bài từ mui, user tự đặt vào `submit_folder/2026_08_18/chokkin_irai.md` (45 dòng, chưa phân tích)**: ① **dựng môi trường dev riêng cho E-GW** (`dev’`, tách khỏi dev của E-Smart vì dev E-Smart dùng cho duyệt app) ② **chiến lược branch**: E-GW `syp-gw-dev` (phái sinh từ `syp-dev`, đồng bộ mỗi lần `syp-dev` đổi) + `gw-develop` (cần trước lúc thử nghiệm thực địa); E-Smart giữ `syp-dev`/`develop`/`main` — áp cho **cả BE, màn hình quản trị, mobile app** ③ **tái cấu trúc thư mục mobile app**: `apps/{e-smart-app, e-gw-app}` + `package/{theme, ui_components}` ④ **refactor E-Smart** sau khi dựng xong môi trường (review đổi tên model, tách tầng chung/tầng app, theme riêng từng app) ⑤ **điều tra danh sách batch backend** — chính là hạng mục đang làm dở (nhóm 集計・計算 còn 17/19 dòng). → **Chưa bàn với user, chưa lên kế hoạch.**
1. **6 phát hiện ở nguồn N1–N6** → user quyết có gộp thành đợt QA gửi mui/北ガス không (gộp chung với 4 câu QA đang chờ ở `submit_folder/qa/qa_review_20260813_20260817.md` hay tách riêng).
2. **Phụ lục C** chưa thêm dòng `GW-04` エネファーム dù nay nó chặn spec `b05` — mapping mục D đã ghi "để user quyết".
3. **Phụ lục D — Bản đồ tra cứu** chưa có dòng nào trỏ `4_spec/app/`.
4. `requirements/README.md` (bộ khung + tiêu chuẩn review) và `requirements/self_study_plan.md` **chưa rà theo tầng spec app mới** — riêng self_study_plan dòng 54 vẫn còn lỗi cũ chưa sửa (「集計・計算系 — e-smart không có gì dùng lại」, đã bị bác từ 08-12).
5. Hàng đợi cũ chưa đụng tới: **điền 7 dòng 配信・通知系 + Xzilla vào `summary_batch_migration_ja.md`** ・ **điều tra nhóm 集計・計算系** (17/19 dòng còn lại).
6. Việc thuộc user/member từ đợt 08-13: gửi 4 câu QA ・ cập nhật 13 sheet xlsx + thay 2 file md G3 ・ điền URL Notion.

## 6. CHƯA KIỂM (ghi rõ để phiên sau không tưởng đã kiểm)

- **Nội dung 2 bản nháp spec `c02_グラフ.md` và `c03_レポート.md` CHƯA đọc** — user chọn mức "Vừa" cho §7.5 (giới thiệu tầng + quy ước, không đi vào nội dung 2 file). `Z_コントロールタブ構成検討.md` cũng mới chỉ đọc tên.
- **Skill mới `.claude/skills/draft-app-spec/SKILL.md` (212 dòng) chưa đọc** — mới biết là nó tồn tại.
- **Thư mục app trên máy này (`sources/syp-eminelstandard-app-syp-dev`) không phải git** — trong khi CLAUDE.md (sửa 16/08 trên máy cũ) khẳng định repo app là git thật `@41ee385` tên `syp-eminelstandard-app`. 🔸 Nhiều khả năng **hai máy khác nhau**; chưa xác nhận với user, chưa sửa CLAUDE.md.
- Trạng thái QA trên Notion **vẫn là số liệu đọc ngày 2026-08-04** — chưa mở lại lần nào.

## 7. [Cuối phiên] Task mới — tái cấu trúc source app (đang chạy)

User chuyển sang task **tách/nhúng source E-GW vào repo app E-Smart**. **Toàn bộ nhật ký điều tra, số liệu đã kiểm chứng, kết luận và việc còn treo nằm ở `submit_folder/2026_08_18/output_schedule.md`** — phiên sau đọc file đó, không cần điều tra lại.

Tóm tắt để tra ngược:
1. Đề bài mui = `2026_08_18/requirements/app_source_change.md`; bản đã nộp = `CLIENT_REPORT_APP_RESTRUCTURE_ja.md`.
2. Review của AI đối chiếu nguồn thật đã bắt: bản「全体表」thiếu **6/23 section** (A2・B5・E1–E4) — **đã vá**; còn 3 khoảng trống: phiên bản Riverpod (kurashi 3.x ↔ E-Smart 2.5/2.6), "dùng chung UI" dễ hiểu nhầm (màn hình vẫn phải dựng lại từng app), và 2 kỷ luật bảo vệ goal 3 chưa viết ra.
3. Đã sửa trong báo cáo: §4.3 (+6 hàng căn cứ) ・ §5.3 (bảng 5 nhóm, bỏ hàng分類対象外 và câu漏れなく theo chỉ thị) ・ §5.1/§5.2 (thêm **`packages/data`**, gỡ REST client khỏi `utils`) ・ §7 câu 2 (chỉ hỏi applicationId Android).
4. ⚠️ **Đính chính trong phiên**: AI từng báo "báo cáo ghi sai applicationId (`_gas` thay vì `-gas`)" — **sai, file vốn đúng**; đã xác nhận lại trên đĩa và báo user. Bài học: trích dẫn mã định danh phải `grep` chứ không đọc bằng mắt.

### 7b. [19/08] Chốt bản nộp — sửa 2 mục, đóng 1 mục

- **Tiêu chí user chốt 19/08**: *chỉ sửa cái sai đến mức **đổi quyết định của người đọc**, còn lại kệ* — "đừng bắt từng con kiến trong miếng bánh"; rà đến khi hết lỗi thì không bao giờ nộp được. Áp cho mọi đợt hoàn thiện tài liệu từ nay.
- **Đã sửa vào `CLIENT_REPORT_APP_RESTRUCTURE_ja.md`**: ① §2.2 + §8.1 「24件」→**23件** requirement (đếm thật `docs/eminel/3_requirements/app/` @`1100487`: A01–A04·B01–B06·C01–C05·D01–D04·E01–E04) ② §4.1 ô 規模 lấy **481 file viết tay / ~74.000 dòng** làm số chính, 881 = số sau khi sinh code ③ §5.3 thêm ghi chú 「共通」の範囲 — chung là logic/state/data/部品, `features/common` **không chứa màn hình**, nên màn hình đăng nhập/お知らせ vẫn dựng lại ở từng app (chặn hiểu nhầm "dùng lại cả màn hình").
- **Đóng vĩnh viễn**: *lệch phiên bản Riverpod kurashi 3.x ↔ E-Smart 2.x* **không phải việc** — kurashi chỉ là repo mẫu cấu trúc thư mục, đã chốt không dùng `kurashi_data`, báo cáo grep "riverpod" = 0. Ghi chú cũ nói nó "ảnh hưởng ước lượng 15–27 người-ngày" là **diễn đạt sai**: 15–27 người-ngày là ước lượng CẢ đợt tái cấu trúc (§5.7 báo cáo).
- **Không đưa vào bản nộp** (quyết định): 2 kỷ luật bảo vệ goal 3 + "CI build cả 2 app mỗi PR" — kỷ luật nội bộ lúc implement.
- ⚠️ **Bài học của AI trong phiên**: khi user phản biện, tôi đã **kết luận "không có gì phải vá" nhanh hơn mức bằng chứng cho phép** (chưa mở báo cáo đã khẳng định ý nghĩa con số 15–27). Phải kiểm trên đĩa TRƯỚC khi đồng ý hay bác bỏ — đồng ý vội cũng là một dạng hallucinate.
- Việc còn treo rút còn 3 mục, xem mục 7 của `submit_folder/2026_08_18/output_schedule.md`.
