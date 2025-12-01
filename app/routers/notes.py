from fastapi import APIRouter, HTTPException, status, Path, Query
from typing import Optional
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson import ObjectId
from app.db import get_notes_collection
from app.schemas import NoteCreate, NoteResponse, NoteUpdate, NoteList

router = APIRouter()

# POST /notes
@router.post("/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate):
    try:
        note_dict = note.dict()
        note_dict["created_at"] = datetime.now()
        result = await get_notes_collection().insert_one(note_dict)
        note_dict["id"] = str(result.inserted_id)
        return note_dict
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Note with this title already exists")
    except PyMongoError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the note")

# GET /notes/{id}
@router.get("/notes/{id}", response_model=NoteResponse)
async def get_note(id: str = Path(..., min_length=24, max_length=24)):
    try:
        note = await get_notes_collection().find_one({"_id": ObjectId(id)})
        if note:
            return NoteResponse(**note)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    except PyMongoError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving the note")

# PUT /notes/{id}
@router.put("/notes/{id}", response_model=NoteResponse)
async def update_note(id: str = Path(..., min_length=24, max_length=24), note: NoteUpdate = None):
    try:
        update_data = note.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now()
        result = await get_notes_collection().update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.modified_count == 1:
            updated_note = await get_notes_collection().find_one({"_id": ObjectId(id)})
            return NoteResponse(**updated_note)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    except PyMongoError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the note")

# DELETE /notes/{id}
@router.delete("/notes/{id}", response_model=NoteResponse)
async def delete_note(id: str = Path(..., min_length=24, max_length=24)):
    try:
        result = await get_notes_collection().update_one({"_id": ObjectId(id)}, {"$set": {"deleted_at": datetime.now()}})
        if result.modified_count == 1:
            deleted_note = await get_notes_collection().find_one({"_id": ObjectId(id)})
            return NoteResponse(**deleted_note)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    except PyMongoError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while deleting the note")

# GET /notes
@router.get("/notes", response_model=list[NoteResponse])
async def list_notes(list_params: NoteList = Depends()):
    try:
        search_query = {}
        if list_params.search:
            search_query = {"$text": {"$search": list_params.search}}
        notes = await get_notes_collection().find(
            {"deleted_at": None, **search_query},
            {"_id": 1, "title": 1, "body": 1, "created_at": 1, "updated_at": 1, "deleted_at": 1}
        ).sort("created_at", DESCENDING).skip(list_params.skip).limit(list_params.limit).to_list(None)
        return [NoteResponse(**note) for note in notes]
    except PyMongoError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving notes")