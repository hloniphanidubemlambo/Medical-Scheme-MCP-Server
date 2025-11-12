import pytest
import asyncio
from datetime import datetime
from fastapi.testclient import TestClient
from src.server import app
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

def test_list_mcp_tools():
    """Test listing available MCP tools"""
    response = client.get("/mcp/tools")
    assert response.status_code == 200
    
    data = response.json()
    assert "tools" in data
    assert data["total_tools"] == 4
    
    # Check that all expected tools are present
    tool_names = [tool["name"] for tool in data["tools"]]
    expected_tools = [
        "check_patient_benefits",
        "request_procedure_authorization", 
        "submit_medical_claim",
        "complete_patient_workflow"
    ]
    
    for expected_tool in expected_tools:
        assert expected_tool in tool_names

def test_check_patient_benefits_mcp_tool(auth_headers):
    """Test the check patient benefits MCP tool"""
    response = client.post(
        "/mcp/tools/check_patient_benefits",
        headers=auth_headers,
        params={
            "patient_name": "John Doe",
            "member_id": "DISC123456",
            "scheme_name": "discovery",
            "procedure_codes": ["CONS001", "MRI001"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "content" in data
    assert len(data["content"]) == 2
    assert data["content"][0]["type"] == "text"
    assert "John Doe" in data["content"][0]["text"]
    
    # Check resource data
    resource = data["content"][1]["resource"]
    assert resource["patient_name"] == "John Doe"
    assert resource["member_id"] == "DISC123456"
    assert resource["scheme_name"] == "discovery"
    assert len(resource["benefits"]) == 2

def test_request_procedure_authorization_mcp_tool(auth_headers):
    """Test the request procedure authorization MCP tool"""
    response = client.post(
        "/mcp/tools/request_procedure_authorization",
        headers=auth_headers,
        params={
            "patient_name": "Jane Smith",
            "member_id": "GEMS789012",
            "scheme_name": "gems",
            "provider_id": "PROV001",
            "procedure_code": "MRI001",
            "procedure_name": "Brain MRI with contrast",
            "estimated_cost": 3500.00,
            "urgency": "routine"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "content" in data
    resource = data["content"][1]["resource"]
    assert resource["patient_name"] == "Jane Smith"
    assert resource["procedure_name"] == "Brain MRI with contrast"
    assert resource["authorization_id"] is not None
    assert resource["status"] in ["approved", "pending", "rejected"]

def test_submit_medical_claim_mcp_tool(auth_headers):
    """Test the submit medical claim MCP tool"""
    procedures = [
        {
            "procedure_code": "CONS001",
            "procedure_name": "General Consultation",
            "quantity": 1,
            "unit_price": 500.00,
            "total_amount": 500.00
        },
        {
            "procedure_code": "BLOOD001",
            "procedure_name": "Full Blood Count", 
            "quantity": 1,
            "unit_price": 180.00,
            "total_amount": 180.00
        }
    ]
    
    response = client.post(
        "/mcp/tools/submit_medical_claim",
        headers=auth_headers,
        params={
            "patient_name": "Mike Johnson",
            "member_id": "MED555666",
            "scheme_name": "medscheme",
            "provider_id": "PROV001",
            "service_date": "2024-10-22"
        },
        json={"procedures": procedures}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    resource = data["content"][1]["resource"]
    assert resource["patient_name"] == "Mike Johnson"
    assert resource["claim_id"] is not None
    assert resource["submitted_amount"] == 680.00
    assert resource["procedures_count"] == 2

def test_complete_patient_workflow_mcp_tool(auth_headers):
    """Test the complete patient workflow MCP tool"""
    procedures = [
        {
            "procedure_code": "CONS001",
            "procedure_name": "General Consultation",
            "estimated_cost": 500.00,
            "urgency": "routine"
        },
        {
            "procedure_code": "ECG001",
            "procedure_name": "Electrocardiogram",
            "estimated_cost": 250.00,
            "urgency": "routine"
        }
    ]
    
    response = client.post(
        "/mcp/tools/complete_patient_workflow",
        headers=auth_headers,
        params={
            "patient_name": "Sarah Wilson",
            "member_id": "DISC987654",
            "scheme_name": "discovery",
            "provider_id": "PROV001",
            "practice_name": "City Medical Centre",
            "workflow_type": "check_and_auth",
            "service_date": "2024-10-22"
        },
        json={"procedures": procedures}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    resource = data["content"][1]["resource"]
    assert resource["patient_name"] == "Sarah Wilson"
    assert resource["practice_name"] == "City Medical Centre"
    assert resource["workflow_type"] == "check_and_auth"
    assert resource["summary"]["procedures_processed"] == 2

def test_practice_dashboard():
    """Test the practice dashboard HTML page"""
    response = client.get("/practice/dashboard")
    assert response.status_code == 200
    assert "Medical Practice MCP Dashboard" in response.text
    assert "Discovery Health" in response.text
    assert "GEMS" in response.text
    assert "Medscheme" in response.text

def test_get_common_procedures():
    """Test getting common procedures list"""
    response = client.get("/practice/procedures")
    assert response.status_code == 200
    
    data = response.json()
    assert "procedures" in data
    assert data["total"] > 0
    
    # Check that procedures have required fields
    for procedure in data["procedures"]:
        assert "code" in procedure
        assert "name" in procedure
        assert "typical_cost" in procedure

def test_get_supported_schemes():
    """Test getting supported schemes"""
    response = client.get("/practice/schemes")
    assert response.status_code == 200
    
    data = response.json()
    assert "supported_schemes" in data
    assert data["total"] == 3
    
    scheme_codes = [scheme["code"] for scheme in data["supported_schemes"]]
    assert "discovery" in scheme_codes
    assert "gems" in scheme_codes
    assert "medscheme" in scheme_codes

def test_quick_benefit_check(auth_headers):
    """Test quick benefit check endpoint"""
    response = client.post(
        "/practice/quick-benefit-check",
        headers=auth_headers,
        params={
            "patient_name": "Test Patient",
            "member_id": "TEST123456",
            "scheme_name": "discovery"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["patient_name"] == "Test Patient"
    assert data["member_id"] == "TEST123456"
    assert data["scheme_name"] == "discovery"
    assert "benefits" in data
    assert "summary" in data
    assert "recommendations" in data

def test_workflow_templates():
    """Test getting workflow templates"""
    response = client.get("/practice/workflow-templates")
    assert response.status_code == 200
    
    data = response.json()
    assert "templates" in data
    assert data["total"] > 0
    
    # Check template structure
    for template in data["templates"]:
        assert "name" in template
        assert "description" in template
        assert "steps" in template
        assert "typical_procedures" in template
        assert "workflow_type" in template

def test_mcp_tool_error_handling(auth_headers):
    """Test error handling in MCP tools"""
    # Test with invalid scheme
    response = client.post(
        "/mcp/tools/check_patient_benefits",
        headers=auth_headers,
        params={
            "patient_name": "John Doe",
            "member_id": "INVALID123",
            "scheme_name": "invalid_scheme",
            "procedure_codes": ["CONS001"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["isError"] is True
    assert "Error" in data["content"][0]["text"]

def test_unauthorized_access():
    """Test that endpoints require authentication"""
    response = client.post(
        "/mcp/tools/check_patient_benefits",
        params={
            "patient_name": "John Doe",
            "member_id": "DISC123456", 
            "scheme_name": "discovery",
            "procedure_codes": ["CONS001"]
        }
    )
    
    assert response.status_code == 403  # Forbidden without auth

if __name__ == "__main__":
    pytest.main([__file__, "-v"])