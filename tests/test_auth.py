import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DB_USER", "admin")
os.environ.setdefault("DB_PASSWORD", "test12345")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "app_db")

from app.db import Base, get_db
from app.main import app
from app.models.db.user import User
from app.services import auth_service


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def db_session_factory(test_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session(db_session_factory):
    session = db_session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session_factory):
    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    user = User(user_name="pytest-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_get_my_profile_with_valid_jwt_returns_200(client, test_user):
    token = auth_service.create_access_token(str(test_user.id))

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(test_user.id),
        "user_name": test_user.user_name,
    }


def test_get_my_profile_without_authorization_header_returns_401(client, monkeypatch):
    def fail_decode(*args, **kwargs):
        raise AssertionError("decode_access_token should not be called when Authorization is missing")

    monkeypatch.setattr(auth_service, "decode_access_token", fail_decode)

    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "無效的登入憑證"}


def test_get_my_profile_with_malformed_token_returns_401(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "無效的登入憑證"}


def test_get_my_profile_with_expired_token_returns_401(client, test_user):
    expired_token = jwt.encode(
        {
            "sub": str(test_user.id),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        auth_service.JWT_SECRET,
        algorithm=auth_service.JWT_ALGORITHM,
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "登入已過期，請重新登入"}
