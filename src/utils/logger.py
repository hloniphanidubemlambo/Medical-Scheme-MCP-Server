import logging
import json
from datetime import datetime
from typing import Any, Dict
from fastapi import Request, Response
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('medical_mcp.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("medical_mcp")

class RequestLogger:
    """Logger for API requests and responses"""
    
    @staticmethod
    def log_request(request: Request, body: Any = None):
        """Log incoming API request"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
        }
        
        if body:
            # Don't log sensitive data
            if isinstance(body, dict):
                safe_body = {k: v for k, v in body.items() if k not in ['api_key', 'password', 'token']}
                log_data["body"] = safe_body
        
        logger.info(f"REQUEST: {json.dumps(log_data, default=str)}")
    
    @staticmethod
    def log_response(response: Response, processing_time: float, body: Any = None):
        """Log API response"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": response.status_code,
            "processing_time_ms": round(processing_time * 1000, 2),
            "headers": dict(response.headers),
        }
        
        if body and response.status_code < 400:
            log_data["response_size"] = len(str(body))
        
        logger.info(f"RESPONSE: {json.dumps(log_data, default=str)}")
    
    @staticmethod
    def log_scheme_interaction(scheme_name: str, operation: str, success: bool, details: Dict[str, Any] = None):
        """Log interactions with medical schemes"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "scheme": scheme_name,
            "operation": operation,
            "success": success,
            "details": details or {}
        }
        
        level = logging.INFO if success else logging.ERROR
        logger.log(level, f"SCHEME_INTERACTION: {json.dumps(log_data, default=str)}")

# Middleware for automatic request/response logging
async def log_requests(request: Request, call_next):
    """Middleware to log all requests and responses"""
    start_time = time.time()
    
    # Log request
    RequestLogger.log_request(request)
    
    # Process request
    response = await call_next(request)
    
    # Log response
    processing_time = time.time() - start_time
    RequestLogger.log_response(response, processing_time)
    
    return response