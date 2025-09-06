# 🧹 Data Cleanup Guide - Remove All Resumes & Job Descriptions

## 📋 **Overview**

This guide provides step-by-step instructions to completely clean up all existing resume and job description data from your AWS infrastructure before loading real-world data.

**⚠️ WARNING**: This process will permanently delete all existing data. Make sure you want to proceed before executing these commands.

---

## 🗂️ **What Will Be Cleaned**

### **S3 Buckets:**
- `trujobs-resume-pdfs` - All PDF files and any other objects
- `trujobs-jd-pdfs` - All PDF files and any other objects

### **OpenSearch Indices:**
- `resumes` index - All resume documents and embeddings
- `job_descriptions` index - All job description documents and embeddings

---

## 🔧 **Method 1: AWS Console (GUI)**

### **🗄️ Clean S3 Buckets**

#### **Step 1: Clean Resume Bucket**
1. Open AWS Console → S3 Service
2. Navigate to bucket: `trujobs-resume-pdfs`
3. Select all objects (use "Select all" checkbox)
4. Click "Delete" button
5. Type "delete" in confirmation box
6. Click "Delete objects"

#### **Step 2: Clean Job Description Bucket**
1. Navigate to bucket: `trujobs-jd-pdfs`
2. Select all objects (use "Select all" checkbox)
3. Click "Delete" button
4. Type "delete" in confirmation box
5. Click "Delete objects"

### **🔍 Clean OpenSearch Indices**

#### **Step 1: Access OpenSearch Dashboard**
1. Go to AWS Console → OpenSearch Service
2. Click on domain: `recruitment-search`
3. Click "OpenSearch Dashboards URL"
4. Login with your credentials

#### **Step 2: Delete Resume Index**
1. In OpenSearch Dashboard, go to "Dev Tools"
2. Run this command:
```json
DELETE resumes
```
3. Verify deletion:
```json
GET resumes
```
*(Should return "index_not_found_exception")*

#### **Step 3: Delete Job Descriptions Index**
1. In Dev Tools, run:
```json
DELETE job_descriptions
```
2. Verify deletion:
```json
GET job_descriptions
```
*(Should return "index_not_found_exception")*

---

## 💻 **Method 2: AWS CLI Commands**

### **Prerequisites:**
- AWS CLI installed and configured
- Proper permissions for S3 and OpenSearch

### **🗄️ Clean S3 Buckets**

#### **Delete All Resume PDFs:**
```bash
# List objects first (optional - to see what will be deleted)
aws s3 ls s3://trujobs-resume-pdfs --recursive

# Delete all objects
aws s3 rm s3://trujobs-resume-pdfs --recursive

# Verify bucket is empty
aws s3 ls s3://trujobs-resume-pdfs
```

#### **Delete All Job Description PDFs:**
```bash
# List objects first (optional)
aws s3 ls s3://trujobs-jd-pdfs --recursive

# Delete all objects
aws s3 rm s3://trujobs-jd-pdfs --recursive

# Verify bucket is empty
aws s3 ls s3://trujobs-jd-pdfs
```

### **🔍 Clean OpenSearch via API**

#### **Get OpenSearch Endpoint:**
```bash
# Replace with your actual domain name
aws opensearch describe-domain --domain-name recruitment-search --query 'DomainStatus.Endpoint' --output text
```

#### **Delete Indices (using curl):**
```bash
# Set your OpenSearch endpoint
OPENSEARCH_ENDPOINT="https://search-recruitment-search-xr3oxgazrekcvieeeogvudpf6u.aos.us-east-1.on.aws"

# Delete resumes index
curl -X DELETE "$OPENSEARCH_ENDPOINT/resumes" \
  --aws-sigv4 "aws:amz:us-east-1:es" \
  --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY"

# Delete job_descriptions index
curl -X DELETE "$OPENSEARCH_ENDPOINT/job_descriptions" \
  --aws-sigv4 "aws:amz:us-east-1:es" \
  --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY"
```

---

## 📋 **Method 3: OpenSearch Dev Tools (Recommended)**

### **🔍 Complete OpenSearch Cleanup**

#### **Step 1: Check Current Data**
```json
# See what indices exist
GET _cat/indices

# Count documents in each index
GET resumes/_count
GET job_descriptions/_count
```

#### **Step 2: Delete All Resume Documents**
```json
# Option A: Delete entire index (faster)
DELETE resumes

# Option B: Delete all documents but keep index structure
POST resumes/_delete_by_query
{
  "query": {
    "match_all": {}
  }
}
```

#### **Step 3: Delete All Job Description Documents**
```json
# Option A: Delete entire index (faster)
DELETE job_descriptions

# Option B: Delete all documents but keep index structure
POST job_descriptions/_delete_by_query
{
  "query": {
    "match_all": {}
  }
}
```

#### **Step 4: Verify Cleanup**
```json
# Check if indices still exist
GET _cat/indices

# If indices were deleted, this should return errors
GET resumes/_count
GET job_descriptions/_count
```

**🔍 How to Read the Indices Output:**

When you run `GET _cat/indices`, you should see a list of all existing indices. After successful cleanup, you should **NOT** see:
- `resumes` 
- `job_descriptions`

**Example of CLEAN state (what you want to see):**
```
green open .plugins-ml-model-group           0EMX3y2aTYSMAGGNa8fYbg 1 0  2 0  11.7kb  11.7kb
green open .plugins-ml-config                owkY2YzETaisai7QqlwJjg 1 0  9 0  14.1kb  14.1kb
green open .opensearch-observability         Obh_ZiEkSP6OdxuYJPvpDQ 1 0  0 0    208b    208b
... (other system indices starting with dots)
```

**✅ SUCCESS INDICATORS:**
- No `resumes` index in the list
- No `job_descriptions` index in the list  
- Only system indices (starting with dots) are present
- Running `GET resumes/_count` returns "index_not_found_exception"
- Running `GET job_descriptions/_count` returns "index_not_found_exception"

**❌ If you still see your data indices:**
```
green open resumes                           xyz123... 1 0  9 0  1.2mb  1.2mb
green open job_descriptions                  abc456... 1 0  9 0  1.5mb  1.5mb
```
This means cleanup was not successful - repeat the DELETE commands.

#### **Step 5: Recreate Indices (Optional)**
If you want to keep the index structure but remove data:
```json
# Create resumes index with mapping
PUT resumes
{
  "mappings": {
    "properties": {
      "file_name": {"type": "keyword"},
      "text_content": {"type": "text"},
      "metadata": {"type": "object"},
      "embeddings": {
        "type": "knn_vector",
        "dimension": 1536,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimilarity"
        }
      },
      "processed_at": {"type": "date"},
      "document_type": {"type": "keyword"}
    }
  }
}

# Create job_descriptions index with mapping
PUT job_descriptions
{
  "mappings": {
    "properties": {
      "file_name": {"type": "keyword"},
      "text_content": {"type": "text"},
      "metadata": {"type": "object"},
      "embeddings": {
        "type": "knn_vector",
        "dimension": 1536,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimilarity"
        }
      },
      "processed_at": {"type": "date"},
      "document_type": {"type": "keyword"}
    }
  }
}
```

---

## ✅ **Verification Steps**

### **1. Verify S3 Cleanup**
```bash
# Both commands should return empty or "no objects found"
aws s3 ls s3://trujobs-resume-pdfs
aws s3 ls s3://trujobs-jd-pdfs
```

### **2. Verify OpenSearch Cleanup**
```json
# In OpenSearch Dev Tools
GET _cat/indices
GET resumes/_count
GET job_descriptions/_count
```

**🎯 What to Look For:**

**✅ SUCCESSFUL CLEANUP:**
- `GET _cat/indices` shows only system indices (starting with dots like `.plugins-ml-model`, `.kibana_1`, etc.)
- No `resumes` or `job_descriptions` indices in the list
- `GET resumes/_count` returns: `{"error": {"type": "index_not_found_exception"}}`
- `GET job_descriptions/_count` returns: `{"error": {"type": "index_not_found_exception"}}`

**❌ CLEANUP STILL NEEDED:**
- You see `resumes` or `job_descriptions` in the indices list
- Count queries return actual numbers instead of errors

### **3. Test API Endpoints**
```bash
# Health check should still work
curl "https://gkw40ufkhe.execute-api.us-east-1.amazonaws.com/prod/health"

# These should return empty results or errors (expected)
curl -X POST "https://gkw40ufkhe.execute-api.us-east-1.amazonaws.com/prod/search/resumes" \
  -H "Content-Type: application/json" \
  -d '{"job_id": "any-id", "limit": 5}'
```

---

## 🔄 **After Cleanup - Preparing for Real Data**

### **1. Indices Will Be Auto-Created**
- When you upload new PDFs to S3, the Lambda functions will automatically recreate the indices
- No manual intervention needed for index creation

### **2. Upload Process**
1. Upload real resume PDFs to `s3://trujobs-resume-pdfs/`
2. Upload real job description PDFs to `s3://trujobs-jd-pdfs/`
3. Lambda functions will automatically process and index the data
4. New data will be available via API within 10-15 seconds per document

### **3. Monitor Processing**
- Check CloudWatch logs for Lambda functions
- Use OpenSearch Dev Tools to verify data is being indexed
- Test API endpoints to confirm functionality

---

## ⚠️ **Important Notes**

### **🔒 Backup Considerations**
- **No backup needed** if you're replacing with real data
- **Create backup** if you want to preserve current test data:
  ```bash
  # Export current data (optional)
  elasticdump --input="$OPENSEARCH_ENDPOINT/resumes" --output=resumes_backup.json
  elasticdump --input="$OPENSEARCH_ENDPOINT/job_descriptions" --output=jobs_backup.json
  ```

### **💰 Cost Implications**
- Deleting data reduces storage costs
- S3 cleanup is immediate
- OpenSearch storage is freed up after deletion

### **🔄 Recovery**
- Data deletion is permanent
- To restore, you'll need to re-upload PDFs to S3
- Lambda functions will automatically reprocess everything

---

## 🎯 **Recommended Approach**

### **For Complete Fresh Start:**
1. **Use OpenSearch Dev Tools** (Method 3) to delete indices
2. **Use AWS Console** (Method 1) to clean S3 buckets
3. **Verify cleanup** using the verification steps
4. **Upload real data** to S3 buckets
5. **Monitor processing** through CloudWatch and OpenSearch

### **Quick Commands Summary:**
```json
# OpenSearch Dev Tools - Delete everything
DELETE resumes
DELETE job_descriptions
GET _cat/indices
```

```bash
# AWS CLI - Clean S3 buckets
aws s3 rm s3://trujobs-resume-pdfs --recursive
aws s3 rm s3://trujobs-jd-pdfs --recursive
```

---

## 🚀 **Post-Cleanup Verification**

After cleanup, your system should be in a clean state ready for real-world data:

- ✅ S3 buckets empty but functional
- ✅ Lambda functions ready to process new uploads
- ✅ API endpoints operational (but returning empty results)
- ✅ OpenSearch domain ready for new indices
- ✅ All processing pipelines intact and ready

**You're now ready to upload real resume and job description data!** 🎉

---

*Remember: This cleanup is irreversible. Make sure you have backups of any data you want to preserve before proceeding.*
