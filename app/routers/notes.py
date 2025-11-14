from fastapi import APIRouter, HTTPException, status, Path, Query
from typing import Optional
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson import ObjectId
from app.db import get_notes_collection
from app.schemas import NoteCreate, NoteResponse, NoteUpdate, NoteList

router = APIRouter()

@router.post('/notes', response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteCreate):
    try:
        note_dict = note.dict()
        note_dict['created_at'] = note_dict['updated_at'] = datetime.now()
        result = await get_notes_collection().insert_one(note_dict)
        note_dict['id'] = str(result.inserted_id)
        return note_dict
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Note with same title already exists')
    except PyMongoError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to create note')

@router.get('/notes/{note_id}', response_model=NoteResponse)
async def get_note(note_id: str = Path(..., title='Note ID')):
    try:
        note = await get_notes_collection().find_one({'_id': ObjectId(note_id)})
        if note is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Note not found')
        return NoteResponse(**note)
    except PyMongoError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to retrieve note')

@router.put('/notes/{note_id}', response_model=NoteResponse)
async def update_note(note_id: str = Path(..., title='Note ID'), note: NoteUpdate = None):
    try:
        update_data = note.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.now()
        result = await get_notes_collection().update_one({'_id': ObjectId(note_id)}, {'$set': update_data})
        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Note not found')
        updated_note = await get_notes_collection().find_one({'_id': ObjectId(note_id)})
        return NoteResponse(**updated_note)
    except PyMongoError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to update note')

@router.delete('/notes/{note_id}', response_model=NoteResponse)
async def delete_note(note_id: str = Path(..., title='Note ID')):
    try:
        result = await get_notes_collection().update_one({'_id': ObjectId(note_id)}, {'$set': {'deleted_at': datetime.now()}})
        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Note not found')
        deleted_note = await get_notes_collection().find_one({'_id': ObjectId(note_id)})
        return NoteResponse(**deleted_note)
    except PyMongoError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to delete note')

@router.get('/notes', response_model=list[NoteList])
async def list_notes(
    search: Optional[str] = Query(None, title='Search text', min_length=1),
    page: int = Query(1, ge=1, title='Page number'),
    limit: int = Query(10, ge=1, le=100, title='Number of results per page')
):
    try:
        query = {}
        if search:
            query['$text'] = {'$search': search}
        skip = (page - 1) * limit
        notes = await get_notes_collection().find(query, {'score': {'$meta': 'textScore'}}).sort([('score', {'$meta': 'textScore'})]).skip(skip).limit(limit).to_list(length=None)
        return [NoteList(**note) for note in notes]
    except PyMongoError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to retrieve notes')