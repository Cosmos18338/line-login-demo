from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db
from app.models.schemas.common import ResponseBase, StatusBase

router = APIRouter(prefix="/api", tags=["default"])


@router.get("/health", response_model=ResponseBase)
def health_check():
    """服務健康確認"""
    return ResponseBase(
        status=StatusBase(code="0", err_msg=""),
        main={"message": "Service is running"},
    )


@router.get("/db-check", response_model=ResponseBase)
def db_check(db: Session = Depends(get_db)):
    """DB 連線確認"""
    try:
        db.execute(text("SELECT 1"))
        return ResponseBase(main={"message": "DB connection OK"})
    except Exception as e:
        return ResponseBase(
            status=StatusBase(code="500", err_msg=str(e)),
            main={},
        )
