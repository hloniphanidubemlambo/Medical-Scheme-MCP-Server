# Security Middleware for POPIA/HIPAA Compliance

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse and ensure fair resource usage.
    Implements sliding window rate limiting per IP address.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable):
        client_ip = request.client.host
        now = datetime.now()
        
        # Clean old requests (older than 1 minute)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "retry_after": 60
                }
            )
        
        # Add current request
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Relaxed CSP for API documentation (Swagger UI needs inline scripts and CDN resources)
        # In production, you may want to restrict this further or serve docs from a separate domain
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc") or request.url.path.startswith("/openapi.json"):
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://cdn.jsdelivr.net"
        else:
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

class AuditMiddleware(BaseHTTPMiddleware):
    """Audit all API requests for compliance"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        from src.utils.audit_logger import audit_logger, AuditEventType
        
        start_time = time.time()
        
        # Extract user info if available
        user_id = "anonymous"
        if hasattr(request.state, "user"):
            user_id = request.state.user
        
        try:
            response = await call_next(request)
            
            # Log successful API access
            if request.url.path.startswith(("/fhir/", "/scheme/", "/mcp/")):
                audit_logger.log_event(
                    event_type=AuditEventType.DATA_ACCESS,
                    user_id=user_id,
                    action=request.method,
                    resource_type=request.url.path.split('/')[1],
                    success=True,
                    details={
                        "path": request.url.path,
                        "method": request.method,
                        "status_code": response.status_code,
                        "duration_ms": round((time.time() - start_time) * 1000, 2)
                    },
                    ip_address=request.client.host
                )
            
            return response
            
        except Exception as e:
            # Log failed access attempts
            audit_logger.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=user_id,
                action=request.method,
                resource_type=request.url.path.split('/')[1] if len(request.url.path.split('/')) > 1 else "unknown",
                success=False,
                details={
                    "path": request.url.path,
                    "error": str(e)
                },
                ip_address=request.client.host
            )
            raise
