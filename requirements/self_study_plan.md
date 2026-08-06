# Kế hoạch tự tìm hiểu — 4 hạng mục SYP phải đối ứng

| | |
|---|---|
| Người học | Bui Trong Dat (SYP) |
| Ngày lập | 2026-08-06 |
| Mục tiêu | Nắm đủ để (a) điều tra tiếp ~35 batch còn lại, (b) đọc/viết requirement, (c) ước công khi spec chốt |
| Phạm vi | 4 khối SYP đối ứng: server E-GW ・ batch + liên kết ngoài ・ 管理画面 ・ mobile app |
| Ghi chú path | Mọi đường dẫn tính từ `sources/`. Bốn repo git + 1 snapshot app (xem `CLAUDE.md`) |

## Nguyên tắc chung khi tự học

1. **`git fetch` + so `origin/main` trước khi tin số dòng** — local có thể cũ (⛔#1).
2. **Code thắng tài liệu**: `docs/eminel-smart/` là bản khảo sát, đã phát hiện 6 chỗ lệch code thật. Trích tài liệu → kiểm lại code trước khi dùng làm căn cứ.
3. **Phân biệt 3 hệ**: `eminel` (E-GW, sắp làm) ・ `old_eminel` (hệ cũ đang chạy) ・ `eminel-smart`/ESTA (nền tảng sẽ dùng lại). Đọc nhầm hệ là hỏng cả mạch.
4. **Nguồn sống**: QAデータベース Notion — trạng thái đổi liên tục, ghi 参照日 khi trích.

---

## Hạng mục 1 — Nghiệp vụ server EMINEL-smart cho E-GW

**Mục tiêu**: biết server phải làm gì cho khách (dữ liệu đo, sưởi, điểm, report), ranh giới với GW管理クラウド, và dữ liệu chảy đi đâu.

| Thứ tự | Đọc gì | Vì sao |
|---|---|---|
| 1 | `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` — mục 3 (構成), 4 (IF一覧 IF-01〜24), 8-1〜8-4 (F-GW/F-MC/F-ES/F-AD) | **Tài liệu gốc quan trọng nhất.** Mục 8-3 F-ES-xx chính là danh mục chức năng server bạn phải làm |
| 2 | `eminel_gw_project/docs/eminel/1_product/11_business_process/readme.md` | Luồng nghiệp vụ theo slide đối khách: onboarding, hiển thị, sưởi, DR, giải ước. Đọc để biết **ai thao tác gì, thứ tự nào** |
| 3 | `eminel_gw_project/docs/eminel/1_product/10_feature_list.md` | Bảng chức năng + cột 劣後 (✅ = lùi 2027). Biết cái nào phải làm năm nay |
| 4 | `eminel_gw_project/docs/eminel/2_management/22_decisions.md` + `20_open_issues.md` + `21_todo.md` | Cái gì đã chốt / đang treo (CLD-01, CLD-02, CLD-07…) / ai phải làm gì |
| 5 | `eminel_gw_project/docs/eminel-smart/02_product_overview.md` + `03_backend_models.md` | Nền tảng e-smart hiện có: kiến trúc AWS, danh sách bảng DynamoDB |
| 6 | Code: `syp-eminelstandard-backend/template.yaml` (hạ tầng), `src/functions/` (Lambda), `src/layers/common/nodejs/` (models, business-logic, services) | Xem thật hệ đang chạy thế nào — đối chiếu với mục 5 |

**Cách đọc**: mở mục 8-3 (F-ES) của v1.2, mỗi chức năng tự hỏi "e-smart đã có chưa?" → grep trong `syp-eminelstandard-backend/src`. Đây đúng là cách 3 báo cáo batch đã làm.

**Tự kiểm**: ① khách mở app xem biểu đồ — dữ liệu qua bao nhiêu chặng, master nằm ở đâu? ② vì sao 管理画面 và app không được gọi thẳng GW管理クラウド? ③ kể 5 chức năng F-ES thuộc scope 2026.

---

## Hạng mục 2 — Danh sách batch + liên kết ngoài

**Mục tiêu**: biết ~46 batch gồm những nhóm nào, batch nào còn cần, batch nào bỏ — và điều tra tiếp được một mình.

| Thứ tự | Đọc gì | Vì sao |
|---|---|---|
| 1 | `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` | **Danh mục gốc toàn bộ batch hệ cũ** — chia nhóm sẵn. Đây là bảng phân việc của bạn |
| 2 | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/` (cron設定概要.txt, mng-webap_cron設定_20241029.txt, tgz chứa shell) | Lịch chạy thật + shell wrapper (flock, `set -eu`). Biết batch nào chạy khi nào |
| 3 | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/` | **Code thật của từng batch.** Đọc theo tên batch trong danh mục |
| 4 | `legacy_eminel_docs/docs/02_詳細設計/00_データベース設計` + `07_データ加工` + `08_データ削除と過去データCSV作成` | Ý nghĩa bảng `t_xxx`/`s_xxx`, quy tắc xử lý dữ liệu, chính sách xóa |
| 5 | `syp-eminelstandard-backend/src/statemachine/*.asl.json` + `src/functions/batch-*` | Batch của e-smart chạy kiểu gì (Step Functions + EventBridge, one-shot) |
| 6 | `mui-ai/submit_folder/2026_08_06/new_2/` (3 báo cáo của chính bạn) | Mẫu điều tra hoàn chỉnh — lặp lại cách này cho batch còn lại |

**Nhóm batch (theo danh mục gốc)** — đã điều tra 11/46:
- ✅ 配信・通知系 (4) ・ 外部連携・受信系 Xzilla (3) ・ CSV/ZIPエクスポート系 (4)
- ⬜ 集計・計算系 — **dự kiến nặng nhất**, e-smart không có gì dùng lại
- ⬜ 暖房制御系 ・ アラート系 ・ DB保守系 ・ còn lại

**Quy trình điều tra 1 batch** (rút từ 11 batch đã làm):
```
① đọc mô tả trong 04_バッチ一覧.md
② mở code Command tương ứng → ghi: đọc bảng nào, ghi bảng nào, logic gì
③ tra cron: chạy khi nào, mấy lần
④ grep trong syp-eminelstandard-backend: e-smart có tương đương không
⑤ tra v1.2 + 10_feature_list: E-GW có yêu cầu không, scope năm nào
⑥ kết luận: dùng lại / tạo mới / bỏ (nêu rõ BỎ gì – GIỮ gì – THAY bằng gì)
```

**Tự kiểm**: ① kể tên 3 nhóm đã điều tra và kết luận từng nhóm; ② batch nào của hệ cũ đọc bảng `s_102`? ③ vì sao "bỏ batch" không có nghĩa là bỏ nghiệp vụ?

---

## Hạng mục 3 — 管理画面 (web-admin)

**Mục tiêu**: đọc được spec 10 màn hình, biết cái nào kế thừa ESTA, cái nào mới hoàn toàn.

| Thứ tự | Đọc gì | Vì sao |
|---|---|---|
| 1 | `eminel_gw_project/docs/eminel/4_spec/admin/` — 10 file `A_`〜`J_` | **Spec chính.** [C] E-GW管理 và [D] dashboard là **mới hoàn toàn**; [D] thuộc 劣後 2027 |
| 2 | `eminel_gw_project/docs/eminel/5_design/admin/index.html` (mở bằng trình duyệt) | Bản thiết kế nháp HTML — nhìn thấy màn hình trước khi đọc spec chữ |
| 3 | `syp-eminelstandard-web-admin/pages/` + `components/` + `constants/common.ts` | Màn hình ESTA đang chạy — cái sẽ được dùng lại/mở rộng |
| 4 | `legacy_eminel_docs/docs/02_詳細設計/03_管理画面` | Màn quản trị hệ cũ (`eminelsv`) — đối chiếu chức năng vận hành cũ |
| 5 | `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` mục 8-4 (F-AD-xx) | Danh mục chức năng màn hình quản trị ở tầng yêu cầu |

**Lưu ý quan trọng**: 管理画面 **chung source code và chung deploy với ESTA** (QA masao takahashi, 2026-08-03, 回答中) — khác với server (hướng độc lập). Nghĩa là bạn sẽ **thêm màn hình vào chính repo `syp-eminelstandard-web-admin`**, không dựng repo mới.

**Tự kiểm**: ① 10 spec [A]–[J] tương ứng những màn hình nào? ② màn hình nào mới hoàn toàn, màn nào lùi 2027? ③ trang data-management hiện có mấy loại dữ liệu tải được?

---

## Hạng mục 4 — Mobile app

**Mục tiêu**: hiểu app ESTA đang có gì (Flutter), 23 section requirement E-GW đòi gì, chỗ nào phải sửa.

| Thứ tự | Đọc gì | Vì sao |
|---|---|---|
| 1 | `eminel_gw_project/docs/eminel/3_requirements/app/README.md` | Chỉ mục 23 section + trạng thái + cột 劣後 (giá trị lấy từ slide đối khách) |
| 2 | `eminel_gw_project/docs/eminel/3_requirements/app/` — 23 file `A01`〜`E04` | **Requirement app.** Đọc theo nhóm: A tài khoản/điểm ・ B điều khiển thiết bị ・ C hiển thị năng lượng ・ D thông báo ・ E khác. Nặng nhất: `B02_heating_control.md` |
| 3 | `eminel_gw_project/docs/eminel/3_requirements/app/Z_old_mapping.md` | Bản đồ đối chiếu chức năng app cũ ↔ section mới |
| 4 | `eminel_gw_project/docs/eminel-smart/05_view_structure.md` + `04_app_models.md` | Cấu trúc màn hình + model của app ESTA hiện có |
| 5 | `syp-eminelstandard-app-syp-dev/lib/presentation/pages/` + `lib/server/rest_client/` | Code thật: màn hình và client API |
| 6 | `legacy_eminel_docs/docs/04_アプリ/` — `01_機能設計・仕様書まとめ.md`, `03_ソース構成まとめ.md`, `11_アーキテクチャ.md`, `12_画面遷移・画面構成.md` | App cũ: chức năng, kiến trúc, sơ đồ chuyển màn hình |
| 7 | `eminel_gw_project/docs/old_eminel/app/00_feature_list.md` + `screens/` (22 ảnh) | Ảnh chụp màn hình app cũ — nhanh nhất để hình dung |

**Lưu ý**: app build **2 bản riêng** (ESTA / EMINEL) bằng biến môi trường; repo app là **snapshot không có git** → số dòng có thể lệch khi mui giao bản mới.

**Tự kiểm**: ① 23 section chia làm mấy nhóm, nhóm nào nặng nhất? ② app ESTA đã có màn hình nào dùng lại được cho E-GW? ③ section nào đang 劣後?

---

## Thứ tự học đề nghị

```
Tuần này    Hạng mục 1 (mục 1–4) → nền chung, không có nó thì 3 cái kia rời rạc
            Hạng mục 2 (mục 1–3) → phục vụ trực tiếp việc đang làm: điều tra batch tiếp
Tuần sau    Hạng mục 2 (mục 4–6) → điều tra nhóm 集計・計算系
            Hạng mục 3           → nhẹ, đọc khi cần viết/review spec
Khi có spec Hạng mục 4           → app phụ thuộc requirement chốt (23 section đang review)
```

**Song song, không chờ ai**: bám 3 điểm chặn CLD-01 (spec API GW) ・ CLD-02 ・ CLD-07 (IF-01 Xzilla) — mọi thiết kế đều dừng ở đây.

## Tài liệu nội bộ hỗ trợ

| File | Dùng khi |
|---|---|
| `mui-ai/requirements/onboarding_guide.md` | Nền tổng thể — 10 chương; tra nhanh bằng Phụ lục D |
| `mui-ai/requirements/qa_kitagas.md` | Câu hỏi đã/sắp gửi khách |
| `mui-ai/submit_folder/2026_08_06/new_2/` | 3 báo cáo batch — mẫu để lặp lại |
| `mui-ai/skillAI/create-investigation-report/TEMPLATE.md` | Khuôn viết báo cáo điều tra |
