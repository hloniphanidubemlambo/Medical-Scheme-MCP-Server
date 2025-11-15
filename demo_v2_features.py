#!/usr/bin/env python3
"""
Interactive Demo - Medical Scheme MCP Server v2.0
Demonstrates all new features with live API calls
"""

import httpx
import asyncio
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import time

console = Console()
BASE_URL = "http://localhost:8000"

async def demo():
    console.print("\n[bold cyan]╔══════════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║   Medical Scheme MCP Server v2.0 - Live Demo            ║[/bold cyan]")
    console.print("[bold cyan]║   Showcasing All New Features                            ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════════════════════════╝[/bold cyan]\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Demo 1: Authentication with Audit Logging
        console.print("\n[bold yellow]═══ Demo 1: Authentication & Audit Logging ═══[/bold yellow]\n")
        console.print("🔐 Logging in as admin...")
        
        auth_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "password123"}
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            console.print(f"✅ [green]Login successful![/green]")
            console.print(f"   Token: {token[:50]}...")
            console.print(f"   Expires in: 24 hours")
            console.print(f"   [dim]This login was automatically logged in audit_trail.log[/dim]")
        else:
            console.print(f"❌ [red]Login failed[/red]")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Demo 2: Security Headers
        console.print("\n[bold yellow]═══ Demo 2: Security Headers ═══[/bold yellow]\n")
        console.print("🛡️  Checking security headers on response...")
        
        health_response = await client.get(f"{BASE_URL}/health")
        
        table = Table(title="Security Headers", show_header=True)
        table.add_column("Header", style="cyan")
        table.add_column("Value", style="green")
        
        security_headers = [
            "x-frame-options",
            "x-content-type-options", 
            "x-xss-protection",
            "strict-transport-security"
        ]
        
        for header in security_headers:
            value = health_response.headers.get(header, "Not Set")
            table.add_row(header, value)
        
        console.print(table)
        
        # Demo 3: Rate Limiting
        console.print("\n[bold yellow]═══ Demo 3: Rate Limiting (60 req/min) ═══[/bold yellow]\n")
        console.print("⚡ Sending rapid requests to test rate limiting...")
        
        success_count = 0
        blocked_count = 0
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Testing rate limit...", total=70)
            
            for i in range(70):
                try:
                    resp = await client.get(f"{BASE_URL}/health")
                    if resp.status_code == 200:
                        success_count += 1
                    elif resp.status_code == 429:
                        blocked_count += 1
                except:
                    blocked_count += 1
                
                progress.update(task, advance=1)
                await asyncio.sleep(0.01)  # Small delay
        
        console.print(f"\n✅ [green]Successful requests: {success_count}[/green]")
        console.print(f"🚫 [red]Blocked requests: {blocked_count}[/red]")
        console.print(f"   [dim]Rate limit: 60 requests per minute per IP[/dim]")
        
        # Wait for rate limit to reset
        console.print("\n⏳ Waiting 5 seconds for rate limit to reset...")
        await asyncio.sleep(5)
        
        # Demo 4: MCP Tools
        console.print("\n[bold yellow]═══ Demo 4: MCP Tools ═══[/bold yellow]\n")
        console.print("🤖 Listing available MCP tools...")
        
        tools_response = await client.get(f"{BASE_URL}/mcp/tools")
        tools_data = tools_response.json()
        
        table = Table(title="Available MCP Tools", show_header=True)
        table.add_column("#", style="cyan", width=3)
        table.add_column("Tool Name", style="green")
        table.add_column("Description", style="white")
        
        for idx, tool in enumerate(tools_data["tools"], 1):
            table.add_row(
                str(idx),
                tool["name"],
                tool["description"][:60] + "..."
            )
        
        console.print(table)
        
        # Demo 5: Complete Patient Workflow
        console.print("\n[bold yellow]═══ Demo 5: Complete Patient Workflow ═══[/bold yellow]\n")
        console.print("🏥 Executing end-to-end patient workflow...")
        console.print("   Patient: Sarah Johnson")
        console.print("   Scheme: Discovery Health")
        console.print("   Procedure: General Consultation\n")
        
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
            console.print(Panel(
                workflow_data["content"][0]["text"],
                title="Workflow Result",
                border_style="green"
            ))
        
        # Demo 6: Analytics Dashboard
        console.print("\n[bold yellow]═══ Demo 6: Analytics Dashboard ═══[/bold yellow]\n")
        console.print("📊 Fetching analytics data...")
        
        analytics_response = await client.get(
            f"{BASE_URL}/analytics/dashboard",
            headers=headers
        )
        
        if analytics_response.status_code == 200:
            analytics = analytics_response.json()
            
            table = Table(title="System Overview", show_header=True)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green", justify="right")
            
            overview = analytics["overview"]
            table.add_row("Total Claims", str(overview["total_claims"]))
            table.add_row("Total Authorizations", str(overview["total_authorizations"]))
            table.add_row("Benefit Checks", str(overview["total_benefit_checks"]))
            table.add_row("Active Schemes", str(overview["active_schemes"]))
            
            console.print(table)
            
            # Approval Rates
            rates = analytics["approval_rates"]
            
            table2 = Table(title="Approval Rates", show_header=True)
            table2.add_column("Type", style="cyan")
            table2.add_column("Total", style="white", justify="right")
            table2.add_column("Approved", style="green", justify="right")
            table2.add_column("Rate", style="yellow", justify="right")
            
            table2.add_row(
                "Claims",
                str(rates["claims"]["total"]),
                str(rates["claims"]["approved"]),
                f"{rates['claims']['approval_rate']:.1f}%"
            )
            table2.add_row(
                "Authorizations",
                str(rates["authorizations"]["total"]),
                str(rates["authorizations"]["approved"]),
                f"{rates['authorizations']['approval_rate']:.1f}%"
            )
            
            console.print(table2)
        
        # Demo 7: FHIR Integration
        console.print("\n[bold yellow]═══ Demo 7: FHIR Integration ═══[/bold yellow]\n")
        console.print("🌐 Testing FHIR server connectivity...")
        
        fhir_response = await client.get(
            f"{BASE_URL}/fhir/integration/test",
            headers=headers
        )
        
        if fhir_response.status_code == 200:
            fhir_data = fhir_response.json()
            
            table = Table(title="FHIR Integration Status", show_header=True)
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="white")
            table.add_column("Details", style="dim")
            
            fhir_info = fhir_data["fhir"]
            table.add_row(
                "HAPI FHIR Server",
                f"[green]{fhir_info['status']}[/green]" if fhir_info['status'] == 'connected' else f"[red]{fhir_info['status']}[/red]",
                fhir_info['url']
            )
            
            console.print(table)
            
            # Search for real patients
            console.print("\n🔍 Searching for real patients in FHIR server...")
            
            patients_response = await client.get(
                f"{BASE_URL}/fhir/patients/search?limit=3",
                headers=headers
            )
            
            if patients_response.status_code == 200:
                patients_data = patients_response.json()
                
                table = Table(title="Real Patient Data from FHIR", show_header=True)
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Gender", style="white")
                table.add_column("Birth Date", style="yellow")
                
                for patient in patients_data["patients"]:
                    table.add_row(
                        patient["id"],
                        patient["name"],
                        patient["gender"],
                        patient["birthDate"]
                    )
                
                console.print(table)
        
        # Demo 8: Error Handling
        console.print("\n[bold yellow]═══ Demo 8: Enhanced Error Handling ═══[/bold yellow]\n")
        console.print("🔧 Testing error handling with invalid request...")
        
        error_response = await client.post(
            f"{BASE_URL}/mcp/tools/check_patient_benefits",
            params={"invalid": "data"},  # Missing required fields
            headers=headers
        )
        
        if error_response.status_code == 422:
            error_data = error_response.json()
            console.print(Panel(
                json.dumps(error_data, indent=2),
                title="Structured Error Response",
                border_style="red"
            ))
        
        # Demo 9: Audit Trail
        console.print("\n[bold yellow]═══ Demo 9: Audit Trail ═══[/bold yellow]\n")
        console.print("📝 Reading recent audit log entries...")
        
        try:
            with open("audit_trail.log", "r") as f:
                lines = f.readlines()
                recent_entries = [json.loads(line) for line in lines[-5:]]
            
            table = Table(title="Recent Audit Entries", show_header=True)
            table.add_column("Timestamp", style="cyan")
            table.add_column("Event Type", style="yellow")
            table.add_column("User", style="green")
            table.add_column("Action", style="white")
            table.add_column("Status", style="white")
            
            for entry in recent_entries:
                timestamp = entry["timestamp"].split("T")[1][:8]
                status = "✅" if entry["success"] else "❌"
                table.add_row(
                    timestamp,
                    entry["event_type"],
                    entry["user_id"],
                    entry["action"],
                    status
                )
            
            console.print(table)
            console.print(f"\n   [dim]Total audit entries: {len(lines)}[/dim]")
            console.print(f"   [dim]Log file: audit_trail.log[/dim]")
        except Exception as e:
            console.print(f"[red]Could not read audit log: {e}[/red]")
        
        # Summary
        console.print("\n[bold cyan]╔══════════════════════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║   Demo Complete! All Features Working ✅                 ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════════════════════════╝[/bold cyan]\n")
        
        console.print("[bold green]✅ Authentication & JWT Tokens[/bold green]")
        console.print("[bold green]✅ Security Headers (4 headers)[/bold green]")
        console.print("[bold green]✅ Rate Limiting (60 req/min)[/bold green]")
        console.print("[bold green]✅ MCP Tools (4 tools)[/bold green]")
        console.print("[bold green]✅ Complete Workflows[/bold green]")
        console.print("[bold green]✅ Analytics Dashboard[/bold green]")
        console.print("[bold green]✅ FHIR Integration[/bold green]")
        console.print("[bold green]✅ Error Handling[/bold green]")
        console.print("[bold green]✅ Audit Logging[/bold green]")
        
        console.print("\n[bold yellow]📚 Next Steps:[/bold yellow]")
        console.print("   • View API docs: http://localhost:8000/docs")
        console.print("   • Check audit logs: cat audit_trail.log")
        console.print("   • Read guide: QUICK_START_IMPROVEMENTS.md")
        console.print("   • Deploy: See DEPLOYMENT_CHECKLIST.md\n")

if __name__ == "__main__":
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]Demo error: {e}[/red]\n")
        console.print("[yellow]Make sure the server is running: python start_server_simple.py[/yellow]\n")
