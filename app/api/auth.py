import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


@router.get("/line")
async def line_login(request: Request):
    """產生 state 並導向 LINE 授權頁"""
    state = auth_service.generate_state()
    request.session["oauth_state"] = state
    auth_url = auth_service.build_line_auth_url(state)
    return RedirectResponse(auth_url)


@router.get("/line/redirect")
async def line_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """LINE 授權後的 callback：驗證 state → 換 token → DB upsert → 簽發 JWT"""
    # Step 1：驗證 state 防 CSRF
    if state != request.session.get("oauth_state"):
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    request.session.pop("oauth_state", None)

    # Step 2：換取用戶資料（call LINE API）
    profile = await auth_service.exchange_code_for_profile(code)

    # Step 3：查詢或建立用戶（業務邏輯在 service，API 層不碰 DB 細節）
    user = auth_service.get_or_create_user(
        db,
        provider="line",
        provider_user_id=profile["sub"],
        display_name=profile["name"],
    )

    # Step 4：簽發 JWT，導回前端
    token = auth_service.create_access_token(str(user.id))
    return RedirectResponse(f"{FRONTEND_URL}/login/callback?token={token}")
