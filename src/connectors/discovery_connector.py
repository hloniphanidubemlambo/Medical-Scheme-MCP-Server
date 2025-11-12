import httpx
from datetime import datetime, timedelta
from src.connectors.base_connector import BaseSchemeConnector
from src.models.claim import Claim, ClaimResponse
from src.models.authorization import AuthorizationRequest, AuthorizationResponse, BenefitCheck, BenefitResponse

class DiscoveryConnector(BaseSchemeConnector):
    """Discovery Health Medical Scheme connector"""
    
    def __init__(self, api_key: str):
        # Mock URL - replace with real Discovery API endpoint when available
        super().__init__(api_key, "https://api.discovery.co.za/health/v1")
    
    async def check_benefits(self, benefit_check: BenefitCheck) -> BenefitResponse:
        """Check member benefits - currently returns mock data"""
        # Mock implementation - replace with real API call
        return BenefitResponse(
            member_id=benefit_check.member_id,
            procedure_code=benefit_check.procedure_code,
            benefit_available=True,
            remaining_benefit=15000.00,
            annual_limit=50000.00,
            co_payment_required=500.00,
            authorization_required=benefit_check.procedure_code.startswith("MRI")
        )
        
        # Real implementation would be:
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"{self.base_url}/benefits/{benefit_check.member_id}/{benefit_check.procedure_code}",
        #         headers=self.headers
        #     )
        #     data = response.json()
        #     return BenefitResponse(**data)
    
    async def request_authorization(self, auth_request: AuthorizationRequest) -> AuthorizationResponse:
        """Request pre-authorization - currently returns mock data"""
        # Mock implementation
        return AuthorizationResponse(
            authorization_id=f"DISC-AUTH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="approved",
            authorization_number=f"AUTH{datetime.now().strftime('%Y%m%d%H%M%S')}",
            approved_amount=5000.00,
            valid_until=datetime.now() + timedelta(days=30),
            reference_number=f"DISC-REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        # Real implementation would be:
        # payload = {
        #     "memberId": auth_request.member_id,
        #     "providerId": auth_request.provider_id,
        #     "procedureCode": auth_request.procedure_code,
        #     "diagnosisCode": auth_request.diagnosis_code,
        #     "patientName": auth_request.patient_name,
        #     "requestedDate": auth_request.requested_date.isoformat(),
        #     "urgency": auth_request.urgency,
        #     "clinicalNotes": auth_request.clinical_notes
        # }
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"{self.base_url}/authorizations",
        #         json=payload,
        #         headers=self.headers
        #     )
        #     data = response.json()
        #     return AuthorizationResponse(**data)
    
    async def submit_claim(self, claim: Claim) -> ClaimResponse:
        """Submit claim - currently returns mock data"""
        # Mock implementation
        return ClaimResponse(
            claim_id=f"DISC-CLAIM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="approved",
            approved_amount=claim.total_claim_amount * 0.8,  # 80% coverage
            reference_number=f"DISC-REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            processed_date=datetime.now()
        )
        
        # Real implementation would be:
        # payload = claim.dict()
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"{self.base_url}/claims",
        #         json=payload,
        #         headers=self.headers
        #     )
        #     data = response.json()
        #     return ClaimResponse(**data)
    
    async def get_claim_status(self, claim_id: str) -> ClaimResponse:
        """Get claim status - currently returns mock data"""
        return ClaimResponse(
            claim_id=claim_id,
            status="processed",
            approved_amount=4000.00,
            reference_number=f"DISC-REF-{claim_id}",
            processed_date=datetime.now()
        )
    
    async def get_authorization_status(self, authorization_id: str) -> AuthorizationResponse:
        """Get authorization status - currently returns mock data"""
        return AuthorizationResponse(
            authorization_id=authorization_id,
            status="approved",
            authorization_number=f"AUTH{authorization_id}",
            approved_amount=5000.00,
            valid_until=datetime.now() + timedelta(days=25),
            reference_number=f"DISC-REF-{authorization_id}"
        )