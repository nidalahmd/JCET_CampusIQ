import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def unique_email() -> str:
    return f"student_{uuid.uuid4().hex[:8]}@jcet.ac.in"


@pytest.fixture
def admin_email() -> str:
    return f"admin_{uuid.uuid4().hex[:8]}@jcet.ac.in"


def test_user_registration(unique_email: str) -> None:
    payload = {
        "name": "Jane Doe",
        "email": unique_email,
        "password": "SecurePassword123!",
        "role": "student",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["name"] == "Jane Doe"
    assert data["user"]["email"] == unique_email
    assert data["user"]["role"] == "student"
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_duplicate_email_rejected(unique_email: str) -> None:
    payload = {
        "name": "Jane Doe",
        "email": unique_email,
        "password": "SecurePassword123!",
        "role": "student",
    }
    first_res = client.post("/api/auth/register", json=payload)
    assert first_res.status_code == 201

    # Attempt to register again with same email
    dup_res = client.post("/api/auth/register", json=payload)
    assert dup_res.status_code == 409
    assert "already exists" in dup_res.json()["detail"]


def test_login_success(unique_email: str) -> None:
    # Register first
    client.post(
        "/api/auth/register",
        json={
            "name": "John Student",
            "email": unique_email,
            "password": "MySecretPassword123",
            "role": "student",
        },
    )

    # Login
    login_res = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": "MySecretPassword123"},
    )
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert data["user"]["email"] == unique_email


def test_login_wrong_password_rejected(unique_email: str) -> None:
    client.post(
        "/api/auth/register",
        json={
            "name": "John Student",
            "email": unique_email,
            "password": "CorrectPassword123",
            "role": "student",
        },
    )

    # Wrong password
    bad_res = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": "WrongPassword999"},
    )
    assert bad_res.status_code == 401
    assert "Incorrect email or password" in bad_res.json()["detail"]


def test_login_nonexistent_email_rejected() -> None:
    bad_res = client.post(
        "/api/auth/login",
        json={"email": f"nonexistent_{uuid.uuid4().hex}@jcet.ac.in", "password": "AnyPassword123"},
    )
    assert bad_res.status_code == 401


def test_get_current_user_profile(unique_email: str) -> None:
    reg_res = client.post(
        "/api/auth/register",
        json={
            "name": "Profile User",
            "email": unique_email,
            "password": "ValidPassword123",
            "role": "student",
        },
    )
    token = reg_res.json()["access_token"]

    # Call /api/auth/me
    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["name"] == "Profile User"
    assert user_data["email"] == unique_email
    assert user_data["role"] == "student"


def test_unauthenticated_request_rejected() -> None:
    # No auth header
    res = client.get("/api/auth/me")
    assert res.status_code == 401

    # Invalid auth token
    invalid_res = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid.fake.token"},
    )
    assert invalid_res.status_code == 401


def test_role_based_access_control(unique_email: str, admin_email: str) -> None:
    # Register student
    student_res = client.post(
        "/api/auth/register",
        json={
            "name": "Student User",
            "email": unique_email,
            "password": "Password12345",
            "role": "student",
        },
    )
    student_token = student_res.json()["access_token"]

    # Register admin
    admin_res = client.post(
        "/api/auth/register",
        json={
            "name": "Admin User",
            "email": admin_email,
            "password": "Password12345",
            "role": "admin",
        },
    )
    admin_token = admin_res.json()["access_token"]

    # Student accessing admin endpoint -> 403 Forbidden
    forbidden_res = client.get(
        "/api/auth/admin-check",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert forbidden_res.status_code == 403

    # Admin accessing admin endpoint -> 200 OK
    allowed_res = client.get(
        "/api/auth/admin-check",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert allowed_res.status_code == 200
    assert allowed_res.json()["status"] == "ok"


def test_update_profile(unique_email: str) -> None:
    reg_res = client.post(
        "/api/auth/register",
        json={
            "name": "Original Name",
            "email": unique_email,
            "password": "Password12345",
            "role": "student",
        },
    )
    token = reg_res.json()["access_token"]

    # Update name
    patch_res = client.patch(
        "/api/auth/me",
        json={"name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Updated Name"


def test_change_password(unique_email: str) -> None:
    reg_res = client.post(
        "/api/auth/register",
        json={
            "name": "Password User",
            "email": unique_email,
            "password": "OldPassword123",
            "role": "student",
        },
    )
    token = reg_res.json()["access_token"]

    # Fail with incorrect current password
    bad_change = client.post(
        "/api/auth/change-password",
        json={"current_password": "WrongOldPassword", "new_password": "NewSecretPassword123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert bad_change.status_code == 400

    # Succeed with correct current password
    good_change = client.post(
        "/api/auth/change-password",
        json={"current_password": "OldPassword123", "new_password": "NewSecretPassword123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert good_change.status_code == 200
    assert good_change.json()["status"] == "ok"

    # Verify old password no longer works
    old_login = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": "OldPassword123"},
    )
    assert old_login.status_code == 401

    # Verify new password works
    new_login = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": "NewSecretPassword123"},
    )
    assert new_login.status_code == 200
