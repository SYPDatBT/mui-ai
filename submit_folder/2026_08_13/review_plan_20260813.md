# PLAN REVIEW — Tài liệu điều tra batch & mobile app của team (đợt 2026-08-13)

| | |
|---|---|
| Người lập | AI (Claude) — theo yêu cầu Dat (SYP) |
| Ngày lập / cập nhật | 2026-08-13 / **2026-08-16** (bản đã qua 4 agent phản biện, 26 findings vá hết) |
| Trạng thái | **ĐÃ DUYỆT 2026-08-16** (user chốt: member đã ngừng sửa ・ deadline thứ 2 tuần sau — hiểu an toàn là 17/08 ・ P4/P5/P6 chạy song song ・ mặc định §8.1–3, 6 chấp thuận) — đang thực thi từ P0 |
| Đối tượng | Toàn bộ tài liệu trong `submit_folder/2026_08_13/` do các thành viên team tạo: 75 file điều tra (md) + 7 file phán định `batch_decision.xlsx` (**43 sheet**) + bảng tổng hợp `summary_batch_migration_ja.md` (47 dòng) |
| Đầu ra | ① findings đúng/sai từng file (kèm `file:dòng` nguồn đối chiếu) ② verdict cho **từng phán định của member trong 43 sheet `batch_decision`** ③ bản sửa các file có lỗi + bản dịch tiếng Nhật cho file chưa có — đặt trong `new/` từng folder ④ 7 file `batch_decision.md` convert 1-1 từ xlsx (giữ nguyên nội dung, đã tự review) ⑤ `review_summary.md` tổng hợp: sai ở đâu・nguyên nhân・đối chiếu nguồn nào・đã sửa thế nào |
| Quy trình | Skill `3-step-review` (3 vòng: XÁC THỰC → NHẤT QUÁN → DỄ HIỂU), điều chỉnh cho tài liệu member (§4.6) |

**Mốc repo đối chiếu** (P0 đã fetch lại **16/08**: cả 5 repo khớp origin, HEAD không đổi so bảng — mốc giữ nguyên):

| Repo | Branch | HEAD (13/08) | Vai trò trong review |
|---|---|---|---|
| `eminel_gw_project` | main | `1100487` | Requirement mới: v1.2 + feature list + spec admin + requirement app C01–C05 — 第一優先 của phán định |
| `legacy_eminel_docs` | main | `ccd8f56` | Code + thiết kế hệ cũ (nguồn xác thực chính của các file điều tra) |
| `syp-eminelstandard-backend` | gw-syp-dev | `dc39aa39` | Code e-smart — xác thực khẳng định "e-smart có/không có" |
| `syp-eminelstandard-web-admin` | gw-syp-dev | `e550326` | Màn hình quản trị e-smart (khi phán định nhắc F-AD) |
| `syp-eminelstandard-app` | syp-dev | `41ee385` | App ESTA — mốc đối chiếu G8/P1. ⚠️ Là **git repo thật** (không phải snapshot như CLAUDE.md đang ghi — đề xuất cập nhật CLAUDE.md, ngoài phạm vi plan) |

---

## 1. Nhiệm vụ (đọc lại từ yêu cầu user)

1. **Review file điều tra** của các thành viên (hệ batch cũ old-eminel + 5 module mobile app C1–C5) — đúng quy trình 3 vòng của skill `3-step-review`.
2. **Review lại phán định của member** — gồm cả kết luận nằm trong **từng sheet `batch_decision.xlsx`** (user nhấn mạnh 08-16): mỗi phán định nhận 1 verdict riêng, đối chiếu **requirement mới** (`00_integrated_requirements_v1.2.md` là 第一優先) chứ không chỉ đối chiếu code.
3. **Sửa** các chỗ sai tìm được — bản sửa đặt trong `new/` từng folder (§4.3), file gốc member không đụng.
4. File nào **chưa có bản tiếng Nhật** → sau khi review + sửa xong, **tạo bản tiếng Nhật** (bản nộp khách) vào `new/`.
5. **Convert 7 file `batch_decision.xlsx` → markdown**: 1 xlsx = đúng 1 md (bất kể bao nhiêu sheet), **giữ nguyên tuyệt đối nội dung**; tạo xong **tự review lại bản md** (đối chiếu ngược từng ô). Chi tiết §5b.
6. Ghi toàn bộ vào `review_summary.md`: sai ở đâu, nguyên nhân, đối chiếu ở đâu (source nào, file nào, dòng bao nhiêu), đã sửa như thế nào.

## 2. Hiện trạng đã khảo sát (lúc lập plan; P0 kiểm kê lại)

### 2.1 Kiểm kê 8 thư mục con

| # | Thư mục | File điều tra | Ngôn ngữ | Phán định | Cần dịch JA sau review? |
|---|---|---|---|---|---|
| G1 | `集計・計算系バッチの調査・分析・報告` | 36 md legacy (17 cặp VN+JA + 2 chỉ JA) + 1 md current-eminelsmart (JA) | VN+JA | xlsx **19 sheet** | Không (đã đủ JA) — nhưng phải kiểm cặp VN↔JA khớp nhau |
| G2 | `データ管理系バッチの調査・分析` | 8 md | VN | xlsx **8 sheet** | **Có — 8 file** |
| G3 | `配信・通知系バッチの調査・分析` | 4 md legacy + 4 md current-eminelsmart | VN | xlsx **4 sheet** (chỉ trỏ file — kết luận chính thức nằm trong 4 md current-eminelsmart) | **Có — 8 file** |
| G4 | `外部連携・受信系（Xzilla取込）バッチの調査・分析` | 3 md | VN | xlsx **3 sheet** | **Có — 3 file** |
| G5 | `監視・ログ系バッチの調査・分析` | 3 md | VN | xlsx **3 sheet** | **Có — 3 file** |
| G6 | `CSV,ZIPエクスポート系バッチの調査・分析` | 4 md (JA) | JA | xlsx **4 sheet** | Không |
| G7 | `EminelSV（新EMINELサーバ／運用管理画面）の調査・分析` | 2 md | VN | xlsx **2 sheet** | **Có — 2 file** |
| G8 | `モバイルアプリ要件レビュー（C1～C5）` | 5 cặp ja+vn (10 md) | VN+JA | không có (đúng như user báo) | Không |

Tổng: **75 file điều tra ・ 43 sheet phán định (19+8+4+3+3+4+2) ・ 24 file cần dịch JA** (sau khi sửa xong).

### 2.2 Phát hiện từ khảo sát — định hình trọng tâm review

1. **4 file `_ja.md` của G6 (CSV/ZIP) GIỐNG HỆT** (diff = 0) bản của SYP ở `submit_folder/2026_08_12/` — đã qua review nhiều vòng và đã nộp. → Đề xuất **không review lại nội dung 4 file này** (chỉ review 4 sheet phán định xlsx) — cần user duyệt, xem §8.3.
2. **27/43 sheet phán định chứa nguyên văn câu** 「再利用可能なバッチ、または同等のロジックは存在しません。」, phân bố **G1 18/19 ・ G2 4/8 ・ G4 3/3 ・ G7 2/2** (26 sheet chỉ có đúng câu đó, không kèm dẫn chứng `file:dòng` nào; riêng sheet `DeleteTimeOutControlOneMinuteCommand` của G2 kèm thêm 1 vế về việc bỏ polling). Trong đó:
   - **18/19 sheet của G1 (集計・計算系)** — ngoại lệ duy nhất là sheet `CalcTenMinutesEnergyCommand` trỏ sang `current-eminelsmart_CalcTenMinutesEnergy_ja.md`. Câu này **va chạm trực diện** với phát hiện đã kiểm chứng 08-12 của workspace: e-smart **CÓ** 3 bảng tích luỹ `DeviceAccumulatedHistoryTable`/`DeviceDailyUsageHistoryTable`/`DeviceMonthlyUsageHistoryTable` (`template-dynamodb.yaml:1113/1145/1177`), ghi bởi 5 batch `batch-import-rinnai/noritz-*`. Khác biệt thật: e-smart **nhận giá trị đã tính sẵn** từ Rinnai/Noritz chứ không tự tính. → Kết luận hành động của member có thể vẫn đúng, nhưng câu 「存在しません」 sai sự kiện — từng batch phải phân định lại (quy tắc phân ranh verdict: §5).
   - **3/3 sheet của G4 (Xzilla)** — va chạm với phát hiện new_2: e-smart **CÓ** nền nhận Xzilla SFTP→S3→DynamoDB.
3. **Phán định hầu hết chỉ trả lời "e-smart có sẵn hay chưa", chưa đối chiếu requirement E-GW** — trong khi nhiệm vụ user giao là phán định theo **requirement mới**. Ví dụ rủi ro: bỏ toàn bộ batch 集計 nhưng C1 グラフ表示・C2 レポート表示 (đã レビュー済) vẫn cần dữ liệu chuỗi thời gian + so sánh nhóm → dữ liệu đó ai sinh ra trong hệ mới? Đây là **trục review thứ hai, bắt buộc cho mọi batch** (§5 bước 5); "bảng nhu cầu dữ liệu app" được dựng ngay ở P1 làm căn cứ dùng chung.
4. **4 batch hemssv** (`DlLimitManager`/`DlUlController`/`ErrorDeviceMailSend`/`LogDelete`): không có thư mục điều tra, cột 担当 trong summary = **mui**, 4 dòng đều điền "—" → **ngoài phạm vi SYP, không phải gap**. Plan coi là ngoài phạm vi trừ khi user phản đối (§8).
5. `summary_batch_migration_ja.md` bản 2026_08_13 (khác bản 2026_08_12; **đang được member sửa tiếp** — mtime 16/08 02:34) đã điền **47/47 dòng** (4 dòng hemssv = "—"). → P7 đối chiếu **43 sheet xlsx ↔ 43 dòng SYP của summary** (47 − 4 hemssv) ↔ verdict các phase; đồng thời so bản 2026_08_12 xem có phân nhánh mâu thuẫn.
6. C1–C5 phía requirement đều đã **レビュー済** (`3_requirements/app/README.md` bảng C系) → mốc đối chiếu rõ cho G8. `1100487` vừa mở `4_spec/app/` (`c02_グラフ.md`・`c03_レポート.md`) — spec mới nhất, đối chiếu kèm.

### 2.3 Bài học cũ được "gài" sẵn vào review lần này (từ `memory/00_INDEX.md`)

| Bẫy đã gặp | Áp vào đợt này |
|---|---|
| Grep phủ định thiếu dạng viết (⛔#2) / không mở file nén (⛔#13) | Mọi câu "grep X = 0" trong file member phải **chạy lại**, đủ biến thể, mở cả `.tgz` (`cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz`) |
| Finding của agent review có thể SAI (⛔#13, vụ flock) | Mọi finding [cao] phải qua vòng **kiểm-chứng-đối-kháng** trước khi vá (§4.4) |
| `emn_all` là bảng 取込 không phải 速報 (bài học new_2) | Kiểm riêng khi review `RcvHalfHourElectricPower` (G4) |
| Hệ cũ CÓ chiều gửi SFTP Xzilla (`PutLogFileCommand`) | Kiểm riêng khi review `PutLogFile` (G5) — đối chiếu new_2 §7.6 |
| `handleControlDevice` là hàm local, lõi thật `business-logic/control-device.ts` | Kiểm riêng khi review `current-eminelsmart_ControlDrOperation` (G3) |
| Path `InterfaceCode.php` phải có `PointInfinity/` | Kiểm riêng khi review `DistributeMonthlyEcoPoints` (G3) |
| 前々月 (bài học CSV 08-06) | Kiểm các mô tả kỳ dữ liệu/lịch chạy trong G1/G6 |
| Findings chỉ nằm trong chat → MẤT (vụ 78 findings 08-12) | **Cuối MỖI phase ghi findings + verdict ra đĩa ngay** (§6) |

## 3. Căn cứ đối chiếu — nguồn nào dùng cho việc gì

| Nguồn | Dùng để | Ưu tiên |
|---|---|---|
| `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` | Phán định "E-GW có cần nghiệp vụ này không" (F-GW/F-MC/F-ES/F-AD, IF-01〜24, scope 2026) | **第一優先** |
| `…/1_product/10_feature_list.md` | Cột 劣後 (lùi 2027) — phán định "cần nhưng năm nào" | Cao |
| `…/4_spec/admin/A_〜J_*.md` (nhất là `I_data_download.md`) | Khi phán định viện dẫn F-AD (vd F-AD-09 データダウンロード của G6) | Cao |
| `…/3_requirements/app/C01〜C05*.md` (レビュー済) + `…/4_spec/app/c02_グラフ.md`・`c03_レポート.md` | Mốc đối chiếu G8; và trục "app cần dữ liệu gì" cho phán định batch | Cao |
| `legacy_eminel_docs/sources/conciergesv-develop/src/Command/` + `eminelsv-develop` + `eminel_sv_lib-develop` | Xác thực nội dung điều tra hệ cũ (code là nguồn 一次) | Cao |
| `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/` (cron txt + **tgz**) | Xác thực lịch chạy, shell wrapper | Cao |
| `syp-eminelstandard-backend` (`template-dynamodb.yaml`, `src/functions/`, `src/layers/`, `src/statemachine/`) | Xác thực "e-smart có/không có" | Cao |
| `submit_folder/2026_08_06/new_2/` (3 cặp báo cáo SYP đã review kỹ + đã nộp) | Baseline đối chiếu chéo cho G3/G4/G5/G6 — lệch member ↔ new_2 là finding cần phân xử | Trung |
| `legacy_eminel_docs/docs/04_アプリ/02_アプリ仕様書/` (機能設計書 V1.0.4) + `syp-eminelstandard-app` | Đối chiếu G8 phần 現行踏襲 / ESTA踏襲 | Trung |
| `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` | Danh mục gốc 47 batch — kiểm phủ | Trung |

⚠️ Quy tắc chung: tài liệu khảo sát (`docs/eminel-smart/`, `docs/old_eminel/`) từng phát hiện 6 điểm lệch code → **code thắng tài liệu**; trích tài liệu phải kiểm lại code.

## 4. Nguyên tắc thực thi (không thương lượng)

1. **KHÔNG sửa bất cứ thứ gì trong `../sources/`** (memory: sources read-only). KHÔNG push git khi user chưa yêu cầu. KHÔNG đụng Notion (user tự đăng).
2. **KHÔNG sửa `batch_decision.xlsx`** — bản giao nộp của member, sửa nhị phân dễ hỏng định dạng. Mỗi xlsx được **convert sang 1 file `batch_decision.md` cùng thư mục** (§5b) làm bản đọc/grep/trích dẫn chính thức; phán định sai → verdict + căn cứ + **câu chữ thay thế đề xuất** vào `review_summary.md`; member/user tự quyết cập nhật xlsx. Hệ quả có chủ đích: sau P8, xlsx còn mang câu cũ trong khi summary md đã sửa — `review_summary.md` mục Giới hạn liệt kê danh sách sheet chờ member cập nhật, bảng verdict có cột 「xlsx đã cập nhật chưa」 để member tick sau bàn giao. Bảng `summary_batch_migration_ja.md` thì **được sửa trực tiếp** khi có kết luận sai.
3. **File md điều tra của member: KHÔNG sửa tại chỗ** (user chỉ đạo 08-13). File gốc giữ nguyên; bản đã sửa ghi vào **thư mục `new/` bên trong từng folder hệ batch** (vd `集計・計算系…・報告/new/legacy-batch_CalcDailyAverageData.md`), **giữ nguyên tên file**. Quy ước nội dung `new/`:
   - File có finding phải sửa → bản sửa vào `new/` (sửa = **viết lại liền mạch** ⛔#9, giữ giọng văn + cấu trúc vốn có của member). File thuộc cặp VN+JA mà chỉ 1 bên có lỗi → **vá đồng thời cả cặp** vào `new/` cho đồng bộ (22 cặp sẵn có: 17 G1 + 5 G8).
   - Bản dịch JA mới tạo (cho file VN-only) → cũng đặt vào `new/`. Quy ước tên: theo mẫu của chính member trong folder đó — file VN giữ nguyên tên, bản dịch thêm hậu tố `_ja` (vd `CreateGroupSummary.md` → `new/CreateGroupSummary_ja.md`).
   - File **không có finding** → không copy vào `new/` (bản gốc tại chỗ = bản chuẩn). Re-review sau sửa (⛔#5) chạy trên file trong `new/`.
   - **Mỗi nhóm có xlsx → 1 file `new/batch_decision.md`** (user chỉ đạo 08-16, mở rộng 17/08 cho đủ 7 nhóm): file này là mặt phẳng copy-paste duy nhất của member, đủ mọi sheet đúng thứ tự như bản gốc, meta đầu file ghi verdict từng sheet + trỏ QA-0x. Hai biến thể: **修正版** cho nhóm có ≥1 sheet **要修正** — sheet 要修正 thay câu kết luận bằng câu đã chốt qua đối kháng (replacement_ja), sheet còn lại giữ nguyên văn; **レビュー確認版** cho nhóm 0 sheet 要修正 — mọi ô trùng khít bản gốc, giá trị nằm ở meta (xác nhận "đã review, không phải sửa câu", member không phải dán gì). Ca đặc thù G3 配信・通知系: ô xlsx chỉ trỏ TÊN FILE điều tra nên không có câu để thay — câu đã sửa đưa vào dòng 「レビュー結果」 (dòng không tồn tại trong xlsx, chỉ để tra cứu/copy), hành động thật của member là thay nội dung file `current-eminelsmart_*.md`. Câu bổ sung cho sheet **妥当だが根拠不足** (nếu có soạn sẵn) đặt ở mục 付録 cuối file, nhãn 【提案・未適用】, KHÔNG lẫn vào ô sẽ dán. Bản convert trung thực ở gốc folder KHÔNG đổi (vẫn phản ánh xlsx nguyên trạng).
4. **Mọi finding phải kiểm lại trên nguồn trước khi vá** (⛔#13). Finding [cao] qua vòng đối kháng ≥2 agent, chạy theo **LÔ finding cùng gốc** (vd cụm 18 sheet G1 chung câu trần = 1 lô, 2 agent phản biện cả lô) — không nhân bản đối kháng theo từng finding trùng nhau. Sửa xong chạy lại 3 vòng thu hẹp phạm vi (⛔#5), tối đa 2 lượt; còn tồn đọng [cao] → dừng, trình user.
5. **Tách QUAN SÁT / SUY ĐOÁN** (⛔#3); trích nguyên văn tiếng Nhật trong 「」 (⛔#8); mọi khẳng định trong `review_summary.md` phải có `file:dòng`.
6. **Miễn kiểm tuân thủ TEMPLATE v4 cho file member ở CẢ vòng 2 lẫn vòng 3** — file member theo format 1-batch-1-file do user chỉ đạo 08-12 (mẫu: `legacy-batch_CalcTenMinutesSensor_ja.md`), phán định đặt ở bảng tổng hợp → khác cấu trúc TEMPLATE v4 **không phải lỗi**. Vòng 3 áp mức nhẹ: chỉ finding thật sự cản trở hiểu hoặc gây hiểu nhầm ("bỏ batch" ≠ bỏ nghiệp vụ…). Lệch lớn ghi nhận 1 dòng trong review_summary, không tính finding.
   **Trọng tâm duy nhất của review là TÍNH CHÍNH XÁC** (user chỉ đạo 08-16): phong cách **ngắn gọn, dễ hiểu** của file member là chuẩn phải GIỮ — bản sửa trong `new/` giữ độ dài + giọng văn tương đương bản gốc, chỉ thay đúng chỗ sai, **không phình file**, không bổ sung mục mới theo thói quen template SYP. Chuẩn kiểm chứng độ sâu: **truy tường tận luồng data đến TẬN BẢNG** — hệ cũ: bảng `t_xxx`/`s_xxx` (model tập trung ở `eminel_sv_lib-develop/src/Model`), e-smart: bảng DynamoDB trong `template-dynamodb.yaml` — grep xác minh, không đoán; đúng cách member đã điều tra. Độ sâu này áp cho việc KIỂM của reviewer, không phải cớ bắt member viết dài thêm.
7. Bản dịch JA tạo **sau khi** file VN đã sửa xong + qua re-review; **ngắn gọn, dễ hiểu y như các file `_ja` member đã viết** (mẫu chuẩn: các cặp VN↔JA sẵn có của G1 — dịch 1-1 trung thành, không phình, không thêm mục); **sau dịch phải qua kiểm** (§6 P8): cặp VN↔JA mới khớp heading + kết luận 1-1 (cách kiểm như đợt vá new_2 08-13), và **grep quét sạch mã nội bộ** trên toàn bộ file JA (CLD-xx, GW-xx, đường dẫn repo, 🔴 — ⛔#4).

## 5. Phương pháp review 1 batch (checklist — verifier agent nhóm G1–G7 đều theo)

```
⓪ Đọc mốc repo từ bảng đầu plan (P0 đã re-pin) — verifier KHÔNG tự fetch giữa chừng;
   trước khi tin nội dung trên đĩa: git log -1 đúng repo mình trích (⛔#14)
① Đọc file điều tra member (cả cặp VN+JA nếu có) + phán định trong batch_decision.md tương ứng
② XÁC THỰC (vòng 1): chọn ≥15 dẫn chứng/con số/trích code rải đều (file <200 dòng: kiểm TOÀN BỘ);
   mở code hệ cũ thật (Command/*.php, cron txt+tgz) đối chiếu từng token; TRUY LUỒNG DATA ĐẾN TẬN BẢNG:
   batch đọc bảng nào ghi bảng nào (hệ cũ: t_xxx/s_xxx trong eminel_sv_lib/src/Model; e-smart: bảng
   DynamoDB trong template-dynamodb.yaml) — grep xác minh từng tên bảng member nêu, không đoán
③ Chạy lại MỌI grep phủ định trong file (đủ biến thể ⛔#2, mở tgz ⛔#13)
④ Kiểm khẳng định "e-smart có/không có" trên code backend thật (template-dynamodb.yaml, src/…)
⑤ TÁI PHÁN ĐỊNH độc lập theo requirement mới: nghiệp vụ batch này ứng F-xx nào trong v1.2?
   scope 2026 hay 劣後? spec admin/app nào cần dữ liệu nó sinh ra (tra "bảng nhu cầu dữ liệu app" từ P1)?
   → so với phán định member trong sheet batch_decision
⑥ Đối chiếu chéo new_2 nếu batch thuộc nhóm SYP đã điều tra (G3/G4/G5/G6)
⑦ NHẤT QUÁN (vòng 2): nội bộ file + cặp VN↔JA + file md ↔ sheet batch_decision ↔ dòng summary
   (miễn kiểm TEMPLATE v4 — §4.6)
⑧ DỄ HIỂU (vòng 3, mức nhẹ §4.6) → xuất findings [cao/vừa/thấp] + verdict phán định
```

**Verdict phán định** — đơn vị là **dòng summary** (43 dòng = 47 − 4 hemssv; nguồn phán định: sheet `batch_decision` với G1/G2/G4–G7, câu kết luận trong md `current-eminelsmart_*` với G3; G8 không có phán định → không có verdict, chỉ có findings). 4 giá trị:

- **妥当** — đúng, đủ căn cứ.
- **妥当だが根拠不足** — câu đúng sự kiện nhưng thiếu dẫn chứng/thiếu vế.
- **要修正** — sai, kèm câu thay thế. **Quy tắc phân ranh cho ca câu-trần**: kết luận hành động (bỏ/giữ) có thể đúng nhưng câu khẳng định **sai sự kiện** (nói 「存在しません」 về thứ đã chứng minh tồn tại) → **要修正** kèm câu thay thế chính xác hoá; nguyên nhân ghi đúng nhãn (vd "chưa đối chiếu requirement mới" / "tài liệu nguồn đã đổi sau khi member viết" — ca sau không phải lỗi điều tra của member, không quy oan).
- **要業務確認** — không tự quyết được, cần hỏi mui/khách; kèm câu hỏi soạn sẵn (nếu user duyệt gửi → tách ra `submit_folder/qa/qa_<chủ-đề>_<ngày>.md` theo ⛔#12).

**Biến thể cho G8 (không phải batch)**: bỏ bước ①③④⑤⑥ dạng batch; thay bằng đối chiếu 3 tầng — requirement `C01〜C05` (レビュー済, 第一優先) → spec `4_spec/app/c02・c03` (mốc `1100487`) → 現行 V1.0.4 + code ESTA (`syp-eminelstandard-app@41ee385`) — cộng kiểm cặp ja↔vn khớp 1-1 và scope 26年/劣後 ghi đúng. Output chỉ là findings, không có verdict phán định.

## 5b. Convert `batch_decision.xlsx` → markdown (yêu cầu user 08-13)

- **Quy tắc 1-1**: mỗi thư mục hệ batch có 1 `batch_decision.xlsx` → tạo đúng 1 file **`batch_decision.md` cùng thư mục** (KHÔNG trong `new/` — là bản convert trung thực của xlsx gốc, không phải bản sửa), bất kể xlsx có bao nhiêu sheet. 7 xlsx → 7 md, tổng 43 sheet.
- **Giữ nguyên tuyệt đối nội dung**: không dịch, không viết lại, không tóm tắt, không "sửa lỗi" trong lúc convert (kể cả khi biết phán định sai — chỗ sai xử lý ở `review_summary.md`). Xuống dòng trong ô giữ nguyên (dùng `<br>` trong bảng md).
- **Cấu trúc md**: mỗi sheet = 1 mục `##` theo đúng thứ tự sheet trong xlsx, tiêu đề = tên batch trong sheet; nội dung sheet dạng bảng nhãn–giá trị đúng thứ tự hàng/cột gốc; đầu file 1 dòng meta: nguồn convert, ngày convert, số sheet.
- **Cách convert**: bằng **script Python đọc thẳng XML trong xlsx** (zipfile + sharedStrings + sheetN.xml — script dựng sẵn khi khảo sát) — máy móc 100%, không để agent gõ lại nội dung.
- **Tự review bản convert** (ngay sau khi tạo, trước khi các phase dùng nó làm nguồn trích dẫn):
  - Vòng xác thực: agent đối chiếu **từng ô** md ↔ xlsx (qua bản dump XML độc lập) — đủ sheet, đúng thứ tự, không thêm/bớt/lệch ký tự, kể cả tiếng Nhật và xuống dòng trong ô.
  - Vòng nhất quán: tên batch trong md ↔ tên sheet ↔ tên file điều tra được trỏ có tồn tại thật; bảng md render đúng (escape `|` trong ô nếu gặp).
  - Finding → sửa md (xlsx không đụng) → kiểm lại lượt nữa. Kết quả ghi `review_summary.md` mục 5.
- Vai trò kép: bản convert là **bản trích chung** cho mọi verifier (không ai phải tự parse xlsx nhị phân) và là mỏ neo `batch_decision.md:dòng` cho mọi trích dẫn phán định.

## 6. Kế hoạch theo phase

> Mỗi phase = 1 workflow đa agent. **Kết thúc MỖI phase, toàn bộ findings + verdict ghi ngay vào `review_summary.md` trên đĩa rồi mới chuyển phase** — không để findings chỉ tồn tại trong chat (bài học 78 findings 08-12). Sau mỗi phase trình findings trong chat để user liếc nhanh (không chờ duyệt từng cái — trừ 要業務確認 thì chờ user).
>
> **Chống sập trần usage (⛔#15, bổ sung 16/08 sau khi chạm trần thật)**: phase nặng chia thành KHỐI tự-hoàn-chỉnh — riêng P8 chạy **theo NHÓM** (mỗi nhóm: đối kháng bù nếu thiếu → vá vào `new/` → re-review → dịch JA → ghi review_summary + memory nhích theo → mới sang nhóm kế), KHÔNG chạy 1 lượt 40+ agent; thứ tự nhóm ưu tiên: G1 (nhiều 要修正 nhất) → G4 → G3 → G5 → G2/G7 → G8. Mỗi khối sập là chạy lại được độc lập từ script/verdict đã lưu.
> **Định lượng**: trước mỗi khối ƯỚC LƯỢNG token theo `notes/usage_budget.md` (đơn giá hiệu chỉnh từ số thật 16/08); ước lượng **> 600k token (= 20% ngân sách giả định gói Max 20x)** → chia tiếp; chạy xong ghi số thật vào ledger. Bài học chuẩn: P2 chạy 1 lượt 2,21M token ≈ 74% cửa sổ → trần sập giữa chừng.
>
> **Phụ thuộc thật giữa các phase**: P0 → P1 (bảng nhu cầu dữ liệu app) → P2 → P3; **P4・P5・P6 độc lập nhau, chạy song song sau P1**; P7 chờ đủ P1–P6; P8 cuối. (Nếu user muốn duyệt theo nhịp từng phase thì chạy tuần tự — đó là lựa chọn nhịp trình bày, không phải phụ thuộc dữ liệu; xem §8.5.)

| Phase | Phạm vi | Trọng tâm / điểm kiểm đặc thù | Ước lượng agent |
|---|---|---|---|
| **P0** | **Chốt mốc & chuẩn bị** (chạy ngay khi user duyệt): ① `git add` + **commit local** toàn bộ `2026_08_13/` làm mốc bàn giao (không push) — TRƯỚC mọi review; ② `git fetch` + `git log -1` cả 5 repo, HEAD đổi so bảng mốc → cập nhật bảng + báo user trước khi chạy tiếp; ③ kiểm kê lại số file/sheet so §2.1; ④ xác nhận với user: member đã CHỐT bàn giao/freeze chưa; ⑤ convert 7 xlsx → 7 `batch_decision.md` + tự review bản convert (§5b). Nếu giữa chừng phát hiện file đổi so commit mốc → dừng phase, báo user | Trung thực từng ô, đủ 43 sheet; escape ký tự vỡ bảng | script + ~7 agent đối chiếu |
| **P1** | **G8 mobile app C1–C5** (5 cặp ja+vn) — chạy TRƯỚC các nhóm batch + xuất **"bảng nhu cầu dữ liệu app"** dùng chung: C01 グラフ cần chuỗi thời gian gì・C02 レポート có mục so sánh 他世帯 không・C03〜C05 cần gì, kèm `file:dòng` từ requirement レビュー済 + spec `4_spec/app` mốc pin | Checklist biến thể G8 (§5); kiểm cặp ja↔vn; scope 26年/劣後 | 5 verifier + 1 tổng hợp bảng nhu cầu + ~2 đối kháng |
| **P2** | **G1 集計・計算系** — 19 batch, 37 md, 19 sheet | **18 câu trần** vs 3 bảng tích luỹ `DeviceAccumulatedHistoryTable`/`DeviceDailyUsageHistoryTable`/`DeviceMonthlyUsageHistoryTable` + 5 batch import Rinnai/Noritz; trục nhu cầu dữ liệu app (bảng P1); cặp VN↔JA khớp?; 2 file chỉ JA (`CalcTenMinutesSensor/Energy`) là mẫu của member khác — 2 dòng summary có sẵn từ trước, đối chiếu | 19 verifier + đối kháng theo lô (~4 lô) + 1 tổng hợp |
| **P3** | **G2 データ管理系** 8 batch + **G7 EminelSV** 2 batch | TTL/PITR thay batch xoá — đúng cho bảng nào (kiểm TTL từng bảng); `RankingCreation` vs A03 ポイント/A04 バッジ・ランク; `CreateGroupSummary` "so sánh nhóm chưa được port" vs C02 レポート (tra bảng P1) — nếu đúng là **gap phải nêu to**, không phải lý do bỏ | 10 verifier + ~3 đối kháng + 1 tổng hợp |
| **P4** | **G5 監視・ログ系** 3 + **G4 Xzilla** 3 (song song được với P5/P6) | `PutLogFile` ↔ new_2 §7.6 + ⛔#13 flock; 3 câu trần G4 vs nền nhận SFTP→S3→DynamoDB; `RcvHalfHourElectricPower` vs bài học `emn_all`; `SendAlertLogMail` câu 「今回のセッションでKita Gas向けに拡張された仕組み」— kiểm nghĩa | 6 verifier + ~3 đối kháng + 1 tổng hợp |
| **P5** | **G3 配信・通知系** — 4 legacy + 4 current-eminelsmart, 4 sheet (song song được) | Đối chiếu chéo new_2 (đã review kỹ nhất); kết luận chính thức của member nằm trong 4 md current-eminelsmart (xlsx chỉ trỏ file) — xác định câu kết luận trước khi phán xét; bẫy `handleControlDevice`, path `PointInfinity/` | 8 verifier + ~3 đối kháng + 1 tổng hợp |
| **P6** | **G6 CSV/ZIP** — 4 sheet phán định (4 md đề xuất skip §8.3) (song song được) | Verdict 「F-AD-09で代替」+ TTL/PITR: khớp new_2 + `I_data_download.md`? Spec [I] còn giữ 4 bảng batch #5–#7 làm loại download nội bộ (phát hiện 08-12) — phán định member có phủ ý này không | 2 verifier + 1 đối kháng |
| **P7** | **Tổng đối chiếu 3 nơi ghi phán định**: 43 sheet (qua `batch_decision.md`) ↔ 43 dòng SYP trong summary (47 − 4 hemssv) ↔ verdict P2–P6; so bản summary 2026_08_12 xem có phân nhánh; dòng SYP (11 batch cũ) có bị member sửa đè không | Bảng nào lệch bảng nào | 2 agent |
| **P8** | **Sửa + dịch + chốt**: bản sửa vào `new/` từng folder (§4.3 — file gốc không đụng; cặp VN+JA vá đồng thời cả cặp); **tạo `new/batch_decision.md` cho cả 7 nhóm có xlsx** — 修正版 với nhóm có sheet 要修正, レビュー確認版 với nhóm không có (§4.3); re-review thu hẹp trên `new/` (⛔#5, max 2 lượt); sửa dòng sai trong summary md; dịch JA 24 file VN-only vào `new/` + **kiểm sau dịch** (khớp cặp 1-1 + quét mã nội bộ ⛔#4); hoàn thiện `review_summary.md`; **commit local lần 2** (cặp commit trước/sau cho phép `git diff` chứng minh mọi thay đổi); cập nhật **mục 4 SKILL.md của `3-step-review`** (đối tượng, mốc, trạng thái, điểm kiểm đặc thù mới) rồi chốt phiên `/update-memory` | — | ~10 fixer + ~24 translator + ~8 re-review/kiểm dịch |

Tổng ước lượng: **~115 lượt agent** qua 9 workflow. Nếu user muốn gọn: bỏ đối kháng cho finding [vừa/thấp] (giữ [cao]) — giảm ~15%.

## 7. Cấu trúc `review_summary.md` (định trước — các phase điền thẳng vào file này ngay khi xong)

```
1. Tổng quan: phạm vi, mốc repo, thống kê (số file review, findings theo mức, phán định theo verdict)
2. Bảng verdict 43 phán định (đơn vị = dòng summary, không gồm G8/hemssv):
   nhóm | batch | phán định member (nguyên văn, trích batch_decision.md:dòng) | verdict | căn cứ (file:dòng)
   | xlsx đã cập nhật theo verdict chưa (member tick sau bàn giao)
3. Chi tiết theo nhóm (G1→G8), mỗi file:
   - findings đánh số [cao/vừa/thấp]: vị trí (file gốc:dòng) | sai gì (trích nguyên văn) | nguyên nhân
     (vd: grep thiếu dạng viết / đọc nhầm bảng / chưa đối chiếu requirement mới / nguồn đã đổi sau khi
     member viết) | đối chiếu (source repo + file + dòng) | đã sửa thế nào (trích câu sau sửa + đường dẫn
     bản sửa trong new/) hoặc lý do không sửa
4. Các điểm 要業務確認 → câu hỏi soạn sẵn (đích: PM mui / 業務側) — user duyệt thì tách ra
   submit_folder/qa/qa_<chủ-đề>_<YYYYMMDD>.md theo ⛔#12
5. Kết quả convert xlsx→md: 7 file batch_decision.md + kết quả tự review đối chiếu
6. Danh sách file đã dịch JA + kết quả kiểm sau dịch + ghi chú thuật ngữ
7. Giới hạn của đợt review: cái gì chưa kiểm được vì sao + danh sách sheet xlsx còn mang câu cũ
   chờ member cập nhật theo verdict
```

## 8. Điểm cần user quyết khi duyệt plan

1. **Commit git local mốc bàn giao ngay đầu P0** (trước mọi review, không push) + commit lần 2 sau P8 — OK? *(Mặc định: có)*
2. **Không sửa xlsx** của member; phán định sai ghi verdict trong review_summary (+ sửa summary md); `batch_decision.md` convert đặt cạnh xlsx ở gốc folder, không trong `new/` — OK? *(Mặc định: như §4.2/§5b)*
3. **4 file md G6 identical (diff=0) với bản SYP đã review + nộp 2026_08_12** → đề xuất skip review nội dung, chỉ review 4 sheet phán định — OK? *(Mặc định: skip)*
4. **Member đã ngừng sửa file trong `2026_08_13/` chưa** — cần freeze trong thời gian review không? (summary vừa được sửa 16/08 02:34; file đổi giữa chừng làm trôi mọi finding `file:dòng`) *(Cần user trả lời)*
5. **Deadline nộp kết quả đợt review?** — quyết chạy P4/P5/P6 song song (nhanh) hay tuần tự để user duyệt theo nhịp từng phase; và chọn bản đầy đủ hay bản gọn (~115 vs ~95 lượt agent). *(Cần user trả lời)*
6. Thông báo mặc định (phản đối thì nói): 4 batch hemssv 担当 mui — ngoài phạm vi, không điều tra; sau đợt này đề xuất cập nhật CLAUDE.md mục SOURCES (repo app thực tế là git `syp-eminelstandard-app@syp-dev`, không phải snapshot).
