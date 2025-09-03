import boto3
import PyPDF2
import logging
import base64
import io
import re
from config import BUCKET_NAME, RESUME_PREFIX

logger = logging.getLogger()
s3 = boto3.client('s3')


def parse_multipart_form(event):
    """Parse multipart form data from API Gateway event"""
    try:
        headers = event.get('headers', {})
        if not headers and 'multiValueHeaders' in event:
            headers = {k: v[0] if isinstance(v, list) else v for k, v in event['multiValueHeaders'].items()}
        
        content_type = None
        for key in headers:
            if key.lower() == 'content-type':
                content_type = headers[key]
                break
        
        if not content_type:
            raise ValueError('Content-Type header missing in request')

        boundary_match = re.search(r'boundary=([^;,\s]+)', content_type, re.IGNORECASE)
        if not boundary_match:
            raise ValueError('Boundary not found in Content-Type header')
        boundary = boundary_match.group(1).strip('"')

        body = event.get('body', '')
        if not body:
            raise ValueError('Request body is empty')
            
        if event.get('isBase64Encoded', False):
            try:
                body = base64.b64decode(body)
            except Exception as e:
                logger.error(f"Failed to decode base64 body: {str(e)}")
                raise ValueError('Failed to decode base64 body')
        else:
            if isinstance(body, str):
                body = body.encode('utf-8')

        boundary_bytes = f'--{boundary}'.encode('utf-8')
        parts = body.split(boundary_bytes)

        pdf_file = None
        job_description_id = None

        for part in parts:
            if not part or part.strip() in [b'', b'--', b'--\r\n', b'--\n']:
                continue

            try:
                header_end = -1
                for separator in [b'\r\n\r\n', b'\n\n', b'\r\r']:
                    pos = part.find(separator)
                    if pos != -1:
                        header_end = pos + len(separator)
                        break
                
                if header_end == -1:
                    continue

                header_section = part[:header_end].decode('utf-8', errors='ignore')
                content_section = part[header_end:]

                if 'name="pdf_file"' in header_section:
                    if content_section.endswith(b'--\r\n'):
                        content_section = content_section[:-4]
                    elif content_section.endswith(b'--\n'):
                        content_section = content_section[:-3]
                    elif content_section.endswith(b'\r\n'):
                        content_section = content_section[:-2]
                    elif content_section.endswith(b'\n'):
                        content_section = content_section[:-1]

                    if len(content_section) > 0:
                        pdf_file = io.BytesIO(content_section)

                elif 'name="job_description_id"' in header_section:
                    content_text = content_section.decode('utf-8', errors='ignore').strip()
                    content_text = content_text.strip('\r\n-')
                    if content_text:
                        job_description_id = content_text

            except Exception as e:
                logger.warning(f"Error processing multipart section: {str(e)}")
                continue

        if pdf_file is None:
            raise ValueError('PDF file not found in request')
        if not job_description_id or job_description_id.strip() == '':
            raise ValueError('Job description ID is required')

        pdf_file.seek(0)
        if len(pdf_file.getvalue()) < 100:
            raise ValueError('PDF file appears to be too small or corrupted')

        return pdf_file, job_description_id.strip()

    except Exception as e:
        logger.error(f"Multipart parsing error: {str(e)}")
        raise


def extract_text_from_pdf(pdf_content):
    """Extract text content from PDF file"""
    try:
        pdf_content.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_content)
        
        logger.info(f"PDF has {len(pdf_reader.pages)} pages")
        
        if len(pdf_reader.pages) == 0:
            raise ValueError("PDF contains no pages")
        
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    logger.info(f"Page {page_num + 1}: extracted {len(page_text)} characters")
                else:
                    logger.warning(f"Page {page_num + 1}: no text extracted")
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
                continue
        
        extracted_text = text.strip()
        logger.info(f"Total extracted text length: {len(extracted_text)}")
        
        if not extracted_text:
            raise ValueError("No text content extracted from PDF")
        
        return extracted_text
        
    except Exception as e:
        logger.error(f"PDF text extraction error: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def save_pdf_to_s3(pdf_content, filename):
    """Save PDF file to S3 bucket"""
    try:
        s3_key = f"{RESUME_PREFIX}{filename}"
        s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=pdf_content)
        return s3_key
    except Exception as e:
        logger.error(f"S3 upload error: {str(e)}")
        raise 