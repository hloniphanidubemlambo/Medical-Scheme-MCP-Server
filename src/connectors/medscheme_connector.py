import httpx
from datetime import datetime, timedelta
from src.connectors.base_connector import BaseSchemeConnector
from src.models.claim import Claim, ClaimResponse
from src.models.authorization import AuthorizationRequest, AuthorizationResponse, BenefitCheck, BenefitResponse

class MedschemeConnector(BaseSchemeConnector):
    """Medscheme Medical Scheme connector"""
    
    def __init__(self, api_key: str):
        # Mock URL - replace with real Medscheme API endpoint when available
        super().__init__(api_key, "https://api.medscheme.co.za/health/v1")
    
    async def check_benefits(self, benefit_check: BenefitCheck) -> BenefitResponse:
        """Check member benefits - currently returns mock data"""
        # Mock implementation with Medscheme-specific logic
        return BenefitResponse(
            member_id=benefit_check.member_id,
            procedure_code=benefit_check.procedure_code,
            benefit_available=True,
            remaining_benefit=18000.00,
            annual_limit=60000.00,
            co_payment_required=750.00,
            authorization_required=benefit_check.procedure_code.startswith(("MRI", "CT", "SURG"))
        )
    
    async def request_authorization(self, auth_request: AuthorizationRequest) -> AuthorizationResponse:
        """Request pre-authorization - currently returns mock data"""
        # Mock implementation with Medscheme workflow
        return AuthorizationResponse(
            authorization_id=f"MED-AUTH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="approved",
            authorization_number=f"MED{datetime.now().strftime('%Y%m%d%H%M%S')}",
            approved_amount=6000.00,
            valid_until=datetime.now() + timedelta(days=35),
            reference_number=f"MED-REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
    
    async def submit_claim(self, claim: Claim) -> ClaimResponse:
        """Submit claim - currently returns mock data"""
        # Mock implementation with Medscheme processing
        return ClaimResponse(
            claim_id=f"MED-CLAIM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="approved",
            approved_amount=claim.total_claim_amount * 0.75,  # 75% coverage
            reference_number=f"MED-REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            processed_date=datetime.now()
        )
    
    async def get_claim_status(self, claim_id: str) -> ClaimResponse:
        """Get claim status - currently returns mock data"""
        return ClaimResponse(
            claim_id=claim_id,
            status="processed",
            approved_amount=3750.00,
            reference_number=f"MED-REF-{claim_id}",
            processed_date=datetime.now()
        )
    
    async def get_authorization_status(self, authorization_id: str) -> AuthorizationResponse:
        """Get authorization status - currently returns mock data"""
        return AuthorizationResponse(
            authorization_id=authorization_id,
            status="approved",
            authorization_number=f"MED{authorization_id}",
            approved_amount=6000.00,
            valid_until=datetime.now() + timedelta(days=30),
            reference_number=f"MED-REF-{authorization_id}"
        )