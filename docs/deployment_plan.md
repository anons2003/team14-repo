# Team 14 Deployment Plan — BudgetBot

## Goal

Ship BudgetBot as a public HTTPS AI SaaS demo for W7.

Happy path:

1. User opens CloudFront URL.
2. User uploads a bank statement CSV.
3. Backend stores the raw CSV in S3.
4. Lambda calls Amazon Bedrock to classify transactions.
5. Categorized transactions are saved in DynamoDB.
6. User views spending summary and transaction list after refresh.
7. Team shows CloudWatch monitoring and Cost Explorer evidence.

## Final Architecture

| W7 Capability | Service | Owner |
|---|---|---|
| User Interface | S3 static frontend + CloudFront HTTPS | Infra owner |
| API Entry | API Gateway HTTP API | Backend owner |
| Application Compute | Lambda Python / FastAPI | Backend owner |
| AI / ML Feature | Bedrock InvokeModel | AI owner |
| Data Persistence | DynamoDB | Data owner |
| Object Storage | S3 upload bucket | Infra owner |
| Network Foundation | No public DB, VPC endpoints where used, no NAT Gateway | Infra owner |
| Identity & Access | IAM least-privilege Lambda role | Infra + Backend owners |
| Optional Capability | CloudWatch dashboard + custom metrics + alarm + Logs Insights query | Observability owner |

## Team Roles

| Role | Main Responsibility | Deliverables |
|---|---|---|
| Project Lead / Presenter | Keep scope tight, coordinate checkpoints, own final story | Demo script, slide flow, QnA prep |
| Infra Owner | AWS resources, IAM, S3, CloudFront, API Gateway, tags, budget safety | Public URL, IAM policies, tagged resources |
| Backend + AI Owner | Lambda app, Bedrock prompt, classification API, error logs | Working upload/classify/summary endpoints |
| Data Owner | DynamoDB table design, transaction persistence, review queue | Data model, persistence proof, sample records |
| Evidence + Cost Owner | Evidence Pack, screenshots, Cost Explorer, teardown checklist | `docs/W7_evidence.md`, cost screenshots, teardown doc |
| Observability Owner | CloudWatch dashboard, custom metric, alarm, Log Insights | Monitoring screenshots and alarm proof |

If the team has fewer people, combine roles in this order:

1. Project Lead + Evidence
2. Infra + Observability
3. Backend + AI + Data

## Day 0 — Pre-flight Checklist

Complete before deploying paid resources.

- [ ] AWS root MFA enabled.
- [ ] AWS Budget alert set to `$80`.
- [ ] SNS budget alert email confirmed.
- [ ] Cost Anomaly Detection enabled.
- [ ] Bedrock model access enabled for chosen model.
- [ ] Team tags agreed:
  - `Project=W7Capstone`
  - `Team=G14`
  - `Owner=<member-name>`
  - `Environment=hackathon`
- [ ] GitHub repo public and accessible.
- [ ] `docs/W7_evidence.md` created.
- [ ] Architecture draft created.

## Day 1 Plan — Infrastructure + Happy Path

### 09:00-10:30 — Architecture Lock

Owner: Project Lead

- [ ] Confirm BudgetBot scope.
- [ ] Confirm services for all 7 mandatory capabilities.
- [ ] Assign final owners.
- [ ] Draw first architecture diagram.
- [ ] Decide optional capability: Full Observability.

### 10:30-11:00 — Safety Check

Owner: Evidence + Cost Owner

- [ ] Show Budget alert.
- [ ] Show SNS confirmation.
- [ ] Show Cost Anomaly Detection.
- [ ] Show Bedrock access.
- [ ] Confirm tagging convention.

### 11:00-13:00 — Foundation Resources

Owner: Infra Owner

- [ ] Create S3 frontend bucket.
- [ ] Create S3 upload bucket.
- [ ] Enable S3 Block Public Access.
- [ ] Enable encryption.
- [ ] Create DynamoDB table.
- [ ] Create Lambda execution role with least privilege.
- [ ] Apply tags to all resources.

### 14:00-16:30 — Core Services

Owners: Infra Owner + Backend Owner + Data Owner

- [ ] Deploy Lambda.
- [ ] Configure API Gateway HTTP API.
- [ ] Wire frontend API base URL.
- [ ] Test `/health`.
- [ ] Test DynamoDB write/read.
- [ ] Test S3 upload.
- [ ] Test one Bedrock InvokeModel call from Lambda.

### 16:30-17:00 — Day 1 Close

Owner: Project Lead

- [ ] Public URL loads.
- [ ] API returns health.
- [ ] One transaction can be written and read.
- [ ] Bedrock response appears in CloudWatch logs.
- [ ] Take Day 1 Cost Explorer screenshot.
- [ ] Commit current code and docs.

## Day 2 Plan — AI Feature + Observability + Evidence

### 09:00-09:30 — Scope Review

Owner: Project Lead

- [ ] List what works.
- [ ] Cut non-essential work.
- [ ] Confirm final demo path.

### 09:30-12:00 — AI Integration

Owner: Backend + AI Owner

- [ ] Replace local classifier with Bedrock path for deployed environment.
- [ ] Use JSON-only prompt response.
- [ ] Add confidence output.
- [ ] Add low-confidence review queue.
- [ ] Batch classify transactions where practical.
- [ ] Test with `sample_data/bank_statement_q2_2026.csv`.

### 12:00-13:00 — Data And Summary

Owner: Data Owner

- [ ] Store categorized transactions in DynamoDB.
- [ ] Query by `user_id` and month.
- [ ] Return summary by category.
- [ ] Confirm data persists after browser refresh.

### 13:00-14:30 — Optional Capability: Full Observability

Owner: Observability Owner

- [ ] Add custom metric `UploadSucceeded`.
- [ ] Add custom metric `TransactionsCategorized`.
- [ ] Add custom metric `LowConfidenceTransactions`.
- [ ] Create CloudWatch dashboard.
- [ ] Create alarm in `OK` or `ALARM` state.
- [ ] Save Logs Insights query.

### 14:30-15:30 — Evidence Pack

Owner: Evidence + Cost Owner

- [ ] Add architecture diagram.
- [ ] Add service decision table.
- [ ] Add IAM/security screenshots.
- [ ] Add monitoring screenshots.
- [ ] Add Day 2 Cost Explorer screenshot.
- [ ] Complete two decision blocks:
  - DynamoDB over RDS.
  - Bedrock Haiku batch classification over alternatives.

### 15:30-16:30 — Demo Rehearsal

Owner: Project Lead

- [ ] Run demo twice end-to-end.
- [ ] Test from phone hotspot or different network.
- [ ] Record backup demo video.
- [ ] Write 7-minute live demo script.
- [ ] Prepare QnA answers.

### 16:30-17:00 — Final Push

Owner: All

- [ ] Push repo.
- [ ] Export slides to `docs/slides.pdf`.
- [ ] Check public URL again.
- [ ] Check total spend.
- [ ] Confirm teardown plan.

## Demo Script

1. Open public HTTPS URL.
2. Upload sample bank statement.
3. Show AI classification result.
4. Show spending summary by category.
5. Show low-confidence review queue.
6. Refresh browser and show persisted transactions.
7. Open CloudWatch dashboard.
8. Open Cost Explorer screenshot/evidence.

## QnA Prep

Every member must answer these without passing:

- Why DynamoDB instead of RDS?
- Why InvokeModel instead of Bedrock Knowledge Base?
- Why Haiku instead of Sonnet?
- Why API Gateway HTTP API instead of REST API?
- What permissions does the Lambda execution role have?
- Where is uploaded raw data stored?
- How do we prevent public database exposure?
- What is the biggest cost driver?
- What happens when the model returns low confidence?
- What is the teardown order?

## Cut List

Do not build these unless all required items are already done:

- Full Cognito signup flow.
- New React frontend.
- Custom domain.
- CI/CD pipeline.
- Multi-region failover.
- Complex chatbot memory.
- RDS migration.
- Full PDF parsing.

## Teardown Plan

After demo:

1. Delete CloudFront distribution.
2. Delete API Gateway.
3. Delete Lambda function.
4. Delete DynamoDB table.
5. Empty and delete S3 buckets.
6. Delete CloudWatch dashboard, alarms, and log groups.
7. Delete VPC endpoints and VPC resources if created.
8. Take final Cost Explorer screenshot.
9. Complete `docs/teardown_confirmation.md`.
10. Commit teardown confirmation.

