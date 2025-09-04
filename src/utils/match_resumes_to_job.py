import boto3
import json
import logging
import os
import sys
from opensearchpy import OpenSearch, RequestsHttpConnection
from aws_requests_auth.aws_auth import AWSRequestsAuth

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def search_matching_resumes(job_description_id, limit=10):
    """
    Search for matching resumes for a given job description
    """
    try:
        # Get OpenSearch endpoint from environment variables
        opensearch_endpoint = os.environ.get('OPENSEARCH_ENDPOINT')
        if not opensearch_endpoint:
            raise ValueError("OPENSEARCH_ENDPOINT environment variable not set")
        
        # Create OpenSearch client for data operations
        credentials = boto3.Session().get_credentials()
        awsauth = AWSRequestsAuth(
            aws_access_key=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_token=credentials.token,
            aws_region='ap-south-1',
            aws_service='es',
            aws_host=opensearch_endpoint
        )
        
        opensearch_client = OpenSearch(
            hosts=[{'host': opensearch_endpoint.replace('https://', ''), 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
        
        # Get job description from OpenSearch
        job_desc_response = opensearch_client.get(
            index='job_descriptions',
            id=job_description_id
        )
        
        job_description = job_desc_response['_source']
        job_embedding = job_description['embeddings']
        
        # Perform k-NN search
        knn_query = {
            "size": limit,
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "document_type": "resume"
                            }
                        }
                    ]
                }
            },
            "knn": {
                "embeddings": {
                    "vector": job_embedding,
                    "k": limit
                }
            }
        }
        
        response = opensearch_client.search(
            body=knn_query,
            index='resumes'
        )
        
        # Process and return results
        results = []
        for hit in response['hits']['hits']:
            resume = hit['_source']
            metadata = resume.get('metadata', {})
            
            # Extract relevant information
            result = {
                'resume_id': hit['_id'],
                'score': hit['_score'],
                'name': metadata.get('name', 'Unknown'),
                'match_details': calculate_match_details(job_description, resume),
                'metadata': metadata
            }
            
            results.append(result)
        
        return {
            'job_description': {
                'id': job_description_id,
                'title': job_description.get('metadata', {}).get('job_title', 'Unknown Job')
            },
            'matching_resumes': results
        }
        
    except Exception as e:
        logger.error(f"Error searching for matching resumes: {str(e)}")
        return {
            'error': str(e)
        }

def calculate_match_details(job_description, resume):
    """
    Calculate detailed matching information between a job description and resume
    """
    try:
        job_metadata = job_description.get('metadata', {})
        resume_metadata = resume.get('metadata', {})
        
        # Extract key information
        job_skills = job_metadata.get('skills_required', [])
        job_requirements = job_metadata.get('job_requirements', [])
        resume_skills = resume_metadata.get('skills', [])
        
        # Calculate skills match
        matching_skills = []
        for skill in resume_skills:
            # Simple string matching (can be improved with semantic matching)
            if any(skill.lower() in req.lower() for req in job_skills + job_requirements):
                matching_skills.append(skill)
        
        # Calculate experience match
        experience_years = resume_metadata.get('total_experience_years', 0)
        required_experience = job_metadata.get('experience_level', '')
        experience_match = False
        
        # Simple experience matching logic (can be improved)
        if 'entry' in required_experience.lower() and experience_years <= 2:
            experience_match = True
        elif 'mid' in required_experience.lower() and 2 <= experience_years <= 5:
            experience_match = True
        elif 'senior' in required_experience.lower() and experience_years >= 5:
            experience_match = True
        
        # Calculate overall match percentage (simple algorithm)
        if len(job_skills) > 0:
            skills_match_percentage = (len(matching_skills) / len(job_skills)) * 100
        else:
            skills_match_percentage = 0
        
        # Overall match score (simple weighted average)
        overall_match = skills_match_percentage * 0.7 + (100 if experience_match else 0) * 0.3
        
        return {
            'matching_skills': matching_skills,
            'skills_match_percentage': round(skills_match_percentage, 2),
            'experience_match': experience_match,
            'overall_match_percentage': round(overall_match, 2)
        }
        
    except Exception as e:
        logger.error(f"Error calculating match details: {str(e)}")
        return {
            'error': str(e)
        }

def main():
    """
    Main function to test job description matching
    """
    if len(sys.argv) < 2:
        logger.error("Please provide a job description ID as an argument")
        sys.exit(1)
    
    job_description_id = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    logger.info(f"Searching for matching resumes for job description ID: {job_description_id}")
    results = search_matching_resumes(job_description_id, limit)
    
    # Print results
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
