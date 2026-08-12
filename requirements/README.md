# Bộ khung xây dựng tài liệu hướng dẫn dự án EMINEL Gateway

> **File này không phải tài liệu học.** Đây là **bản thiết kế** của tài liệu học — ghi lại tài liệu đó phải có gì, viết theo nguyên tắc nào, trích dẫn ra sao.
> Mục đích: sau khi `onboarding_guide.md` được tạo xong, bất kỳ ai cũng có thể mở file này ra và **đối chiếu để review** xem tài liệu đã đạt chuẩn chưa.

| | |
|---|---|
| Ngày lập | 2026-08-03 |
| Đối chiếu với repo | `eminel_gw_project` commit `460c671` (2026-08-06) |
| Cập nhật gần nhất | 2026-08-12 |
| Người dùng cuối của tài liệu | Người **mới vào dự án**, có thể **mới học IT**, phía SYP hoặc mui Lab |
| Vị trí | thư mục `eminel_gw_onboarding\` đặt **cạnh** (ngoài) repo dự án. Bản gốc soạn tại `D:\SYP_Home\mui\eminelGW\`, hiện tại: `c:\Users\BuiTrongDat.AzureAD\Documents\mui\eminel\` |

---

## 1. Ba câu hỏi mà tài liệu phải trả lời được

Đây là tiêu chí nghiệm thu cao nhất. Người mới đọc xong phải tự trả lời được:

| # | Câu hỏi | Được trả lời ở |
|---|---|---|
| **1** | **Dự án này là về cái gì?** | Chương 1 → 5 |
| **2** | **Đã làm được đến đâu?** | Chương 6 (phạm vi đã chốt), 7 (tài liệu đã sản xuất), 8 (quyết định & vấn đề) |
| **3** | **Giờ phải làm gì tiếp?** | Chương 9, 10 |

Nếu một chương không phục vụ trực tiếp một trong ba câu hỏi trên → chương đó thừa.

---

## 2. Cấu trúc thư mục

```
requirements/                  ← bộ tài liệu mà khung này quản
├── README.md                  ← file này (bộ khung + tiêu chuẩn review)
├── onboarding_guide.md        ← TÀI LIỆU CHÍNH (một file, có mục lục ở đầu)
├── qa_kitagas.md              ← 8 câu hỏi chính + 4 dự phòng (Việt–Nhật) gửi khách hàng
└── assets/
    ├── 01_architecture/       ← ảnh copy từ docs/eminel/3_requirements/images/
    ├── 02_business_flow/      ← ảnh copy từ docs/eminel/1_product/11_business_process/captures/
    ├── 03_legacy_app/         ← ảnh copy từ docs/old_eminel/app/screens/
    └── 04_diagrams/           ← (CHƯA TẠO) chỗ dành sẵn cho sơ đồ tự vẽ dạng ảnh,
                                  nếu sau này cần; hiện guide vẽ sơ đồ bằng ASCII trong code block
```

> Phạm vi file này chỉ là `requirements/`. **Cấu trúc toàn workspace** (memory/, skillAI/, sources/…):
> xem [`../CLAUDE.md`](../CLAUDE.md) — nguồn sự thật duy nhất về bố cục, không lặp lại ở đây.

**Ghi chú về `04_diagrams/`**: thư mục này **cố ý để trống**. Toàn bộ sơ đồ do tài liệu tự vẽ (cây khái niệm điều khiển sưởi, hành trình một điểm dữ liệu, ranh giới hai đám mây, dòng thời gian) đều được viết bằng **ASCII nhúng thẳng vào markdown** — ưu điểm là sửa được bằng text, hiển thị mọi nơi, và nằm trong cùng một file với nội dung. Chỉ dùng thư mục này nếu sau này cần sơ đồ dạng ảnh mà ASCII không diễn đạt nổi.

**Nguyên tắc bất di bất dịch về ảnh và tham chiếu:**

| | |
|---|---|
| **Ảnh hiển thị** | Lấy từ bản copy trong `assets/` — để tài liệu luôn hiển thị được, không phụ thuộc đường dẫn tương đối ra ngoài |
| **Dẫn chứng / tham chiếu** | **Luôn trỏ về file gốc trong `eminel_gw_project/`** — người đọc phải truy được về nguồn thật |
| **Đường dẫn ghi trong tài liệu** | Bắt đầu từ `eminel_gw_project/...`, **không bao giờ** ghi `D:\SYP_Home\...` |

---

## 3. Bộ khung nội dung — 10 chương + 7 phụ lục

### Phần mở đầu

| Mục | Nội dung bắt buộc |
|---|---|
| 0.1 | Tài liệu này dành cho ai · đọc mất bao lâu · đọc theo thứ tự nào (có 3 lộ trình: đọc hết / đọc nhanh / tra cứu) |
| 0.2 | Bảng ký hiệu dùng xuyên suốt |
| 0.3 | Quy ước trích dẫn nguồn |
| 0.4 | ⭐ **Tóm tắt một trang** + **bức tranh toàn cảnh** — trả lời gọn 3 câu hỏi cho người chỉ có 5 phút |
| 0.5 | **Sống sót với tài liệu tiếng Nhật** — cách đọc bảng `出典 / 最終更新`, ý nghĩa `※要確認` `T.B.D` `🔴` |
| 0.6 | **Thuật ngữ IT cơ bản** — bảng giải thích cho người mới học IT các từ dùng xuyên suốt (firmware, API, MQTT, Webhook...) |
| 0.7 | **Giới hạn của tài liệu này** — repo là tài liệu cấp 2, những thư mục không có ở bản local |

### Mười chương

| Ch. | Tên | Nội dung bắt buộc |
|---|---|---|
| **1** | Dự án này là về cái gì | Câu chuyện mở đầu (gia đình Hokkaido) · ba cái tên dễ lẫn · bốn bên · vì sao có dự án · ai trả tiền phần nào · phạm vi in/out · dòng thời gian 2022→nay · stack công nghệ thực tế sẽ đụng vào |
| **2** | Hệ thống mới được xây thế nào | Sơ đồ tổng thể · 8 thành phần · **ranh giới trách nhiệm hai đám mây** · Webhook + Pull · 24 interface · Bルート vs Cルート · 9 cấu hình lắp đặt |
| **3** | Câu chuyện của một điểm dữ liệu | Trace end-to-end: cảm biến → GW → đám mây thiết bị → đám mây nghiệp vụ → biểu đồ. Và chiều ngược lại: người dùng bấm nút → thiết bị chạy |
| **4** | Hệ thống cũ — cái đang bị thay | Vì sao phải học · bẫy tên gọi `Cサーバ` · stack · **4 logic nghiệp vụ đặc thù** · vòng đời dữ liệu · bảng kế thừa/bỏ |
| **5** | Người dùng thực sự trải qua những gì | UC-01 onboarding · UC-04 hiển thị & thông báo · UC-05 điều khiển sưởi (cây khái niệm + 5 quy tắc thiết bị) · làm lạnh · DR · UC-06 vận hành |
| **6** | Làm cái gì, khi nào | 4 nhóm mã chức năng · cách đọc bảng chức năng · quyết định phạm vi 12/2026 · danh sách bị lùi · tiền & hợp đồng |
| **7** | Bộ tài liệu của dự án | Bản đồ 6 tầng `0_foundation`→`5_design` · cấu trúc file requirement · 23 section + trạng thái · spec admin · design draft |
| **8** | Đã làm được đến đâu | Cỗ máy 20/21/22/23 · dòng thời gian quyết định · bản đồ vấn đề đang mở · 3 vấn đề chặn SYP |
| **9** | Giờ phải làm gì tiếp | Lịch tính ngược · đang đứng ở đâu · 5 tiền đề mới từ trại tập trung · vai trò & môi trường SYP |
| **10** | Ngày đầu tiên của bạn | Checklist thực hành: cài gì · xin quyền gì · đọc gì trước · hỏi ai · 3 việc làm được ngay |

### Bảy phụ lục

| | Tên | Yêu cầu |
|---|---|---|
| **A** | Từ điển thuật ngữ | Nhật · đọc là gì · Việt · giải thích một dòng. Sắp theo nhóm, không theo bảng chữ cái |
| **B** | Bảng mâu thuẫn giữa các tài liệu | Mỗi mâu thuẫn: tài liệu nào nói gì · nghi ngờ cái nào sai · hệ quả |
| **C** | Danh mục T.B.D đang chặn việc | Cái gì chưa quyết · chặn ai · hỏi ai |
| **D** | Bản đồ tra cứu | "Muốn biết X → mở file nào" |
| **E** | Cách truy về nguồn gốc | Thứ tự tra: docs → input → repo tham chiếu → Slack → Notion/OneDrive. Kèm skill `/trace-source` |
| **F** | Đề tự kiểm tra | 42 câu, **không kèm đáp án** |
| **G** | Đáp án | Tách rời khỏi F, kèm giải thích ngắn |

---

## 4. Sáu nguyên tắc biên soạn

| # | Nguyên tắc | Kiểm tra bằng cách |
|---|---|---|
| **1** | **Mỗi lý luận phải có dẫn chứng** — file nào, mục nào, dòng bao nhiêu | Random 10 khẳng định bất kỳ, xem có nguồn không |
| **2** | **Giải thích thuật ngữ tại chỗ**, không bắt người đọc nhảy xuống phụ lục | Đọc từ trên xuống, gặp từ lạ nào không được giải thích ngay không? |
| **3** | **Khái niệm trừu tượng phải có ví dụ đời thường** | Mỗi khái niệm khó có kèm box 💡 không? |
| **4** | **Nói rõ cái gì chắc, cái gì chưa chắc** — không trộn sự thật với suy đoán | Suy đoán có được đánh dấu rõ không? |
| **5** | **Giữ nguyên thuật ngữ tiếng Nhật**, chú thích lần đầu xuất hiện | Vì mọi tài liệu gốc, Slack, Notion, họp đều tiếng Nhật — dịch hết ra tiếng Việt thì không tra ngược được |
| **6** | **Mỗi chương kết thúc bằng "Kiểm tra nhanh" 3–5 câu** (chương khó nhất được phép 5) | Có đủ ở tất cả 10 chương không? |

---

## 5. Quy ước ký hiệu

| Ký hiệu | Loại box | Dùng khi |
|---|---|---|
| 📖 | **Thuật ngữ** | Khái niệm IT xuất hiện lần đầu — giải thích như cho người ngoài ngành |
| 💡 | **Ví dụ đời thường** | Khái niệm trừu tượng cần một ẩn dụ |
| 🔍 | **Dẫn chứng** | Trích nguyên văn + nguồn |
| ⚠️ | **Bẫy** | Chỗ dễ hiểu sai |
| ❌ | **Mâu thuẫn** | Hai tài liệu nói ngược nhau |
| 🔴 | **Chưa quyết** | T.B.D đang chặn việc |
| 🔸 | **Giả thuyết** | Suy đoán của người viết, CHƯA được nguồn nào xác nhận — không dùng làm căn cứ |

Ký hiệu trạng thái vấn đề (lấy đúng từ repo, không tự chế):
`🔴 chưa động` · `🔵 đang chạy` · `🟡 chờ thông tin` · `🟣 đang review` · `✅ đã quyết`

---

## 6. Quy ước trích dẫn

Định dạng chuẩn:

```
🔍 Nguồn: eminel_gw_project/docs/eminel/1_product/10_feature_list.md
   → mục 「サマリ（劣後可能工数）」, dòng 16–23
   → nguyên văn: 「合計 13人月」
```

**Vì sao ghi cả tên mục lẫn số dòng**: số dòng giúp nhảy tới ngay, tên mục giúp vẫn tìm lại được khi file bị sửa và số dòng trôi đi.

**Bắt buộc**: đầu tài liệu đóng dấu ngày đối chiếu, để người đọc biết số dòng ứng với bản nào của repo.

---

## 7. Bảng kê ảnh đã copy

Ảnh trong `assets/` là **bản sao**. Bảng này để đối chiếu, kiểm tra, hoặc cập nhật lại khi ảnh gốc thay đổi.

### `assets/01_architecture/` — nguồn: `eminel_gw_project/docs/eminel/3_requirements/images/`

| File | Nội dung | Dùng ở |
|---|---|---|
| `3-1_system_overview.png` | Sơ đồ tổng thể toàn hệ thống | Ch.0.4, Ch.2 |
| `4-2_interface.png` | Sơ đồ 24 interface | Ch.2 |
| `4-5_dataflow_responsibility.png` | Luồng dữ liệu theo ranh giới trách nhiệm | Ch.2 |
| `4-5_dataflow_local.png` | Luồng 2 phút / 10 phút | Ch.3 |
| `3-5-3_pattern2_koremo.png` | Cấu hình pattern ② コレモ (mục tiêu chính) | Ch.2 |
| `8-4_admin_system.png` | Cấu trúc hệ thống màn hình quản trị | Ch.7 |

### `assets/02_business_flow/` — nguồn: `eminel_gw_project/docs/eminel/1_product/11_business_process/captures/`

| File | Nội dung | Dùng ở |
|---|---|---|
| `slide-04/05/06.png` | Onboarding 3 phần | Ch.5 |
| `slide-15/16/17.png` | Biểu đồ · report · sinh dữ liệu report | Ch.5 |
| `slide-27.png` | Hiển thị lỗi đang xảy ra | Ch.5 |
| `slide-29/30.png` | Thông báo về nhà · thông báo trông nom | Ch.5 |
| `slide-35.png` | Cài đặt điều khiển nhiệt độ phòng | Ch.3 |
| `slide-36/37/38.png` | Điều khiển nhiệt độ phòng · nhà コレモ · chạy theo lịch | Ch.3 (36, 37) · Ch.5 (38) |
| `slide-40/41.png` | Hai phương án kết thúc DR | Ch.5 |
| `slide-45.png` | Dashboard quản trị | Ch.5 |

### `assets/03_legacy_app/` — nguồn: `eminel_gw_project/docs/old_eminel/app/screens/`

| File | Nội dung | Dùng ở |
|---|---|---|
| `image003.png` | Màn hình lịch sưởi app cũ | Ch.4 |
| `image006.png` | Màn hình biểu đồ app cũ | Ch.4 |
| `image016.png` | Màn hình HOME app cũ | Ch.4 |
| `image022.png` | Màn hình điểm thưởng app cũ | Ch.4 |

**Tổng: 26 ảnh, ~4.0 MB.** Chỉ copy ảnh thực sự được nhúng — không bê toàn bộ 75 ảnh của repo.

---

## 8. Checklist review ba vòng

Sau khi tài liệu được tạo xong, chạy đúng ba vòng này theo thứ tự.

### Vòng 1 — Soi chỗ trọng yếu làm chưa kỹ

Không đọc dàn đều. Nhắm thẳng vào những chỗ **dễ làm ẩu nhất**:

- [ ] Số dòng trích dẫn có đúng không? (kiểm tra ngẫu nhiên ít nhất 10 chỗ bằng cách mở file thật)
- [ ] Chương 3 (câu chuyện điểm dữ liệu) có thật sự liền mạch không, hay chỉ là ghép các mảnh rời?
- [ ] Cây khái niệm điều khiển sưởi — chỗ khó nhất — đã đủ rõ để người mới không nhầm chưa?
- [ ] Ba mâu thuẫn tài liệu đã trình bày công bằng chưa (nêu cả hai phía, không tự phán bên nào đúng)?
- [ ] Có chỗ nào tôi viết theo trí nhớ mà **quên kiểm lại file gốc** không?
- [ ] Có chỗ nào **suy đoán bị viết như sự thật** không?

### Vòng 2 — Đối chiếu toàn bộ với bộ khung này

- [ ] Đủ 10 chương chưa? Đủ 7 phụ lục chưa?
- [ ] Mỗi chương có đủ các mục "nội dung bắt buộc" liệt kê ở §3 chưa?
- [ ] Cả 6 nguyên tắc ở §4 có được tuân thủ xuyên suốt không?
- [ ] Cả 6 loại box ký hiệu có được dùng không, hay có loại bị bỏ quên?
- [ ] Mỗi chương có mục "Kiểm tra nhanh" chưa?
- [ ] 26 ảnh trong bảng kê §7 có được nhúng đủ không, hay có ảnh copy ra rồi bỏ không dùng?
- [ ] Mục lục đầu file có khớp với nội dung thật không?

### Vòng 3 — Rà tiêu chí / quan điểm bị bỏ sót

Vòng này không có checklist cố định. Đặt lại các câu hỏi gốc:

- [ ] **Người mới học IT** đọc có hiểu không, hay vẫn giả định quá nhiều kiến thức nền?
- [ ] Ba câu hỏi lớn ở §1 đã được trả lời **rõ ràng và tìm thấy dễ dàng** chưa?
- [ ] Có góc nhìn nào của dự án bị bỏ quên không? (ví dụ: góc nhìn khách hàng, góc nhìn vận hành, góc nhìn rủi ro, góc nhìn tiền bạc)
- [ ] Tài liệu có nói rõ **giới hạn của chính nó** không — chỗ nào chưa chắc, chỗ nào cần tự đi xác minh?
- [ ] Nếu ngày mai dự án thay đổi, người đọc có biết **phải cập nhật chỗ nào** không?

---

## 9. Cách bảo trì

| Khi nào cập nhật | Làm gì |
|---|---|
| Repo dự án có thay đổi lớn (đổi scope, chốt một vấn đề đang mở) | Sửa chương liên quan + đổi ngày đối chiếu ở đầu tài liệu |
| Số dòng trích dẫn không còn khớp | Tìm lại bằng **tên mục** (lý do quy ước §6 bắt ghi cả hai) |
| Ảnh gốc trong repo thay đổi | Copy lại theo bảng kê §7 |
| Một mâu thuẫn ở phụ lục B được giải quyết | Chuyển sang phần nội dung chính, xoá khỏi B, cập nhật `qa_kitagas.md` |

**Lưu ý**: thư mục này nằm **ngoài** repo dự án nên **không** kích hoạt quy tắc "sửa docs thì phải cập nhật README + CLAUDE.md" ghi tại `eminel_gw_project/CLAUDE.md` dòng 27–34. Đây là lý do đặt nó ở ngoài.
