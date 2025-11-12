from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.models.claim import Claim, ClaimResponse
from src.models.authorization import AuthorizationRequest, AuthorizationResponse, BenefitCheck, BenefitResponse
from src.config.registry import get_connector, get_available_schemes
from src.utils.logger import RequestLogger
from src.utils.auth import verify_token

router = APIRouter(prefix="/scheme", tags=["Medical Schemes"])

@router.get("/available")
async def list_available_schemes():
    """Get list of available medical schemes"""
    schemes = get_available_schemes()
    return {"schemes": schemes, "count": len(schemes)}

@router.post("/{scheme_name}/benefits/check")
async def check_member_benefits(
    scheme_name: str, 
    benefit_check: BenefitCheck,
    current_user: str = Depends(verify_token)
):
    """Check member benefits for a specific procedure"""
    try:
        connector = get_connector(scheme_name)
        result = await connector.check_benefits(benefit_check)
        
        RequestLogger.log_scheme_interaction(
            scheme_name, 
            "benefit_check", 
            True, 
            {"member_id": benefit_check.member_id, "procedure_code": benefit_check.procedure_code}
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        RequestLogger.log_scheme_interaction(scheme_name, "benefit_check", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error checking benefits: {str(e)}")

@router.post("/{scheme_name}/authorization/request")
async def request_authorization(
    scheme_name: str, 
    auth_request: AuthorizationRequest,
    current_user: str = Depends(verify_token)
):
    """Request pre-authorization for a medical procedure"""
    try:
        connector = get_connector(scheme_name)
        result = await connector.request_authorization(auth_request)
        
        RequestLogger.log_scheme_interaction(
            scheme_name, 
            "authorization_request", 
            True, 
            {
                "member_id": auth_request.member_id, 
                "procedure_code": auth_request.procedure_code,
                "authorization_id": result.authorization_id
            }
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        RequestLogger.log_scheme_interaction(scheme_name, "authorization_request", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error requesting authorization: {str(e)}")

@router.get("/{scheme_name}/authorization/{authorization_id}")
async def get_authorization_status(
    scheme_name: str, 
    authorization_id: str,
    current_user: str = Depends(verify_token)
):
    """Get the status of an authorization request"""
    try:
        connector = get_connector(scheme_name)
        result = await connector.get_authorization_status(authorization_id)
        
        RequestLogger.log_scheme_interaction(
            scheme_name, 
            "authorization_status", 
            True, 
            {"authorization_id": authorization_id}
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        RequestLogger.log_scheme_interaction(scheme_name, "authorization_status", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error getting authorization status: {str(e)}")

@router.post("/{scheme_name}/claim/submit")
async def submit_claim(
    scheme_name: str, 
    claim: Claim,
    current_user: str = Depends(verify_token)
):
    """Submit a medical claim for processing"""
    try:
        connector = get_connector(scheme_name)
        result = await connector.submit_claim(claim)
        
        RequestLogger.log_scheme_interaction(
            scheme_name, 
            "claim_submission", 
            True, 
            {
                "member_id": claim.member_id, 
                "total_amount": claim.total_claim_amount,
                "claim_id": result.claim_id
            }
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        RequestLogger.log_scheme_interaction(scheme_name, "claim_submission", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error submitting claim: {str(e)}")

@router.get("/{scheme_name}/claim/{claim_id}")
async def get_claim_status(
    scheme_name: str, 
    claim_id: str,
    current_user: str = Depends(verify_token)
):
    """Get the status of a submitted claim"""
    try:
        connector = get_connector(scheme_name)
        result = await connector.get_claim_status(claim_id)
        
        RequestLogger.log_scheme_interaction(
            scheme_name, 
            "claim_status", 
            True, 
            {"claim_id": claim_id}
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        RequestLogger.log_scheme_interaction(scheme_name, "claim_status", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error getting claim status: {str(e)}")