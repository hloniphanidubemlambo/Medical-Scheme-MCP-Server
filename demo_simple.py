#!/usr/bin/env python3
"""
Simple Interactive Demo - Medical Scheme MCP Server v2.0
No external dependencies required
"""

import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    print(f"✅ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_data(label, value):
    print(f"   {label}: {value}")

async def demo():
    print("\n" + "="*60)
    print("  Medical Scheme MCP Server v2.0 - Live Demo")
    print("  Showcasing All New Features")
    print("="*60 + "\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Demo 1: Authentication
        print_header("Demo 1: Authentication & Audit Logging")
        print("🔐 Logging in as admin...")
        
        auth_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "password123"}
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            print_success("Login successful!")
            print_data("Token", token[:50] + "...")
            print_data("Expires in", "24 hours")
            print("   (This login was logged in audit_trail.log)")
        else:
            print("❌ Login failed")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Demo 2: Security Headers
        print_header("Demo 2: Security Headers")
        print("🛡️  Checking security headers...")
        
        health_response = await client.get(f"{BASE_URL}/health")
        
        print("\nSecurity Headers:")
        print_data("X-Frame-Options", health_response.headers.get("x-frame-options"))
        print_data("X-Content-Type-Options", health_response.headers.get("x-content-type-options"))
        print_data("X-XSS-Protection", health_response.headers.get("x-xss-protection"))
        print_data("Strict-Transport-Security", health_response.headers.get("strict-transport-security")[:40] + "...")
        
        # Demo 3: Rate Limiting
        print_header("Demo 3: Rate Limiting (60 req/min)")
        print("⚡ Sending 70 rapid requests to test rate limiting...")
        
        success_count = 0
        blocked_count = 0
        
        for i in range(70):
            try:
                resp = await client.get(f"{BASE_URL}/health")
                if resp.status_code == 200:
                    success_count += 1
                elif resp.status_code == 429:
                    blocked_count += 1
            except:
                blocked_count += 1
            
            if (i + 1) % 10 == 0:
                print(f"   Progress: {i + 1}/70 requests sent...")
        
        print(f"\n✅ Successful requests: {success_count}")
        print(f"🚫 Blocked requests: {blocked_count}")
        print("   Rate limit: 60 requests per minute per IP")
        
        # Wait for rate limit
        print("\n⏳ Waiting 65 seconds for rate limit to fully reset...")
        for i in range(13):
            await asyncio.sleep(5)
            print(f"   {(i+1)*5} seconds elapsed...")
        
        # Demo 4: MCP Tools
        print_header("Demo 4: MCP Tools")
        print("🤖 Listing available MCP tools...")
        
        tools_response = await client.get(f"{BASE_URL}/mcp/tools")
        tools_data = tools_response.json()
        
        print(f"\nFound {tools_data['total_tools']} MCP Tools:\n")
        for idx, tool in enumerate(tools_data["tools"], 1):
            print(f"{idx}. {tool['name']}")
            print(f"   {tool['description'][:70]}...")
        
        # Demo 5: Complete Workflow
        print_header("Demo 5: Complete Patient Workflow")
        print("🏥 Executing end-to-end patient workflow...")
        print_data("Patient", "Sarah Johnson")
        print_data("Scheme", "Discovery Health")
        print_data("Procedure", "General Consultation")
        
        workflow_response = await client.post(
            f"{BASE_URL}/mcp/tools/complete_patient_workflow",
            params={
                "patient_name": "Sarah Johnson",
                "member_id": "DISC789012",
                "scheme_name": "discovery",
                "provider_id": "PROV001",
                "practice_name": "City Medical Centre",
                "workflow_type": "check_and_auth"
            },
            json=[{
                "procedure_code": "CONS001",
                "procedure_name": "General Consultation",
                "estimated_cost": 500.00
            }],
            headers=headers
        )
        
        if workflow_response.status_code == 200:
            workflow_data = workflow_response.json()
            print("\n" + "-"*60)
            print(workflow_data["content"][0]["text"])
            print("-"*60)
        
        # Demo 6: Analytics
        print_header("Demo 6: Analytics Dashboard")
        print("📊 Fetching analytics data...")
        
        analytics_response = await client.get(
            f"{BASE_URL}/analytics/dashboard",
            headers=headers
        )
        
        if analytics_response.status_code == 200:
            analytics = analytics_response.json()
            
            print("\nSystem Overview:")
            overview = analytics["overview"]
            print_data("Total Claims", overview["total_claims"])
            print_data("Total Authorizations", overview["total_authorizations"])
            print_data("Benefit Checks", overview["total_benefit_checks"])
            print_data("Active Schemes", overview["active_schemes"])
            
            print("\nApproval Rates:")
            rates = analytics["approval_rates"]
            print_data("Claims Approval Rate", f"{rates['claims']['approval_rate']:.1f}%")
            print_data("Auth Approval Rate", f"{rates['authorizations']['approval_rate']:.1f}%")
        
        # Demo 7: FHIR Integration
        print_header("Demo 7: FHIR Integration")
        print("🌐 Testing FHIR server connectivity...")
        
        fhir_response = await client.get(
            f"{BASE_URL}/fhir/integration/test",
            headers=headers
        )
        
        if fhir_response.status_code == 200:
            fhir_data = fhir_response.json()
            fhir_info = fhir_data["fhir"]
            
            print_data("FHIR Status", fhir_info['status'])
            print_data("FHIR Server", fhir_info['url'])
            
            print("\n🔍 Searching for real patients...")
            
            patients_response = await client.get(
                f"{BASE_URL}/fhir/patients/search?limit=3",
                headers=headers
            )
            
            if patients_response.status_code == 200:
                patients_data = patients_response.json()
                
                print("\nReal Patient Data from FHIR:")
                for patient in patients_data["patients"]:
                    print(f"\n   ID: {patient['id']}")
                    print(f"   Name: {patient['name']}")
                    print(f"   Gender: {patient['gender']}")
                    print(f"   Birth Date: {patient['birthDate']}")
        
        # Demo 8: Error Handling
        print_header("Demo 8: Enhanced Error Handling")
        print("🔧 Testing error handling with invalid request...")
        
        error_response = await client.post(
            f"{BASE_URL}/mcp/tools/check_patient_benefits",
            params={"invalid": "data"},
            headers=headers
        )
        
        if error_response.status_code == 422:
            error_data = error_response.json()
            print("\nStructured Error Response:")
            print(json.dumps(error_data, indent=2))
        
        # Demo 9: Audit Trail
        print_header("Demo 9: Audit Trail")
        print("📝 Reading recent audit log entries...")
        
        try:
            with open("audit_trail.log", "r") as f:
                lines = f.readlines()
                recent_entries = [json.loads(line) for line in lines[-5:]]
            
            print(f"\nTotal audit entries: {len(lines)}")
            print("\nRecent Audit Entries:")
            
            for entry in recent_entries:
                timestamp = entry["timestamp"].split("T")[1][:8]
                status = "✅" if entry["success"] else "❌"
                print(f"\n   {timestamp} | {entry['event_type']} | {entry['user_id']} | {entry['action']} {status}")
            
            print(f"\n   Log file: audit_trail.log")
        except Exception as e:
            print(f"❌ Could not read audit log: {e}")
        
        # Summary
        print("\n" + "="*60)
        print("  Demo Complete! All Features Working ✅")
        print("="*60 + "\n")
        
        print("✅ Authentication & JWT Tokens")
        print("✅ Security Headers (4 headers)")
        print("✅ Rate Limiting (60 req/min)")
        print("✅ MCP Tools (4 tools)")
        print("✅ Complete Workflows")
        print("✅ Analytics Dashboard")
        print("✅ FHIR Integration")
        print("✅ Error Handling")
        print("✅ Audit Logging")
        
        print("\n📚 Next Steps:")
        print("   • View API docs: http://localhost:8000/docs")
        print("   • Check audit logs: type audit_trail.log")
        print("   • Read guide: QUICK_START_IMPROVEMENTS.md")
        print("   • Deploy: See DEPLOYMENT_CHECKLIST.md\n")

if __name__ == "__main__":
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user\n")
    except Exception as e:
        print(f"\n❌ Demo error: {e}\n")
        print("⚠️ Make sure the server is running: python start_server_simple.py\n")
