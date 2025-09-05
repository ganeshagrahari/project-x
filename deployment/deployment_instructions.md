# 🚀 AWS Lambda Deployment Instructions

## 📦 Package Information
- **Function Name**: similarity-search-api
- **Handler**: lambda_function.lambda_handler
- **Runtime**: Python 3.11
- **Timeout**: 30 seconds
- **Memory**: 512 MB

## 🔧 Required IAM Permissions
Your Lambda function needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "es:ESHttpGet",
                "es:ESHttpPost",
                "es:ESHttpPut",
                "es:ESHttpDelete"
            ],
            "Resource": "arn:aws:es:us-east-1:*:domain/search-trujobs-opensearch-*/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:us-east-1:*:*"
        }
    ]
}
```

## 🎯 Test Events

### Search Resumes for Job
```json
{
    "action": "search_resumes",
    "job_id": "your-job-document-id",
    "limit": 10,
    "min_score": 60.0
}
```

### Search Jobs for Resume
```json
{
    "action": "search_jobs",
    "resume_id": "your-resume-document-id",
    "limit": 10,
    "min_score": 60.0
}
```

### Detailed Match Analysis
```json
{
    "action": "detailed_match",
    "resume_id": "your-resume-document-id",
    "job_id": "your-job-document-id"
}
```

## 🚀 Deployment Steps

1. **Upload ZIP file** to AWS Lambda console
2. **Set configuration**:
   - Handler: `lambda_function.lambda_handler`
   - Runtime: Python 3.11
   - Timeout: 30 seconds
   - Memory: 512 MB
3. **Add IAM permissions** (see above)
4. **Test with sample events** (see above)
5. **Monitor CloudWatch logs** for any issues

## 🔗 Integration Options

### Option A: Direct Lambda Invocation
```python
import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')

response = lambda_client.invoke(
    FunctionName='similarity-search-api',
    Payload=json.dumps({
        "action": "search_resumes",
        "job_id": "your-job-id",
        "limit": 5,
        "min_score": 70.0
    })
)

result = json.loads(response['Payload'].read())
```

### Option B: API Gateway (for web access)
1. Create API Gateway REST API
2. Create resource and method (POST)
3. Set integration to Lambda function
4. Enable CORS if needed
5. Deploy API to stage

## 📊 Expected Response Format
```json
{
    "success": true,
    "job_id": "job-123",
    "total_candidates_analyzed": 45,
    "qualified_candidates": 8,
    "matches": [
        {
            "resume_id": "resume-456",
            "score": 87.5,
            "component_scores": {
                "skills_score": 92.0,
                "experience_score": 85.0,
                "location_score": 95.0
            },
            "candidate_info": {
                "name": "John Doe",
                "skills": ["Python", "AWS", "ML"],
                "experience_years": 5
            },
            "recommendations": [
                "Excellent match! Strong candidate for this position"
            ]
        }
    ]
}
```
