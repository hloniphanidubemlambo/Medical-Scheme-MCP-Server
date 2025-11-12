# 🏥 MCP Tools Usage Examples

## Overview
These examples show how medical practices can use the MCP tools through AI assistants or direct API calls.

## 🔐 Authentication First

Before using any tools, get an authentication token:

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```

Use the returned token in all subsequent requests:
```bash
Authorization: Bearer <your-token>
```

## 🔍 1. Check Patient Benefits

**Scenario:** Patient arrives for consultation, you want to check what's covered.

### AI Assistant Prompt:
```
"Check benefits for patient Sarah Johnson with member ID DISC789012 on Discovery Health for procedures CONS001, BLOOD001, and MRI001"
```

### Direct API Call:
```bash
curl -X POST "http://localhost:8000/mcp/tools/check_patient_benefits" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Sarah Johnson",
    "member_id": "DISC789012", 
    "scheme_name": "discovery",
    "procedure_codes": ["CONS001", "BLOOD001", "MRI001"]
  }'
```

### Expected Response:
```json
{
  "content": [
    {
      "type": "text",
      "text": "✅ Benefit check completed for Sarah Johnson (DISC789012)"
    },
    {
      "type": "resource",
      "resource": {
        "patient_name": "Sarah Johnson",
        "benefits": [
          {
            "procedure_code": "CONS001",
            "benefit_available": true,
            "remaining_benefit": 15000.00,
            "authorization_required": false
          },
          {
            "procedure_code": "MRI001", 
            "benefit_available": true,
            "remaining_benefit": 15000.00,
            "authorization_required": true
          }
        ]
      }
    }
  ]
}
```

## 🔐 2. Request Procedure Authorization

**Scenario:** Patient needs MRI, which requires pre-authorization.

### AI Assistant Prompt:
```
"Request authorization for patient Sarah Johnson (DISC789012) on Discovery for Brain MRI with contrast, procedure code MRI001, estimated cost R3500, routine urgency"
```

### Direct API Call:
```bash
curl -X POST "http://localhost:8000/mcp/tools/request_procedure_authorization" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Sarah Johnson",
    "member_id": "DISC789012",
    "scheme_name": "discovery", 
    "provider_id": "PROV001",
    "procedure_code": "MRI001",
    "procedure_name": "Brain MRI with contrast",
    "estimated_cost": 3500.00,
    "urgency": "routine",
    "diagnosis_code": "G93.1",
    "clinical_notes": "Patient experiencing persistent headaches"
  }'
```

### Expected Response:
```json
{
  "content": [
    {
      "type": "text", 
      "text": "✅ Authorization approved for Sarah Johnson"
    },
    {
      "type": "resource",
      "resource": {
        "authorization_id": "DISC-AUTH-20241022143022",
        "status": "approved",
        "authorization_number": "AUTH20241022143022",
        "approved_amount": 5000.00,
        "valid_until": "2024-11-21T14:30:22"
      }
    }
  ]
}
```

## 📄 3. Submit Medical Claim

**Scenario:** Patient consultation and tests completed, submit claim for payment.

### AI Assistant Prompt:
```
"Submit claim for patient Sarah Johnson (DISC789012) on Discovery for consultation and blood work completed today, total amount R680"
```

### Direct API Call:
```bash
curl -X POST "http://localhost:8000/mcp/tools/submit_medical_claim" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Sarah Johnson",
    "member_id": "DISC789012",
    "scheme_name": "discovery",
    "provider_id": "PROV001", 
    "service_date": "2024-10-22",
    "procedures": [
      {
        "procedure_code": "CONS001",
        "procedure_name": "General Consultation",
        "quantity": 1,
        "unit_price": 500.00,
        "total_amount": 500.00
      },
      {
        "procedure_code": "BLOOD001", 
        "procedure_name": "Full Blood Count",
        "quantity": 1,
        "unit_price": 180.00,
        "total_amount": 180.00
      }
    ]
  }'
```

## 🔄 4. Complete Patient Workflow

**Scenario:** Handle everything for a new patient in one go.

### AI Assistant Prompt:
```
"Complete full workflow for new patient Mike Chen (GEMS456789) on GEMS: check benefits, get authorization, and prepare for claim submission for consultation, ECG, and blood work"
```

### Direct API Call:
```bash
curl -X POST "http://localhost:8000/mcp/tools/complete_patient_workflow" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Mike Chen",
    "member_id": "GEMS456789",
    "scheme_name": "gems",
    "provider_id": "PROV001",
    "practice_name": "City Medical Centre",
    "procedures": [
      {
        "procedure_code": "CONS001",
        "procedure_name": "General Consultation", 
        "estimated_cost": 500.00,
        "urgency": "routine"
      },
      {
        "procedure_code": "ECG001",
        "procedure_name": "Electrocardiogram",
        "estimated_cost": 250.00,
        "urgency": "routine"
      }
    ],
    "workflow_type": "check_and_auth",
    "service_date": "2024-10-22"
  }'
```

## 🤖 AI Assistant Integration Examples

### ChatGPT/Claude Prompts:

**Quick Benefit Check:**
```
"I have a patient John Smith with Discovery member ID DISC123456. Can you check his benefits for a general consultation (CONS001) and chest X-ray (XRAY001)?"
```

**Authorization Request:**
```
"Patient needs urgent CT scan. Details: Mary Wilson, GEMS member ID GEMS789012, procedure CT001 (CT Scan Chest), estimated cost R2200, urgent priority due to chest pain. Please request authorization."
```

**End-to-End Processing:**
```
"New patient visit: David Brown, Medscheme member MED555666. Needs consultation, blood work, and ECG. Please check benefits, get any needed authorizations, and prepare claim for today's date."
```

## 🏥 Practice Management System Integration

### Webhook Integration:
```javascript
// When patient checks in
async function processPatientCheckIn(patientData) {
  const response = await fetch('/mcp/tools/check_patient_benefits', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      patient_name: patientData.name,
      member_id: patientData.memberId,
      scheme_name: patientData.scheme,
      procedure_codes: ['CONS001', 'BLOOD001'] // Default procedures
    })
  });
  
  const result = await response.json();
  // Update patient record with benefit information
  updatePatientBenefits(patientData.id, result);
}
```

### Automated Workflows:
```javascript
// Complete patient processing
async function processPatientVisit(visitData) {
  const workflowResponse = await fetch('/mcp/tools/complete_patient_workflow', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      ...visitData,
      workflow_type: 'full_workflow'
    })
  });
  
  return await workflowResponse.json();
}
```

## 📊 Common Use Cases

### 1. **Morning Patient Prep**
Check benefits for all scheduled patients:
```bash
# Batch check for multiple patients
for patient in scheduled_patients:
  check_patient_benefits(patient.name, patient.member_id, patient.scheme, common_procedures)
```

### 2. **Radiology Referrals**
Streamline imaging authorizations:
```bash
# Request auth for imaging
request_procedure_authorization(
  patient_name="Jane Doe",
  procedure_code="MRI001", 
  urgency="routine",
  clinical_notes="Chronic headaches, rule out structural abnormality"
)
```

### 3. **End-of-Day Claims**
Submit all completed procedures:
```bash
# Batch claim submission
for completed_visit in today_visits:
  submit_medical_claim(completed_visit.patient, completed_visit.procedures, today)
```

### 4. **Emergency Procedures**
Fast-track urgent authorizations:
```bash
# Emergency authorization
request_procedure_authorization(
  urgency="emergency",
  clinical_notes="Acute chest pain, suspected MI"
)
```

## 🔧 Error Handling

### Common Errors and Solutions:

**Authentication Error:**
```json
{"detail": "Could not validate credentials"}
```
**Solution:** Get a new token from `/auth/login`

**Scheme Not Supported:**
```json
{"detail": "Scheme 'unknown' not supported"}
```
**Solution:** Use 'discovery', 'gems', or 'medscheme'

**Invalid Member ID:**
```json
{"detail": "Member not found"}
```
**Solution:** Verify member ID format and scheme

## 📈 Best Practices

1. **Always check benefits first** before expensive procedures
2. **Request authorization early** for procedures that require it
3. **Submit claims promptly** after service completion
4. **Use batch processing** for multiple patients
5. **Handle errors gracefully** with retry logic
6. **Log all interactions** for audit purposes

## 🎯 Integration Tips

- **Cache benefit information** to avoid repeated API calls
- **Set up webhooks** for real-time status updates
- **Use workflow templates** for common scenarios
- **Implement retry logic** for network failures
- **Monitor API usage** and rate limits