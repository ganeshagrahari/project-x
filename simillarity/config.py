import os
import logging

# Environment variables
REGION = os.environ.get('AWS_REGION', 'ap-south-1')
SERVICE = os.environ.get('OPENSEARCH_SERVICE', 'aoss')
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'rcs-edubuk-resume')
JOB_DESCRIPTION_INDEX = os.environ.get('JOB_DESCRIPTION_INDEX', 'rcs-job-description')
RESUME_INDEX = os.environ.get('RESUME_INDEX', 'resume_upload')
DEFAULT_TOP_K = int(os.environ.get('DEFAULT_TOP_K', '100'))
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
DEBUG_FILTERING = os.environ.get('DEBUG_FILTERING', 'false').lower() == 'true'

# Configure logging
logger = logging.getLogger()
logger.setLevel(getattr(logging, LOG_LEVEL))

# If debug filtering is enabled, ensure debug level for detailed filtering logs
if DEBUG_FILTERING and LOG_LEVEL != 'DEBUG':
    logger.setLevel(logging.DEBUG)

# Constants
HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
}