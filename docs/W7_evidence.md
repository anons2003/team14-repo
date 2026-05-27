# W7 Evidence Pack — Team 14 BudgetBot

## 1. Cover

- Team: Team 14
- Domain: FinTech — AI Money Coach
- Live URL:
- GitHub repo:
- Total spend:

## 2. Pitch And Vision

BudgetBot helps users understand where their money went by uploading bank statements, classifying transactions, and showing spending summaries by category.

Target users: students, young professionals, and small business owners who need a quick spending overview without manually tagging every transaction.

## 3. Architecture

Add final architecture diagram here: `docs/architecture.png`.

| Capability | Service | Rationale |
|---|---|---|
| User Interface | S3 + CloudFront | Public HTTPS static frontend |
| Application Compute | Lambda + API Gateway HTTP API | Low cost, serverless request processing |
| AI / ML Feature | Bedrock InvokeModel | Direct transaction classification does not need RAG |
| Data Persistence | DynamoDB | Simple user/month transaction access pattern |
| Object Storage | S3 | Raw bank statement storage |
| Network Foundation | VPC endpoints / no public DB | Avoid NAT and keep AWS service access private where used |
| Identity & Access | IAM least privilege | Scoped Lambda execution role |

## 4. Cost Discipline

Screenshots to add:

- Day 1 EOD Cost Explorer:
- Day 2 EOD Cost Explorer:
- Friday pre-demo Cost Explorer:

Top cost drivers:

1.
2.
3.

## 5. Security

- Root MFA:
- Budget alert SNS confirmed:
- IAM Lambda role:
- S3 Block Public Access:
- Encryption:

## 6. Monitoring

- CloudWatch dashboard:
- Custom metric:
- Alarm:
- Logs Insights query:

## 6.5 Measurement & Decisions

### Decision 1 — DynamoDB Over RDS

DECISION:

ALTERNATIVES CONSIDERED:

MEASUREMENT:

EVIDENCE:

TRADE-OFF ACCEPTED:

### Decision 2 — Bedrock Haiku Batch Classification

DECISION:

ALTERNATIVES CONSIDERED:

MEASUREMENT:

EVIDENCE:

TRADE-OFF ACCEPTED:

## 7. Lessons Learned

Write around 200 words after the build. Include one failure case, what changed, and what you would do differently next time.

## 8. Teardown Plan

1. Delete CloudFront distribution.
2. Delete API Gateway.
3. Delete Lambda function.
4. Delete DynamoDB table.
5. Empty and delete S3 buckets.
6. Delete CloudWatch alarms, dashboards, and log groups.
7. Delete VPC endpoints and VPC resources if created.

