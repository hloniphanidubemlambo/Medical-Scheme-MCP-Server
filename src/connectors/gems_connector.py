import httpx
from datetime import datetime, timedelta
from src.connectors.base_connector import BaseSchemeConnector
from src.models.claim import Claim, ClaimResponse
from src.models.authorization import AuthorizationRequest, AuthorizationResponse, BenefitCheck, BenefitResponse

class GEMSConnector(BaseSchemeConnector):
    """Government Employees Medical Scheme (GEMS) connector"""
    
    def __init__(self, api_key: str):
        # Mock URL - GEMS typically requires intermediary access
        super().__init__(api_key, "https://api.gems.gov.za/medical/v1")
    
    async def check_benefits(self, benefit_check: BenefitCheck) -> BenefitResponse:
        """Check member benefits - currently returns mock data"""
        # Mock implementation with GEMS-specific logic
        return BenefitResponse(
            member_id=benefit_check.member_id,
            procedure_code=benefit_check.procedure_code,
            benefit_available=True,
            remaining_benefit=25000.00,  # GEMS typically has higher limits
            annual_limit=75000.00,
            co_payment_required=200.00,  # Lower co-payments for government employees
            authorization_required=benefit_check.procedure_code.startswith(("MRI", "CT", "PET"))
        )
    
    async def request_authorization(self, auth_request: AuthorizationRequest) -> AuthorizationResponse:
        """Request pre-authorization - currently returns mock data"""
        # Mock implementation with GEMS workflow
        status = "approved" if auth_request.urgency == "emergency" else "pending"
        
        return AuthorizationResponse(
            authorization_id=f"GEMS-AUTH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status=status,
            authorization_number=f"GEMS{datetime.now().strftime('%Y%m%d%H%M%S')}" if status == "approved" else None,
            approved_amount=7500.00 if status == "approved" else None,
            valid_until=datetime.now() + timedelta(days=45) if status == "approved" else None,
            reference_number=f"GEMS-REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
    
    async def submit_claim(self, claim: Claim) -> ClaimResponse:
        """Submit claim - currently returns mock data"""
        # Mock implementation with GEMS processing
        coverage_rate = 0.9 if claim.total_claim_amount < 5000 else 0.85  # Higher coverage for smaller claims
        
        return ClaimResponse(
            claim_id=f"GEMS-CLAIM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="approved",
            approved_amount=claim.total_claim_amount * coverage_rate,
            reference_number=f"GEMS-REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            processed_date=datetime.now()
        )
    
    async def get_claim_status(self, claim_id: str) -> ClaimResponse:
        """Get claim status - currently returns mock data"""
        return ClaimResponse(
            claim_id=claim_id,
            status="processed",
            approved_amount=6750.00,
            reference_number=f"GEMS-REF-{claim_id}",
            processed_date=datetime.now()
        )
    
    async def get_authorization_status(self, authorization_id: str) -> AuthorizationResponse:
        """Get authorization status - currently returns mock data"""
        return AuthorizationResponse(
            authorization_id=authorization_id,
            status="approved",
            authorization_number=f"GEMS{authorization_id}",
            approved_amount=7500.00,
            valid_until=datetime.now() + timedelta(days=40),
            reference_number=f"GEMS-REF-{authorization_id}"
        )