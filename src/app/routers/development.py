from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import models
from ..schemas import schemas

router = APIRouter(
    prefix="/development",
    tags=["development"]
)

# Requirements endpoints
@router.post("/requirements/", response_model=schemas.Requirement, status_code=status.HTTP_201_CREATED)
def create_requirement(
    requirement: schemas.RequirementCreate,
    db: Session = Depends(get_db)
):
    # 施策の存在確認
    initiative = db.query(models.Initiative).filter(models.Initiative.id == requirement.initiative_id).first()
    if not initiative:
        raise HTTPException(status_code=404, detail="Initiative not found")

    db_requirement = models.Requirement(
        initiative_id=requirement.initiative_id,
        title=requirement.title,
        description=requirement.description,
        status=requirement.status
    )
    db.add(db_requirement)
    db.commit()
    db.refresh(db_requirement)
    return db_requirement

@router.get("/requirements/", response_model=List[schemas.Requirement])
def list_requirements(
    skip: int = 0,
    limit: int = 100,
    initiative_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Requirement)
    if initiative_id:
        query = query.filter(models.Requirement.initiative_id == initiative_id)
    requirements = query.offset(skip).limit(limit).all()
    return requirements

@router.get("/requirements/{requirement_id}", response_model=schemas.Requirement)
def get_requirement(requirement_id: int, db: Session = Depends(get_db)):
    requirement = db.query(models.Requirement).filter(models.Requirement.id == requirement_id).first()
    if requirement is None:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return requirement

@router.put("/requirements/{requirement_id}/status", response_model=schemas.Requirement)
def update_requirement_status(
    requirement_id: int,
    status_update: schemas.RequirementStatusUpdate,
    db: Session = Depends(get_db)
):
    requirement = db.query(models.Requirement).filter(models.Requirement.id == requirement_id).first()
    if requirement is None:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    requirement.status = status_update.status
    db.commit()
    db.refresh(requirement)
    return requirement

# Development Tasks endpoints
@router.post("/tasks/", response_model=schemas.DevelopmentTask, status_code=status.HTTP_201_CREATED)
def create_development_task(
    task: schemas.DevelopmentTaskCreate,
    db: Session = Depends(get_db)
):
    # 要件の存在確認
    requirement = db.query(models.Requirement).filter(models.Requirement.id == task.requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    db_task = models.DevelopmentTask(
        requirement_id=task.requirement_id,
        title=task.title,
        description=task.description,
        status=task.status
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/tasks/", response_model=List[schemas.DevelopmentTask])
def list_development_tasks(
    skip: int = 0,
    limit: int = 100,
    requirement_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.DevelopmentTask)
    if requirement_id:
        query = query.filter(models.DevelopmentTask.requirement_id == requirement_id)
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/tasks/{task_id}", response_model=schemas.DevelopmentTask)
def get_development_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.DevelopmentTask).filter(models.DevelopmentTask.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Development task not found")
    return task

@router.put("/tasks/{task_id}", response_model=schemas.DevelopmentTask)
def update_development_task(
    task_id: int,
    task_update: schemas.DevelopmentTaskCreate,
    db: Session = Depends(get_db)
):
    task = db.query(models.DevelopmentTask).filter(models.DevelopmentTask.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Development task not found")
    
    for var, value in vars(task_update).items():
        setattr(task, var, value)
    
    db.commit()
    db.refresh(task)
    return task

@router.get("/requirements/{requirement_id}/tasks", response_model=List[schemas.DevelopmentTask])
def get_tasks_by_requirement(
    requirement_id: int,
    db: Session = Depends(get_db)
):
    requirement = db.query(models.Requirement).filter(models.Requirement.id == requirement_id).first()
    if requirement is None:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    tasks = db.query(models.DevelopmentTask)\
        .filter(models.DevelopmentTask.requirement_id == requirement_id)\
        .all()
    return tasks
