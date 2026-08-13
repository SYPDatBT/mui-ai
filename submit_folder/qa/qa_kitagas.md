# Bảng câu hỏi gửi 北海道ガス — E-GW

> **Cách dùng**: mỗi câu gồm **bản tiếng Việt** (để nội bộ hiểu) và ngay bên dưới là **bản tiếng Nhật** (để copy dán vào Notion gửi khách).
> Phần trong khung 🇯🇵 là phần **paste được nguyên vẹn**.

| | |
|---|---|
| Ngày lập | 2026-08-03 |
| Đối chiếu repo | `eminel_gw_project` bản ngày 2026-08-03 |
| Số câu | 8 chính + 4 dự phòng |
| Đường đi | SYP → PM mui Lab → 北ガス *(SYP không gửi trực tiếp)* |
| Diễn biến | 2026-08-03: bắt đầu đăng lên **QAデータベース Notion** — câu 1 đã có trả lời tạm của mui (回答中/*đang trả lời* — kiểm tra 2026-08-04, xem ghi chú tại câu 1) |
| Nguồn phân tích | [onboarding_guide.md](onboarding_guide.md) Phụ lục B và C |

**Quy ước tham chiếu**: phần **tiếng Việt** (nội bộ) dẫn đường dẫn repo bắt đầu từ `eminel_gw_project/`; phần **tiếng Nhật** (paste gửi khách) chỉ dùng tên tài liệu mà hai bên cùng biết (統合要件定義書v1.2, 業務フロー資料, 機能一覧…) — **không** chứa đường dẫn repo nội bộ, ID quản lý nội bộ (CLD-xx, GW-xx…) hay ký hiệu trạng thái (🔴…).

**Thứ tự ưu tiên**: câu 1–4 chặn công việc đang chạy, cần trả lời sớm nhất. Câu 5 tuy thuộc phạm vi 2027 nhưng ràng buộc thiết kế firmware của 2026.

---
---

## Câu 1 — Huy hiệu / xếp hạng thuộc phạm vi năm nào?

> **Diễn biến (2026-08-03)**: khối 🇯🇵 dưới đây đã được đăng lên QAデータベース Notion (trang 「バッジ・ランクは2026年度対応スコープでしょうか」). Trả lời tạm của mui — masao takahashi, 2026-08-03, trạng thái **回答中** (*đang trả lời, chưa chốt* — kiểm tra 2026-08-04): 「今の所、2026年スコープ外です」 (*hiện tại nằm ngoài scope 2026* — nghiêng về phía 劣後/*được lùi lại sau*). Chưa phải xác nhận cuối, A04 trên repo chưa được sửa. Chi tiết: [onboarding_guide.md](onboarding_guide.md) — Chương 6 và Phụ lục B.1.

**Bối cảnh điều tra**

Khi đối chiếu chéo ba tài liệu về phạm vi phát triển năm 2026, chúng tôi phát hiện nội dung không khớp nhau đối với hạng mục huy hiệu và xếp hạng:

- Nhật ký quyết định (10/06/2026) ghi huy hiệu thuộc nhóm **được lùi lại**
- Bảng chức năng cũng đánh dấu **✅ được lùi** ở cột 劣後
- Nhưng tài liệu yêu cầu ứng dụng lại viết **toàn bộ** hạng mục này vào mục 「26年対応スコープ」, và mục 「それ以降スコープ」 ghi 「なし」

File yêu cầu ứng dụng này mới được tách ra từ mục "Điểm thưởng" vào ngày 27/07/2026, nên chúng tôi nghi ngờ đây có thể là sai sót khi tách file, chứ không phải thay đổi phạm vi.

**Điểm thắc mắc**

Hạng mục huy hiệu và xếp hạng thuộc phạm vi bắt buộc đến cuối tháng 12/2026, hay được lùi sang sau tháng 4/2027?

Nếu là phạm vi bắt buộc năm nay, khối lượng công việc ở phía ứng dụng, máy chủ và màn hình quản trị (chức năng H) đều cần được tính lại.

**Tài liệu tham chiếu**

- `eminel_gw_project/docs/eminel/3_requirements/app/A04_badge_rank.md` — mục 「要件案：26年対応スコープ」 và 「要件案：それ以降スコープ」
- `eminel_gw_project/docs/eminel/1_product/10_feature_list.md` — cột 「劣後」, dòng 「バッジ管理」
- `eminel_gw_project/docs/eminel/2_management/22_decisions.md` — dòng ngày 2026-06-10

---

### 🇯🇵 【JP】バッジ・ランクは26年対応スコープ（2026年12月末まで）に含まれますでしょうか

**調査の背景**

2026年対応スコープについて3つの資料を突き合わせたところ、バッジ・ランクの扱いに差異が見られました。

- 意思決定ログ（2026-06-10）では、バッジは**劣後**扱いと記載されています
- 機能一覧の「劣後」列でも**✅（劣後可能）**となっています
- 一方、モバイルアプリ要件定義書では本項目が**すべて**「要件案：26年対応スコープ」に記載されており、「要件案：それ以降スコープ」は「なし」となっています

当該要件ファイルは2026-07-27に「ポイント」から分離して新設されたものであるため、分離時の記載漏れの可能性も考えられますが、こちらでは判断いたしかねます。

**確認したい点**

バッジ・ランクは **2026年12月末までの必須スコープ**でしょうか。それとも **2027年4月以降の劣後機能**でしょうか。

2026年の必須スコープである場合、アプリ・サーバー・管理画面（H バッジ設定）それぞれの工数の見直しが必要となります。

**参照資料**

- モバイルアプリ要件定義書「A4 バッジ・ランク」—「要件案：26年対応スコープ」「要件案：それ以降スコープ」
- 機能一覧（見積v0.3ベース）—「劣後」列、「バッジ管理」行
- 定例議事録（Notion 6/3・6/15・6/19）— 決定事項（決定日 2026-06-10）

---
---

## Câu 2 — Liên kết điểm thưởng thuộc phạm vi năm nào?

**Bối cảnh điều tra**

Tương tự câu 1, hạng mục liên kết điểm thưởng cũng có ba tài liệu ghi khác nhau:

- Nhật ký quyết định (10/06/2026) ghi liên kết điểm thưởng là **bắt buộc** trong giai đoạn 1
- Bảng chức năng lại đánh dấu **✅ được lùi** cho cả "quản lý điểm" và "liên kết PointInfinity"
- Tài liệu yêu cầu ứng dụng viết vào phạm vi **năm 2026**

Bảng chức năng lấy nguồn từ bảng báo giá phiên bản v0.3 ngày 13/05/2026 — tức là **trước** quyết định ngày 10/06/2026. Do đó chúng tôi cho rằng bảng chức năng có thể là tài liệu đã cũ, nhưng cần được xác nhận.

**Điểm thắc mắc**

Liên kết điểm thưởng (bao gồm quản lý điểm và liên kết với PointInfinity) thuộc phạm vi bắt buộc năm 2026 hay được lùi sang 2027?

Nếu là bắt buộc năm nay, khối lượng phía máy chủ tăng thêm khoảng **2 người-tháng** so với bảng chức năng hiện tại.

Ngoài ra xin xác nhận: hạng mục tư vấn tiết kiệm năng lượng ở phía ứng dụng cũng có tình trạng ghi khác nhau tương tự.

**Tài liệu tham chiếu**

- `eminel_gw_project/docs/eminel/2_management/22_decisions.md` — dòng ngày 2026-06-10
- `eminel_gw_project/docs/eminel/1_product/10_feature_list.md` — dòng 「ポイント管理」「PI連携(PointInfinity)」「ポイント・省エネアドバイス」
- `eminel_gw_project/docs/eminel/3_requirements/app/A03_point.md` · `C05_energy_advice.md`

---

### 🇯🇵 【JP】ポイント連携は26年対応スコープ（2026年12月末まで）に含まれますでしょうか

**調査の背景**

設問1と同様に、ポイント連携についても3つの資料で記載が異なっております。

- 意思決定ログ（2026-06-10）では、ポイント連携は第一段階の**必須**と記載されています
- 機能一覧では「ポイント管理」「PI連携(PointInfinity)」ともに**✅（劣後可能）**となっています
- モバイルアプリ要件定義書では**2026年対応スコープ**に記載されています

機能一覧の出典は見積書 v0.3（2026-05-13）であり、意思決定（2026-06-10）より**前**の資料です。そのため機能一覧側が旧情報である可能性が考えられますが、確証が得られておりません。

**確認したい点**

ポイント連携（ポイント管理およびPointInfinity連携を含む）は、**2026年の必須スコープ**でしょうか。それとも**2027年以降の劣後機能**でしょうか。

2026年必須である場合、現行の機能一覧に対しサーバー側で約**2人月**の増加となります。

あわせて、アプリ側の省エネアドバイスについても同様の記載差異がございますので、ご確認いただけますでしょうか。

**参照資料**

- 定例議事録（Notion 6/3・6/15・6/19）— 決定事項（決定日 2026-06-10）
- 機能一覧（見積v0.3ベース）—「ポイント管理」「PI連携(PointInfinity)」「ポイント・省エネアドバイス」各行
- モバイルアプリ要件定義書「A3 ポイント」「C5 省エネアドバイス」

---
---

## Câu 3 — Thông báo trông nom có thực hiện hay không?

**Bối cảnh điều tra**

Hạng mục thông báo trông nom (F-ES-05) hiện đang được ghi nhận là **chưa quyết định có thực hiện hay không** trong danh sách vấn đề đang mở (CLD-05, trạng thái 🔴 chưa động), với ghi chú chênh lệch 0 đến 1 người-tháng.

Tuy nhiên:
- Bảng chức năng đã ghi 0.75 người-tháng và **không** đánh dấu được lùi
- Tài liệu yêu cầu ứng dụng (D4) đã viết đầy đủ nội dung vào phạm vi năm 2026

Điểm chúng tôi lo ngại: theo tài liệu luồng nghiệp vụ, **logic phán đoán của thông báo trông nom nằm ở phía thiết bị gateway**, không phải ở máy chủ. Cụ thể, gateway lưu khung giờ được phép thông báo và tự phán đoán chuyển đổi trạng thái phát hiện người.

Do đó, nếu quyết định "không thực hiện" đến muộn, phần firmware đã phát triển sẽ trở thành lãng phí.

**Điểm thắc mắc**

Chúng tôi hiểu rằng thông báo trông nom (ただいま通知 / 見守り通知) **sẽ được thực hiện** trong dự án này — cách hiểu như vậy có đúng không?

Nếu đúng, xin cho biết thời điểm dự kiến xác nhận chính thức, vì hạng mục này ảnh hưởng tới thiết kế firmware chứ không chỉ phía máy chủ và ứng dụng.

> *Ghi chú nội bộ (không gửi khách): câu tiếng Nhật cố ý hỏi theo hướng xác nhận "có làm" — vì bảng chức năng đã tính 0.75人月 và requirement D4 đã viết vào phạm vi 2026 — để thúc khách chốt sớm thay vì mở lại tranh luận từ đầu.*

**Tài liệu tham chiếu**

- `eminel_gw_project/docs/eminel/2_management/20_open_issues.md` — mục 「CLD-05 見守り通知（F-ES-05）の実装要否」
- `eminel_gw_project/docs/eminel/1_product/10_feature_list.md` — dòng 「見守り通知」
- `eminel_gw_project/docs/eminel/3_requirements/app/D04_mimamori.md`
- `eminel_gw_project/docs/eminel/1_product/11_business_process/readme.md` — mục 「02-5. ただいま通知（Slide 29）」「02-5. 見守り通知（Slide 30）」

---

### 🇯🇵 【JP】見守り通知の実装要否についてご確認をお願いいたします

**調査の背景**

見守り通知（F-ES-05）につきまして、弊社の課題管理上は**実装要否が未確定**の項目として整理されており、実施可否により0〜1人月の工数変動が見込まれます。

一方で、

- 機能一覧では 0.75人月が計上され、劣後マークは**付いておりません**
- モバイルアプリ要件定義書（D4 見守り通知）では2026年対応スコープとして内容が記載されております

こちらで懸念しておりますのは、業務フロー資料によれば、**見守り通知の判定ロジックはGW側に配置される**設計となっている点です。具体的には、通知時間をGWが保持し、人感検知の状態遷移の判定もGW側で行う流れとなっております。

そのため、「実施しない」というご判断が遅れた場合、開発済みのファームウェア部分が無駄になる可能性がございます。

**確認したい点**

見守り通知（ただいま通知／見守り通知）は本プロジェクトで**実装する**という理解でよろしいでしょうか。

実装する場合、正式にご確認いただける時期の目安をご教示いただけますでしょうか。本項目はサーバー・アプリだけでなく**ファームウェアの設計にも影響する**ため、早期の確定をお願いしたく存じます。

**参照資料**

- 機能一覧（見積v0.3ベース）—「見守り通知」行
- モバイルアプリ要件定義書「D4 見守り通知」
- 業務フロー資料 —「02-5. ただいま通知（Slide 29）」「02-5. 見守り通知（Slide 30）」

---
---

## Câu 4 — Điều kiện phân loại lỗi nghiêm trọng / lỗi nhẹ

**Bối cảnh điều tra**

Trong đặc tả chức năng màn hình quản trị E-GW, mục phân loại lỗi (C-B-12) hiện ghi điều kiện là **T.B.D** cho cả hai loại: nghiêm trọng và nhẹ.

Trong mục vấn đề chưa rõ của cùng tài liệu có ghi lại điều kiện phỏng đoán theo mã nhà sản xuất và mã lỗi của hệ thống hiện hành, nhưng đây chỉ là suy đoán, chưa được xác nhận.

Vấn đề: **màn hình dashboard cũng tham chiếu trực tiếp** sang quy tắc này (mục D-C-08 ghi "phân loại và phán đoán lỗi thiết bị tuân theo C-B-12"). Đồng thời, danh sách E-GW cũng có cột hiển thị tình trạng phát sinh lỗi theo phân loại này.

Do đó, một hạng mục chưa quyết đang khiến **hai màn hình mới hoàn toàn** của E-GW không thể hoàn thiện đặc tả.

**Điểm thắc mắc**

Xin cho biết điều kiện cụ thể để phân loại lỗi thành **重篤** (nghiêm trọng) và **軽微** (nhẹ).

Cụ thể, chúng tôi mong được xác nhận:
1. Danh sách mã nhà sản xuất và mã lỗi tương ứng với từng mức
2. Cách xử lý đối với lỗi của エコジョーズ (hệ thống hiện hành dường như không phân biệt mức độ)
3. Trường hợp thiết bị mới chưa có trong danh sách thì phân loại thế nào

**Tài liệu tham chiếu**

- `eminel_gw_project/docs/eminel/4_spec/admin/C_egw_management.md` — mục 「詳細」項目 C-B-12, và mục 「明確な未決事項」項目 3
- `eminel_gw_project/docs/eminel/4_spec/admin/D_dashboard.md` — mục 「詳細」項目 D-C-08

---

### 🇯🇵 【JP】エラー種別（重篤／軽微）の判定条件についてご教示ください

**調査の背景**

E-GW管理画面の機能仕様におきまして、エラー種別の判定条件（C-B-12）が重篤・軽微ともに **T.B.D** となっております。

同資料の「明確な未決事項」には、現行システムのメーカーコード・エラーコードに基づく推定条件が記載されておりますが、あくまで推定であり確認が取れておりません。

課題としましては、**ダッシュボード側も本ルールを直接参照している**点がございます（D-C-08「機器エラーの種別および判定はC-B-12に従う」）。またE-GW一覧にも本分類に基づく「エラー発生有無」列がございます。

そのため、本項目が未確定であることにより、**E-GW新規の2画面**（C E-GW管理／D ダッシュボード）の仕様が確定できない状況となっております。

**確認したい点**

エラー種別を **重篤** と **軽微** に振り分ける具体的な条件をご教示いただけますでしょうか。

特に以下の3点についてご確認をお願いいたします。

1. 各区分に該当するメーカーコード・エラーコードの一覧
2. エコジョーズのエラーの扱い（現行では重篤・軽微を区別していないように見受けられます）
3. 一覧に存在しない新規機器のエラーが発生した場合の分類方法

**参照資料**

- 管理画面 機能仕様「C E-GW管理」—「詳細」C-B-12、「明確な未決事項」3
- 管理画面 機能仕様「D ダッシュボード」—「詳細」D-C-08

---
---

## Câu 5 — Phương thức kết thúc điều khiển DR

**Bối cảnh điều tra**

Trong tài liệu luồng nghiệp vụ, phần điều khiển thiết bị DR có **hai phương án** được trình bày song song mà chưa chọn:

| | Phương án A (Slide 40) | Phương án B (Slide 41) |
|---|---|---|
| Cách kết thúc | Máy chủ phát lệnh kết thúc đúng giờ | Gửi kèm giờ kết thúc ngay lúc bắt đầu, gateway tự kết thúc |
| Lo ngại được ghi | Nếu có sự cố mạng thì không gửi được lệnh kết thúc | Gateway phải lưu trạng thái — phía phát triển mong muốn tránh |

Chúng tôi hiểu rằng DR đã được xếp vào nhóm lùi sang sau tháng 4/2027.

Tuy nhiên, điểm chúng tôi muốn nêu là: quyết định **"gateway có phải lưu giữ trạng thái hay không"** là một quyết định về kiến trúc firmware, mà firmware lại được phát triển trong **năm 2026**. Nếu quyết định này đến sau khi firmware đã ổn định, sẽ phát sinh chi phí sửa lại.

**Điểm thắc mắc**

Xin cho biết phương án nào được chọn cho việc kết thúc DR.

Nếu chưa thể quyết định ngay, xin cho biết liệu có thể xác nhận trước một điểm hẹp hơn: **gateway có được phép lưu giữ trạng thái đang thực hiện DR hay không?** Chỉ cần điểm này được xác nhận, thiết kế firmware năm 2026 có thể tiến hành mà không phải làm lại.

Ngoài ra xin xác nhận quy tắc đã ghi trong tài liệu: khi khởi động lại gateway thì bỏ lệnh DR và quay về điều khiển nhiệt độ phòng thông thường — cách hiểu này có đúng không?

> *Ghi chú nội bộ (không gửi khách): "GW có giữ trạng thái hay không" là quyết định kiến trúc firmware thuộc thẩm quyền mui — Phụ lục C.5 của onboarding_guide ghi người cần hỏi là **kihara + 北ガス**, trong đó kihara là lead GW HW/FW của mui Lab. Nên chốt nội bộ với kihara trước (giữ trạng thái có khả thi không, chi phí bao nhiêu), rồi gửi khách kèm khuyến nghị của mui thay vì hỏi mở hoàn toàn.*

**Tài liệu tham chiếu**

- `eminel_gw_project/docs/eminel/1_product/11_business_process/readme.md` — mục 「01-3. 機器制御DR（サーバーから開始・終了時に指令）（Slide 40）」và 「01-3'. 機器制御DR（サーバーから開始時に終了時刻も送信）（Slide 41）」, kèm ghi chú 「※【懸念点】」
- `eminel_gw_project/docs/eminel/3_requirements/app/B05_dr.md`

---

### 🇯🇵 【JP】DR終了指令の方式についてご確認をお願いいたします

**調査の背景**

業務フロー資料の機器制御DRにつきまして、**2つの方式**が併記されたまま決定に至っていないと理解しております。

| | 案A（Slide 40） | 案B（Slide 41） |
|---|---|---|
| 終了方法 | サーバーから終了時刻に終了指令を送信 | 開始時に終了時刻も併せて送信し、GW側で終了 |
| 記載されている懸念 | ネットワーク障害時に終了指令を送信できない | GW側で状態を保存する必要がある（GW側で保存はしたくない旨の記載あり） |

DRにつきましては2027年4月以降の劣後機能と整理されていることは承知しております。

その上でご相談したいのは、**「GWが状態を保持するか否か」はファームウェアのアーキテクチャに関わる判断**であり、当該ファームウェアは**2026年内**に開発される点です。ファームウェアが安定した後にこの判断が確定した場合、手戻りが発生する可能性がございます。

**確認したい点**

DR終了指令の方式について、どちらの案を採用されるかご教示いただけますでしょうか。

即時のご判断が難しい場合、より限定した論点として、**「GWがDR実施中の状態を保持することを許容するか否か」**のみ先行してご確認いただくことは可能でしょうか。この点さえ確定すれば、2026年のファームウェア設計を手戻りなく進めることができます。

あわせて、資料に記載の「GWを再起動した場合はDR指令を受けず通常の室温制御に戻る」という想定仕様について、この理解で相違ないかご確認をお願いいたします。

**参照資料**

- 業務フロー資料 —「01-3. 機器制御DR（サーバーから開始・終了時に指令）（Slide 40）」「01-3'. 機器制御DR（サーバーから開始時に終了時刻も送信）（Slide 41）」および「※【懸念点】」注記
- モバイルアプリ要件定義書「B5 DR」

---
---

## Câu 6 — Gán cảm biến với thiết bị ở nhà có nhiều mạch sưởi

**Bối cảnh điều tra**

Tài liệu yêu cầu quy định nhà **2 mạch sưởi là bắt buộc phải hỗ trợ**, từ 3 mạch trở lên là T.B.D. Đồng thời quy định mạch thứ nhất dùng lớp thiết bị nguồn nhiệt nước lạnh/nóng (冷温水熱源機クラス), mạch thứ hai dùng lớp sàn sưởi (床暖房クラス).

Tuy nhiên, trong luồng onboarding có ghi chú "cần bàn thêm": khi đăng ký cảm biến, phải xác định cảm biến đó thuộc phòng nào và gắn với thiết bị nào trong phòng đó.

Ngoài ra, phía chúng tôi ghi nhận một ràng buộc kỹ thuật: bộ điều khiển Wi-Fi chỉ tạo được **một** đối tượng thuộc lớp nguồn nhiệt nước lạnh/nóng (冷温水熱源機クラス), nên mạch thứ hai buộc phải gán sang lớp sàn sưởi. Điều này có thể dẫn đến việc giao diện phải cho người dùng tự chỉ định mạch nào là mạch nào.

**Điểm thắc mắc**

1. Ở nhà có 2 mạch sưởi, việc gán cảm biến với thiết bị được thực hiện như thế nào? Người dùng tự chọn trong quá trình cài đặt ban đầu, hay hệ thống tự nhận biết?
2. Trường hợp mạch thứ hai được gán vào lớp sàn sưởi trong khi thực tế không phải sàn sưởi (ví dụ lò sưởi panel ở tầng 2), thì hiển thị cho người dùng nên như thế nào?
3. Nhà có 3 mạch trở lên đang là T.B.D — xin cho biết tỷ lệ ước tính trong tập khách hàng, để chúng tôi cân nhắc mức độ ưu tiên.

**Tài liệu tham chiếu**

- `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` — mục 「8-1. E-GW機能詳細」→ F-GW-05 「複数系統対応」
- `eminel_gw_project/docs/eminel/1_product/11_business_process/readme.md` — mục 「01. 通常系 / EMINEL契約の有無（3/3）（Slide 6）」, ghi chú 「※要検討【多系統の機器制御がある場合】」
- `eminel_gw_project/docs/eminel/3_requirements/app/B02_heating_control.md` — mục 「懸念」

---

### 🇯🇵 【JP】多系統宅におけるセンサーと機器の紐付けについてご教示ください

**調査の背景**

統合要件定義書では、**2系統までを必須**とし、3系統以降はT.B.Dと定義されております。また、1系統目は冷温水熱源機クラス、2系統目は床暖房クラスを使用して制御する旨が記載されております。

一方、業務フロー（オンボーディング）には「※要検討【多系統の機器制御がある場合】：センサー登録時にどの部屋のセンサーか、そのセンサーがある部屋の機器との紐付けを行う必要があるため要検討」との注記がございます。

また弊社側の技術検討において、Wi-Fiリモコンは冷温水熱源機クラスのインスタンスを**1つしか生成しない**ため、2系統目は床暖房クラスに割り当てる必要があるという制約を確認しております。この制約により、UI上でユーザーに系統の割り当てを行っていただく必要が生じる可能性がございます。

**確認したい点**

1. 2系統宅において、センサーと機器の紐付けはどのように行う想定でしょうか。初期設定時にユーザーが選択する運用でしょうか、それともシステムが自動判別する想定でしょうか。
2. 2系統目を床暖房クラスに割り当てた場合、実態が床暖房でないケース（例：2階のパネルヒーター）について、ユーザーへの表示はどのようにすべきでしょうか。
3. 3系統以降はT.B.Dとされておりますが、お客さま全体に占めるおおよその割合をご教示いただけますでしょうか。対応の優先度判断の材料とさせていただきたく存じます。

**参照資料**

- 統合要件定義書 v1.2 —「8-1. E-GW機能詳細」F-GW-05「複数系統対応」
- 業務フロー資料 —「01. 通常系 / EMINEL契約の有無（3/3）（Slide 6）」の「※要検討【多系統の機器制御がある場合】」注記
- モバイルアプリ要件定義書「B2 暖房自動制御」—「懸念」

---
---

## Câu 7 — Còn cần logic tách gas nước nóng và gas sưởi không?

**Bối cảnh điều tra**

Ở hệ thống EMINEL hiện hành, do đồng hồ gas chỉ đo được tổng lượng gas, hệ thống phải **suy ra** phần dùng cho đun nước nóng và phần dùng cho sưởi, bằng cách đối chiếu lượng gas tích luỹ 10 phút với số lần ra lệnh sưởi và một ngưỡng nhất định.

Ở hệ thống mới, danh sách interface có mục IF-23 dành cho đồng hồ gas thông minh, nhưng cả phương thức truyền lẫn nội dung đều đang ghi **T.B.D**.

Hai kịch bản dẫn tới hai hướng phát triển hoàn toàn khác nhau:

- Nếu **đo trực tiếp được** phần gas dùng cho sưởi → có thể bỏ logic suy luận
- Nếu **vẫn phải suy luận** → cần được cung cấp đặc tả thuật toán của hệ thống hiện hành

Đây là hạng mục nền tảng vì **toàn bộ biểu đồ lượng gas và các report liên quan đến sưởi** đều dựa trên con số này.

**Điểm thắc mắc**

1. Trong hệ thống E-GW, phần gas dùng cho sưởi có được đo trực tiếp không? Hay vẫn cần suy luận như hệ thống hiện hành?
2. Nếu vẫn cần suy luận, xin xác nhận tài liệu `20170728_給湯暖房分離ロジック_1.pptx` (đã nhận trong bộ tài liệu hiện hành) là bản mới nhất và đầy đủ; nếu có bản cập nhật hoặc tài liệu chi tiết hơn, xin được cung cấp thêm.
3. IF-23 (đồng hồ gas thông minh) hiện đang T.B.D — xin cho biết có nằm trong phạm vi năm 2026 hay không.

**Tài liệu tham chiếu**

- `eminel_gw_project/docs/old_eminel/01_overview.md` — mục 「02_データ生成・アプリ通信（旧コンシェルジュ踏襲）」, phần 「給湯・暖房分離ロジック」
- `eminel_gw_project/docs/old_eminel/00_sources.md` — mục 「02_詳細設計 / 02_データ生成・アプリ通信」, mục 「20170728_給湯暖房分離ロジック_1.pptx」
- `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` — mục 「4-1. インタフェース一覧」, dòng IF-23

---

### 🇯🇵 【JP】給湯・暖房分離ロジックの要否についてご確認をお願いいたします

**調査の背景**

現行EMINELでは、ガスメーターが総使用量のみを計測するため、10分積算ガス消費量を暖房指令回数と閾値により給湯分・暖房分に**按分（推定）**する処理が実装されていると理解しております。

新システムでは、インタフェース一覧に IF-23（ガススマートメーターI/F）が定義されておりますが、通信方式・通信内容ともに **T.B.D** となっております。

以下の2つのケースで開発方針が大きく異なります。

- 暖房分のガス使用量を**直接計測できる**場合 → 按分ロジックは不要となります
- **引き続き按分が必要な**場合 → 現行の算出ロジックの詳細仕様をご提供いただく必要がございます

本項目は、**ガス消費量グラフおよび暖房関連の各種レポート**の基礎となる数値であるため、早期の確認をお願いしたく存じます。

**確認したい点**

1. E-GWにおいて、暖房分のガス使用量は直接計測可能でしょうか。それとも現行同様に按分が必要でしょうか。
2. 按分が必要な場合、既にご提供いただいている資料『20170728_給湯暖房分離ロジック_1.pptx』が最新かつ完全な仕様であるという理解でよろしいでしょうか。改訂版やより詳細な資料がございましたら、ご提供をお願いいたします。
3. IF-23（ガススマートメーター）は現在T.B.Dとなっておりますが、2026年対応スコープに含まれるかご教示ください。

**参照資料**

- 現行EMINEL設計資料 —「給湯・暖房分離ロジック」（『20170728_給湯暖房分離ロジック_1.pptx』）
- 統合要件定義書 v1.2 —「4-1. インタフェース一覧」IF-23 行

---
---

## Câu 8 — Nguồn dữ liệu dùng để gom nhóm hộ tương tự

**Bối cảnh điều tra**

Chức năng gom nhóm (F-ES-12) được định nghĩa trong tài liệu yêu cầu là "gom nhóm **dựa trên thông tin hợp đồng**", phục vụ cho xếp hạng và tính giá trị trung bình.

Tuy nhiên, trong đặc tả màn hình quản lý người dùng E-GW lại có **5 thuộc tính người dùng** do chính người dùng khai báo: số người trong gia đình, diện tích sàn, số lượng điều hoà, có điện mặt trời hay không, sở hữu hay thuê nhà.

Ở hệ thống hiện hành cũng có tài liệu riêng về gom nhóm, với ghi chú "tổng hợp theo 5 thuộc tính".

Chúng tôi phỏng đoán rằng 5 thuộc tính này có thể chính là tiêu chí gom nhóm, nhưng "thông tin hợp đồng" và "thuộc tính người dùng tự khai" là **hai nguồn dữ liệu khác nhau**, nên không thể tự kết luận.

Điểm này ảnh hưởng trực tiếp tới thiết kế xử lý theo lô để tạo dữ liệu xếp hạng và so sánh.

**Điểm thắc mắc**

1. Việc gom nhóm hộ tương tự dựa trên tiêu chí nào? Là 5 thuộc tính người dùng tự khai, hay thông tin hợp đồng, hay kết hợp cả hai?
2. Ngưỡng phân chia của từng tiêu chí (ví dụ khoảng diện tích sàn) hiện được ghi nhận là chưa xác định trong danh sách hạng mục còn để tạm — xin cho biết thời điểm dự kiến xác nhận.
3. Trường hợp người dùng chưa khai báo thuộc tính, thì việc gom nhóm và hiển thị xếp hạng xử lý như thế nào?

**Tài liệu tham chiếu**

- `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` — mục 「7-3. EMINEL-smartサーバー機能」, dòng F-ES-12
- `eminel_gw_project/docs/eminel/4_spec/admin/B_user_management.md` — mục 「E-GWユーザー情報：ユーザー属性情報」項目 B-C-01
- `eminel_gw_project/docs/old_eminel/01_overview.md` — mục 「02_データ生成・アプリ通信」, phần 別紙「グルーピング（5属性集計）」
- `eminel_gw_project/docs/eminel/2_management/20_open_issues.md` — mục 「CLD-06 細部の仮置き項目」, phần 「グルーピング閾値」

---

### 🇯🇵 【JP】グルーピングの基準データについてご教示ください

**調査の背景**

グルーピング機能（F-ES-12）は、統合要件定義書において「**契約情報に基づく**グルーピング（ランキング/平均値用）」と定義されております。

一方、E-GWユーザー管理の機能仕様には、ユーザーご自身にご入力いただく**5つの属性情報**（家族人数／延べ床面積／エアコン台数／太陽光発電／持ち家区分）が定義されております。

また現行EMINELにも別紙「グルーピング（5属性集計）」が存在すると把握しております。

この5属性がグルーピングの基準である可能性が高いと推測しておりますが、「契約情報」と「ユーザー入力の属性情報」は**取得元の異なるデータ**であるため、弊社側では判断いたしかねます。

本項目は、ランキング・比較用データを生成するバッチ処理の設計に直接影響いたします。

**確認したい点**

1. グルーピングの基準は、ユーザー入力の5属性でしょうか、契約情報でしょうか、あるいは両方を組み合わせるものでしょうか。
2. 各基準の区分閾値（例：延べ床面積の区分）につきまして、弊社の課題管理上は「グルーピング閾値」が未確定の仮置き項目として整理されております。確定時期の目安をご教示いただけますでしょうか。
3. ユーザーが属性情報を未入力の場合、グルーピングおよびランキング表示はどのように扱う想定でしょうか。

**参照資料**

- 統合要件定義書 v1.2 —「7-3. EMINEL-smartサーバー機能」F-ES-12 行
- 管理画面 機能仕様「B ユーザー管理」—「E-GWユーザー情報：ユーザー属性情報」B-C-01
- 現行EMINEL設計資料 —「02_データ生成・アプリ通信」別紙「グルーピング（5属性集計）」

---
---

# Phụ lục — Các câu hỏi dự phòng

Bốn câu dưới đây để dự phòng — đưa vào nếu bảng câu hỏi còn chỗ. Dự phòng 1, 2, 4 là cấp bách thấp hơn; riêng **Dự phòng 3 (GW-01) là vấn đề nặng** nhưng đặt ở đây vì bóng đang ở phía 北ガス (đã nêu qua QA ngày 17/06) — câu hỏi chỉ nhằm thúc thời điểm cung cấp.

## Dự phòng 1 — Gom 15 loại tư vấn tiết kiệm còn 7

**Bối cảnh**: hệ thống hiện hành có khoảng 15 loại tư vấn tiết kiệm. Trong danh sách hạng mục còn để tạm (CLD-06) có ghi kế hoạch gom lại còn 7 loại cộng điểm sưởi eco, nhưng nguyên tắc gom chưa được xác định. Ảnh hưởng tới cả yêu cầu ứng dụng (C5) và màn hình quản trị (G).

**Câu hỏi (bản Việt)**: xin cho biết danh mục 7 loại tư vấn sau khi gom và điều kiện kích hoạt của từng loại.

**Nguồn**: `eminel_gw_project/docs/eminel/2_management/20_open_issues.md` — mục 「CLD-06 細部の仮置き項目」

### 🇯🇵 省エネアドバイスの統廃合方針についてご教示ください

現行の省エネアドバイスは約15種類と把握しております。弊社の課題整理では「約15種→7種+エコ暖房ポイント」への統廃合の方向と把握しておりますが、統廃合の方針は未確定と理解しております。

本項目はアプリ要件（C5 省エネアドバイス）および管理画面（G 省エネアドバイス管理）の双方に影響いたします。統廃合後の7種類の内訳と、各種の判定条件をご教示いただけますでしょうか。

**参照資料**: モバイルアプリ要件定義書「C5 省エネアドバイス」／管理画面 機能仕様「G 省エネアドバイス管理」

## Dự phòng 2 — Nội dung màn hình thống kê (F-AD-11)

**Bối cảnh**: chức năng thống kê F-AD-11 được ghi trong danh sách chức năng màn hình quản trị, nhưng nội dung hiển thị hoàn toàn chưa được xác định. Hạng mục này cũng nằm trong nhóm được lùi sang 2027, nhưng vẫn cần biết hướng để tránh thiết kế lại cấu trúc dữ liệu.

**Câu hỏi (bản Việt)**: nếu không chốt được danh mục dữ liệu cần tích luỹ thì nền dữ liệu xây năm 2026 có nguy cơ phải làm lại — xin cho biết trước định hướng các thống kê muốn hiển thị, dù chỉ ở mức phương hướng.

**Nguồn**: `eminel_gw_project/docs/eminel/2_management/20_open_issues.md` — mục 「CLD-06」, phần 「F-AD-11統計表示内容（完全TBD）」

### 🇯🇵 統計情報画面（F-AD-11）の表示内容についてご教示ください

管理画面の機能一覧に F-AD-11（統計情報）が定義されておりますが、表示内容が完全にT.B.Dと整理されております。

本機能は劣後（2027年4月以降）と理解しておりますが、蓄積すべきデータ項目が決まらないと、2026年に構築するデータ基盤側で手戻りが生じる可能性がございます。表示したい統計の方向性のみでも先行してご教示いただけますでしょうか。

**参照資料**: 管理画面 機能一覧 — F-AD-11（統計情報）

---

## Dự phòng 3 — Đặc tả chi tiết logic điều khiển sưởi (2 mạch · điều khiển phức hợp)

**Bối cảnh**: đây là vấn đề nặng nhất trong danh sách đang mở (GW-01, bóng 北ガス): không lấy được source code gateway hiện hành nên firmware phải viết mới hoàn toàn, nhưng đặc tả chi tiết (điều kiện điều khiển nhà 2 mạch, điều kiện điều khiển phức hợp…) vẫn chưa được cung cấp — "phải làm cái gì" chưa quyết được. Trao đổi QA ngày 17/06 đã tách bạch định nghĩa (điều khiển lịch sưởi vs điều khiển từ xa) nhưng đặc tả 2 mạch · phức hợp vẫn chưa có. Chậm trễ ở đây lan sang cả phía cloud.

**Câu hỏi (bản Việt)**: xin cho biết thời điểm có thể cung cấp đặc tả chi tiết điều kiện điều khiển 2 mạch và điều khiển phức hợp; nếu chưa có tài liệu hoàn chỉnh, có thể trao đổi theo hình thức QA từng điểm được không?

**Nguồn**: `eminel_gw_project/docs/eminel/2_management/20_open_issues.md` — mục 「GW-01 暖房制御ロジックの詳細仕様が北ガス未提示」, dòng 94–99

### 🇯🇵 暖房制御ロジック詳細仕様（2系統・複合制御）のご提示時期についてご教示ください

現行GWのソースコードが入手できないため、E-GWのファームウェアはフルスクラッチで開発いたします。6/17のQAにて「暖房スケジュール制御」と「暖房遠隔制御」の定義はご整理いただきましたが、**2系統宅の制御条件・複合制御の制御条件等の詳細仕様は、依然としてご提示いただけていない状況**と認識しております。

本項目が確定しない場合、ファームウェアの実装内容が決められず、遅延がGW以外（クラウド側）にも連鎖する懸念がございます。

詳細仕様のご提示時期の目安をご教示いただけますでしょうか。完成資料のご用意が難しい場合は、論点ごとのQA形式でのご確認でも差し支えございません。

**参照資料**: 統合要件定義書 v1.2 — F-GW-05／業務フロー資料（暖房制御関連スライド）

---

## Dự phòng 4 — Nấc thời gian và số khung giờ của lịch sưởi

**Bối cảnh**: hệ hiện hành dùng nấc 10 phút, tối đa 6 khung giờ/ngày. Requirement app ghi hạng mục 「スケジュール刻み」 nằm trong danh sách TBD của 北ガス, chưa xác định — trong khi đây là tham số nền của UI đặt lịch (app) lẫn firmware.

**Câu hỏi (bản Việt)**: hệ mới có kế thừa nguyên nấc 10 phút · tối đa 6 khung giờ/ngày của hệ hiện hành không? Nếu muốn thay đổi, xin cho biết giá trị mong muốn.

**Nguồn**: `eminel_gw_project/docs/eminel/3_requirements/app/B02_heating_control.md` — mục 「要確認事項」, dòng 272–273

### 🇯🇵 スケジュールの時間刻み・時間帯数上限についてご確認をお願いいたします

暖房スケジュールの時間刻みおよび1日あたりの時間帯数上限につきまして、現行は**10分刻み・1日最大6時間帯**と把握しております。貴社のTBDリストに「スケジュール刻み」が挙げられており、未確定と認識しております。

本項目はアプリのスケジュール設定UIとファームウェア双方の基礎仕様となるため、**現行踏襲（10分刻み・最大6時間帯）でよろしいか**、変更のご意向がある場合はご希望の値もあわせてご教示いただけますでしょうか。

**参照資料**: モバイルアプリ要件定義書「B2 暖房自動制御」—「要確認事項」

---

## Ghi chú độ phủ (nội bộ, không gửi khách)

Đối chiếu với Phụ lục C của [onboarding_guide.md](onboarding_guide.md) (12 mục T.B.D đang chặn việc): bảng này phủ các mục nặng nhất. Các mục sau **cố ý chưa** đưa vào bảng hỏi khách, xử lý theo đường khác:

| Mục | Vì sao chưa đưa vào bảng |
|---|---|
| C.2 — 「無効」của gateway chặn những gì (C-B-06) | Cần mui định nghĩa phương án trước, rồi mới hỏi khách xác nhận |
| C.11 — Yêu cầu phi chức năng server (SVC-03) | Nên đi kèm đề xuất kiến trúc của mui, không hỏi suông |
| C.12 — Tài khoản dev TagTag/PI/Xzilla (CLD-02) | Việc xin cấp quyền, đi qua PM mui — không phải câu hỏi spec |
