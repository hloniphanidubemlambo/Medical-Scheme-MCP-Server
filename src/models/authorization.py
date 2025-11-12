from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AuthorizationRequest(BaseModel):
    member_id: str = Field(..., description="Medical scheme member ID")
    provider_id: str = Field(..., description="Healthcare provider ID")
    procedure_code: str = Field(..., description="Medical procedure code requiring authorization")
    diagnosis_code: Optional[str] = Field(None, description="ICD-10 diagnosis code")
    patient_name: str = Field(..., description="Patient full name")
    requested_date: datetime = Field(..., description="Requested date for procedure")
    urgency: str = Field(default="routine", description="Urgency level: routine, urgent, emergency")
    clinical_notes: Optional[str] = Field(None, description="Additional clinical information")

class AuthorizationResponse(BaseModel):
    authorization_id: str = Field(..., description="Unique authorization identifier")
    status: str = Field(..., description="Authorization status: approved, rejected, pending")
    authorization_number: Optional[str] = Field(None, description="Authorization number if approved")
    approved_amount: Optional[float] = Field(None, description="Approved amount")
    valid_until: Optional[datetime] = Field(None, description="Authorization expiry date")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection")
    reference_number: str = Field(..., description="Scheme reference number")

class BenefitCheck(BaseModel):
    member_id: str = Field(..., description="Medical scheme member ID")
    procedure_code: str = Field(..., description="Medical procedure code")

class BenefitResponse(BaseModel):
    member_id: str
    procedure_code: str
    benefit_available: bool
    remaining_benefit: Optional[float] = None
    annual_limit: Optional[float] = None
    co_payment_required: Optional[float] = None
    authorization_required: bool = False