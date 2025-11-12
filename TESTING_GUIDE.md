# 🧪 Complete Testing Guide - Step by Step

## 🚀 **Quick Start Testing (5 Minutes)**

### **Option 1: Automated Setup (Easiest)**
```cmd
# Double-click this file in Windows Explorer:
run_server.bat

# This will automatically:
# 1. Create virtual environment
# 2. Install dependencies  
# 3. Start the server
```

### **Recommended Setup (Tested & Working)**
```cmd
# 1. Open Command Prompt in your project folder
# 2. Create virtual environment
py -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\activate

# 4. Install core packages (REQUIRED)
pip install fastapi uvicorn python-dotenv httpx PyJWT

# 5. Start the server
.venv\Scripts\python.exe start_server_simple.py
```

**Expected Server Output:**
```
✅ uvicorn imported successfully
✅ Server app imported successfully
🚀 Starting Medical Scheme MCP Server...
📍 Server will be available at: http://localhost:8000
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## 🔍 **Step-by-Step Testing Process**

### **Step 1: Verify Project Structure**
```cmd
# Run structure validation
py test_structure.py
```
**Expected Output:**
```
✅ Directory: src
✅ Directory: src/config
✅ File: requirements.txt
✅ File: .env
📊 Project Structure Summary: 7/7 directories, 9/9 files
✅ Structure test completed!
```

### **Step 2: Start the Server**
```cmd
# Method 1: Use the startup script
py run_server.py

# Method 2: Use the batch file
run_server.bat

# Method 3: Direct uvicorn command
py -m uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
🏥 Medical Scheme MCP Server Starting...
📍 Host: 0.0.0.0
🔌 Port: 8000
🐛 Debug Mode: True
📊 API Documentation: http://0.0.0.0:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **Step 3: Test Server Health**
```cmd
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T14:09:12.960280",
  "version": "1.0.0",
  "services": {
    "discovery": "available",
    "gems": "available",
    "medscheme": "available"
  }
}
```

### **Step 3.5: Test FHIR Integration (Real Healthcare Data)**
```powershell
# Get authentication token
$auth = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -ContentType "application/json" -Body '{"username": "admin", "password": "password123"}'
$token = $auth.access_token

# Test FHIR connectivity
$headers = @{"Authorization" = "Bearer $token"}
$fhirTest = Invoke-RestMethod -Uri "http://localhost:8000/fhir/integration/test" -Headers $headers
$fhirTest | ConvertTo-Json -Depth 3
```

**Expected FHIR Response:**
```json
{
  "fhir": {
    "status": "connected",
    "url": "https://hapi.fhir.org/baseR4",
    "test_patients": 1
  },
  "integration_ready": true
}
```

### **Step 3.6: Get Real Patient Data**
```powershell
# Search for real patients in FHIR
$patients = Invoke-RestMethod -Uri "http://localhost:8000/fhir/patients/search?limit=3" -Headers $headers
$patients.patients | Format-Table -AutoSize
```

**Expected Real Patients:**
```
id      name                    gender  birthDate 
--      ----                    ------  ---------
7082689 Mayank Panwar           male    1974-12-25
7082691 Peter James Chalmers    male    1974-12-25
7082690 Peter2 James2 Chalmers2 unknown 1979-12-25
```

### **Step 4: Explore the API Documentation**
```
http://localhost:8000/docs
```
You should see:
- ✅ Interactive Swagger UI
- ✅ All API endpoints listed
- ✅ MCP Tools section
- ✅ Medical Schemes section
- ✅ Practice Tools section

### **Step 5: Test the Practice Dashboard**
```
http://localhost:8000/practice/dashboard
```
You should see:
- ✅ Medical Practice MCP Dashboard
- ✅ Tool cards for each MCP function
- ✅ Quick test form
- ✅ Scheme badges (Discovery, GEMS, Medscheme)

## 🤖 **Testing MCP Tools**

### **Step 1: Get Authentication Token**

**Method 1: Using Browser (Easiest)**
1. Go to `http://localhost:8000/docs`
2. Click "Authorize" button (🔒)
3. Click "Try it out" on `/auth/login`
4. Use credentials:
   ```json
   {
     "username": "admin",
     "password": "password123"
   }
   ```
5. Copy the `access_token` from response

**Method 2: Using Command Line**
```cmd
curl -X POST "http://localhost:8000/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"admin\", \"password\": \"password123\"}"
```

### **Step 2: Test Benefit Check**
In the API docs (`/docs`), find "MCP Tools" section:

1. Click on `POST /mcp/tools/check_patient_benefits`
2. Click "Try it out"
3. Fill in parameters:
   ```
   patient_name: John Doe
   member_id: DISC123456
   scheme_name: discovery
   procedure_codes: ["CONS001", "MRI001"]
   ```
4. Click "Execute"

**Expected Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "✅ Benefit check completed for John Doe (DISC123456)"
    },
    {
      "type": "resource",
      "resource": {
        "patient_name": "John Doe",
        "benefits": [
          {
            "procedure_code": "CONS001",
            "benefit_available": true,
            "remaining_benefit": 15000.00
          }
        ]
      }
    }
  ]
}
```

### **Step 3: Test Authorization Request**
1. Find `POST /mcp/tools/request_procedure_authorization`
2. Fill in parameters:
   ```
   patient_name: Jane Smith
   member_id: GEMS789012
   scheme_name: gems
   provider_id: PROV001
   procedure_code: MRI001
   procedure_name: Brain MRI with contrast
   estimated_cost: 3500.00
   ```

### **Step 4: Test Claim Submission**
1. Find `POST /mcp/tools/submit_medical_claim`
2. Fill in parameters and JSON body with procedures

### **Step 5: Test Complete Workflow**
1. Find `POST /mcp/tools/complete_patient_workflow`
2. Test end-to-end patient processing

## 🧪 **Running Automated Tests**

### **Unit Tests**
```cmd
# Install pytest if not already installed
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_mock_connectors.py -v

# Run MCP tools tests
pytest tests/test_mcp_tools.py -v

# Run with coverage
pip install pytest-cov
pytest tests/ --cov=src --cov-report=html
```

**Expected Output:**
```
tests/test_mock_connectors.py::test_discovery_benefit_check PASSED
tests/test_mock_connectors.py::test_discovery_authorization PASSED
tests/test_mcp_tools.py::test_check_patient_benefits_mcp_tool PASSED
========================= 15 passed in 2.34s =========================
```

### **Interactive Demo**
```cmd
# Make sure server is running first, then in another terminal:
py demo_mcp_tools.py
```

**Expected Output:**
```
🏥 Medical Scheme MCP Server - Demo
============================================================
🔐 Authenticating...
✅ Authentication successful!

============================================================
🔍 DEMO: Checking Patient Benefits
============================================================
✅ Benefit check completed for John Doe (DISC123456)

📊 Benefit Details:
  ✅ CONS001: R15,000.00 remaining | ✅ No Auth Needed
  ✅ MRI001: R15,000.00 remaining | 🔐 Auth Required
```

## 🌐 **Browser Testing Checklist**

### **Basic Endpoints**
- [ ] `http://localhost:8000` - Root endpoint
- [ ] `http://localhost:8000/health` - Health check
- [ ] `http://localhost:8000/status` - Server status
- [ ] `http://localhost:8000/docs` - API documentation
- [ ] `http://localhost:8000/practice/dashboard` - Practice dashboard

### **API Functionality**
- [ ] Authentication works (`/auth/login`)
- [ ] Benefit checks return data
- [ ] Authorization requests work
- [ ] Claim submissions work
- [ ] Complete workflows work
- [ ] Error handling works (try invalid data)

### **MCP Tools**
- [ ] All 4 MCP tools listed at `/mcp/tools`
- [ ] Each tool returns proper MCP format
- [ ] Tools work with different schemes (discovery, gems, medscheme)
- [ ] Error responses are in MCP format

## 🐛 **Troubleshooting Common Issues**

### **Server Won't Start**
```cmd
# Check if port 8000 is in use
netstat -an | findstr :8000

# Try different port
set PORT=8001
py run_server.py
```

### **Dependencies Not Installing**
```cmd
# Update pip first
py -m pip install --upgrade pip

# Clear pip cache
pip cache purge

# Install with verbose output
pip install -r requirements.txt -v
```

### **Authentication Fails**
- Check username: `admin`
- Check password: `password123`
- Make sure server is running
- Try refreshing the page

### **API Returns Errors**
- Check server logs in terminal
- Verify authentication token
- Check request format in `/docs`
- Look at `medical_mcp.log` file

## 📊 **Performance Testing**

### **Load Testing (Optional)**
```cmd
# Install locust for load testing
pip install locust

# Create simple load test
# Then run: locust -f load_test.py --host=http://localhost:8000
```

### **Response Time Testing**
```cmd
# Test response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/health"
```

## ✅ **Success Criteria**

Your testing is successful when:

### **✅ Server Health**
- Server starts without errors
- Health endpoint returns "healthy"
- API documentation loads
- Practice dashboard displays correctly

### **✅ Authentication**
- Login returns valid JWT token
- Protected endpoints accept token
- Invalid credentials are rejected

### **✅ MCP Tools**
- All 4 tools return proper responses
- Tools work with all 3 schemes
- Error handling works correctly
- Response format matches MCP standard

### **✅ Mock Data**
- Realistic responses for all operations
- Different schemes return different data
- Authorization requirements vary by procedure
- Claims show proper approval amounts

## 🎯 **Next Steps After Testing**

Once testing is successful:

1. **✅ Demo to stakeholders** using practice dashboard
2. **✅ Integrate with AI assistants** using MCP tools
3. **✅ Connect practice management systems** via API
4. **✅ Train staff** on new workflows
5. **✅ Plan real API integration** when ready

## 🆘 **Getting Help**

If you encounter issues:

1. **Check server logs** in terminal
2. **Look at `medical_mcp.log`** file
3. **Run `py test_structure.py`** to verify setup
4. **Check `/docs`** for API reference
5. **Try the demo script** `py demo_mcp_tools.py`

Your MCP server is ready for comprehensive testing! 🚀