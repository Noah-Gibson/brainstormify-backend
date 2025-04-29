from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(15), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    #brainstorms = relationship("Brainstorm", back_populates="document", cascade="all, delete")
    #author = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    last_updated = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

class Brainstorm(Base):
    __tablename__ = "brainstorms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    document_id = Column(String(15), ForeignKey("documents.id"), nullable=False)
    #document = relationship("Document", back_populates="brainstorms")