#!/bin/bash

# AWS Lambda Deployment Script for AI Recruitment System
# This script packages and deploys Lambda functions

echo "🚀 AI Recruitment System - Deployment Script"
echo "=============================================="

# Set variables
RESUME_FUNCTION="resume-processor"
JD_FUNCTION="job-description-processor"
REGION="us-east-1"

echo "📦 Creating deployment packages..."

# Create deployment package for resume processor
cd src/lambda_functions
echo "📄 Packaging resume processor..."
zip -r ../../deployment/resume-processor.zip resume_processor_lambda.py
echo "✅ Resume processor packaged"

# Create deployment package for job description processor  
echo "📄 Packaging job description processor..."
zip -r ../../deployment/job-description-processor.zip job_description_processor_lambda.py
echo "✅ Job description processor packaged"

cd ../../

echo "🎯 Deployment packages created in deployment/ folder"
echo "📋 Next steps:"
echo "   1. Upload resume-processor.zip to Lambda function: $RESUME_FUNCTION"
echo "   2. Upload job-description-processor.zip to Lambda function: $JD_FUNCTION"
echo "   3. Test both functions in AWS Console"

echo "✅ Deployment preparation complete!"
