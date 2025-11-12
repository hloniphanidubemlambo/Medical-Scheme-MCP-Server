from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.models.claim import Claim, ClaimItem
from src.models.authorization import AuthorizationRequest
from src.config.registry import get_connector
from src.utils.logger import RequestLogger
from src.utils.auth import verify_token

router = APIRouter(prefix="/ris", tags=["Radiology Information System"])

class RISStudy(BaseModel):
    study_id: str = Field(..., description="Unique study identifier")
    patient_id: str = Field(..., description="Patient identifier")
    patient_name: str = Field(..., description="Patient full name")
    member_id: str = Field(..., description="Medical scheme member ID")
    scheme_name: str = Field(..., description="Medical scheme name")
    modality: str = Field(..., description="Imaging modality (CT, MRI, X-Ray, etc.)")
    procedure_code: str = Field(..., description="Medical procedure code")
    procedure_description: str = Field(..., description="Procedure description")
    study_date: datetime = Field(..., description="Date of study")
    referring_physician: str = Field(..., description="Referring physician name")
    provider_id: str = Field(..., description="Healthcare provider ID")
    estimated_cost: float = Field(..., description="Estimated cost of procedure")
    urgency: str = Field(default="routine", description="Study urgency level")
    clinical_indication: Optional[str] = Field(None, description="Clinical indication for study")

class RISClaimRequest(BaseModel):
    study: RISStudy
    auto_submit: bool = Field(default=True, description="Automatically submit claim after study completion")

class BillingData(BaseModel):
    patient_id: str
    patient_name: str
    member_id: str
    scheme_name: str
    provider_id: str
    services: List[dict] = Field(..., description="List of services provided")
    total_amount: float
    service_date: datetime

@router.post("/study/authorize")
async def authorize_ris_study(
    study: RISStudy,
    current_user: str = Depends(verify_token)
):
    """Request authorization for a radiology study"""
    try:
        connector = get_connector(study.scheme_name)
        
        # Create authorization request from RIS study data
        auth_request = AuthorizationRequest(
            member_id=study.member_id,
            provider_id=study.provider_id,
            procedure_code=study.procedure_code,
            patient_name=study.patient_name,
            requested_date=study.study_date,
            urgency=study.urgency,
            clinical_notes=study.clinical_indication
        )
        
        result = await connector.request_authorization(auth_request)
        
        RequestLogger.log_scheme_interaction(
            study.scheme_name, 
            "ris_authorization", 
            True, 
            {
                "study_id": study.study_id,
                "modality": study.modality,
                "authorization_id": result.authorization_id
            }
        )
        
        return {
            "study_id": study.study_id,
            "authorization": result,
            "message": "Authorization request processed successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        RequestLogger.log_scheme_interaction(study.scheme_name, "ris_authorization", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error processing RIS authorization: {str(e)}")

@router.post("/study/claim")
async def submit_ris_claim(
    claim_request: RISClaimRequest,
    current_user: str = Depends(verify_token)
):
    """Submit a claim for a completed radiology study"""
    try:
        study = claim_request.study
        connector = get_connector(study.scheme_name)
        
        # Create claim from RIS study data
        claim_item = ClaimItem(
            procedure_code=study.procedure_code,
            description=study.procedure_description,
            quantity=1,
            unit_price=study.estimated_cost,
            total_amount=study.estimated_cost
        )
        
        claim = Claim(
            member_id=study.member_id,
            provider_id=study.provider_id,
            patient_name=study.patient_name,
            date_of_service=study.study_date,
            claim_items=[claim_item],
            total_claim_amount=study.estimated_cost
        )
        
        result = await connector.submit_claim(claim)
        
        RequestLogger.log_scheme_interaction(
            study.scheme_name, 
            "ris_claim", 
            True, 
            {
                "study_id": study.study_id,
                "modality": study.modality,
                "claim_id": result.claim_id,
                "amount": study.estimated_cost
            }
        )
        
        return {
            "study_id": study.study_id,
            "claim": result,
            "message": "Claim submitted successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        RequestLogger.log_scheme_interaction(claim_request.study.scheme_name, "ris_claim", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error submitting RIS claim: {str(e)}")

@router.post("/billing/submit")
async def submit_billing_data(
    billing_data: BillingData,
    current_user: str = Depends(verify_token)
):
    """Submit billing data and automatically create claims"""
    try:
        connector = get_connector(billing_data.scheme_name)
        
        # Convert billing services to claim items
        claim_items = []
        total_amount = 0
        
        for service in billing_data.services:
            item = ClaimItem(
                procedure_code=service.get("code", "UNKNOWN"),
                description=service.get("description", "Medical Service"),
                quantity=service.get("quantity", 1),
                unit_price=service.get("unit_price", 0),
                total_amount=service.get("total_amount", 0)
            )
            claim_items.append(item)
            total_amount += item.total_amount
        
        # Create and submit claim
        claim = Claim(
            member_id=billing_data.member_id,
            provider_id=billing_data.provider_id,
            patient_name=billing_data.patient_name,
            date_of_service=billing_data.service_date,
            claim_items=claim_items,
            total_claim_amount=total_amount
        )
        
        result = await connector.submit_claim(claim)
        
        RequestLogger.log_scheme_interaction(
            billing_data.scheme_name, 
            "billing_claim", 
            True, 
            {
                "patient_id": billing_data.patient_id,
                "services_count": len(billing_data.services),
                "claim_id": result.claim_id,
                "amount": total_amount
            }
        )
        
        return {
            "patient_id": billing_data.patient_id,
            "claim": result,
            "services_processed": len(claim_items),
            "message": "Billing data processed and claim submitted successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        RequestLogger.log_scheme_interaction(billing_data.scheme_name, "billing_claim", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error processing billing data: {str(e)}")

@router.get("/study/{study_id}/status")
async def get_study_status(
    study_id: str,
    scheme_name: str,
    current_user: str = Depends(verify_token)
):
    """Get the status of authorizations and claims for a specific study"""
    try:
        # This would typically query a database for study records
        # For now, return a mock response
        return {
            "study_id": study_id,
            "scheme_name": scheme_name,
            "authorization_status": "approved",
            "claim_status": "processed",
            "last_updated": datetime.now(),
            "message": "Study processing completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting study status: {str(e)}")