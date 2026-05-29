# Project Lead Final Scope

Owner: Project Lead

Mục tiêu phần này là chốt lại câu chuyện demo cuối cùng: cái gì đã chạy thật, cái gì không cần đưa vào demo, và trainer sẽ đi qua luồng nào để thấy BudgetBot hoạt động end-to-end.

## 1. Những Gì Đã Chạy

### Hạ tầng và safety

- AWS region đã dùng: `ap-southeast-1`.
- CloudFormation stack đã deploy: `team14-budgetbot-iac`.
- Budget alert đã tạo: `W7-Team14-HardCap-100USD`, cảnh báo khi actual cost vượt `$80`.
- SNS email alert đã confirm: `truclt0311@gmail.com`.
- Cost Anomaly Detection đã bật và đã thêm subscriber.
- Tagging convention đã thống nhất:
  - `Project=W7Capstone`
  - `Team=G14`
  - `Owner=<member-name>`
  - `Environment=hackathon`

### Foundation resources

- S3 frontend bucket đã tạo, bật Block Public Access và encryption.
- S3 raw statements bucket đã tạo, bật Block Public Access và encryption.
- Đã xóa 2 bucket S3 cũ bị trùng chức năng:
  - `team14-budgetbot-frontend-325137989598`
  - `team14-budgetbot-raw-325137989598`
- S3 buckets còn dùng cho demo:
  - `team14-budgetbot-cfn-frontend-325137989598-ap-southeast-1` cho static frontend.
  - `team14-budgetbot-cfn-raw-325137989598-ap-southeast-1` cho raw statement uploads và Lambda artifacts đã deploy thủ công.
  - `team14-budgetbot-artifacts-325137989598-ap-southeast-1` cho GitHub Actions Lambda artifacts nếu dùng CI/CD.
- DynamoDB table đã tạo: `team14-budgetbot-cfn-transactions`.
- Lambda execution role đã tạo theo hướng least privilege.
- VPC đã tạo với private Lambda subnets across two AZs.
- VPC endpoints đã tạo cho S3, DynamoDB, Bedrock Runtime, và CloudWatch Monitoring.
- CloudFront distribution đã tạo để serve frontend bằng HTTPS.
- API Gateway HTTP API đã tạo để expose backend endpoints.

### Core application

- Lambda backend đã deploy: `team14-budgetbot-cfn-backend`.
- API routes đã chạy:
  - `GET /health`
  - `POST /upload`
  - `GET /transactions`
  - `GET /summary`
  - `GET /review-queue`
- Frontend đã cấu hình gọi API thật.
- Upload CSV thật đã chạy được với S3 raw storage.
- Bedrock InvokeModel đã chạy thật bằng Amazon Nova Micro.
- DynamoDB write/read đã chạy thật.
- Duplicate upload đã xử lý: upload cùng một file không nhân bản transaction.
- Low-confidence review queue đã chạy qua API Gateway và hiển thị trên frontend.
- File `bank_statement_q2_2026.csv` đã test thành công với `83` transaction.
- Data Owner proof đã chạy với `user_id=data-owner-1779934940`: upload lưu 83 categorized transactions, query `month=2026-03` trả 30 transactions, DynamoDB query cùng key condition cũng trả count 30, và summary trả category breakdown.
- CloudWatch logs đã có evidence từ Lambda và Bedrock classification path.
- Observability Owner proof đã chạy với `user_id=observability-1779935557`: custom metrics có datapoints `UploadSucceeded=1`, `TransactionsCategorized=83`, `LowConfidenceTransactions=7`, `BedrockLatencyMs≈6102`; dashboard `team14-budgetbot-cfn-observability` tồn tại; alarm `team14-budgetbot-cfn-low-confidence-transactions` ở trạng thái `OK`; saved Logs Insights query `team14-budgetbot-cfn/upload-classification-path` chạy ra 5 rows.

### Public endpoints

- Frontend URL: `https://d104yk0i41rvg5.cloudfront.net`
- API endpoint: `https://mlhwir8gc5.execute-api.ap-southeast-1.amazonaws.com`

## 2. Cắt Những Phần Không Cần Thiết

Những phần dưới đây không đưa vào demo chính để giữ demo gọn, giảm rủi ro, và tập trung vào 7 mandatory capabilities cộng optional Full Observability.

### Cắt khỏi scope build/demo

- Không làm banking integration thật.
- Không dùng dữ liệu tài chính thật của người dùng.
- Không làm Cognito signup/login.
- Không làm multi-user auth flow phức tạp.
- Không làm Bedrock Knowledge Base hoặc RAG.
- Không làm vector database.
- Không làm RDS/Postgres migration.
- Không làm mobile app.
- Không làm custom domain.
- Không làm multi-region failover.
- Không làm NAT Gateway vì private subnets dùng VPC endpoints.
- Không demo full CI/CD nếu không cần; GitHub Actions chỉ là bonus/supporting evidence.
- Không dùng lại S3 buckets thủ công cũ. App demo chỉ dùng bucket được quản lý bởi CloudFormation.

### Không nhấn mạnh trong presentation

- Không giải thích quá sâu phần subnet route table nếu trainer không hỏi.
- Không nói app là production banking app.
- Không claim có authentication hoặc data privacy chuẩn ngân hàng.
- Không claim DynamoDB nằm trong VPC. DynamoDB là AWS managed regional service, Lambda truy cập riêng qua Gateway Endpoint.
- Không claim Bedrock nằm trong VPC. Bedrock Runtime là AWS managed service, Lambda truy cập qua Interface Endpoint.
- Không claim Claude Haiku đang chạy nếu account chưa được approve. Demo hiện dùng Amazon Nova Micro qua Bedrock Runtime.

## 3. Demo Path Cuối Cùng

Đây là luồng demo chính, nên đi đúng thứ tự để ít lỗi và dễ ghi điểm.

### Path 1: User-facing demo

1. Mở frontend public HTTPS URL:

   ```text
   https://d104yk0i41rvg5.cloudfront.net
   ```

2. Upload file CSV mẫu:

   ```text
   sample_data/bank_statement_q2_2026.csv
   ```

3. Xác nhận UI hiển thị upload success.

4. Xác nhận transaction list có dữ liệu đã phân loại category.

5. Xác nhận summary theo category hiển thị được.

6. Mở Review queue để chứng minh low-confidence classifications có hàng chờ review.

7. Refresh browser và mở lại transaction/summary để chứng minh dữ liệu được lưu trong DynamoDB, không chỉ nằm trong memory.

### Path 2: Backend/API proof

1. Gọi health check:

   ```bash
   curl https://mlhwir8gc5.execute-api.ap-southeast-1.amazonaws.com/health
   ```

2. Kết quả mong đợi:

   ```json
   {
     "status": "ok",
     "backends": {
       "ai": "bedrock",
       "storage": "s3",
       "userstore": "dynamodb"
     }
   }
   ```

3. Nếu cần chứng minh duplicate fix, upload cùng file hai lần với cùng `X-User-Id`, sau đó gọi `/transactions`. Kết quả đúng là vẫn `83` transaction, không tăng lên `166`.

4. Nếu cần chứng minh review queue:

   ```bash
   curl -H "X-User-Id: <demo-user>" https://mlhwir8gc5.execute-api.ap-southeast-1.amazonaws.com/review-queue
   ```

### Path 3: AWS evidence proof

1. Mở CloudFormation stack `team14-budgetbot-iac`.
2. Show tab Resources để thấy S3, DynamoDB, Lambda, API Gateway, CloudFront, VPC endpoints.
3. Show tab Outputs để lấy Frontend URL và API endpoint.
4. Mở DynamoDB table `team14-budgetbot-cfn-transactions` để chứng minh transaction đã persist.
5. Mở S3 raw bucket `team14-budgetbot-cfn-raw-325137989598-ap-southeast-1` để chứng minh CSV gốc đã được lưu.
6. Mở CloudWatch Logs của Lambda để chứng minh Bedrock classification path chạy thật.
7. Mở CloudWatch dashboard/alarm để chứng minh optional capability Full Observability.
8. Mở Budget/SNS/Cost Anomaly Detection screenshot hoặc console nếu trainer hỏi về cost safety.
9. Nếu trainer hỏi vì sao còn nhiều S3 buckets, trả lời: app chính dùng 2 bucket `team14-budgetbot-cfn-*`; bucket `team14-budgetbot-artifacts-*` phục vụ CI/CD artifact; bucket `cf-templates-*` do CloudFormation Console tự tạo khi upload template.

## 4. Final Scope Statement

BudgetBot là một serverless AI Money Coach cho FinTech. Người dùng upload bank statement CSV qua CloudFront frontend, frontend gọi API Gateway, Lambda parse giao dịch, lưu CSV gốc vào S3, gọi Amazon Bedrock Runtime để phân loại giao dịch, ghi kết quả vào DynamoDB, và frontend đọc lại transactions/summary. Hệ thống được deploy bằng CloudFormation, chạy trong private Lambda subnets với VPC endpoints, dùng IAM least privilege, và có CloudWatch observability làm optional capability.

## 5. Presenter Checklist

- [ ] Public URL mở được.
- [ ] `/health` trả `status=ok`.
- [ ] Upload CSV thành công.
- [ ] Transactions hiển thị đúng category.
- [ ] Summary hiển thị được.
- [ ] Review queue load được qua UI hoặc `/review-queue`.
- [ ] Upload lại cùng file không tạo duplicate.
- [ ] CloudWatch logs có Bedrock classification evidence.
- [ ] DynamoDB có transaction records.
- [ ] S3 raw bucket có uploaded CSV.
- [ ] S3 duplicate buckets cũ đã được xóa, chỉ còn bucket CloudFormation/artifact/template cần thiết.
- [ ] CloudFormation outputs có Frontend URL và API endpoint.
- [ ] Budget alert, SNS confirmation, Cost Anomaly Detection có screenshot/evidence.
