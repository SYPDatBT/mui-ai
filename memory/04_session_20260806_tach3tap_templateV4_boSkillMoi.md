# SESSION 2026-08-06 — Tách báo cáo 3 tập (JP+VN) ・ template v4 ・ bộ skill mới ・ kế hoạch tự học
> Đọc SAU `00_INDEX.md`. ⭐ TRẠNG THÁI MỚI NHẤT (chưa có file nào thay).

## 1. Bối cảnh & mục tiêu phiên

- Khách break task điều tra batch trên Notion thành **3 task riêng** (外部連携・受信系（Xzilla取込）／配信・通知系／CSV・ZIPエクスポート系, đều 08/03→08/14, In Review) → báo cáo gộp 11 batch không dùng được nữa, phải **tách thành 3 tập × 2 ngôn ngữ**.
- User nộp + trình bày tập **Xzilla** trong ngày → tập này phải review kỹ, gồm cả kiểm tác động của thay đổi repo mới.
- Cuối phiên user chuyển hướng: yêu cầu **bản ngắn** (`new_2/`), rồi yêu cầu **thể chế hóa quy trình thành skill**, cuối cùng là **kế hoạch tự tìm hiểu 4 hạng mục**.

## 2. ĐÃ LÀM

### 2.1 Pull repo + phân tích thay đổi
- `eminel_gw_project` **fast-forward `788b438` → `fbc0af0`** (6 commit của hanamiju: 1 commit 03/08 19:53 「スライドの内容から反映」 + 5 commit 05/08 17:56–18:15). Diff = **13 file `docs/eminel/3_requirements/app/` + 1 dòng `.claude/skills/draft-app-requirements/SKILL.md`**, +215/−355.
- 3 repo còn lại không đổi: `legacy_eminel_docs@ccd8f56`, backend@`dc39aa39`, web-admin@`e550326` (đều = origin).
- Nội dung thay đổi chính (workflow 7 agent phân tích + kiểm chứng chéo):
  - `app/README.md`: bỏ cột 「状態」, thêm **「内容・スコープ」「ステータス」「劣後」 lấy từ slide đối khách (2026-08-05反映)**; trạng thái review md chuyển sang `tasks/app_requirements_plan.md`. **22/23 section đổi trạng thái** — đáng chú ý: **C1–C5 đều 「レビュー済」**; 劣後 ✅ = A3 ポイント, A4 バッジ, B3 冷房; 「一部」 = B4, B5.
  - **B02 暖房 sửa lớn** (+33/−84): bỏ khái niệm **設定値運転**, thay bằng trục 「室温制御の有無」 + khái niệm mới **温度レベル**; xóa section 「機器構成とできること」, xóa yêu cầu đặt 就寝時刻, xóa section ローカル通信（2027/4〜）. 経緯 ghi rõ: phản ánh 先方レビュー từ slide (08-03) + xóa mô tả lấy 合宿議事 làm 出典 (08-05).
  - **B06 マイホーム発電 viết lại hoàn toàn** (+86/−8): 1 yêu cầu 【新規】 = nhận 案内 dừng コレモ/エネファーム khi PV đạt ngưỡng.
  - **A01 xóa sạch 「未ログイン利用モード」**; B01 gỡ toàn bộ TBD cảm biến nhiệt/ẩm; **B05 DR yêu cầu KHÔNG đổi** (chỉ gỡ trích 合宿議事); nhóm D cắt gọn (D04 bỏ khối 要確認 CLD-05, D02 bỏ quan ngại 匿名性…).
  - Xu hướng chung: xóa tiểu mục 「現行からの変更点（候補）」 ở mọi file, cắt 関連項目 và chi tiết so sánh 現行/ESTA.

### 2.2 Bộ báo cáo tách 3 tập — 3 thế hệ
| Thư mục | Nội dung |
|---|---|
| `submit_folder/2026_08_06/` | **Thế hệ 1** — 6 file tách theo 3 task, dựng dần theo yêu cầu user (kết luận-trước, sơ đồ ASCII, trích code, bảng chi tiết 8 IF, gloss tự chứa). Đã qua review độc lập từng cặp; findings vá hết |
| `submit_folder/2026_08_06/new/` | **Thế hệ 2 (v4)** — dựng lại theo TEMPLATE v4 (2 PHẦN), 3 reviewer độc lập, vá hết. Xzilla 607×2 ・ 配信 780/784 ・ CSV 481/482 dòng |
| `submit_folder/2026_08_06/new_2/` | **Thế hệ 3 — BẢN DÙNG** (user chốt "ngắn gọn, người đọc là chính tôi"): cắt ~50%, bỏ giải thích vỡ lòng/ví von, gloss gom về 1 bảng Ký hiệu đầu file. Xzilla 314×2 ・ 配信 402/395 ・ CSV 244/243 |

- **Chuẩn hóa cuối trên `new_2/`** (tự làm, không qua agent): mọi trích dẫn **full path từ tên repo → dòng** (kiểm `short=0, noprefix=0` cả 6 file; sửa cả `InterfaceCode.php` về đúng `src/PointInfinity/Api/`); mỗi luồng data có sơ đồ + dòng đối chiếu Cũ ↔ Mới.
- Kết luận phán định **không đổi qua cả 3 thế hệ**: #5/#6 = bỏ batch–giữ nghiệp vụ/dữ liệu ・ #7 = tạo mới (nặng nhất) ・ #1 = dùng lại point+PI, mới tầng phán định ・ #2 = tạo mới engine ・ #3 = bỏ batch, dùng hạ tầng FCM ・ #4 = 2026 không code ・ #8–#11 = bỏ cả 4.

### 2.3 Findings đáng giá do review độc lập bắt được
- **[cao] 前月 → 前々月** (nhóm CSV/ZIP): `subDays(32)` từ 05:15 ngày 1 **luôn** rơi vào tháng −2, khớp `dropMonthlyTable(…, 2)` = `subMonths(2)` (`DeleteDataCommand.php:110-112`). Đã vá 6 vị trí/file.
- **[cao] path bịa** (Xzilla v4): ghi `1_product/00_integrated_requirements_v1.2.md` — file thật ở `3_requirements/`.
- **[vừa]** sót chữ tiếng Anh "still" trong heading bản JP (2 tập); mã nội bộ `spec [I]`/`SVC-03` lọt vào blockquote câu gửi khách; rơi mục 使い続け và kết luận 集計・計算系 khi tái cấu trúc.
- Con số tự đếm được xác nhận: backend `src/functions/` = **105 thư mục, 81 tên `batch-*`, chỉ 3 `ScheduleV2`** → "batch-" ở repo mới **không có nghĩa chạy theo lịch**.
- Bảng chi tiết 8 kênh IF (nguồn 基幹 → trường từ code → bảng đích → tác dụng): trường lấy từ **enum `LIST_COL_*` trong `constants.ts:468-565`** (interface `IData*.ts` chỉ là mapped type trỏ về đây).

### 2.4 Bộ skill mới (thể chế hóa quy trình)
| Skill | Vai trò |
|---|---|
| `skillAI/create-investigation-report/` | **TEMPLATE.md v4** (nguồn sự thật duy nhất về cấu trúc báo cáo điều tra: 2 PHẦN + 12 tiêu chí) + quy trình 6 bước (code-first → dựng → tự kiểm → review độc lập → bàn giao) |
| `skillAI/analyze-change-request/` | **⛔#11**: tiếp nhận mọi yêu cầu sửa → phân loại → tổng quát hóa → tranh biện 3 agent (MINIMAL/HOLISTIC/CRITIC + brainstorm chéo) → đề xuất tổng thể → thực thi nguyên khối |
| `skillAI/3-step-review/` (sửa) | Thêm tiêu chí ⑤ TỰ CHỨA + checklist 10 điểm ở Vòng 3 + kiểm tuân thủ TEMPLATE v4 (thiếu/đảo mục = [cao]) + baseline mục 4 trỏ sang bộ v4 |

### 2.5 Tài liệu khác
- `requirements/self_study_plan.md` (MỚI): kế hoạch tự tìm hiểu 4 hạng mục SYP đối ứng — mọi path đã verify tồn tại.
- `CLAUDE.md`: mục `skillAI/` cập nhật 5 skill.

## 3. QUYẾT ĐỊNH & PHÁT HIỆN

1. **Bản dùng chính thức = `new_2/`**; `new/` và bản gốc `2026_08_06/` giữ làm vết (không sửa ngược).
2. **Quy tắc ⛔#10 (tự chứa)** và **⛔#11 (phân tích trước khi đồng thuận)** sinh từ chính phiên này — ⛔#11 từ bài học "vá đuổi tạo tài liệu nồi lẩu, phải đập làm lại".
3. Chuẩn giao tiếp với user (ghi vào memory cá nhân): user hiểu kỹ thuật → **chat viết ngắn, không giải thích vỡ lòng**; tài liệu VN vẫn giữ lớp giải thích vì phục vụ người đọc khác.
4. 🔸 Chưa kiểm chứng: quan hệ nhân quả giữa 6 commit tối 05/08 và buổi làm việc chiều 05/08 với mui (thời điểm trùng nhau).
5. Sự cố vận hành: 3 agent nền chết giữa chừng vì **hết hạn mức chi tiêu tháng** — phần chuẩn hóa cuối của `new_2/` do main tự làm.

## 4. Thay đổi phía repo dự án

- `eminel_gw_project`: pull `788b438` → **`fbc0af0`** (= origin/main). Không commit/push gì vào repo dự án.
- 3 repo còn lại: không đổi (`ccd8f56` / `dc39aa39` / `e550326`).
- Ảnh hưởng tới tài liệu: nhóm Xzilla và CSV/ZIP **không bị ảnh hưởng** (đã kiểm bằng `git diff`); nhóm 配信・通知系 phải cập nhật số dòng trích: `B05_dr.md:8, 32-34` ・ `D03_push.md:5, 7, 29-31, 81-83`. Ghi nhận lệch có hệ thống: 状態 trong file md (レビュー中) ≠ ステータス trên README/slide khách (レビュー前) ở cả B05 lẫn D03.

## 5. VIỆC DỞ DANG / NGÀY MAI LÀM GÌ

1. **Nộp tập Xzilla + trình bày** (nếu chưa xong trong ngày): bản JP `new_2/旧EMINELバッチ移行判定報告書_外部連携・受信系（Xzilla取込）3本.md`; bản VN cùng tên.
2. **Kiểm QAデータベース Notion** — 3 trang vẫn trích theo trạng thái 回答中 ngày 08-04; nếu đã 回答済 thì cập nhật các tập.
3. **Điều tra tiếp batch còn lại (~35/46)** — nhóm ưu tiên: **集計・計算系** (dự kiến nặng nhất, e-smart không có gì dùng lại). Dùng skill `create-investigation-report`.
4. **Cập nhật `onboarding_guide.md` theo `fbc0af0`** (việc user hoãn lại từ đầu phiên): guide 7.3 theo B06 mới, rà các mục trích B02/B05/D03/A01/B01, mục 8.x về "23/23 section chưa chốt" (nay C1–C5 đã レビュー済).
5. Các việc treo từ phiên trước vẫn nguyên: trả lời vế ただし QA 独立デプロイ ・ chốt kihara Q5 (DR) → gửi `qa_kitagas.md` ・ hỏi đích `/EST` ・ theo dõi CLD-01/CLD-02/CLD-07 + spec [G]/[I].
6. Bắt đầu **kế hoạch tự học** theo `requirements/self_study_plan.md` (thứ tự: hạng mục 1 → 2 → 3 → 4).

## 6. CHƯA KIỂM

- Kết quả buổi làm việc chiều 05/08 với mui — chưa có ghi nhận nào vào memory (session 03 để lại việc này).
- 3 trang QA Notion: vẫn 回答中 theo ảnh chụp 08-04, chưa mở lại trang gốc.
- Đích SFTP `/EST` (secret ngoài repo); `periodSecond` phía nền tảng MUI.
- Bộ `new_2/` **chưa chạy review độc lập** sau khi rút ngắn + chuẩn hóa trích dẫn (bản `new/` thì đã review đủ) — user dự định đưa Codex review ngoài.
