import json
import base64
import re
import logging
from io import BytesIO

logger = logging.getLogger()

def determine_input_type(event):
    """Determine if the input is JSON or multipart form data"""
    try:
        content_type = event.get('headers', {}).get('Content-Type', '').lower()
        
        if 'application/json' in content_type:
            return 'json'
        elif 'multipart/form-data' in content_type:
            return 'multipart'
        else:
            # Try to parse as JSON if no clear content type
            try:
                if event.get('body'):
                    json.loads(event['body'])
                    return 'json'
            except:
                pass
            
            # Default to multipart if content-type suggests form data
            if 'boundary=' in content_type:
                return 'multipart'
                
        return 'json'  # Default to JSON
    except Exception as e:
        logger.warning(f"Error determining input type: {str(e)}, defaulting to JSON")
        return 'json'

def parse_json_input(event):
    """Parse JSON input from the event"""
    try:
        body = event.get('body', '{}')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')
        
        data = json.loads(body)
        
        # Validate required fields
        job_description_text = data.get('job_description')
        if not job_description_text:
            raise ValueError('job_description field is required in JSON input')
        
        # Optional fields with defaults
        job_title = data.get('job_title', '')
        job_requirements = data.get('job_requirements', [])
        job_location = data.get('job_location', '')
        
        return {
            'text': job_description_text,
            'metadata': {
                'job_title': job_title,
                'job_requirements': job_requirements if isinstance(job_requirements, list) else [],
                'job_location': job_location
            },
            'filename': None  # No file for JSON input
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {str(e)}")
        raise ValueError(f'Invalid JSON format: {str(e)}')
    except Exception as e:
        logger.error(f"Error parsing JSON input: {str(e)}")
        raise ValueError(f'Error parsing JSON input: {str(e)}')

def parse_multipart_form(event):
    """Parse multipart form data from the event"""
    try:
        if 'Content-Type' not in event['headers']:
            raise ValueError('Content-Type header missing in request')

        content_type = event['headers']['Content-Type']
        boundary = re.search(r'boundary=(.+)', content_type)
        if not boundary:
            raise ValueError('Boundary not found in Content-Type header')
        boundary = boundary.group(1)

        body = event['body']
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body)
        else:
            body = body.encode('utf-8')

        boundary_bytes = f'--{boundary}'.encode('utf-8')
        parts = body.split(boundary_bytes)

        pdf_file = None

        for part in parts:
            if not part or part.strip() == b'--':
                continue

            try:
                headers_str = part[:1000].decode('utf-8', errors='ignore')
            except Exception as e:
                logger.warning(f"Error decoding part headers: {str(e)}")
                continue

            if 'name="pdf_file"' in headers_str:
                try:
                    header_end = part.find(b'\r\n\r\n')
                    if header_end == -1:
                        header_end = part.find(b'\n\n')
                    if header_end == -1:
                        continue

                    pdf_content = part[header_end + 4:]
                    if pdf_content.endswith(b'--\r\n'):
                        pdf_content = pdf_content[:-4]
                    elif pdf_content.endswith(b'--\n'):
                        pdf_content = pdf_content[:-3]

                    pdf_file = BytesIO(pdf_content)
                    logger.info("Successfully extracted PDF content")

                except Exception as e:
                    logger.error(f"Error processing PDF content: {str(e)}")
                    continue

        if pdf_file is None:
            raise ValueError('PDF file not found in request')

        return pdf_file

    except Exception as e:
        logger.error(f"Error parsing multipart form data: {str(e)}")
        raise ValueError(f'Error parsing multipart form data: {str(e)}') 