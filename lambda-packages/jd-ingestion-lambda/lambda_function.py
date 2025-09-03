import json
import logging
import uuid
import time
import os
from datetime import datetime

# Import custom modules
from config import Config
from input_parser import determine_input_type, parse_json_input, parse_multipart_form
from storage_service import save_text_to_s3, save_pdf_to_s3, extract_text_from_pdf
from ai_service import get_metadata_from_bedrock, get_embedding
from search_service import get_opensearch_client, check_and_create_opensearch_index, index_document
from utils import time_function, success_response, error_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# All functions have been moved to respective modules

def lambda_handler(event, context):
    total_start_time = time.time()
    try:
        logger.info("Starting lambda_handler")
        logger.info(f"Event headers: {json.dumps(event.get('headers', {}), default=str)}")
        
        # Validate configuration
        Config.validate()
        
        # Determine input type
        input_type = determine_input_type(event)
        logger.info(f"Detected input type: {input_type}")
        
        # Parse input based on type
        if input_type == 'json':
            parsed_data = parse_json_input(event)
            text = parsed_data['text']
            provided_metadata = parsed_data['metadata']
            filename = None
            s3_key = None
            
            # Generate a unique ID for the job description
            job_description_id = str(uuid.uuid4())
            
            # Save text content to S3 as a text file
            text_filename = f"{job_description_id}.txt"
            s3_key = save_text_to_s3(text, text_filename)
            logger.info(f"Saved text content to S3: {s3_key}")
            
        else:  # multipart
            # Parse the multipart form data
            pdf_content = parse_multipart_form(event)
            
            # Generate a unique ID for the job description
            job_description_id = str(uuid.uuid4())
            filename = f"{job_description_id}.pdf"
            
            # Save PDF to S3
            s3_key = save_pdf_to_s3(pdf_content, filename)
            logger.info(f"Saved PDF to S3: {s3_key}")
            
            # Extract text from PDF
            text = extract_text_from_pdf(pdf_content)
            logger.info("Successfully extracted text from PDF")
            provided_metadata = None
        
        # Initialize OpenSearch client
        opensearch = get_opensearch_client()
        check_and_create_opensearch_index(opensearch)
        
        # Get metadata - use provided metadata for JSON input or extract for PDF
        if input_type == 'json' and provided_metadata:
            # Use provided metadata, but still extract if fields are missing
            metadata = provided_metadata.copy()
            
            # Fill in missing fields using Bedrock if needed
            if not metadata.get('job_title') or not metadata.get('job_requirements') or not metadata.get('job_location'):
                logger.info("Some metadata fields missing, extracting from text using Bedrock")
                extracted_metadata = get_metadata_from_bedrock(text)
                
                # Fill in only the missing fields
                if not metadata.get('job_title'):
                    metadata['job_title'] = extracted_metadata.get('job_title', 'Unknown')
                if not metadata.get('job_requirements'):
                    metadata['job_requirements'] = extracted_metadata.get('job_requirements', [])
                if not metadata.get('job_location'):
                    metadata['job_location'] = extracted_metadata.get('job_location', '')
        else:
            # Extract metadata from text using Bedrock
            metadata = get_metadata_from_bedrock(text)
        
        job_title = metadata.get('job_title', 'Unknown')
        logger.info(f"Successfully processed metadata for job title: {job_title}")
        
        # Generate embedding
        embedding = get_embedding(text)
        logger.info("Successfully generated embedding vector")
        
        # Update metadata
        s3_config = Config.get_s3_config()
        metadata['job_description_id'] = job_description_id
        metadata['s3_path'] = f"s3://{s3_config['bucket_name']}/{s3_key}"
        metadata['job_description'] = text
        metadata['upload_date'] = datetime.utcnow().isoformat()
        metadata['input_type'] = input_type
        
        # Prepare document for indexing
        document = {
            'metadata': metadata,
            'embedding': embedding,
            'job_title': job_title,
            'job_description_id': job_description_id,
            'file_name': filename or f"{job_description_id}.txt",
            'upload_date': metadata['upload_date'],
            'input_type': input_type
        }
        
        # Index document
        response = index_document(opensearch, job_description_id, document)
        
        total_end_time = time.time()
        logger.info(f"Total lambda execution time: {(total_end_time - total_start_time)*1000:.2f} ms")
        
        return success_response({
            'job_description_id': job_description_id,
            'job_title': job_title,
            'filename': filename or f"{job_description_id}.txt",
            's3_key': s3_key,
            'input_type': input_type
        }, 'Successfully processed job description')
        
    except Exception as e:
        total_end_time = time.time()
        logger.error(f"Total lambda execution time before failure: {(total_end_time - total_start_time)*1000:.2f} ms")
        logger.error(f"Error in lambda_handler: {str(e)}")
        return error_response(str(e))