import boto3
import json
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_s3_trigger(bucket_name, lambda_function_name, prefix):
    """
    Create an S3 event trigger for a Lambda function
    """
    try:
        # Initialize clients
        s3_client = boto3.client('s3')
        lambda_client = boto3.client('lambda')
        
        # Get Lambda function ARN
        lambda_response = lambda_client.get_function(FunctionName=lambda_function_name)
        lambda_arn = lambda_response['Configuration']['FunctionArn']
        
        logger.info(f"Setting up S3 trigger for Lambda function: {lambda_arn}")
        
        # Configure notification for S3 bucket
        notification_config = {
            'LambdaFunctionConfigurations': [
                {
                    'Id': f"{lambda_function_name}-trigger",
                    'LambdaFunctionArn': lambda_arn,
                    'Events': ['s3:ObjectCreated:*'],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {
                                    'Name': 'prefix',
                                    'Value': prefix
                                }
                            ]
                        }
                    }
                }
            ]
        }
        
        # Put the notification configuration
        s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=notification_config
        )
        
        logger.info(f"Successfully set up S3 trigger for bucket {bucket_name} with prefix {prefix}")
        
        # Add permissions for S3 to invoke Lambda
        try:
            lambda_client.add_permission(
                FunctionName=lambda_function_name,
                StatementId=f"AllowS3Invocation-{bucket_name}",
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn=f"arn:aws:s3:::{bucket_name}"
            )
            logger.info(f"Added permission for S3 bucket {bucket_name} to invoke Lambda function")
        except lambda_client.exceptions.ResourceConflictException:
            logger.info(f"Permission already exists for S3 bucket {bucket_name} to invoke Lambda function")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up S3 trigger: {str(e)}")
        return False

def main():
    """
    Main function to set up the S3 trigger
    """
    # Get configuration from command-line arguments or environment variables
    if len(sys.argv) >= 4:
        bucket_name = sys.argv[1]
        lambda_function_name = sys.argv[2]
        prefix = sys.argv[3]
    else:
        bucket_name = os.environ.get('BUCKET_NAME', 'trujobs-jd-pdfs')
        lambda_function_name = os.environ.get('LAMBDA_FUNCTION_NAME', 'job_description_processor')
        prefix = os.environ.get('PREFIX', '')
    
    logger.info(f"Setting up S3 trigger for bucket: {bucket_name}, lambda: {lambda_function_name}, prefix: {prefix}")
    
    success = create_s3_trigger(bucket_name, lambda_function_name, prefix)
    
    if success:
        logger.info("S3 trigger setup completed successfully!")
        sys.exit(0)
    else:
        logger.error("Failed to set up S3 trigger. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
