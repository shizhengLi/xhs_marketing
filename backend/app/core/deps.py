from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Generator, Optional
from jose import jwt, JWTError
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings


security = HTTPBearer()


def get_db() -> Generator:
    """
    数据库依赖函数
    """
    from app.database import SessionLocal
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    获取当前用户ID
    """
    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
        )