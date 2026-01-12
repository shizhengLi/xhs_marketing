"""
报告生成服务 - 每日生成小红书热点趋势报告
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.keyword import Keyword
from app.models.post import Post
from app.models.report import Report
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)


class ReportGenerationService:
    """报告生成服务"""

    def __init__(self):
        self.openai_service = openai_service

    def generate_daily_report(self, db: Session) -> Dict[str, Any]:
        """
        生成每日热点报告

        Args:
            db: 数据库会话

        Returns:
            报告生成结果
        """
        try:
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)

            # 检查今天是否已经生成过报告
            existing_report = db.query(Report).filter(
                Report.report_date == today
            ).first()

            if existing_report:
                return {
                    "success": False,
                    "message": "今日报告已生成",
                    "report_id": existing_report.id
                }

            # 获取所有活跃关键词
            keywords = db.query(Keyword).filter(Keyword.is_active == True).all()

            if not keywords:
                return {
                    "success": False,
                    "message": "没有活跃的关键词"
                }

            # 收集昨天的数据进行分析
            analyses = []
            for keyword in keywords:
                # 获取该关键词的最新帖子（按点赞排序）
                recent_posts = db.query(Post).filter(
                    Post.keyword_id == keyword.id,
                    Post.crawled_at >= yesterday
                ).order_by(Post.likes.desc()).limit(20).all()

                if not recent_posts:
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
                        'content': post.content,
                        'url': post.url,
                        'crawled_at': post.crawled_at.isoformat()
                    })

                # 使用GPT进行分析
                analysis = self.openai_service.analyze_trending_content(
                    posts_data, keyword.keyword
                )

                if analysis.get('success'):
                    analyses.append(analysis.get('analysis', {}))

            if not analyses:
                return {
                    "success": False,
                    "message": "没有可分析的数据"
                }

            # 生成综合报告，使用新的增强方法
            report_content = self.openai_service.generate_comprehensive_daily_report(
                analyses,
                datetime.now().strftime("%Y年%m月%d日")
            )

            # 保存报告到数据库
            report = Report(
                user_id=1,  # 默认用户
                keyword_id=None,  # 综合报告
                title=f"小红书热点趋势报告 - {today.strftime('%Y-%m-%d')}",
                content=report_content,
                summary=self._generate_summary(analyses),
                report_date=today
            )

            db.add(report)
            db.commit()
            db.refresh(report)

            logger.info(f"成功生成每日报告: {report.id}")

            return {
                "success": True,
                "message": "报告生成成功",
                "report_id": report.id,
                "report_date": today.isoformat(),
                "keywords_analyzed": len(analyses)
            }

        except Exception as e:
            db.rollback()
            logger.error(f"生成每日报告失败: {str(e)}")
            return {
                "success": False,
                "message": f"报告生成失败: {str(e)}"
            }

    def generate_keyword_report(self, keyword_id: int, db: Session) -> Dict[str, Any]:
        """
        为单个关键词生成报告

        Args:
            keyword_id: 关键词ID
            db: 数据库会话

        Returns:
            报告生成结果
        """
        try:
            # 获取关键词
            keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
            if not keyword:
                return {
                    "success": False,
                    "message": "关键词不存在"
                }

            # 获取最近7天的数据
            seven_days_ago = datetime.now() - timedelta(days=7)

            recent_posts = db.query(Post).filter(
                Post.keyword_id == keyword_id,
                Post.crawled_at >= seven_days_ago
            ).order_by(Post.likes.desc()).limit(30).all()

            if not recent_posts:
                return {
                    "success": False,
                    "message": "该关键词暂无数据"
                }

            # 转换数据格式
            posts_data = []
            for post in recent_posts:
                posts_data.append({
                    'title': post.title,
                    'author': post.author,
                    'likes': post.likes,
                    'collects': post.collects,
                    'comments': post.comments,
                    'content': post.content,
                    'url': post.url,
                    'crawled_at': post.crawled_at.isoformat()
                })

            # 使用GPT进行分析
            analysis = self.openai_service.analyze_trending_content(
                posts_data, keyword.keyword
            )

            if not analysis.get('success'):
                return {
                    "success": False,
                    "message": "GPT分析失败"
                }

            # 生成关键词报告
            analysis_data = analysis.get('analysis', {})

            report = Report(
                user_id=1,
                keyword_id=keyword_id,
                title=f"{keyword.keyword} - 热点分析报告",
                content=str(analysis_data),
                summary=analysis_data.get('summary', ''),
                report_date=datetime.now().date()
            )

            db.add(report)
            db.commit()
            db.refresh(report)

            return {
                "success": True,
                "message": "关键词报告生成成功",
                "report_id": report.id
            }

        except Exception as e:
            db.rollback()
            logger.error(f"生成关键词报告失败: {str(e)}")
            return {
                "success": False,
                "message": f"报告生成失败: {str(e)}"
            }

    def _generate_summary(self, analyses: List[Dict[str, Any]]) -> str:
        """生成报告摘要"""
        if not analyses:
            return "暂无分析数据"

        summary_parts = []

        for i, analysis in enumerate(analyses):
            keyword = analysis.get('keyword', f'关键词{i+1}')
            trends = analysis.get('trends', [])
            summary_parts.append(f"{keyword}: {', '.join(trends[:3])}")

        return " | ".join(summary_parts)


# 全局实例
report_service = ReportGenerationService()