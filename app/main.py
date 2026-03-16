import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.api.default import router as default_router
from app.api.auth import router as auth_router

app = FastAPI(title="Accounting App API")

# Session middleware：state CSRF 驗證需要，secret 務必存進 .env
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "change-this-secret"),
)

app.include_router(default_router)
app.include_router(auth_router)
