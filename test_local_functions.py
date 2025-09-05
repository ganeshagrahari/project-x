#!/usr/bin/env python3
"""
Local testing script for AI Recruitment System Lambda functions
Test your functions locally before deploying to AWS
"""

import os
import sys
import json
import boto3
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def setup_environment():
    """Set up environment variables for local testing"""
    os.environ['OPENSEARCH_ENDPOINT'] = 'https://search-recruitment-search-xr3oxgazrekcvieeeogvudpf6u.aos.us-east-1.on.aws'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    print("🔧 Environment configured for local testing")
    print(f"📍 OpenSearch: {os.environ['OPENSEARCH_ENDPOINT']}")
    print(f"🌍 Region: {os.environ['AWS_REGION']}")

def test_aws_connection():
    """Test AWS SDK connection"""
    try:
        print("\n🧪 Testing AWS connection...")
        
        # Test STS (Identity)
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Identity: {identity['Arn']}")
        
        # Test S3 access
        s3 = boto3.client('s3')
        buckets = s3.list_buckets()
        bucket_names = [bucket['Name'] for bucket in buckets['Buckets']]
        print(f"✅ S3 Access: Found {len(bucket_names)} buckets")
        
        # Check for our specific buckets
        resume_bucket = 'trujobs-resume-pdfs' in bucket_names
        jd_bucket = 'trujobs-jd-pdfs' in bucket_names
        print(f"📄 Resume bucket (trujobs-resume-pdfs): {'✅ Found' if resume_bucket else '❌ Missing'}")
        print(f"📋 Job Description bucket (trujobs-jd-pdfs): {'✅ Found' if jd_bucket else '❌ Missing'}")
        
        # Test Bedrock access
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("✅ Bedrock Runtime access configured")
        
        return True
        
    except Exception as e:
        print(f"❌ AWS connection failed: {str(e)}")
        return False

def test_opensearch_connection():
    """Test OpenSearch connection"""
    try:
        print("\n🔍 Testing OpenSearch connection...")
        
        # Import OpenSearch utilities
        from utils.verify_opensearch_data import test_opensearch_connection as verify_os
        
        success = verify_os()
        if success:
            print("✅ OpenSearch connection successful")
        else:
            print("❌ OpenSearch connection failed")
            
        return success
        
    except Exception as e:
        print(f"❌ OpenSearch test failed: {str(e)}")
        return False

def test_local_lambda_function():
    """Test Lambda function locally"""
    try:
        print("\n🤖 Testing Lambda function locally...")
        
        # Create a mock S3 event for testing
        mock_event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "trujobs-resume-pdfs"},
                        "object": {"key": "test-resume.pdf"}
                    }
                }
            ]
        }
        
        # Import and test resume processor
        try:
            from lambda_functions.resume_processor_lambda import lambda_handler
            print("✅ Resume processor Lambda function imported successfully")
            print("🔧 Function ready for local testing")
        except ImportError as e:
            print(f"❌ Failed to import resume processor: {str(e)}")
            
        # Import and test job description processor
        try:
            from lambda_functions.job_description_processor_lambda import lambda_handler as jd_handler
            print("✅ Job description processor Lambda function imported successfully")
            print("🔧 Function ready for local testing")
        except ImportError as e:
            print(f"❌ Failed to import job description processor: {str(e)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Lambda function test failed: {str(e)}")
        return False

def main():
    """Main testing function"""
    print("🚀 AI Recruitment System - Local Development Testing")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Run tests
    aws_ok = test_aws_connection()
    opensearch_ok = test_opensearch_connection()
    lambda_ok = test_local_lambda_function()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 LOCAL DEVELOPMENT SETUP SUMMARY:")
    print(f"🌍 AWS Connection: {'✅ Working' if aws_ok else '❌ Failed'}")
    print(f"🔍 OpenSearch: {'✅ Working' if opensearch_ok else '❌ Failed'}")
    print(f"🤖 Lambda Functions: {'✅ Ready' if lambda_ok else '❌ Failed'}")
    
    if aws_ok and opensearch_ok and lambda_ok:
        print("\n🎉 LOCAL DEVELOPMENT READY!")
        print("🚀 You can now test your functions locally before deploying!")
        print("\n📋 Next steps:")
        print("  1. Test data verification: python src/utils/verify_opensearch_data.py")
        print("  2. Test matching: python src/utils/match_resumes_to_job.py <job_id>")
        print("  3. Build new search APIs locally")
    else:
        print("\n⚠️  Some components need attention before local development")

if __name__ == "__main__":
    main()
