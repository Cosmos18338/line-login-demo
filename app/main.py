# app/main.py
# 只負責：app 建立、middleware 設定、掛載總路由
# 路由注冊一律在 app/api/__init__.py 管理
import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.api import api_router

app = FastAPI(title="Accounting App API")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "change-this-secret"),
)

app.include_router(api_router)
