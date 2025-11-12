from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ClaimItem(BaseModel):
    procedure_code: str = Field(..., description="Medical procedure code")
    description: str = Field(..., description="Procedure description")
    quantity: int = Field(default=1, description="Number of procedures")
    unit_price: float = Field(..., description="Price per unit")
    total_amount: float = Field(..., description="Total amount for this item")

class Claim(BaseModel):
    claim_id: Optional[str] = Field(None, description="Unique claim identifier")
    member_id: str = Field(..., description="Medical scheme member ID")
    provider_id: str = Field(..., description="Healthcare provider ID")
    patient_name: str = Field(..., description="Patient full name")
    date_of_service: datetime = Field(..., description="Date when service was provided")
    claim_items: List[ClaimItem] = Field(..., description="List of claimed procedures")
    total_claim_amount: float = Field(..., description="Total claim amount")
    diagnosis_code: Optional[str] = Field(None, description="ICD-10 diagnosis code")
    authorization_number: Optional[str] = Field(None, description="Pre-authorization number if applicable")

class ClaimResponse(BaseModel):
    claim_id: str
    status: str  # "approved", "rejected", "pending"
    approved_amount: Optional[float] = None
    rejection_reason: Optional[str] = None
    reference_number: str
    processed_date: datetime