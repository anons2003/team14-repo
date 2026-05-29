# Cấu Trúc Slide Demo Day — Team 14 BudgetBot

Mục tiêu deck: 12-18 slides, xuất bản cuối cùng thành `docs/slides.pdf`.

Thời lượng trình bày theo rule:

- Pitch + Vision: 5 phút
- Live Demo: 7 phút
- Architecture Walkthrough: 14 phút
- Individual Q&A: 12 phút
- Cost + Lessons Learned: 2 phút

## Slide 1 — Cover

**Title:** Team 14 BudgetBot — AI Money Coach

**Nội dung chính:**

- Domain: FinTech
- Public URL: `https://budgetbot.topjob.id.vn`
- Repo: `https://github.com/anons2003/team14-repo`
- Region: `ap-southeast-1`
- Stack: `team14-budgetbot-iac`

**Visual nên dùng:** screenshot trang home hoặc architecture thumbnail.

**Speaker note:** Mở đầu ngắn: nhóm xây một AI Money Coach cho người dùng upload sao kê ngân hàng, tự động phân loại giao dịch, xem summary chi tiêu và review các giao dịch AI chưa chắc chắn.

## Slide 2 — Problem & Target User

**Title:** Người dùng cần hiểu tiền đã đi đâu mà không phải tự phân loại từng dòng

**Nội dung chính:**

- Target users: sinh viên, người mới đi làm, freelancer, small business owner.
- Pain point: bank statement có mô tả ngắn, merchant name không đồng nhất, nhiều dòng khó hiểu.
- BudgetBot giải quyết: upload CSV -> AI classify -> lưu kết quả -> xem summary/review.

**Visual nên dùng:** 3 bước ngắn: Upload CSV / AI classify / Spending insight.

**Speaker note:** Nhấn mạnh đây không chỉ là CRUD app. AI có giá trị vì dữ liệu ngân hàng thực tế thường lộn xộn và khó phân loại bằng rule cứng.

## Slide 3 — Product Scope & Demo Path

**Title:** Scope đã chốt cho hackathon

**Nội dung chính:**

- Upload `sample_data/bank_statement_q2_2026.csv`.
- Lưu raw statement vào S3.
- Bedrock trả category + confidence dạng JSON-only.
- Lưu transaction vào DynamoDB.
- UI hiển thị summary, transaction list, review queue, AI performance.
- Refresh browser vẫn còn dữ liệu.

**Visual nên dùng:** simple flow 1 -> 6.

**Speaker note:** Nói rõ scope không làm full personal finance suite; nhóm tập trung end-to-end happy path, AI confidence và observability.

## Slide 4 — Live Demo Checklist

**Title:** Demo flow 7 phút

**Nội dung chính:**

1. Mở `https://budgetbot.topjob.id.vn`.
2. Upload `bank_statement_q2_2026.csv`.
3. Xem classified transactions.
4. Xem category summary.
5. Xem low-confidence review queue.
6. Refresh browser để chứng minh persistence.
7. Mở CloudWatch log/metrics nếu cần chứng minh Bedrock path.

**Visual nên dùng:** ảnh `docs/evidence_screenshots/demo/02_upload_success.png`.

**Speaker note:** Trainer có thể tự mở URL. Nhóm nên demo bằng dữ liệu đã chuẩn bị để tránh lỗi do file format lạ.

## Slide 5 — Final Architecture Overview

**Title:** AWS Serverless Architecture

**Nội dung chính:**

- Route 53 + CloudFront + private S3 frontend.
- API Gateway HTTP API.
- Lambda FastAPI backend trong private subnets across 2 AZs.
- S3 raw bucket, DynamoDB, Bedrock Runtime.
- CloudWatch dashboard, metrics, alarm, Logs Insights.

**Visual nên dùng:** `docs/architecture.png`.

**Speaker note:** Đây là slide chính. Đi từ trái sang phải theo runtime path, sau đó tách riêng deployment path ở slide sau.

## Slide 6 — Runtime Request Flow

**Title:** Runtime path: user upload đến AI result

**Nội dung chính:**

`Users -> Route 53 -> CloudFront HTTPS -> S3 frontend -> API Gateway -> Lambda -> S3 / Bedrock / DynamoDB / CloudWatch`

**Explain từng bước:**

- CloudFront phục vụ frontend qua HTTPS.
- Browser gọi API Gateway.
- API Gateway invoke Lambda.
- Lambda lưu CSV vào S3 raw bucket.
- Lambda gọi Bedrock Runtime để classify.
- Lambda ghi DynamoDB và publish CloudWatch custom metrics.

**Speaker note:** Nhấn mạnh DynamoDB, S3, Bedrock, CloudWatch là managed AWS services ngoài customer VPC; Lambda gọi qua endpoints/private AWS path theo thiết kế.

## Slide 7 — 7 Mandatory Capabilities Mapping

**Title:** 7 mandatory capabilities đã đủ service

| Capability | Service Team 14 dùng |
|---|---|
| User-facing entry | Route 53, CloudFront, S3 frontend, API Gateway |
| Compute | AWS Lambda + FastAPI/Mangum |
| AI/ML | Amazon Bedrock Runtime InvokeModel |
| Data persistence | DynamoDB |
| Object storage | S3 raw, S3 frontend, S3 artifact |
| Network foundation | VPC, private subnets, VPC endpoints |
| Identity/access | IAM least-privilege Lambda role |

**Speaker note:** Đây là slide để trainer thấy checklist mandatory ngay lập tức. Không đọc hết bảng, chỉ nói từng service có vai trò gì.

## Slide 8 — Compute & API Decisions

**Title:** Vì sao chọn Lambda + API Gateway HTTP API

**Nội dung chính:**

- Workload request-driven: upload CSV, classify batch, query summary.
- Không cần server chạy liên tục.
- Lambda 512 MB, timeout 30s đủ cho demo path.
- API Gateway HTTP API rẻ và đủ cho Lambda proxy routes.

**Trade-off:**

- Lambda có cold start và timeout giới hạn.
- Với file lớn hơn hoặc xử lý lâu hơn, production nên thêm async queue/SQS hoặc Step Functions.

**Speaker note:** Không nói Lambda tốt nhất trong mọi trường hợp; nói Lambda phù hợp với constraints hackathon và chi phí thấp.

## Slide 9 — AI Design: Bedrock JSON-only Classification

**Title:** Bedrock path cho transaction classification

**Nội dung chính:**

- Model: `apac.amazon.nova-micro-v1:0`.
- Prompt bắt model trả JSON-only.
- Output gồm `category` và `confidence`.
- Low-confidence transactions được đưa vào review queue.
- Có batch classify nếu kịp để giảm latency/cost.

**Trade-off:**

- Nova Micro tiết kiệm chi phí, đủ tốt cho classification.
- Model lớn có thể chính xác hơn nhưng không hợp cost cap nếu chạy nhiều test loop.

**Speaker note:** Nhấn mạnh nhóm không dùng Bedrock KB vì bài toán không phải RAG/document Q&A; đây là row classification.

## Slide 10 — Data & Persistence

**Title:** DynamoDB access pattern

**Nội dung chính:**

- Table: `team14-budgetbot-cfn-transactions`.
- PK: `user_id`.
- SK: `TXN#date#id`.
- Query theo `user_id` và month.
- Summary theo category được tính từ transaction đã lưu.
- Refresh browser vẫn đọc lại được từ DynamoDB.
- PITR và SSE enabled.

**Trade-off:**

- DynamoDB rẻ và ít vận hành hơn RDS.
- Aggregation phức tạp hơn SQL, nhưng phù hợp với demo scale và access pattern hiện tại.

## Slide 11 — Network & Security

**Title:** Private Lambda tier, no NAT Gateway

**Nội dung chính:**

- Lambda gắn private subnets ở 2 AZs.
- Không có public IP.
- S3 và DynamoDB dùng Gateway Endpoints.
- Bedrock Runtime và CloudWatch Monitoring dùng Interface Endpoints.
- Không dùng NAT Gateway để giảm chi phí.

**Security controls:**

- S3 Block Public Access.
- CloudFront OAC cho frontend bucket.
- HTTPS bằng ACM + CloudFront.
- IAM least privilege.
- DynamoDB encryption + PITR.

**Speaker note:** Nếu trainer hỏi “DB sao không nằm trong VPC”, trả lời DynamoDB là managed regional service, không deploy vào customer VPC; app truy cập riêng qua gateway endpoint.

## Slide 12 — Observability Optional #8

**Title:** Optional capability: Full Observability

**Nội dung chính:**

- Dashboard: `team14-budgetbot-cfn-observability`.
- Custom metrics namespace: `BudgetBot/Team14`.
- Metrics:
  - `UploadSucceeded`
  - `TransactionsCategorized`
  - `LowConfidenceTransactions`
  - `BedrockLatencyMs`
- Alarm: `team14-budgetbot-cfn-low-confidence-transactions`.
- Saved Logs Insights query: `team14-budgetbot-cfn/upload-classification-path`.

**Visual nên dùng:** dashboard screenshot + alarm OK screenshot.

**Speaker note:** Đây là optional nhóm chọn. Cần nói rõ metric được publish từ app path thật, không chỉ tạo dashboard trống.

## Slide 13 — CI/CD & IaC

**Title:** Deploy bằng GitHub Actions + CloudFormation

**Nội dung chính:**

- Push to `main` trigger workflow.
- Run tests: `pytest -q`.
- Build Lambda zip.
- Upload artifact lên S3 artifact bucket.
- Deploy CloudFormation stack.
- Sync frontend vào S3 frontend bucket.
- Invalidate CloudFront cache.

**Bonus paths:**

- B. CI/CD pipeline.
- E. Full IaC coverage.

**Visual nên dùng:** CI/CD flow diagram hoặc screenshot `docs/evidence_screenshots/deployment/03_github_actions_success.png`.

**Speaker note:** Nhấn mạnh CloudFormation là source of truth cho infra, redeploy/teardown bằng CLI được.

## Slide 14 — Cost Discipline

**Title:** Cost safety under $100 hard cap

**Nội dung chính:**

- Budget: `W7-Team14-HardCap-100USD`.
- SNS confirmed: `truclt0311@gmail.com`.
- Cost Anomaly Detection enabled.
- Tags:
  - `Project=W7Capstone`
  - `Team=G14`
  - `Owner=Team14`
  - `Environment=hackathon`

**Cost drivers dự kiến:**

- Bedrock Runtime.
- VPC Interface Endpoints.
- CloudFront + S3.
- DynamoDB.
- Lambda + API Gateway.

**Speaker note:** Nếu Cost Explorer chưa có data, nói rõ Budget/SNS/Anomaly đã bật và Cost Explorer có độ trễ ingest. Không bịa số.

## Slide 15 — Trade-offs & What We Cut

**Title:** Những quyết định có chủ đích để ship trong 48 giờ

**Trade-offs:**

- Không làm Cognito full auth: dùng demo user header vì rule cần IAM least privilege, không bắt buộc full user auth.
- Không dùng NAT Gateway: dùng endpoints để giảm cost.
- Không dùng RDS: DynamoDB đủ cho access pattern user/month và tránh idle database cost.
- Không dùng Bedrock KB/Agent: transaction classification không cần RAG.
- Không build full budget goals/forecasting: tập trung upload -> classify -> persist -> observe.

**Speaker note:** Slide này rất quan trọng cho Q&A. Trainer muốn nghe “vì sao không chọn X”, không chỉ “tụi em chọn Y”.

## Slide 16 — Evidence Pack & Security Proof

**Title:** Evidence đã chuẩn bị

**Nội dung chính:**

- Evidence pack: `docs/W7_evidence.md`.
- Architecture: `docs/architecture.png`.
- Screenshots:
  - Cost: Budget/SNS/Anomaly/Cost Explorer.
  - Security: MFA, IAM policy, S3 private/encryption, CloudFront HTTPS, DynamoDB PITR, VPC endpoints.
  - Monitoring: Dashboard, custom metrics, alarm, Logs Insights, Lambda logs.
  - Deployment/Demo: GitHub Actions success, upload success.
- CLI outputs: `docs/evidence_cli_outputs`.

**Speaker note:** Không cần trình bày từng ảnh; dùng slide này để chứng minh repo có đủ artifact khi trainer kiểm tra.

## Slide 17 — Lessons Learned

**Title:** Lessons learned

**Nội dung chính:**

- Serverless giúp ship nhanh, nhưng phải hiểu boundary của managed services.
- Cost safety phải làm trước khi build: Budget, SNS, anomaly, tags.
- Prompt JSON-only + confidence giúp AI output dễ kiểm soát hơn.
- Observability giúp demo đáng tin hơn vì có metric/log thật.
- CloudFormation giúp recreate và teardown sạch hơn thao tác tay.

**What we would improve:**

- Thêm auth thật bằng Cognito.
- Thêm async processing cho file lớn.
- Thêm user correction feedback loop.
- Thêm budget goals, recurring detection, forecasting nếu còn thời gian.

## Slide 18 — Teardown Plan

**Title:** Clean teardown after demo

**Nội dung chính:**

- Delete CloudFormation stack: `team14-budgetbot-iac`.
- Empty/delete S3 artifact bucket nếu ngoài stack.
- Remove Route 53/ACM/SNS/Budget nếu chỉ dùng cho hackathon.
- Verify bằng CLI.
- Commit `docs/teardown_confirmation.md`.
- Add Monday Cost Explorer screenshot: `docs/teardown_confirmed.png`.

**Speaker note:** Đây là slide ngắn cuối cùng để chứng minh nhóm hiểu trách nhiệm chi phí cá nhân sau demo.

## Recommended Final Deck Length

Nếu muốn gọn hơn, dùng 16 slides:

- Gộp Slide 16 vào Slide 14 hoặc Appendix.
- Gộp Slide 18 vào Slide 17.

Nếu trainer yêu cầu architecture sâu, giữ đủ 18 slides vì phần Architecture Walkthrough chiếm 14 phút.

## Speaker Ownership Gợi Ý

| Phần | Slides | Owner |
|---|---:|---|
| Pitch + Vision | 1-3 | Project Lead |
| Live Demo | 4 | Backend/Frontend Owner |
| Architecture overview | 5-7 | Project Lead + Infra Owner |
| Compute/API/AI/Data | 8-10 | Backend Owner + Data Owner |
| Network/Security | 11 | Infra/Security Owner |
| Observability | 12 | Observability Owner |
| CI/CD/IaC | 13 | Infra Owner |
| Cost + Trade-offs | 14-15 | Cost Owner + Project Lead |
| Evidence/Lessons/Teardown | 16-18 | Project Lead |

## Assets Cần Gắn Vào Slide

- `docs/architecture.png`
- `docs/evidence_screenshots/demo/02_upload_success.png`
- `docs/evidence_screenshots/deployment/03_github_actions_success.png`
- `docs/evidence_screenshots/monitoring/01_cloudwatch_dashboard.png`
- `docs/evidence_screenshots/monitoring/02_custom_metrics.png`
- `docs/evidence_screenshots/monitoring/03_alarm_ok.png`
- `docs/evidence_screenshots/security/02_lambda_role_policy.png`
- `docs/evidence_screenshots/cost/01_budget_alert.png`
- `docs/evidence_screenshots/cost/02_sns_confirmed.png`
- `docs/evidence_screenshots/cost/03_cost_anomaly_detection.png`
