import pytest
import asyncio
from datetime import datetime
from fastapi.testclient import TestClient
from src.server import app
from src.connectors.hapi_fhir_connector import HAPIFHIRConnector
from src.utils.auth import create_access_token

# Create test client
client = TestClient(app)

@pytest.fixture
def auth_token():
    """Create a test authentication token"""
    token_data = {"sub": "test_user"}
    return create_access_token(token_data)

@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def fhir_connector():
    """Create FHIR connector instance"""
    return HAPIFHIRConnector()

@pytest.mark.asyncio
async def test_fhir_connector_initialization(fhir_connector):
    """Test FHIR connector initializes correctly"""
    assert fhir_connector.base_url == "https://hapi.fhir.org/baseR4"
    assert "application/fhir+json" in fhir_connector.headers["Accept"]

@pytest.mark.asyncio
async def test_fhir_benefit_check(fhir_connector):
    """Test FHIR benefit check functionality"""
    from src.models.authorization import BenefitCheck
    
    benefit_check = BenefitCheck(
        member_id="test-patient-123",
        procedure_code="CONS001"
    )
    
    result = await fhir_connector.check_benefits(benefit_check)
    
    assert result.member_id == "test-patient-123"
    assert result.procedure_code == "CONS001"
    assert isinstance(result.benefit_available, bool)
    assert isinstance(result.remaining_benefit, (int, float))

@pytest.mark.asyncio
async def test_fhir_authorization_request(fhir_connector):
    """Test FHIR authorization request"""
    from src.models.authorization import AuthorizationRequest
    
    auth_request = AuthorizationRequest(
        member_id="test-patient-123",
        provider_id="test-provider-456",
        procedure_code="MRI001",
        patient_name="Test Patient",
        requested_date=datetime.now()
    )
    
    result = await fhir_connector.request_authorization(auth_request)
    
    assert result.authorization_id is not None
    assert result.status in ["approved", "pending", "rejected"]
    assert "FHIR-AUTH-" in result.authorization_id

@pytest.mark.asyncio
async def test_fhir_claim_submission(fhir_connector):
    """Test FHIR claim submission"""
    from src.models.claim import Claim, ClaimItem
    
    claim_item = ClaimItem(
        procedure_code="CONS001",
        description="General Consultation",
        quantity=1,
        unit_price=500.00,
        total_amount=500.00
    )
    
    claim = Claim(
        member_id="test-patient-123",
        provider_id="test-provider-456",
        patient_name="Test Patient",
        date_of_service=datetime.now(),
        claim_items=[claim_item],
        total_claim_amount=500.00
    )
    
    result = await fhir_connector.submit_claim(claim)
    
    assert result.claim_id is not None
    assert result.status in ["approved", "pending", "rejected"]
    assert result.approved_amount > 0

@pytest.mark.asyncio
async def test_fhir_patient_search(fhir_connector):
    """Test FHIR patient search functionality"""
    patients = await fhir_connector.search_patients(limit=5)
    
    assert isinstance(patients, list)
    # Note: May be empty if FHIR server has no patients, which is okay for testing

def test_fhir_integration_endpoint(auth_headers):
    """Test FHIR integration test endpoint"""
    response = client.get("/fhir/integration/test", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "fhir" in data
    assert "openemr" in data
    assert "integration_ready" in data
    
    # FHIR should always be testable (public API)
    assert data["fhir"]["url"] == "https://hapi.fhir.org/baseR4"

def test_fhir_patient_search_endpoint(auth_headers):
    """Test FHIR patient search endpoint"""
    response = client.get("/fhir/patients/search?limit=3", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "patients" in data
    assert "total" in data
    assert "source" in data
    assert data["source"] == "HAPI FHIR"

def test_mcp_tools_with_fhir_scheme(auth_headers):
    """Test MCP tools work with FHIR scheme"""
    response = client.post(
        "/mcp/tools/check_patient_benefits",
        headers=auth_headers,
        params={
            "patient_name": "Test Patient",
            "member_id": "fhir-patient-123",
            "scheme_name": "fhir",  # Use FHIR scheme
            "procedure_codes": ["CONS001", "MRI001"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "content" in data
    assert len(data["content"]) == 2
    assert "Test Patient" in data["content"][0]["text"]
    
    # Check that FHIR data is returned
    resource = data["content"][1]["resource"]
    assert resource["scheme_name"] == "fhir"
    assert len(resource["benefits"]) == 2

def test_fhir_scheme_in_registry():
    """Test that FHIR scheme is registered"""
    from src.config.registry import get_available_schemes, get_connector
    
    schemes = get_available_schemes()
    assert "fhir" in schemes
    
    # Test getting FHIR connector
    fhir_connector = get_connector("fhir")
    assert fhir_connector is not None
    assert isinstance(fhir_connector, HAPIFHIRConnector)

def test_practice_dashboard_includes_fhir():
    """Test that practice dashboard includes FHIR option"""
    response = client.get("/practice/dashboard")
    
    assert response.status_code == 200
    html_content = response.text
    
    # Check that FHIR is mentioned in the dashboard
    assert "HAPI FHIR" in html_content
    assert "Real Data" in html_content

def test_fhir_workflow_patient_lookup(auth_headers):
    """Test integrated patient lookup workflow"""
    response = client.post(
        "/fhir/workflow/patient-lookup",
        headers=auth_headers,
        params={
            "member_id": "test-patient-123",
            "scheme_name": "fhir"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["member_id"] == "test-patient-123"
    assert data["scheme_name"] == "fhir"
    assert "fhir_data" in data
    assert "openemr_data" in data

def test_unauthorized_fhir_access():
    """Test that FHIR endpoints require authentication"""
    response = client.get("/fhir/integration/test")
    assert response.status_code == 403  # Forbidden without auth
    
    response = client.get("/fhir/patients/search")
    assert response.status_code == 403  # Forbidden without auth

@pytest.mark.asyncio
async def test_fhir_error_handling(fhir_connector):
    """Test FHIR connector error handling"""
    from src.models.authorization import BenefitCheck
    
    # Test with potentially problematic data
    benefit_check = BenefitCheck(
        member_id="invalid-patient-id-that-might-cause-errors",
        procedure_code="INVALID_CODE"
    )
    
    # Should not raise exception, should return fallback response
    result = await fhir_connector.check_benefits(benefit_check)
    
    assert result is not None
    assert result.member_id == "invalid-patient-id-that-might-cause-errors"
    assert result.procedure_code == "INVALID_CODE"

def test_fhir_complete_workflow_endpoint(auth_headers):
    """Test complete FHIR workflow endpoint"""
    workflow_data = {
        "member_id": "test-patient-123",
        "provider_id": "test-provider-456",
        "procedures": [
            {"code": "CONS001", "name": "Consultation", "cost": 500},
            {"code": "BLOOD001", "name": "Blood Test", "cost": 180}
        ],
        "scheme_name": "fhir"
    }
    
    response = client.post(
        "/fhir/workflow/complete-visit",
        headers=auth_headers,
        params={
            "member_id": workflow_data["member_id"],
            "provider_id": workflow_data["provider_id"],
            "scheme_name": workflow_data["scheme_name"]
        },
        json={"procedures": workflow_data["procedures"]}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["member_id"] == "test-patient-123"
    assert "steps" in data
    assert len(data["steps"]) > 0
    assert "procedures" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])