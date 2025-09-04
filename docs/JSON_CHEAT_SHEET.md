# 🔍 OpenSearch Queries - AI Recruitment System

## 🎯 **WORKING SYSTEM - Use These Queries!**
Your AI recruitment system is processing resumes and storing them in OpenSearch. Use these queries in OpenSearch Dashboards Dev Tools.

**Access:** OpenSearch Dashboards → Dev Tools → Console

---

## 📊 **Essential Queries for Your System**

### **1. See All Processed Resumes**
```json
GET /resumes/_search
{
  "query": {
    "match_all": {}
  },
  "sort": [
    {
      "processed_at": {
        "order": "desc"
      }
    }
  ]
}
```

### **2. Count Total Resumes**
```json
GET /resumes/_count
```

### **3. Get Resume Summary (File Names & Dates)**
```json
GET /resumes/_search
{
  "query": {
    "match_all": {}
  },
  "_source": ["file_name", "processed_at"],
  "size": 10
}
```

### **4. Search by Exact File Name**
```json
GET /resumes/_search
{
  "query": {
    "term": {
      "file_name": "Ganesh-Agrahari-Resume.pdf"
    }
  },
  "_source": ["file_name", "processed_at"]
}
```

### **5. Search by Candidate Name**
```json
GET /resumes/_search
{
  "query": {
    "match": {
      "metadata.name": "Ganesh"
    }
  }
}
```

### **5. Search by Candidate Name**
```json
GET /resumes/_search
{
  "query": {
    "match": {
      "metadata.name": "Ganesh"
    }
  }
}
```

### **6. Search by Skills**
```json
GET /resumes/_search
{
  "query": {
    "match": {
      "metadata.skills": "Python"
    }
  }
}
```

### **7. Search by Experience Level**
```json
GET /resumes/_search
{
  "query": {
    "range": {
      "metadata.total_experience_years": {
        "gte": 3,
        "lte": 10
      }
    }
  }
}
```

### **8. Search by File Name (Partial Match)**
```json
GET /resumes/_search
{
  "query": {
    "match": {
      "file_name": "Ganesh-Agrahari-Resume.pdf"
    }
  }
}
```

### **9. Get Specific Resume by ID**
```json
GET /resumes/_doc/2b262f12-45ca-447b-adaf-fce249534d0f
```

### **10. Search Resume Content**
```json
GET /resumes/_search
{
  "query": {
    "match": {
      "text_content": "software engineer"
    }
  }
}
```

### **11. Complex Search (Multiple Criteria)**
```json
GET /resumes/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "metadata.skills": "Python"
          }
        },
        {
          "range": {
            "metadata.total_experience_years": {
              "gte": 2
            }
          }
        }
      ]
    }
  }
}
```

### **12. Get Only Specific Fields**
```json
GET /resumes/_search
{
  "query": {
    "match_all": {}
  },
  "_source": ["file_name", "metadata.name", "metadata.skills", "processed_at"]
}
```

---

## 🔥 **Advanced Queries (Coming in Day 3)**

### **Semantic Vector Search (Coming Soon)**
```json
GET /resumes/_search
{
  "query": {
    "knn": {
      "embeddings": {
        "vector": [0.1, 0.2, 0.3, ...],
        "k": 5
      }
    }
  }
}
```

---

## 🎓 **JSON Basics for Beginners**

### **Basic Structure:**
```json
{
  "name": "John Doe",
  "age": 30,
  "city": "Mumbai"
}
```

**How to read this:**
- `{}` = A container (like a box)
- `"name"` = A label (like a sticky note)
- `"John Doe"` = The value (what's written on the sticky note)
- `:` = "equals" or "is"
- `,` = "and also"

**In English:** "Name is John Doe, AND age is 30, AND city is Mumbai"

---

## 🏠 **JSON Like a House**

```json
{
  "house": {
    "address": "123 Main Street",
    "rooms": ["kitchen", "bedroom", "bathroom"],
    "owner": {
      "name": "John",
      "age": 30
    }
  }
}
```

**Think of it as:**
- 🏠 **House** = Main container
- 📍 **Address** = Simple information
- 🚪 **Rooms** = A list of things
- 👤 **Owner** = Another container inside the house

---

## 🛒 **Common JSON Patterns You'll See**

### **1. Simple Key-Value (Like a name tag)**
```json
{
  "service": "Lambda",
  "region": "ap-south-1",
  "memory": 512
}
```

### **2. Lists (Like a shopping list)**
```json
{
  "skills": ["Python", "AWS", "Machine Learning"],
  "languages": ["English", "Hindi", "Tamil"]
}
```

### **3. Nested Objects (Like Russian dolls)**
```json
{
  "person": {
    "name": "John",
    "contact": {
      "email": "john@email.com",
      "phone": "9876543210"
    }
  }
}
```

---

## 🎯 **JSON for Our Project**

### **Example 1: Resume Data**
```json
{
  "candidate": {
    "name": "Priya Sharma",
    "email": "priya@email.com",
    "skills": ["Python", "Django", "MySQL"],
    "experience": {
      "years": 5,
      "companies": ["TCS", "Infosys"]
    }
  }
}
```

**Translation:** "This candidate is named Priya Sharma, her email is priya@email.com, she knows Python, Django, and MySQL, and has 5 years experience at TCS and Infosys."

### **Example 2: AWS Configuration**
```json
{
  "lambda": {
    "memory": "512 MB",
    "timeout": "5 minutes",
    "environment": {
      "OPENSEARCH_ENDPOINT": "search-recruitment-xxxxx.com"
    }
  }
}
```

**Translation:** "Configure Lambda with 512MB memory, 5-minute timeout, and set the OpenSearch endpoint variable."

---

## ✍️ **JSON Rules (Don't Worry, I'll Provide Templates!)**

### **✅ What's Correct:**
```json
{
  "name": "value",
  "number": 123,
  "list": ["item1", "item2"],
  "object": {
    "nested": "value"
  }
}
```

### **❌ Common Mistakes:**
```json
{
  name: "value",          // ❌ Missing quotes around 'name'
  "number": "123",        // ❌ Numbers don't need quotes
  "list": ["item1" "item2"], // ❌ Missing comma between items
  "object": {
    "nested": "value"     // ❌ Missing comma (if more items follow)
  },                      // ❌ Extra comma at the end
}
```

---

## 🔧 **AWS Console JSON Examples**

### **IAM Policy (Permissions)**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

**Translation:** "Allow getting objects from my-bucket in S3"

### **OpenSearch Index Mapping**
```json
{
  "mappings": {
    "properties": {
      "name": {"type": "text"},
      "skills": {"type": "keyword"},
      "experience_years": {"type": "integer"}
    }
  }
}
```

**Translation:** "Create fields for name (searchable text), skills (exact matches), and experience_years (numbers)"

---

## 🛠️ **Tools to Help with JSON**

### **1. JSON Validators (Check if correct):**
- jsonlint.com
- JSON Viewer in browser developer tools

### **2. JSON Formatters (Make it pretty):**
- jsonformatter.org
- VS Code (if you use it later)

### **3. In AWS Console:**
- Built-in JSON editor with syntax highlighting
- Error messages show exactly what's wrong

---

## 🎯 **For Our Project: Copy-Paste Ready**

**Don't worry about creating JSON from scratch!** I'll provide:

### **✅ Ready-to-use templates:**
- IAM policies (permissions)
- OpenSearch mappings (database structure)
- Lambda configurations (function settings)
- Test data (sample resumes)

### **✅ Step-by-step instructions:**
- Where to paste each JSON
- What each part does
- How to modify values

### **✅ Error troubleshooting:**
- Common JSON errors and fixes
- AWS-specific error messages
- How to debug issues

---

## 🚨 **When You See JSON in AWS Console**

### **Scenario 1: Creating IAM Policy**
```
You'll see: [JSON editor box]
Action: Copy my template → Paste → Replace YOUR_ACCOUNT_ID
```

### **Scenario 2: OpenSearch Index Creation**
```
You'll see: [Dev Tools console]
Action: Copy my command → Paste → Press Enter
```

### **Scenario 3: Lambda Environment Variables**
```
You'll see: Key-Value form (not JSON!)
Action: Fill in the form with values I provide
```

---

## 🎓 **JSON Learning Strategy for Our 10 Days**

### **Day 1-2: Just Copy-Paste**
- Use my templates exactly
- Don't worry about understanding every detail
- Focus on getting things working

### **Day 3-4: Start Reading**
- Look at the JSON and try to understand what it does
- Ask questions about confusing parts
- Recognize patterns

### **Day 5-6: Light Modifications**
- Change simple values (names, numbers)
- Add new key-value pairs
- Feel more confident

### **Day 7-8: Understanding Structure**
- See how nested objects work
- Understand arrays/lists
- Debug simple errors

### **Day 9-10: Comfortable with JSON**
- Read and understand most JSON
- Make modifications confidently
- Help troubleshoot issues

---

## 🆘 **JSON Help Strategy**

### **If JSON looks confusing:**
1. 📸 Take a screenshot
2. 📝 Tell me which step you're on
3. ❓ Ask "What does this part do?"

### **If you get JSON errors:**
1. 📋 Copy the exact error message
2. 📄 Show me what you pasted
3. 🔧 I'll fix it and explain why

### **If you want to learn more:**
1. 🎯 Focus on getting the project working first
2. 📚 Learn JSON theory later
3. 🎓 Practice with small examples

---

## 🎉 **Remember: You Don't Need to Be a JSON Expert!**

**For our project success, you just need to:**
- ✅ Copy and paste my templates
- ✅ Replace placeholder values (like YOUR_ACCOUNT_ID)
- ✅ Recognize when something looks wrong
- ✅ Know how to ask for help

**JSON mastery comes with practice - focus on building your AI recruitment system first!** 🚀

---

## 🎯 **Quick Reference**

```json
{                    ← Start of container
  "key": "value",    ← Text value
  "number": 123,     ← Number value
  "list": [          ← Start of list
    "item1",         ← List item
    "item2"          ← Last item (no comma)
  ],                 ← End of list
  "nested": {        ← Start of nested container
    "inner": "value" ← Nested key-value
  }                  ← End of nested container (no comma if last)
}                    ← End of main container
```

**Ready to start? Let's build your AI recruitment system!** 🎯
