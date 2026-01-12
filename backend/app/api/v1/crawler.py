from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_db, get_current_user_id
from app.schemas import PostResponse, CrawlResponse
from app.models.post import Post as PostModel
from app.models.keyword import Keyword as KeywordModel
from app.services.mock_crawler import crawl_by_keyword_mock, get_trends_mock

router = APIRouter()


@router.post("/crawl/{keyword_id}")
async def crawl_content_by_keyword(
    keyword_id: int,
    count: int = Query(20, ge=1, le=100, description="抓取数量"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    根据关键词ID抓取内容
    ⚠️ 此功能已禁用 - 请使用MediaCrawler进行真实数据爬取
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="爬虫功能已禁用。请使用爬虫管理页面的MediaCrawler功能进行真实数据爬取。"
    )


@router.post("/crawl/batch")
async def batch_crawl(
    keyword_ids: List[int],
    count_per_keyword: int = Query(20, ge=1, le=100, description="每个关键词抓取数量"),
    background_tasks: BackgroundTasks = None,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    批量抓取多个关键词的内容
    ⚠️ 此功能已禁用 - 请使用MediaCrawler进行真实数据爬取
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="批量爬虫功能已禁用。请使用爬虫管理页面的MediaCrawler功能进行真实数据爬取。"
    )


@router.get("/trends")
async def get_hot_trends(
    limit: int = Query(10, ge=1, le=50, description="返回趋势数量"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    获取当前热点趋势
    ⚠️ 此功能已禁用 - 请使用MediaCrawler进行真实数据爬取
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="热点趋势功能已禁用。请使用爬虫管理页面的MediaCrawler功能进行真实数据爬取。"
    )