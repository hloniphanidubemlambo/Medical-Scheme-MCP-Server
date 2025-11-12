# 🔄 How to Switch from Mock to Real APIs

## 📍 **Exact Files to Modify**

When you get real API keys, here are the **exact files** you need to update:

### 1. **Update Environment Variables**
**File:** `.env`
```env
# Replace these mock values with real API keys:
DISCOVERY_API_KEY=your_real_discovery_key_here
GEMS_API_KEY=your_real_gems_key_here  
MEDSCHEME_API_KEY=your_real_medscheme_key_here

# Add real base URLs (you'll get these from the schemes):
DISCOVERY_BASE_URL=https://api.discovery.co.za/health/v1
GEMS_BASE_URL=https://api.gems.gov.za/medical/v1
MEDSCHEME_BASE_URL=https://api.medscheme.co.za/health/v1
```

### 2. **Discovery Connector**
**File:** `src/connectors/discovery_connector.py`

**Lines to change:** 13, 25-35, 50-70, 85-95, 110-120

```python
# Line 13: Update base URL
def __init__(self, api_key: str):
    # OLD: super().__init__(api_key, "https://api.discovery.co.za/health/v1")
    # NEW: 
    base_url = os.getenv("DISCOVERY_BASE_URL", "https://api.discovery.co.za/health/v1")
    super().__init__(api_key, base_url)

# Lines 25-35: Replace mock benefit check
async def check_benefits(self, benefit_check: BenefitCheck) -> BenefitResponse:
    # DELETE THIS MOCK CODE:
    # return BenefitResponse(
    #     member_id=benefit_check.member_id,
    #     procedure_code=benefit_check.procedure_code,
    #     benefit_available=True,
    #     remaining_benefit=15000.00,
    #     annual_limit=50000.00,
    #     co_payment_required=500.00,
    #     authorization_required=benefit_check.procedure_code.startswith("MRI")
    # )
    
    # UNCOMMENT AND USE THIS REAL CODE:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{self.base_url}/benefits/{benefit_check.member_id}/{benefit_check.procedure_code}",
            headers=self.headers
        )
        if response.status_code == 200:
            data = response.json()
            return BenefitResponse(**data)
        else:
            raise HTTPException(response.status_code, f"Discovery API error: {response.text}")

# Lines 50-70: Replace mock authorization
async def request_authorization(self, auth_request: AuthorizationRequest) -> AuthorizationResponse:
    # DELETE MOCK CODE AND UNCOMMENT REAL CODE:
    payload = {
        "memberId": auth_request.member_id,
        "providerId": auth_request.provider_id,
        "procedureCode": auth_request.procedure_code,
        "diagnosisCode": auth_request.diagnosis_code,
        "patientName": auth_request.patient_name,
        "requestedDate": auth_request.requested_date.isoformat(),
        "urgency": auth_request.urgency,
        "clinicalNotes": auth_request.clinical_notes
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{self.base_url}/authorizations",
            json=payload,
            headers=self.headers
        )
        if response.status_code == 200:
            data = response.json()
            return AuthorizationResponse(**data)
        else:
            raise HTTPException(response.status_code, f"Discovery API error: {response.text}")

# Lines 85-95: Replace mock claim submission
async def submit_claim(self, claim: Claim) -> ClaimResponse:
    # DELETE MOCK CODE AND UNCOMMENT REAL CODE:
    payload = claim.dict()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{self.base_url}/claims",
            json=payload,
            headers=self.headers
        )
        if response.status_code == 200:
            data = response.json()
            return ClaimResponse(**data)
        else:
            raise HTTPException(response.status_code, f"Discovery API error: {response.text}")
```

### 3. **GEMS Connector**
**File:** `src/connectors/gems_connector.py`

**Same pattern as Discovery - replace mock returns with real API calls**

### 4. **Medscheme Connector**  
**File:** `src/connectors/medscheme_connector.py`

**Same pattern as Discovery - replace mock returns with real API calls**

### 5. **Add Error Handling**
**File:** `src/connectors/base_connector.py`

Add this method to the base class:
```python
async def _make_api_call(self, method: str, endpoint: str, data: dict = None):
    """Generic API call with error handling"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method.upper() == "GET":
                response = await client.get(endpoint, headers=self.headers)
            elif method.upper() == "POST":
                response = await client.post(endpoint, json=data, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise HTTPException(401, "Invalid API credentials")
            elif response.status_code == 404:
                raise HTTPException(404, "Member or procedure not found")
            elif response.status_code == 429:
                raise HTTPException(429, "Rate limit exceeded")
            else:
                raise HTTPException(500, f"API error: {response.text}")
                
    except httpx.TimeoutException:
        raise HTTPException(408, "API request timeout")
    except httpx.NetworkError:
        raise HTTPException(503, "Network error connecting to API")
```

## 🎯 **Step-by-Step Switching Process**

### **Phase 1: Preparation**
1. **Get API credentials** from medical schemes
2. **Read API documentation** they provide
3. **Set up test environment** first

### **Phase 2: Configuration**
1. **Update `.env`** with real keys and URLs
2. **Test connectivity** with simple API calls

### **Phase 3: Code Changes**
1. **Start with Discovery** (usually easiest)
2. **Replace mock code** with real API calls in `discovery_connector.py`
3. **Test thoroughly** with real member IDs
4. **Repeat for GEMS and Medscheme**

### **Phase 4: Testing**
1. **Test each function** individually
2. **Test error scenarios** (invalid member, network issues)
3. **Test MCP tools** end-to-end
4. **Performance test** with expected load

## 📞 **Where to Get Real API Access**

### **Discovery Health**
- **Website:** https://developer.discovery.co.za
- **Email:** api-support@discovery.co.za
- **Phone:** 0860 99 88 77
- **Requirements:** POPIA compliance, practice registration, SSL cert

### **GEMS (Government Employees Medical Scheme)**
- **Email:** it-support@gems.gov.za
- **Phone:** 0860 436 7 (0860 GEMS)
- **Address:** GEMS House, 2 Oxbow Crescent, Century City, Cape Town
- **Requirements:** Government provider registration, security clearance

### **Medscheme**
- **Website:** https://www.medscheme.co.za
- **Email:** integration@medscheme.co.za
- **Phone:** 021 529 8000
- **Requirements:** Provider accreditation, technical assessment

## 🚨 **Important Notes**

### **Before Making Changes:**
1. **Backup your working mock version**
2. **Create a git branch** for real API integration
3. **Test in development environment** first

### **Testing Strategy:**
1. **Start with sandbox/test APIs** if available
2. **Use real but non-sensitive data** for testing
3. **Test one scheme at a time**
4. **Keep mock connectors** as fallback during transition

### **Common Issues:**
- **Different response formats** than expected
- **Rate limiting** from APIs
- **Authentication token expiry**
- **Network timeouts**
- **Different error codes**

## 📋 **Quick Checklist**

When you're ready to switch:

- [ ] **Got real API keys** from all schemes
- [ ] **Read API documentation** thoroughly  
- [ ] **Updated `.env`** with real credentials
- [ ] **Modified Discovery connector** first
- [ ] **Tested Discovery integration** thoroughly
- [ ] **Modified GEMS connector**
- [ ] **Tested GEMS integration**
- [ ] **Modified Medscheme connector**
- [ ] **Tested Medscheme integration**
- [ ] **Tested all MCP tools** end-to-end
- [ ] **Added proper error handling**
- [ ] **Set up monitoring** and alerting
- [ ] **Trained staff** on new system

## 🎯 **The Exact Moment to Switch**

You'll know you're ready when:
1. ✅ You have **real API keys** from at least one scheme
2. ✅ You've **read their API documentation**
3. ✅ You have **test member IDs** to use
4. ✅ You're **comfortable with the current mock system**

**Start with just ONE scheme** (Discovery is usually easiest), get it working, then add the others one by one.

Your mock implementation is **perfect for now** - it lets you develop, test, and demonstrate everything while you work on getting real API access! 🚀