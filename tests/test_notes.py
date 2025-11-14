import pytest
from httpx import AsyncClient
from app.main import app
from datetime import datetime
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
        assert get_resp.json()['title'] == 'Test Note'
        assert get_resp.json()['body'] == 'This is a test'

@pytest.mark.asyncio
async def test_update_note():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        payload = {'title': 'Test Note', 'body': 'This is a test'}
        post_resp = await ac.post('/api/v1/notes', json=payload)
        note_id = post_resp.json()['id']
        update_payload = {'title': 'Updated Note', 'body': 'This is an updated test'}
        put_resp = await ac.put(f'/api/v1/notes/{note_id}', json=update_payload)
        assert put_resp.status_code == 200
        assert put_resp.json()['title'] == 'Updated Note'
        assert put_resp.json()['body'] == 'This is an updated test'
        assert put_resp.json()['created_at'] == post_resp.json()['created_at']

@pytest.mark.asyncio
async def test_delete_note():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        payload = {'title': 'Test Note', 'body': 'This is a test'}
        post_resp = await ac.post('/api/v1/notes', json=payload)
        note_id = post_resp.json()['id']
        delete_resp = await ac.delete(f'/api/v1/notes/{note_id}')
        assert delete_resp.status_code == 200
        assert delete_resp.json()['deleted_at'] is not None

@pytest.mark.asyncio
async def test_list_notes():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        for i in range(20):
            payload = {'title': f'Test Note {i}', 'body': f'This is a test note {i}'}
            await ac.post('/api/v1/notes', json=payload)
        list_resp = await ac.get('/api/v1/notes?page=2&limit=10')
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 10
        assert list_resp.json()[0]['title'] == 'Test Note 10'

@pytest.mark.asyncio
async def test_search_notes():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        payload = {'title': 'Search Test', 'body': 'This is a test for search'}
        await ac.post('/api/v1/notes', json=payload)
        search_resp = await ac.get('/api/v1/notes?search=search')
        assert search_resp.status_code == 200
        assert len(search_resp.json()) >= 1
        assert 'Search Test' in [note['title'] for note in search_resp.json()]

@pytest.mark.asyncio
async def test_note_not_found():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        invalid_id = str(ObjectId())
        get_resp = await ac.get(f'/api/v1/notes/{invalid_id}')
        assert get_resp.status_code == 404
        put_resp = await ac.put(f'/api/v1/notes/{invalid_id}', json={'title': 'Updated Note'})
        assert put_resp.status_code == 404
        delete_resp = await ac.delete(f'/api/v1/notes/{invalid_id}')
        assert delete_resp.status_code == 404