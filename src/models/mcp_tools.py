from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class MCPTool(BaseModel):
    """Base MCP tool definition"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    inputSchema: Dict[str, Any] = Field(..., description="JSON schema for tool input")

class MCPToolResult(BaseModel):
    """MCP tool execution result"""
    content: List[Dict[str, Any]] = Field(..., description="Tool result content")
    isError: bool = Field(default=False, description="Whether the result is an error")

# Practice-specific models for MCP tools
class PracticeInfo(BaseModel):
    """Practice information for MCP tools"""
    practice_id: str = Field(..., description="Unique practice identifier")
    practice_name: str = Field(..., description="Practice name")
    provider_id: str = Field(..., description="Healthcare provider ID")
    contact_person: str = Field(..., description="Contact person name")
    phone: Optional[str] = Field(None, description="Practice phone number")
    email: Optional[str] = Field(None, description="Practice email")

class PatientInfo(BaseModel):
    """Patient information for MCP tools"""
    patient_id: str = Field(..., description="Patient identifier")
    patient_name: str = Field(..., description="Patient full name")
    member_id: str = Field(..., description="Medical scheme member ID")
    scheme_name: str = Field(..., description="Medical scheme name (discovery, gems, medscheme)")
    id_number: Optional[str] = Field(None, description="Patient ID number")
    date_of_birth: Optional[datetime] = Field(None, description="Patient date of birth")

class ProcedureInfo(BaseModel):
    """Procedure information for MCP tools"""
    procedure_code: str = Field(..., description="Medical procedure code")
    procedure_name: str = Field(..., description="Procedure description")
    estimated_cost: float = Field(..., description="Estimated procedure cost")
    urgency: str = Field(default="routine", description="Urgency: routine, urgent, emergency")
    diagnosis_code: Optional[str] = Field(None, description="ICD-10 diagnosis code")
    clinical_notes: Optional[str] = Field(None, description="Additional clinical information")

class QuickAuthRequest(BaseModel):
    """Quick authorization request for practices"""
    patient: PatientInfo
    procedure: ProcedureInfo
    practice: PracticeInfo
    requested_date: datetime = Field(default_factory=datetime.now, description="Requested procedure date")

class QuickBenefitCheck(BaseModel):
    """Quick benefit check for practices"""
    patient: PatientInfo
    procedure_codes: List[str] = Field(..., description="List of procedure codes to check")

class QuickClaimSubmission(BaseModel):
    """Quick claim submission for practices"""
    patient: PatientInfo
    practice: PracticeInfo
    procedures: List[ProcedureInfo]
    service_date: datetime = Field(..., description="Date services were provided")
    total_amount: float = Field(..., description="Total claim amount")

class PracticeWorkflow(BaseModel):
    """Complete practice workflow"""
    patient: PatientInfo
    practice: PracticeInfo
    procedures: List[ProcedureInfo]
    workflow_type: str = Field(..., description="Type: check_and_auth, check_and_claim, full_workflow")
    auto_submit_claims: bool = Field(default=True, description="Automatically submit claims after authorization")