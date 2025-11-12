#!/usr/bin/env python3
"""
Medical Scheme MCP Server Startup Script
"""
import sys
import os
import uvicorn
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import settings
from src.utils.logger import logger

def main():
    """Main entry point for the server"""
    logger.info("=" * 60)
    logger.info("🏥 Medical Scheme MCP Server Starting...")
    logger.info("=" * 60)
    logger.info(f"📍 Host: {settings.HOST}")
    logger.info(f"🔌 Port: {settings.PORT}")
    logger.info(f"🐛 Debug Mode: {settings.DEBUG}")
    logger.info(f"📊 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 60)
    
    try:
        uvicorn.run(
            "src.server:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info" if not settings.DEBUG else "debug",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()