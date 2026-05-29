# Teardown Confirmation

Complete this file after the Sunday 1/6 EOD teardown and commit it with the final
Monday 2/6 Cost Explorer screenshot.

## Teardown Status

- Teardown date:
- AWS account: `325137989598`
- AWS region: `ap-southeast-1`
- Confirmed by:
- Final Cost Explorer screenshot: `docs/teardown_confirmed.png`

## Primary Teardown Command

Most runtime resources are managed by CloudFormation. Delete the stack first:

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

If stack deletion fails because S3 buckets are not empty, empty the relevant
buckets, then rerun the delete command.

## CloudFormation Managed Resources

- [ ] CloudFormation stack deleted: `team14-budgetbot-iac`
- [ ] CloudFront distribution deleted: `E349TWP6TRPSOC`
- [ ] API Gateway HTTP API deleted: `mlhwir8gc5`
- [ ] Lambda function deleted: `team14-budgetbot-cfn-backend`
- [ ] Lambda execution role deleted: `team14-budgetbot-cfn-lambda-role`
- [ ] DynamoDB table deleted: `team14-budgetbot-cfn-transactions`
- [ ] S3 frontend bucket deleted: `team14-budgetbot-cfn-frontend-325137989598-ap-southeast-1`
- [ ] S3 raw statement bucket deleted: `team14-budgetbot-cfn-raw-325137989598-ap-southeast-1`
- [ ] CloudWatch dashboard deleted: `team14-budgetbot-cfn-observability`
- [ ] CloudWatch alarm deleted: `team14-budgetbot-cfn-low-confidence-transactions`
- [ ] CloudWatch Logs log group deleted: `/aws/lambda/team14-budgetbot-cfn-backend`
- [ ] VPC deleted: `vpc-044f26a2a760491ba`
- [ ] Private/public subnets deleted
- [ ] Security groups deleted
- [ ] VPC endpoints deleted: S3, DynamoDB, Bedrock Runtime, CloudWatch Monitoring
- [ ] Route tables and Internet Gateway deleted

## Resources Created Outside The Main Stack

- [ ] S3 artifact bucket emptied and deleted: `team14-budgetbot-artifacts-325137989598-ap-southeast-1`
- [ ] Route 53 custom domain records removed: `budgetbot.topjob.id.vn`
- [ ] Route 53 hosted zone removed if created only for this hackathon
- [ ] ACM certificate deleted if created only for this hackathon: `budgetbot.topjob.id.vn`
- [ ] SNS topic deleted: `W7-Team14-BudgetAlerts`
- [ ] AWS Budget deleted: `W7-Team14-HardCap-100USD`
- [ ] Cost Anomaly Detection subscription/monitor removed if created only for this hackathon

## Verification Commands

```bash
aws cloudformation describe-stacks \
  --profile hackathon \
  --region ap-southeast-1 \
  --stack-name team14-budgetbot-iac

aws s3 ls --profile hackathon | grep team14-budgetbot || true

aws lambda get-function \
  --profile hackathon \
  --region ap-southeast-1 \
  --function-name team14-budgetbot-cfn-backend

aws dynamodb describe-table \
  --profile hackathon \
  --region ap-southeast-1 \
  --table-name team14-budgetbot-cfn-transactions

aws apigatewayv2 get-api \
  --profile hackathon \
  --region ap-southeast-1 \
  --api-id mlhwir8gc5
```

Expected result after teardown: CloudFormation stack is gone, S3 lookup returns
no Team 14 buckets, and service-specific commands return `ResourceNotFound`
or `NotFoundException`.

## Final Cost Check

- [ ] Monday 2/6 Cost Explorer screenshot committed as `docs/teardown_confirmed.png`
- [ ] Cost Explorer filtered by tag `Team=G14`
- [ ] Total spend remains under `$100`
- [ ] Bonus target checked: total spend under `$30` with clean teardown
- Final total spend:
- Top cost drivers:
- Notes:
