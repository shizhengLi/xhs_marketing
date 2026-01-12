"""
报告生成API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from app.core.deps import get_db, get_current_user_id
from app.services.report_service import report_service
from app.services.openai_service import openai_service
from app.database import SessionLocal
from app.models.keyword import Keyword
from app.models.post import Post

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze-keywords")
async def analyze_keywords_trending(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    分析所有活跃关键词的热点内容，按关键词领域分别分析

    Returns:
        各关键词的分析结果
    """
    db = SessionLocal()
    try:
        # 获取所有活跃关键词
        keywords = db.query(Keyword).filter(Keyword.is_active == True).all()

        if not keywords:
            raise HTTPException(
                status_code=404,
                detail="没有活跃的关键词"
            )

        # 为每个关键词进行GPT分析
        analyses = []
        for keyword in keywords:
            try:
                # 获取该关键词的最新帖子数据
                recent_posts = db.query(Post).filter(
                    Post.keyword_id == keyword.id
                ).order_by(Post.likes.desc()).limit(15).all()

                if not recent_posts:
                    logger.info(f"关键词 '{keyword.keyword}' 没有数据，跳过分析")
                    continue

                # 转换为字典格式
                posts_data = []
                for post in recent_posts:
                    posts_data.append({
                        'title': post.title,
                        'author': post.author,
                        'likes': post.likes,
                        'collects': post.collects,
                        'comments': post.comments,
                        'shares': post.shares,
                        'content': post.content,
                        'url': post.url,
                        'crawled_at': post.crawled_at.isoformat() if post.crawled_at else None
                    })

                # 使用增强的GPT服务进行分析
                analysis = openai_service.analyze_trending_content(
                    posts_data, keyword.keyword
                )

                if analysis.get('success'):
                    analyses.append({
                        "keyword": keyword.keyword,
                        "keyword_id": keyword.id,
                        "posts_analyzed": len(posts_data),
                        "analysis": analysis.get('analysis', {}),
                        "analysis_date": analysis.get('analysis_date'),
                        "model_used": analysis.get('model_used', 'gpt-4o-mini')
                    })
                    logger.info(f"成功分析关键词: {keyword.keyword}")
                else:
                    logger.warning(f"关键词 '{keyword.keyword}' 分析失败: {analysis.get('error')}")

            except Exception as e:
                logger.error(f"分析关键词 '{keyword.keyword}' 时出错: {str(e)}")
                continue

        if not analyses:
            raise HTTPException(
                status_code=400,
                detail="没有成功生成任何分析，请确保有足够的数据和OpenAI API配置正确"
            )

        return {
            "success": True,
            "total_keywords": len(keywords),
            "analyzed_keywords": len(analyses),
            "analyses": analyses,
            "summary": {
                "message": f"成功分析 {len(analyses)} 个关键词的热点内容",
                "keywords_analyzed": [a['keyword'] for a in analyses]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分析关键词API错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )
    finally:
        db.close()


@router.post("/generate-comprehensive-report")
async def generate_comprehensive_report(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    生成综合性的热点趋势分析报告，按不同关键词领域分析
    """
    try:
        # 首先分析各关键词
        analysis_result = await analyze_keywords_trending(current_user_id)

        if not analysis_result.get('success'):
            raise HTTPException(
                status_code=400,
                detail="分析关键词失败，无法生成报告"
            )

        analyses = analysis_result.get('analyses', [])

        # 生成综合报告
        report_content = openai_service.generate_comprehensive_daily_report(
            analyses,
            None  # 使用当前日期
        )

        # 保存报告到数据库
        from app.models.report import Report
        from datetime import datetime

        today = datetime.now().date()

        report = Report(
            user_id=int(current_user_id),
            keyword_id=None,  # 综合报告
            title=f"🎯 小红书热点趋势综合分析报告 - {today.strftime('%Y-%m-%d')}",
            content=report_content,
            summary=f"分析了 {len(analyses)} 个关键词领域的热点内容，提供深度趋势洞察和战略建议。",
            report_date=today
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        logger.info(f"成功生成综合热点分析报告: {report.id}")

        return {
            "success": True,
            "message": "综合热点分析报告生成成功",
            "report_id": report.id,
            "report_date": today.isoformat(),
            "keywords_analyzed": len(analyses),
            "preview": {
                "title": report.title,
                "summary": report.summary,
                "keywords": [a['keyword'] for a in analyses]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"生成综合报告API错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"报告生成失败: {str(e)}"
        )


@router.post("/generate-daily-report")
async def generate_daily_report(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    生成每日热点报告
    """
    try:
        result = report_service.generate_daily_report(db)

        if result.get('success'):
            return {
                "success": True,
                "message": "每日报告生成成功",
                "report_id": result.get('report_id'),
                "report_date": result.get('report_date'),
                "keywords_analyzed": result.get('keywords_analyzed')
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get('message', '报告生成失败')
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成每日报告API错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器错误: {str(e)}"
        )


@router.post("/generate-keyword-report/{keyword_id}")
async def generate_keyword_report(
    keyword_id: int,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    为指定关键词生成报告
    """
    try:
        result = report_service.generate_keyword_report(keyword_id, db)

        if result.get('success'):
            return {
                "success": True,
                "message": "关键词报告生成成功",
                "report_id": result.get('report_id')
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get('message', '报告生成失败')
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成关键词报告API错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器错误: {str(e)}"
        )


@router.get("/reports")
async def get_reports(
    keyword_id: int = None,
    limit: int = 10,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取报告列表
    """
    try:
        from app.models.report import Report

        query = db.query(Report).filter(Report.user_id == int(current_user_id))

        if keyword_id:
            query = query.filter(Report.keyword_id == keyword_id)

        reports = query.order_by(Report.created_at.desc()).limit(limit).all()

        return {
            "success": True,
            "reports": [
                {
                    "id": report.id,
                    "title": report.title,
                    "summary": report.summary,
                    "report_date": report.report_date.isoformat(),
                    "created_at": report.created_at.isoformat(),
                    "keyword_id": report.keyword_id
                }
                for report in reports
            ]
        }

    except Exception as e:
        logger.error(f"获取报告列表错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器错误: {str(e)}"
        )


@router.get("/reports/{report_id}")
async def get_report_detail(
    report_id: int,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取报告详情
    """
    try:
        from app.models.report import Report

        report = db.query(Report).filter(
            Report.id == report_id,
            Report.user_id == int(current_user_id)
        ).first()

        if not report:
            raise HTTPException(
                status_code=404,
                detail="报告不存在"
            )

        return {
            "success": True,
            "report": {
                "id": report.id,
                "title": report.title,
                "content": report.content,
                "summary": report.summary,
                "report_date": report.report_date.isoformat(),
                "created_at": report.created_at.isoformat(),
                "keyword_id": report.keyword_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取报告详情错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器错误: {str(e)}"
        )