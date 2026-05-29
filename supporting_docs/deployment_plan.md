# Kế Hoạch Triển Khai Team 14 — BudgetBot

## Mục Tiêu

Triển khai BudgetBot thành một AI SaaS demo có public HTTPS URL cho W7.

Happy path:

1. Người dùng mở CloudFront URL.
2. Người dùng upload file sao kê ngân hàng dạng CSV.
3. Backend lưu file CSV gốc vào S3.
4. Lambda gọi Amazon Bedrock để phân loại giao dịch.
5. Các giao dịch đã phân loại được lưu vào DynamoDB.
6. Người dùng xem tổng quan chi tiêu và danh sách giao dịch sau khi refresh.
7. Team trình bày CloudWatch monitoring và Cost Explorer evidence.

## Kiến Trúc Cuối

| Năng lực W7 | Service | Người phụ trách |
|---|---|---|
| User Interface | S3 static frontend + CloudFront HTTPS | Infra owner |
| API Entry | API Gateway HTTP API | Backend owner |
| Application Compute | Lambda Python / FastAPI | Backend owner |
| AI / ML Feature | Bedrock InvokeModel | AI owner |
| Data Persistence | DynamoDB | Data owner |
| Object Storage | S3 upload bucket | Infra owner |
| Network Foundation | Không public DB, dùng VPC endpoints nếu cần, không dùng NAT Gateway | Infra owner |
| Identity & Access | IAM least-privilege Lambda role | Infra + Backend owners |
| Optional Capability | CloudWatch dashboard + custom metrics + alarm + Logs Insights query | Observability owner |

## Chia Vai Team

| Vai trò | Trách nhiệm chính | Deliverables |
|---|---|---|
| Project Lead / Presenter | Giữ scope gọn, điều phối checkpoint, nắm câu chuyện cuối | Demo script, flow slide, QnA prep |
| Infra Owner | AWS resources, IAM, S3, CloudFront, API Gateway, tags, budget safety | Public URL, IAM policies, tagged resources |
| Backend + AI Owner | Lambda app, Bedrock prompt, classification API, error logs | Endpoint upload/classify/summary chạy được |
| Data Owner | DynamoDB table design, transaction persistence, review queue | Data model, bằng chứng persistence, sample records |
| Evidence + Cost Owner | Evidence Pack, screenshots, Cost Explorer, teardown checklist | `docs/W7_evidence.md`, cost screenshots, teardown doc |
| Observability Owner | CloudWatch dashboard, custom metric, alarm, Log Insights | Monitoring screenshots và alarm proof |

Nếu team ít người, gộp vai theo thứ tự:

1. Project Lead + Evidence
2. Infra + Observability
3. Backend + AI + Data

## Day 0 — Checklist Pre-flight

Hoàn thành trước khi deploy bất kỳ resource tốn tiền nào.

- [ ] AWS root MFA đã bật.
- [ ] AWS Budget alert đặt ở mức `$80`.
- [ ] Email SNS của budget alert đã confirm.
- [ ] Cost Anomaly Detection đã bật.
- [ ] Bedrock model access đã bật cho model nhóm chọn.
- [ ] Thống nhất tags:
  - `Project=W7Capstone`
  - `Team=G14`
  - `Owner=<member-name>`
  - `Environment=hackathon`
- [ ] GitHub repo public và truy cập được.
- [ ] Đã tạo `docs/W7_evidence.md`.
- [ ] Đã có bản nháp architecture diagram.

## Day 1 — Hạ Tầng + Happy Path

### 09:00-10:30 — Chốt Kiến Trúc

Owner: Project Lead

- [ ] Xác nhận scope BudgetBot.
- [ ] Xác nhận service cho đủ 7 mandatory capabilities.
- [ ] Chia owner cuối cùng.
- [ ] Vẽ architecture diagram bản đầu.
- [x] Chốt optional capability: Full Observability.

### 10:30-11:00 — Safety Check

Owner: Evidence + Cost Owner

- [ ] Show Budget alert.
- [ ] Show SNS confirmation.
- [ ] Show Cost Anomaly Detection.
- [ ] Show Bedrock access.
- [ ] Confirm tagging convention.

### 11:00-13:00 — Tạo Foundation Resources

Owner: Infra Owner

- [ ] Tạo S3 frontend bucket.
- [ ] Tạo S3 upload bucket.
- [ ] Bật S3 Block Public Access.
- [ ] Bật encryption.
- [ ] Tạo DynamoDB table.
- [ ] Tạo Lambda execution role với least privilege.
- [ ] Gắn tags cho toàn bộ resources.

### 14:00-16:30 — Core Services

Owners: Infra Owner + Backend Owner + Data Owner

- [ ] Deploy Lambda.
- [ ] Configure API Gateway HTTP API.
- [ ] Cấu hình frontend API base URL.
- [ ] Test `/health`.
- [ ] Test DynamoDB write/read.
- [ ] Test S3 upload.
- [ ] Test một Bedrock InvokeModel call từ Lambda.

### 16:30-17:00 — Chốt Day 1

Owner: Project Lead

- [ ] Public URL load được.
- [ ] API trả health.
- [ ] Ghi và đọc được một transaction.
- [ ] Bedrock response xuất hiện trong CloudWatch logs.
- [ ] Chụp Day 1 Cost Explorer screenshot.
- [ ] Commit code và docs hiện tại.

## Day 2 — AI Feature + Observability + Evidence

### 09:00-09:30 — Review Scope

Owner: Project Lead

- [x] Liệt kê cái đã chạy.
- [x] Cắt những phần không cần thiết.
- [x] Xác nhận demo path cuối.

### 09:30-12:00 — Tích Hợp AI

Owner: Backend + AI Owner

- [x] Thay local classifier bằng Bedrock path cho deployed environment.
- [x] Dùng prompt bắt model trả JSON-only.
- [x] Thêm confidence output.
- [x] Thêm low-confidence review queue.
- [x] Batch classify transactions nếu kịp.
- [x] Test bằng `sample_data/bank_statement_q2_2026.csv`.

### 12:00-13:00 — Data Và Summary

Owner: Data Owner

- [x] Lưu categorized transactions vào DynamoDB.
- [x] Query theo `user_id` và month.
- [x] Trả summary theo category.
- [x] Xác nhận data vẫn còn sau khi refresh browser.

### 13:00-14:30 — Optional Capability: Full Observability

Owner: Observability Owner

- [x] Thêm custom metric `UploadSucceeded`.
- [x] Thêm custom metric `TransactionsCategorized`.
- [x] Thêm custom metric `LowConfidenceTransactions`.
- [x] Tạo CloudWatch dashboard.
- [x] Tạo alarm ở trạng thái `OK` hoặc `ALARM`.
- [x] Lưu Logs Insights query.

### 14:30-15:30 — Evidence Pack

Owner: Evidence + Cost Owner

- [ ] Thêm architecture diagram.
- [ ] Thêm service decision table.
- [ ] Thêm IAM/security screenshots.
- [ ] Thêm monitoring screenshots.
- [ ] Thêm Day 2 Cost Explorer screenshot.
- [ ] Hoàn thành 2 decision blocks:
  - DynamoDB over RDS.
  - Bedrock Haiku batch classification over alternatives.

### 15:30-16:30 — Rehearse Demo

Owner: Project Lead

- [ ] Chạy demo end-to-end 2 lần.
- [ ] Test bằng phone hotspot hoặc mạng khác.
- [ ] Record backup demo video.
- [ ] Viết live demo script 7 phút.
- [ ] Chuẩn bị câu trả lời QnA.

### 16:30-17:00 — Final Push

Owner: All

- [ ] Push repo.
- [ ] Export slides thành `docs/slides.pdf`.
- [ ] Check lại public URL.
- [ ] Check total spend.
- [ ] Confirm teardown plan.

## Demo Script

1. Mở public HTTPS URL.
2. Upload sample bank statement.
3. Show AI classification result.
4. Show spending summary by category.
5. Show low-confidence review queue.
6. Refresh browser và show persisted transactions.
7. Mở CloudWatch dashboard.
8. Mở Cost Explorer screenshot/evidence.

## QnA Prep

Tất cả thành viên phải trả lời được các câu này, không chuyển câu hỏi cho người khác:

- Vì sao chọn DynamoDB thay vì RDS?
- Vì sao chọn InvokeModel thay vì Bedrock Knowledge Base?
- Vì sao chọn Haiku thay vì Sonnet?
- Vì sao chọn API Gateway HTTP API thay vì REST API?
- Lambda execution role có những quyền gì?
- Raw uploaded data được lưu ở đâu?
- Làm sao tránh public database exposure?
- Cost driver lớn nhất là gì?
- Nếu model trả low confidence thì xử lý thế nào?
- Thứ tự teardown là gì?

## Cut List

Không làm các phần này trừ khi toàn bộ mục bắt buộc đã xong:

- Full Cognito signup flow.
- Frontend React mới.
- Custom domain.
- CI/CD pipeline.
- Multi-region failover.
- Complex chatbot memory.
- RDS migration.
- Full PDF parsing.

## Teardown Plan

Sau demo:

1. Delete CloudFront distribution.
2. Delete API Gateway.
3. Delete Lambda function.
4. Delete DynamoDB table.
5. Empty và delete S3 buckets.
6. Delete CloudWatch dashboard, alarms, và log groups.
7. Delete VPC endpoints và VPC resources nếu có tạo.
8. Chụp final Cost Explorer screenshot.
9. Hoàn thành `docs/teardown_confirmation.md`.
10. Commit teardown confirmation.
