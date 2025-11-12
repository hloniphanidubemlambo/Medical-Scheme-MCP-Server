#!/usr/bin/env python3
"""
Demo script showing how easy it is to use MCP tools for medical practices
"""
import asyncio
import httpx
import json
from datetime import datetime

# Server configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "password123"

class MCPDemo:
    def __init__(self):
        self.token = None
        self.headers = {}
    
    async def authenticate(self):
        """Get authentication token"""
        print("🔐 Authenticating...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"username": USERNAME, "password": PASSWORD}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ Authentication successful!")
            else:
                print("❌ Authentication failed!")
                return False
        return True
    
    async def demo_benefit_check(self):
        """Demo: Check patient benefits"""
        print("\n" + "="*60)
        print("🔍 DEMO: Checking Patient Benefits")
        print("="*60)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp/tools/check_patient_benefits",
                headers=self.headers,
                params={
                    "patient_name": "John Doe",
                    "member_id": "DISC123456",
                    "scheme_name": "discovery",
                    "procedure_codes": ["CONS001", "MRI001", "BLOOD001"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['content'][0]['text']}")
                
                benefits = result['content'][1]['resource']['benefits']
                print("\n📊 Benefit Details:")
                for benefit in benefits:
                    status = "✅" if benefit['benefit_available'] else "❌"
                    auth_req = "🔐 Auth Required" if benefit['authorization_required'] else "✅ No Auth Needed"
                    print(f"  {status} {benefit['procedure_code']}: R{benefit['remaining_benefit']:,.2f} remaining | {auth_req}")
            else:
                print(f"❌ Error: {response.status_code}")
    
    async def demo_authorization(self):
        """Demo: Request procedure authorization"""
        print("\n" + "="*60)
        print("🔐 DEMO: Requesting Procedure Authorization")
        print("="*60)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp/tools/request_procedure_authorization",
                headers=self.headers,
                params={
                    "patient_name": "Jane Smith",
                    "member_id": "GEMS789012",
                    "scheme_name": "gems",
                    "provider_id": "PROV001",
                    "procedure_code": "MRI001",
                    "procedure_name": "Brain MRI with contrast",
                    "estimated_cost": 3500.00,
                    "urgency": "routine",
                    "clinical_notes": "Patient experiencing persistent headaches"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['content'][0]['text']}")
                
                auth = result['content'][1]['resource']
                print(f"\n📋 Authorization Details:")
                print(f"  🆔 Authorization ID: {auth['authorization_id']}")
                print(f"  📊 Status: {auth['status'].upper()}")
                print(f"  💰 Approved Amount: R{auth['approved_amount']:,.2f}")
                print(f"  📅 Valid Until: {auth['valid_until']}")
            else:
                print(f"❌ Error: {response.status_code}")
    
    async def demo_claim_submission(self):
        """Demo: Submit medical claim"""
        print("\n" + "="*60)
        print("📄 DEMO: Submitting Medical Claim")
        print("="*60)
        
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
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp/tools/submit_medical_claim",
                headers=self.headers,
                params={
                    "patient_name": "Mike Johnson",
                    "member_id": "MED555666",
                    "scheme_name": "medscheme",
                    "provider_id": "PROV001",
                    "service_date": datetime.now().strftime("%Y-%m-%d")
                },
                json={"procedures": procedures}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['content'][0]['text']}")
                
                claim = result['content'][1]['resource']
                print(f"\n📋 Claim Details:")
                print(f"  🆔 Claim ID: {claim['claim_id']}")
                print(f"  📊 Status: {claim['status'].upper()}")
                print(f"  💰 Submitted: R{claim['submitted_amount']:,.2f}")
                print(f"  💰 Approved: R{claim['approved_amount']:,.2f}")
                print(f"  📅 Processed: {claim['processed_date']}")
            else:
                print(f"❌ Error: {response.status_code}")
    
    async def demo_fhir_integration(self):
        """Demo: FHIR integration with real healthcare data"""
        print("\n" + "="*60)
        print("🌐 DEMO: FHIR Integration (Real Healthcare Data)")
        print("="*60)
        
        async with httpx.AsyncClient() as client:
            # Test FHIR connectivity
            response = await client.get(
                f"{BASE_URL}/fhir/integration/test",
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ FHIR Integration Test Results:")
                print(f"  🌐 HAPI FHIR: {result['fhir']['status']}")
                print(f"  🏥 OpenEMR: {result['openemr']['status']}")
                print(f"  🔗 Integration Ready: {result['integration_ready']}")
                
                # Test FHIR benefit check
                print("\n🔍 Testing FHIR Benefit Check...")
                fhir_response = await client.post(
                    f"{BASE_URL}/mcp/tools/check_patient_benefits",
                    headers=self.headers,
                    params={
                        "patient_name": "FHIR Test Patient",
                        "member_id": "fhir-patient-123",
                        "scheme_name": "fhir",
                        "procedure_codes": ["CONS001", "MRI001"]
                    }
                )
                
                if fhir_response.status_code == 200:
                    fhir_result = fhir_response.json()
                    print("✅ FHIR benefit check successful!")
                    benefits = fhir_result['content'][1]['resource']['benefits']
                    for benefit in benefits:
                        status = "✅" if benefit['benefit_available'] else "❌"
                        print(f"  {status} {benefit['procedure_code']}: R{benefit['remaining_benefit']:,.2f} remaining")
                else:
                    print(f"❌ FHIR benefit check failed: {fhir_response.status_code}")
            else:
                print(f"❌ FHIR integration test failed: {response.status_code}")

    async def demo_complete_workflow(self):
        """Demo: Complete patient workflow"""
        print("\n" + "="*60)
        print("🔄 DEMO: Complete Patient Workflow")
        print("="*60)
        
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
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp/tools/complete_patient_workflow",
                headers=self.headers,
                params={
                    "patient_name": "Sarah Wilson",
                    "member_id": "DISC987654",
                    "scheme_name": "discovery",
                    "provider_id": "PROV001",
                    "practice_name": "City Medical Centre",
                    "workflow_type": "check_and_auth",
                    "service_date": datetime.now().strftime("%Y-%m-%d")
                },
                json={"procedures": procedures}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Workflow completed successfully!")
                print(result['content'][0]['text'])
                
                workflow = result['content'][1]['resource']
                print(f"\n📊 Workflow Summary:")
                print(f"  👤 Patient: {workflow['patient_name']}")
                print(f"  🏥 Practice: {workflow['practice_name']}")
                print(f"  📋 Procedures: {workflow['summary']['procedures_processed']}")
                print(f"  🔐 Authorizations: {workflow['summary']['authorizations_requested']}")
            else:
                print(f"❌ Error: {response.status_code}")
    
    async def show_ai_examples(self):
        """Show AI assistant examples"""
        print("\n" + "="*60)
        print("🤖 AI ASSISTANT EXAMPLES")
        print("="*60)
        print("You can ask an AI assistant to help with these tasks:")
        print()
        print("💬 'Check benefits for patient John Doe (DISC123456) on Discovery for consultation and MRI'")
        print("💬 'Request authorization for Jane Smith (GEMS789012) on GEMS for urgent CT scan'")
        print("💬 'Submit claim for Mike Johnson consultation and blood work completed today'")
        print("💬 'Process new patient Sarah Wilson: check benefits, get auth, submit claim'")
        print("💬 'Check benefits for patient-123 on FHIR for consultation and blood work'")
        print("💬 'Run complete FHIR workflow for patient-456 with real healthcare data'")
        print()
        print("🌐 Visit the practice dashboard: http://localhost:8000/practice/dashboard")
        print("📚 API Documentation: http://localhost:8000/docs")
    
    async def run_demo(self):
        """Run complete demo"""
        print("🏥 Medical Scheme MCP Server - Demo")
        print("="*60)
        
        if not await self.authenticate():
            return
        
        try:
            await self.demo_benefit_check()
            await asyncio.sleep(1)
            
            await self.demo_authorization()
            await asyncio.sleep(1)
            
            await self.demo_claim_submission()
            await asyncio.sleep(1)
            
            await self.demo_complete_workflow()
            await asyncio.sleep(1)
            
            await self.demo_fhir_integration()
            await asyncio.sleep(1)
            
            await self.show_ai_examples()
            
            print("\n" + "="*60)
            print("✅ Demo completed successfully!")
            print("🚀 Your MCP server is ready for medical practices!")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            print("💡 Make sure the server is running:")
        print("   .venv\\Scripts\\python.exe start_server_simple.py")

async def main():
    """Main demo function"""
    demo = MCPDemo()
    await demo.run_demo()

if __name__ == "__main__":
    print("Starting MCP Tools Demo...")
    print("Make sure the server is running first!")
    print()
    asyncio.run(main())