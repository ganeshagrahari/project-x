import json
import uuid
import logging
from pdf_processor import parse_multipart_form, extract_text_from_pdf, save_pdf_to_s3
from ai_services import get_metadata_from_bedrock, create_section_embeddings
from opensearch_client import get_opensearch_client, normalize_metadata_for_opensearch, index_resume_document

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Main Lambda handler function"""
    try:
        logger.info("Processing resume upload request")
        logger.info(f"Event: {json.dumps(event, default=str)}")

        # Parse multipart form data
        pdf_content, job_description_id = parse_multipart_form(event)
        
        # Generate unique identifiers
        resume_id = str(uuid.uuid4())
        filename = f"{resume_id}.pdf"
        
        # Save PDF to S3
        pdf_content_bytes = pdf_content.getvalue()
        s3_key = save_pdf_to_s3(pdf_content_bytes, filename)
        logger.info(f"Saved PDF to S3: {s3_key}")

        # Initialize OpenSearch
        opensearch = get_opensearch_client()
        
        # Extract text from PDF
        pdf_content.seek(0)
        text = extract_text_from_pdf(pdf_content)
        logger.info(f"Extracted {len(text)} characters from PDF")

        # Get structured metadata using Bedrock
        raw_metadata = get_metadata_from_bedrock(text)
        candidate_name = raw_metadata.get('full_name', 'Unknown')
        logger.info(f"Extracted metadata for candidate: {candidate_name}")

        # Normalize metadata for OpenSearch compatibility
        normalized_metadata = normalize_metadata_for_opensearch(raw_metadata, text)

        # Create section-specific embeddings
        embeddings = create_section_embeddings(raw_metadata)
        logger.info("Generated section-specific embeddings")

        # Index document in OpenSearch
        response = index_resume_document(
            opensearch, resume_id, job_description_id, filename, 
            candidate_name, s3_key, normalized_metadata, embeddings
        )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Successfully processed resume',
                'resume_id': resume_id,
                'filename': filename,
                'job_description_id': job_description_id,
                'candidate_name': candidate_name,
                's3_key': s3_key
                # 'opensearch_id': response.get('_id')
            })
        }

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Invalid request format or missing required data'
            })
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': f'Failed to process resume: {str(e)}'
            })
        }