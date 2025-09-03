import json
import boto3
import logging
import os
from urllib.parse import unquote_plus
import uuid
from datetime import datetime
import io

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='ap-south-1')
opensearch_client = boto3.client('opensearch', region_name='ap-south-1')

def lambda_handler(event, context):
    """
    Main Lambda handler function that processes job description files uploaded to S3
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Process each S3 record in the event
        for record in event['Records']:
            # Extract S3 bucket and object information
            bucket_name = record['s3']['bucket']['name']
            object_key = unquote_plus(record['s3']['object']['key'])
            
            logger.info(f"Processing file: {object_key} from bucket: {bucket_name}")
            
            # Process job description - we assume all files in this bucket are job descriptions
            # Process based on file type
            if object_key.lower().endswith('.pdf'):
                result = process_jd_pdf(bucket_name, object_key)
            elif object_key.lower().endswith('.txt') or object_key.lower().endswith('.json'):
                result = process_jd_text(bucket_name, object_key)
            else:
                logger.warning(f"Skipping unsupported file type: {object_key}")
                continue
            
            if result['success']:
                logger.info(f"Successfully processed job description: {object_key}")
            else:
                logger.error(f"Failed to process job description: {object_key}. Error: {result['error']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Job description processing completed',
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

def process_jd_pdf(bucket_name, object_key):
    """
    Process a job description PDF file
    """
    try:
        # Step 1: Download PDF from S3
        logger.info(f"Downloading PDF: {object_key}")
        pdf_content = download_file_from_s3(bucket_name, object_key)
        
        # Step 2: Extract text from PDF
        logger.info(f"Extracting text from PDF: {object_key}")
        extracted_text = extract_text_from_pdf(pdf_content)
        
        if not extracted_text.strip():
            return {
                'success': False,
                'error': 'No text could be extracted from PDF'
            }
        
        # Continue with the text processing
        return process_jd_content(object_key, extracted_text)
        
    except Exception as e:
        logger.error(f"Error processing job description PDF {object_key}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def process_jd_text(bucket_name, object_key):
    """
    Process a job description text file
    """
    try:
        # Download text file from S3
        logger.info(f"Downloading text file: {object_key}")
        file_content = download_file_from_s3(bucket_name, object_key)
        
        # Read the content
        text_content = file_content.decode('utf-8')
        
        # Check if it's JSON format
        if object_key.lower().endswith('.json'):
            try:
                json_data = json.loads(text_content)
                # If JSON contains 'text' field, use that
                if 'text' in json_data:
                    text_content = json_data['text']
                    provided_metadata = json_data.get('metadata', {})
                    # Process with provided metadata
                    return process_jd_content(object_key, text_content, provided_metadata)
            except json.JSONDecodeError:
                logger.warning(f"File {object_key} has .json extension but is not valid JSON. Processing as text.")
        
        # Process as plain text
        return process_jd_content(object_key, text_content)
        
    except Exception as e:
        logger.error(f"Error processing job description text {object_key}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def process_jd_content(object_key, text_content, provided_metadata=None):
    """
    Process the extracted job description content
    """
    try:
        # Step 1: Extract structured metadata using Claude 3 Haiku
        logger.info(f"Extracting metadata using Bedrock: {object_key}")
        
        if provided_metadata:
            # Use provided metadata but fill missing fields with Bedrock extraction
            metadata = provided_metadata.copy()
            
            # Fill in missing fields if needed
            if not metadata.get('job_title') or not metadata.get('job_requirements') or not metadata.get('job_location'):
                extracted_metadata = extract_jd_metadata_with_bedrock(text_content)
                
                # Fill in only the missing fields
                if not metadata.get('job_title'):
                    metadata['job_title'] = extracted_metadata.get('job_title', 'Unknown')
                if not metadata.get('job_requirements'):
                    metadata['job_requirements'] = extracted_metadata.get('job_requirements', [])
                if not metadata.get('job_location'):
                    metadata['job_location'] = extracted_metadata.get('job_location', '')
        else:
            # Extract all metadata from text using Bedrock
            metadata = extract_jd_metadata_with_bedrock(text_content)
        
        # Step 2: Generate embeddings using Titan
        logger.info(f"Generating embeddings: {object_key}")
        embeddings = generate_embeddings_with_titan(text_content)
        
        # Step 3: Store in OpenSearch
        logger.info(f"Storing in OpenSearch: {object_key}")
        opensearch_result = store_in_opensearch(
            object_key, 
            text_content, 
            metadata, 
            embeddings,
            'job_description'
        )
        
        return {
            'success': True,
            'metadata': metadata,
            'opensearch_id': opensearch_result.get('_id')
        }
        
    except Exception as e:
        logger.error(f"Error processing job description content: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def download_file_from_s3(bucket_name, object_key):
    """
    Download file from S3 bucket
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return response['Body'].read()
    except Exception as e:
        logger.error(f"Error downloading file from S3: {str(e)}")
        raise

def extract_text_from_pdf(pdf_content):
    """
    Extract text content from PDF using PyPDF2
    """
    try:
        import PyPDF2
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

def extract_jd_metadata_with_bedrock(text):
    """
    Use Amazon Bedrock Claude 3 Haiku to extract structured metadata from job description text
    """
    try:
        # Prepare the prompt for Claude
        prompt = f"""
        Please analyze the following job description text and extract structured information in JSON format.
        Return only valid JSON without any additional text or explanation.

        Extract the following information:
        - job_title: The title of the job position
        - company_name: Name of the company
        - job_location: Location(s) where the job is based (city, state, country, or remote)
        - employment_type: Full-time, part-time, contract, etc.
        - experience_level: Required years of experience or level (entry, mid, senior)
        - job_description: Brief summary of the job role (2-3 sentences)
        - job_requirements: Array of key requirements and qualifications
        - skills_required: Array of technical or soft skills required
        - salary_range: Salary information if provided
        - application_deadline: Application deadline if mentioned

        Job description text:
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
                "job_title": "Unknown",
                "company_name": "",
                "job_location": "",
                "employment_type": "",
                "experience_level": "",
                "job_description": text[:200] + "...",
                "job_requirements": [],
                "skills_required": [],
                "salary_range": "",
                "application_deadline": ""
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

def store_in_opensearch(object_key, text, metadata, embeddings, document_type='job_description'):
    """
    Store the processed job description data in OpenSearch
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
            aws_region='ap-south-1',
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
            'document_type': document_type
        }
        
        # Index the document
        index_name = 'job_descriptions'
        doc_id = str(uuid.uuid4())
        
        # Create index if it doesn't exist
        if not opensearch_data_client.indices.exists(index=index_name):
            index_body = {
                'settings': {
                    'index': {
                        'number_of_shards': 1,
                        'number_of_replicas': 1
                    }
                },
                'mappings': {
                    'properties': {
                        'file_name': {'type': 'keyword'},
                        'text_content': {'type': 'text'},
                        'metadata': {'type': 'object'},
                        'embeddings': {'type': 'knn_vector', 'dimension': 1536},
                        'processed_at': {'type': 'date'},
                        'document_type': {'type': 'keyword'}
                    }
                }
            }
            opensearch_data_client.indices.create(index=index_name, body=index_body)
            logger.info(f"Created new OpenSearch index: {index_name}")
        
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
