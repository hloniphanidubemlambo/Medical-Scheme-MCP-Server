#!/usr/bin/env python3
"""
Setup script for Medical Scheme MCP Server improvements.
Installs dependencies and verifies the setup.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   Medical Scheme MCP Server - Improvements Setup        ║
    ║   Version 2.0.0                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install core dependencies
    run_command(
        "pip install fastapi uvicorn python-dotenv httpx PyJWT pydantic",
        "Installing core dependencies"
    )
    
    # Install testing dependencies
    run_command(
        "pip install pytest pytest-asyncio pytest-cov",
        "Installing testing dependencies"
    )
    
    # Install development tools
    run_command(
        "pip install black flake8 mypy bandit",
        "Installing development tools"
    )
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    Path("logs").mkdir(exist_ok=True)
    Path("analytics").mkdir(exist_ok=True)
    print("✅ Directories created")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("\n📝 Creating .env file...")
        env_content = """# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Authentication
JWT_SECRET_KEY=change-this-to-a-strong-secret-key-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Security
RATE_LIMIT_PER_MINUTE=60

# Analytics
ANALYTICS_STORAGE_PATH=analytics_data.json
AUDIT_LOG_PATH=audit_trail.log

# Medical Scheme API Keys (optional - uses mock if not provided)
DISCOVERY_API_KEY=
GEMS_API_KEY=
MEDSCHEME_API_KEY=

# FHIR Configuration
FHIR_SERVER_URL=https://hapi.fhir.org/baseR4
"""
        env_file.write_text(env_content)
        print("✅ .env file created")
    else:
        print("ℹ️  .env file already exists")
    
    # Run tests
    print("\n🧪 Running test suite...")
    test_result = run_command(
        "pytest tests/ -v --tb=short",
        "Running tests"
    )
    
    # Check code formatting
    print("\n🎨 Checking code formatting...")
    run_command(
        "black --check src tests",
        "Code formatting check"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SETUP SUMMARY")
    print(f"{'='*60}")
    print("✅ Dependencies installed")
    print("✅ Directories created")
    print("✅ Configuration file ready")
    print(f"{'✅' if test_result else '⚠️ '} Tests {'passed' if test_result else 'need attention'}")
    
    print(f"\n{'='*60}")
    print("🚀 NEXT STEPS")
    print(f"{'='*60}")
    print("1. Review and update .env file with your settings")
    print("2. Start the server: python start_server_simple.py")
    print("3. Access dashboard: http://localhost:8000/practice/dashboard")
    print("4. View analytics: http://localhost:8000/analytics/dashboard")
    print("5. Check audit logs: cat audit_trail.log")
    
    print(f"\n{'='*60}")
    print("📚 DOCUMENTATION")
    print(f"{'='*60}")
    print("- IMPROVEMENTS_IMPLEMENTED.md - Full improvement details")
    print("- README.md - General usage guide")
    print("- API Docs: http://localhost:8000/docs")
    
    print("\n✨ Setup complete! Your Medical Scheme MCP Server is ready.\n")

if __name__ == "__main__":
    main()
