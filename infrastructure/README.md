# Infrastructure

Team 14 uses CloudFormation YAML for bonus path **E. Infrastructure as Code**.

Template:

- `cloudformation.yaml`

The template defines the BudgetBot serverless infrastructure:

- S3 frontend bucket with Block Public Access and SSE-S3 encryption
- CloudFront distribution with Origin Access Control
- S3 raw statements bucket with Block Public Access and SSE-S3 encryption
- DynamoDB transaction table with on-demand billing and PITR
- VPC with two public subnets and two private Lambda subnets across two AZs
- S3 and DynamoDB Gateway Endpoints
- Bedrock Runtime and CloudWatch Monitoring Interface Endpoints
- Lambda execution role with least-privilege inline policy
- Optional Lambda + API Gateway HTTP API when a Lambda zip artifact is provided
- CloudWatch dashboard and low-confidence transaction alarm
- Required W7 tags on supported resources

## Deploy Foundation Resources

This deploys the network, buckets, DynamoDB, IAM role, CloudFront, dashboard, and alarm.
It does not deploy Lambda/API Gateway until `DeployApplication=true`.

```bash
aws cloudformation deploy \
  --profile hackathon \
  --region ap-southeast-1 \
  --stack-name team14-budgetbot-iac \
  --template-file infrastructure/cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    ResourceNamePrefix=team14-budgetbot-cfn \
    OwnerTag=Team14 \
    EnvironmentTag=hackathon \
    DeployApplication=false
```

## Deploy Application Resources

After packaging the backend Lambda zip and uploading it to S3, redeploy with:

```bash
aws cloudformation deploy \
  --profile hackathon \
  --region ap-southeast-1 \
  --stack-name team14-budgetbot-iac \
  --template-file infrastructure/cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    ResourceNamePrefix=team14-budgetbot-cfn \
    OwnerTag=Team14 \
    EnvironmentTag=hackathon \
    DeployApplication=true \
    LambdaCodeS3Bucket=<artifact-bucket> \
    LambdaCodeS3Key=<lambda-zip-key>
```

## Inspect Outputs

```bash
aws cloudformation describe-stacks \
  --profile hackathon \
  --region ap-southeast-1 \
  --stack-name team14-budgetbot-iac \
  --query 'Stacks[0].Outputs'
```

## Teardown

Empty S3 buckets first, then delete the stack:

```bash
aws cloudformation delete-stack \
  --profile hackathon \
  --region ap-southeast-1 \
  --stack-name team14-budgetbot-iac
```
