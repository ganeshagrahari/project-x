# Job Description Processor Deployment Guide

This guide outlines the steps to deploy and configure the job description processing Lambda function.

## Prerequisites

- AWS account with access to Lambda, S3, Bedrock, and OpenSearch
- AWS CLI configured with appropriate permissions
- Python 3.9 or higher for local development
- S3 bucket for job descriptions (`trujobs-jd-pdfs`)

## Deployment Steps

### 1. Create Lambda Deployment Package

```bash
# Create a directory for the Lambda package
mkdir -p lambda-packages/job-description-processor

# Copy the Lambda function file
cp job_description_processor_lambda.py lambda-packages/job-description-processor/lambda_function.py

# Change to the package directory
cd lambda-packages/job-description-processor

# Install dependencies
pip install PyPDF2 opensearchpy aws-requests-auth -t .

# Create deployment zip
zip -r ../job-description-processor.zip .

# Return to project root
cd ../..
```

### 2. Create Lambda Function

Create a new Lambda function using the AWS Console or AWS CLI:

```bash
# Using AWS CLI
aws lambda create-function \
  --function-name job-description-processor \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --timeout 300 \
  --memory-size 512 \
  --role arn:aws:iam::<ACCOUNT-ID>:role/lambda-bedrock-s3-opensearch-role \
  --zip-file fileb://lambda-packages/job-description-processor.zip
```

### 3. Configure Environment Variables

Set the required environment variables for the Lambda function:

- `OPENSEARCH_ENDPOINT`: Your OpenSearch domain endpoint

```bash
# Using AWS CLI
aws lambda update-function-configuration \
  --function-name job-description-processor \
  --environment "Variables={OPENSEARCH_ENDPOINT=https://your-opensearch-endpoint.region.es.amazonaws.com}"
```

### 4. Set Up S3 Trigger

Run the S3 trigger setup script:

```bash
# Using the setup script
python setup_jd_s3_trigger.py trujobs-jd-pdfs job-description-processor
```

This sets up an S3 trigger for the job descriptions bucket to invoke the Lambda function.

## Testing the Deployment

### 1. Upload a Sample Job Description

You can upload a job description file in either PDF or text format:

```bash
# Upload a PDF
aws s3 cp sample_job_description.pdf s3://trujobs-jd-pdfs/

# Upload a text file
aws s3 cp sample_job_description.txt s3://trujobs-jd-pdfs/

# Upload a JSON file with text and metadata
aws s3 cp sample_job_description.json s3://trujobs-jd-pdfs/
```

### 2. Verify Processing

Check the CloudWatch logs for the Lambda function:

```bash
# Get the latest log events
aws logs get-log-events \
  --log-group-name /aws/lambda/job-description-processor \
  --log-stream-name $(aws logs describe-log-streams \
  --log-group-name /aws/lambda/job-description-processor \
  --order-by LastEventTime \
  --descending \
  --limit 1 \
  --query 'logStreams[0].logStreamName' \
  --output text)
```

### 3. Verify Data in OpenSearch

You can use the verify_opensearch_data.py script or query OpenSearch directly:

```bash
# Using the OpenSearch Dev Tools console:
GET job_descriptions/_search
{
  "query": {
    "match_all": {}
  }
}
```

## Using the Resume-Job Matching Utility

The `match_resumes_to_job.py` script allows you to find matching resumes for a job description:

```bash
# Get the job description ID from OpenSearch
JOB_ID=$(aws opensearch --region ap-south-1 --query "Items[0].Id" --output text)

# Run the matching utility
python match_resumes_to_job.py $JOB_ID

# Specify number of results (optional)
python match_resumes_to_job.py $JOB_ID 20
```

## Troubleshooting

- **S3 Trigger Not Working**: Verify the S3 event notification configuration and Lambda permissions
- **OpenSearch Connection Failure**: Check the OPENSEARCH_ENDPOINT environment variable and IAM permissions
- **PDF Processing Error**: Ensure the PyPDF2 package is correctly installed in the Lambda package
- **Bedrock API Error**: Verify that the Bedrock models (Claude 3 Haiku and Titan) are enabled in your account

## Next Steps

After successfully deploying the job description processor, you can proceed to:

1. Develop the search API for more advanced queries
2. Create a web interface for resume and job management
3. Implement additional matching algorithms and ranking features
