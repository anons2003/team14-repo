# 🎬 BudgetBot W7 — Kịch bản Quay Demo Recording

> **Tổng thời lượng mục tiêu:** 5–7 phút  
> **Tool quay:** OBS / Loom / Windows Game Bar (Win+G)  
> **Độ phân giải:** 1920×1080, 30fps  
> **Trình duyệt:** Chrome, phóng to 100%, ẩn bookmark bar  
> **URL cần mở sẵn:** https://budgetbot.topjob.id.vn  

---

## 📋 Tổng quan các cảnh

| # | Cảnh | Thời lượng | Nội dung chính |
|---|---|---|---|
| 1 | Mở đầu + Architecture | ~60s | Giới thiệu hệ thống, sơ đồ AWS |
| 2 | Upload CSV + AI phân loại | ~90s | Happy path: upload → Bedrock → DynamoDB |
| 3 | Dashboard Overview | ~60s | Biểu đồ chi tiêu, lọc tháng |
| 4 | AI Safety Guard | ~60s | Bảo mật 2 lớp, demo block input độc hại |
| 5 | Review Queue + User Correction | ~60s | Low-confidence → tay sửa → lưu lại |
| 6 | Persistent State (bonus) | ~30s | Refresh browser → data vẫn còn |

---

## 🎬 CẢNH 1 — Mở đầu & Kiến trúc AWS (60 giây)

### Màn hình hiển thị
- Mở slide hoặc file `docs/architecture.png` toàn màn hình

### Lời dẫn (đọc hoặc ghi âm)

> "Đây là BudgetBot — AI Money Coach, sản phẩm của Team 14 trong W7 Capstone Hackathon.
>
> BudgetBot giải quyết bài toán: bạn upload một file sao kê ngân hàng CSV, hệ thống tự động phân loại từng giao dịch bằng Amazon Bedrock Nova Micro, lưu kết quả vào DynamoDB, và hiển thị dashboard chi tiêu trực quan.
>
> Kiến trúc gồm 7 mandatory capabilities của W7:
> - **Capability 1** — Entry: Route 53 → CloudFront HTTPS → S3 frontend
> - **Capability 2** — Compute: AWS Lambda chạy FastAPI
> - **Capability 3** — AI: Amazon Bedrock InvokeModel, model Nova Micro
> - **Capability 4** — Persistence: DynamoDB PAY_PER_REQUEST
> - **Capability 5** — Object Storage: S3 lưu raw CSV
> - **Capability 6** — Network: Lambda trong private subnet, không có NAT, dùng VPC Endpoints
> - **Capability 7** — IAM least-privilege execution role
>
> Và Optional #8: Full Observability với CloudWatch dashboard, custom metrics, alarm, Log Insights."

### Action
- Dùng chuột trỏ vào từng layer khi đọc
- Zoom vào phần AI flow (Bedrock → Lambda → DynamoDB) trong 3 giây

---

## 🎬 CẢNH 2 — Upload CSV + AI phân loại (90 giây)

### Màn hình hiển thị
- Tab trình duyệt: `https://budgetbot.topjob.id.vn`
- File CSV chuẩn bị sẵn: `supporting_docs/test_transactions.csv` hoặc `sample_data/bank_statement_q2_2026.csv`

### Bước thực hiện

**[0:00–0:10]** Mở trang chủ, show URL trên thanh địa chỉ

> "Trainer mở URL `budgetbot.topjob.id.vn`. Trang load qua CloudFront HTTPS — đây là Capability #1."

**[0:10–0:25]** Click tab **"Overview"** (sidebar bên trái), thấy trạng thái trống

> "Hiện tại chưa có dữ liệu. Tôi sẽ upload một file sao kê."

**[0:25–0:45]** Kéo thả hoặc click nút **"📂 Upload CSV"**, chọn file CSV

> "File CSV này có 91 giao dịch thực từ tháng 3–5/2026. Các mô tả như 'Vietnam Airlines', 'KFC District 1', 'Unknown merchant POS' — đây là dữ liệu bank statement thực."

**[0:45–0:70]** Chờ loading bar, show message "Processing X transactions..."

> "Lambda nhận file, lưu raw CSV vào S3 — Capability #5. Sau đó gọi Amazon Bedrock InvokeModel với từng batch giao dịch — Capability #3. Kết quả được persist vào DynamoDB — Capability #4."

**[0:70–1:30]** Upload xong → Dashboard tự refresh, show tiles:

> "Xong. Hệ thống đã phân loại 91 giao dịch. Ta thấy:
> - Cash Inflow: tổng tiền vào
> - Cash Outflow: tổng chi tiêu
> - Net Balance: số dư ròng
> - Threats Blocked: input độc hại đã chặn
>
> Hai biểu đồ donut: bên trái là chi tiêu theo danh mục (đỏ), bên phải là dòng tiền vào (xanh)."

---

## 🎬 CẢNH 3 — Dashboard Overview: Biểu đồ & Lọc tháng (60 giây)

### Màn hình hiển thị
- Tab Overview vừa load xong

### Bước thực hiện

**[0:00–0:15]** Hover vào từng slice trên donut chart đỏ

> "Donut chart bên trái breakdown chi tiêu: Food chiếm nhiều nhất, kế đến Transport, Subscriptions..."

**[0:15–0:30]** Scroll xuống xem bar chart **"Category Breakdown"**

> "Bar chart này so sánh tất cả category — màu đỏ là chi tiêu, màu xanh là thu nhập."

**[0:30–0:50]** Click dropdown **"Filter by month"** → chọn `2026-05`

> "Tôi lọc tháng 5/2026. Dashboard tự cập nhật — biểu đồ và bảng giao dịch đều filter theo tháng này. Đây là live filtering, không cần reload trang."

**[0:50–1:00]** Chuyển sang tab **"All Transactions"**

> "Tab All Transactions hiển thị danh sách giao dịch, phân trang 30 dòng mỗi trang — filter tháng vẫn được giữ nguyên."

---

## 🎬 CẢNH 4 — AI Safety Guard: 2 lớp bảo vệ (60 giây)

### Màn hình hiển thị
- Click tab **"AI Safety Guard"** trên sidebar

### Bước thực hiện

**[0:00–0:15]** Show màn hình AI Safety Guard

> "Đây là tính năng bảo mật — BudgetBot có 2 lớp bảo vệ trước khi input đến AI:"

**[0:15–0:30]** Trỏ vào **Layer 1 card**

> "Layer 1 — Input Validation: kiểm tra độ dài (max 255 ký tự) và regex pattern. Chặn các ký tự đặc biệt nguy hiểm ngay từ đầu, trước khi xử lý."

**[0:30–0:45]** Trỏ vào **Layer 2 card**

> "Layer 2 — Threat Pattern Matching: phát hiện SQL injection, command injection, template injection, và prompt injection bằng regex patterns."

**[0:45–1:00]** Click nút **"🧪 Run Safety Test"**

> "Tôi chạy bộ test với 8 input độc hại:
> - `{{constructor.constructor('return this')()}}` — template injection
> - `'; DROP TABLE transactions; --` — SQL injection
> - `${process.env.SECRET}` — command injection
> - `UNION SELECT * FROM users` — SQL injection
> - `Ignore previous instructions` — prompt injection
>
> Kết quả: 5 bị BLOCK, 3 input bình thường được cho qua. Hệ thống hoạt động đúng."

*Show bảng kết quả test với màu đỏ/xanh*

---

## 🎬 CẢNH 5 — Review Queue & User Correction (60 giây)

### Màn hình hiển thị
- Click tab **"Review Queue"** trên sidebar

### Bước thực hiện

**[0:00–0:15]** Show danh sách giao dịch low-confidence

> "Review Queue hiển thị các giao dịch mà AI không chắc chắn — confidence = low. Ví dụ:
> - 'Unknown merchant POS' → AI đoán Other (sai)
> - 'Vietnam Airlines HAN-SGN' → AI đoán Other (sai)"

**[0:15–0:35]** Click dropdown category của **"Unknown merchant POS"** → chọn **"Shopping"**

> "Tôi sửa 'Unknown merchant POS' thành 'Shopping' vì đây là giao dịch tại quầy POS vật lý. User correction gọi `POST /correct`..."

**[0:35–0:50]** Click **"✓ Save"** → row biến mất khỏi queue hoặc hiện "corrected"

> "DynamoDB được cập nhật: category = Shopping, confidence = human. AI đã học từ correction này."

**[0:50–1:00]** Hover vào giao dịch trong All Transactions để thấy label "human"

> "Trong danh sách giao dịch, giao dịch này giờ hiển thị đã được human-verified."

---

## 🎬 CẢNH 6 — Persistent State Demo (30 giây)

### Bước thực hiện

**[0:00–0:10]** Đang ở trang hiển thị đủ data → nhấn **F5** refresh trang

> "Tôi refresh hoàn toàn trình duyệt..."

**[0:10–0:25]** Trang load lại → tự động show lại 91 giao dịch, biểu đồ, tiles

> "Data vẫn còn. DynamoDB lưu tất cả trạng thái qua các session — đây là Capability #4 Persistent State."

**[0:25–0:30]** Mở tab mới, nhập cùng URL, thấy data vẫn load

> "Mở tab mới, cùng URL — data vẫn ở đó. Persistent state hoạt động hoàn toàn."

---

## 🎬 CẢNH 7 — Kết thúc (15 giây, optional)

> "BudgetBot — 7 mandatory AWS capabilities, AI phân loại 91 giao dịch với accuracy 70% baseline và gần 100% với Review Queue, 2-layer safety protection, Full Observability với CloudWatch, triển khai tự động qua CI/CD, và custom domain HTTPS.
>
> Team 14 — W7 Capstone Hackathon 2026."

---

## 📋 Checklist trước khi bấm Record

- [ ] Chrome đang mở `https://budgetbot.topjob.id.vn` (load được, không lỗi)
- [ ] File CSV `supporting_docs/test_transactions.csv` (hoặc `sample_data/bank_statement_q2_2026.csv`) để sẵn ở Desktop
- [ ] **Clear data cũ trước:** gọi `DELETE /transactions` hoặc đổi user header để bắt đầu sạch
- [ ] Tắt notification Windows, không có Teams/Zalo popup
- [ ] Micro kiểm tra (nếu record có giọng)
- [ ] OBS/Loom đang capture đúng màn hình
- [ ] Màn hình độ phân giải 1920×1080, zoom Chrome = 100%
- [ ] Ẩn bookmark bar (Ctrl+Shift+B)
- [ ] Xem thử 1 lần không record trước

---

## 💡 Tips quay

| Tình huống | Xử lý |
|---|---|
| Upload bị lỗi | Kiểm tra server local còn chạy không, hoặc dùng production URL |
| Loading quá chậm | Quay local (`http://127.0.0.1:8006`) để nhanh hơn, sau đó cut sang production URL |
| Lỡ lời | Không cần re-record toàn bộ — cắt bằng DaVinci/Clipchamp |
| Muốn show architecture | Mở `docs/architecture.png` full screen trong Paint hoặc browser |
| Demo bị lag | Giảm số transaction trong CSV xuống ~20 dòng cho demo nhanh |

---

## 🗂 Cấu trúc file nên lưu

```
docs/
├── demo.mp4                    ← file quay cuối cùng (upload lên GitHub hoặc YouTube)
├── evidence_screenshots/
│   └── demo/
│       ├── 01_upload_csv.png
│       ├── 02_dashboard_overview.png
│       ├── 03_donut_charts.png
│       ├── 04_safety_guard.png
│       └── 05_review_queue.png
```
