from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import hashlib
from app.core.config import settings

# 密码加密上下文 - 使用sha256_crypt替代bcrypt
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    创建访问令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt