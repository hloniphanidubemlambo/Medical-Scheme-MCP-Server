from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
import uvicorn

from src.config.settings import settings
from src.routes.scheme_routes import router as scheme_router
from src.routes.ris_routes import router as ris_router
from src.routes.mcp_routes import router as mcp_router
from src.routes.practice_routes import router as practice_router
from src.routes.fhir_routes import router as fhir_router
from src.routes.analytics_routes import router as analytics_router
from src.utils.logger import log_requests, logger
from src.utils.auth import authenticate_user, create_access_token
from src.utils.error_handlers import register_error_handlers
from src.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware, AuditMiddleware
from src.utils.audit_logger import audit_logger

# Initialize FastAPI app
app = FastAPI(
    title="Medical Scheme MCP Server",
    description="Model Context Protocol Server for South African Medical Schemes with POPIA Compliance",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register error handlers
register_error_handlers(app)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
app.add_middleware(AuditMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.middleware("http")(log_requests)

# Include routers
app.include_router(scheme_router)
app.include_router(ris_router)
app.include_router(mcp_router)
app.include_router(practice_router)
app.include_router(fhir_router)
app.include_router(analytics_router)

# Security
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Medical Scheme MCP Server",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "schemes": "/scheme/available",
            "login": "/auth/login",
            "mcp_tools": "/mcp/tools",
            "practice_dashboard": "/practice/dashboard"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "services": {
            "discovery": "available",
            "gems": "available", 
            "medscheme": "available"
        }
    }

@app.post("/auth/login", response_model=TokenResponse)
async def login(login_request: LoginRequest, request: Request):
    """Authenticate user and return JWT token"""
    success = authenticate_user(login_request.username, login_request.password)
    
    # Log authentication attempt
    audit_logger.log_authentication(
        user_id=login_request.username,
        success=success,
        ip_address=request.client.host,
        failure_reason="Invalid credentials" if not success else None
    )
    
    if not success:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": login_request.username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User {login_request.username} logged in successfully")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400  # 24 hours in seconds
    )

@app.get("/status")
async def server_status():
    """Detailed server status"""
    from src.config.registry import get_available_schemes
    
    return {
        "server": "Medical Scheme MCP Server",
        "status": "operational",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "available_schemes": get_available_schemes(),
        "endpoints": {
            "total": len(app.routes),
            "scheme_operations": [
                "benefit_check",
                "authorization_request", 
                "claim_submission",
                "status_inquiry"
            ],
            "ris_operations": [
                "study_authorization",
                "study_claim_submission",
                "billing_integration"
            ]
        },
        "configuration": {
            "debug_mode": settings.DEBUG,
            "host": settings.HOST,
            "port": settings.PORT
        }
    }

if __name__ == "__main__":
    logger.info("Starting Medical Scheme MCP Server...")
    logger.info(f"Server configuration: Host={settings.HOST}, Port={settings.PORT}, Debug={settings.DEBUG}")
    
    uvicorn.run(
        "src.server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )