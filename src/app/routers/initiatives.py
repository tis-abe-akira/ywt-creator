from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import models
from ..schemas import schemas

router = APIRouter(
    prefix="/initiatives",
    tags=["initiatives"]
)

@router.post("/", response_model=schemas.Initiative, status_code=status.HTTP_201_CREATED)
def create_initiative(initiative: schemas.InitiativeCreate, db: Session = Depends(get_db)):
    db_initiative = models.Initiative(
        title=initiative.title,
        description=initiative.description,
        irr=initiative.irr,
        cost=initiative.cost,
        status=models.InitiativeStatus.PROPOSED
    )
    db.add(db_initiative)
    db.commit()
    db.refresh(db_initiative)
    return db_initiative

@router.get("/", response_model=List[schemas.Initiative])
def list_initiatives(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    initiatives = db.query(models.Initiative).offset(skip).limit(limit).all()
    return initiatives

@router.get("/{initiative_id}", response_model=schemas.Initiative)
def get_initiative(initiative_id: int, db: Session = Depends(get_db)):
    initiative = db.query(models.Initiative).filter(models.Initiative.id == initiative_id).first()
    if initiative is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    return initiative

@router.post("/{initiative_id}/assessments", response_model=schemas.InitiativeAssessment)
def create_initiative_assessment(
    initiative_id: int,
    assessment: schemas.InitiativeAssessmentCreate,
    db: Session = Depends(get_db)
):
    # 施策の存在確認
    initiative = db.query(models.Initiative).filter(models.Initiative.id == initiative_id).first()
    if initiative is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    
    db_assessment = models.InitiativeAssessment(
        initiative_id=initiative_id,
        feasibility_score=assessment.feasibility_score,
        compliance_check=assessment.compliance_check,
        terms_impact=assessment.terms_impact
    )
    
    # 施策のステータス更新
    initiative.status = models.InitiativeStatus.UNDER_REVIEW
    
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

@router.post("/{initiative_id}/effects", response_model=schemas.InitiativeEffect)
def record_initiative_effect(
    initiative_id: int,
    effect: schemas.InitiativeEffectCreate,
    db: Session = Depends(get_db)
):
    # 施策の存在確認
    initiative = db.query(models.Initiative).filter(models.Initiative.id == initiative_id).first()
    if initiative is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    
    db_effect = models.InitiativeEffect(
        initiative_id=initiative_id,
        metric_name=effect.metric_name,
        metric_value=effect.metric_value
    )
    
    db.add(db_effect)
    db.commit()
    db.refresh(db_effect)
    return db_effect

@router.put("/{initiative_id}/status", response_model=schemas.Initiative)
def update_initiative_status(
    initiative_id: int,
    status_update: schemas.InitiativeStatusUpdate,
    db: Session = Depends(get_db)
):
    initiative = db.query(models.Initiative).filter(models.Initiative.id == initiative_id).first()
    if initiative is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    
    initiative.status = status_update.status
    db.commit()
    db.refresh(initiative)
    return initiative
