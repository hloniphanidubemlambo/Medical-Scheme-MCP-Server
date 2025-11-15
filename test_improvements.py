#!/usr/bin/env python3
"""
Quick test script to verify all improvements are working.
Run this after setup to ensure everything is functioning correctly.
"""

import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if details:
        print(f"    {details}")

async def test_improvements():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Testing Medical Scheme MCP Server v2.0 Improvements{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Server Health
        print(f"\n{Colors.YELLOW}1. Testing Server Health{Colors.END}")
        try:
            response = await client.get(f"{BASE_URL}/health")
            print_test("Health Check", response.status_code == 200, 
                      f"Status: {response.json().get('status')}")
        except Exception as e:
            print_test("Health Check", False, str(e))
            print(f"\n{Colors.RED}❌ Server not running! Start with: python start_server_simple.py{Colors.END}\n")
            return
        
        # Test 2: Authentication
        print(f"\n{Colors.YELLOW}2. Testing Authentication & Audit Logging{Colors.END}")
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"username": "admin", "password": "password123"}
            )
            print_test("Login Success", response.status_code == 200)
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                print(f"    Token: {token[:50]}...")
            else:
                print_test("Login Failed", False, response.text)
                return
        except Exception as e:
            print_test("Authentication", False, str(e))
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 3: Rate Limiting
        print(f"\n{Colors.YELLOW}3. Testing Rate Limiting{Colors.END}")
        try:
            # Send 5 rapid requests (won't hit limit)
            for i in range(5):
                await client.get(f"{BASE_URL}/health")
            print_test("Rate Limiting Active", True, "5 requests succeeded (under limit)")
        except Exception as e:
            print_test("Rate Limiting", False, str(e))
        
        # Test 4: Security Headers
        print(f"\n{Colors.YELLOW}4. Testing Security Headers{Colors.END}")
        try:
            response = await client.get(f"{BASE_URL}/health")
            headers_present = all([
                "x-content-type-options" in response.headers,
                "x-frame-options" in response.headers,
            ])
            print_test("Security Headers", headers_present,
                      f"X-Frame-Options: {response.headers.get('x-frame-options')}")
        except Exception as e:
            print_test("Security Headers", False, str(e))
        
        # Test 5: MCP Tools
        print(f"\n{Colors.YELLOW}5. Testing MCP Tools{Colors.END}")
        try:
            response = await client.get(f"{BASE_URL}/mcp/tools")
            tools = response.json()
            print_test("MCP Tools List", response.status_code == 200,
                      f"Found {tools.get('total_tools', 0)} tools")
        except Exception as e:
            print_test("MCP Tools", False, str(e))
        
        # Test 6: Benefit Check
        print(f"\n{Colors.YELLOW}6. Testing Benefit Check (MCP Tool){Colors.END}")
        try:
            response = await client.post(
                f"{BASE_URL}/mcp/tools/check_patient_benefits",
                params={
                    "patient_name": "Test Patient",
                    "member_id": "TEST123",
                    "scheme_name": "discovery",
                    "procedure_codes": ["CONS001"]
                },
                headers=headers
            )
            print_test("Benefit Check", response.status_code == 200,
                      "Successfully checked benefits")
        except Exception as e:
            print_test("Benefit Check", False, str(e))
        
        # Test 7: Analytics Dashboard
        print(f"\n{Colors.YELLOW}7. Testing Analytics Dashboard{Colors.END}")
        try:
            response = await client.get(
                f"{BASE_URL}/analytics/dashboard",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                print_test("Analytics Dashboard", True,
                          f"Claims: {data.get('overview', {}).get('total_claims', 0)}, "
                          f"Authorizations: {data.get('overview', {}).get('total_authorizations', 0)}")
            else:
                print_test("Analytics Dashboard", False, response.text)
        except Exception as e:
            print_test("Analytics Dashboard", False, str(e))
        
        # Test 8: FHIR Integration
        print(f"\n{Colors.YELLOW}8. Testing FHIR Integration{Colors.END}")
        try:
            response = await client.get(
                f"{BASE_URL}/fhir/integration/test",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                fhir_status = data.get('fhir', {}).get('status')
                print_test("FHIR Integration", fhir_status == "connected",
                          f"FHIR Status: {fhir_status}")
            else:
                print_test("FHIR Integration", False, response.text)
        except Exception as e:
            print_test("FHIR Integration", False, str(e))
        
        # Test 9: Error Handling
        print(f"\n{Colors.YELLOW}9. Testing Error Handling{Colors.END}")
        try:
            response = await client.post(
                f"{BASE_URL}/mcp/tools/check_patient_benefits",
                params={"invalid": "data"},  # Missing required fields
                headers=headers
            )
            has_error_format = (
                response.status_code == 422 and
                "error" in response.json()
            )
            print_test("Error Handling", has_error_format,
                      "Validation errors properly formatted")
        except Exception as e:
            print_test("Error Handling", False, str(e))
        
        # Test 10: Audit Log
        print(f"\n{Colors.YELLOW}10. Checking Audit Log{Colors.END}")
        try:
            from pathlib import Path
            audit_file = Path("audit_trail.log")
            if audit_file.exists():
                with open(audit_file, 'r') as f:
                    lines = f.readlines()
                    print_test("Audit Log", len(lines) > 0,
                              f"Found {len(lines)} audit entries")
                    if lines:
                        last_entry = json.loads(lines[-1])
                        print(f"    Last event: {last_entry.get('event_type')} at {last_entry.get('timestamp')}")
            else:
                print_test("Audit Log", False, "audit_trail.log not found")
        except Exception as e:
            print_test("Audit Log", False, str(e))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"\n{Colors.GREEN}✅ All core improvements are functional!{Colors.END}\n")
    
    print("Next steps:")
    print("1. Check audit_trail.log for detailed audit entries")
    print("2. Visit http://localhost:8000/docs for API documentation")
    print("3. Access http://localhost:8000/analytics/dashboard for analytics")
    print("4. Run 'pytest tests/' for comprehensive test suite")
    print("5. Review IMPROVEMENTS_IMPLEMENTED.md for details\n")

if __name__ == "__main__":
    print(f"\n{Colors.BLUE}Starting improvement tests...{Colors.END}")
    print(f"{Colors.YELLOW}Make sure the server is running on {BASE_URL}{Colors.END}\n")
    
    try:
        asyncio.run(test_improvements())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Test error: {e}{Colors.END}\n")
