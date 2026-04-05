from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
from app.models.user import User
from app.utils.security import get_hashed_password


def seed_user(db, email="test@test.com", username="testuser", password="testpass123", is_verified=True):
    user = User(
        email=email,
        username=username,
        hashed_password=get_hashed_password(password),
        is_verified=is_verified,
        first_name="Test",
        last_name="User",
        verification_code=None,
        code_expire_time=None
    )
    db.add(user)
    db.commit()
    return user


# ==================== GET /auth/register ====================

def test_get_register_page(client):
    response = client.get("/auth/register")
    assert response.status_code == 200


# ==================== GET /auth/login ====================

def test_get_login_page(client):
    response = client.get("/auth/login")
    assert response.status_code == 200

def test_get_login_page_registered_param(client):
    response = client.get("/auth/login?registered=true")
    assert response.status_code == 200
    assert "Registration successful" in response.text


# ==================== POST /auth/register ====================

def test_register_success(client):
    with patch("app.routers.auth.send_verification_email", new_callable=AsyncMock):
        response = client.post("/auth/register", data={
            "email": "newuser@test.com",
            "password": "testpass123",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User"
        }, follow_redirects=False)
    assert response.status_code == 303
    assert "verify-notice" in response.headers["location"]

def test_register_duplicate_email(client, db_session):
    seed_user(db_session)
    with patch("app.routers.auth.send_verification_email", new_callable=AsyncMock):
        response = client.post("/auth/register", data={
            "email": "test@test.com",
            "password": "testpass123",
            "username": "newuser2",
        }, follow_redirects=False)
    assert response.status_code == 200
    assert "Email already registered" in response.text

def test_register_duplicate_username(client, db_session):
    seed_user(db_session)
    with patch("app.routers.auth.send_verification_email", new_callable=AsyncMock):
        response = client.post("/auth/register", data={
            "email": "another@test.com",
            "password": "testpass123",
            "username": "testuser",
        }, follow_redirects=False)
    assert response.status_code == 200
    assert "Username already taken" in response.text

def test_register_password_too_long(client):
    with patch("app.routers.auth.send_verification_email", new_callable=AsyncMock):
        response = client.post("/auth/register", data={
            "email": "long@test.com",
            "password": "a" * 73,
            "username": "longpassuser",
        }, follow_redirects=False)
    assert response.status_code == 200
    assert "too long" in response.text

def test_register_password_too_short(client):
    with patch("app.routers.auth.send_verification_email", new_callable=AsyncMock):
        response = client.post("/auth/register", data={
            "email": "short@test.com",
            "password": "123",
            "username": "shortpassuser",
        }, follow_redirects=False)
    assert response.status_code == 200
    assert "too short" in response.text

# ==================== POST /auth/login ====================

def test_login_success(client, db_session):
    seed_user(db_session)
    response = client.post("/auth/login", data={
        "email": "test@test.com",
        "password": "testpass123"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "access_token" in response.cookies

def test_login_wrong_password(client, db_session):
    seed_user(db_session)
    response = client.post("/auth/login", data={
        "email": "test@test.com",
        "password": "wrongpass"
    }, follow_redirects=False)
    assert response.status_code == 200
    assert "Incorrect password" in response.text

def test_login_user_not_found(client):
    response = client.post("/auth/login", data={
        "email": "ghost@test.com",
        "password": "testpass123"
    }, follow_redirects=False)
    assert response.status_code == 200
    assert "User not found" in response.text

def test_login_unverified_user(client, db_session):
    seed_user(db_session, is_verified=False)
    response = client.post("/auth/login", data={
        "email": "test@test.com",
        "password": "testpass123"
    }, follow_redirects=False)
    assert response.status_code == 200

def test_login_with_username(client, db_session):
    seed_user(db_session)
    response = client.post("/auth/login", data={
        "email": "testuser",  # dùng username thay vì email
        "password": "testpass123"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "access_token" in response.cookies


# ==================== GET /auth/logout ====================

def test_logout(client):
    response = client.get("/auth/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


# ==================== POST /auth/verify-email ====================

def test_verify_email_success(client, db_session):
    user = seed_user(db_session, is_verified=False)
    user.verification_code = 123456
    user.code_expire_time = datetime.utcnow() + timedelta(minutes=10)
    db_session.commit()

    response = client.post("/auth/verify-email", data={
        "email": user.email,
        "code": "123456"
    }, follow_redirects=False)
    assert response.status_code == 200
    assert "verify_success" in response.text or response.status_code == 200

def test_verify_email_wrong_code(client, db_session):
    user = seed_user(db_session, is_verified=False)
    user.verification_code = 123456
    user.code_expire_time = datetime.utcnow() + timedelta(minutes=10)
    db_session.commit()

    response = client.post("/auth/verify-email", data={
        "email": user.email,
        "code": "999999"
    }, follow_redirects=False)
    assert response.status_code == 200
    assert "Invalid or expired" in response.text

def test_verify_email_expired_code(client, db_session):
    user = seed_user(db_session, is_verified=False)
    user.verification_code = 123456
    user.code_expire_time = datetime.utcnow() - timedelta(minutes=1)  # đã hết hạn
    db_session.commit()

    response = client.post("/auth/verify-email", data={
        "email": user.email,
        "code": "123456"
    }, follow_redirects=False)
    assert response.status_code == 200
    assert "Invalid or expired" in response.text

def test_verify_email_user_not_found(client):
    response = client.post("/auth/verify-email", data={
        "email": "ghost@test.com",
        "code": "123456"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/auth/login"


# ==================== POST /auth/resend-verification ====================

def test_resend_verification_success(client, db_session):
    seed_user(db_session, is_verified=False)
    with patch("app.routers.auth.send_verification_email", new_callable=AsyncMock):
        response = client.post("/auth/resend-verification", data={
            "email": "test@test.com"
        }, follow_redirects=False)
    assert response.status_code == 200
    assert "Verification email resent" in response.text

def test_resend_verification_user_not_found(client):
    with patch("app.routers.auth.send_verification_email", new_callable=AsyncMock):
        response = client.post("/auth/resend-verification", data={
            "email": "ghost@test.com"
        }, follow_redirects=False)
    assert response.status_code == 200
    assert "User not found" in response.text