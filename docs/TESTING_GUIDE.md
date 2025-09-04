# 🧪 Testing Guide

## 🎯 **Testing Overview**
This guide covers testing procedures for the AI recruitment system.

## 🔥 **System Testing Status**
✅ **Resume Processing**: Fully tested and operational  
✅ **Job Description Processing**: Fully tested and operational  
✅ **S3 Triggers**: Automated testing with file uploads  
✅ **AI Processing**: Claude 3 Haiku and Titan embeddings verified  
✅ **Data Storage**: OpenSearch indices working correctly  

## 🧪 **Testing Procedures**

### **1. Resume Processing Test**
```bash
# Upload a test resume to S3
aws s3 cp test-resume.pdf s3://trujobs-resume-pdfs/

# Monitor CloudWatch logs
aws logs tail /aws/lambda/resume-processor --follow

# Verify data in OpenSearch
python src/utils/verify_opensearch_data.py
```

### **2. Job Description Processing Test**
```bash
# Upload a test job description to S3
aws s3 cp test-job.pdf s3://trujobs-jd-pdfs/

# Monitor CloudWatch logs  
aws logs tail /aws/lambda/job-description-processor --follow

# Verify data storage
python src/utils/verify_opensearch_data.py
```

### **3. Matching Algorithm Test**
```bash
# Test resume-job matching
python src/utils/match_resumes_to_job.py <job_id>

# Example output should show:
# - Similarity scores
# - Matched candidates
# - Skills alignment
```

### **4. OpenSearch Query Testing**
```json
# Test resume search
GET /resumes/_search
{
  "query": {
    "match": {
      "metadata.skills": "Python"
    }
  }
}

# Test job description search
GET /job_descriptions/_search  
{
  "query": {
    "match": {
      "metadata.job_title": "Developer"
    }
  }
}
```

## 📊 **Test Results Verification**

### **Expected Processing Time**
- Resume processing: 10-15 seconds
- Job description processing: 10-15 seconds
- Matching algorithm: 2-3 seconds

### **Expected Data Structure**
- Structured metadata extraction ✅
- 1536-dimensional embeddings ✅
- Proper index separation ✅
- Error handling ✅

## 🔍 **Debugging**

### **Common Issues**
1. **Lambda timeout**: Check function timeout settings
2. **Permission errors**: Verify IAM roles
3. **Region mismatch**: Ensure us-east-1 consistency
4. **Missing dependencies**: Check requirements.txt

### **Log Analysis**
```bash
# Check for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/resume-processor \
  --filter-pattern "ERROR"

# Monitor processing
aws logs filter-log-events \
  --log-group-name /aws/lambda/job-description-processor \
  --filter-pattern "Processing complete"
```

## ✅ **Test Checklist**
- [ ] Resume upload triggers Lambda
- [ ] Job description upload triggers Lambda  
- [ ] CloudWatch logs show processing
- [ ] Data appears in OpenSearch
- [ ] Embeddings are generated
- [ ] Matching algorithm returns results
- [ ] No error messages in logs

## 🎯 **Performance Testing**
- Upload multiple files simultaneously
- Monitor processing times
- Check memory usage
- Verify concurrent processing

For detailed testing scripts and examples, see the samples/ folder.
