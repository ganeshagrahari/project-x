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

## 🔎 Sample Data Queries

### 5. Get First 5 Job Descriptions with Details
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

### 6. Get First 5 Resumes with Details
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

### 7. Search for Specific Skills (Job Descriptions)
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

### 8. Search for Specific Skills (Resumes)
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

### 9. Get Sample Job ID for Testing
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

### 10. Get Sample Resume ID for Testing
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

### 11. Find Jobs with Specific Experience Level
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

### 12. Find Resumes with Specific Location
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

### 13. Get Jobs with Multiple Criteria
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

### 14. Get Vector Embeddings (if available)
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

### 15. Extract Job IDs for API Testing
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

### 16. Extract Resume IDs for API Testing
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
   - First run command #9 to get a `job_id`
   - Then use that `job_id` in your Postman/curl tests
   - Example: If you get `job_id: "12345"`, use it in your API calls

## 🚀 Next Steps:
1. Run these commands to explore your data
2. Note down some `job_id` and `resume_id` values
3. Use these IDs to test your similarity search API with real data!
s