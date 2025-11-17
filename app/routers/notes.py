from fastapi import APIRouter, HTTPException, status, Path, Query
from typing import Optional
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson import ObjectId
from app.db import get_notes_collection
from app.schemas import NoteCreate, NoteResponse, NoteUpdate, NoteList

router = APIRouter()

# Existing routes...

@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str = Path(..., min_length=24, max_length=24), note: NoteUpdate = None):
    try:
        note_id = ObjectId(note_id)
        update_data = note.dict(exclude_unset=True)
        updated_note = await get_notes_collection().find_one_and_update(
            {"_id": note_id},
            {"$set": update_data},
            return_document=True
        )
        if not updated_note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return updated_note
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/notes/{note_id}", response_model=NoteResponse)
async def delete_note(note_id: str = Path(..., min_length=24, max_length=24)):
    try:
        note_id = ObjectId(note_id)
        deleted_note = await get_notes_collection().find_one_and_update(
            {"_id": note_id},
            {"$set": {"deleted_at": datetime.utcnow()}},
            return_document=True
        )
        if not deleted_note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return deleted_note
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/notes", response_model=list[NoteResponse])
async def list_notes(
    limit: int = Query(10, gt=0, lt=101),
    skip: int = Query(0, ge=0),
    search: Optional[str] = Query(None, min_length=1)
):
    try:
        query = {}
        if search:
            query = {"$text": {"$search": search}}
        notes = await get_notes_collection().find(
            query,
            {"deleted_at": 0}
        ).sort("created_at", DESCENDING).skip(skip).limit(limit).to_list(length=None)
        return notes
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
