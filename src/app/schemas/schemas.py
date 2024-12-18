from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Initiative Schemas
class InitiativeStatus(str, Enum):
    PROPOSED = "PROPOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

class InitiativeBase(BaseModel):
    title: str
    description: str
    irr: float = Field(ge=0)
    cost: float = Field(ge=0)

class InitiativeCreate(InitiativeBase):
    pass

class Initiative(InitiativeBase):
    id: int
    status: InitiativeStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InitiativeStatusUpdate(BaseModel):
    status: InitiativeStatus

# Initiative Assessment Schemas
class InitiativeAssessmentBase(BaseModel):
    initiative_id: int
    feasibility_score: float = Field(ge=0, le=100)
    compliance_check: bool
    terms_impact: bool

class InitiativeAssessmentCreate(InitiativeAssessmentBase):
    pass

class InitiativeAssessment(InitiativeAssessmentBase):
    id: int
    assessment_date: datetime

    class Config:
        from_attributes = True

# Terms of Service Schemas
class TermsOfServiceBase(BaseModel):
    version: str
    content: str
    effective_date: datetime

class TermsOfServiceCreate(TermsOfServiceBase):
    pass

class TermsOfService(TermsOfServiceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Requirement Schemas
class RequirementStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    IN_DEVELOPMENT = "IN_DEVELOPMENT"
    COMPLETED = "COMPLETED"

class RequirementBase(BaseModel):
    initiative_id: int
    title: str
    description: str
    status: RequirementStatus

class RequirementCreate(RequirementBase):
    pass

class Requirement(RequirementBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RequirementStatusUpdate(BaseModel):
    status: RequirementStatus

# Development Task Schemas
class DevelopmentTaskBase(BaseModel):
    requirement_id: int
    title: str
    description: str
    status: str

class DevelopmentTaskCreate(DevelopmentTaskBase):
    pass

class DevelopmentTask(DevelopmentTaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Release Schemas
class ReleaseStatus(str, Enum):
    PLANNED = "PLANNED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    ROLLED_BACK = "ROLLED_BACK"

class ReleaseBase(BaseModel):
    version: str
    description: str
    status: ReleaseStatus
    planned_date: datetime

class ReleaseCreate(ReleaseBase):
    pass

class Release(ReleaseBase):
    id: int
    actual_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReleaseStatusUpdate(BaseModel):
    status: ReleaseStatus

# Release Rollback Schemas
class ReleaseRollbackBase(BaseModel):
    release_id: int
    reason: str

class ReleaseRollbackCreate(ReleaseRollbackBase):
    pass

class ReleaseRollback(ReleaseRollbackBase):
    id: int
    rollback_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Initiative Effect Schemas
class InitiativeEffectBase(BaseModel):
    initiative_id: int
    metric_name: str
    metric_value: float

class InitiativeEffectCreate(InitiativeEffectBase):
    pass

class InitiativeEffect(InitiativeEffectBase):
    id: int
    measurement_date: datetime

    class Config:
        from_attributes = True
