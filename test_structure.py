#!/usr/bin/env python3
"""
Test script to verify project structure and basic imports
"""
import os
import sys
from pathlib import Path

def test_project_structure():
    """Test that all required files and directories exist"""
    print("🔍 Testing project structure...")
    
    required_files = [
        "requirements.txt",
        ".env",
        "src/server.py",
        "src/config/settings.py",
        "src/connectors/base_connector.py",
        "src/models/claim.py",
        "src/models/authorization.py",
        "README.md",
        "Dockerfile"
    ]
    
    required_dirs = [
        "src",
        "src/config",
        "src/connectors", 
        "src/models",
        "src/routes",
        "src/utils",
        "tests"
    ]
    
    # Check directories
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory: {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")
    
    # Check files
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
    
    print("\n📊 Project Structure Summary:")
    print(f"   📁 Total directories: {len([d for d in required_dirs if os.path.exists(d)])}/{len(required_dirs)}")
    print(f"   📄 Total files: {len([f for f in required_files if os.path.exists(f)])}/{len(required_files)}")

def test_python_syntax():
    """Test Python syntax of main files"""
    print("\n🐍 Testing Python syntax...")
    
    python_files = [
        "src/server.py",
        "src/config/settings.py", 
        "src/connectors/base_connector.py",
        "src/models/claim.py",
        "run_server.py"
    ]
    
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), file_path, 'exec')
                print(f"✅ Syntax OK: {file_path}")
            except SyntaxError as e:
                print(f"❌ Syntax Error in {file_path}: {e}")
            except Exception as e:
                print(f"⚠️  Warning in {file_path}: {e}")
        else:
            print(f"❌ File not found: {file_path}")

def show_next_steps():
    """Show next steps for setup"""
    print("\n🚀 Next Steps:")
    print("1. Install Python dependencies:")
    print("   py -m venv .venv")
    print("   .venv\\Scripts\\activate")
    print("   pip install -r requirements.txt")
    print()
    print("2. Configure environment:")
    print("   Edit .env file with your API keys")
    print()
    print("3. Start the server:")
    print("   py run_server.py")
    print("   OR")
    print("   run_server.bat")
    print()
    print("4. Test the API:")
    print("   Open http://localhost:8000/docs")
    print("   Use /health endpoint to verify server is running")

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 Medical Scheme MCP Server - Structure Test")
    print("=" * 60)
    
    test_project_structure()
    test_python_syntax()
    show_next_steps()
    
    print("\n" + "=" * 60)
    print("✅ Structure test completed!")
    print("=" * 60)