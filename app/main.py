from typing import Union, Any
from dataclasses import dataclass, field

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.backstage.router import router as admin_api_router
from app.backstage.views import router as admin_view_router
from app.api.default import router as default_router


app = FastAPI()


templates = Jinja2Templates(directory="app/templates")


app.include_router(admin_api_router)
app.include_router(admin_view_router)
app.include_router(default_router)
