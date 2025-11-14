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

@app.post('/api/v1/notes', status_code=status.HTTP_201_CREATED, response_model=NoteResponse)
async def create_note(note: NoteCreate):
    try:
        collection = get_notes_collection()
        now = datetime.now(timezone.utc)
        note_data = note.dict()
        note_data['created_at'] = now
        note_data['updated_at'] = now
        result = await collection.insert_one(note_data)
        note_data['id'] = str(result.inserted_id)
        return note_data
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Note with the same title and date already exists')
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get('/api/v1/notes/{id}', response_model=NoteResponse)
async def get_note(id: str = Path(..., title='Note ID')):
    try:
        collection = get_notes_collection()
        note = await collection.find_one({'_id': ObjectId(id)})
        if note:
            return NoteResponse(**note)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Note not found')
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Ensure indexes
collection = get_notes_collection()
await collection.create_index([('title', ASCENDING), ('created_at', ASCENDING)], unique=True)
await collection.create_index([('created_at', DESCENDING)])
