# Đề xuất thay đổi cấu trúc thư mục syp-eminelstandard-app — E-Smart / Eminel

**Gửi tới:** mui Lab
**Người thực hiện:** SYP
**Phạm vi:** Bước 1 — Đề xuất cấu trúc thư mục sau thay đổi (theo yêu cầu「依頼: モバイルアプリ構成の変更」/ "Yêu cầu: Thay đổi cấu trúc mobile app")
**Trạng thái:** Bản nháp để review

---

## Mục lục

1. Bối cảnh và yêu cầu
2. Cách tiếp cận và nguồn tham khảo
3. Tiêu chí/quy tắc dẫn dắt phương án
4. Phân tích và căn cứ lựa chọn kiến trúc
5. Giải pháp đề xuất
6. Rủi ro chính cần lưu ý
7. Hạng mục cần khách hàng xác nhận
8. Phụ lục

---

## 1. Bối cảnh và yêu cầu

### 1.1. Bối cảnh

App eGW (**Eminel**) sẽ được phát triển và lưu trữ trong **cùng 1 repo** với app hiện tại **`syp-eminelstandard-app`** (sau đây gọi là **E-Smart**, applicationId hiện tại `jp.co.hokkaido-gas.esta`). Lý do đặt chung 1 repo:

- Muốn **tái sử dụng các thành phần dùng chung** giữa 2 app: UI component, cơ chế đăng nhập, logic chung với E-Smart.
- **Niêm yết trên App Store khác nhau** (E-Smart và Eminel là 2 app riêng biệt trên store), nên cần **build riêng được từng app** từ cùng 1 repo.

### 1.2. Mục tiêu cần đạt được

| # | Mục tiêu | Giải thích |
|---|---|---|
| 1 | Tách thành **tầng app** và **tầng chung**, quản lý nhiều app trong 1 repo | Cấu trúc **dễ thêm code** ở các giai đoạn phát triển sau |
| 2 | **E-Smart** và **Eminel** build được thành app độc lập | `applicationId`/bundle id khác nhau, gói phân phối lên store khác nhau |
| 3 | Thêm code cho Eminel **không ảnh hưởng** đến việc phát triển E-Smart | Chiều ngược lại cũng vậy — thay đổi của 1 app không bắt buộc app kia phải release |

### 1.3. Ràng buộc lịch trình

| Giai đoạn | Nội dung | Hạn |
|---|---|---|
| 1 | Đề xuất cấu trúc thư mục sau thay đổi (SYP) | 8/3 – 8/14 |
| 2 | mui review (mui, SYP) | 8/17 – 8/19 |
| 2a | Phản ánh kết quả review | 8/20 – 8/21 |
| 3 | Triển khai (SYP) | Tuần 8/24 – 8/28 |

Tài liệu này tương ứng với **Bước 1**.

---

## 2. Cách tiếp cận và nguồn tham khảo

Để phương án bám sát chuẩn kỹ thuật nội bộ mui Lab (thay vì áp một kiến trúc phổ quát chưa kiểm chứng), đã khảo sát theo thứ tự ưu tiên 3 nguồn sau:

### 2.1. Repo tham khảo: `kurashi-for-energy`

Đây là repo được **mui Lab chỉ định trực tiếp** trong tài liệu yêu cầu ("tham khảo: cấu trúc tương tự"). Đây là source code đang chạy thực tế của 1 app năng lượng khác của mui Lab, và quan trọng hơn, trong repo có **tài liệu kiến trúc nội bộ dạng quy tắc bắt buộc** (kiến trúc, routing, storage, design system, error handling) do chính team mui Lab soạn và đang áp dụng thực tế — nên đây là **nguồn tham khảo đáng tin cậy nhất** cho việc tái thiết kế `syp-eminelstandard-app`.

**Kết luận rút ra:**
- Không cần tách toàn bộ domain/business logic ra package chung — chỉ tách phần **thực sự dùng chung và không có UI**. Domain riêng của từng app giữ nguyên trong app đó.
- Cơ chế phân biệt nhiều app/brand là **tách theo folder riêng từng app**, không dùng Gradle flavor.
- Có quy tắc bắt buộc về routing, Dependency Injection, design system — mọi thay đổi kiến trúc nên theo để review thuận lợi.

### 2.2. Tài liệu yêu cầu chức năng chi tiết của app Eminel

23 tài liệu yêu cầu chức năng của app Eminel sắp phát triển (nhóm A: tài khoản/điểm/badge, nhóm B: điều khiển thiết bị qua Gateway, nhóm C: biểu đồ/báo cáo năng lượng, nhóm D: thông báo/khảo sát/theo dõi, nhóm E: lỗi hệ thống/log/hỗ trợ/yêu cầu phi chức năng).

**Kết luận rút ra:** Đây là **nguồn quyết định** để phán đoán chính xác "chức năng nào nên dùng chung, chức năng nào nên tách riêng" — không suy đoán từ tên màn hình, mà dựa trên ghi chép trực tiếp trong tài liệu (vd: một chức năng ghi "đã có sẵn ở E-Smart nên không phải yêu cầu mới", hoặc ngược lại "thiết bị/phương thức giao tiếp hoàn toàn khác E-Smart"). Phân loại chi tiết xem chương 4, mục 5.3.

### 2.3. Khảo sát source code hiện tại của `syp-eminelstandard-app`

Khảo sát trực tiếp cấu trúc `lib/`, cấu hình Android/iOS, cấu hình Firebase, CI/CD hiện tại để đánh giá phạm vi thay đổi (chi tiết mục 4.1).

---

## 3. Tiêu chí/quy tắc dẫn dắt phương án

Mọi quyết định kiến trúc trong đề xuất này đều dựa trên 1 trong 4 nhóm tiêu chí sau:

### 3.1. Ràng buộc bắt buộc từ yêu cầu khách hàng

- Việc tách module chung/E-Smart/Eminel **độc lập** với việc cuối cùng build ra 1 hay 2 binary.
- Phải build được thành **2 app thực sự khác nhau** (applicationId, niêm yết trên store khác nhau).
- Thay đổi của 1 app **không bắt buộc** app kia phải **release**.
- Cấu trúc phải **dễ mở rộng** khi thêm chức năng/brand sau này.

### 3.2. Quy tắc kỹ thuật bắt buộc theo chuẩn `kurashi-for-energy`

| Quy tắc | Nội dung |
|---|---|
| Domain logic | Không bắt buộc tách toàn bộ vào package chung — chỉ tách phần thực sự headless (không UI) và thực sự dùng chung |
| Dependency Injection | Khai báo provider trừu tượng tập trung tại 1 chỗ; mỗi app override implementation cụ thể lúc khởi động; không khai báo provider rải rác nhiều nơi |
| Routing | Bắt buộc dùng `go_router`, cấm chuyển màn hình trực tiếp bằng `Navigator.push`; mỗi màn hình khai báo route path rõ ràng — **áp dụng cho app mới**; app hiện tại có thể giữ cách cũ nếu chuyển ngay tạo rủi ro không cần thiết (xem mục 5.4) |
| Design system | Cấm hard-code màu/khoảng cách, bắt buộc dùng design token; khi có từ 2 app/brand trở lên, token phải trừu tượng hóa để mỗi app cung cấp bộ giá trị riêng |
| Phân nhánh theo app/brand trong code | Cấm nhánh kiểu "nếu là app A thì..." trong UI — khác biệt giữa các app xử lý bằng injection/theme, không rẽ nhánh trong widget |
| Build Android | Không dùng Gradle flavor để phân biệt brand — mỗi app 1 subdirectory riêng, applicationId cố định theo từng app |
| CI/CD | Pipeline có tham số chọn app cần build/deploy, secrets tách riêng theo từng app |
| Quản lý workspace | Repo nhiều package (monorepo) khai báo bằng công cụ quản lý workspace kiểu glob pattern |

### 3.3. Tiêu chí phân loại chức năng "chung / riêng E-Smart / riêng Eminel"

1. Ưu tiên **căn cứ trực tiếp trong tài liệu yêu cầu** hơn là suy đoán từ tên màn hình.
2. Nếu 2 app **dùng chung 1 nguồn dữ liệu/backend** (cùng hệ ghi nhận, cùng API) → xếp vào **chung**, dù màn hình hiển thị mỗi app có khác nhau (vd: điểm thưởng).
3. Nếu **phương thức giao tiếp hoặc nguồn dữ liệu hoàn toàn khác nhau**, dù tên chức năng giống nhau → **tách riêng theo app**, không gộp cưỡng ép (vd: automation/dr/sensor — tên giống nhưng đường dữ liệu hoàn toàn khác).
4. Nếu tài liệu **chưa đủ căn cứ để phân loại** → đưa vào danh sách cần xác nhận thêm với khách hàng (chương 7), không tự suy đoán quyết định.

### 3.4. Nguyên tắc quản lý rủi ro khi triển khai

- Không thay đổi identifier (`applicationId`/bundle id) của app đang chạy thực tế trên store.
- Với phần ranh giới dùng chung chưa xác định rõ, ưu tiên **giữ nguyên cấu trúc hiện tại và di chuyển nguyên khối**, thay vì chia nhỏ ngay từ đầu, để giảm rủi ro/công sức không cần thiết.
- Việc chuẩn hóa thành package có thể thực hiện **theo từng giai đoạn**, không cần hoàn thiện 100% ranh giới ngay lần triển khai đầu.

---

## 4. Phân tích và căn cứ lựa chọn kiến trúc

### 4.1. Source code hiện tại của `syp-eminelstandard-app`

| Khía cạnh | Hiện trạng |
|---|---|
| Quy mô | 481 file Dart viết tay/~74.000 dòng (sau khi sinh code tự động là 881 file; file tự sinh chưa commit vào repo) |
| Cấu trúc | Theo **layer** (`data/`, `domain/`, `presentation/`, `server/`) — không theo feature, nhiều file dùng chung cho nhiều màn hình |
| Chuyển màn hình | Kiểu cũ (danh sách route gom vào 1 file, ~30 màn hình), chưa dùng `go_router` |
| Build | Chỉ có 1 project Android/iOS, applicationId truyền động lúc build, chưa có cơ chế build nhiều app/brand |
| Test | Chưa có test tự động (unit/widget/integration) |
| Kết nối thiết bị đa hãng | Xử lý bằng tham số runtime, không tách module theo hãng |
| Chức năng Eminel | **Chưa tồn tại** trong source code hiện tại — toàn bộ là phát triển mới |

### 4.2. Các hướng kiến trúc đã xem xét

Trước khi chốt phương án cuối, đã đánh giá 2 hướng tách package:

| Hướng | Mô tả | Đánh giá |
|---|---|---|
| **A — Tách package chi tiết theo từng chức năng** | Mỗi chức năng (kể cả chức năng riêng của E-Smart) là 1 package Dart độc lập | Về lý thuyết ranh giới rõ nhất, nhưng phải tách toàn bộ layer `domain`/`data` đang dùng chung cho nhiều màn hình → công sức/rủi ro cao, không phù hợp với code hiện tại (ranh giới theo feature chưa có sẵn). Cũng khác chuẩn thực tế mà `kurashi-for-energy` đang áp dụng. |
| **B — Chỉ tách tối thiểu phần thực sự dùng chung (theo chuẩn `kurashi-for-energy`)** | Chỉ đưa vào package chung phần thực sự dùng chung (theme, UI component, utility, một phần domain headless); phần còn lại giữ nguyên trong từng app | Phù hợp với code hiện tại (giảm rủi ro phân loại sai ranh giới), khớp với chuẩn kỹ thuật mui Lab đang vận hành thực tế, công sức thấp hơn nhiều |

**Kết luận:** Chọn **hướng B**. Lý do: vừa đạt 3 mục tiêu ở mục 1.2, vừa giảm thiểu rủi ro kỹ thuật, vừa khớp chuẩn nội bộ mui Lab.

### 4.3. Phân tích phân loại chức năng cụ thể

Đối chiếu tài liệu yêu cầu chức năng Eminel với các nhóm chức năng hiện có của E-Smart, rút ra kết luận dựa trên căn cứ trực tiếp (trích dẫn nội dung tài liệu yêu cầu):

| Chức năng | Phân loại | Căn cứ |
|---|---|---|
| Đăng nhập/Tài khoản | **Chung** | Tài liệu yêu cầu Eminel xác nhận: mọi yêu cầu liên quan đăng nhập đều "đã có sẵn ở E-Smart, không phải yêu cầu mới" — dùng chung nguyên cơ chế xác thực hiện tại |
| Thông báo/Khảo sát/Push notification | **Chung** | Tài liệu yêu cầu Eminel xác nhận: "mọi yêu cầu đã có sẵn ở E-Smart nên không có gì mới" — dùng lại nguyên hệ thống backend hiện tại |
| Điểm/Badge/Rank | **Chung** | Dùng chung sổ cái (ledger) điểm thưởng ngoài với E-Smart, chỉ khác nhau đường lấy điểm giữa các app |
| Vận hành theo lịch, cảm biến nhiệt độ/độ ẩm, theo dõi tại nhà (đã có ở E-Smart) | **Riêng E-Smart** | Tài liệu yêu cầu Eminel xác nhận chức năng Eminel tương ứng dùng **cơ chế hoàn toàn khác** (khác phương thức giao tiếp/nguồn dữ liệu) — không dùng lại, giữ nguyên bên E-Smart |
| Đăng ký/điều khiển thiết bị qua Gateway, đăng ký smart meter | **Riêng Eminel** | Tài liệu yêu cầu Eminel xác nhận: thiết bị/phương thức giao tiếp hoàn toàn khác E-Smart (giao thức riêng của Gateway), phát triển hoàn toàn mới |
| Biểu đồ/báo cáo năng lượng, tình trạng cảm biến, tư vấn tiết kiệm năng lượng | **Riêng Eminel** | Nguồn dữ liệu (smart meter, cảm biến qua Gateway) hoàn toàn khác dữ liệu E-Smart hiện tại |
| Theo dõi (giám sát tại nhà bằng cảm biến hiện diện) | **Riêng Eminel** | Kế thừa từ app Eminel thế hệ trước, E-Smart không có chức năng tương đương |
| Cài đặt (thông tin khách hàng/cài đặt thông báo) | **Chung** | Tài liệu yêu cầu Eminel ghi rõ "mọi yêu cầu đã có sẵn ở hệ hiện tại hoặc ESTA nên không có gì mới" — dùng chung nguyên cơ chế hiện tại. Cài đặt thông báo gắn liền với Push notification (đã xếp chung) |
| Trợ giúp (hướng dẫn sử dụng/FAQ/hướng dẫn dùng) | **Chung** | Cũng ghi "đã có sẵn ở cả hệ hiện tại và ESTA, không có gì mới". Repo tham khảo `kurashi-for-energy` cũng đặt FAQ/liên hệ trong `packages/features/common`, khớp chuẩn nội bộ |
| Thu thập/gửi app log | **Chung (không có màn hình)** | "Đã có sẵn ở cả hệ hiện tại và ESTA, không có gì mới". Vì không có màn hình người dùng thao tác, nên đặt ở **hạ tầng chung** (`packages/utils`, API gửi log ở `packages/data`) thay vì package chức năng |
| Hiển thị lỗi hệ thống | **Phần hiển thị chung / đường dữ liệu riêng theo app** | Nguồn phát sinh lỗi và đường lấy lỗi hoàn toàn khác nhau giữa 2 app (Eminel qua Gateway management cloud, E-Smart qua lỗi thiết bị hiện tại). Tuy nhiên repo tham khảo có sẵn component hiển thị lỗi trong `packages/ui_components`, nên chỉ dùng chung **phần hiển thị** |
| DR (Demand Response — điều chỉnh nhu cầu điện) | **Chỉ giữ chỗ trong thiết kế thư mục lần này** | DR phía Eminel theo tài liệu yêu cầu ghi "**không thuộc phạm vi năm 2026**", ngoài phạm vi triển khai giai đoạn này. Màn hình DR hiện có của E-Smart giữ nguyên trong `apps/e-smart-app` |
| Yêu cầu phi chức năng | **Không thuộc đối tượng phân loại (ràng buộc xuyên suốt)** | Không phải chức năng có màn hình, mà là ràng buộc áp dụng cho toàn bộ 2 app + package chung, nên không đưa vào phân loại thư mục |

**Phát hiện quan trọng về hạ tầng mạng:** Theo tài liệu yêu cầu phi chức năng của Eminel, đường truyền dữ liệu thiết bị Gateway là **kênh riêng** (giao thức MQTT qua Gateway management cloud), hoàn toàn khác kênh REST API hiện tại của E-Smart. Vì vậy, "networking dùng chung" trong đề xuất này **chỉ giới hạn ở REST API thực sự dùng chung** (đăng nhập, thông báo, điểm thưởng...); tầng giao tiếp Gateway được xử lý như hạ tầng riêng của Eminel.

---

## 5. Giải pháp đề xuất

### 5.1. Kiến trúc tổng thể

Theo mô hình **monorepo**, cấu trúc 2 tầng: **tầng app** (`apps/`) và **tầng chung** (`packages/`).

```
                  packages/
   (theme, ui_components, utils, data, features/common)
    — tầng chung, không phụ thuộc vào app nào —
                 │                    │
                 ▼                    ▼
     apps/e-smart-app        apps/e-gw-app
   (app hiện tại,             (app mới,
    giữ logic riêng)           logic riêng Eminel)
```

**Nguyên tắc cốt lõi:** Package chung **không phụ thuộc ngược lại app**; mỗi app tự quyết định cách dùng package chung theo nhu cầu riêng. 2 app **không phụ thuộc lẫn nhau**.

### 5.2. Cấu trúc thư mục chi tiết

```
syp-eminelstandard-app/
├── apps/
│   ├── e-smart-app/                # App hiện tại — di chuyển nguyên trạng
│   │   ├── android/ ios/          #   Giữ nguyên applicationId đang public thực tế
│   │   └── lib/
│   │       ├── main.dart          #   Khởi tạo cung cấp implementation riêng của E-Smart
│   │       ├── data/ domain/ presentation/ server/   # Giữ nguyên cấu trúc hiện tại
│   │       └── router/            #   Bảng chuyển màn hình riêng của E-Smart
│   │
│   └── e-gw-app/                # App mới
│       ├── android/ ios/          #   applicationId mới, cấu hình Firebase mới
│       └── lib/
│           ├── main.dart
│           ├── data/ domain/ presentation/ server/   # Nơi phát triển chức năng mới
│           └── router/
│
├── packages/
│   ├── theme/                     # Design chung: màu, typography, khoảng cách
│   ├── ui_components/             # UI component chung (bao gồm component hiển thị lỗi)
│   ├── utils/                     # Utility chung: logging, thu thập/gửi app log,
│   │                              #   local storage, formatter chung...
│   ├── data/                      # Tầng dữ liệu chung: entities / datastores / repositories /
│   │                              #   REST client (cùng cấu trúc với data package ngoài của repo
│   │                              #   tham khảo, nhưng lần này đặt trong repo)
│   └── features/
│       └── common/                # Logic chung (không UI): đăng nhập, cài đặt (thông tin khách hàng/cài đặt thông báo),
│                                  #   điểm/badge, thông báo/khảo sát/push notification,
│                                  #   trợ giúp (hướng dẫn sử dụng/FAQ)
│
└── (cấu hình quản lý workspace ở root repo)
```

> Tên thư mục `apps/e-smart-app`, `apps/e-gw-app`, `packages/` đã được đối chiếu theo tài liệu định hướng kỹ thuật nội bộ được chia sẻ, và khớp với định hướng tách tầng chung (`packages/`)/tầng app (`apps/`), mỗi app có theme/màu sắc riêng.

**Lý do tách riêng `packages/data` (khác biệt so với repo tham khảo):** Repo tham khảo `kurashi-for-energy` tách tầng dữ liệu (implementation repository, API client) ra **package dữ liệu nằm ngoài repo**. Trong khi đó, `syp-eminelstandard-app` chưa có package ngoài tương đương, và `lib/data`/`lib/server` hiện tại có cấu trúc **gần như giống hệt** package dữ liệu tham khảo (`server/mui_service.dart`, `mui_api_endpoint.dart`, `rest_client/`, `data/{entities,datastores}`). Vì vậy đề xuất này giữ nguyên cấu trúc đó nhưng **di chuyển vào `packages/data` trong cùng repo** — vì hiện 2 app đang ở chung 1 repo nên cách này vẫn đạt mục đích dùng chung; sau này nếu cần tách thành package ngoài thì chỉ cần nhấc nguyên package ra.

### 5.3. Bảng tổng hợp phân loại chức năng

| Nhóm | Vị trí trong cấu trúc mới | Chức năng tương ứng |
|---|---|---|
| **Chung (logic, không màn hình)** | `packages/features/common` | Đăng nhập/tài khoản, **cài đặt (thông tin khách hàng/cài đặt thông báo)**, thông báo, khảo sát, push notification, điểm, badge/rank, **trợ giúp (hướng dẫn sử dụng/FAQ)** |
| **Chung (UI/design)** | `packages/theme` + `packages/ui_components` | Design token, UI component chung, **component hiển thị lỗi** (phần hiển thị lỗi hệ thống) |
| **Chung (hạ tầng không màn hình)** | `packages/utils` | **Thu thập/gửi app log**, logging, local storage |
| **Chung (tầng dữ liệu)** | `packages/data` | REST client dùng chung cho 2 app cùng entities/datastores/repositories (đăng nhập, thông báo, khảo sát, điểm, liên hệ, app log...) |
| **Riêng E-Smart** | `apps/e-smart-app` (giữ nguyên vị trí hiện tại) | Vận hành theo lịch hiện có, kết nối điều hòa/bình nóng lạnh nhiều hãng, điều khiển hồng ngoại, khảo sát riêng E-Smart, màn hình cảm biến/giám sát hiện có, **màn hình DR hiện có**, **đường dữ liệu lỗi thiết bị hiện có** |
| **Riêng Eminel** | `apps/e-gw-app` (phát triển mới) | Đăng ký/điều khiển thiết bị qua Gateway, đăng ký smart meter, biểu đồ/báo cáo năng lượng, tình trạng cảm biến, tư vấn tiết kiệm năng lượng, theo dõi, **lấy lỗi hệ thống nguồn gốc từ E-GW (đường dữ liệu lỗi hệ thống)** |

> **Về phạm vi "chung" (khả năng dùng lại màn hình):** "Chung" trong bảng trên chỉ việc dùng chung **logic, quản lý state, lấy dữ liệu, UI component**. Theo chuẩn kỹ thuật của repo tham khảo, `packages/features/common` **không chứa màn hình** (không phụ thuộc UI framework), `packages/ui_components` chỉ cung cấp **component** (nút, ô nhập, list, modal...). Vì vậy màn hình đăng nhập, màn hình thông báo... sẽ **dùng chung phần xử lý lấy dữ liệu và quản lý state, còn màn hình thì mỗi app tự dựng riêng**. Cách này khớp với yêu cầu "mỗi app muốn đổi theme/màu sắc riêng" — không gộp hẳn file màn hình để 2 app dùng chung 1 bản.

### 5.4. Nguyên tắc kỹ thuật áp dụng

- **Chuyển màn hình (routing):** Áp dụng cách khác nhau cho mỗi app — ưu tiên tiêu chí **giảm thiểu ảnh hưởng đến app E-Smart hiện tại**:
  - `apps/e-smart-app`: **Giữ nguyên cách chuyển màn hình hiện tại**, không đổi logic, di chuyển nguyên trạng — loại bỏ hoàn toàn rủi ro phá vỡ luồng chuyển màn hình đang chạy ổn định.
  - `apps/e-gw-app`: Dùng `go_router` ngay từ đầu — vì là app hoàn toàn mới nên không có rủi ro tương thích ngược, đồng thời khớp chuẩn kỹ thuật của `kurashi-for-energy` cho code mới.
  - Đây là ngoại lệ có chủ đích, sẽ ghi rõ trong tài liệu kỹ thuật để tránh hiểu nhầm là "làm sót"; nếu cần, giai đoạn sau có thể chuyển `e-smart-app` sang `go_router`.
- **Dependency Injection:** Usecase dùng chung khai báo trừu tượng trong package chung, mỗi app cung cấp implementation cụ thể lúc khởi động — cho phép 2 app có hành vi khác nhau tại cùng 1 điểm logic khi cần (vd: sau đăng nhập, mỗi app chuyển đến màn hình chính khác nhau).
- **Design (design system):** Chuẩn hóa design token dạng trừu tượng ngay từ giai đoạn này (vì đây là lần đầu có 2 app), để mỗi app tùy biến UI riêng mà không phá phần chung.
- **Không rẽ nhánh theo app trong UI:** Mọi khác biệt hành vi giữa 2 app xử lý qua cấu hình/injection, không viết điều kiện "app nào" trực tiếp trong màn hình.

### 5.5. Hạ tầng liên quan cần chuẩn bị song song

| Hạng mục | Nội dung |
|---|---|
| Firebase | Tạo Firebase project/app mới cho Eminel (khác project hiện tại) |
| Android | Mỗi app có cấu hình build riêng, applicationId cố định; **cần xác nhận applicationId thực tế đang public của E-Smart trước khi đổi cấu hình** (tránh rủi ro bị store coi là app mới) |
| Ký ứng dụng (keystore) | Mỗi app cần keystore riêng |
| iOS | Cần tạo mới App ID/provisioning profile/certificate trên Apple Developer cho Eminel, và tạo record app mới trên App Store Connect |
| CI/CD | Thêm tham số chọn app cần build/deploy vào pipeline hiện tại |

### 5.6. Lộ trình triển khai theo giai đoạn

| Giai đoạn | Nội dung |
|---|---|
| 1 | Dựng cấu trúc workspace (`apps/`, `packages/`), di chuyển nguyên trạng E-Smart vào `apps/e-smart-app` |
| 2 | Tách package chung (`theme`, `ui_components`, `utils`, `features/common`) từ source code hiện tại |
| 3 | Khởi tạo `apps/e-gw-app` — app shell rỗng dùng `go_router`, xác nhận build/chạy độc lập với E-Smart |
| 4 | Cập nhật CI/CD pipeline hỗ trợ 2 app |
| 5 | Test regression cho `apps/e-smart-app` — xác nhận hành vi hiện tại không đổi sau khi di chuyển vị trí |
| 6 | Bàn giao cấu trúc cho team phát triển chức năng Eminel (bản thân giai đoạn phát triển chức năng nằm ngoài phạm vi tái cấu trúc thư mục lần này) |

### 5.7. Ước lượng công sức

Dựa trên quy mô source code đã khảo sát (mục 4.1), ước lượng công sức cho toàn bộ giai đoạn 1–5 nêu trên (không bao gồm phát triển chức năng nghiệp vụ mới của Eminel): khoảng **15–27 người-ngày** nếu 1 kỹ sư làm full-time. Ước lượng này đã tính đến quyết định giữ nguyên cách chuyển màn hình của `apps/e-smart-app` (mục 5.4) — nếu không có quyết định này, sẽ phải rà soát lại toàn bộ ~30 màn hình hiện có, khiến công sức tăng thêm đáng kể.

So với thời gian triển khai dự kiến trong lịch tổng thể [8/24 – 8/28] (~5 ngày làm việc), có sự chênh lệch, cần trao đổi về phạm vi/nguồn lực trước khi bắt đầu (xem câu hỏi 5, chương 7).

---

## 6. Rủi ro chính cần lưu ý

| # | Rủi ro | Mức độ nghiêm trọng | Biện pháp giảm thiểu |
|---|---|---|---|
| 1 | Vô tình đổi sai identifier (applicationId) của app E-Smart đang chạy thực tế | **Rất cao** | Xác nhận identifier đang chạy thực tế trước khi đổi cấu hình build |
| 2 | Chưa có test tự động nên khó phát hiện sớm regression khi di chuyển lượng lớn source code | Cao | Lập checklist test thủ công dựa trên danh sách màn hình hiện có, trước khi release |
| 3 | E-Smart và Eminel dùng 2 cách chuyển màn hình khác nhau trong cùng 1 repo (quyết định có chủ đích — mục 5.4) | Thấp | Ghi rõ trong tài liệu kỹ thuật để tránh hiểu nhầm "làm sót"; lập kế hoạch thống nhất ở giai đoạn sau nếu cần |
| 4 | Chênh lệch giữa công sức ước lượng và lịch triển khai đã đưa ra | Trung bình–Cao | Trao đổi lại với khách hàng về phạm vi/nguồn lực trước khi bắt đầu |
| 5 | Các hạng mục hạ tầng ngoài source code (Firebase, keystore, đăng ký app lên store) có lead time riêng, không phụ thuộc tiến độ code | Trung bình | Bắt đầu song song các hạng mục hạ tầng này ngay từ giai đoạn review, không chờ code xong |

---

## 7. Hạng mục cần khách hàng xác nhận

| # | Hạng mục cần xác nhận | Lý do quan trọng |
|---|---|---|
| 1 | Xác nhận applicationId/bundle id chính thức của `e-gw-app` | Ảnh hưởng trực tiếp đến cấu hình build, Firebase, keystore |
| 2 | Xác nhận applicationId **bản Android** đang public của E-Smart (bản iOS đã xác nhận trong repo là `jp.co.hokkaido-gas.esta`; bản Android truyền `APP_ID` qua biến môi trường lúc build nên không xác nhận được từ repo) | Tránh rủi ro bị store coi là app mới khi đổi cấu hình |
| 3 | Phạm vi giai đoạn triển khai [8/24 – 8/28] có bao gồm phát triển chức năng nghiệp vụ mới của Eminel không, hay chỉ tái cấu trúc thư mục + dựng app shell rỗng | Ảnh hưởng lớn đến công sức thực tế và khả năng đạt lịch trình |
| 4 | Có cần Single Sign-On (SSO) giữa app E-Smart và Eminel không | Tài liệu yêu cầu Eminel chưa xác nhận rõ điểm này — ảnh hưởng đến phạm vi dùng chung cơ chế đăng nhập |
| 5 | Ai sẽ dựng các hạng mục hạ tầng mới cho Eminel (Firebase project, record app trên App Store/Play Store, keystore), bắt đầu khi nào | Các hạng mục này có lead time riêng, cần bắt đầu sớm để không làm chậm tiến độ tổng thể |
| 6 | Một số nội dung trong chính tài liệu yêu cầu chức năng Eminel còn ghi "chưa xác định" (vd: nơi lưu trữ system log, hành vi cụ thể của một số màn hình cài đặt/tư vấn tiết kiệm năng lượng, tần suất cập nhật dữ liệu phía Gateway) | Cần chốt trước khi triển khai chi tiết business logic (không ảnh hưởng đến việc cấu hình thư mục ở giai đoạn này) |

---

## 8. Phụ lục

### 8.1. Tài liệu tham khảo

- Tài liệu yêu cầu gốc: 「依頼: モバイルアプリ構成の変更」(Yêu cầu: Thay đổi cấu trúc mobile app) (mui Lab)
- Repo tham khảo kiến trúc: `kurashi-for-energy` (mui Lab)
- Tài liệu yêu cầu chức năng chi tiết app Eminel: 23 tài liệu do mui Lab cung cấp (A01–A04, B01–B06, C01–C05, D01–D04, E01–E04)

### 8.2. Ghi chú

Mọi số liệu, trích dẫn, kết luận phân loại trong tài liệu này đều đã đối chiếu trực tiếp với nội dung tài liệu yêu cầu và source code tham khảo tại thời điểm khảo sát. Tài liệu phân tích kỹ thuật chi tiết hơn (bảng ước lượng công sức theo từng hạng mục công việc, phân tích rủi ro mở rộng, trích dẫn nguyên văn tiếng Nhật) được lưu riêng phục vụ nội bộ team triển khai, có thể cung cấp thêm khi cần.
