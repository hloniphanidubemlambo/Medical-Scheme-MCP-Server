import pytest
import asyncio
from datetime import datetime
from src.connectors.discovery_connector import DiscoveryConnector
from src.connectors.gems_connector import GEMSConnector
from src.connectors.medscheme_connector import MedschemeConnector
from src.models.claim import Claim, ClaimItem
from src.models.authorization import AuthorizationRequest, BenefitCheck

@pytest.fixture
def discovery_connector():
    return DiscoveryConnector("mock_api_key")

@pytest.fixture
def gems_connector():
    return GEMSConnector("mock_api_key")

@pytest.fixture
def medscheme_connector():
    return MedschemeConnector("mock_api_key")

@pytest.fixture
def sample_benefit_check():
    return BenefitCheck(
        member_id="DISC123456",
        procedure_code="MRI001"
    )

@pytest.fixture
def sample_auth_request():
    return AuthorizationRequest(
        member_id="DISC123456",
        provider_id="PROV001",
        procedure_code="MRI001",
        patient_name="John Doe",
        requested_date=datetime.now(),
        urgency="routine"
    )

@pytest.fixture
def sample_claim():
    claim_item = ClaimItem(
        procedure_code="CONS001",
        description="General Consultation",
        quantity=1,
        unit_price=500.00,
        total_amount=500.00
    )
    
    return Claim(
        member_id="DISC123456",
        provider_id="PROV001",
        patient_name="John Doe",
        date_of_service=datetime.now(),
        claim_items=[claim_item],
        total_claim_amount=500.00
    )

@pytest.mark.asyncio
async def test_discovery_benefit_check(discovery_connector, sample_benefit_check):
    """Test Discovery benefit check"""
    result = await discovery_connector.check_benefits(sample_benefit_check)
    
    assert result.member_id == sample_benefit_check.member_id
    assert result.procedure_code == sample_benefit_check.procedure_code
    assert result.benefit_available is True
    assert result.remaining_benefit > 0

@pytest.mark.asyncio
async def test_discovery_authorization(discovery_connector, sample_auth_request):
    """Test Discovery authorization request"""
    result = await discovery_connector.request_authorization(sample_auth_request)
    
    assert result.authorization_id is not None
    assert result.status == "approved"
    assert result.authorization_number is not None

@pytest.mark.asyncio
async def test_discovery_claim_submission(discovery_connector, sample_claim):
    """Test Discovery claim submission"""
    result = await discovery_connector.submit_claim(sample_claim)
    
    assert result.claim_id is not None
    assert result.status == "approved"
    assert result.approved_amount > 0

@pytest.mark.asyncio
async def test_gems_benefit_check(gems_connector, sample_benefit_check):
    """Test GEMS benefit check"""
    result = await gems_connector.check_benefits(sample_benefit_check)
    
    assert result.member_id == sample_benefit_check.member_id
    assert result.benefit_available is True
    assert result.remaining_benefit == 25000.00  # GEMS specific amount

@pytest.mark.asyncio
async def test_gems_authorization(gems_connector, sample_auth_request):
    """Test GEMS authorization request"""
    result = await gems_connector.request_authorization(sample_auth_request)
    
    assert result.authorization_id.startswith("GEMS-AUTH-")
    assert result.status in ["approved", "pending"]

@pytest.mark.asyncio
async def test_medscheme_claim_submission(medscheme_connector, sample_claim):
    """Test Medscheme claim submission"""
    result = await medscheme_connector.submit_claim(sample_claim)
    
    assert result.claim_id.startswith("MED-CLAIM-")
    assert result.status == "approved"
    assert result.approved_amount == sample_claim.total_claim_amount * 0.75  # 75% coverage

@pytest.mark.asyncio
async def test_all_connectors_claim_status():
    """Test claim status retrieval for all connectors"""
    connectors = [
        DiscoveryConnector("mock_key"),
        GEMSConnector("mock_key"),
        MedschemeConnector("mock_key")
    ]
    
    for connector in connectors:
        result = await connector.get_claim_status("TEST_CLAIM_123")
        assert result.claim_id == "TEST_CLAIM_123"
        assert result.status == "processed"

if __name__ == "__main__":
    pytest.main([__file__])