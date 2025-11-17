from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    body: Optional[str] = Field(None, min_length=1, max_length=5000)

    @validator('title', 'body')
    def _strip(cls, v):
        return v.strip() if v else v

class NoteList(BaseModel):
    limit: int = Field(10, gt=0, lt=101)
    skip: int = Field(0, ge=0)
    search: Optional[str] = Field(None, min_length=1)
