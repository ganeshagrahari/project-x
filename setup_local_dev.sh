#!/bin/bash

# AI Recruitment System - Local Development Environment Setup
echo "🚀 Setting up local development environment..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Set environment variables for local development
export OPENSEARCH_ENDPOINT="https://search-recruitment-search-xr3oxgazrekcvieeeogvudpf6u.aos.us-east-1.on.aws"
export AWS_REGION="us-east-1"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

echo "✅ Environment configured!"
echo "📍 OpenSearch Endpoint: $OPENSEARCH_ENDPOINT"
echo "🌍 AWS Region: $AWS_REGION"
echo "🐍 Python Path: $PYTHONPATH"
echo ""
echo "🎯 Available commands:"
echo "  python src/utils/verify_opensearch_data.py    # Check your data"
echo "  python src/utils/match_resumes_to_job.py      # Test matching"
echo "  python test_local_functions.py                # Test Lambda functions locally"
echo ""
echo "🚀 Ready for local development!"
