import os
import secrets
import uuid
from datetime import datetime, timedelta
from urllib.parse import urlencode

import httpx
import jwt
from sqlalchemy.orm import Session

from app.models.db.user import User, UserOAuthBinding

LINE_CHANNEL_ID = os.getenv("LINE_CHANNEL_ID")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_REDIRECT_URI = os.getenv("LINE_REDIRECT_URI")
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 24 小時


# ── LINE OAuth ──────────────────────────────────────────────

def generate_state() -> str:
    return secrets.token_urlsafe(16)


def build_line_auth_url(state: str) -> str:
    params = {
        "response_type": "code",
        "client_id": LINE_CHANNEL_ID,
        "redirect_uri": LINE_REDIRECT_URI,
        "state": state,
        "scope": "profile openid",
    }
    return "https://access.line.me/oauth2/v2.1/authorize?" + urlencode(params)


async def exchange_code_for_profile(code: str) -> dict:
    """用 code 換 access_token，解碼 id_token 取得用戶資料"""
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://api.line.me/oauth2/v2.1/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": LINE_REDIRECT_URI,
                "client_id": LINE_CHANNEL_ID,
                "client_secret": LINE_CHANNEL_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_res.raise_for_status()
        tokens = token_res.json()

    # 解碼 id_token（verify_signature=False 僅適合開發測試）
    id_token = tokens["id_token"]
    payload = jwt.decode(id_token, options={"verify_signature": False})
    return {
        "sub": payload["sub"],
        "name": payload.get("name", "使用者"),
    }


# ── DB 操作 ─────────────────────────────────────────────────

def get_binding(db: Session, provider: str, provider_user_id: str) -> UserOAuthBinding | None:
    return (
        db.query(UserOAuthBinding)
        .filter_by(provider=provider, provider_user_id=provider_user_id)
        .first()
    )


def create_user_with_binding(
    db: Session, user_name: str, provider: str, provider_user_id: str
) -> User:
    user = User(user_name=user_name)
    db.add(user)
    db.flush()  # 取得 user.id，尚未 commit

    binding = UserOAuthBinding(
        user_id=user.id,
        provider=provider,
        provider_user_id=provider_user_id,
    )
    db.add(binding)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_user(
    db: Session, provider: str, provider_user_id: str, display_name: str
) -> User:
    """查詢 DB 是否有對應綁定，有則回傳既有用戶，無則建立新用戶與綁定"""
    binding = get_binding(db, provider, provider_user_id)
    if binding:
        return binding.user
    return create_user_with_binding(db, display_name, provider, provider_user_id)


# ── JWT 例外 ────────────────────────────────────────────────

class TokenExpiredError(Exception):
    """JWT 已過期"""


class InvalidTokenError(Exception):
    """JWT 無效或格式錯誤"""


# ── JWT ─────────────────────────────────────────────────────

def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> uuid.UUID:
    """驗證並解碼 JWT，回傳使用者 UUID。
    - jwt.ExpiredSignatureError → TokenExpiredError
    - 其他 jwt 相關錯誤 → InvalidTokenError
    - payload 缺少 sub 或非合法 UUID → InvalidTokenError
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("token 已過期")
    except jwt.PyJWTError:
        raise InvalidTokenError("token 無效")

    sub = payload.get("sub")
    if not sub:
        raise InvalidTokenError("payload 缺少 sub")
    try:
        return uuid.UUID(sub)
    except (ValueError, AttributeError, TypeError):
        raise InvalidTokenError("sub 不是合法的 UUID")
