from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    body: str = Field(..., min_length=1, max_length=5000)

    @validator('title')
    def _t(cls, v: str): return v.strip()

    @validator('body')
    def _b(cls, v: str): return v.strip()

class NoteResponse(BaseModel):
    id: str
    title: str
    body: str
    created_at: datetime
    updated_at: datetime

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    body: Optional[str] = Field(None, min_length=1, max_length=5000)

    @validator('title')
    def _t(cls, v: str): return v.strip() if v else v

    @validator('body')
    def _b(cls, v: str): return v.strip() if v else v

class NoteList(BaseModel):
    id: str
    title: str
    body: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None