from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import models
from ..schemas import schemas
from datetime import datetime

router = APIRouter(
    prefix="/terms",
    tags=["terms"]
)

@router.post("/", response_model=schemas.TermsOfService, status_code=status.HTTP_201_CREATED)
def create_terms(
    terms: schemas.TermsOfServiceCreate,
    db: Session = Depends(get_db)
):
    db_terms = models.TermsOfService(
        version=terms.version,
        content=terms.content,
        effective_date=terms.effective_date
    )
    db.add(db_terms)
    db.commit()
    db.refresh(db_terms)
    return db_terms

@router.get("/", response_model=List[schemas.TermsOfService])
def list_terms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    terms = db.query(models.TermsOfService).offset(skip).limit(limit).all()
    return terms

@router.get("/latest", response_model=schemas.TermsOfService)
def get_latest_terms(db: Session = Depends(get_db)):
    terms = db.query(models.TermsOfService)\
        .order_by(models.TermsOfService.effective_date.desc())\
        .first()
    if terms is None:
        raise HTTPException(status_code=404, detail="No terms of service found")
    return terms

@router.get("/{terms_id}", response_model=schemas.TermsOfService)
def get_terms(terms_id: int, db: Session = Depends(get_db)):
    terms = db.query(models.TermsOfService).filter(models.TermsOfService.id == terms_id).first()
    if terms is None:
        raise HTTPException(status_code=404, detail="Terms of service not found")
    return terms

@router.post("/{terms_id}/agreements", status_code=status.HTTP_201_CREATED)
def record_agreement(
    terms_id: int,
    member_id: str,
    db: Session = Depends(get_db)
):
    # 利用規約の存在確認
    terms = db.query(models.TermsOfService).filter(models.TermsOfService.id == terms_id).first()
    if terms is None:
        raise HTTPException(status_code=404, detail="Terms of service not found")
    
    # 既存の同意確認
    existing_agreement = db.query(models.TermsAgreement)\
        .filter(
            models.TermsAgreement.terms_id == terms_id,
            models.TermsAgreement.member_id == member_id
        ).first()
    
    if existing_agreement:
        raise HTTPException(
            status_code=400,
            detail="Member has already agreed to these terms"
        )
    
    # 新規同意の記録
    agreement = models.TermsAgreement(
        terms_id=terms_id,
        member_id=member_id
    )
    db.add(agreement)
    db.commit()
    
    return {"status": "success", "message": "Agreement recorded"}

@router.get("/agreements/{member_id}", response_model=List[dict])
def get_member_agreements(member_id: str, db: Session = Depends(get_db)):
    agreements = db.query(models.TermsAgreement)\
        .filter(models.TermsAgreement.member_id == member_id)\
        .all()
    
    return [
        {
            "terms_id": agreement.terms_id,
            "agreed_at": agreement.agreed_at,
            "member_id": agreement.member_id
        }
        for agreement in agreements
    ]

@router.get("/check-agreement/{member_id}")
def check_latest_agreement(member_id: str, db: Session = Depends(get_db)):
    # 最新の利用規約を取得
    latest_terms = db.query(models.TermsOfService)\
        .order_by(models.TermsOfService.effective_date.desc())\
        .first()
    
    if not latest_terms:
        raise HTTPException(status_code=404, detail="No terms of service found")
    
    # 会員の同意を確認
    agreement = db.query(models.TermsAgreement)\
        .filter(
            models.TermsAgreement.terms_id == latest_terms.id,
            models.TermsAgreement.member_id == member_id
        ).first()
    
    return {
        "has_agreed": agreement is not None,
        "latest_terms_version": latest_terms.version,
        "latest_terms_id": latest_terms.id,
        "agreement_date": agreement.agreed_at if agreement else None
    }
