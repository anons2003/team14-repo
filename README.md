# Team 14 — BudgetBot

FinTech capstone app for W7: upload a bank statement CSV, classify transactions with AI, persist categorized transactions, and show spending summaries.

## Architecture Target

- Frontend: S3 static site + CloudFront HTTPS
- API entry: API Gateway HTTP API
- Compute: AWS Lambda running FastAPI
- AI: Amazon Bedrock InvokeModel
- Persistence: DynamoDB or SQLite for local development
- Object storage: S3 for uploaded bank statements
- Observability: CloudWatch dashboard, custom metrics, alarm, and Logs Insights query

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.app:app --reload --port 8000
```

Open:

```bash
http://localhost:8000
```

Smoke test:

```bash
pytest -q
```

## Demo Flow

1. Open the public HTTPS frontend URL.
2. Upload `sample_data/bank_statement_q2_2026.csv`.
3. Backend stores the raw CSV in S3.
4. Lambda calls Bedrock to classify transactions.
5. Categorized rows are persisted.
6. Summary and transaction list are visible after refresh.

## Required W7 Artifacts

- `docs/W7_evidence.md`
- `docs/architecture.png`
- `docs/slides.pdf`
- `docs/demo.mp4` or unlisted video link
- `docs/teardown_confirmation.md` after teardown

## Teardown

Delete resources in dependency order:

1. CloudFront distribution
2. API Gateway
3. Lambda function
4. DynamoDB table
5. S3 buckets after emptying them
6. CloudWatch dashboard, alarms, and log groups
7. VPC endpoints and VPC resources, if created

