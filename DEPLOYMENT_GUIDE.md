# 🚀 Lambda Deployment Guide - Modular AI Recruitment System

## 📋 **Overview**
This guide helps you deploy the improved modular Lambda functions for resume and job description processing.

## 🏗️ **Lambda Functions to Deploy**

### **1. Resume Ingestion Lambda**
- **Name:** `resume-ingestion-api`
- **Purpose:** Process uploaded resumes with AI analysis
- **Folder:** `lambda-packages/resume-ingestion-lambda/`

### **2. Job Description Ingestion Lambda** 
- **Name:** `jd-ingestion-api`
- **Purpose:** Process job descriptions with AI analysis
- **Folder:** `lambda-packages/jd-ingestion-lambda/`

---

## 🔧 **Deployment Steps**

### **📦 Step 1: Create Lambda Layers (Reuse Existing)**
Since you already have working Lambda layers with the required dependencies, we'll reuse them:
- **Layer Name:** Your existing layer with PyPDF2, opensearch-py, aws-requests-auth

### **⚡ Step 2: Deploy Resume Ingestion Lambda**

1. **Go to Lambda Console:**
   - AWS Console → Lambda → Create function

2. **Basic Configuration:**
   - **Function name:** `resume-ingestion-api`
   - **Runtime:** Python 3.9
   - **Architecture:** x86_64
   - **Memory:** 512 MB
   - **Timeout:** 5 minutes

3. **Upload Code:**
   - Zip the contents of `lambda-packages/resume-ingestion-lambda/`
   - Upload to Lambda function

4. **Add Layer:**
   - Add your existing layer with dependencies

5. **Environment Variables:**
   ```
   OPENSEARCH_ENDPOINT = https://search-recruitment-search-xr3oxgazrekcvieeeogvudpf6u.aos.us-east-1.on.aws
   AWS_REGION = us-east-1
   S3_BUCKET_NAME = trujobs-resume-pdfs
   OPENSEARCH_INDEX = resumes
   ```

6. **IAM Permissions:**
   - Attach the same IAM role from your working `resume-processor` function

### **⚡ Step 3: Deploy Job Description Ingestion Lambda**

1. **Create Function:**
   - **Function name:** `jd-ingestion-api`
   - **Runtime:** Python 3.9
   - **Same configuration as above**

2. **Upload Code:**
   - Zip the contents of `lambda-packages/jd-ingestion-lambda/`
   - Upload to Lambda function

3. **Add Layer & Environment Variables:**
   - Same layer and environment variables as resume function

4. **IAM Permissions:**
   - Same IAM role as resume function

---

## 🧪 **Testing the Functions**

### **Test Resume Ingestion:**
```json
{
  "httpMethod": "POST",
  "headers": {
    "Content-Type": "multipart/form-data"
  },
  "body": "base64-encoded-multipart-data",
  "isBase64Encoded": true
}
```

### **Test Job Description Ingestion:**
```json
{
  "httpMethod": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"job_title\": \"Python Developer\", \"company\": \"Tech Corp\", \"description\": \"We are looking for...\", \"requirements\": \"3+ years Python experience\"}"
}
```

---

## 🔍 **Verification Steps**

### **1. Check CloudWatch Logs:**
- Look for successful processing logs
- Verify AI model calls (Claude + Titan)
- Confirm OpenSearch storage

### **2. Query OpenSearch:**
```json
GET /resumes/_search
{
  "query": {
    "match": {
      "document_type": "resume"
    }
  }
}

GET /resumes/_search  
{
  "query": {
    "match": {
      "document_type": "job_description"
    }
  }
}
```

### **3. Verify Data Structure:**
Both resumes and job descriptions should be stored in the same `resumes` index with different `document_type` values.

---

## 🎯 **Next Steps After Deployment**

1. **✅ Deploy both Lambda functions**
2. **✅ Test with sample data**
3. **✅ Verify OpenSearch storage**
4. **🚀 Build search/matching API (Day 3 Phase 2)**
5. **🌐 Create web interface (Days 4-5)**

---

## 🆘 **Troubleshooting**

### **Common Issues:**
- **Import errors:** Ensure all modules are in the same directory
- **Environment variables:** Double-check all required variables are set
- **Permissions:** Use the same IAM role from your working system
- **Dependencies:** Use the existing Lambda layer

### **Debug Commands:**
```python
# Test configuration
from config import Config
print(Config.OPENSEARCH_ENDPOINT)

# Test AI services  
from ai_services import get_metadata_from_bedrock
```

---

**🎉 Ready to deploy your enterprise-grade modular AI recruitment system!**
