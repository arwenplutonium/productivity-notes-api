import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    with app.app_context():
        from backend.extensions import db
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_signup_login_notes_crud_and_authorization(client):
    signup_response = client.post(
        "/signup",
        json={"username": "alice", "password": "password123"},
    )
    assert signup_response.status_code == 201

    second_signup = client.post(
        "/signup",
        json={"username": "bob", "password": "password123"},
    )
    assert second_signup.status_code == 201

    login_response = client.post(
        "/login",
        json={"username": "alice", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]
    assert token

    create_note = client.post(
        "/notes",
        json={"title": "Planning", "content": "Finish backend"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_note.status_code == 201
    note_id = create_note.get_json()["id"]

    notes_response = client.get(
        "/notes",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert notes_response.status_code == 200
    assert notes_response.get_json()["total"] == 1

    unauthorized_note = client.get(
        f"/notes/{note_id}",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert unauthorized_note.status_code == 401

    bob_login = client.post(
        "/login",
        json={"username": "bob", "password": "password123"},
    )
    bob_token = bob_login.get_json()["access_token"]

    forbidden_access = client.get(
        f"/notes/{note_id}",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert forbidden_access.status_code == 403

    patch_response = client.patch(
        f"/notes/{note_id}",
        json={"title": "Updated planning"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_response.status_code == 200
    assert patch_response.get_json()["title"] == "Updated planning"

    delete_response = client.delete(
        f"/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 200
