import pytest
from httpx import AsyncClient
from app.main import app
from datetime import datetime, timezone
from bson import ObjectId

@pytest.mark.asyncio
async def test_create_and_get_note():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        payload = {'title': 'Test Note', 'body': 'This is a test'}
        post_resp = await ac.post('/api/v1/notes', json=payload)
        assert post_resp.status_code == 201
        note_id = post_resp.json()['id']

        get_resp = await ac.get(f'/api/v1/notes/{note_id}')
        assert get_resp.status_code == 200
        note = get_resp.json()
        assert note['title'] == 'Test Note'
        assert note['body'] == 'This is a test'
        assert isinstance(note['created_at'], datetime)
        assert isinstance(note['updated_at'], datetime)
        assert isinstance(ObjectId(note['id']), ObjectId)

@pytest.mark.asyncio
async def test_create_note_invalid_payload():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        payload = {'title': '', 'body': 'This is a test'}
        post_resp = await ac.post('/api/v1/notes', json=payload)
        assert post_resp.status_code == 422

@pytest.mark.asyncio
async def test_get_note_not_found():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        get_resp = await ac.get('/api/v1/notes/invalid_id')
        assert get_resp.status_code == 404

@pytest.mark.asyncio
async def test_create_note_duplicate():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        payload = {'title': 'Test Note', 'body': 'This is a test'}
        await ac.post('/api/v1/notes', json=payload)
        post_resp = await ac.post('/api/v1/notes', json=payload)
        assert post_resp.status_code == 400
        assert 'Note with the same title and date already exists' in post_resp.json()['detail']
