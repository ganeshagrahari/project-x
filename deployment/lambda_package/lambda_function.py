#!/usr/bin/env python3
"""
AWS Lambda Function for Similarity Search API
Serverless deployment of the advanced matching system
"""

import json
import boto3
import os
import sys
from typing import Dict, List, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Import our matching engine (will be included in deployment package)
from advanced_matcher import AdvancedMatcher

class LambdaSimilarityAPI:
    def __init__(self):
        """Initialize the Lambda-based similarity API"""
        self.matcher = AdvancedMatcher()
        self.opensearch_client = self._initialize_opensearch()
    
    def _initialize_opensearch(self):
        """Initialize OpenSearch client for Lambda"""
        try:
            # Get AWS credentials from Lambda environment
            credentials = boto3.Session().get_credentials()
            awsauth = AWS4Auth(
                credentials.access_key,
                credentials.secret_key,
                'us-east-1',
                'es',
                session_token=credentials.token
            )
            
            # Your OpenSearch endpoint
            opensearch_endpoint = "search-trujobs-opensearch-ydxvqg3ptu26pykub2shpf2r6m.us-east-1.es.amazonaws.com"
            
            client = OpenSearch(
                hosts=[{'host': opensearch_endpoint, 'port': 443}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                timeout=30
            )
            
            return client
            
        except Exception as e:
            print(f"Error initializing OpenSearch: {e}")
            return None

    def find_matching_resumes(self, job_id: str, limit: int = 10, min_score: float = 50.0) -> Dict:
        """Find the best matching resumes for a given job"""
        
        if not self.opensearch_client:
            return {'error': 'OpenSearch client not available'}
        
        try:
            # Get job document
            job_response = self.opensearch_client.get(
                index='job-descriptions',
                id=job_id
            )
            job_data = job_response['_source']
            
            # Search all resumes with pagination
            resume_query = {
                "query": {"match_all": {}},
                "size": 100  # Process in batches
            }
            
            resume_response = self.opensearch_client.search(
                index='resumes',
                body=resume_query
            )
            
            # Calculate similarity scores
            matches = []
            for hit in resume_response['hits']['hits']:
                resume_data = hit['_source']
                resume_id = hit['_id']
                
                # Calculate detailed similarity using our advanced engine
                similarity_result = self.matcher.calculate_similarity_score(resume_data, job_data)
                
                if similarity_result['overall_score'] >= min_score:
                    matches.append({
                        'resume_id': resume_id,
                        'score': similarity_result['overall_score'],
                        'component_scores': similarity_result['component_scores'],
                        'match_details': similarity_result['match_details'],
                        'recommendations': similarity_result['recommendations'],
                        'candidate_info': {
                            'name': resume_data.get('metadata', {}).get('name', 'Unknown'),
                            'location': resume_data.get('metadata', {}).get('location', 'Unknown'),
                            'skills': resume_data.get('metadata', {}).get('skills', []),
                            'experience_years': resume_data.get('metadata', {}).get('total_experience_years', 0),
                            'education': resume_data.get('metadata', {}).get('education', [])
                        }
                    })
            
            # Sort by score and limit results
            matches.sort(key=lambda x: x['score'], reverse=True)
            matches = matches[:limit]
            
            return {
                'success': True,
                'job_id': job_id,
                'job_info': {
                    'title': job_data.get('metadata', {}).get('job_title', 'Unknown'),
                    'company': job_data.get('metadata', {}).get('company_name', 'Unknown'),
                    'location': job_data.get('metadata', {}).get('job_location', 'Unknown'),
                    'skills_required': job_data.get('metadata', {}).get('skills_required', [])
                },
                'total_candidates_analyzed': len(resume_response['hits']['hits']),
                'qualified_candidates': len(matches),
                'matches': matches
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error finding matching resumes: {str(e)}'
            }

    def find_matching_jobs(self, resume_id: str, limit: int = 10, min_score: float = 50.0) -> Dict:
        """Find the best matching jobs for a given resume"""
        
        if not self.opensearch_client:
            return {'error': 'OpenSearch client not available'}
        
        try:
            # Get resume document
            resume_response = self.opensearch_client.get(
                index='resumes',
                id=resume_id
            )
            resume_data = resume_response['_source']
            
            # Search all jobs
            job_query = {
                "query": {"match_all": {}},
                "size": 100
            }
            
            job_response = self.opensearch_client.search(
                index='job-descriptions',
                body=job_query
            )
            
            # Calculate similarity scores
            matches = []
            for hit in job_response['hits']['hits']:
                job_data = hit['_source']
                job_id = hit['_id']
                
                # Calculate detailed similarity
                similarity_result = self.matcher.calculate_similarity_score(resume_data, job_data)
                
                if similarity_result['overall_score'] >= min_score:
                    matches.append({
                        'job_id': job_id,
                        'score': similarity_result['overall_score'],
                        'component_scores': similarity_result['component_scores'],
                        'match_details': similarity_result['match_details'],
                        'recommendations': similarity_result['recommendations'],
                        'job_info': {
                            'title': job_data.get('metadata', {}).get('job_title', 'Unknown'),
                            'company': job_data.get('metadata', {}).get('company_name', 'Unknown'),
                            'location': job_data.get('metadata', {}).get('job_location', 'Unknown'),
                            'skills_required': job_data.get('metadata', {}).get('skills_required', []),
                            'experience_level': job_data.get('metadata', {}).get('experience_level', 'Unknown'),
                            'salary_range': job_data.get('metadata', {}).get('salary_range', 'Not specified')
                        }
                    })
            
            # Sort by score and limit results
            matches.sort(key=lambda x: x['score'], reverse=True)
            matches = matches[:limit]
            
            return {
                'success': True,
                'resume_id': resume_id,
                'candidate_info': {
                    'name': resume_data.get('metadata', {}).get('name', 'Unknown'),
                    'location': resume_data.get('metadata', {}).get('location', 'Unknown'),
                    'skills': resume_data.get('metadata', {}).get('skills', []),
                    'experience_years': resume_data.get('metadata', {}).get('total_experience_years', 0)
                },
                'total_jobs_analyzed': len(job_response['hits']['hits']),
                'matching_jobs': len(matches),
                'matches': matches
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error finding matching jobs: {str(e)}'
            }

    def analyze_specific_match(self, resume_id: str, job_id: str) -> Dict:
        """Detailed analysis between specific resume and job"""
        
        if not self.opensearch_client:
            return {'error': 'OpenSearch client not available'}
        
        try:
            # Get both documents
            resume_response = self.opensearch_client.get(index='resumes', id=resume_id)
            job_response = self.opensearch_client.get(index='job-descriptions', id=job_id)
            
            resume_data = resume_response['_source']
            job_data = job_response['_source']
            
            # Calculate detailed similarity
            similarity_result = self.matcher.calculate_similarity_score(resume_data, job_data)
            
            return {
                'success': True,
                'resume_id': resume_id,
                'job_id': job_id,
                'candidate_info': {
                    'name': resume_data.get('metadata', {}).get('name', 'Unknown'),
                    'skills': resume_data.get('metadata', {}).get('skills', []),
                    'experience_years': resume_data.get('metadata', {}).get('total_experience_years', 0),
                    'location': resume_data.get('metadata', {}).get('location', 'Unknown'),
                    'education': resume_data.get('metadata', {}).get('education', [])
                },
                'job_info': {
                    'title': job_data.get('metadata', {}).get('job_title', 'Unknown'),
                    'company': job_data.get('metadata', {}).get('company_name', 'Unknown'),
                    'location': job_data.get('metadata', {}).get('job_location', 'Unknown'),
                    'skills_required': job_data.get('metadata', {}).get('skills_required', []),
                    'experience_level': job_data.get('metadata', {}).get('experience_level', 'Unknown')
                },
                'similarity_analysis': similarity_result,
                'compatibility_summary': self._generate_compatibility_summary(similarity_result)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error analyzing specific match: {str(e)}'
            }

    def _generate_compatibility_summary(self, similarity_result: Dict) -> Dict:
        """Generate a human-readable compatibility summary"""
        
        overall_score = similarity_result['overall_score']
        
        if overall_score >= 90:
            compatibility = "Excellent Match"
            recommendation = "Strongly recommend this candidate/job"
        elif overall_score >= 80:
            compatibility = "Very Good Match"
            recommendation = "Good candidate/job with high potential"
        elif overall_score >= 70:
            compatibility = "Good Match"
            recommendation = "Suitable candidate/job worth considering"
        elif overall_score >= 60:
            compatibility = "Fair Match"
            recommendation = "Potential fit with some development needed"
        elif overall_score >= 50:
            compatibility = "Partial Match"
            recommendation = "Limited fit, consider other options first"
        else:
            compatibility = "Poor Match"
            recommendation = "Not recommended for this position"
        
        return {
            'compatibility_level': compatibility,
            'recommendation': recommendation,
            'key_strengths': self._identify_strengths(similarity_result['component_scores']),
            'areas_for_improvement': self._identify_weaknesses(similarity_result['component_scores'])
        }

    def _identify_strengths(self, component_scores: Dict) -> List[str]:
        """Identify the strongest match areas"""
        strengths = []
        
        for component, score in component_scores.items():
            if score >= 80:
                component_name = component.replace('_score', '').replace('_', ' ').title()
                strengths.append(f"Strong {component_name} alignment ({score:.1f}%)")
        
        return strengths[:3]  # Top 3 strengths

    def _identify_weaknesses(self, component_scores: Dict) -> List[str]:
        """Identify areas that need improvement"""
        weaknesses = []
        
        for component, score in component_scores.items():
            if score < 60:
                component_name = component.replace('_score', '').replace('_', ' ').title()
                weaknesses.append(f"{component_name} needs development ({score:.1f}%)")
        
        return weaknesses[:3]  # Top 3 areas for improvement


# Lambda handler function
def lambda_handler(event, context):
    """
    AWS Lambda handler for similarity search API
    
    Expected event structure:
    {
        "action": "search_resumes|search_jobs|detailed_match",
        "job_id": "job-123",  # for search_resumes
        "resume_id": "resume-456",  # for search_jobs or detailed_match
        "limit": 10,  # optional
        "min_score": 60.0  # optional
    }
    """
    
    try:
        # Initialize the API
        api = LambdaSimilarityAPI()
        
        # Parse the action
        action = event.get('action')
        
        if not action:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: action',
                    'valid_actions': ['search_resumes', 'search_jobs', 'detailed_match']
                })
            }
        
        # Handle different actions
        if action == 'search_resumes':
            job_id = event.get('job_id')
            if not job_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing required parameter: job_id'})
                }
            
            limit = event.get('limit', 10)
            min_score = event.get('min_score', 50.0)
            
            result = api.find_matching_resumes(job_id, limit, min_score)
            
        elif action == 'search_jobs':
            resume_id = event.get('resume_id')
            if not resume_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing required parameter: resume_id'})
                }
            
            limit = event.get('limit', 10)
            min_score = event.get('min_score', 50.0)
            
            result = api.find_matching_jobs(resume_id, limit, min_score)
            
        elif action == 'detailed_match':
            resume_id = event.get('resume_id')
            job_id = event.get('job_id')
            
            if not resume_id or not job_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing required parameters: resume_id and job_id'})
                }
            
            result = api.analyze_specific_match(resume_id, job_id)
            
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Invalid action: {action}',
                    'valid_actions': ['search_resumes', 'search_jobs', 'detailed_match']
                })
            }
        
        # Return successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # Enable CORS
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps(result, indent=2)
        }
        
    except Exception as e:
        # Handle errors gracefully
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}',
                'success': False
            })
        }


# Test function for local development
if __name__ == "__main__":
    print("🧪 Testing Lambda Similarity API locally...")
    
    # Test event
    test_event = {
        "action": "search_resumes",
        "job_id": "test-job-id",
        "limit": 5,
        "min_score": 60.0
    }
    
    # Mock context
    class MockContext:
        def __init__(self):
            self.function_name = "similarity-search-api"
            self.memory_limit_in_mb = 512
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:similarity-search-api"
    
    context = MockContext()
    
    # Test the handler
    response = lambda_handler(test_event, context)
    
    print("📋 Test Response:")
    print(json.dumps(response, indent=2))
    
    print("\n✅ Lambda function is ready for deployment!")
