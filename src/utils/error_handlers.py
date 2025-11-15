# Global Error Handlers for FastAPI

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
from datetime import datetime
from typing import Union

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class SchemeConnectionError(APIError):
    """Medical scheme connection failed"""
    def __init__(self, scheme_name: str, message: str):
        super().__init__(
            message=f"Failed to connect to {scheme_name}: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"scheme": scheme_name}
        )

class AuthorizationError(APIError):
    """Authorization request failed"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )

class FHIRIntegrationError(APIError):
    """FHIR integration error"""
    def __init__(self, message: str, fhir_response: dict = None):
        super().__init__(
            message=f"FHIR integration error: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"fhir_response": fhir_response}
        )

async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors"""
    logger.error(f"API Error: {exc.message}", extra={
        "status_code": exc.status_code,
        "path": request.url.path,
        "details": exc.details
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "details": exc.details
        }
    )

async def validation_error_handler(request: Request, exc: Union[RequestValidationError, ValidationError]):
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error on {request.url.path}", extra={"errors": errors})
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "message": "Request data validation failed",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "validation_errors": errors
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "request_id": getattr(request.state, "request_id", None)
        }
    )

def register_error_handlers(app):
    """Register all error handlers with FastAPI app"""
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
