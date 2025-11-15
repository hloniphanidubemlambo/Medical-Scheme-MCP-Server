# Pytest Configuration and Fixtures

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import app
from src.utils.auth import create_access_token

@pytest.fixture
def client():
    """Test client for API requests"""
    return TestClient(app)

@pytest.fixture
def auth_token():
    """Generate valid JWT token for testing"""
    return create_access_token(data={"sub": "test_user"})

@pytest.fixture
def auth_headers(auth_token):
    """Headers with authentication token"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def sample_patient():
    """Sample patient data for testing"""
    return {
        "patient_name": "John Doe",
        "member_id": "TEST123456",
        "date_of_birth": "1980-01-01",
        "gender": "male"
    }

@pytest.fixture
def sample_procedure():
    """Sample procedure data"""
    return {
        "procedure_code": "CONS001",
        "procedure_name": "General Consultation",
        "estimated_cost": 500.00
    }

@pytest.fixture
def sample_claim_data():
    """Sample claim submission data"""
    return {
        "patient_name": "John Doe",
        "member_id": "TEST123456",
        "scheme_name": "discovery",
        "provider_id": "PROV001",
        "service_date": datetime.now().date().isoformat(),
        "procedures": [
            {
                "procedure_code": "CONS001",
                "procedure_name": "General Consultation",
                "quantity": 1,
                "unit_price": 500.00,
                "total_amount": 500.00
            }
        ]
    }

@pytest.fixture
def mock_fhir_patient():
    """Mock FHIR patient response"""
    return {
        "resourceType": "Patient",
        "id": "7082689",
        "name": [{"family": "Panwar", "given": ["Mayank"]}],
        "gender": "male",
        "birthDate": "1974-12-25"
    }
