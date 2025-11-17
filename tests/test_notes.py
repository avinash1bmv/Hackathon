import pytest
from httpx import AsyncClient
from app.main_notes import app
from app.db import get_notes_collection
from datetime import datetime
from bson import ObjectId

@pytest.mark.asyncio
async def test_update_note():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create a test note
        response = await ac.post("/notes", json={"title": "Test Note", "body": "Test body"})
        note_id = response.json()["id"]

        # Update the note
        response = await ac.put(f"/notes/{note_id}", json={"title": "Updated Note"})
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Note"
        assert response.json()["body"] == "Test body"
        assert response.json()["created_at"] == response.json()["updated_at"]

        # Clean up
        await get_notes_collection().delete_one({"_id": ObjectId(note_id)})

@pytest.mark.asyncio
async def test_delete_note():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create a test note
        response = await ac.post("/notes", json={"title": "Test Note", "body": "Test body"})
        note_id = response.json()["id"]

        # Delete the note
        response = await ac.delete(f"/notes/{note_id}")
        assert response.status_code == 200
        assert "deleted_at" in response.json()

        # Clean up
        await get_notes_collection().delete_one({"_id": ObjectId(note_id)})

@pytest.mark.asyncio
async def test_list_notes():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create some test notes
        await get_notes_collection().insert_many([
            {"title": "Note 1", "body": "Body 1"},
            {"title": "Note 2", "body": "Body 2"},
            {"title": "Note 3", "body": "Body 3"},
            {"title": "Note 4", "body": "Body 4"},
            {"title": "Note 5", "body": "Body 5"},
        ])

        # Test pagination
        response = await ac.get("/notes?limit=2&skip=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Test search
        response = await ac.get("/notes?search=Note 3")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "Note 3"

        # Clean up
        await get_notes_collection().delete_many({"title": {"$in": ["Note 1", "Note 2", "Note 3", "Note 4", "Note 5"]}})
