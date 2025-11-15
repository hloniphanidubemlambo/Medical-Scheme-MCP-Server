# Comprehensive API Endpoint Tests

import pytest
from fastapi import status

class TestHealthEndpoints:
    """Test health check and status endpoints"""
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "running"
        assert "endpoints" in data
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_login_success(self, client):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "password123"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "wrong"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_without_token(self, client):
        response = client.get("/mcp/tools")
        assert response.status_code == status.HTTP_403_FORBIDDEN

class TestMCPTools:
    """Test MCP tool endpoints"""
    
    def test_list_mcp_tools(self, client):
        response = client.get("/mcp/tools")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tools" in data
        assert data["total_tools"] == 4
    
    def test_check_benefits(self, client, auth_headers):
        response = client.post(
            "/mcp/tools/check_patient_benefits",
            params={
                "patient_name": "John Doe",
                "member_id": "TEST123",
                "scheme_name": "discovery",
                "procedure_codes": ["CONS001", "MRI001"]
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "content" in data
    
    def test_request_authorization(self, client, auth_headers):
        response = client.post(
            "/mcp/tools/request_procedure_authorization",
            params={
                "patient_name": "John Doe",
                "member_id": "TEST123",
                "scheme_name": "discovery",
                "provider_id": "PROV001",
                "procedure_code": "MRI001",
                "procedure_name": "MRI Scan",
                "estimated_cost": 5000.00
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

class TestSchemeOperations:
    """Test medical scheme operations"""
    
    def test_benefit_check(self, client, auth_headers):
        response = client.post(
            "/scheme/discovery/benefits/check",
            json={
                "member_id": "TEST123",
                "procedure_code": "CONS001"
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "benefit_available" in data
    
    def test_invalid_scheme(self, client, auth_headers):
        response = client.post(
            "/scheme/invalid_scheme/benefits/check",
            json={
                "member_id": "TEST123",
                "procedure_code": "CONS001"
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestFHIRIntegration:
    """Test FHIR integration endpoints"""
    
    def test_fhir_integration_test(self, client, auth_headers):
        response = client.get(
            "/fhir/integration/test",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "fhir" in data
    
    def test_search_patients(self, client, auth_headers):
        response = client.get(
            "/fhir/patients/search?limit=3",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "patients" in data

class TestErrorHandling:
    """Test error handling and validation"""
    
    def test_validation_error(self, client, auth_headers):
        response = client.post(
            "/mcp/tools/check_patient_benefits",
            params={
                "patient_name": "John Doe",
                # Missing required fields
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_json(self, client, auth_headers):
        response = client.post(
            "/scheme/discovery/benefits/check",
            data="invalid json",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
