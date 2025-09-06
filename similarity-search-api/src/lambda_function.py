#!/usr/bin/env python3
"""
AWS Lambda Handler for Similarity Search API
Combines advanced_matcher.py + similarity_search_api.py for AWS deployment
"""

import sys
import os

# Add lib directory to Python path for dependencies
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

import json
import os
import sys
import boto3
from typing import Dict, List, Optional

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

# Import our similarity matching components
from advanced_matcher import AdvancedMatcher
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

class LambdaSimilarityAPI:
    def __init__(self):
        """Initialize the Lambda similarity API"""
        self.matcher = AdvancedMatcher()
        self.opensearch_client = self._initialize_opensearch()
    
    def _initialize_opensearch(self):
        """Initialize OpenSearch client for Lambda"""
        try:
            # AWS credentials for OpenSearch (Lambda execution role)
            credentials = boto3.Session().get_credentials()
            awsauth = AWS4Auth(
                credentials.access_key,
                credentials.secret_key,
                'us-east-1',
                'es',
                session_token=credentials.token
            )
            
            # OpenSearch endpoint from environment variable or hardcoded
            opensearch_endpoint = os.environ.get(
                'OPENSEARCH_ENDPOINT',
                'https://search-recruitment-search-xr3oxgazrekcvieeeogvudpf6u.aos.us-east-1.on.aws'
            )
            
            # Remove https:// prefix for client initialization
            host = opensearch_endpoint.replace('https://', '').replace('http://', '')
            
            client = OpenSearch(
                hosts=[{'host': host, 'port': 443}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
            
            return client
            
        except Exception as e:
            print(f"Error initializing OpenSearch: {e}")
            return None
    
    def health_check(self) -> Dict:
        """Health check endpoint"""
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'healthy',
                'service': 'similarity-search-api',
                'opensearch_connected': self.opensearch_client is not None,
                'version': '1.0.0'
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    
    def search_resumes_for_job(self, event_body: Dict) -> Dict:
        """Find best matching resumes for a job description"""
        try:
            job_id = event_body.get('job_id')
            limit = event_body.get('limit', 10)
            min_score = event_body.get('min_score', 50.0)
            
            if not job_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'job_id is required'}),
                    'headers': {'Content-Type': 'application/json'}
                }
            
            results = self._find_matching_resumes(job_id, limit, min_score)
            
            return {
                'statusCode': 200,
                'body': json.dumps(results),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)}),
                'headers': {'Content-Type': 'application/json'}
            }
    
    def search_jobs_for_resume(self, event_body: Dict) -> Dict:
        """Find best matching jobs for a resume"""
        try:
            resume_id = event_body.get('resume_id')
            limit = event_body.get('limit', 10)
            min_score = event_body.get('min_score', 50.0)
            
            if not resume_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'resume_id is required'}),
                    'headers': {'Content-Type': 'application/json'}
                }
            
            results = self._find_matching_jobs(resume_id, limit, min_score)
            
            return {
                'statusCode': 200,
                'body': json.dumps(results),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)}),
                'headers': {'Content-Type': 'application/json'}
            }
    
    def detailed_match_analysis(self, event_body: Dict) -> Dict:
        """Get detailed match analysis between specific resume and job"""
        try:
            resume_id = event_body.get('resume_id')
            job_id = event_body.get('job_id')
            
            if not resume_id or not job_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Both resume_id and job_id are required'}),
                    'headers': {'Content-Type': 'application/json'}
                }
            
            result = self._analyze_specific_match(resume_id, job_id)
            
            return {
                'statusCode': 200,
                'body': json.dumps(result),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)}),
                'headers': {'Content-Type': 'application/json'}
            }
    
    def _find_matching_resumes(self, job_id: str, limit: int = 10, min_score: float = 50.0) -> Dict:
        """Find the best matching resumes for a given job"""
        
        if not self.opensearch_client:
            return {'error': 'OpenSearch client not available'}
        
        try:
            # Get job document
            job_response = self.opensearch_client.get(
                index=os.environ.get('JOB_INDEX_NAME', 'job_descriptions'),
                id=job_id
            )
            job_data = job_response['_source']
            
            # Search all resumes
            resume_query = {
                "query": {"match_all": {}},
                "size": 100  # Get up to 100 resumes to analyze
            }
            
            resume_response = self.opensearch_client.search(
                index=os.environ.get('RESUME_INDEX_NAME', 'resumes'),
                body=resume_query
            )
            
            # Calculate similarity scores for each resume
            matches = []
            for hit in resume_response['hits']['hits']:
                resume_data = hit['_source']
                resume_id = hit['_id']
                
                try:
                    # Calculate detailed similarity with error handling
                    similarity_result = self.matcher.calculate_similarity_score(resume_data, job_data)
                    
                    if similarity_result['overall_score'] >= min_score:
                        matches.append({
                            'resume_id': resume_id,
                            'score': similarity_result['overall_score'],
                            'component_scores': similarity_result['component_scores'],
                            'match_details': similarity_result['match_details'],
                            'recommendations': similarity_result['recommendations'],
                            'candidate_name': resume_data.get('metadata', {}).get('name', 'Unknown'),
                            'candidate_location': resume_data.get('metadata', {}).get('location', 'Unknown'),
                            'candidate_skills': resume_data.get('metadata', {}).get('skills', []),
                            'candidate_experience': resume_data.get('metadata', {}).get('total_experience_years', 0)
                        })
                except Exception as e:
                    print(f"Error calculating similarity for resume {resume_id}: {str(e)}")
                    # Skip this resume if similarity calculation fails
                    continue
            
            # Sort by score and limit results
            matches.sort(key=lambda x: x['score'], reverse=True)
            matches = matches[:limit]
            
            return {
                'job_id': job_id,
                'job_title': job_data.get('metadata', {}).get('job_title', 'Unknown'),
                'total_candidates_analyzed': len(resume_response['hits']['hits']),
                'qualified_candidates': len(matches),
                'matches': matches
            }
            
        except Exception as e:
            return {'error': f'Error finding matching resumes: {str(e)}'}
    
    def _find_matching_jobs(self, resume_id: str, limit: int = 10, min_score: float = 50.0) -> Dict:
        """Find the best matching jobs for a given resume"""
        
        if not self.opensearch_client:
            return {'error': 'OpenSearch client not available'}
        
        try:
            # Get resume document
            resume_response = self.opensearch_client.get(
                index=os.environ.get('RESUME_INDEX_NAME', 'resumes'),
                id=resume_id
            )
            resume_data = resume_response['_source']
            
            # Search all jobs
            job_query = {
                "query": {"match_all": {}},
                "size": 100  # Get up to 100 jobs to analyze
            }
            
            job_response = self.opensearch_client.search(
                index=os.environ.get('JOB_INDEX_NAME', 'job_descriptions'),
                body=job_query
            )
            
            # Calculate similarity scores for each job
            matches = []
            for hit in job_response['hits']['hits']:
                job_data = hit['_source']
                job_id = hit['_id']
                
                try:
                    # Calculate detailed similarity with error handling
                    similarity_result = self.matcher.calculate_similarity_score(resume_data, job_data)
                    
                    if similarity_result['overall_score'] >= min_score:
                        matches.append({
                            'job_id': job_id,
                            'score': similarity_result['overall_score'],
                            'component_scores': similarity_result['component_scores'],
                            'match_details': similarity_result['match_details'],
                            'recommendations': similarity_result['recommendations'],
                            'job_title': job_data.get('metadata', {}).get('job_title', 'Unknown'),
                            'company_name': job_data.get('metadata', {}).get('company_name', 'Unknown'),
                            'job_location': job_data.get('metadata', {}).get('job_location', 'Unknown'),
                            'skills_required': job_data.get('metadata', {}).get('skills_required', []),
                            'experience_level': job_data.get('metadata', {}).get('experience_level', 'Unknown')
                        })
                except Exception as e:
                    print(f"Error calculating similarity for job {job_id}: {str(e)}")
                    # Skip this job if similarity calculation fails
                    continue
            
            # Sort by score and limit results
            matches.sort(key=lambda x: x['score'], reverse=True)
            matches = matches[:limit]
            
            return {
                'resume_id': resume_id,
                'candidate_name': resume_data.get('metadata', {}).get('name', 'Unknown'),
                'total_jobs_analyzed': len(job_response['hits']['hits']),
                'matching_jobs': len(matches),
                'matches': matches
            }
            
        except Exception as e:
            return {'error': f'Error finding matching jobs: {str(e)}'}
    
    def _analyze_specific_match(self, resume_id: str, job_id: str) -> Dict:
        """Analyze detailed match between specific resume and job"""
        
        if not self.opensearch_client:
            return {'error': 'OpenSearch client not available'}
        
        try:
            # Get both documents
            resume_response = self.opensearch_client.get(index=os.environ.get('RESUME_INDEX_NAME', 'resumes'), id=resume_id)
            job_response = self.opensearch_client.get(index=os.environ.get('JOB_INDEX_NAME', 'job_descriptions'), id=job_id)
            
            resume_data = resume_response['_source']
            job_data = job_response['_source']
            
            try:
                # Calculate detailed similarity with error handling
                similarity_result = self.matcher.calculate_similarity_score(resume_data, job_data)
            except Exception as calc_error:
                print(f"Error in similarity calculation: {str(calc_error)}")
                return {
                    'error': f'Error calculating similarity: {str(calc_error)}',
                    'resume_id': resume_id,
                    'job_id': job_id
                }
            
            return {
                'resume_id': resume_id,
                'job_id': job_id,
                'candidate_name': resume_data.get('metadata', {}).get('name', 'Unknown'),
                'job_title': job_data.get('metadata', {}).get('job_title', 'Unknown'),
                'company_name': job_data.get('metadata', {}).get('company_name', 'Unknown'),
                'analysis': similarity_result,
                'detailed_comparison': {
                    'candidate_skills': resume_data.get('metadata', {}).get('skills', []),
                    'required_skills': job_data.get('metadata', {}).get('skills_required', []),
                    'candidate_experience': resume_data.get('metadata', {}).get('total_experience_years', 0),
                    'required_experience': job_data.get('metadata', {}).get('experience_level', 'Unknown'),
                    'candidate_location': resume_data.get('metadata', {}).get('location', 'Unknown'),
                    'job_location': job_data.get('metadata', {}).get('job_location', 'Unknown')
                }
            }
            
        except Exception as e:
            return {'error': f'Error analyzing specific match: {str(e)}'}

# Initialize the API instance globally for Lambda reuse
api_instance = LambdaSimilarityAPI()

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    Routes API Gateway requests to appropriate similarity search functions
    """
    
    print(f"Received event: {json.dumps(event, default=str)}")
    
    try:
        # Initialize defaults
        http_method = 'UNKNOWN'
        path = 'UNKNOWN'
        body = {}
        
        # Check if this is a direct body pass-through (non-proxy integration)
        if isinstance(event, dict) and 'resume_id' in event and 'job_id' in event:
            # API Gateway is passing the body directly for /match/detailed (both IDs present)
            http_method = 'POST'
            path = '/match/detailed'
            body = event
            print("Detected: Direct body pass-through for /match/detailed")
        
        elif isinstance(event, dict) and 'resume_id' in event:
            # API Gateway is passing the body directly for /search/jobs
            http_method = 'POST'
            path = '/search/jobs'
            body = event
            print("Detected: Direct body pass-through for /search/jobs")
        
        elif isinstance(event, dict) and 'job_id' in event:
            # API Gateway is passing the body directly for /search/resumes
            http_method = 'POST'
            path = '/search/resumes'
            body = event
            print("Detected: Direct body pass-through for /search/resumes")
        
        # Handle standard API Gateway event formats
        elif 'httpMethod' in event:
            # API Gateway REST API format
            http_method = event['httpMethod']
            path = event.get('path', '')
            
            # Parse request body
            if event.get('body'):
                if isinstance(event['body'], str):
                    body = json.loads(event['body'])
                else:
                    body = event['body']
        
        elif 'requestContext' in event and 'http' in event['requestContext']:
            # API Gateway HTTP API format
            http_method = event['requestContext']['http']['method']
            path = event['requestContext']['http']['path']
            
            # Parse request body
            if event.get('body'):
                if isinstance(event['body'], str):
                    body = json.loads(event['body'])
                else:
                    body = event['body']
        
        elif 'version' in event and event['version'] == '2.0':
            # API Gateway v2.0 format
            http_method = event.get('requestContext', {}).get('http', {}).get('method', 'UNKNOWN')
            path = event.get('rawPath', event.get('path', 'UNKNOWN'))
            
            # Parse request body
            if event.get('body'):
                if isinstance(event['body'], str):
                    body = json.loads(event['body'])
                else:
                    body = event['body']
        
        elif 'resource' in event:
            # Another API Gateway format variation
            http_method = event.get('httpMethod', 'UNKNOWN')
            path = event.get('path', 'UNKNOWN')
            
            # Parse request body
            if event.get('body'):
                if isinstance(event['body'], str):
                    body = json.loads(event['body'])
                else:
                    body = event['body']
        
        else:
            # Direct Lambda invocation or unknown format
            http_method = event.get('httpMethod', 'UNKNOWN')
            path = event.get('path', 'UNKNOWN')
            body = event.get('body', event)
            print(f"WARNING: Unrecognized event format. Event keys: {list(event.keys())}")
            print(f"Full event structure: {json.dumps(event, default=str, indent=2)}")
        
        print(f"Parsed - Method: {http_method}, Path: {path}")
        print(f"Body: {body}")
        
        # More precise routing with exact path matching
        if http_method == 'GET' and path == '/health':
            return api_instance.health_check()
        
        elif http_method == 'POST' and path == '/search/resumes':
            return api_instance.search_resumes_for_job(body)
        
        elif http_method == 'POST' and path == '/search/jobs':
            return api_instance.search_jobs_for_resume(body)
        
        elif http_method == 'POST' and path == '/match/detailed':
            return api_instance.detailed_match_analysis(body)
        
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Endpoint not found',
                    'received_method': http_method,
                    'received_path': path,
                    'event_keys': list(event.keys()),
                    'available_endpoints': [
                        'GET /health',
                        'POST /search/resumes',
                        'POST /search/jobs', 
                        'POST /match/detailed'
                    ]
                }),
                'headers': {'Content-Type': 'application/json'}
            }
    
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            }),
            'headers': {'Content-Type': 'application/json'}
        }

# Test function for local development
def test_lambda_locally():
    """Test the Lambda function locally"""
    
    print("🧪 Testing Lambda function locally...")
    
    # Test health check
    health_event = {
        'httpMethod': 'GET',
        'path': '/health'
    }
    
    health_response = lambda_handler(health_event, {})
    print("Health Check Response:", json.dumps(health_response, indent=2))
    
    # Test with sample data (requires real OpenSearch data)
    search_event = {
        'httpMethod': 'POST',
        'path': '/search/resumes',
        'body': json.dumps({
            'job_id': 'sample-job-id',
            'limit': 5,
            'min_score': 70.0
        })
    }
    
    print("\nTesting search endpoint...")
    search_response = lambda_handler(search_event, {})
    print("Search Response:", json.dumps(search_response, indent=2))

if __name__ == "__main__":
    print("🚀 Lambda Similarity Search API - Local Test")
    print("=" * 50)
    test_lambda_locally()
