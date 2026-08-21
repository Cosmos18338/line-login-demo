from typing import Any
from pydantic import BaseModel


class StatusBase(BaseModel):
    code: str = "0"
    err_msg: str = ""


class ResponseBase(BaseModel):
    status: StatusBase = StatusBase()
    main: Any = {}
    detail: Any = {}
