"""
帖子相关API
展示和管理爬取的小红书内容
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from app.database import SessionLocal
from app.models.post import Post
from app.models.keyword import Keyword

router = APIRouter()
logger = logging.getLogger(__name__)


# Pydantic模型
class PostListResponse(BaseModel):
    id: int
    keyword_id: int
    title: str
    content: Optional[str] = None
    author: Optional[str] = None
    likes: int
    collects: int
    comments: int
    shares: int
    url: Optional[str] = None
    published_at: Optional[str] = None
    crawled_at: Optional[str] = None
    keyword_name: Optional[str] = None

    class Config:
        from_attributes = True


class PostsResponse(BaseModel):
    total: int
    posts: List[PostListResponse]


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=PostsResponse)
async def get_posts(
    keyword_id: Optional[int] = None,
    keyword_name: Optional[str] = None,
    sort_by: str = "likes",  # likes, collects, comments, shares, published_at
    order: str = "desc",     # desc, asc
    limit: int = 50,
    offset: int = 0,
    min_likes: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取帖子列表，支持多种排序方式

    Args:
        keyword_id: 关键词ID
        keyword_name: 关键词名称
        sort_by: 排序字段 (likes, collects, comments, shares, published_at)
        order: 排序方向 (desc, asc)
        limit: 返回数量限制（最大100）
        offset: 偏移量
        min_likes: 最小点赞数筛选

    Returns:
        帖子列表
    """
    try:
        # 限制最大返回数量
        limit = min(limit, 100)

        # 构建基础查询，只选择需要的字段
        query = db.query(
            Post.id,
            Post.keyword_id,
            Post.title,
            Post.content,
            Post.author,
            Post.likes,
            Post.collects,
            Post.comments,
            Post.shares,
            Post.url,
            Post.published_at,
            Post.crawled_at
        ).join(Keyword, Post.keyword_id == Keyword.id)

        # 按关键词筛选
        if keyword_id:
            query = query.filter(Post.keyword_id == keyword_id)
        elif keyword_name:
            query = query.filter(Keyword.keyword == keyword_name)

        # 按点赞数筛选
        if min_likes is not None:
            query = query.filter(Post.likes >= min_likes)

        # 排序
        sort_column = getattr(Post, sort_by, Post.likes)
        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # 先获取总数
        total = query.count()

        # 分页并获取数据
        posts_data = query.limit(limit).offset(offset).all()

        # 转换为响应格式
        post_responses = []
        for post_data in posts_data:
            # 获取关键词名称
            keyword = db.query(Keyword).filter(Keyword.id == post_data.keyword_id).first()

            post_dict = {
                "id": post_data.id,
                "keyword_id": post_data.keyword_id,
                "title": post_data.title,
                "content": post_data.content,
                "author": post_data.author,
                "likes": post_data.likes,
                "collects": post_data.collects,
                "comments": post_data.comments,
                "shares": post_data.shares,
                "url": post_data.url,
                "published_at": post_data.published_at.isoformat() if post_data.published_at else None,
                "crawled_at": post_data.crawled_at.isoformat() if post_data.crawled_at else None,
                "keyword_name": keyword.keyword if keyword else None
            }
            post_responses.append(PostListResponse(**post_dict))

        return PostsResponse(total=total, posts=post_responses)

    except Exception as e:
        logger.error(f"获取帖子列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取帖子列表失败: {str(e)}")


@router.get("/stats")
async def get_posts_stats(
    keyword_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取帖子统计信息

    Args:
        keyword_id: 关键词ID（可选）

    Returns:
        统计信息
    """
    try:
        # 使用聚合函数计算统计数据
        from sqlalchemy import func

        # 构建基础查询用于统计
        stats_query = db.query(Post)

        if keyword_id:
            stats_query = stats_query.filter(Post.keyword_id == keyword_id)

        # 执行统计查询
        stats = stats_query.with_entities(
            func.count(Post.id).label('total_posts'),
            func.sum(Post.likes).label('total_likes'),
            func.sum(Post.collects).label('total_collects'),
            func.sum(Post.comments).label('total_comments')
        ).first()

        total_posts = stats.total_posts or 0
        total_likes = stats.total_likes or 0
        total_collects = stats.total_collects or 0
        total_comments = stats.total_comments or 0

        # 热门帖子查询（独立的查询对象）
        top_posts_query = db.query(
            Post.title,
            Post.author,
            Post.likes,
            Post.collects,
            Post.comments,
            Post.url
        )

        if keyword_id:
            top_posts_query = top_posts_query.filter(Post.keyword_id == keyword_id)

        top_posts = top_posts_query.order_by(Post.likes.desc()).limit(10).all()

        top_posts_data = []
        for post in top_posts:
            top_posts_data.append({
                "title": post.title,
                "author": post.author,
                "likes": post.likes,
                "collects": post.collects,
                "comments": post.comments,
                "url": post.url
            })

        return {
            "total_posts": total_posts,
            "total_likes": total_likes,
            "total_collects": total_collects,
            "total_comments": total_comments,
            "avg_likes": round(total_likes / total_posts, 1) if total_posts > 0 else 0,
            "avg_collects": round(total_collects / total_posts, 1) if total_posts > 0 else 0,
            "avg_comments": round(total_comments / total_posts, 1) if total_posts > 0 else 0,
            "top_posts": top_posts_data
        }

    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/trending")
async def get_trending_posts(
    keyword_id: Optional[int] = None,
    days: int = 7,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取热门趋势帖子

    Args:
        keyword_id: 关键词ID（可选）
        days: 最近多少天
        limit: 返回数量（最大50）

    Returns:
        热门帖子列表
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func

        # 限制最大返回数量
        limit = min(limit, 50)

        # 计算时间范围
        time_threshold = datetime.now() - timedelta(days=days)

        # 只查询需要的字段
        query = db.query(
            Post.title,
            Post.content,
            Post.author,
            Post.likes,
            Post.collects,
            Post.comments,
            Post.shares,
            Post.url,
            Post.published_at,
            Keyword.keyword.label('keyword_name')
        ).join(Keyword, Post.keyword_id == Keyword.id)

        if keyword_id:
            query = query.filter(Post.keyword_id == keyword_id)

        # 筛选最近的数据
        query = query.filter(Post.published_at >= time_threshold)

        # 计算热度分数并排序
        heat_score = (Post.likes + Post.collects * 2 + Post.comments).label('heat_score')
        query = query.add_columns(heat_score).order_by(heat_score.desc())

        posts = query.limit(limit).all()

        # 转换为响应格式
        post_responses = []
        for post in posts:
            # 提取内容摘要
            content = post.content
            if content and len(content) > 200:
                content = content[:200] + "..."

            post_data = {
                "title": post.title,
                "content": content or "",
                "author": post.author or "匿名",
                "likes": post.likes,
                "collects": post.collects,
                "comments": post.comments,
                "shares": post.shares,
                "url": post.url,
                "keyword_name": post.keyword_name,
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "heat_score": post.heat_score  # 使用计算好的热度分数
            }
            post_responses.append(post_data)

        return {
            "total": len(post_responses),
            "posts": post_responses,
            "time_range": f"最近{days}天"
        }

    except Exception as e:
        logger.error(f"获取热门帖子失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热门帖子失败: {str(e)}")