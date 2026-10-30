import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_health_check():
    """Verify service health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_public_endpoint_unauthenticated():
    """Public endpoint should be accessible without credentials."""
    response = client.get(f"{settings.API_V1_STR}/resources/public")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_user_registration_and_login():
    """Test full cycle: register user -> login -> get profile -> verify default role."""
    # 1. Register
    reg_data = {
        "username": "alice_test",
        "email": "alice@example.com",
        "password": "Password@123",
        "full_name": "Alice Tester"
    }
    reg_resp = client.post(f"{settings.API_V1_STR}/auth/register", json=reg_data)
    assert reg_resp.status_code in [201, 400]  # 400 if already created in earlier test run

    # 2. Login
    login_data = {
        "username_or_email": "alice@example.com",
        "password": "Password@123"
    }
    login_resp = client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]

    # 3. Access /auth/me
    headers = {"Authorization": f"Bearer {access_token}"}
    me_resp = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["username"] == "alice_test"
    role_names = [r["name"] for r in me_data["roles"]]
    assert "User" in role_names


def test_standard_user_permission_barrier():
    """Standard user should be forbidden from accessing admin endpoints."""
    # Login as standard user
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username_or_email": "user@example.com", "password": "User@123456"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to access admin settings -> should return 403 Forbidden
    resp = client.get(f"{settings.API_V1_STR}/resources/admin-system-settings", headers=headers)
    assert resp.status_code == 403
    assert "Access denied" in resp.json()["detail"]


def test_superadmin_full_access():
    """SuperAdmin should pass all permission barriers."""
    # Login as SuperAdmin
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={
            "username_or_email": settings.FIRST_SUPERADMIN_EMAIL,
            "password": settings.FIRST_SUPERADMIN_PASSWORD
        }
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # SuperAdmin accessing system admin settings -> should be 200 OK
    resp = client.get(f"{settings.API_V1_STR}/resources/admin-system-settings", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    # SuperAdmin listing all users
    users_resp = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
    assert users_resp.status_code == 200
    assert len(users_resp.json()) >= 2


def test_dynamic_role_creation_and_permission_assignment():
    """Admin dynamically creates a role, assigns permissions, and grants to a user."""
    # 1. Login as SuperAdmin
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={
            "username_or_email": settings.FIRST_SUPERADMIN_EMAIL,
            "password": settings.FIRST_SUPERADMIN_PASSWORD
        }
    )
    token = login_resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {token}"}

    # 2. Get permission ID for 'report:delete'
    perms_resp = client.get(f"{settings.API_V1_STR}/permissions/", headers=admin_headers)
    assert perms_resp.status_code == 200
    all_perms = perms_resp.json()
    report_del_perm = next(p for p in all_perms if p["name"] == "report:delete")

    # 3. Create a custom role 'ReportAuditor'
    role_payload = {
        "name": "ReportAuditor",
        "description": "Can audit and delete reports",
        "permission_ids": [report_del_perm["id"]]
    }
    role_resp = client.post(f"{settings.API_V1_STR}/roles/", json=role_payload, headers=admin_headers)
    assert role_resp.status_code in [201, 400]
    if role_resp.status_code == 201:
        created_role_id = role_resp.json()["id"]
    else:
        # Find existing role
        roles_list = client.get(f"{settings.API_V1_STR}/roles/", headers=admin_headers).json()
        created_role_id = next(r["id"] for r in roles_list if r["name"] == "ReportAuditor")

    # 4. Standard user cannot delete report
    # Ensure user has only standard 'User' role (id: 4) before testing permission barrier
    users_list = client.get(f"{settings.API_V1_STR}/users/", headers=admin_headers).json()
    user_entry = next((u for u in users_list if u["email"] == "user@example.com"), None)
    if user_entry:
        client.post(
            f"{settings.API_V1_STR}/users/{user_entry['id']}/roles",
            json={"role_ids": [4]},
            headers=admin_headers
        )

    user_login = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username_or_email": "user@example.com", "password": "User@123456"}
    )
    user_token = user_login.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    del_resp = client.delete(f"{settings.API_V1_STR}/resources/reports/101", headers=user_headers)
    assert del_resp.status_code == 403

    # 5. Admin assigns ReportAuditor role to user (user ID 3)
    user_data = client.get(f"{settings.API_V1_STR}/auth/me", headers=user_headers).json()
    user_id = user_data["id"]
    assign_resp = client.post(
        f"{settings.API_V1_STR}/users/{user_id}/roles",
        json={"role_ids": [4, created_role_id]},  # 4 is 'User' role
        headers=admin_headers
    )
    assert assign_resp.status_code == 200

    # 6. User now can successfully delete report!
    del_success_resp = client.delete(f"{settings.API_V1_STR}/resources/reports/101", headers=user_headers)
    assert del_success_resp.status_code == 200
    assert del_success_resp.json()["status"] == "success"
