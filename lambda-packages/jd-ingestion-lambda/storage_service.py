import boto3
import PyPDF2
import logging
from config import Config

logger = logging.getLogger()

# Initialize S3 client
s3 = boto3.client('s3')

def save_text_to_s3(text_content, filename):
    """Save text content to S3 bucket as a text file"""
    try:
        s3_config = Config.get_s3_config()
        s3_key = f"{s3_config['jd_prefix']}{filename}"
        
        s3.put_object(
            Bucket=s3_config['bucket_name'],
            Key=s3_key,
            Body=text_content.encode('utf-8'),
            ContentType='text/plain'
        )
        return s3_key
    except Exception as e:
        logger.error(f"Error saving text to S3: {str(e)}")
        raise

def save_pdf_to_s3(pdf_content, filename):
    """Save PDF content to S3 bucket"""
    try:
        s3_config = Config.get_s3_config()
        s3_key = f"{s3_config['jd_prefix']}{filename}"
        
        s3.put_object(
            Bucket=s3_config['bucket_name'],
            Key=s3_key,
            Body=pdf_content
        )
        return s3_key
    except Exception as e:
        logger.error(f"Error saving PDF to S3: {str(e)}")
        raise

def extract_text_from_pdf(pdf_content):
    """Extract text content from PDF bytes"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_content)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
        if not text.strip():
            raise ValueError("No text content extracted from PDF")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise 