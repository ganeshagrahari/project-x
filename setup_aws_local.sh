#!/bin/bash

# AWS Credentials Setup for Local Development
# Replace these values with your actual AWS credentials

echo "🔑 Setting up AWS credentials for local development..."

# Method 1: Export environment variables (recommended for development)
echo "Setting AWS environment variables..."

# REPLACE THESE WITH YOUR ACTUAL CREDENTIALS:
export AWS_ACCESS_KEY_ID="your-access-key-here"
export AWS_SECRET_ACCESS_KEY="your-secret-key-here"
export AWS_DEFAULT_REGION="us-east-1"

echo "✅ AWS credentials set!"
echo "Region: us-east-1"

# Test connection
echo "Testing AWS connection..."
aws sts get-caller-identity

echo "🚀 Ready for local development!"
