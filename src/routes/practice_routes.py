from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from src.models.mcp_tools import PracticeInfo, PatientInfo, ProcedureInfo
from src.config.registry import get_available_schemes
from src.utils.auth import verify_token
from src.utils.logger import RequestLogger

router = APIRouter(prefix="/practice", tags=["Medical Practice Tools"])

# Sample data for demonstration
SAMPLE_PROCEDURES = [
    {"code": "CONS001", "name": "General Consultation", "typical_cost": 500.00},
    {"code": "MRI001", "name": "Brain MRI with Contrast", "typical_cost": 3500.00},
    {"code": "CT001", "name": "CT Scan Chest", "typical_cost": 2200.00},
    {"code": "XRAY001", "name": "Chest X-Ray", "typical_cost": 350.00},
    {"code": "BLOOD001", "name": "Full Blood Count", "typical_cost": 180.00},
    {"code": "ECG001", "name": "Electrocardiogram", "typical_cost": 250.00},
    {"code": "ULTRA001", "name": "Abdominal Ultrasound", "typical_cost": 800.00},
    {"code": "SURG001", "name": "Minor Surgery", "typical_cost": 1500.00}
]

@router.get("/dashboard", response_class=HTMLResponse)
async def practice_dashboard():
    """Simple HTML dashboard for medical practices"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medical Practice MCP Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #2c3e50; margin-bottom: 30px; }
            .tool-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .tool-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }
            .tool-card h3 { color: #2c3e50; margin-top: 0; }
            .tool-card p { color: #7f8c8d; margin-bottom: 15px; }
            .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
            .btn:hover { background: #2980b9; }
            .quick-form { background: #ecf0f1; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #2c3e50; }
            .form-group input, .form-group select { width: 100%; padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; }
            .schemes { display: flex; gap: 10px; margin: 20px 0; }
            .scheme-badge { background: #27ae60; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; }
            .api-info { background: #e8f5e8; padding: 15px; border-radius: 8px; margin-top: 20px; }
            .endpoint { font-family: monospace; background: #34495e; color: #ecf0f1; padding: 5px 10px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 Medical Practice MCP Dashboard</h1>
                <p>AI-Powered Medical Scheme Integration Tools</p>
                <div class="schemes">
                    <span class="scheme-badge">Discovery Health</span>
                    <span class="scheme-badge">GEMS</span>
                    <span class="scheme-badge">Medscheme</span>
                    <span class="scheme-badge" style="background: #e74c3c;">HAPI FHIR</span>
                </div>
            </div>

            <div class="tool-grid">
                <div class="tool-card">
                    <h3>🔍 Check Patient Benefits</h3>
                    <p>Quickly verify what procedures are covered for a patient before treatment.</p>
                    <p><strong>Use when:</strong> Patient arrives for consultation</p>
                    <a href="/docs#/MCP%20Tools%20for%20Medical%20Practices/check_patient_benefits_mcp_tools_check_patient_benefits_post" class="btn">Try Tool</a>
                </div>

                <div class="tool-card">
                    <h3>🔐 Request Authorization</h3>
                    <p>Get pre-approval for procedures that require medical scheme authorization.</p>
                    <p><strong>Use when:</strong> Planning MRI, CT scans, surgery, or specialist procedures</p>
                    <a href="/docs#/MCP%20Tools%20for%20Medical%20Practices/request_procedure_authorization_mcp_tools_request_procedure_authorization_post" class="btn">Try Tool</a>
                </div>

                <div class="tool-card">
                    <h3>📄 Submit Claims</h3>
                    <p>Submit medical claims for completed procedures to get reimbursed.</p>
                    <p><strong>Use when:</strong> Treatment is complete and you need payment</p>
                    <a href="/docs#/MCP%20Tools%20for%20Medical%20Practices/submit_medical_claim_mcp_tools_submit_medical_claim_post" class="btn">Try Tool</a>
                </div>

                <div class="tool-card">
                    <h3>🔄 Complete Workflow</h3>
                    <p>End-to-end patient processing: benefits → authorization → claims in one go.</p>
                    <p><strong>Use when:</strong> You want to handle everything automatically</p>
                    <a href="/docs#/MCP%20Tools%20for%20Medical%20Practices/complete_patient_workflow_mcp_tools_complete_patient_workflow_post" class="btn">Try Tool</a>
                </div>

                <div class="tool-card" style="border-left-color: #e74c3c;">
                    <h3>🌐 FHIR Integration</h3>
                    <p>Real healthcare data from HAPI FHIR server and local OpenEMR system.</p>
                    <p><strong>Use when:</strong> You want to test with real FHIR-compliant data</p>
                    <a href="/docs#/FHIR%20Integration" class="btn">Try FHIR</a>
                </div>
            </div>

            <div class="quick-form">
                <h3>🚀 Quick Test Form</h3>
                <p>Test the tools with sample data (requires authentication token)</p>
                
                <div class="form-group">
                    <label>Patient Name:</label>
                    <input type="text" id="patientName" value="John Doe" placeholder="Enter patient name">
                </div>
                
                <div class="form-group">
                    <label>Member ID:</label>
                    <input type="text" id="memberId" value="DISC123456" placeholder="Enter member ID">
                </div>
                
                <div class="form-group">
                    <label>Medical Scheme:</label>
                    <select id="scheme">
                        <option value="discovery">Discovery Health</option>
                        <option value="gems">GEMS</option>
                        <option value="medscheme">Medscheme</option>
                        <option value="fhir">HAPI FHIR (Real Data)</option>
                    </select>
                </div>
                
                <button class="btn" onclick="testBenefitCheck()">Test Benefit Check</button>
            </div>

            <div class="api-info">
                <h3>📚 For Developers & AI Systems</h3>
                <p>These MCP tools can be used by AI assistants, practice management systems, or custom applications:</p>
                <ul>
                    <li><strong>List Tools:</strong> <span class="endpoint">GET /mcp/tools</span></li>
                    <li><strong>Interactive Docs:</strong> <span class="endpoint">GET /docs</span></li>
                    <li><strong>Authentication:</strong> <span class="endpoint">POST /auth/login</span></li>
                </ul>
                <p><strong>Sample AI Prompt:</strong> "Check benefits for patient John Doe (member ID: DISC123456) on Discovery for procedures MRI001 and CONS001"</p>
            </div>
        </div>

        <script>
            async function testBenefitCheck() {
                const patientName = document.getElementById('patientName').value;
                const memberId = document.getElementById('memberId').value;
                const scheme = document.getElementById('scheme').value;
                
                alert(`Testing benefit check for ${patientName} (${memberId}) on ${scheme}\\n\\nThis would check benefits for common procedures. In a real implementation, you would need an authentication token.`);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/procedures")
async def get_common_procedures():
    """Get list of common medical procedures with codes and typical costs"""
    return {
        "procedures": SAMPLE_PROCEDURES,
        "total": len(SAMPLE_PROCEDURES),
        "note": "These are sample procedures with typical costs. Actual costs may vary by provider and location."
    }

@router.get("/schemes")
async def get_supported_schemes():
    """Get list of supported medical schemes with details"""
    schemes = get_available_schemes()
    scheme_details = {
        "discovery": {
            "name": "Discovery Health",
            "type": "Private Medical Scheme",
            "coverage": "Comprehensive medical coverage",
            "features": ["Benefit checks", "Pre-authorizations", "Claims processing", "Real-time status"]
        },
        "gems": {
            "name": "Government Employees Medical Scheme",
            "type": "Government Medical Scheme", 
            "coverage": "Government employee medical benefits",
            "features": ["Higher benefit limits", "Lower co-payments", "Extended authorization validity"]
        },
        "medscheme": {
            "name": "Medscheme",
            "type": "Private Medical Scheme Administrator",
            "coverage": "Various medical scheme options",
            "features": ["Flexible benefit structures", "Multiple plan options", "Corporate schemes"]
        }
    }
    
    return {
        "supported_schemes": [
            {
                "code": scheme,
                "details": scheme_details.get(scheme, {"name": scheme.title(), "type": "Medical Scheme"})
            }
            for scheme in schemes
        ],
        "total": len(schemes)
    }

@router.post("/quick-benefit-check")
async def quick_benefit_check(
    patient_name: str,
    member_id: str,
    scheme_name: str,
    procedure_codes: Optional[List[str]] = None,
    current_user: str = Depends(verify_token)
):
    """Quick benefit check for common scenarios"""
    if not procedure_codes:
        # Default to common procedures
        procedure_codes = ["CONS001", "BLOOD001", "XRAY001"]
    
    try:
        from src.config.registry import get_connector
        from src.models.authorization import BenefitCheck
        
        connector = get_connector(scheme_name)
        results = []
        
        for procedure_code in procedure_codes:
            benefit_check = BenefitCheck(
                member_id=member_id,
                procedure_code=procedure_code
            )
            
            benefit_result = await connector.check_benefits(benefit_check)
            
            # Find procedure name from sample data
            proc_info = next((p for p in SAMPLE_PROCEDURES if p["code"] == procedure_code), None)
            procedure_name = proc_info["name"] if proc_info else procedure_code
            
            results.append({
                "procedure_code": procedure_code,
                "procedure_name": procedure_name,
                "benefit_available": benefit_result.benefit_available,
                "remaining_benefit": benefit_result.remaining_benefit,
                "authorization_required": benefit_result.authorization_required,
                "co_payment": benefit_result.co_payment_required
            })
        
        RequestLogger.log_scheme_interaction(
            scheme_name, "quick_benefit_check", True,
            {"patient": patient_name, "procedures": len(procedure_codes)}
        )
        
        return {
            "patient_name": patient_name,
            "member_id": member_id,
            "scheme_name": scheme_name,
            "benefits": results,
            "summary": {
                "total_checked": len(results),
                "with_benefits": len([r for r in results if r["benefit_available"]]),
                "requiring_auth": len([r for r in results if r["authorization_required"]]),
                "estimated_total_remaining": sum(r["remaining_benefit"] or 0 for r in results)
            },
            "recommendations": [
                "✅ Proceed with procedures that have benefits available",
                "🔐 Request authorization for procedures that require it",
                "💰 Inform patient of any co-payment requirements"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking benefits: {str(e)}")

@router.get("/workflow-templates")
async def get_workflow_templates():
    """Get pre-defined workflow templates for common practice scenarios"""
    templates = [
        {
            "name": "New Patient Consultation",
            "description": "Complete workflow for new patient visit",
            "steps": [
                "Check benefits for consultation and basic tests",
                "Request authorization if needed",
                "Submit claim after consultation"
            ],
            "typical_procedures": ["CONS001", "BLOOD001", "ECG001"],
            "workflow_type": "full_workflow"
        },
        {
            "name": "Radiology Referral",
            "description": "Process radiology referrals with authorization",
            "steps": [
                "Check imaging benefits",
                "Request pre-authorization",
                "Schedule procedure once approved"
            ],
            "typical_procedures": ["MRI001", "CT001", "ULTRA001"],
            "workflow_type": "check_and_auth"
        },
        {
            "name": "Routine Follow-up",
            "description": "Standard follow-up visit processing",
            "steps": [
                "Check consultation benefits",
                "Submit claim immediately"
            ],
            "typical_procedures": ["CONS001"],
            "workflow_type": "check_and_claim"
        },
        {
            "name": "Emergency Procedure",
            "description": "Fast-track emergency authorization",
            "steps": [
                "Request urgent authorization",
                "Proceed with treatment",
                "Submit claim with authorization"
            ],
            "typical_procedures": ["SURG001", "CT001"],
            "workflow_type": "urgent_auth",
            "urgency": "emergency"
        }
    ]
    
    return {
        "templates": templates,
        "total": len(templates),
        "usage": "Select a template that matches your scenario and customize the procedures as needed"
    }