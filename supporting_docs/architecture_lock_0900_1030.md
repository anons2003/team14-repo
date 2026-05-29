# 09:00-10:30 — Chốt Kiến Trúc

Owner: Project Lead

Mục tiêu của phiên này là khóa scope, service choices, owner, architecture diagram, và optional capability trước khi team bắt đầu deploy hạ tầng. Sau phiên này, mọi thành viên phải hiểu BudgetBot giải quyết bài toán gì, service nào cover từng mandatory capability, ai chịu trách nhiệm phần nào, và demo path cuối cùng đi qua những bước nào.

## 1. Xác Nhận Scope BudgetBot

BudgetBot là ứng dụng **AI Money Coach** cho domain FinTech. Người dùng upload file sao kê ngân hàng dạng CSV, hệ thống đọc các giao dịch, dùng Amazon Bedrock để phân loại chi tiêu, lưu kết quả vào database, và hiển thị summary chi tiêu theo category.

Happy path cần demo:

1. Trainer mở public HTTPS URL.
2. Người dùng upload file CSV sao kê ngân hàng.
3. Backend lưu file CSV gốc vào S3 raw statements bucket.
4. Lambda parse transaction từ CSV.
5. Lambda gửi mô tả giao dịch sang Amazon Bedrock Runtime.
6. Bedrock trả về `category` và `confidence`.
7. Lambda lưu transaction đã phân loại vào DynamoDB.
8. Người dùng xem danh sách giao dịch và spending summary.
9. Refresh browser vẫn đọc lại được dữ liệu đã lưu.
10. Team mở CloudWatch để chứng minh logs, metrics, dashboard, và alarm.

In scope:

- Upload CSV bank statement.
- Parse transaction fields: `date`, `description`, `amount`.
- Classify transactions bằng Bedrock Haiku.
- Store raw uploaded CSV in S3.
- Store categorized transactions in DynamoDB.
- Show transaction list and category summary in frontend.
- Use public HTTPS URL.
- Use IAM least privilege.
- Show CloudWatch observability evidence.

Out of scope:

- Banking integration thật.
- Dữ liệu tài chính thật.
- Full Cognito signup/login flow.
- RAG hoặc Bedrock Knowledge Base.
- Multi-region failover.
- RDS migration.
- Mobile app.
- Custom domain nếu chưa xong mandatory flow.

## 2. Xác Nhận Service Cho Đủ 7 Mandatory Capabilities

| # | Mandatory Capability | Service Chọn | BudgetBot Dùng Để Làm Gì | Lý Do Chọn |
|---|---|---|---|---|
| 1 | User Interface | CloudFront + S3 static frontend + API Gateway HTTP API | Public HTTPS URL, frontend static UI, API entry cho upload/summary/transactions | Serverless, chi phí thấp, dễ demo, không cần quản lý server |
| 2 | Application Compute | AWS Lambda Python/FastAPI | Xử lý request, parse CSV, gọi Bedrock, ghi S3/DynamoDB, trả summary | Phù hợp workload ngắn, pay-per-use, đủ cho hackathon |
| 3 | AI / ML Feature | Amazon Bedrock Runtime + Claude 3 Haiku | Phân loại giao dịch thành category và confidence | Direct classification không cần RAG, Haiku rẻ và đủ nhanh |
| 4 | Data Persistence | Amazon DynamoDB | Lưu categorized transactions theo `user_id` và sort key `TXN#date#id` | NoSQL access pattern đơn giản, managed service, không phải vận hành database |
| 5 | Object Storage | Amazon S3 raw statements bucket | Lưu file CSV gốc người dùng upload | Object storage chuẩn cho file/blob, bật encryption và Block Public Access |
| 6 | Network Foundation | VPC private subnets + VPC endpoints | Lambda chạy trong private subnets, AWS service access qua endpoints, không NAT Gateway | Chứng minh network isolation, tránh public backend path và giảm cost |
| 7 | Identity & Access | IAM least-privilege Lambda execution role | Scope quyền Lambda tới đúng S3 bucket, DynamoDB table, Bedrock model, CloudWatch logs/metrics | Đáp ứng baseline security, không dùng wildcard/admin policy |

One-liner cho slide:

```text
BudgetBot covers all 7 mandatory capabilities with CloudFront/S3/API Gateway for the public UI, Lambda for compute, Bedrock for AI classification, DynamoDB for persistence, S3 for raw statements, VPC private subnets plus endpoints for network isolation, and IAM least-privilege roles for access control.
```

## 3. Chia Owner Cuối Cùng

| Owner | Phụ Trách Chính | Mandatory / Optional | Deliverable |
|---|---|---|---|
| Project Lead / Presenter | Scope, timeline, final story, demo script, QnA coordination | Overall | Demo script, architecture walkthrough, owner alignment |
| Infra Owner | S3 buckets, CloudFront, API Gateway, VPC, endpoints, tags, deploy foundation | #1, #5, #6 | Public URL, network foundation, tagged resources |
| Backend Owner | Lambda FastAPI, API routes, S3/DynamoDB integration | #2, #4, #5 | `/upload`, `/summary`, `/transactions`, `/health` |
| AI Owner | Bedrock prompt, JSON response contract, confidence handling | #3 | AI classification result with category/confidence |
| Security/IAM Owner | Lambda execution role, scoped policies, evidence screenshots | #7 | IAM policy proof and security notes |
| Observability Owner | CloudWatch dashboard, custom metrics, alarm, Logs Insights query | Optional #8 | Monitoring evidence for `docs/W7_evidence.md` |
| Evidence + Cost Owner | Evidence Pack, Cost Explorer screenshots, teardown checklist | Evidence | `docs/W7_evidence.md`, cost screenshots, teardown doc |

Nếu team ít người, gộp vai:

1. Project Lead + Evidence + Cost.
2. Infra + Network + IAM.
3. Backend + Data.
4. AI + Observability.

QnA rule: mỗi owner phải trả lời được service mình chọn, vì sao chọn, alternative là gì, và trade-off chi phí/bảo mật/vận hành.

## 4. Vẽ Architecture Diagram Bản Đầu

Architecture diagram bản đầu phải phản ánh đúng hệ thống sẽ deploy, không vẽ component ảo.

Các điểm bắt buộc trên diagram:

- Users mở public HTTPS URL qua CloudFront.
- CloudFront serve static frontend từ private S3 frontend bucket bằng OAC.
- Browser gọi API Gateway HTTP API.
- API Gateway nằm ngoài VPC vì là AWS managed regional service.
- Lambda FastAPI backend chạy trong private subnets across AZ A và AZ B.
- Lambda không có public IP.
- S3 raw statements bucket nằm ngoài VPC, private, Block Public Access, encryption enabled.
- DynamoDB nằm ngoài VPC vì là AWS managed regional NoSQL service.
- Bedrock Runtime nằm ngoài VPC vì là AWS managed AI service.
- CloudWatch nằm ngoài VPC và nhận logs/custom metrics.
- VPC có private subnets, VPC endpoints, và no NAT Gateway.
- S3 Gateway Endpoint cho raw statement upload.
- DynamoDB Gateway Endpoint cho transaction persistence.
- Bedrock Runtime Interface Endpoint cho AI call.
- IAM execution role least privilege.

Data flow chính:

1. User mở CloudFront HTTPS URL.
2. CloudFront serve frontend từ S3 private bucket.
3. Browser gọi API Gateway HTTP API.
4. API Gateway invoke Lambda.
5. Lambda lưu CSV gốc vào S3 raw bucket.
6. Lambda gửi transaction descriptions sang Bedrock.
7. Bedrock trả JSON category/confidence.
8. Lambda lưu categorized transactions vào DynamoDB.
9. Frontend gọi `/summary` hoặc `/transactions`; Lambda query DynamoDB và trả kết quả.
10. Lambda ghi logs/custom metrics vào CloudWatch.
11. IAM role giới hạn quyền truy cập của Lambda.

Diagram artifact:

- Draw.io version: `supporting_docs/budgetbot-aws-architecture.drawio`
- UML version: `supporting_docs/architecture.puml`
- Final PNG for evidence: `docs/architecture.png`

## 5. Chốt Optional Capability: Full Observability

Team 14 chọn **Optional Capability #8: Full Observability**.

Lý do chọn:

- Phù hợp với BudgetBot vì cần chứng minh upload và AI classification chạy thật.
- Dễ demo trong thời gian hackathon.
- Tăng điểm Architecture và Working Deployment nếu có dashboard/alarm rõ ràng.
- Không làm tăng độ phức tạp như multi-region hoặc full Cognito.

Required observability evidence:

- CloudWatch dashboard.
- Ít nhất 1 custom metric bằng `cloudwatch:PutMetricData`.
- Ít nhất 1 alarm ở trạng thái `OK` hoặc `ALARM`, không để `INSUFFICIENT_DATA`.
- Ít nhất 1 saved Logs Insights query.

Custom metrics sẽ dùng:

- `UploadSucceeded`
- `TransactionsCategorized`
- `LowConfidenceTransactions`
- `BedrockLatencyMs`

Logs Insights query đề xuất:

```sql
fields @timestamp, @message
| filter @message like /upload|Bedrock|classification|summary/
| sort @timestamp desc
| limit 50
```

Alarm đề xuất:

```text
Alarm name: BudgetBot-LowConfidenceTransactions-Alarm
Metric: LowConfidenceTransactions
Condition: >= 1 for 1 datapoint within 5 minutes
Purpose: Show when AI classification needs human review.
```

Slide one-liner:

```text
Team 14 chooses Optional Capability #8: Full Observability. We demonstrate CloudWatch dashboard, custom metrics, one alarm in OK/ALARM state, and one Logs Insights query for the BudgetBot upload/classification path.
```

## Definition Of Done For 09:00-10:30

- [x] BudgetBot scope is locked.
- [x] 7 mandatory capabilities are mapped to named AWS services.
- [x] Final owners are assigned.
- [x] Architecture diagram direction is approved.
- [x] Optional capability is locked as Full Observability.
- [x] Team can explain the happy path and service choices before deploying.
