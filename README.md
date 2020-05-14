# Twilio-AWS-Lex

AWS Lex with lambdas, DynamoDB, S3, and Simple Email Service

Chat Bot that collects survey data, populates to DynamoDB via lambda, a second lambda to format data and drop in S3 bucket, a third lambda function to email survey to clinician after file uploaded to S3 bucket
