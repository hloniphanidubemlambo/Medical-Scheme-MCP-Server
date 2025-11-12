#!/usr/bin/env python3
"""
Simple server starter that bypasses import issues
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import uvicorn
    print("✅ uvicorn imported successfully")
    
    # Try to import our server
    from src.server import app
    print("✅ Server app imported successfully")
    
    print("🚀 Starting Medical Scheme MCP Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🏥 Practice Dashboard: http://localhost:8000/practice/dashboard")
    
    uvicorn.run(
        "src.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid issues
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the virtual environment")
    sys.exit(1)
except Exception as e:
    print(f"❌ Server error: {e}")
    sys.exit(1)