from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app import schemas, models
from nanoid import generate
from typing import List

router = APIRouter()

@router.post("/documents", response_model=schemas.DocumentRead)
def create_document(document: schemas.DocumentCreate, db: Session = Depends(get_db)):
    try:
        db_doc = models.Document(
            id=generate(size=15),
            title=document.title,
            created_at=document.created_at,
            last_updated=document.last_updated
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
    except IntegrityError:
        db.rollback()
    
    return db_doc

@router.get("/documents", response_model=List[schemas.DocumentRead])
def get_documents(db: Session = Depends(get_db)):
    documents = db.query(models.Document).order_by(models.Document.last_updated.desc()).all()
    return documents

@router.get("/documents/{document_id}", response_model=schemas.DocumentRead)
def get_document(
    document_id: str = Path(..., description="ID of document"),
    include_brainstorms: bool = False,
    db: Session = Depends(get_db)
):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    if include_brainstorms:
        doc.brainstorms = db.query(models.Brainstorm).filter(models.Brainstorm.document_id == document_id).all()

    return doc

@router.patch("/documents/{document_id}", response_model=schemas.DocumentRead)
def update_document(
    document_id: str,
    document_update: schemas.DocumentUpdate,
    db: Session = Depends(get_db)
):
    db_doc = db.query(models.Document).filter(models.Document.id == document_id).first()

    if not db_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    update_data = document_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_doc, key, value)
    
    db.commit()
    db.refresh(db_doc)

    return db_doc

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    db_doc = db.query(models.Document).filter(models.Document.id == document_id).first()

    if not db_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    db.delete(db_doc)
    db.commit()

    return