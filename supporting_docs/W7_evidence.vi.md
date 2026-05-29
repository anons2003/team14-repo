# W7 Evidence Pack — Team 14 BudgetBot — Bản Tiếng Việt

## 1. Trang Bìa

| Mục | Giá trị |
|---|---|
| Nhóm | Team 14 / G14 |
| Domain | FinTech — AI Money Coach / BudgetBot |
| Live public URL | https://budgetbot.topjob.id.vn |
| CloudFront URL | https://d104yk0i41rvg5.cloudfront.net |
| API endpoint | https://mlhwir8gc5.execute-api.ap-southeast-1.amazonaws.com |
| GitHub repo | https://github.com/anons2003/team14-repo |
| AWS account | 325137989598 |
| AWS region | ap-southeast-1 |
| CloudFormation stack | team14-budgetbot-iac |
| Tổng chi phí | TODO: điền từ Cost Explorer screenshot sáng demo |
| Hard cap | $100/nhóm |
| Budget alert | W7-Team14-HardCap-100USD, monthly cost budget $100 |
| Email SNS đã confirm | truclt0311@gmail.com |

### Artifact Bắt Buộc

| Artifact | Trạng thái | Bằng chứng |
|---|---:|---|
| Live HTTPS URL | Xong | `https://budgetbot.topjob.id.vn` trả HTTP 200 qua CloudFront |
| GitHub repo | Xong | `https://github.com/anons2003/team14-repo` |
| Sơ đồ kiến trúc cuối | Xong | `docs/architecture.png` |
| Evidence Pack | Xong | `docs/W7_evidence.md`; bản tiếng Việt lưu ở `supporting_docs/W7_evidence.vi.md` |
| Video demo | Xong | [Google Drive demo video](https://drive.google.com/file/d/1oH1wG4hl6nWI2Uhk2RK6m-2kBWuROAQh/view) |
| Slides PDF | TODO | Thêm `docs/slides.pdf` |
| Teardown confirmation | Đã lên kế hoạch | `docs/teardown_confirmation.md` sau hạn Sun 1/6 EOD |

## 2. Pitch Và Tầm Nhìn

BudgetBot là một AI Money Coach giúp người dùng hiểu nhanh tiền của mình đã đi đâu. Người dùng upload sao kê ngân hàng dạng CSV; BudgetBot lưu file gốc, phân loại từng giao dịch bằng Amazon Bedrock, lưu kết quả vào DynamoDB, hiển thị summary theo category và đưa các giao dịch low-confidence vào review queue.

Người dùng mục tiêu là sinh viên, người mới đi làm, freelancer và chủ doanh nghiệp nhỏ cần nhìn nhanh tình hình chi tiêu mà không muốn tự gắn nhãn từng dòng giao dịch. Sản phẩm tương tự ngoài đời gồm Money Lover, YNAB, Spendee, Monzo/Revolut spending insights và Cake by VPBank. Domain này quan trọng vì dữ liệu tài chính thực tế rất bẩn: mô tả giao dịch ngắn, tên merchant không thống nhất, nhiều dòng mơ hồ hoặc không đủ thông tin. Vì vậy AI chỉ hữu ích khi hệ thống có confidence score và cho phép người dùng sửa kết quả không chắc chắn.

### Demo Flow

1. Trainer mở `https://budgetbot.topjob.id.vn`.
2. Upload `sample_data/bank_statement_q2_2026.csv`.
3. Lambda lưu raw CSV vào S3.
4. Lambda gửi mô tả giao dịch sang Amazon Bedrock InvokeModel.
5. Bedrock trả JSON-only gồm `category` và `confidence`.
6. Lambda lưu categorized transactions vào DynamoDB.
7. UI refresh summary, transaction list, AI performance, failure cases và review queue.
8. Sau khi refresh browser, dữ liệu vẫn còn vì state được lưu trong DynamoDB.

### Ảnh Demo Evidence Đã Gắn

| Screenshot | File | Ghi chú |
|---|---|---|
| Video demo | [Google Drive demo video](https://drive.google.com/file/d/1oH1wG4hl6nWI2Uhk2RK6m-2kBWuROAQh/view) | Video backup demo 3 phút |
| Live URL home | `docs/evidence_screenshots/demo/01_live_url_home.png` | TODO: gắn ảnh public HTTPS landing page |
| Upload success | `docs/evidence_screenshots/demo/02_upload_success.png` | Chứng minh CSV upload và transaction đã classify |

#### Upload Success

![Upload success](./evidence_screenshots/demo/02_upload_success.png)

## 3. Kiến Trúc

![Team 14 BudgetBot AWS Architecture](architecture.png)

### Tóm Tắt Kiến Trúc

Luồng runtime:

`Users -> Route 53 -> CloudFront HTTPS -> private S3 frontend -> API Gateway HTTP API -> Lambda FastAPI -> S3 raw bucket / Bedrock Runtime / DynamoDB / CloudWatch`

Luồng deployment:

`Developer push -> GitHub Actions -> pytest -> build Lambda zip -> S3 artifact bucket -> CloudFormation deploy -> S3 frontend sync -> CloudFront invalidation`

### 7 Mandatory Capabilities

| # | Capability | Service đã triển khai | Bằng chứng / Resource | Lý do chọn |
|---:|---|---|---|---|
| 1 | User-Facing Entry | Route 53 + CloudFront + S3 static frontend + API Gateway HTTP API | `budgetbot.topjob.id.vn`, CloudFront `E349TWP6TRPSOC`, API `mlhwir8gc5` | CloudFront cung cấp HTTPS public và truy cập S3 private qua OAC. API Gateway HTTP API rẻ và đơn giản hơn REST API cho Lambda proxy. |
| 2 | Application Compute | AWS Lambda chạy FastAPI qua Mangum | `team14-budgetbot-cfn-backend`, Python 3.12, 512 MB, timeout 30s | Upload CSV và classify là request-driven workload. Lambda không có idle server cost và deploy nhanh trong hackathon 48 giờ. |
| 3 | AI / ML Feature | Amazon Bedrock Runtime InvokeModel | `AI_MODEL_ID=apac.amazon.nova-micro-v1:0` | BudgetBot cần classify từng transaction, không cần RAG. InvokeModel đơn giản và tiết kiệm hơn Knowledge Base. |
| 4 | Data Persistence | DynamoDB | `team14-budgetbot-cfn-transactions`, PK `user_id`, SK `sk`, PAY_PER_REQUEST, PITR enabled | Access pattern là query theo user/month và summary category. DynamoDB giảm vận hành và tránh chi phí RDS instance/proxy. |
| 5 | Object Storage | Amazon S3 | raw bucket `team14-budgetbot-cfn-raw-325137989598-ap-southeast-1`, frontend bucket `team14-budgetbot-cfn-frontend-325137989598-ap-southeast-1`, artifact bucket `team14-budgetbot-artifacts-325137989598-ap-southeast-1` | S3 phù hợp để lưu raw CSV, static frontend và Lambda artifact. |
| 6 | Network Foundation | VPC, private subnets 2 AZ, security groups, VPC endpoints, không dùng NAT Gateway | VPC `vpc-044f26a2a760491ba`; private subnets `subnet-0acedaa53e5480c96`, `subnet-0f404f193e6534efd`; endpoints cho S3, DynamoDB, Bedrock Runtime, CloudWatch Monitoring | Lambda không có public IP. Private subnets gọi AWS services qua endpoint để giảm chi phí và giữ traffic private. |
| 7 | Identity & Access | IAM least-privilege Lambda execution role | `arn:aws:iam::325137989598:role/team14-budgetbot-cfn-lambda-role` | Rule yêu cầu IAM least privilege. User login là optional, nên app dùng demo `X-User-Id` thay vì tốn thời gian triển khai Cognito đầy đủ. |

### Optional Capability Đã Chọn

Team 14 chọn **Optional #8 — Full Observability**.

| Yêu cầu | Triển khai | Trạng thái |
|---|---|---:|
| CloudWatch dashboard | `team14-budgetbot-cfn-observability` | Xong |
| Custom metric qua `PutMetricData` | `UploadSucceeded`, `TransactionsCategorized`, `LowConfidenceTransactions`, `BedrockLatencyMs` trong namespace `BudgetBot/Team14` | Xong |
| Alarm ở OK/ALARM | `team14-budgetbot-cfn-low-confidence-transactions`, state `OK`, `TreatMissingData=notBreaching` | Xong |
| Saved Logs Insights query | `team14-budgetbot-cfn/upload-classification-path`, id `81030937-11c7-4d22-900e-b13f51a6c9d8` | Xong |

### Bonus Paths Đã Làm

| Bonus Path | Bằng chứng |
|---|---|
| B. CI/CD pipeline | `.github/workflows/build-and-deploy.yml`; latest runs trên `main` đã success |
| C. Custom domain + HTTPS | Route 53 `budgetbot.topjob.id.vn`, ACM certificate ở `us-east-1`, CloudFront alias |
| E. IaC full coverage | `infrastructure/cloudformation.yaml` tạo VPC, endpoints, S3, CloudFront, DynamoDB, IAM, Lambda, API Gateway, CloudWatch dashboard/alarm/query |
| H. Cost under $30 | Chờ Cost Explorer screenshot cuối và teardown sạch |

#### CI/CD Pipeline Evidence

![GitHub Actions success](./evidence_screenshots/deployment/03_github_actions_success.png)

#### Ảnh Deployment Và Demo

![GitHub Actions success](./evidence_screenshots/deployment/03_github_actions_success.png)

![Upload success](./evidence_screenshots/demo/02_upload_success.png)

### Quyết Định Service Chính

| Quyết định | Lựa chọn | Phương án cân nhắc | Lý do |
|---|---|---|---|
| Compute | Lambda | ECS/Fargate hoặc EC2 | Lambda hợp với request upload/API, không có idle cost. ECS/EC2 thêm vận hành server/container không cần thiết cho demo. |
| API entry | API Gateway HTTP API | REST API hoặc ALB | HTTP API đủ cho Lambda proxy routes và rẻ hơn REST API. ALB phù hợp hơn cho service chạy lâu. |
| Frontend | S3 + CloudFront | Amplify hoặc backend-served frontend | HTML/JS static đủ cho demo. CloudFront giải quyết HTTPS và caching. |
| AI path | Bedrock InvokeModel | Bedrock KB/Agent | BudgetBot classify transaction rows, không retrieve knowledge từ tài liệu upload. |
| Model | Amazon Nova Micro | Model lớn hơn như Claude/Sonnet | Nova Micro rẻ hơn và đủ cho category classification khi có JSON-only prompt + review queue fallback. |
| Database | DynamoDB | RDS PostgreSQL | DynamoDB tránh chi phí instance và đáp ứng access pattern user/month. Aggregation trong app chấp nhận được ở quy mô hackathon. |
| Network | Không NAT, dùng VPC endpoints | NAT Gateway | S3/DynamoDB gateway endpoints miễn phí; Bedrock/CloudWatch interface endpoints rẻ hơn NAT cho traffic AWS-only. |
| Identity | IAM least privilege + demo user header | Full Cognito flow | Rule yêu cầu IAM least privilege; Cognito optional. Bỏ Cognito giúp giữ scope đúng 48 giờ. |
| Observability | CloudWatch dashboard/metrics/alarm/query | Monitoring ngoài AWS | CloudWatch native, đã học W1-W6, đáp ứng trực tiếp Optional #8. |

## 4. Kỷ Luật Chi Phí

### Safety Bắt Buộc

| Yêu cầu | Trạng thái | Bằng chứng |
|---|---:|---|
| AWS Budget alert | Xong | `W7-Team14-HardCap-100USD`, monthly COST budget $100 |
| SNS email confirmed | Xong | `truclt0311@gmail.com`, subscription ARN đã confirm |
| Cost Anomaly Detection | Xong | Monitor `Default-Services-Monitor`; gắn `docs/evidence_screenshots/cost/03_cost_anomaly_detection.png` |
| Tagging convention | Xong | `Project=W7Capstone`, `Team=G14`, `Owner=Team14`, `Environment=hackathon` trong CloudFormation resources |
| Bedrock access | Xong | Lambda health trả `ai=bedrock`; InvokeModel chạy qua app đã deploy |
| Cost Explorer screenshots | Một phần | Đã gắn Day 1 EOD; Day 2 EOD và Friday pre-demo còn pending |

### Ảnh Cost Evidence Đã Gắn

| Screenshot | File | Ghi chú |
|---|---|---|
| Budget alert | `docs/evidence_screenshots/cost/01_budget_alert.png` | Show budget $100 / threshold $80 |
| SNS confirmation | `docs/evidence_screenshots/cost/02_sns_confirmed.png` | Show email subscription confirmed |
| Cost Anomaly Detection | `docs/evidence_screenshots/cost/03_cost_anomaly_detection.png` | Show monitor/subscription active |
| Day 1 EOD Cost Explorer | `docs/evidence_screenshots/cost/04_cost_explorer_day1_eod.png` | Chụp trạng thái dữ liệu Cost Explorer ở Day 1 EOD |
| Day 2 EOD Cost Explorer | `docs/evidence_screenshots/cost/05_cost_explorer_day2_eod.png` | TODO: thêm tổng chi phí sau khi chụp |
| Friday pre-demo Cost Explorer | `docs/evidence_screenshots/cost/06_cost_explorer_friday_predemo.png` | TODO: số chính thức trước demo sau khi chụp |

#### Budget Alert

![Budget alert](evidence_screenshots/cost/01_budget_alert.png)

#### SNS Confirmation

![SNS confirmation](evidence_screenshots/cost/02_sns_confirmed.png)

#### Cost Anomaly Detection

![Cost Anomaly Detection](evidence_screenshots/cost/03_cost_anomaly_detection.png)

#### Day 1 EOD Cost Explorer

![Day 1 EOD Cost Explorer](evidence_screenshots/cost/04_cost_explorer_day1_eod.png)

### Cost Drivers Dự Kiến

| Driver | Vì sao phát sinh | Cách kiểm soát |
|---|---|---|
| Bedrock Runtime | AI classification khi upload và chạy accuracy test | Dùng Nova Micro, batch classification, prompt ngắn JSON-only, tránh loop model đắt |
| CloudFront + S3 | Public frontend, raw CSV, Lambda artifacts | Static site và file volume thấp |
| VPC Interface Endpoints | Lambda private gọi Bedrock Runtime và CloudWatch Monitoring | Tránh NAT Gateway; S3/DynamoDB dùng gateway endpoints miễn phí |
| DynamoDB | Lưu transaction state | PAY_PER_REQUEST, item count nhỏ, không provision capacity |
| Lambda + API Gateway | Backend compute và API entry | Serverless, không có idle EC2/RDS cost |

### Ghi Nhận Cost

Khi soạn evidence, AWS Cost Explorer trả `DataUnavailableException`, thường xảy ra khi Cost Explorer mới bật hoặc dữ liệu ngày chưa ingest xong. Trước khi nộp, cần thay ghi chú này bằng tổng chi phí sáng demo và top 3 cost drivers từ Cost Explorer.

## 5. Bảo Mật

### Security Controls Đã Triển Khai

| Mảng | Triển khai | Bằng chứng |
|---|---|---|
| Root account safety | Root MFA là pre-flight requirement | Gắn `docs/evidence_screenshots/security/01_root_mfa_enabled.png` từ account owner |
| HTTPS public entry | Route 53 + CloudFront + ACM certificate | `budgetbot.topjob.id.vn`; ACM cert `arn:aws:acm:us-east-1:325137989598:certificate/5aece9cc-fd4b-4ebc-a6a5-24ab429455de`; CloudFront TLS minimum `TLSv1.2_2021` |
| Frontend bucket private | S3 Block Public Access + CloudFront OAC | `team14-budgetbot-cfn-frontend-325137989598-ap-southeast-1`, OAC `E3U013UCJVZJJW` |
| Raw statement storage | S3 Block Public Access + SSE-S3 | `team14-budgetbot-cfn-raw-325137989598-ap-southeast-1`, AES256 encryption |
| Data encryption | DynamoDB SSE enabled + PITR enabled | `team14-budgetbot-cfn-transactions`, `SSE=ENABLED`, continuous backups `ENABLED` |
| Network isolation | Lambda trong private subnets, không public IP, private route table không có internet default route | private subnets `subnet-0acedaa53e5480c96`, `subnet-0f404f193e6534efd`; không NAT Gateway |
| Least privilege | Lambda role chỉ có action cần thiết | `BudgetBotLambdaLeastPrivilegePolicy` |
| Cost safety | Budget + SNS + Cost Anomaly Detection | Budget `W7-Team14-HardCap-100USD`; SNS confirmed |

### Ảnh Security Evidence Đã Gắn

| Screenshot | File |
|---|---|
| Root MFA enabled | `docs/evidence_screenshots/security/01_root_mfa_enabled.png` |
| Lambda role least-privilege policy | `docs/evidence_screenshots/security/02_lambda_role_policy.png` |
| Frontend bucket private / Block Public Access | `docs/evidence_screenshots/security/03_frontend_bucket_private.png` |
| Raw bucket default encryption | `docs/evidence_screenshots/security/04_raw_bucket_encryption.png` |
| CloudFront HTTPS + ACM certificate | `docs/evidence_screenshots/security/05_cloudfront_https_acm.png05_cloudfront_https_acm.png` |
| DynamoDB encryption + PITR | `docs/evidence_screenshots/security/06_dynamodb_encryption_pitr.png` |
| VPC private subnets/endpoints, phần 1 | `docs/evidence_screenshots/security/07_vpc_private_subnets_endpoints1.png` |
| VPC private subnets/endpoints, phần 2 | `docs/evidence_screenshots/security/07_vpc_private_subnets_endpoints2.png` |

#### Root MFA Enabled

![Root MFA enabled](evidence_screenshots/security/01_root_mfa_enabled.png)

#### Lambda Role Policy

![Lambda role policy](evidence_screenshots/security/02_lambda_role_policy.png)

#### Frontend Bucket Private

![Frontend bucket private](evidence_screenshots/security/03_frontend_bucket_private.png)

#### Raw Bucket Encryption

![Raw bucket encryption](evidence_screenshots/security/04_raw_bucket_encryption.png)

#### CloudFront HTTPS Và ACM

![CloudFront HTTPS ACM](evidence_screenshots/security/05_cloudfront_https_acm.png05_cloudfront_https_acm.png)

#### DynamoDB Encryption Và PITR

![DynamoDB encryption PITR](evidence_screenshots/security/06_dynamodb_encryption_pitr.png)

#### VPC Private Subnets Và Endpoints

![VPC private subnets endpoints part 1](evidence_screenshots/security/07_vpc_private_subnets_endpoints1.png)

![VPC private subnets endpoints part 2](evidence_screenshots/security/07_vpc_private_subnets_endpoints2.png)

### IAM Scope Của Lambda

Lambda execution role chỉ cho phép các action cần cho demo path:

- S3 raw bucket: `s3:PutObject`, `s3:GetObject`, `s3:ListBucket`
- DynamoDB transactions table: `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:Query`, `dynamodb:UpdateItem`
- Bedrock: `bedrock:InvokeModel` trên Nova Micro inference profile/foundation model đã chọn và một fallback model ARN được liệt kê rõ
- CloudWatch Logs: `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`
- CloudWatch custom metrics: `cloudwatch:PutMetricData` chỉ cho namespace `BudgetBot/Team14`
- Lambda VPC attachment: EC2 network-interface actions cần cho Lambda ENI

Trade-off: một số quyền như CloudWatch metrics và Lambda ENI vẫn cần `Resource: "*"`, vì AWS API đó không hỗ trợ resource-level scoping giống S3/DynamoDB. Điều kiện namespace giới hạn phần CloudWatch metric.

## 6. Monitoring

Team 14 triển khai **Full Observability**.

### CloudWatch Dashboard

| Mục | Giá trị |
|---|---|
| Dashboard name | `team14-budgetbot-cfn-observability` |
| Dashboard ARN | `arn:aws:cloudwatch::325137989598:dashboard/team14-budgetbot-cfn-observability` |
| Region | ap-southeast-1 |
| Widgets | BudgetBot demo path metrics |

### Custom Metrics

| Metric | Namespace | Unit | Ý nghĩa |
|---|---|---|---|
| `UploadSucceeded` | `BudgetBot/Team14` | Count | Một upload CSV hoàn tất thành công |
| `TransactionsCategorized` | `BudgetBot/Team14` | Count | Số transaction đã classify và persist |
| `LowConfidenceTransactions` | `BudgetBot/Team14` | Count | Số classification low-confidence được đưa vào review |
| `BedrockLatencyMs` | `BudgetBot/Team14` | Milliseconds | Latency classify cho batch upload |

### Alarm

| Mục | Giá trị |
|---|---|
| Alarm name | `team14-budgetbot-cfn-low-confidence-transactions` |
| State khi validate | `OK` |
| Metric | `LowConfidenceTransactions` |
| Threshold | `>= 1` trong 300 giây |
| Treat missing data | `notBreaching` |
| Vì sao quan trọng | Báo rủi ro chất lượng classification khi upload có transaction low-confidence. |

### Logs Insights Query

Saved query:

```sql
fields @timestamp, @message
| filter @message like /bedrock_classification_result|cloudwatch_put_metric_data_failed|upload|summary|review/
| sort @timestamp desc
| limit 50
```

Bằng chứng:

- Query definition name: `team14-budgetbot-cfn/upload-classification-path`
- Query definition id: `81030937-11c7-4d22-900e-b13f51a6c9d8`
- Log group: `/aws/lambda/team14-budgetbot-cfn-backend`

### Ảnh Monitoring Evidence Đã Gắn

| Screenshot | File |
|---|---|
| CloudWatch dashboard | `docs/evidence_screenshots/monitoring/01_cloudwatch_dashboard.png` |
| Custom metrics namespace | `docs/evidence_screenshots/monitoring/02_custom_metrics.png` |
| CloudWatch alarm OK | `docs/evidence_screenshots/monitoring/03_alarm_ok.png` |
| Logs Insights saved query | `docs/evidence_screenshots/monitoring/04_logs_insights_query.png` |
| Lambda logs có Bedrock classification result | `docs/evidence_screenshots/monitoring/05_lambda_logs_bedrock_result.png` |

#### CloudWatch Dashboard

![CloudWatch dashboard](evidence_screenshots/monitoring/01_cloudwatch_dashboard.png)

#### Custom Metrics

![Custom metrics](evidence_screenshots/monitoring/02_custom_metrics.png)

#### CloudWatch Alarm

![CloudWatch alarm OK](evidence_screenshots/monitoring/03_alarm_ok.png)

#### Logs Insights Query

![Logs Insights query](evidence_screenshots/monitoring/04_logs_insights_query.png)

#### Lambda Logs Bedrock Result

![Lambda logs Bedrock result](evidence_screenshots/monitoring/05_lambda_logs_bedrock_result.png)

## 6.5 Đo Lường Và Quyết Định

### DECISION 1 — Chọn DynamoDB Thay Vì RDS PostgreSQL

**QUYẾT ĐỊNH:** Dùng DynamoDB PAY_PER_REQUEST table `team14-budgetbot-cfn-transactions` để lưu categorized transactions.

**PHƯƠNG ÁN CÂN NHẮC:**

- RDS PostgreSQL: mạnh hơn về SQL aggregation, nhưng có chi phí instance, subnet group, backup lifecycle và connection management.
- SQLite/local file: tốt cho local dev, nhưng không phù hợp deployed Lambda vì không phải shared persistent state.

**ĐO LƯỜNG:**

- Table state: `ACTIVE`.
- Item count khi validate: `91`.
- Billing mode: `PAY_PER_REQUEST`.
- Key schema: `user_id` hash key + `sk` range key.
- Persistent state test: upload data, refresh browser, gọi `GET /transactions` hoặc `GET /summary`, dữ liệu vẫn đọc được từ DynamoDB.

**BẰNG CHỨNG:**

- AWS CLI: `aws dynamodb describe-table --table-name team14-budgetbot-cfn-transactions`
- CloudFormation: `TransactionsTable` trong `infrastructure/cloudformation.yaml`
- API routes: `GET /transactions`, `GET /summary`, `GET /stats`

**TRADE-OFF CHẤP NHẬN:**

DynamoDB không có SQL `GROUP BY`, nên app aggregate summary trong application code sau khi query transactions của user. Với sample hackathon, trade-off này hợp lý và tránh idle cost của RDS. Nếu scale lớn hơn, nhóm sẽ thêm GSI hoặc precomputed monthly summary items.

### DECISION 2 — Amazon Bedrock InvokeModel Với Nova Micro Batch Classification

**QUYẾT ĐỊNH:** Dùng Amazon Bedrock Runtime `InvokeModel` với `apac.amazon.nova-micro-v1:0` để classify transaction. Prompt bắt model trả JSON-only gồm `category` và `confidence`.

**PHƯƠNG ÁN CÂN NHẮC:**

- Local rule-based classifier: không tốn AI cost nhưng yếu với merchant chưa thấy như `Vietnam Airlines HAN-SGN`, `KFC District 1`, `Cursor Pro` và opaque POS rows.
- Bedrock Knowledge Base/Agent: hợp với document retrieval, nhưng BudgetBot là classification trên CSV rows, không phải RAG.
- Model lớn hơn: có thể tốt hơn nhưng tốn token cost hơn, chưa cần cho scoped demo.

**ĐO LƯỜNG:**

- Labeled test set local: 40 transactions.
- Accuracy report trong repo: `28/40 = 70.0%` cho baseline path được đánh giá.
- Known-brand improvement: LocalAI `0/7` trên unseen brands đã liệt kê; Bedrock ước tính khoảng `6/7`.
- Upload metric validation: sample upload publish `TransactionsCategorized` và `LowConfidenceTransactions`.
- Low-confidence fallback: dòng có `confidence="low"` xuất hiện trong `GET /review-queue`.

**BẰNG CHỨNG:**

- `supporting_docs/accuracy_report.txt`
- `supporting_docs/failure_cases.md`
- `src/adapters/ai.py` JSON-only prompts
- `src/handlers.py` review queue và custom metrics
- CloudWatch metric `LowConfidenceTransactions`

**TRADE-OFF CHẤP NHẬN:**

Hệ thống không claim AI tự động đúng 100%. Thay vào đó, app hiển thị confidence và đưa case không chắc chắn vào review queue. Cách này an toàn hơn cho dữ liệu tài chính.

### DECISION 3 — Không Dùng NAT Gateway, Dùng VPC Endpoints

**QUYẾT ĐỊNH:** Chạy Lambda trong private subnets ở 2 AZ và truy cập AWS services qua VPC endpoints thay vì NAT Gateway.

**PHƯƠNG ÁN CÂN NHẮC:**

- NAT Gateway: đơn giản cho internet egress chung, nhưng có hourly cost và data processing cost.
- Lambda ngoài VPC: network đơn giản hơn, nhưng yếu hơn về evidence Network Foundation và private service access.

**ĐO LƯỜNG:**

- VPC `vpc-044f26a2a760491ba`.
- Private subnets 2 AZ: `10.0.2.0/24` và `10.0.102.0/24`.
- S3 Gateway Endpoint: `vpce-0fa20050fb908c907`.
- DynamoDB Gateway Endpoint: `vpce-021f8d076fea679f5`.
- Bedrock Runtime Interface Endpoint: `vpce-0cf470982a94fec03`.
- CloudWatch Monitoring Interface Endpoint: `vpce-0e765088be49cb20d`.

**BẰNG CHỨNG:**

- CloudFormation resources `S3GatewayEndpoint`, `DynamoDbGatewayEndpoint`, `BedrockRuntimeEndpoint`, `CloudWatchMonitoringEndpoint`.
- Private route table có local route và Gateway Endpoint routes; không có NAT route `0.0.0.0/0`.

**TRADE-OFF CHẤP NHẬN:**

Interface endpoints có hourly cost theo AZ, nhưng giữ backend private và tránh NAT Gateway cost. Vì app chỉ gọi AWS services, không cần internet egress chung.

## 7. Bài Học Rút Ra

Bài học lớn nhất là một AI SaaS demo chạy được phụ thuộc nhiều vào kiểm soát scope và evidence, không phải thêm thật nhiều tính năng. BudgetBot bắt đầu từ starter app, nhưng nhóm phải đưa ra các quyết định triển khai thật: Lambda thay vì ECS/EC2, DynamoDB thay vì RDS, Bedrock InvokeModel trực tiếp thay vì Knowledge Base, và VPC endpoints thay vì NAT Gateway. Các lựa chọn này giúp hệ thống đủ nhỏ để ship, nhưng vẫn cover đủ 7 mandatory capabilities.

Vấn đề sản phẩm khó nhất là uncertainty trong classification. Một số transaction dễ đoán như coffee shop hoặc airline, nhưng mô tả như `Unknown merchant POS` không đủ tín hiệu để model classify chắc chắn. Cách xử lý không phải là giả định AI luôn đúng. App trả confidence, đưa low-confidence rows vào review queue, và hỗ trợ user correction qua `POST /correct`. Như vậy failure mode của AI trở thành một workflow minh bạch.

Nếu có thêm một sprint, nhóm sẽ thêm Cognito auth, budget goals theo tháng, alert khi category vượt cap, recurring transaction detection và precomputed monthly summary table cho dataset lớn hơn.

## 8. Kế Hoạch Teardown

Deadline teardown: **Sunday 1/6 EOD**. Commit xác nhận vào `docs/teardown_confirmation.md` và thêm screenshot Cost Explorer ngày Monday.

### Thứ Tự Teardown

1. Disable hoặc remove custom DNS aliases nếu xóa CloudFront.
2. Delete CloudFormation stack `team14-budgetbot-iac`.
3. Nếu stack deletion fail vì S3, empty các bucket này trước:
   - `team14-budgetbot-cfn-frontend-325137989598-ap-southeast-1`
   - `team14-budgetbot-cfn-raw-325137989598-ap-southeast-1`
   - `team14-budgetbot-artifacts-325137989598-ap-southeast-1`
4. Delete CloudFront distribution `E349TWP6TRPSOC` sau khi disable nếu cần.
5. Delete API Gateway `mlhwir8gc5`.
6. Delete Lambda function `team14-budgetbot-cfn-backend`.
7. Delete DynamoDB table `team14-budgetbot-cfn-transactions` nếu còn.
8. Delete CloudWatch dashboard, alarm, saved query và Lambda log group.
9. Delete VPC endpoints, subnets, route tables, security groups, internet gateway và VPC sau cùng.
10. Review Route 53 hosted zones và xóa hosted zone `budgetbot.topjob.id.vn` dư nếu không cần.
11. Verify Cost Explorer vào Monday 2/6 và commit screenshot.

### Lệnh Teardown Khởi Điểm

```bash
aws cloudformation delete-stack \
  --profile hackathon \
  --region ap-southeast-1 \
  --stack-name team14-budgetbot-iac

aws cloudformation wait stack-delete-complete \
  --profile hackathon \
  --region ap-southeast-1 \
  --stack-name team14-budgetbot-iac
```

## Appendix A — Lệnh Kiểm Chứng Live

```bash
curl -I https://budgetbot.topjob.id.vn
curl https://mlhwir8gc5.execute-api.ap-southeast-1.amazonaws.com/health

aws cloudformation describe-stacks \
  --profile hackathon \
  --region ap-southeast-1 \
  --stack-name team14-budgetbot-iac

aws cloudwatch describe-alarms \
  --profile hackathon \
  --region ap-southeast-1 \
  --alarm-names team14-budgetbot-cfn-low-confidence-transactions

aws dynamodb describe-continuous-backups \
  --profile hackathon \
  --region ap-southeast-1 \
  --table-name team14-budgetbot-cfn-transactions
```

## Appendix B — Tài Liệu Yêu Cầu Đã Dùng

Bản Evidence Pack này được viết theo:

- `W7/W7_project_announcement.md`
- `W7/W7_learner_guide.md`
- `W7/W7_hackathon_rules.txt`
- `W7/W7_cost_estimates.md`
- `W7/starter_apps/README.md`
