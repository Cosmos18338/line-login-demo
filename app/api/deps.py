from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.db.user import User
from app.services import auth_service

_bearer = HTTPBearer(auto_error=False)
_WWW_AUTHENTICATE = {"WWW-Authenticate": "Bearer"}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="無效的登入憑證", headers=_WWW_AUTHENTICATE)
    token = credentials.credentials
    try:
        user_id = auth_service.decode_access_token(token)
    except auth_service.TokenExpiredError:
        raise HTTPException(status_code=401, detail="登入已過期，請重新登入", headers=_WWW_AUTHENTICATE)
    except auth_service.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的登入憑證", headers=_WWW_AUTHENTICATE)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="使用者不存在", headers=_WWW_AUTHENTICATE)
    return user
