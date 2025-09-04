#!/usr/bin/env python3
"""
Script to create S3 trigger for Lambda function using boto3
This is an alternative to using the AWS Console
"""

import boto3
import json

def setup_s3_trigger():
    """
    Create S3 event notification to trigger Lambda function
    """
    # Initialize AWS clients
    s3_client = boto3.client('s3', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Configuration
    bucket_name = 'trujobs-resume-pdfs'
    lambda_function_name = 'resume-processor'
    
    try:
        # Step 1: Get Lambda function ARN
        lambda_response = lambda_client.get_function(FunctionName=lambda_function_name)
        lambda_arn = lambda_response['Configuration']['FunctionArn']
        print(f"Lambda ARN: {lambda_arn}")
        
        # Step 2: Add permission for S3 to invoke Lambda (if not already exists)
        try:
            lambda_client.add_permission(
                FunctionName=lambda_function_name,
                StatementId='s3-trigger-permission-2',
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn=f'arn:aws:s3:::{bucket_name}/*'
            )
            print("✅ Added Lambda permission for S3")
        except lambda_client.exceptions.ResourceConflictException:
            print("✅ Lambda permission already exists")
        
        # Step 3: Create S3 event notification
        notification_config = {
            'LambdaConfigurations': [
                {
                    'Id': 'resume-processor-trigger',
                    'LambdaFunctionArn': lambda_arn,
                    'Events': ['s3:ObjectCreated:*'],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {
                                    'Name': 'suffix',
                                    'Value': '.pdf'
                                }
                            ]
                        }
                    }
                }
            ]
        }
        
        # Apply the notification configuration
        s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=notification_config
        )
        
        print("✅ S3 event notification created successfully!")
        print(f"✅ Bucket '{bucket_name}' will now trigger '{lambda_function_name}' for .pdf uploads")
        
        # Step 4: Verify the configuration
        response = s3_client.get_bucket_notification_configuration(Bucket=bucket_name)
        print("\n📋 Current notification configuration:")
        print(json.dumps(response, indent=2, default=str))
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up S3 trigger: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up S3 trigger for Lambda function...")
    success = setup_s3_trigger()
    
    if success:
        print("\n🎉 Setup complete! Your Lambda function should now be triggered when PDFs are uploaded to S3.")
        print("\n🧪 Test by uploading a PDF file to your S3 bucket and checking CloudWatch logs.")
    else:
        print("\n❌ Setup failed. Please check the error message above.")
