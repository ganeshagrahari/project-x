#!/bin/bash

# 🚀 Quick Lambda Deployment Script
# Run this script to create deployment packages for AWS Lambda

echo "🚀 Creating Lambda deployment packages..."

# Create deployment packages directory
mkdir -p deployment-packages

echo "📦 Creating Resume Ingestion package..."
cd resume-ingestion-lambda
zip -r ../deployment-packages/resume-ingestion-lambda.zip .
cd ..

echo "📦 Creating Job Description Ingestion package..."
cd jd-ingestion-lambda  
zip -r ../deployment-packages/jd-ingestion-lambda.zip .
cd ..

echo "✅ Deployment packages created:"
echo "   📁 deployment-packages/resume-ingestion-lambda.zip"
echo "   📁 deployment-packages/jd-ingestion-lambda.zip"

echo ""
echo "🎯 Next Steps:"
echo "1. Go to AWS Lambda Console"
echo "2. Create new functions and upload these zip files"
echo "3. Configure environment variables (see DEPLOYMENT_GUIDE.md)"
echo "4. Add your existing Lambda layer with dependencies"
echo "5. Test the functions!"

ls -la deployment-packages/
