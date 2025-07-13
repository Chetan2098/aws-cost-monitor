# AWS Cost Anomaly Monitor (Lambda)

This Lambda function analyzes AWS Cost Explorer data daily and detects service cost spikes compared to the past 7 days. If a service exceeds 10% of its weekly average, it triggers an SNS alert.

### Features:
- Uses UnblendedCost metric
- Checks daily costs against weekly per-service averages
- Sends notifications via SNS

### Environment Variables
- SNS_TOPIC_ARN: ARN of the SNS topic for alerts

### Deployment
Use Terraform, CDK, or manually upload the code as a Lambda function. Requires permission to call:
- ce:GetCostAndUsage
- sns:Publish

### Technology stack
-aws lambda
-aws sns
-aws eventbridge
-aws iam 

### We can use terrafrom to deploy it using terraform aswell
Check terrafomr wrapper for deployemt
Usee below command to deploy 
-terraform init 
-terraform apply
-terrafrom destory


### source_code_hash
source_code_hash = filebase64sha256("${path.module}/packages/cost_analyzer.zip")
This tells Terraform:

"Calculate the base64-encoded SHA-256 hash of my cost_analyzer.zip file. If the file changes, the hash will change, and Lambda should be updated."

✅ Why it matters:
AWS Lambda requires a source_code_hash when you're passing a local .zip file via filename. This hash serves two purposes:

Change detection: Helps Terraform know when the zip has changed so it can re-deploy the Lambda.

AWS validation: AWS uses the hash to verify the integrity of the uploaded zip file.

Without it, Terraform might not trigger an update, even if the zip content changes.