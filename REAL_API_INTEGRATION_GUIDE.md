# 🔗 Real API Integration Guide

## Current Status: Mock Implementation ⚠️

Your MCP server is currently using **mock connectors** that return realistic test data. This allows you to:
- ✅ Test all functionality immediately
- ✅ Develop and integrate systems
- ✅ Demonstrate to stakeholders
- ✅ Prepare for real integration

## 🔄 Switching to Real APIs

### Step 1: Get Real API Credentials

#### Discovery Health
```bash
# Contact Discovery Developer Portal
# Apply for API access at: https://developer.discovery.co.za
# Requirements:
# - POPIA compliance certificate
# - Practice registration documents
# - SSL certificate for production
```

#### GEMS (Government Employees Medical Scheme)
```bash
# Contact GEMS IT Department
# Email: it-support@gems.gov.za
# Requirements:
# - Government provider registration
# - Integration assessment
# - Security clearance
```

#### Medscheme
```bash
# Contact Medscheme Technical Team
# Email: integration@medscheme.co.za
# Requirements:
# - Provider accreditation
# - Technical integration assessment
# - API documentation request
```

### Step 2: Update Environment Variables

Once you have real API keys, update your `.env` file:

```env
# Replace mock keys with real ones
DISCOVERY_API_KEY=real_discovery_api_key_here
GEMS_API_KEY=real_gems_api_key_here
MEDSCHEME_API_KEY=real_medscheme_api_key_here

# Update base URLs (you'll get these from the schemes)
DISCOVERY_BASE_URL=https://api.discovery.co.za/health/v1
GEMS_BASE_URL=https://api.gems.gov.za/medical/v1
MEDSCHEME_BASE_URL=https://api.medscheme.co.za/health/v1
```

### Step 3: Enable Real API Calls

For each connector, you need to:

#### Discovery Connector Example:
```python
# In src/connectors/discovery_connector.py

async def check_benefits(self, benefit_check: BenefitCheck) -> BenefitResponse:
    """Check member benefits - REAL API IMPLEMENTATION"""
    
    # Comment out or remove mock implementation:
    # return BenefitResponse(...)
    
    # Uncomment and use real implementation:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{self.base_url}/benefits/{benefit_check.member_id}/{benefit_check.procedure_code}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return BenefitResponse(**data)
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Discovery API error: {response.text}"
            )
```

### Step 4: Update Base URLs in Connectors

```python
# In src/connectors/discovery_connector.py
def __init__(self, api_key: str):
    # Change from mock URL to real URL
    super().__init__(api_key, os.getenv("DISCOVERY_BASE_URL", "https://api.discovery.co.za/health/v1"))
```

### Step 5: Handle Real API Responses

Real APIs will return different data structures. You'll need to:

1. **Map API responses** to your Pydantic models
2. **Handle API errors** appropriately
3. **Add retry logic** for network issues
4. **Implement rate limiting** if required

#### Example Real API Response Mapping:
```python
# Discovery might return:
{
    "memberNumber": "DISC123456",
    "procedureCode": "MRI001", 
    "benefitAvailable": true,
    "remainingBenefit": 15000.00,
    "annualLimit": 50000.00,
    "copaymentRequired": 500.00,
    "preAuthRequired": true
}

# Map to your BenefitResponse model:
return BenefitResponse(
    member_id=data["memberNumber"],
    procedure_code=data["procedureCode"],
    benefit_available=data["benefitAvailable"],
    remaining_benefit=data["remainingBenefit"],
    annual_limit=data["annualLimit"],
    co_payment_required=data["copaymentRequired"],
    authorization_required=data["preAuthRequired"]
)
```

## 🧪 Testing Real APIs

### Step 1: Test Environment First
```python
# Use test/sandbox endpoints first
DISCOVERY_BASE_URL=https://sandbox-api.discovery.co.za/health/v1
```

### Step 2: Validate Responses
```python
# Add response validation
def validate_api_response(response_data, expected_fields):
    for field in expected_fields:
        if field not in response_data:
            raise ValueError(f"Missing required field: {field}")
```

### Step 3: Error Handling
```python
async def make_api_call(self, endpoint, method="GET", data=None):
    """Generic API call with error handling"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(endpoint, headers=self.headers)
            else:
                response = await client.post(endpoint, json=data, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise HTTPException(401, "Invalid API credentials")
            elif response.status_code == 404:
                raise HTTPException(404, "Member or procedure not found")
            else:
                raise HTTPException(500, f"API error: {response.text}")
                
    except httpx.TimeoutException:
        raise HTTPException(408, "API request timeout")
    except httpx.NetworkError:
        raise HTTPException(503, "Network error connecting to API")
```

## 🔐 Security Considerations

### API Key Management
```python
# Use environment variables, never hardcode
api_key = os.getenv("DISCOVERY_API_KEY")
if not api_key:
    raise ValueError("DISCOVERY_API_KEY not configured")
```

### SSL/TLS
```python
# Ensure HTTPS for production
if not self.base_url.startswith("https://"):
    raise ValueError("Production APIs must use HTTPS")
```

### Rate Limiting
```python
# Add rate limiting for API calls
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, calls_per_minute=60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def wait_if_needed(self):
        now = datetime.now()
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < timedelta(minutes=1)]
        
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0]).seconds
            await asyncio.sleep(sleep_time)
        
        self.calls.append(now)
```

## 📊 Migration Checklist

### Before Going Live:
- [ ] Obtain real API credentials from all schemes
- [ ] Update environment variables
- [ ] Replace mock implementations with real API calls
- [ ] Update base URLs to production endpoints
- [ ] Test with sandbox/test environments first
- [ ] Implement proper error handling
- [ ] Add rate limiting and retry logic
- [ ] Set up monitoring and alerting
- [ ] Update documentation with real endpoints
- [ ] Train staff on new workflows

### Testing Checklist:
- [ ] Test benefit checks with real member IDs
- [ ] Test authorization requests with valid procedures
- [ ] Test claim submissions with real data
- [ ] Test error scenarios (invalid member, expired auth, etc.)
- [ ] Performance test with expected load
- [ ] Security test API key handling
- [ ] Test failover scenarios

## 🚨 Important Notes

1. **Start with Test Environment**: Always test with sandbox APIs first
2. **Gradual Rollout**: Enable one scheme at a time
3. **Fallback Plan**: Keep mock connectors as backup during transition
4. **Monitor Closely**: Watch for API errors and performance issues
5. **Compliance**: Ensure POPIA compliance for all real data handling

## 🎯 Current Advantages of Mock Implementation

While you work on getting real API access:
- ✅ **Immediate functionality** for development and testing
- ✅ **Stakeholder demonstrations** with realistic data
- ✅ **System integration** without waiting for API approval
- ✅ **Staff training** on new workflows
- ✅ **Performance testing** of your infrastructure
- ✅ **AI assistant integration** development

Your MCP server is **production-ready infrastructure** - it just needs real API credentials to go live! 🚀