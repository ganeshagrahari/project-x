#!/usr/bin/env python3
"""
Script to verify resume data stored in OpenSearch
"""

import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from aws_requests_auth.aws_auth import AWSRequestsAuth

def verify_opensearch_data():
    """
    Connect to OpenSearch and verify stored resume data
    """
    try:
        # OpenSearch endpoint (replace with your actual endpoint)
        opensearch_endpoint = "search-recruitment-search-xr3oxgazrekcvieeeogvudpf6u.aos.us-east-1.on.aws"
        
        # Get AWS credentials
        credentials = boto3.Session().get_credentials()
        awsauth = AWSRequestsAuth(
            aws_access_key=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_token=credentials.token,
            aws_region='us-east-1',
            aws_service='es',
            aws_host=opensearch_endpoint
        )
        
        # Create OpenSearch client
        client = OpenSearch(
            hosts=[{'host': opensearch_endpoint, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
        
        print("🔍 Checking OpenSearch connection...")
        
        # Check if index exists
        if client.indices.exists(index='resumes'):
            print("✅ 'resumes' index exists!")
            
            # Get index info
            index_info = client.indices.get(index='resumes')
            print(f"📊 Index info: {json.dumps(index_info, indent=2, default=str)}")
            
            # Search for all documents
            search_query = {
                "query": {
                    "match_all": {}
                }
            }
            
            response = client.search(index='resumes', body=search_query)
            
            print(f"\n📈 Total documents found: {response['hits']['total']['value']}")
            
            # Display each document
            for i, hit in enumerate(response['hits']['hits'], 1):
                print(f"\n📄 Document {i}:")
                print(f"   ID: {hit['_id']}")
                print(f"   File: {hit['_source'].get('file_name', 'Unknown')}")
                print(f"   Processed: {hit['_source'].get('processed_at', 'Unknown')}")
                
                # Display metadata if available
                metadata = hit['_source'].get('metadata', {})
                if metadata:
                    print(f"   Name: {metadata.get('name', 'Unknown')}")
                    print(f"   Email: {metadata.get('email', 'Unknown')}")
                    print(f"   Skills: {', '.join(metadata.get('skills', []))}")
                    print(f"   Experience: {metadata.get('total_experience_years', 0)} years")
                
                # Show text preview (first 200 chars)
                text_content = hit['_source'].get('text_content', '')
                if text_content:
                    preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
                    print(f"   Text Preview: {preview}")
                
                print("-" * 50)
            
        else:
            print("❌ 'resumes' index does not exist yet")
            
            # List all indices
            all_indices = client.indices.get_alias(index="*")
            print(f"📋 Available indices: {list(all_indices.keys())}")
    
    except Exception as e:
        print(f"❌ Error connecting to OpenSearch: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Verifying OpenSearch Data Storage...")
    print("=" * 60)
    
    success = verify_opensearch_data()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Verification completed successfully!")
    else:
        print("❌ Verification failed. Check the error messages above.")
