from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import models
from ..schemas import schemas

router = APIRouter(
    prefix="/releases",
    tags=["releases"]
)

@router.post("/", response_model=schemas.Release, status_code=status.HTTP_201_CREATED)
def create_release(
    release: schemas.ReleaseCreate,
    db: Session = Depends(get_db)
):
    db_release = models.Release(
        version=release.version,
        description=release.description,
        status=release.status,
        planned_date=release.planned_date
    )
    db.add(db_release)
    db.commit()
    db.refresh(db_release)
    return db_release

@router.get("/", response_model=List[schemas.Release])
def list_releases(
    skip: int = 0,
    limit: int = 100,
    status: schemas.ReleaseStatus = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Release)
    if status:
        query = query.filter(models.Release.status == status)
    releases = query.offset(skip).limit(limit).all()
    return releases

@router.get("/{release_id}", response_model=schemas.Release)
def get_release(release_id: int, db: Session = Depends(get_db)):
    release = db.query(models.Release).filter(models.Release.id == release_id).first()
    if release is None:
        raise HTTPException(status_code=404, detail="Release not found")
    return release

@router.put("/{release_id}/status", response_model=schemas.Release)
def update_release_status(
    release_id: int,
    status_update: schemas.ReleaseStatusUpdate,
    db: Session = Depends(get_db)
):
    release = db.query(models.Release).filter(models.Release.id == release_id).first()
    if release is None:
        raise HTTPException(status_code=404, detail="Release not found")
    
    release.status = status_update.status
    if status_update.status == schemas.ReleaseStatus.COMPLETED:
        release.actual_date = datetime.utcnow()
    
    db.commit()
    db.refresh(release)
    return release

@router.post("/{release_id}/rollback", response_model=schemas.ReleaseRollback)
def create_rollback(
    release_id: int,
    rollback: schemas.ReleaseRollbackCreate,
    db: Session = Depends(get_db)
):
    # リリースの存在確認
    release = db.query(models.Release).filter(models.Release.id == release_id).first()
    if release is None:
        raise HTTPException(status_code=404, detail="Release not found")
    
    # リリースステータスの確認
    if release.status != schemas.ReleaseStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Only completed releases can be rolled back"
        )
    
    # ロールバックの記録
    db_rollback = models.ReleaseRollback(
        release_id=release_id,
        reason=rollback.reason
    )
    
    # リリースステータスの更新
    release.status = schemas.ReleaseStatus.ROLLED_BACK
    
    db.add(db_rollback)
    db.commit()
    db.refresh(db_rollback)
    return db_rollback

@router.get("/{release_id}/rollbacks", response_model=List[schemas.ReleaseRollback])
def get_release_rollbacks(
    release_id: int,
    db: Session = Depends(get_db)
):
    # リリースの存在確認
    release = db.query(models.Release).filter(models.Release.id == release_id).first()
    if release is None:
        raise HTTPException(status_code=404, detail="Release not found")
    
    rollbacks = db.query(models.ReleaseRollback)\
        .filter(models.ReleaseRollback.release_id == release_id)\
        .all()
    return rollbacks

@router.get("/pending/approval", response_model=List[schemas.Release])
def get_pending_releases(db: Session = Depends(get_db)):
    releases = db.query(models.Release)\
        .filter(models.Release.status == schemas.ReleaseStatus.PENDING_APPROVAL)\
        .all()
    return releases

@router.put("/{release_id}/approve", response_model=schemas.Release)
def approve_release(
    release_id: int,
    db: Session = Depends(get_db)
):
    release = db.query(models.Release).filter(models.Release.id == release_id).first()
    if release is None:
        raise HTTPException(status_code=404, detail="Release not found")
    
    if release.status != schemas.ReleaseStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail="Only pending releases can be approved"
        )
    
    release.status = schemas.ReleaseStatus.APPROVED
    db.commit()
    db.refresh(release)
    return release
