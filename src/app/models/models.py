from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class InitiativeStatus(enum.Enum):
    PROPOSED = "PROPOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

class Initiative(Base):
    __tablename__ = "initiatives"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    irr = Column(Float)  # Internal Rate of Return
    cost = Column(Float)
    status = Column(SQLEnum(InitiativeStatus))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assessments = relationship("InitiativeAssessment", back_populates="initiative")
    effects = relationship("InitiativeEffect", back_populates="initiative")
    requirements = relationship("Requirement", back_populates="initiative")

class InitiativeAssessment(Base):
    __tablename__ = "initiative_assessments"

    id = Column(Integer, primary_key=True, index=True)
    initiative_id = Column(Integer, ForeignKey("initiatives.id"))
    feasibility_score = Column(Float)
    compliance_check = Column(Boolean)
    terms_impact = Column(Boolean)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    
    initiative = relationship("Initiative", back_populates="assessments")

class InitiativeEffect(Base):
    __tablename__ = "initiative_effects"

    id = Column(Integer, primary_key=True, index=True)
    initiative_id = Column(Integer, ForeignKey("initiatives.id"))
    metric_name = Column(String)
    metric_value = Column(Float)
    measurement_date = Column(DateTime, default=datetime.utcnow)
    
    initiative = relationship("Initiative", back_populates="effects")

class TermsOfService(Base):
    __tablename__ = "terms_of_service"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, index=True)
    content = Column(String)
    effective_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class TermsAgreement(Base):
    __tablename__ = "terms_agreements"

    id = Column(Integer, primary_key=True, index=True)
    terms_id = Column(Integer, ForeignKey("terms_of_service.id"))
    member_id = Column(String, index=True)  # External CRM member ID
    agreed_at = Column(DateTime, default=datetime.utcnow)

class RequirementStatus(enum.Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    IN_DEVELOPMENT = "IN_DEVELOPMENT"
    COMPLETED = "COMPLETED"

class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    initiative_id = Column(Integer, ForeignKey("initiatives.id"))
    title = Column(String, index=True)
    description = Column(String)
    status = Column(SQLEnum(RequirementStatus))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    initiative = relationship("Initiative", back_populates="requirements")
    development_tasks = relationship("DevelopmentTask", back_populates="requirement")

class DevelopmentTask(Base):
    __tablename__ = "development_tasks"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String)  # TODO: Consider making this an enum
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    requirement = relationship("Requirement", back_populates="development_tasks")

class ReleaseStatus(enum.Enum):
    PLANNED = "PLANNED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    ROLLED_BACK = "ROLLED_BACK"

class Release(Base):
    __tablename__ = "releases"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, index=True)
    description = Column(String)
    status = Column(SQLEnum(ReleaseStatus))
    planned_date = Column(DateTime)
    actual_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReleaseRollback(Base):
    __tablename__ = "release_rollbacks"

    id = Column(Integer, primary_key=True, index=True)
    release_id = Column(Integer, ForeignKey("releases.id"))
    reason = Column(String)
    rollback_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
