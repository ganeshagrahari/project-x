# 🔍 OpenSearch Dev Tools Commands

Use these commands in your OpenSearch Dashboard Dev Tools to explore your data and test similarity search functionality.

## 📊 Basic Data Exploration

### 1. View All Job Descriptions
```json
GET job_descriptions/_search
{
  "query": {
    "match_all": {}
  }
}
```

### 2. View All Resumes
```json
GET resumes/_search
{
  "query": {
    "match_all": {}
  }
}
```

### 3. Get Index Information
```json
GET job_descriptions/_mapping
```

```json
GET resumes/_mapping
```

### 4. Count Documents
```json
GET job_descriptions/_count
```

```json
GET resumes/_count
```

## 🎯 Fetch Specific Documents by ID

### 5. Get Specific Resume by Resume ID
```json
GET resumes/_doc/285d0fb6-0e65-4922-bd24-f462ad85a80d
```
```json
GET resumes/_doc/d6cee2df-264c-4e8a-bccb-dade0969b565
```

**Alternative method with search:**
```json
GET resumes/_search
{
  "query": {
    "term": {
      "_id": "d3b46fcc-483c-48c9-975f-c05ba84f05ea"
    }
  }
}
```

### 6. Get Specific Job Description by Job ID
```json
GET job_descriptions/_doc/320945ca-684a-4310-9acf-eef21a93267b
```

**Alternative method with search:**
```json
GET job_descriptions/_search
{
  "query": {
    "term": {
      "_id": "9979fc61-c742-4606-b2e6-78816699594b"
    }
  }
}
```

### 7. Get Multiple Specific Documents by IDs
```json
GET resumes/_mget
{
  "ids": [
    "d3b46fcc-483c-48c9-975f-c05ba84f05ea",
    "another-resume-id-here"
  ]
}
```

```json
GET job_descriptions/_mget
{
  "ids": [
    "9979fc61-c742-4606-b2e6-78816699594b",
    "another-job-id-here"
  ]
}
```

## 🔎 Sample Data Queries

### 8. Get First 5 Job Descriptions with Details
```json
GET job_descriptions/_search
{
  "query": {
    "match_all": {}
  },
  "size": 5,
  "_source": ["job_id", "title", "company", "skills", "location", "experience_level"]
}
```

### 9. Get First 5 Resumes with Details
```json
GET resumes/_search
{
  "query": {
    "match_all": {}
  },
  "size": 5,
  "_source": ["resume_id", "name", "skills", "experience", "location", "education"]
}
```

### 10. Search for Specific Skills (Job Descriptions)
```json
GET job_descriptions/_search
{
  "query": {
    "match": {
      "skills": "Python"
    }
  },
  "size": 3
}
```

### 11. Search for Specific Skills (Resumes)
```json
GET resumes/_search
{
  "query": {
    "match": {
      "skills": "JavaScript"
    }
  },
  "size": 3
}
```

## 🎯 Testing Data for Similarity API

### 12. Get Sample Job ID for Testing
```json
GET job_descriptions/_search
{
  "query": {
    "match_all": {}
  },
  "size": 1,
  "_source": ["job_id", "title", "skills"]
}
```

### 13. Get Sample Resume ID for Testing
```json
GET resumes/_search
{
  "query": {
    "match_all": {}
  },
  "size": 1,
  "_source": ["resume_id", "name", "skills"]
}
```

### 14. Find Jobs with Specific Experience Level
```json
GET job_descriptions/_search
{
  "query": {
    "match": {
      "experience_level": "mid-level"
    }
  },
  "size": 2
}
```

### 15. Find Resumes with Specific Location
```json
GET resumes/_search
{
  "query": {
    "match": {
      "location": "New York"
    }
  },
  "size": 2
}
```

## 🔧 Advanced Queries for Testing

### 16. Get Jobs with Multiple Criteria
```json
GET job_descriptions/_search
{
  "query": {
    "bool": {
      "must": [
        {"match": {"skills": "Python"}},
        {"match": {"experience_level": "senior"}}
      ]
    }
  },
  "size": 3
}
```

### 17. Get Vector Embeddings (if available)
```json
GET job_descriptions/_search
{
  "query": {
    "match_all": {}
  },
  "size": 1,
  "_source": ["job_id", "embedding"]
}
```

## 📝 Data Extraction for API Testing

### 18. Extract Job IDs for API Testing
```json
GET job_descriptions/_search
{
  "query": {
    "match_all": {}
  },
  "size": 10,
  "_source": ["job_id"]
}
```

### 19. Extract Resume IDs for API Testing
```json
GET resumes/_search
{
  "query": {
    "match_all": {}
  },
  "size": 10,
  "_source": ["resume_id"]
}
```

## 🎯 How to Use These Commands:

1. **Access OpenSearch Dashboard**:
   - Go to your OpenSearch Dashboard URL
   - Navigate to "Dev Tools" section

2. **Copy and Paste Commands**:
   - Copy any command from above
   - Paste in the left panel of Dev Tools
   - Click the "Play" button or press Ctrl+Enter

3. **Get Test Data**:
   - Use commands #9 and #10 to get sample IDs
   - Use these IDs in your similarity API testing

4. **For Similarity API Testing**:
   - First run command #12 to get a `job_id`
   - Run command #13 to get a `resume_id`
   - **Get specific document details**:
     - Use command #5 with actual resume ID: `GET resumes/_doc/YOUR_RESUME_ID`
     - Use command #6 with actual job ID: `GET job_descriptions/_doc/YOUR_JOB_ID`
   - Then use these IDs in your Postman/curl tests
   - Example: If you get `job_id: "12345"`, use it in your API calls

## 🚀 Next Steps:
1. Run these commands to explore your data
2. Use commands #5 and #6 to get complete details of specific documents
3. Note down some `job_id` and `resume_id` values from commands #12 and #13
4. Use these IDs to test your similarity search API with real data!

## 📋 **Common Use Cases:**

### **To fetch specific documents for API testing:**
```bash
# Replace with actual IDs from your data
GET resumes/_doc/d3b46fcc-483c-48c9-975f-c05ba84f05ea
GET job_descriptions/_doc/9979fc61-c742-4606-b2e6-78816699594b
```

### **To verify data before API calls:**
```bash
# Check if resume exists
GET resumes/_doc/YOUR_RESUME_ID

# Check if job exists  
GET job_descriptions/_doc/YOUR_JOB_ID
```
s