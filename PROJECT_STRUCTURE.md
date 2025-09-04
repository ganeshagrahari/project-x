# 📁 Project Structure

```
project-x/
├── 📂 src/                              # Source code
│   ├── 📂 lambda_functions/             # AWS Lambda functions
│   │   ├── resume_processor_lambda.py   # Resume processing pipeline
│   │   └── job_description_processor_lambda.py # Job description processing
│   └── 📂 utils/                        # Utility scripts
│       ├── match_resumes_to_job.py      # Resume-job matching algorithm
│       ├── setup_s3_trigger.py          # Resume S3 trigger setup
│       ├── setup_jd_s3_trigger.py       # Job description S3 trigger setup
│       └── verify_opensearch_data.py    # Data verification utility
│
├── 📂 docs/                             # Documentation
│   ├── 10_DAY_TIMELINE.md              # Project timeline
│   ├── SETUP_GUIDE.md                  # AWS setup instructions
│   ├── DEPLOYMENT_GUIDE.md             # Deployment instructions
│   ├── TESTING_GUIDE.md                # Testing procedures
│   ├── JSON_CHEAT_SHEET.md             # OpenSearch query examples
│   ├── PROJECT_STATUS.md               # Project status tracking
│   ├── BEGINNER_VISUAL_GUIDE.md        # Visual setup guide
│   ├── JOB_DESCRIPTION_DEPLOYMENT.md   # Job description deployment
│   └── VISUAL_SCREENSHOTS_GUIDE.md     # Screenshots guide
│
├── 📂 deployment/                       # Deployment scripts
│   └── deploy.sh                       # Deployment automation
│
├── 📂 samples/                          # Sample files
│   ├── sample_job_description.txt      # Sample job description
│   └── image.png                       # Sample image
│
├── 📄 README.md                        # Main project documentation
├── 📄 requirements.txt                 # Python dependencies
├── 📄 .gitignore                      # Git ignore rules
└── 📄 PROJECT_STRUCTURE.md             # This file - project organization
```

## 🔥 Key Files Explained

### **Source Code (`src/`)**
- **`lambda_functions/`**: Contains the core AI processing pipelines
  - `resume_processor_lambda.py` - Processes resumes with Claude AI
  - `job_description_processor_lambda.py` - Processes job descriptions with Claude AI
  
- **`utils/`**: Helper scripts and utilities
  - `match_resumes_to_job.py` - Semantic matching between resumes and jobs
  - `setup_s3_trigger.py` - Sets up S3 triggers for resume processing
  - `setup_jd_s3_trigger.py` - Sets up S3 triggers for job description processing
  - `verify_opensearch_data.py` - Verifies data storage in OpenSearch

### **Documentation (`docs/`)**
- Comprehensive guides for setup, deployment, and testing
- Project timeline and status tracking
- OpenSearch query examples and best practices

### **Deployment (`deployment/`)**
- Scripts for automating AWS deployment
- Packaging and upload utilities

### **Samples (`samples/`)**
- Example files for testing the system
- Sample job descriptions and reference materials

## 🎯 **Working System Status**
✅ **Day 3 Completed** - Both resume and job description processing pipelines operational
✅ **AI Processing** - Claude 3 Haiku + Titan embeddings working
✅ **Auto-triggers** - S3 upload triggers both Lambda functions
✅ **Vector Storage** - OpenSearch storing embeddings for semantic search
✅ **Matching Algorithm** - Resume-to-job matching implemented

## 🚀 **Next Steps**
Ready for Day 4: Web interface development with clean, organized codebase!
