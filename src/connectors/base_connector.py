from abc import ABC, abstractmethod
from typing import Dict, Any
from src.models.claim import Claim, ClaimResponse
from src.models.authorization import AuthorizationRequest, AuthorizationResponse, BenefitCheck, BenefitResponse

class BaseSchemeConnector(ABC):
    """Abstract base class for all medical scheme connectors"""
    
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = self._build_headers()
    
    def _build_headers(self) -> Dict[str, str]:
        """Build common headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    @abstractmethod
    async def check_benefits(self, benefit_check: BenefitCheck) -> BenefitResponse:
        """Check member benefits for a specific procedure"""
        pass
    
    @abstractmethod
    async def request_authorization(self, auth_request: AuthorizationRequest) -> AuthorizationResponse:
        """Request pre-authorization for a medical procedure"""
        pass
    
    @abstractmethod
    async def submit_claim(self, claim: Claim) -> ClaimResponse:
        """Submit a medical claim for processing"""
        pass
    
    @abstractmethod
    async def get_claim_status(self, claim_id: str) -> ClaimResponse:
        """Get the status of a submitted claim"""
        pass
    
    @abstractmethod
    async def get_authorization_status(self, authorization_id: str) -> AuthorizationResponse:
        """Get the status of an authorization request"""
        pass