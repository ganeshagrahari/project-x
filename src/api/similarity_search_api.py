#!/usr/bin/env python3
"""
Similarity Search API for AI Recruitment System
Provides endpoints for advanced resume-job matching
"""

import os
import sys
import json
import boto3
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from matching.advanced_matcher import AdvancedMatcher

class SimilaritySearchAPI:
    def __init__(self):
        """Initialize the similarity search API"""
        self.matcher = AdvancedMatcher()
        self.opensearch_client = self._initialize_opensearch()
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _initialize_opensearch(self):
        """Initialize OpenSearch client"""
        try:
            # AWS credentials for OpenSearch
            credentials = boto3.Session().get_credentials()
            awsauth = AWS4Auth(
                credentials.access_key,
                credentials.secret_key,
                'us-east-1',
                'es',
                session_token=credentials.token
            )
            
            # OpenSearch endpoint (replace with your actual endpoint)
            opensearch_endpoint = "https://search-trujobs-opensearch-ydxvqg3ptu26pykub2shpf2r6m.us-east-1.es.amazonaws.com"
            
            client = OpenSearch(
                hosts=[{'host': opensearch_endpoint.replace('https://', ''), 'port': 443}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection
            )
            
            return client
            
        except Exception as e:
            print(f"Error initializing OpenSearch: {e}")
            return None
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'similarity-search-api',
                'opensearch_connected': self.opensearch_client is not None
            })
        
        @self.app.route('/search/resumes', methods=['POST'])
        def search_resumes_for_job():
            """Find best matching resumes for a job description"""
            try:
                data = request.get_json()
                job_id = data.get('job_id')
                limit = data.get('limit', 10)
                min_score = data.get('min_score', 50.0)
                
                if not job_id:
                    return jsonify({'error': 'job_id is required'}), 400
                
                results = self.find_matching_resumes(job_id, limit, min_score)
                return jsonify(results)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/search/jobs', methods=['POST'])
        def search_jobs_for_resume():
            """Find best matching jobs for a resume"""
            try:
                data = request.get_json()
                resume_id = data.get('resume_id')
                limit = data.get('limit', 10)
                min_score = data.get('min_score', 50.0)
                
                if not resume_id:
                    return jsonify({'error': 'resume_id is required'}), 400
                
                results = self.find_matching_jobs(resume_id, limit, min_score)
                return jsonify(results)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/match/detailed', methods=['POST'])
        def detailed_match_analysis():
            """Get detailed match analysis between specific resume and job"""
            try:
                data = request.get_json()
                resume_id = data.get('resume_id')
                job_id = data.get('job_id')
                
                if not resume_id or not job_id:
                    return jsonify({'error': 'Both resume_id and job_id are required'}), 400
                
                result = self.analyze_specific_match(resume_id, job_id)
                return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/search/bulk', methods=['POST'])
        def bulk_similarity_search():
            """Perform bulk similarity matching"""
            try:
                data = request.get_json()
                search_type = data.get('type')  # 'job_to_resumes' or 'resume_to_jobs'
                ids = data.get('ids', [])
                limit_per_id = data.get('limit_per_id', 5)
                min_score = data.get('min_score', 50.0)
                
                if not search_type or not ids:
                    return jsonify({'error': 'type and ids are required'}), 400
                
                results = self.bulk_similarity_search(search_type, ids, limit_per_id, min_score)
                return jsonify(results)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
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
            
            # Search all resumes
            resume_query = {
                "query": {"match_all": {}},
                "size": 100  # Get up to 100 resumes to analyze
            }
            
            resume_response = self.opensearch_client.search(
                index='resumes',
                body=resume_query
            )
            
            # Calculate similarity scores for each resume
            matches = []
            for hit in resume_response['hits']['hits']:
                resume_data = hit['_source']
                resume_id = hit['_id']
                
                # Calculate detailed similarity
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
                "size": 100  # Get up to 100 jobs to analyze
            }
            
            job_response = self.opensearch_client.search(
                index='job-descriptions',
                body=job_query
            )
            
            # Calculate similarity scores for each job
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
                        'job_title': job_data.get('metadata', {}).get('job_title', 'Unknown'),
                        'company_name': job_data.get('metadata', {}).get('company_name', 'Unknown'),
                        'job_location': job_data.get('metadata', {}).get('job_location', 'Unknown'),
                        'skills_required': job_data.get('metadata', {}).get('skills_required', []),
                        'experience_level': job_data.get('metadata', {}).get('experience_level', 'Unknown')
                    })
            
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
    
    def analyze_specific_match(self, resume_id: str, job_id: str) -> Dict:
        """Analyze detailed match between specific resume and job"""
        
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
    
    def bulk_similarity_search(self, search_type: str, ids: List[str], limit_per_id: int = 5, min_score: float = 50.0) -> Dict:
        """Perform bulk similarity matching"""
        
        results = []
        
        for id_item in ids:
            try:
                if search_type == 'job_to_resumes':
                    result = self.find_matching_resumes(id_item, limit_per_id, min_score)
                elif search_type == 'resume_to_jobs':
                    result = self.find_matching_jobs(id_item, limit_per_id, min_score)
                else:
                    result = {'error': 'Invalid search type'}
                
                results.append({
                    'id': id_item,
                    'result': result
                })
                
            except Exception as e:
                results.append({
                    'id': id_item,
                    'error': str(e)
                })
        
        return {
            'search_type': search_type,
            'total_processed': len(ids),
            'results': results
        }
    
    def run(self, host='127.0.0.1', port=5000, debug=True):
        """Run the Flask application"""
        print(f"🚀 Starting Similarity Search API on {host}:{port}")
        print("🔍 Available endpoints:")
        print("  POST /search/resumes - Find matching resumes for a job")
        print("  POST /search/jobs - Find matching jobs for a resume") 
        print("  POST /match/detailed - Detailed match analysis")
        print("  POST /search/bulk - Bulk similarity search")
        print("  GET /health - Health check")
        
        self.app.run(host=host, port=port, debug=debug)

# Local testing functions
def test_api_locally():
    """Test the API with local mock data"""
    print("🧪 Testing Similarity Search API locally...")
    
    api = SimilaritySearchAPI()
    
    # Test the matcher directly (without OpenSearch for local testing)
    sample_resume = {
        "metadata": {
            "name": "Alice Johnson",
            "skills": ["Python", "Django", "AWS", "PostgreSQL", "Docker"],
            "total_experience_years": 4,
            "location": "Bangalore, India",
            "experience": [
                {"company": "TechCorp", "position": "Python Developer", "duration": "2020-2024"}
            ],
            "education": [
                {"degree": "Bachelor's in Computer Science", "institution": "IISC Bangalore"}
            ]
        },
        "embeddings": [0.1] * 1536
    }
    
    sample_job = {
        "metadata": {
            "job_title": "Senior Python Developer", 
            "company_name": "InnovateTech",
            "job_location": "Bangalore, India",
            "skills_required": ["Python", "Django", "AWS", "SQL"],
            "experience_level": "Senior (4-6 years)",
            "job_requirements": ["Bachelor's degree", "4+ years Python experience"]
        },
        "embeddings": [0.12] * 1536
    }
    
    # Test the matching
    result = api.matcher.calculate_similarity_score(sample_resume, sample_job)
    
    print("✅ Local API Test Results:")
    print(f"Overall Score: {result['overall_score']}/100")
    print("Component Scores:", result['component_scores'])
    
    return result

if __name__ == "__main__":
    print("🎯 Advanced Similarity Search API")
    print("=" * 50)
    
    # Test locally first
    test_result = test_api_locally()
    
    print("\n🚀 Starting API server...")
    
    # Initialize and run the API
    api = SimilaritySearchAPI()
    api.run(host='0.0.0.0', port=5001, debug=True)
