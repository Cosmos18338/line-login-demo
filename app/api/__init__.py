# app/api/__init__.py
# 集中管理所有 router，main.py 只需找入此檔
from fastapi import APIRouter

from app.api.default import router as default_router
from app.api.auth import router as auth_router

api_router = APIRouter()
api_router.include_router(default_router)
api_router.include_router(auth_router)
