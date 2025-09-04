# 🛠️ AWS Setup Guide

## 🎯 **Prerequisites**
- AWS Account with CLI configured
- Python 3.9+
- Basic understanding of AWS services

## 🚀 **Quick Setup Steps**

### **1. AWS Services Setup**
```bash
# Configure AWS CLI (if not done)
aws configure
```

### **2. Create S3 Buckets**
```bash
# Create buckets for resume and job description storage
aws s3 mb s3://trujobs-resume-pdfs --region us-east-1
aws s3 mb s3://trujobs-jd-pdfs --region us-east-1
```

### **3. Create OpenSearch Domain**
```bash
# Create OpenSearch domain for vector search
# Note: Use AWS Console for OpenSearch setup (complex CLI command)
```

### **4. Create Lambda Functions**
```bash
# Create resume processor Lambda
aws lambda create-function \
  --function-name resume-processor \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://deployment/resume-processor.zip

# Create job description processor Lambda  
aws lambda create-function \
  --function-name job-description-processor \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://deployment/job-description-processor.zip
```

### **5. Setup S3 Triggers**
```bash
# Run utility scripts
python src/utils/setup_s3_trigger.py
python src/utils/setup_jd_s3_trigger.py
```

## 🔧 **Configuration**

### **Environment Variables**
Set these in your Lambda functions:
```
OPENSEARCH_ENDPOINT=your-opensearch-endpoint
AWS_REGION=us-east-1
```

### **IAM Permissions**
Your Lambda execution role needs:
- S3 read access
- OpenSearch write access  
- Bedrock invoke access
- CloudWatch logs access

## ✅ **Verification**
1. Upload test files to S3 buckets
2. Check CloudWatch logs
3. Verify data in OpenSearch
4. Test matching algorithm

For detailed steps, see individual deployment guides in the docs/ folder.
