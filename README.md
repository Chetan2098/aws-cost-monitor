# aws-cost-monitor
This Lambda function analyzes AWS Cost Explorer data daily and detects service cost spikes compared to the past 7 days. If a service exceeds 10% of its weekly average, it triggers an SNS alert.
