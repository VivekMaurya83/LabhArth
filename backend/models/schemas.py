"""
LabhArth AI — Pydantic Schemas
================================
Request/Response models for the API layer.
These are the data contracts between frontend and backend.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# =============================================================================
# Chat Schemas
# =============================================================================


class ChatRequest(BaseModel):
    """Incoming chat message from the user."""

    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    """Chat response from the AI agent."""

    response: str = Field(..., description="Agent response text")
    session_id: str = Field(..., description="Session ID for follow-up messages")
    agent_name: Optional[str] = Field(None, description="Name of the agent that handled the request")
    sources: Optional[list[str]] = Field(None, description="Source references used")


# =============================================================================
# Scheme Schemas
# =============================================================================


class SchemeSearchRequest(BaseModel):
    """Request to search for government schemes."""

    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    state: Optional[str] = Field(None, description="Filter by state")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum results to return")


class SchemeResult(BaseModel):
    """A single scheme search result."""

    id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    state: Optional[str] = None
    relevance_score: Optional[float] = None


class SchemeSearchResponse(BaseModel):
    """Response containing scheme search results."""

    results: list[SchemeResult]
    total: int
    query: str


class SchemeDetailResponse(BaseModel):
    """Full details of a single government scheme."""

    id: UUID
    name: str
    description: Optional[str] = None
    ministry: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    state: Optional[str] = None
    eligibility_criteria: Optional[dict] = None
    benefits: Optional[str] = None
    required_documents: Optional[list[str]] = None
    application_process: Optional[str] = None
    official_url: Optional[str] = None
    status: Optional[str] = None
    last_updated: Optional[datetime] = None


# =============================================================================
# Eligibility Schemas
# =============================================================================


class UserProfile(BaseModel):
    """User profile for eligibility checking."""

    age: Optional[int] = Field(None, ge=0, le=150, description="Age in years")
    gender: Optional[str] = Field(None, description="Gender")
    state: Optional[str] = Field(None, description="State of residence")
    district: Optional[str] = Field(None, description="District")
    category: Optional[str] = Field(None, description="Social category (General/SC/ST/OBC)")
    income_annual: Optional[float] = Field(None, ge=0, description="Annual income in INR")
    occupation: Optional[str] = Field(None, description="Occupation")
    education: Optional[str] = Field(None, description="Education level")
    is_bpl: Optional[bool] = Field(None, description="Below Poverty Line status")
    is_disabled: Optional[bool] = Field(None, description="Disability status")
    is_farmer: Optional[bool] = Field(None, description="Farmer status")
    is_student: Optional[bool] = Field(None, description="Student status")


class EligibilityRequest(BaseModel):
    """Request to check eligibility for a scheme."""

    scheme_id: UUID = Field(..., description="ID of the scheme to check eligibility for")
    profile: UserProfile = Field(..., description="User profile data")


class EligibilityResponse(BaseModel):
    """Eligibility check result."""

    scheme_id: UUID
    scheme_name: str
    is_eligible: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    missing_criteria: Optional[list[str]] = None
    required_documents: Optional[list[str]] = None


# =============================================================================
# Health Check
# =============================================================================


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str = "0.1.0"
    environment: str = "development"
