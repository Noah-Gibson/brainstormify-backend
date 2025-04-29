from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app import schemas, models
from nanoid import generate
from typing import List
from datetime import datetime, timezone

router = APIRouter()

@router.post("/documents/{document_id}/brainstorms", response_model=schemas.BrainstormRead)
def create_brainstorm(
    document_id: str,
    brainstorm_data: schemas.BrainstormCreate,
    db: Session = Depends(get_db)
):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    brainstorm = models.Brainstorm(
        document_id=document_id,
        content=brainstorm_data.content,
        author=brainstorm_data.author,
        created_at=brainstorm_data.created_at
    )
    db.add(brainstorm)
    db.commit()
    db.refresh(brainstorm)

    return brainstorm

@router.get("/documents/{document_id}/brainstorms", response_model=List[schemas.BrainstormRead])
def get_brainstorms(
    document_id: str,
    db: Session = Depends(get_db)
):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    brainstorms = db.query(models.Brainstorm).filter(models.Brainstorm.document_id == document_id).all()
    return brainstorms