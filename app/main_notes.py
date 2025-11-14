from fastapi import FastAPI, HTTPException, status, Path
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from datetime import datetime, timezone
from bson import ObjectId
from app.db import get_notes_collection
from app.schemas import NoteCreate, NoteResponse

app = FastAPI(title='Notes API (FastAPI + MongoDB)')

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

@app.post('/api/v1/notes', status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_note(note: NoteCreate):
    """Create a new note"""
    try:
        collection = get_notes_collection()
        now = datetime.now(timezone.utc)
        note_dict = note.dict()
        note_dict['created_at'] = now
        note_dict['updated_at'] = now
        result = await collection.insert_one(note_dict)
        return {'id': str(result.inserted_id)}
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Note with same title and date already exists')
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get('/api/v1/notes/{id}', response_model=NoteResponse)
async def get_note(id: str = Path(..., title='Note ID', description='The ID of the note to retrieve')):
    """Get a note by ID"""
    try:
        collection = get_notes_collection()
        note = await collection.find_one({'_id': ObjectId(id)})
        if note is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Note not found')
        return NoteResponse(**note)
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.on_event('startup')
async def create_indexes():
    """Create indexes on MongoDB collection"""
    collection = get_notes_collection()
    await collection.create_index([('title', ASCENDING), ('created_at', ASCENDING)], unique=True, partialFilterExpression={'created_at': {'$exists': True}})
    await collection.create_index('created_at', DESCENDING)
