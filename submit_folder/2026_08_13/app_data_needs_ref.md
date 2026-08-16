> Tư liệu làm việc NỘI BỘ của đợt review 2026_08_13 (P1 dựng, 16/08) — bảng nhu cầu dữ liệu app C1–C5 dùng làm căn cứ phán định batch ở P2–P8. Không phải bản giao nộp.

# BẢNG NHU CẦU DỮ LIỆU APP E-GW (module C1–C5 + A3)

Mục đích: sản phẩm dùng chung cho các phase review batch — trả lời câu "nếu bỏ batch tính toán X của hệ cũ thì app E-GW có mất nguồn dữ liệu không".

## Mốc nguồn (đã xác nhận bằng git log)

- Repo: `d:/SYP_Home/mui/eminelGW/sources/eminel_gw_project` @ **1100487** (main, khớp mốc pin — QUAN SÁT: `git log -1` = 「機能仕様着手」)
- Viết tắt đường dẫn trong cột "Căn cứ":
  - `C01` = `docs/eminel/3_requirements/app/C01_graph.md` (tương tự `C02`…`C05`, `A03`)
  - `統合` = `docs/eminel/3_requirements/00_integrated_requirements_v1.2.md`
  - `spec-c02` = `docs/eminel/4_spec/app/c02_グラフ.md`, `spec-c03` = `docs/eminel/4_spec/app/c03_レポート.md`, `spec-README` = `docs/eminel/4_spec/app/README.md`
- QUAN SÁT về trạng thái: các file C01–C05, A03 tại mốc này đều ghi 状態=「レビュー中」 (C01:5, C02:5, C03:5, C04:5, C05:5, A03:5) — KHÔNG phải レビュー済 như đề bài nêu. Spec c02/c03 = 「ドラフト済（レビュー待ち）」 (spec-c02:5, spec-c03:5).

## BẢNG TỔNG HỢP

| Module | Loại dữ liệu cần (đo đạc gì) | Granularity | Có cần SO SÁNH NHÓM/他世帯 không (trích câu) | Có cần giá trị TÍCH LUỸ/trung bình TÍNH SẴN không | F-ES liên quan | Scope 26年 hay 劣後 | Căn cứ (file:dòng) |
|---|---|---|---|---|---|---|---|
| **C1 グラフ表示** | Chuỗi thời gian: 室温(℃)・湿度(%)・人感(検知回数) theo phòng; ガス消費量(㎥, tách 暖房/給湯 khi có Wi-Fiリモコン+メーカーアプリ連携); 消費電力量(kWh, giá trị TÍNH TOÁN); 発電電力量(kWh, 太陽光+マイホーム発電 積み上げ); 売電/買電量(kWh); 蓄電池充放電量(kWh) | 時間値=quá khứ 1 tuần / 日値=quá khứ 1 năm / 月値=当年; riêng 人感: 10分値 (当日3時間) + 1日値 (1 tuần). Bảo lưu dữ liệu: đang hỏi 2年 (C01:153-154) | **CÓ** — 「日値・月値のグラフで、他者の平均と比較できる」(C01:47); mục con giới hạn: グラフ種別=ガス・電気・発電, 時間軸=月値 (C01:53-58); spec chốt 「よく似た世帯の平均 \| 月値」(spec-c02:67). 他者=nhóm 「よく似た世帯の平均」 từ グルーピング 月1回更新 (C01:68) | **CÓ**: (1) 実績の平均 (日値・月値, ví dụ 1日値平均=平均 過去1ヶ月, 「平均の計算はレンジに依存する」 C01:148-149); (2) 他世帯平均 tính sẵn từ グルーピング月1回更新; (3) giá trị 前年 (月値); (4) 消費電力量 là giá trị tính: 「太陽光発電＋ガス発電＋蓄電池放電−蓄電池充電＋買電−売電」で算出 (C01:97) | F-ES-01 (グラフデータ), F-ES-02 (グルーピング=グラフ用平均値・TagTag分担), F-ES-12 (グルーピング) | 26年 (toàn bộ trong 「要件案：26年対応スコープ」; それ以降=なし C01:112-114). Không nằm trong bảng 劣後 của spec-README:158-167 | C01:26-31, 40-59, 67-69, 76-78, 93-101, 147-149, 153-154; 統合:577-592, 618-623; spec-c02:26-31, 46-58, 64-68 |
| **C2 レポート表示** | Số liệu tổng hợp theo kỳ: 使用量 ガス(㎥)/電気(kWh) (tuần, ngày-trong-tuần, tháng); 料金(円) (当月/前年同月/前月 — việc hiển thị 料金 chưa chốt); 予測 使用量 当月 (電気・ガス); 省エネ効果=削減額(円) so 24時間暖房; ランキング thứ hạng trong nhóm (100世帯換算, ガス/電気/総合 một次エネルギー換算); 発電機器効果: 売電量(kWh)・売電金額(円)・自給率(%)・自家消費率(%)・買電削減金額(円)・買ガス削減金額(円); CO2排出 削減量・増減率(%); グラフ nhúng (値はC1流用・検針ベース) | 週値 (当週vs前週) + 日値 (日ごとの使用量) + 月値 (検針後, 前年同月/前月) + 年値 (当年vs前年, CO2=月次前年同月比 tích 12 tháng). Phạm vi xem lại: 月間=1年前, 週間=1ヶ月(要仕様検討), 年間=前年分 (spec-c03:23-26) | **CÓ** — 「週間・月間・年間のレポートが届き、省エネの成果や他世帯との比較を振り返れる。」(C02:23); 「よく似た世帯との比較（ランキング）を確認できる」「当月の使用量による同グループ内の順位（100世帯換算）」「ガス・電気・総合（一次エネルギー換算）のそれぞれ」(C02:109-111); đã chốt 「→「実施する」で要件進める」(C02:192); 統合: 「他者比較（似た家庭との比較・順位、一次エネルギー換算）」(統合:604) | **CÓ, nặng nhất trong C1–C5**: 予測使用量 (踏襲 tính toán省エネコンテンツ側, 統合:599); 省エネ効果 theo công thức 統合:607; 自給率/自家消費率 (統合:608-609; 「レポート用はまとめた値を使う想定（1時間値、1日値の用途はグラフ用）」 C02:202); CO2=使用量×CO2排出係数 đăng ký sẵn trên server (C02:147); ランキング từ グルーピング月1回更新, có fallback 「グループの最低件数を下回る場合は絞り込み前のグルーピングで表示」(C02:126) | F-ES-02 (レポートデータ+グルーピング), F-ES-09 (ポイント付与ボタン→PI), F-ES-12 | 26年 (それ以降=なし C02:152-154). Không trong bảng 劣後 | C02:23-33, 65-79, 83-87, 101-117, 133-139, 146-147, 190-213; 統合:594-623; spec-c03:10-15, 74-86, 127-133, 137-143, 154-160, 162-169 |
| **C3 エネルギーの現在状態表示** | Trạng thái hiện tại: 発電状態 + 現在の発電電力(W); 電力収支 1 màn hình: 太陽光発電・マイホーム発電・消費電力・買電・売電・蓄電池充放電 (kWh) + ガス消費(㎥) | 瞬時値・1時間値・1日値・1月値 (切替; 瞬時値 là 【新規】 so hệ cũ — hệ cũ min=1時間値). Bảo lưu: 瞬時値=0 / 1時間値=1週間 / 1日値=1週間 / 1月値=2年 (C03:124-128) | KHÔNG — không có câu nào về 他世帯/グループ trong C03 (grep 「他者」「世帯」「平均」「グルーピング」 đều 0 hit trong C03) | **CÓ một phần**: 消費電力量 là giá trị tính (như C1); 1時間/1日/1月値 là giá trị集計 sẵn. Không cần 平均/前年 tính sẵn | F-ES-15 (リアルタイムモニタ), F-ES-13 (異常値処理 — tham chiếu 統合7-3, C03:16) | 26年 (それ以降=なし C03:85-87). Không trong bảng 劣後 | C03:33, 46-56, 63-64, 115-128; 統合:625-628; spec-README:122 (c01 ハブ=C3, 未着手) |
| **C4 センサー情報の現在状態表示** | Giá trị hiện tại 室温(℃)・湿度(%) theo phòng (センサー nhiều phòng thì切替) | Chỉ 現在値 (không chuỗi thời gian — 推移 thuộc C1: 「室温・湿度の推移グラフ（時刻別／日別／月別）はC1。本セクションは現在値」 C04:55) | KHÔNG — không có câu nào về 他世帯/平均 trong C04 | KHÔNG — chỉ cần giá trị đo mới nhất; 「室温・湿度は現在状態を別途表示」(統合:580) | F-ES-01 (室温・湿度の現在状態を別途表示) | 26年 (それ以降=なし C04:46-48). Không trong bảng 劣後 | C04:23, 31-33, 40-42, 55; 統合:580 |
| **C5 省エネアドバイス** | Bản thân app chỉ nhận/hiển thị advice + trạng thái 未読/既読/達成. NHƯNG server cần dữ liệu để phán định điều kiện phát: 先月の使用量 (リマインド), 在宅/就寝/外出温度設定 (設定見直し), tỉ lệ hộ 暖房OFF toàn tập user, 入会月 | Theo điều kiện phát: 月1回 (使用量リマインド・グラフ確認・設定見直し各種), 特定期間内1回 (暖房OFF), ユーザーごとに特定の日 (記念日) — 統合:634-644 | **CÓ (gián tiếp, phía server)** — điều kiện 暖房OFF cần thống kê chéo hộ: 「暖房OFF：暖房をOFFしているユーザーが半数超の場合に暖房ONユーザーへ通知（特定期間内に1回のみ）」(統合:641). Trên UI app không có mục so sánh 他世帯 | **CÓ (phía server)**: 先月の使用量 (giá trị tháng tính sẵn), phán định nhiệt độ 設定 cao/thấp, tỉ lệ OFF 半数超. App không tự tính | F-ES-03 (省エネアドバイス Push), F-AD-05 (quản lý・パラメータ, 「夜間バッチを回すタイミングまで」の変更を許容 統合:646), F-ES-09 (実行ポイント→PI) | 26年 (それ以降=なし C05:70-72). Không trong bảng 劣後 | C05:36-40, 48-56, 62-66, 78-82; 統合:632-647 |
| **A3 ポイント** (liên quan điểm/ranking) | 所持ポイント (từ Point Infinity), 今月EMINEL取得ポイント (từ ポイントログ server); エコ暖房: 目標温度 + 現在の平均設定温度(℃) | エコ暖房: bình quân 設定温度 kỳ đông, hệ cũ 月ごとに判定 (12〜3月, A03:75, 118-119); 所持pt=giá trị hiện tại | KHÔNG so sánh 他世帯 trong A3. (Ranking xếp hạng 他世帯 nằm ở C2; ランク制度 điểm thưởng nằm A4 バッジ・ランク) | **CÓ**: 平均設定温度 là giá trị bình quân tính sẵn phía server — 「達成可否・付与の判定はサーバーで行い、アプリは検知しない」(A03:75); tổng điểm tháng từ ポイントログ | F-ES-04 (エコ暖房ポイント), F-ES-09 (PI連携) | **劣後** — spec-README bảng 劣後: 「a02 ポイント \| A3 \| ✅」(spec-README:162); A4 バッジ・ランク cũng ✅ (spec-README:163) | A03:26-28, 36-37, 44-45, 51-54, 61, 67-68, 75; 統合:409, 675-690; spec-README:158-163 |

## LÀM RÕ THEO YÊU CẦU

### 1. C1 グラフ — chuỗi thời gian cần granularity nào (chốt theo spec c02)

Bảng trục thời gian (spec-c02:26-31, khớp 統合:587-592):

| 時間軸 | Phạm vi切替 | 1 màn hình vẽ | Có 平均 tính sẵn? | Có so sánh? |
|---|---|---|---|---|
| 時間値 (1時間値) | 過去1週間 | 1日分 (0〜23時) | KHÔNG — 「1時間値：過去1週間を対象とし、平均値は表示しない」(統合:588) | Không (「時間値のグラフでは比較を表示しない」 spec-c02:72) |
| 日値 (1日値) | 過去1年 | 1ヶ月分 | CÓ — 「1日値：過去1年を対象とし、平均値ありで表示する」(統合:589) | 実績の平均 |
| 月値 (1月値) | 当年 | 当年12ヶ月 | CÓ — 「1月値：当年を対象とし、平均値ありおよび前年比較で表示する」(統合:590) | 実績の平均・よく似た世帯の平均・前年の自分 |
| 人感 (riêng) | 10分値=当日3時間 / 1日値=1週間 | — | KHÔNG (「平均値は表示しない」 統合:591) | Không |

- QUAN SÁT lệch trong C01: câu cha nói 「日値・月値のグラフで、他者の平均と比較できる」(C01:47) nhưng mục con 時間軸 chỉ ghi 月値 (C01:57-58); spec c02 chốt 他世帯平均 chỉ 月値 (spec-c02:64-68) — đúng quy tắc spec-README:76 「要件の中で本文と下位項目が食い違うときは、より具体的な下位項目を採る」.
- 他世帯平均 chỉ 3 loại グラフ: ガス消費量・消費電力量(電気)・発電電力量 (C01:53-56; spec-c02:51-53 cột 「よく似た世帯の平均」=◯ chỉ 3 dòng này).
- Lưu ý cho review batch: 灯油消費量グラフ hệ cũ → 「不要で決定」(C01:142-143).

### 2. C2 レポート — mục so sánh 他世帯 (câu nguyên văn)

- Khái quát: 「週間・月間・年間のレポートが届き、省エネの成果や他世帯との比較を振り返れる。」(C02:23)
- Yêu cầu tháng: 「よく似た世帯との比較（ランキング）を確認できる」「当月の使用量による同グループ内の順位（100世帯換算）」「ガス・電気・総合（一次エネルギー換算）のそれぞれ」(C02:109-111); năm: 「よく似た世帯との比較（順位）」(C02:135)
- Trạng thái: từng 検討中 nhưng đã chốt — 「→「実施する」で要件進める」(C02:192)
- Ràng buộc nhóm: 「グループの最低件数を下回る場合は絞り込み前のグルーピングで表示」(C02:126; spec-c03:133); コージェネ設置時 chỉ 総合 (C02:72, spec-c03:82)
- Nguồn nhóm: 「グルーピング（他者比較）：月1回更新。グラフ用平均値・レポート内他者比較に使用」(統合:618) — thuộc tính nhóm: 建物種別(Xzilla)・世帯人数(オンボーディング)・料金メニュー・ロードヒーティング・コージェネ有無・売電有無・アンペア数・延べ床面積 (統合:619)

### 3. Nguồn dữ liệu: GW đẩy lên hay server tự tính? (theo những gì tài liệu NÓI RÕ)

QUAN SÁT (tài liệu nói rõ):
- Toàn bộ F-ES-01/02/15 là 「EMINEL-smartサーバー機能」 (統合:573) → dữ liệu グラフ/レポート/モニタ do **server sinh** (「グラフデータ生成」「レポートデータ生成」 統合:406-407).
- 消費電力量 = **server tính**: 「「太陽光発電電力量」＋「ガス発電電力量」＋「蓄電池放電量」−「蓄電池充電量」＋「買電量」−「売電量」で算出する」(統合:582).
- 電力30分値 KHÔNG từ GW mà từ **Xzilla (Cルート)**: 「CルートでのXzillaからEMINEL-smartサーバーへの電力30分値（速報値、確報値）データ取得」(統合:694).
- CO2: 「CO2排出量は使用量にあらかじめサーバに登録したCO2排出係数を乗じて算出」(C02:147).
- エコ暖房: 「達成可否・付与の判定はサーバーで行い、アプリは検知しない」(A03:75).
- 省エネアドバイス: phán định điều kiện gắn 「夜間バッチを回すタイミングまで」(統合:646) → tồn tại **batch đêm** phía server.
- C3 瞬時値 chưa chốt định nghĩa giữa 2 phương án: 「デバイスから直接取れた最新値」 vs 「クラウドにN分単位でアップロードされたN分値」(C03:115-121) → tài liệu thừa nhận tồn tại luồng GW upload N分値 lên cloud, nhưng lựa chọn chưa quyết.
- Phân công TagTag chưa chốt: 「1時間値・1日値のグラフはEMINELアプリ（仮）が担当、1月値のグラフ・週間レポートはTagTagが担当」 và 2 án cho phía EMINELアプリ 「案1）TagTag（省エネコンテンツサーバ）からデータ連携／案2）TagTagと同じ方法でデータ作成」(統合:622-623, TBD). Nhưng C2 đã chốt app hiển thị 週間レポート: 「アプリで週間レポートを表示するでFIX」(C02:184-185).
- 予測使用量: 「使用量予測：省エネコンテンツ側に実装予定の計算方法を踏襲する」(統合:599) — kế thừa cách tính của hệ 省エネコンテンツ (コンシェルジェ), tương tự 省エネ効果 「現行コンシェルジェサーバの計算方法を踏襲」(C02:125).

推定 (suy đoán, tài liệu KHÔNG nói rõ): đường đo đạc GW→cloud cho 室温/湿度/人感/ガス/発電… không được mô tả chi tiết trong 3 file nguồn của nhiệm vụ này; chỉ suy ra gián tiếp từ phương án 「クラウドにN分単位でアップロードされたN分値」(C03:120) rằng GW đẩy giá trị N分 lên. Cần đối chiếu thêm phần E-GW (F-GW) của 統合要件 khi review batch.

### 4. Hệ quả cho review batch (điểm treo cần theo dõi)

- Mọi 平均/ランキング đều phụ thuộc **グルーピング batch 月1回** (統合:618) — bỏ batch này thì C1 (他世帯平均・月値) và C2 (ランキング 月間・年間) mất nguồn.
- 実績の平均 của C1 phụ thuộc pipeline tính bình quân theo range (C01:148-149) — chưa chốt granularity lưu.
- C2 phụ thuộc chuỗi batch: 予測 (kế thừa 省エネコンテンツ), 省エネ効果 (kế thừa コンシェルジェサーバ), CO2係数, 検針trigger (月間=検針後 C02:101).
- C5 phụ thuộc **夜間バッチ** phán định điều kiện + thống kê 暖房OFF toàn tập user (統合:641, 646).
- A3 エコ暖房 phụ thuộc batch bình quân 設定温度 mùa đông + phán định server (A03:75) — nhưng A3 đang 劣後 (spec-README:162).
- C3 giữ 1月値 2年, 1時間/1日値 chỉ 1週間 (C03:124-128) ≠ C1 đang hỏi giữ 2年 theo粒度 (C01:153-154) — hai chính sách bảo lưu khác nhau giữa module, cần thống nhất khi thiết kế batch/bảng dữ liệu.
