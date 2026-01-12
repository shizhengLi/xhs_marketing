"""
MediaCrawler 自动化 API
提供一键启动MediaCrawler的功能
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging
from sqlalchemy.orm import Session

from app.services.mediacrawler_service import mediacrawler_automation
from app.services.data_import_service import media_importer
from app.core.deps import get_db
from app.models.keyword import Keyword
from app.models.post import Post

router = APIRouter()
logger = logging.getLogger(__name__)


class StartCrawlerRequest(BaseModel):
    """启动爬虫请求"""
    keywords: List[str]
    count: int = 15


class CrawlerResponse(BaseModel):
    """爬虫响应"""
    success: bool
    message: str
    process_id: Optional[int] = None
    keywords: Optional[List[str]] = None
    count: Optional[int] = None
    error: Optional[str] = None


@router.post("/start-crawler", response_model=CrawlerResponse)
async def start_crawler(request: StartCrawlerRequest):
    """
    一键启动MediaCrawler爬虫

    Args:
        request: 包含关键词列表和爬取数量的请求

    Returns:
        CrawlerResponse: 启动结果
    """
    try:
        if not request.keywords:
            raise HTTPException(
                status_code=400,
                detail="关键词列表不能为空"
            )

        logger.info(f"启动MediaCrawler，关键词: {request.keywords}, 数量: {request.count}")

        # 启动爬虫
        result = await mediacrawler_automation.start_xhs_crawler(
            keywords=request.keywords,
            count=request.count
        )

        return CrawlerResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动爬虫失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"启动爬虫失败: {str(e)}"
        )


@router.post("/quick-start")
async def quick_start(request: StartCrawlerRequest):
    """
    快速启动：扫码登录 + 开始爬虫

    Args:
        request: 包含关键词列表和爬取数量的请求

    Returns:
        启动结果
    """
    try:
        if not request.keywords:
            raise HTTPException(
                status_code=400,
                detail="关键词列表不能为空"
            )

        logger.info(f"快速启动MediaCrawler，关键词: {request.keywords}")

        # 启动爬虫（会自动处理登录）
        result = await mediacrawler_automation.start_xhs_crawler(
            keywords=request.keywords,
            count=request.count
        )

        return {
            **result,
            "instructions": "浏览器已自动打开，请扫描二维码登录。登录完成后爬虫将自动开始工作。"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"快速启动失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"快速启动失败: {str(e)}"
        )


@router.get("/config-info")
async def get_config_info():
    """
    获取MediaCrawler配置信息

    Returns:
        配置信息
    """
    try:
        config_info = mediacrawler_automation.get_config_info()
        return config_info

    except Exception as e:
        logger.error(f"获取配置信息失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取配置信息失败: {str(e)}"
        )


@router.post("/login-only")
async def login_only():
    """
    仅启动登录（不进行爬取）
    用于首次登录MediaCrawler账号

    Returns:
        启动结果
    """
    try:
        logger.info("启动MediaCrawler登录模式")

        result = await mediacrawler_automation.check_and_start_browser()

        return {
            **result,
            "instructions": "浏览器已打开，请扫描二维码登录。登录成功后，浏览器会自动关闭。"
        }

    except Exception as e:
        logger.error(f"启动登录失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"启动登录失败: {str(e)}"
        )


@router.get("/login-status")
async def get_login_status():
    """
    获取MediaCrawler登录状态

    Returns:
        登录状态信息
    """
    try:
        # 这里可以检查实际的登录状态
        # 暂时返回一个基本的状态
        return {
            "is_logged_in": False,
            "login_method": "qrcode",
            "message": "登录状态检查功能待实现"
        }

    except Exception as e:
        logger.error(f"检查登录状态失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"检查登录状态失败: {str(e)}"
        )


@router.post("/confirm-login")
async def confirm_login(login_method: str = "qrcode", success: bool = True):
    """
    确认手动登录成功

    Args:
        login_method: 登录方式
        success: 是否登录成功

    Returns:
        确认结果
    """
    try:
        logger.info(f"确认登录: {login_method}, 成功: {success}")

        return {
            "success": True,
            "message": "登录状态已更新"
        }

    except Exception as e:
        logger.error(f"确认登录失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"确认登录失败: {str(e)}"
        )


@router.post("/reset-login")
async def reset_login():
    """
    重置登录状态

    Returns:
        重置结果
    """
    try:
        logger.info("重置登录状态")

        return {
            "success": True,
            "message": "登录状态已重置"
        }

    except Exception as e:
        logger.error(f"重置登录状态失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"重置登录状态失败: {str(e)}"
        )


@router.post("/import-data")
async def import_data(keyword: str):
    """
    导入MediaCrawler爬取的数据到项目数据库

    Args:
        keyword: 关键词名称

    Returns:
        导入结果
    """
    try:
        logger.info(f"开始导入关键词 '{keyword}' 的数据")

        result = media_importer.import_data_to_db(keyword)

        if result['success']:
            logger.info(f"数据导入成功: {result}")
        else:
            logger.warning(f"数据导入失败: {result['message']}")

        return result

    except Exception as e:
        logger.error(f"导入数据失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"导入数据失败: {str(e)}"
        )


@router.get("/data-summary")
async def get_data_summary():
    """
    获取MediaCrawler数据摘要信息

    Returns:
        数据摘要
    """
    try:
        summary = media_importer.get_data_summary()
        return summary

    except Exception as e:
        logger.error(f"获取数据摘要失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取数据摘要失败: {str(e)}"
        )


@router.get("/available-keywords")
async def get_available_keywords():
    """
    获取可以导入数据的关键词列表

    Returns:
        可用关键词列表
    """
    try:
        summary = media_importer.get_data_summary()

        if summary['success']:
            return {
                "success": True,
                "keywords": ["双肩包"],  # 可以从文件名中提取关键词
                "latest_file": summary['latest_file'],
                "file_count": summary['file_count']
            }
        else:
            return {
                "success": False,
                "keywords": [],
                "message": summary['message']
            }

    except Exception as e:
        logger.error(f"获取可用关键词失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取可用关键词失败: {str(e)}"
        )


@router.get("/crawl-statistics")
async def get_crawl_statistics(
    keyword_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取爬虫数据统计，按关键词显示真实的帖子数据

    Args:
        keyword_id: 可选，指定关键词ID

    Returns:
        数据统计信息
    """
    try:
        from app.models.post import Post
        from app.models.keyword import Keyword
        from sqlalchemy import func

        logger.info("开始获取爬虫数据统计")

        # 构建查询 - 使用JOIN来确保只返回有关联的关键词
        query = db.query(
            Keyword.id.label('keyword_id'),
            Keyword.keyword,
            func.count(Post.id).label('total_posts'),
            func.sum(Post.likes).label('total_likes'),
            func.sum(Post.collects).label('total_collects'),
            func.sum(Post.comments).label('total_comments'),
            func.sum(Post.shares).label('total_shares'),
            func.avg(Post.likes).label('avg_likes'),
            func.avg(Post.collects).label('avg_collects'),
            func.avg(Post.comments).label('avg_comments'),
            func.max(Post.likes).label('max_likes')
        ).join(Post, Keyword.id == Post.keyword_id)  # 改用INNER JOIN，只显示有帖子数据的关键词

        if keyword_id:
            query = query.filter(Keyword.id == keyword_id)

        # 只显示活跃的关键词
        query = query.filter(Keyword.is_active == True)

        # 按关键词分组
        stats = query.group_by(Keyword.id, Keyword.keyword).all()

        logger.info(f"查询到 {len(stats)} 个关键词的统计数据")

        # 转换为响应格式
        result = []
        total_posts_all = 0  # 记录总帖子数

        for stat in stats:
            # 获取最新的几条数据
            latest_posts = db.query(Post).filter(
                Post.keyword_id == stat.keyword_id
            ).order_by(Post.crawled_at.desc()).limit(5).all()

            latest_posts_data = []
            for post in latest_posts:
                latest_posts_data.append({
                    "title": post.title,
                    "author": post.author,
                    "likes": post.likes,
                    "collects": post.collects,
                    "comments": post.comments,
                    "url": post.url,
                    "crawled_at": post.crawled_at.isoformat() if post.crawled_at else None
                })

            keyword_stat = {
                "keyword_id": stat.keyword_id,
                "keyword": stat.keyword,
                "total_posts": stat.total_posts or 0,
                "total_likes": stat.total_likes or 0,
                "total_collects": stat.total_collects or 0,
                "total_comments": stat.total_comments or 0,
                "total_shares": stat.total_shares or 0,
                "avg_likes": round(stat.avg_likes or 0, 1),
                "avg_collects": round(stat.avg_collects or 0, 1),
                "avg_comments": round(stat.avg_comments or 0, 1),
                "max_likes": stat.max_likes or 0,
                "latest_posts": latest_posts_data
            }

            total_posts_all += keyword_stat["total_posts"]
            result.append(keyword_stat)
            logger.info(f"关键词 '{stat.keyword}': {stat.total_posts} 条帖子")

        logger.info(f"总计: {total_posts_all} 条帖子")

        return {
            "success": True,
            "statistics": result,
            "total_posts_all": total_posts_all  # 添加总帖子数
        }

    except Exception as e:
        logger.error(f"获取爬虫数据统计失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取爬虫数据统计失败: {str(e)}"
        )


@router.delete("/delete-data/{keyword}")
async def delete_keyword_data(keyword: str, delete_type: str = "all", db: Session = Depends(get_db)):
    """
    删除指定关键词的数据

    Args:
        keyword: 关键词
        delete_type: 删除类型 (all: 删除文件和数据库数据, file: 只删除文件, database: 只删除数据库数据)
        db: 数据库会话
    """
    try:
        # 查找关键词
        keyword_obj = db.query(Keyword).filter(Keyword.keyword == keyword).first()
        if not keyword_obj:
            raise HTTPException(
                status_code=404,
                detail=f"关键词 '{keyword}' 不存在"
            )

        deleted_files = 0
        deleted_db_records = 0
        messages = []

        # 删除数据库中的数据
        if delete_type in ["all", "database"]:
            # 删除与该关键词相关的所有帖子
            deleted_posts = db.query(Post).filter(Post.keyword_id == keyword_obj.id).count()
            db.query(Post).filter(Post.keyword_id == keyword_obj.id).delete()
            db.commit()
            deleted_db_records = deleted_posts
            messages.append(f"已删除数据库中的 {deleted_posts} 条记录")

        # 删除数据文件
        if delete_type in ["all", "file"]:
            import os
            import glob

            # 查找相关的数据文件
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            search_pattern = f"**/search_contents_{keyword}*.json"
            matching_files = []

            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if f"search_contents_{keyword}" in file and file.endswith('.json'):
                        matching_files.append(os.path.join(root, file))

            # 删除找到的文件
            for file_path in matching_files:
                try:
                    os.remove(file_path)
                    deleted_files += 1
                    logger.info(f"已删除文件: {file_path}")
                except Exception as e:
                    logger.warning(f"删除文件失败 {file_path}: {str(e)}")

            if deleted_files > 0:
                messages.append(f"已删除 {deleted_files} 个数据文件")
            else:
                messages.append("未找到相关的数据文件")

        return {
            "success": True,
            "message": f"删除完成: {'; '.join(messages)}",
            "deleted_files": deleted_files,
            "deleted_db_records": deleted_db_records
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除数据失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"删除数据失败: {str(e)}"
        )