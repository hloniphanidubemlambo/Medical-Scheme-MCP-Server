import httpx
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.utils.logger import RequestLogger

class OpenEMRConnector:
    """OpenEMR connector for local clinic/hospital data"""
    
    def __init__(self, base_url: str = "http://localhost:8300", username: str = "admin", password: str = "pass"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.access_token = None
        self.token_expires = None
        
    async def _get_access_token(self) -> str:
        """Get or refresh access token from OpenEMR"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/apis/default/auth",
                    json={
                        "grant_type": "password",
                        "username": self.username,
                        "password": self.password,
                        "scope": "user"
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 min early
                    
                    RequestLogger.log_scheme_interaction("openemr", "authentication", True, {"expires_in": expires_in})
                    return self.access_token
                else:
                    raise Exception(f"OpenEMR auth failed: {response.status_code}")
                    
        except Exception as e:
            RequestLogger.log_scheme_interaction("openemr", "authentication", False, {"error": str(e)})
            raise Exception(f"Failed to authenticate with OpenEMR: {str(e)}")
    
    async def _make_api_call(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make authenticated API call to OpenEMR"""
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = await client.get(f"{self.base_url}/apis/default/api{endpoint}", headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(f"{self.base_url}/apis/default/api{endpoint}", json=data, headers=headers)
                elif method.upper() == "PUT":
                    response = await client.put(f"{self.base_url}/apis/default/api{endpoint}", json=data, headers=headers)
                
                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    raise Exception(f"OpenEMR API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            RequestLogger.log_scheme_interaction("openemr", f"api_call_{method}_{endpoint}", False, {"error": str(e)})
            raise e
    
    async def get_patients(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of patients from OpenEMR"""
        try:
            response = await self._make_api_call("GET", f"/patient?_limit={limit}")
            
            patients = []
            if isinstance(response, list):
                for patient in response:
                    patients.append({
                        "id": patient.get("id"),
                        "uuid": patient.get("uuid"),
                        "name": f"{patient.get('fname', '')} {patient.get('lname', '')}".strip(),
                        "dob": patient.get("DOB"),
                        "gender": patient.get("sex"),
                        "phone": patient.get("phone_home"),
                        "email": patient.get("email"),
                        "address": f"{patient.get('street', '')} {patient.get('city', '')}".strip(),
                        "insurance_id": patient.get("pubpid")  # Public patient ID often used for insurance
                    })
            
            RequestLogger.log_scheme_interaction("openemr", "get_patients", True, {"count": len(patients)})
            return patients
            
        except Exception as e:
            RequestLogger.log_scheme_interaction("openemr", "get_patients", False, {"error": str(e)})
            return []
    
    async def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """Get specific patient from OpenEMR"""
        try:
            response = await self._make_api_call("GET", f"/patient/{patient_id}")
            
            if response:
                patient_data = {
                    "id": response.get("id"),
                    "uuid": response.get("uuid"),
                    "name": f"{response.get('fname', '')} {response.get('lname', '')}".strip(),
                    "dob": response.get("DOB"),
                    "gender": response.get("sex"),
                    "phone": response.get("phone_home"),
                    "email": response.get("email"),
                    "address": f"{response.get('street', '')} {response.get('city', '')}".strip(),
                    "insurance_id": response.get("pubpid"),
                    "emergency_contact": response.get("contact_relationship"),
                    "pharmacy": response.get("pharmacy_id")
                }
                
                RequestLogger.log_scheme_interaction("openemr", "get_patient", True, {"patient_id": patient_id})
                return patient_data
            else:
                return {}
                
        except Exception as e:
            RequestLogger.log_scheme_interaction("openemr", "get_patient", False, {"error": str(e)})
            return {}
    
    async def get_encounters(self, patient_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get patient encounters (visits) from OpenEMR"""
        try:
            endpoint = f"/encounter?_limit={limit}"
            if patient_id:
                endpoint += f"&patient={patient_id}"
                
            response = await self._make_api_call("GET", endpoint)
            
            encounters = []
            if isinstance(response, list):
                for encounter in response:
                    encounters.append({
                        "id": encounter.get("id"),
                        "uuid": encounter.get("uuid"),
                        "patient_id": encounter.get("pid"),
                        "date": encounter.get("date"),
                        "reason": encounter.get("reason"),
                        "facility": encounter.get("facility"),
                        "provider": encounter.get("provider_id"),
                        "encounter_type": encounter.get("pc_catname"),
                        "billing_note": encounter.get("billing_note")
                    })
            
            RequestLogger.log_scheme_interaction("openemr", "get_encounters", True, {"count": len(encounters)})
            return encounters
            
        except Exception as e:
            RequestLogger.log_scheme_interaction("openemr", "get_encounters", False, {"error": str(e)})
            return []
    
    async def get_insurance_companies(self) -> List[Dict[str, Any]]:
        """Get insurance companies from OpenEMR"""
        try:
            response = await self._make_api_call("GET", "/insurance_company")
            
            companies = []
            if isinstance(response, list):
                for company in response:
                    companies.append({
                        "id": company.get("id"),
                        "name": company.get("name"),
                        "attn": company.get("attn"),
                        "cms_id": company.get("cms_id"),
                        "x12_receiver_id": company.get("x12_receiver_id"),
                        "x12_default_partner_id": company.get("x12_default_partner_id")
                    })
            
            RequestLogger.log_scheme_interaction("openemr", "get_insurance_companies", True, {"count": len(companies)})
            return companies
            
        except Exception as e:
            RequestLogger.log_scheme_interaction("openemr", "get_insurance_companies", False, {"error": str(e)})
            return []
    
    async def create_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new patient in OpenEMR"""
        try:
            # Map our patient data to OpenEMR format
            openemr_patient = {
                "fname": patient_data.get("first_name", ""),
                "lname": patient_data.get("last_name", ""),
                "DOB": patient_data.get("date_of_birth", ""),
                "sex": patient_data.get("gender", ""),
                "phone_home": patient_data.get("phone", ""),
                "email": patient_data.get("email", ""),
                "street": patient_data.get("address", ""),
                "city": patient_data.get("city", ""),
                "pubpid": patient_data.get("insurance_id", "")
            }
            
            response = await self._make_api_call("POST", "/patient", openemr_patient)
            
            RequestLogger.log_scheme_interaction("openemr", "create_patient", True, {"patient_name": f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"})
            return response
            
        except Exception as e:
            RequestLogger.log_scheme_interaction("openemr", "create_patient", False, {"error": str(e)})
            return {"error": str(e)}
    
    async def get_practitioners(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get practitioners/providers from OpenEMR"""
        try:
            response = await self._make_api_call("GET", f"/practitioner?_limit={limit}")
            
            practitioners = []
            if isinstance(response, list):
                for practitioner in response:
                    practitioners.append({
                        "id": practitioner.get("id"),
                        "uuid": practitioner.get("uuid"),
                        "name": f"{practitioner.get('fname', '')} {practitioner.get('lname', '')}".strip(),
                        "npi": practitioner.get("npi"),
                        "taxonomy": practitioner.get("taxonomy"),
                        "specialty": practitioner.get("specialty"),
                        "phone": practitioner.get("phone"),
                        "email": practitioner.get("email")
                    })
            
            RequestLogger.log_scheme_interaction("openemr", "get_practitioners", True, {"count": len(practitioners)})
            return practitioners
            
        except Exception as e:
            RequestLogger.log_scheme_interaction("openemr", "get_practitioners", False, {"error": str(e)})
            return []
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to OpenEMR"""
        try:
            token = await self._get_access_token()
            
            # Try to get a simple endpoint
            response = await self._make_api_call("GET", "/patient?_limit=1")
            
            return {
                "status": "connected",
                "message": "Successfully connected to OpenEMR",
                "base_url": self.base_url,
                "authenticated": bool(token),
                "test_response": "OK"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to connect to OpenEMR: {str(e)}",
                "base_url": self.base_url,
                "authenticated": False
            }
    
    async def get_patient_by_insurance_id(self, insurance_id: str) -> Dict[str, Any]:
        """Find patient by insurance/member ID"""
        try:
            # Search patients by public ID (often used for insurance)
            patients = await self.get_patients(limit=100)  # Get more patients to search
            
            for patient in patients:
                if patient.get("insurance_id") == insurance_id:
                    # Get full patient details
                    full_patient = await self.get_patient(patient["id"])
                    return full_patient
            
            return {}
            
        except Exception as e:
            RequestLogger.log_scheme_interaction("openemr", "get_patient_by_insurance_id", False, {"error": str(e)})
            return {}