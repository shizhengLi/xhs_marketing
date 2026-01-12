from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.deps import get_db, get_current_user_id
from app.core.config import settings
from app.schemas import UserCreate, UserResponse, Token
from app.models.user import User
from app.utils.security import verify_password, get_password_hash, create_access_token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    """
    # 检查用户名是否存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )

    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """
    用户登录
    """
    # 查找用户
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 验证密码
    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 检查用户是否激活
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    获取当前用户信息
    """
    from app.core.deps import get_current_user_id

    # 重新导入以避免循环依赖
    db_user = db.query(User).filter(User.id == int(current_user_id)).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return db_user