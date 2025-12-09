from typing import Union, Any
from dataclasses import dataclass, field

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.backstage.router import router as admin_api_router
from app.backstage.views import router as admin_view_router


app = FastAPI()


templates = Jinja2Templates(directory="app/templates")


app.include_router(admin_api_router)
app.include_router(admin_view_router)


@dataclass
class Pagination:
    page: int = 1
    size: int = 10


@dataclass
class StatusBase:
    code: str = "0"
    err_msg: str = ""


@dataclass
class ResponseBase:
    status: StatusBase = field(default_factory=StatusBase)
    main: Any = field(default_factory=dict)
    detail: Any = field(default_factory=dict)


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.get("/test")
def read_test():
    response = ResponseBase()
    pagi = Pagination(page=2, size=5)
    response.main = {"message": "This is a test endpoint"}
    response.detail = {"pagination": pagi}
    return response
