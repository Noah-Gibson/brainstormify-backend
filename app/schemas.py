from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Author(BaseModel):
    username: str
    email: str

class DocumentCreate(BaseModel):
    title: str
    created_at: datetime
    last_updated: datetime

class DocumentRead(BaseModel):
    id: str
    title: str
    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    last_updated: Optional[datetime] = None

class BrainstormCreate(BaseModel):
    content: str
    author: str
    created_at: datetime

class BrainstormRead(BaseModel):
    id: int
    content: str
    author: str
    created_at: datetime

    class Config:
        from_attributes = True