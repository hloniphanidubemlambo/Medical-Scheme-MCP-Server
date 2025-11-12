from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime
from src.models.mcp_tools import (
    MCPTool, MCPToolResult, QuickAuthRequest, QuickBenefitCheck, 
    QuickClaimSubmission, PracticeWorkflow, PatientInfo, ProcedureInfo
)
from src.models.claim import Claim, ClaimItem
from src.models.authorization import AuthorizationRequest, BenefitCheck
from src.config.registry import get_connector
from src.utils.logger import RequestLogger
from src.utils.auth import verify_token

router = APIRouter(prefix="/mcp", tags=["MCP Tools for Medical Practices"])

# MCP Tool Definitions
MCP_TOOLS = [
    MCPTool(
        name="check_patient_benefits",
        description="Check a patient's medical scheme benefits for specific procedures. Perfect for verifying coverage before treatment.",
        inputSchema={
            "type": "object",
            "properties": {
                "patient_name": {"type": "string", "description": "Patient's full name"},
                "member_id": {"type": "string", "description": "Medical scheme member ID"},
                "scheme_name": {"type": "string", "enum": ["discovery", "gems", "medscheme"], "description": "Medical scheme name"},
                "procedure_codes": {"type": "array", "items": {"type": "string"}, "description": "List of procedure codes to check"}
            },
            "required": ["patient_name", "member_id", "scheme_name", "procedure_codes"]
        }
    ),
    MCPTool(
        name="request_procedure_authorization",
        description="Request pre-authorization for a medical procedure. Use this before performing procedures that require approval.",
        inputSchema={
            "type": "object",
            "properties": {
                "patient_name": {"type": "string", "description": "Patient's full name"},
                "member_id": {"type": "string", "description": "Medical scheme member ID"},
                "scheme_name": {"type": "string", "enum": ["discovery", "gems", "medscheme"], "description": "Medical scheme name"},
                "provider_id": {"type": "string", "description": "Healthcare provider ID"},
                "procedure_code": {"type": "string", "description": "Medical procedure code"},
                "procedure_name": {"type": "string", "description": "Procedure description"},
                "estimated_cost": {"type": "number", "description": "Estimated procedure cost"},
                "urgency": {"type": "string", "enum": ["routine", "urgent", "emergency"], "default": "routine"},
                "diagnosis_code": {"type": "string", "description": "ICD-10 diagnosis code (optional)"},
                "clinical_notes": {"type": "string", "description": "Additional clinical information (optional)"}
            },
            "required": ["patient_name", "member_id", "scheme_name", "provider_id", "procedure_code", "procedure_name", "estimated_cost"]
        }
    ),
    MCPTool(
        name="submit_medical_claim",
        description="Submit a medical claim for procedures that have been completed. Use this after providing treatment to get reimbursement.",
        inputSchema={
            "type": "object",
            "properties": {
                "patient_name": {"type": "string", "description": "Patient's full name"},
                "member_id": {"type": "string", "description": "Medical scheme member ID"},
                "scheme_name": {"type": "string", "enum": ["discovery", "gems", "medscheme"], "description": "Medical scheme name"},
                "provider_id": {"type": "string", "description": "Healthcare provider ID"},
                "service_date": {"type": "string", "format": "date", "description": "Date services were provided (YYYY-MM-DD)"},
                "procedures": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "procedure_code": {"type": "string", "description": "Medical procedure code"},
                            "procedure_name": {"type": "string", "description": "Procedure description"},
                            "quantity": {"type": "integer", "default": 1, "description": "Number of procedures"},
                            "unit_price": {"type": "number", "description": "Price per procedure"},
                            "total_amount": {"type": "number", "description": "Total amount for this procedure"}
                        },
                        "required": ["procedure_code", "procedure_name", "unit_price", "total_amount"]
                    }
                },
                "authorization_number": {"type": "string", "description": "Pre-authorization number (if applicable)"}
            },
            "required": ["patient_name", "member_id", "scheme_name", "provider_id", "service_date", "procedures"]
        }
    ),
    MCPTool(
        name="complete_patient_workflow",
        description="Complete workflow: check benefits, request authorization if needed, and optionally submit claim. Perfect for end-to-end patient processing.",
        inputSchema={
            "type": "object",
            "properties": {
                "patient_name": {"type": "string", "description": "Patient's full name"},
                "member_id": {"type": "string", "description": "Medical scheme member ID"},
                "scheme_name": {"type": "string", "enum": ["discovery", "gems", "medscheme"], "description": "Medical scheme name"},
                "provider_id": {"type": "string", "description": "Healthcare provider ID"},
                "practice_name": {"type": "string", "description": "Medical practice name"},
                "procedures": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "procedure_code": {"type": "string", "description": "Medical procedure code"},
                            "procedure_name": {"type": "string", "description": "Procedure description"},
                            "estimated_cost": {"type": "number", "description": "Estimated procedure cost"},
                            "urgency": {"type": "string", "enum": ["routine", "urgent", "emergency"], "default": "routine"}
                        },
                        "required": ["procedure_code", "procedure_name", "estimated_cost"]
                    }
                },
                "workflow_type": {"type": "string", "enum": ["check_only", "check_and_auth", "full_workflow"], "default": "check_and_auth", "description": "Type of workflow to execute"},
                "service_date": {"type": "string", "format": "date", "description": "Date services were/will be provided (YYYY-MM-DD)"}
            },
            "required": ["patient_name", "member_id", "scheme_name", "provider_id", "practice_name", "procedures"]
        }
    )
]

@router.get("/tools")
async def list_mcp_tools():
    """List all available MCP tools for medical practices"""
    return {
        "tools": MCP_TOOLS,
        "total_tools": len(MCP_TOOLS),
        "description": "MCP tools to help medical practices with common tasks like benefit checks, authorizations, and claim submissions"
    }

@router.post("/tools/check_patient_benefits")
async def check_patient_benefits(
    patient_name: str,
    member_id: str,
    scheme_name: str,
    procedure_codes: List[str],
    current_user: str = Depends(verify_token)
) -> MCPToolResult:
    """MCP Tool: Check patient benefits for multiple procedures"""
    try:
        connector = get_connector(scheme_name)
        results = []
        
        for procedure_code in procedure_codes:
            benefit_check = BenefitCheck(
                member_id=member_id,
                procedure_code=procedure_code
            )
            
            benefit_result = await connector.check_benefits(benefit_check)
            results.append({
                "procedure_code": procedure_code,
                "benefit_available": benefit_result.benefit_available,
                "remaining_benefit": benefit_result.remaining_benefit,
                "annual_limit": benefit_result.annual_limit,
                "co_payment_required": benefit_result.co_payment_required,
                "authorization_required": benefit_result.authorization_required
            })
        
        RequestLogger.log_scheme_interaction(
            scheme_name, "mcp_benefit_check", True, 
            {"patient": patient_name, "procedures_checked": len(procedure_codes)}
        )
        
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": f"✅ Benefit check completed for {patient_name} ({member_id})",
            }, {
                "type": "resource",
                "resource": {
                    "patient_name": patient_name,
                    "member_id": member_id,
                    "scheme_name": scheme_name,
                    "benefits": results,
                    "summary": {
                        "total_procedures_checked": len(procedure_codes),
                        "procedures_with_benefits": len([r for r in results if r["benefit_available"]]),
                        "procedures_requiring_auth": len([r for r in results if r["authorization_required"]])
                    }
                }
            }]
        )
        
    except Exception as e:
        RequestLogger.log_scheme_interaction(scheme_name, "mcp_benefit_check", False, {"error": str(e)})
        return MCPToolResult(
            content=[{"type": "text", "text": f"❌ Error checking benefits: {str(e)}"}],
            isError=True
        )

@router.post("/tools/request_procedure_authorization")
async def request_procedure_authorization(
    patient_name: str,
    member_id: str,
    scheme_name: str,
    provider_id: str,
    procedure_code: str,
    procedure_name: str,
    estimated_cost: float,
    urgency: str = "routine",
    diagnosis_code: str = None,
    clinical_notes: str = None,
    current_user: str = Depends(verify_token)
) -> MCPToolResult:
    """MCP Tool: Request procedure authorization"""
    try:
        connector = get_connector(scheme_name)
        
        auth_request = AuthorizationRequest(
            member_id=member_id,
            provider_id=provider_id,
            procedure_code=procedure_code,
            diagnosis_code=diagnosis_code,
            patient_name=patient_name,
            requested_date=datetime.now(),
            urgency=urgency,
            clinical_notes=clinical_notes
        )
        
        auth_result = await connector.request_authorization(auth_request)
        
        RequestLogger.log_scheme_interaction(
            scheme_name, "mcp_authorization", True,
            {"patient": patient_name, "procedure": procedure_code, "auth_id": auth_result.authorization_id}
        )
        
        status_emoji = "✅" if auth_result.status == "approved" else "⏳" if auth_result.status == "pending" else "❌"
        
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": f"{status_emoji} Authorization {auth_result.status} for {patient_name}",
            }, {
                "type": "resource",
                "resource": {
                    "patient_name": patient_name,
                    "procedure_name": procedure_name,
                    "authorization_id": auth_result.authorization_id,
                    "status": auth_result.status,
                    "authorization_number": auth_result.authorization_number,
                    "approved_amount": auth_result.approved_amount,
                    "valid_until": auth_result.valid_until.isoformat() if auth_result.valid_until else None,
                    "reference_number": auth_result.reference_number,
                    "estimated_cost": estimated_cost,
                    "scheme_name": scheme_name
                }
            }]
        )
        
    except Exception as e:
        RequestLogger.log_scheme_interaction(scheme_name, "mcp_authorization", False, {"error": str(e)})
        return MCPToolResult(
            content=[{"type": "text", "text": f"❌ Error requesting authorization: {str(e)}"}],
            isError=True
        )

@router.post("/tools/submit_medical_claim")
async def submit_medical_claim(
    patient_name: str,
    member_id: str,
    scheme_name: str,
    provider_id: str,
    service_date: str,
    procedures: List[Dict[str, Any]],
    authorization_number: str = None,
    current_user: str = Depends(verify_token)
) -> MCPToolResult:
    """MCP Tool: Submit medical claim"""
    try:
        connector = get_connector(scheme_name)
        
        # Convert procedures to claim items
        claim_items = []
        total_amount = 0
        
        for proc in procedures:
            item = ClaimItem(
                procedure_code=proc["procedure_code"],
                description=proc["procedure_name"],
                quantity=proc.get("quantity", 1),
                unit_price=proc["unit_price"],
                total_amount=proc["total_amount"]
            )
            claim_items.append(item)
            total_amount += item.total_amount
        
        # Create and submit claim
        claim = Claim(
            member_id=member_id,
            provider_id=provider_id,
            patient_name=patient_name,
            date_of_service=datetime.fromisoformat(service_date),
            claim_items=claim_items,
            total_claim_amount=total_amount,
            authorization_number=authorization_number
        )
        
        claim_result = await connector.submit_claim(claim)
        
        RequestLogger.log_scheme_interaction(
            scheme_name, "mcp_claim_submission", True,
            {"patient": patient_name, "claim_id": claim_result.claim_id, "amount": total_amount}
        )
        
        status_emoji = "✅" if claim_result.status == "approved" else "⏳" if claim_result.status == "pending" else "❌"
        
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": f"{status_emoji} Claim {claim_result.status} for {patient_name} - Amount: R{total_amount:,.2f}",
            }, {
                "type": "resource",
                "resource": {
                    "patient_name": patient_name,
                    "claim_id": claim_result.claim_id,
                    "status": claim_result.status,
                    "submitted_amount": total_amount,
                    "approved_amount": claim_result.approved_amount,
                    "reference_number": claim_result.reference_number,
                    "processed_date": claim_result.processed_date.isoformat(),
                    "procedures_count": len(procedures),
                    "scheme_name": scheme_name,
                    "authorization_number": authorization_number
                }
            }]
        )
        
    except Exception as e:
        RequestLogger.log_scheme_interaction(scheme_name, "mcp_claim_submission", False, {"error": str(e)})
        return MCPToolResult(
            content=[{"type": "text", "text": f"❌ Error submitting claim: {str(e)}"}],
            isError=True
        )

@router.post("/tools/complete_patient_workflow")
async def complete_patient_workflow(
    patient_name: str,
    member_id: str,
    scheme_name: str,
    provider_id: str,
    practice_name: str,
    procedures: List[Dict[str, Any]],
    workflow_type: str = "check_and_auth",
    service_date: str = None,
    current_user: str = Depends(verify_token)
) -> MCPToolResult:
    """MCP Tool: Complete patient workflow (benefits + auth + optional claim)"""
    try:
        connector = get_connector(scheme_name)
        workflow_results = []
        
        # Step 1: Check benefits for all procedures
        workflow_results.append("🔍 **Step 1: Checking Benefits**")
        benefit_results = []
        
        for proc in procedures:
            benefit_check = BenefitCheck(
                member_id=member_id,
                procedure_code=proc["procedure_code"]
            )
            benefit_result = await connector.check_benefits(benefit_check)
            benefit_results.append({
                "procedure": proc["procedure_name"],
                "code": proc["procedure_code"],
                "benefit_available": benefit_result.benefit_available,
                "authorization_required": benefit_result.authorization_required,
                "remaining_benefit": benefit_result.remaining_benefit
            })
        
        benefits_summary = f"✅ Benefits checked for {len(procedures)} procedures"
        workflow_results.append(benefits_summary)
        
        # Step 2: Request authorizations if needed and workflow includes it
        authorizations = []
        if workflow_type in ["check_and_auth", "full_workflow"]:
            workflow_results.append("\n🔐 **Step 2: Requesting Authorizations**")
            
            for i, proc in enumerate(procedures):
                if benefit_results[i]["authorization_required"]:
                    auth_request = AuthorizationRequest(
                        member_id=member_id,
                        provider_id=provider_id,
                        procedure_code=proc["procedure_code"],
                        patient_name=patient_name,
                        requested_date=datetime.now(),
                        urgency=proc.get("urgency", "routine")
                    )
                    
                    auth_result = await connector.request_authorization(auth_request)
                    authorizations.append({
                        "procedure": proc["procedure_name"],
                        "authorization_id": auth_result.authorization_id,
                        "status": auth_result.status,
                        "authorization_number": auth_result.authorization_number
                    })
                    workflow_results.append(f"  ✅ {proc['procedure_name']}: {auth_result.status}")
                else:
                    workflow_results.append(f"  ℹ️  {proc['procedure_name']}: No authorization required")
        
        # Step 3: Submit claim if full workflow and service date provided
        claim_result = None
        if workflow_type == "full_workflow" and service_date:
            workflow_results.append("\n📄 **Step 3: Submitting Claim**")
            
            claim_items = []
            total_amount = 0
            
            for proc in procedures:
                item = ClaimItem(
                    procedure_code=proc["procedure_code"],
                    description=proc["procedure_name"],
                    quantity=1,
                    unit_price=proc["estimated_cost"],
                    total_amount=proc["estimated_cost"]
                )
                claim_items.append(item)
                total_amount += item.total_amount
            
            claim = Claim(
                member_id=member_id,
                provider_id=provider_id,
                patient_name=patient_name,
                date_of_service=datetime.fromisoformat(service_date),
                claim_items=claim_items,
                total_claim_amount=total_amount
            )
            
            claim_result = await connector.submit_claim(claim)
            workflow_results.append(f"✅ Claim submitted: {claim_result.status} - R{total_amount:,.2f}")
        
        RequestLogger.log_scheme_interaction(
            scheme_name, "mcp_complete_workflow", True,
            {"patient": patient_name, "workflow_type": workflow_type, "procedures": len(procedures)}
        )
        
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": f"🏥 **Complete Workflow for {patient_name}**\n\n" + "\n".join(workflow_results),
            }, {
                "type": "resource",
                "resource": {
                    "patient_name": patient_name,
                    "practice_name": practice_name,
                    "workflow_type": workflow_type,
                    "scheme_name": scheme_name,
                    "benefits": benefit_results,
                    "authorizations": authorizations,
                    "claim": {
                        "claim_id": claim_result.claim_id if claim_result else None,
                        "status": claim_result.status if claim_result else None,
                        "amount": claim_result.approved_amount if claim_result else None
                    } if claim_result else None,
                    "summary": {
                        "procedures_processed": len(procedures),
                        "authorizations_requested": len(authorizations),
                        "claim_submitted": claim_result is not None
                    }
                }
            }]
        )
        
    except Exception as e:
        RequestLogger.log_scheme_interaction(scheme_name, "mcp_complete_workflow", False, {"error": str(e)})
        return MCPToolResult(
            content=[{"type": "text", "text": f"❌ Error in workflow: {str(e)}"}],
            isError=True
        )