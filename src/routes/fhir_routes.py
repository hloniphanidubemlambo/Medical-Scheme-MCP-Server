from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from src.connectors.hapi_fhir_connector import HAPIFHIRConnector
from src.connectors.openemr_connector import OpenEMRConnector
from src.utils.auth import verify_token
from src.utils.logger import RequestLogger

router = APIRouter(prefix="/fhir", tags=["FHIR Integration"])

# Initialize connectors
fhir_connector = HAPIFHIRConnector()
openemr_connector = OpenEMRConnector()

@router.get("/patients/search")
async def search_fhir_patients(
    name: Optional[str] = None,
    limit: int = 10,
    current_user: str = Depends(verify_token)
):
    """Search for patients in HAPI FHIR server"""
    try:
        patients = await fhir_connector.search_patients(name=name, limit=limit)
        
        RequestLogger.log_scheme_interaction(
            "hapi_fhir", "patient_search", True, 
            {"query": name, "results": len(patients)}
        )
        
        return {
            "patients": patients,
            "total": len(patients),
            "query": name,
            "source": "HAPI FHIR"
        }
        
    except Exception as e:
        RequestLogger.log_scheme_interaction("hapi_fhir", "patient_search", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error searching patients: {str(e)}")

@router.get("/patients/{patient_id}")
async def get_fhir_patient(
    patient_id: str,
    current_user: str = Depends(verify_token)
):
    """Get specific patient from HAPI FHIR"""
    try:
        patient_data = await fhir_connector.get_patient_data(patient_id)
        
        if "error" in patient_data:
            raise HTTPException(status_code=404, detail=patient_data["error"])
        
        RequestLogger.log_scheme_interaction(
            "hapi_fhir", "get_patient", True, 
            {"patient_id": patient_id}
        )
        
        return {
            "patient": patient_data,
            "source": "HAPI FHIR"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        RequestLogger.log_scheme_interaction("hapi_fhir", "get_patient", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error getting patient: {str(e)}")

@router.get("/integration/test")
async def test_fhir_integration(current_user: str = Depends(verify_token)):
    """Test FHIR integration connectivity"""
    try:
        # Test HAPI FHIR
        fhir_patients = await fhir_connector.search_patients(limit=1)
        fhir_status = "connected" if fhir_patients else "no_data"
        
        # Test OpenEMR
        openemr_status = await openemr_connector.test_connection()
        
        return {
            "fhir": {
                "status": fhir_status,
                "url": fhir_connector.base_url,
                "test_patients": len(fhir_patients)
            },
            "openemr": openemr_status,
            "integration_ready": fhir_status == "connected" and openemr_status["status"] == "connected"
        }
        
    except Exception as e:
        return {
            "fhir": {"status": "error", "error": str(e)},
            "openemr": {"status": "not_tested"},
            "integration_ready": False
        }

@router.post("/workflow/patient-lookup")
async def integrated_patient_lookup(
    member_id: str,
    scheme_name: str = "fhir",
    current_user: str = Depends(verify_token)
):
    """Integrated patient lookup across FHIR and OpenEMR"""
    try:
        results = {
            "member_id": member_id,
            "scheme_name": scheme_name,
            "fhir_data": None,
            "openemr_data": None,
            "integrated_profile": None
        }
        
        # Look up in FHIR (as medical scheme)
        if scheme_name == "fhir":
            try:
                from src.models.authorization import BenefitCheck
                benefit_check = BenefitCheck(member_id=member_id, procedure_code="CONS001")
                fhir_benefits = await fhir_connector.check_benefits(benefit_check)
                results["fhir_data"] = {
                    "benefits": fhir_benefits.dict(),
                    "source": "HAPI FHIR"
                }
            except Exception as e:
                results["fhir_data"] = {"error": str(e)}
        
        # Look up in OpenEMR (as clinic system)
        try:
            openemr_patient = await openemr_connector.get_patient_by_insurance_id(member_id)
            if openemr_patient:
                results["openemr_data"] = {
                    "patient": openemr_patient,
                    "source": "OpenEMR"
                }
        except Exception as e:
            results["openemr_data"] = {"error": str(e)}
        
        # Create integrated profile
        if results["fhir_data"] and results["openemr_data"]:
            results["integrated_profile"] = {
                "member_id": member_id,
                "patient_name": results["openemr_data"]["patient"].get("name"),
                "benefits_available": results["fhir_data"]["benefits"].get("benefit_available"),
                "remaining_benefit": results["fhir_data"]["benefits"].get("remaining_benefit"),
                "clinic_records": "available",
                "integration_status": "complete"
            }
        
        RequestLogger.log_scheme_interaction(
            "integrated_lookup", "patient_lookup", True,
            {"member_id": member_id, "has_fhir": bool(results["fhir_data"]), "has_openemr": bool(results["openemr_data"])}
        )
        
        return results
        
    except Exception as e:
        RequestLogger.log_scheme_interaction("integrated_lookup", "patient_lookup", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error in integrated lookup: {str(e)}")

@router.post("/workflow/complete-visit")
async def complete_patient_visit(
    member_id: str,
    provider_id: str,
    procedures: List[Dict[str, Any]],
    scheme_name: str = "fhir",
    current_user: str = Depends(verify_token)
):
    """Complete patient visit workflow using FHIR + OpenEMR"""
    try:
        workflow_results = {
            "member_id": member_id,
            "provider_id": provider_id,
            "procedures": procedures,
            "steps": []
        }
        
        # Step 1: Get patient from OpenEMR
        workflow_results["steps"].append("🔍 Looking up patient in clinic system...")
        openemr_patient = await openemr_connector.get_patient_by_insurance_id(member_id)
        
        if not openemr_patient:
            workflow_results["steps"].append("❌ Patient not found in clinic system")
            return workflow_results
        
        workflow_results["steps"].append(f"✅ Found patient: {openemr_patient.get('name')}")
        
        # Step 2: Check benefits in FHIR
        workflow_results["steps"].append("🔍 Checking medical scheme benefits...")
        
        from src.models.authorization import BenefitCheck
        benefit_results = []
        
        for proc in procedures:
            benefit_check = BenefitCheck(member_id=member_id, procedure_code=proc["code"])
            benefit_result = await fhir_connector.check_benefits(benefit_check)
            benefit_results.append({
                "procedure": proc["name"],
                "code": proc["code"],
                "benefit_available": benefit_result.benefit_available,
                "authorization_required": benefit_result.authorization_required
            })
        
        workflow_results["steps"].append(f"✅ Checked benefits for {len(procedures)} procedures")
        workflow_results["benefit_results"] = benefit_results
        
        # Step 3: Request authorizations if needed
        auth_results = []
        for i, proc in enumerate(procedures):
            if benefit_results[i]["authorization_required"]:
                workflow_results["steps"].append(f"🔐 Requesting authorization for {proc['name']}...")
                
                from src.models.authorization import AuthorizationRequest
                from datetime import datetime
                
                auth_request = AuthorizationRequest(
                    member_id=member_id,
                    provider_id=provider_id,
                    procedure_code=proc["code"],
                    patient_name=openemr_patient.get("name", "Unknown"),
                    requested_date=datetime.now()
                )
                
                auth_result = await fhir_connector.request_authorization(auth_request)
                auth_results.append({
                    "procedure": proc["name"],
                    "authorization_id": auth_result.authorization_id,
                    "status": auth_result.status
                })
                
                workflow_results["steps"].append(f"✅ Authorization {auth_result.status} for {proc['name']}")
        
        workflow_results["authorization_results"] = auth_results
        
        # Step 4: Submit claim to FHIR
        workflow_results["steps"].append("📄 Submitting claim to medical scheme...")
        
        from src.models.claim import Claim, ClaimItem
        from datetime import datetime
        
        claim_items = []
        total_amount = 0
        
        for proc in procedures:
            item = ClaimItem(
                procedure_code=proc["code"],
                description=proc["name"],
                quantity=1,
                unit_price=proc["cost"],
                total_amount=proc["cost"]
            )
            claim_items.append(item)
            total_amount += proc["cost"]
        
        claim = Claim(
            member_id=member_id,
            provider_id=provider_id,
            patient_name=openemr_patient.get("name", "Unknown"),
            date_of_service=datetime.now(),
            claim_items=claim_items,
            total_claim_amount=total_amount
        )
        
        claim_result = await fhir_connector.submit_claim(claim)
        workflow_results["steps"].append(f"✅ Claim submitted: {claim_result.status} - R{claim_result.approved_amount:,.2f}")
        workflow_results["claim_result"] = {
            "claim_id": claim_result.claim_id,
            "status": claim_result.status,
            "approved_amount": claim_result.approved_amount
        }
        
        workflow_results["steps"].append("🎉 Complete patient visit workflow finished!")
        
        RequestLogger.log_scheme_interaction(
            "integrated_workflow", "complete_visit", True,
            {"member_id": member_id, "procedures": len(procedures), "total_amount": total_amount}
        )
        
        return workflow_results
        
    except Exception as e:
        RequestLogger.log_scheme_interaction("integrated_workflow", "complete_visit", False, {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error in complete visit workflow: {str(e)}")

@router.get("/openemr/patients")
async def get_openemr_patients(
    limit: int = 10,
    current_user: str = Depends(verify_token)
):
    """Get patients from local OpenEMR system"""
    try:
        patients = await openemr_connector.get_patients(limit=limit)
        
        return {
            "patients": patients,
            "total": len(patients),
            "source": "OpenEMR Local"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting OpenEMR patients: {str(e)}")

@router.get("/openemr/test")
async def test_openemr_connection(current_user: str = Depends(verify_token)):
    """Test OpenEMR connection"""
    try:
        result = await openemr_connector.test_connection()
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to test OpenEMR: {str(e)}"
        }