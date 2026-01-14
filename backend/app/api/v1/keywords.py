from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.deps import get_db, get_current_user_id
from app.schemas import (
    KeywordCreate, KeywordUpdate, KeywordResponse, KeywordAIExpand, KeywordAIResponse
)
from app.models.keyword import Keyword
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    keyword: KeywordCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    创建关键词
    """
    user_id = int(current_user_id)

    # 检查关键词是否已存在
    # 检查关键词是否已存在（不区分用户，因为系统只有一个用户）
    existing_keyword = db.query(Keyword).filter(
        Keyword.keyword == keyword.keyword
    ).first()

    if existing_keyword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"关键词 '{keyword.keyword}' 已存在"
        )

    # 创建新关键词
    db_keyword = Keyword(
        user_id=user_id,
        keyword=keyword.keyword,
        group_name=keyword.group_name,
        is_active=keyword.is_active
    )

    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)

    return db_keyword


@router.get("/", response_model=List[KeywordResponse])
async def get_keywords(
    group_name: Optional[str] = Query(None, description="按分组筛选"),
    is_active: Optional[bool] = Query(None, description="按状态筛选，None显示所有关键词"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的关键词列表
    """
    user_id = int(current_user_id)

    # 为了兼容数据，暂时不过滤user_id，显示所有关键词
    query = db.query(Keyword)

    # 如果需要严格按用户过滤，取消下面的注释
    # query = db.query(Keyword).filter(Keyword.user_id == user_id)

    # 应用筛选条件
    if group_name:
        query = query.filter(Keyword.group_name == group_name)
    if is_active is not None:
        query = query.filter(Keyword.is_active == is_active)

    keywords = query.order_by(Keyword.created_at.desc()).all()

    return keywords


@router.get("/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    keyword_id: int,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取指定关键词详情
    """
    user_id = int(current_user_id)

    keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.user_id == user_id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )

    return keyword


@router.put("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    keyword_update: KeywordUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新关键词
    """
    user_id = int(current_user_id)

    db_keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.user_id == user_id
    ).first()

    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )

    # 更新字段
    update_data = keyword_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_keyword, field, value)

    db.commit()
    db.refresh(db_keyword)

    return db_keyword


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(
    keyword_id: int,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除关键词（使用软删除，不会实际删除数据）
    """
    user_id = int(current_user_id)

    db_keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.user_id == user_id
    ).first()

    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )

    try:
        # 使用软删除：将is_active设置为False
        db_keyword.is_active = False

        # 同时将关联的帖子也标记为非活跃状态（如果需要的话）
        # 这里我们选择不删除帖子，保留数据

        db.commit()
        logger.info(f"软删除关键词: {db_keyword.keyword}")

        return None

    except Exception as e:
        db.rollback()
        logger.error(f"删除关键词失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除关键词失败: {str(e)}"
        )


@router.delete("/{keyword_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete_keyword(
    keyword_id: int,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    硬删除关键词（会同时删除关联的帖子数据，此操作不可恢复）
    """
    user_id = int(current_user_id)

    db_keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.user_id == user_id
    ).first()

    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )

    try:
        # 先删除关联的帖子数据
        from app.models.post import Post
        deleted_posts = db.query(Post).filter(Post.keyword_id == keyword_id).all()

        if deleted_posts:
            # 删除关联的帖子
            for post in deleted_posts:
                db.delete(post)
            logger.info(f"硬删除了 {len(deleted_posts)} 条关联的帖子数据")

        # 再删除关键词
        db.delete(db_keyword)
        db.commit()

        logger.info(f"硬删除关键词: {db_keyword.keyword} 及其关联数据")
        return None

    except Exception as e:
        db.rollback()
        logger.error(f"硬删除关键词失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"硬删除关键词失败: {str(e)}"
        )


@router.post("/{keyword_id}/restore", response_model=KeywordResponse)
async def restore_keyword(
    keyword_id: int,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    恢复已删除的关键词
    """
    user_id = int(current_user_id)

    db_keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.user_id == user_id,
        Keyword.is_active == False  # 只能恢复已删除的
    ).first()

    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="已删除的关键词不存在"
        )

    try:
        db_keyword.is_active = True
        db.commit()
        db.refresh(db_keyword)

        logger.info(f"恢复关键词: {db_keyword.keyword}")
        return db_keyword

    except Exception as e:
        db.rollback()
        logger.error(f"恢复关键词失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"恢复关键词失败: {str(e)}"
        )


@router.post("/ai-expand", response_model=KeywordAIResponse)
async def ai_expand_keywords(
    expand_request: KeywordAIExpand
    # 暂时移除认证要求进行测试
    # current_user_id: str = Depends(get_current_user_id)
):
    """
    AI扩展关键词 - 使用真实LLM
    """
    from app.services.llm_service import expand_keywords_with_llm

    try:
        # 使用真实的LLM服务扩展关键词
        suggested_keywords = expand_keywords_with_llm(
            expand_request.base_keyword,
            expand_request.count
        )

        return KeywordAIResponse(
            original=expand_request.base_keyword,
            suggested_keywords=suggested_keywords
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI扩展失败: {str(e)}"
        )