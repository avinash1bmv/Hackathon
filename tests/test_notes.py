import pytest
from fastapi.testclient import TestClient
from app.main_notes import app
from app.db import get_notes_collection
from datetime import datetime
from bson import ObjectId

client = TestClient(app)

# Helper function to create a test note
def create_test_note(title, body):
    note = {"title": title, "body": body, "created_at": datetime.now()}
    result = get_notes_collection().insert_one(note)
    return str(result.inserted_id)

# Test POST /notes
def test_create_note():
    note_data = {"title": "Test Note", "body": "This is a test note"}
    response = client.post("/notes", json=note_data)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["title"] == note_data["title"]
    assert response.json()["body"] == note_data["body"]

# Test GET /notes/{id}
def test_get_note():
    note_id = create_test_note("Test Note", "This is a test note")
    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["id"] == note_id

# Test PUT /notes/{id}
def test_update_note():
    note_id = create_test_note("Test Note", "This is a test note")
    update_data = {"title": "Updated Note", "body": "This note has been updated"}
    response = client.put(f"/notes/{note_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]
    assert response.json()["body"] == update_data["body"]
    assert response.json()["created_at"] != response.json()["updated_at"]

# Test DELETE /notes/{id}
def test_delete_note():
    note_id = create_test_note("Test Note", "This is a test note")
    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None

# Test GET /notes with pagination and search
def test_list_notes():
    # Create some test notes
    note_ids = [create_test_note(f"Test Note {i}", f"This is test note {i}") for i in range(20)]

    # Test pagination
    response = client.get("/notes?limit=10&skip=5")
    assert response.status_code == 200
    assert len(response.json()) == 10

    # Test search
    response = client.get("/notes?search=test note 5")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test Note 5"

# Teardown: Delete all test notes
@pytest.fixture(autouse=True, scope="module")
def teardown():
    yield
    get_notes_collection().delete_many({"title": {"$regex": "^Test Note"}})