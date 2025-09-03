import json
import boto3
import logging
import os
from urllib.parse import unquote_plus
import uuid
from datetime import datetime
import PyPDF2
import io

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
opensearch_client = boto3.client('opensearch', region_name='us-east-1')

def lambda_handler(event, context):
    """
    Main Lambda handler function that processes resume PDFs uploaded to S3
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Process each S3 record in the event
        for record in event['Records']:
            # Extract S3 bucket and object information
            bucket_name = record['s3']['bucket']['name']
            object_key = unquote_plus(record['s3']['object']['key'])
            
            logger.info(f"Processing file: {object_key} from bucket: {bucket_name}")
            
            # Skip if not a PDF file
            if not object_key.lower().endswith('.pdf'):
                logger.warning(f"Skipping non-PDF file: {object_key}")
                continue
            
            # Process the resume PDF
            result = process_resume_pdf(bucket_name, object_key)
            
            if result['success']:
                logger.info(f"Successfully processed resume: {object_key}")
            else:
                logger.error(f"Failed to process resume: {object_key}. Error: {result['error']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Resume processing completed',
                'processed_files': len(event['Records'])
            })
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def process_resume_pdf(bucket_name, object_key):
    """
    Process a single resume PDF file
    """
    try:
        # Step 1: Download PDF from S3
        logger.info(f"Downloading PDF: {object_key}")
        pdf_content = download_pdf_from_s3(bucket_name, object_key)
        
        # Step 2: Extract text from PDF
        logger.info(f"Extracting text from PDF: {object_key}")
        extracted_text = extract_text_from_pdf(pdf_content)
        
        if not extracted_text.strip():
            return {
                'success': False,
                'error': 'No text could be extracted from PDF'
            }
        
        # Step 3: Extract structured metadata using Claude 3 Haiku
        logger.info(f"Extracting metadata using Bedrock: {object_key}")
        metadata = extract_metadata_with_bedrock(extracted_text)
        
        # Step 4: Generate embeddings using Titan
        logger.info(f"Generating embeddings: {object_key}")
        embeddings = generate_embeddings_with_titan(extracted_text)
        
        # Step 5: Store in OpenSearch
        logger.info(f"Storing in OpenSearch: {object_key}")
        opensearch_result = store_in_opensearch(
            object_key, 
            extracted_text, 
            metadata, 
            embeddings
        )
        
        return {
            'success': True,
            'metadata': metadata,
            'opensearch_id': opensearch_result.get('_id')
        }
        
    except Exception as e:
        logger.error(f"Error processing resume {object_key}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def download_pdf_from_s3(bucket_name, object_key):
    """
    Download PDF file from S3 bucket
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return response['Body'].read()
    except Exception as e:
        logger.error(f"Error downloading PDF from S3: {str(e)}")
        raise

def extract_text_from_pdf(pdf_content):
    """
    Extract text content from PDF using PyPDF2
    """
    try:
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise

def extract_metadata_with_bedrock(text):
    """
    Use Amazon Bedrock Claude 3 Haiku to extract structured metadata from resume text
    """
    try:
        # Prepare the prompt for Claude
        prompt = f"""
        Please analyze the following resume text and extract structured information in JSON format.
        Return only valid JSON without any additional text or explanation.

        Extract the following information:
        - name: Full name of the candidate
        - email: Email address
        - phone: Phone number
        - location: Current location/address
        - summary: Brief professional summary (2-3 sentences)
        - skills: Array of technical skills
        - experience: Array of work experience objects with company, position, duration, description
        - education: Array of education objects with degree, institution, year
        - total_experience_years: Estimated total years of experience

        Resume text:
        {text}

        JSON:
        """

        # Call Claude 3 Haiku model
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })

        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=body,
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        claude_response = response_body['content'][0]['text']
        
        # Parse the JSON response from Claude
        try:
            metadata = json.loads(claude_response)
            return metadata
        except json.JSONDecodeError:
            # If Claude didn't return valid JSON, create a basic structure
            logger.warning("Claude didn't return valid JSON, creating basic metadata")
            return {
                "name": "Unknown",
                "email": "",
                "phone": "",
                "location": "",
                "summary": text[:200] + "...",
                "skills": [],
                "experience": [],
                "education": [],
                "total_experience_years": 0
            }
        
    except Exception as e:
        logger.error(f"Error extracting metadata with Bedrock: {str(e)}")
        raise

def generate_embeddings_with_titan(text):
    """
    Generate vector embeddings using Amazon Titan Embeddings model
    """
    try:
        model_id = "amazon.titan-embed-text-v1"
        
        # Truncate text if too long (Titan has input limits)
        max_chars = 8000
        if len(text) > max_chars:
            text = text[:max_chars]
        
        body = json.dumps({
            "inputText": text
        })
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=body,
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        embeddings = response_body['embedding']
        
        return embeddings
        
    except Exception as e:
        logger.error(f"Error generating embeddings with Titan: {str(e)}")
        raise

def store_in_opensearch(object_key, text, metadata, embeddings):
    """
    Store the processed resume data in OpenSearch
    """
    try:
        # Get OpenSearch endpoint from environment variables
        opensearch_endpoint = os.environ.get('OPENSEARCH_ENDPOINT')
        if not opensearch_endpoint:
            raise ValueError("OPENSEARCH_ENDPOINT environment variable not set")
        
        # Create OpenSearch client for data operations
        from opensearchpy import OpenSearch, RequestsHttpConnection
        from aws_requests_auth.aws_auth import AWSRequestsAuth
        
        # Get AWS credentials for OpenSearch authentication
        credentials = boto3.Session().get_credentials()
        awsauth = AWSRequestsAuth(
            aws_access_key=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_token=credentials.token,
            aws_region='us-east-1',
            aws_service='es',
            aws_host=opensearch_endpoint
        )
        
        opensearch_data_client = OpenSearch(
            hosts=[{'host': opensearch_endpoint.replace('https://', ''), 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
        
        # Prepare document for indexing
        document = {
            'file_name': object_key,
            'text_content': text,
            'metadata': metadata,
            'embeddings': embeddings,
            'processed_at': datetime.utcnow().isoformat(),
            'document_type': 'resume'
        }
        
        # Index the document
        index_name = 'resumes'
        doc_id = str(uuid.uuid4())
        
        response = opensearch_data_client.index(
            index=index_name,
            id=doc_id,
            body=document
        )
        
        logger.info(f"Successfully stored document in OpenSearch: {doc_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error storing in OpenSearch: {str(e)}")
        raise

# Optional: Health check function for testing
def health_check():
    """
    Simple health check function to test Lambda connectivity
    """
    try:
        # Test S3 connectivity
        s3_client.list_buckets()
        
        # Test Bedrock connectivity
        bedrock_runtime.list_foundation_models()
        
        return {
            'status': 'healthy',
            'services': {
                's3': 'connected',
                'bedrock': 'connected'
            }
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }
