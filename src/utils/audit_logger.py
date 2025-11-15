# Audit Trail & Compliance Logging
# Implements POPIA/HIPAA compliant audit logging for all data access

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from enum import Enum

class AuditEventType(Enum):
    """Types of auditable events"""
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CLAIM_SUBMISSION = "claim_submission"
    BENEFIT_CHECK = "benefit_check"
    FHIR_ACCESS = "fhir_access"
    CONSENT_GIVEN = "consent_given"
    CONSENT_REVOKED = "consent_revoked"

class AuditLogger:
    """
    Immutable audit trail logger for compliance with POPIA/HIPAA requirements.
    Logs all data access, modifications, and security events.
    """
    
    def __init__(self, log_file: str = "audit_trail.log"):
        self.log_file = Path(log_file)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configure dedicated audit logger"""
        logger = logging.getLogger("audit_trail")
        logger.setLevel(logging.INFO)
        
        # File handler with append mode (never overwrite)
        handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
        handler.setLevel(logging.INFO)
        
        # Structured JSON format for easy parsing
        formatter = logging.Formatter(
            '%(message)s'
        )
        handler.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(handler)
        
        return logger
    
    def log_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """
        Log an audit event with full traceability
        
        Args:
            event_type: Type of event being audited
            user_id: ID of user performing action
            action: Specific action taken
            resource_type: Type of resource accessed (Patient, Claim, etc.)
            resource_id: Specific resource identifier
            patient_id: Patient ID if applicable (for POPIA compliance)
            success: Whether action succeeded
            details: Additional context
            ip_address: Source IP address
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "patient_id": patient_id,
            "success": success,
            "ip_address": ip_address,
            "details": details or {}
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    def log_data_access(
        self,
        user_id: str,
        patient_id: str,
        data_type: str,
        purpose: str,
        ip_address: Optional[str] = None
    ):
        """Log patient data access (POPIA requirement)"""
        self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            user_id=user_id,
            action="read",
            resource_type="PatientData",
            patient_id=patient_id,
            details={"data_type": data_type, "purpose": purpose},
            ip_address=ip_address
        )
    
    def log_consent(
        self,
        patient_id: str,
        consent_type: str,
        granted: bool,
        user_id: str
    ):
        """Log patient consent events (POPIA requirement)"""
        event_type = AuditEventType.CONSENT_GIVEN if granted else AuditEventType.CONSENT_REVOKED
        self.log_event(
            event_type=event_type,
            user_id=user_id,
            action="consent_update",
            resource_type="Consent",
            patient_id=patient_id,
            details={"consent_type": consent_type, "granted": granted}
        )
    
    def log_claim_transaction(
        self,
        user_id: str,
        claim_id: str,
        patient_id: str,
        scheme_name: str,
        amount: float,
        action: str,
        ip_address: Optional[str] = None
    ):
        """Log claim submission/processing"""
        self.log_event(
            event_type=AuditEventType.CLAIM_SUBMISSION,
            user_id=user_id,
            action=action,
            resource_type="Claim",
            resource_id=claim_id,
            patient_id=patient_id,
            details={
                "scheme_name": scheme_name,
                "amount": amount
            },
            ip_address=ip_address
        )
    
    def log_authentication(
        self,
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        failure_reason: Optional[str] = None
    ):
        """Log authentication attempts"""
        self.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            user_id=user_id,
            action="login",
            resource_type="User",
            success=success,
            details={"failure_reason": failure_reason} if not success else {},
            ip_address=ip_address
        )

# Global audit logger instance
audit_logger = AuditLogger()
