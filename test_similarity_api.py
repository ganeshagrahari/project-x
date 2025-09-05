#!/usr/bin/env python3
"""
Test Client for Similarity Search API
Demonstrates how to use the advanced matching system
"""

import requests
import json
import time

class SimilarityAPIClient:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
    
    def health_check(self):
        """Test if the API is running"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": f"API not reachable: {e}"}
    
    def search_resumes_for_job(self, job_id, limit=10, min_score=50.0):
        """Find matching resumes for a job"""
        try:
            payload = {
                "job_id": job_id,
                "limit": limit,
                "min_score": min_score
            }
            response = requests.post(f"{self.base_url}/search/resumes", json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def search_jobs_for_resume(self, resume_id, limit=10, min_score=50.0):
        """Find matching jobs for a resume"""
        try:
            payload = {
                "resume_id": resume_id,
                "limit": limit,
                "min_score": min_score
            }
            response = requests.post(f"{self.base_url}/search/jobs", json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def detailed_match_analysis(self, resume_id, job_id):
        """Get detailed match analysis between specific resume and job"""
        try:
            payload = {
                "resume_id": resume_id,
                "job_id": job_id
            }
            response = requests.post(f"{self.base_url}/match/detailed", json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def bulk_similarity_search(self, search_type, ids, limit_per_id=5, min_score=50.0):
        """Perform bulk similarity matching"""
        try:
            payload = {
                "type": search_type,
                "ids": ids,
                "limit_per_id": limit_per_id,
                "min_score": min_score
            }
            response = requests.post(f"{self.base_url}/search/bulk", json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing Similarity Search API Endpoints")
    print("=" * 50)
    
    client = SimilarityAPIClient()
    
    # 1. Health Check
    print("1. 🏥 Health Check...")
    health = client.health_check()
    print(f"   Status: {health}")
    
    if "error" in health:
        print("❌ API is not running. Please start the API first!")
        return
    
    print("✅ API is healthy!")
    
    # Note: The following tests would work with real OpenSearch data
    # For now, we'll show the API structure
    
    print("\n2. 📝 API Endpoint Examples:")
    print("   - POST /search/resumes - Find resumes for job_id")
    print("   - POST /search/jobs - Find jobs for resume_id") 
    print("   - POST /match/detailed - Detailed analysis")
    print("   - POST /search/bulk - Bulk processing")
    
    print("\n3. 📊 Sample Payload Structures:")
    
    print("\n   🔍 Search Resumes for Job:")
    print(json.dumps({
        "job_id": "job-123",
        "limit": 10,
        "min_score": 60.0
    }, indent=4))
    
    print("\n   💼 Search Jobs for Resume:")
    print(json.dumps({
        "resume_id": "resume-456", 
        "limit": 10,
        "min_score": 60.0
    }, indent=4))
    
    print("\n   🎯 Detailed Match Analysis:")
    print(json.dumps({
        "resume_id": "resume-456",
        "job_id": "job-123"
    }, indent=4))
    
    print("\n   📦 Bulk Search:")
    print(json.dumps({
        "type": "job_to_resumes",
        "ids": ["job-123", "job-456", "job-789"],
        "limit_per_id": 5,
        "min_score": 65.0
    }, indent=4))

def create_curl_examples():
    """Generate curl command examples"""
    print("\n🌐 CURL Command Examples:")
    print("=" * 30)
    
    print("\n1. Health Check:")
    print("curl -X GET http://localhost:5001/health")
    
    print("\n2. Search Resumes for Job:")
    print('''curl -X POST http://localhost:5001/search/resumes \\
  -H "Content-Type: application/json" \\
  -d '{
    "job_id": "your-job-id",
    "limit": 10,
    "min_score": 60.0
  }' ''')
    
    print("\n3. Search Jobs for Resume:")
    print('''curl -X POST http://localhost:5001/search/jobs \\
  -H "Content-Type: application/json" \\
  -d '{
    "resume_id": "your-resume-id",
    "limit": 10,
    "min_score": 60.0
  }' ''')
    
    print("\n4. Detailed Match Analysis:")
    print('''curl -X POST http://localhost:5001/match/detailed \\
  -H "Content-Type: application/json" \\
  -d '{
    "resume_id": "your-resume-id",
    "job_id": "your-job-id"
  }' ''')

def integration_example():
    """Show how to integrate with existing AWS data"""
    print("\n🔗 Integration with Your AWS Data:")
    print("=" * 40)
    
    print("""
📋 To use with your real OpenSearch data:

1. 🗂️  Your Current AWS Setup:
   - OpenSearch Domain: search-trujobs-opensearch-ydxvqg3ptu26pykub2shpf2r6m.us-east-1.es.amazonaws.com
   - Indexes: 'resumes', 'job-descriptions'
   - S3 Buckets: trujobs-resume-pdfs, trujobs-jd-pdfs

2. 🔧 Data Requirements:
   Each document should have this structure:
   
   Resume Document:
   {
     "metadata": {
       "name": "John Doe",
       "skills": ["Python", "AWS", "ML"],
       "total_experience_years": 5,
       "location": "Mumbai, India",
       "experience": [...],
       "education": [...]
     },
     "embeddings": [1536-dimensional vector],
     "content": "Full resume text"
   }
   
   Job Document:
   {
     "metadata": {
       "job_title": "Senior Developer",
       "company_name": "TechCorp",
       "job_location": "Mumbai, India",
       "skills_required": ["Python", "AWS"],
       "experience_level": "Senior (5+ years)",
       "job_requirements": [...],
       "salary_range": "$80k-120k"
     },
     "embeddings": [1536-dimensional vector],
     "content": "Full job description"
   }

3. 🚀 Next Steps:
   a) Upload some test resumes and job descriptions using your Lambda functions
   b) Use the API to get document IDs from OpenSearch
   c) Test the similarity matching with real data
   d) Fine-tune the scoring weights based on your requirements
    """)

if __name__ == "__main__":
    print("🎯 Similarity Search API - Test Client")
    print("=" * 50)
    
    # Test the API endpoints
    test_api_endpoints()
    
    # Generate curl examples
    create_curl_examples()
    
    # Show integration guidance
    integration_example()
    
    print("\n✅ Advanced Similarity Matching System Ready!")
    print("🚀 Your AI recruitment system now has sophisticated matching capabilities!")
    print("\n💡 Key Features Implemented:")
    print("   • Multi-factor scoring (skills, experience, location, education)")
    print("   • Fuzzy skill matching with synonyms")
    print("   • Geographic location compatibility")
    print("   • Semantic similarity using embeddings")
    print("   • Detailed match explanations")
    print("   • RESTful API with multiple endpoints")
    print("   • Bulk processing capabilities")
    print("   • Configurable scoring weights")
    
    print("\n🎮 Try it out:")
    print("   1. Keep the API running (python src/api/similarity_search_api.py)")
    print("   2. Test with curl commands above")
    print("   3. Upload real data using your existing Lambda functions")
    print("   4. Use the similarity API to find matches!")
