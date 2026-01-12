"""
定时任务调度服务 - 按用户指定时间定时抓取小红书热点内容
"""
import asyncio
from datetime import datetime, time
from typing import List, Dict, Any
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.keyword import Keyword as KeywordModel
from app.models.post import Post as PostModel
from app.services.mediacrawler_service import crawl_trending_content

logger = logging.getLogger(__name__)


class CrawlerSchedulerService:
    """爬虫定时调度服务"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        """启动调度器"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("定时调度器已启动")

    def stop(self):
        """停止调度器"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("定时调度器已停止")

    def add_daily_crawl_job(self, hour: int, minute: int, keyword_id: int = None, max_results: int = 15):
        """
        添加每日定时爬取任务

        Args:
            hour: 小时 (0-23)
            minute: 分钟 (0-59)
            keyword_id: 指定关键词ID，None表示爬取所有活跃关键词
            max_results: 每个关键词最大爬取结果数量，默认15条
        """
        job_id = f"daily_crawl_{hour}_{minute}_{keyword_id if keyword_id else 'all'}"

        # 移除已存在的任务
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        # 添加新任务
        self.scheduler.add_job(
            self._daily_crawl_task,
            trigger=CronTrigger(hour=hour, minute=minute),
            id=job_id,
            args=[keyword_id, max_results],
            name=f"每日爬取 - {hour:02d}:{minute:02d}"
        )

        logger.info(f"已添加定时任务: {job_id} - 每天 {hour:02d}:{minute:02d}")

    def add_interval_crawl_job(self, minutes: int, keyword_id: int = None, max_results: int = 15):
        """
        添加间隔爬取任务

        Args:
            minutes: 间隔分钟数
            keyword_id: 指定关键词ID，None表示爬取所有活跃关键词
            max_results: 每个关键词最大爬取结果数量，默认15条
        """
        job_id = f"interval_crawl_{minutes}_{keyword_id if keyword_id else 'all'}"

        # 移除已存在的任务
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        # 添加新任务
        self.scheduler.add_job(
            self._daily_crawl_task,
            trigger='interval',
            minutes=minutes,
            id=job_id,
            args=[keyword_id, max_results],
            name=f"间隔爬取 - 每{minutes}分钟"
        )

        logger.info(f"已添加定时任务: {job_id} - 每{minutes}分钟")

    async def _daily_crawl_task(self, keyword_id: int = None, max_results: int = 15):
        """
        执行每日爬取任务

        Args:
            keyword_id: 指定关键词ID，None表示爬取所有活跃关键词
            max_results: 每个关键词最大爬取结果数量
        """
        logger.info(f"开始执行定时爬取任务 - 关键词ID: {keyword_id}")

        db = SessionLocal()
        try:
            # 获取要爬取的关键词
            if keyword_id:
                keywords = db.query(KeywordModel).filter(
                    KeywordModel.id == keyword_id,
                    KeywordModel.is_active == True
                ).all()
            else:
                keywords = db.query(KeywordModel).filter(
                    KeywordModel.is_active == True
                ).all()

            logger.info(f"找到 {len(keywords)} 个活跃关键词需要爬取")

            for keyword in keywords:
                try:
                    # 爬取趋势内容，使用配置的最大结果数量
                    notes = await crawl_trending_content(keyword.keyword, max_results)

                    # 保存到数据库
                    saved_count = 0
                    updated_count = 0

                    for note in notes:
                        # 检查是否已存在
                        existing_post = db.query(PostModel).filter(
                            PostModel.url == note["note_url"]
                        ).first()

                        if existing_post:
                            # 更新现有数据
                            existing_post.title = note["title"]
                            existing_post.content = note["content"]
                            existing_post.author = note["author"]
                            existing_post.likes = note["likes"]
                            existing_post.collects = note["collects"]
                            existing_post.comments = note["comments"]
                            existing_post.shares = note["shares"]
                            existing_post.crawled_at = datetime.now()
                            updated_count += 1
                        else:
                            # 创建新记录
                            new_post = PostModel(
                                keyword_id=keyword.id,
                                title=note["title"],
                                content=note["content"],
                                author=note["author"],
                                likes=note["likes"],
                                collects=note["collects"],
                                comments=note["comments"],
                                shares=note["shares"],
                                url=note["note_url"],
                                published_at=datetime.now(),  # 如果无法获取准确时间，使用当前时间
                                crawled_at=datetime.now()
                            )
                            db.add(new_post)
                            saved_count += 1

                    db.commit()
                    logger.info(f"关键词 '{keyword.keyword}' 爬取完成: 新增 {saved_count} 条，更新 {updated_count} 条")

                    # 避免频繁请求
                    await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"爬取关键词 '{keyword.keyword}' 时出错: {str(e)}")
                    db.rollback()

            logger.info("定时爬取任务执行完成")

            # 爬取完成后自动生成报告
            try:
                from app.services.report_service import report_service
                logger.info("开始生成每日热点报告")

                report_result = report_service.generate_daily_report(db)

                if report_result.get('success'):
                    logger.info(f"每日报告生成成功: 报告ID {report_result.get('report_id')}")
                else:
                    logger.warning(f"每日报告生成失败: {report_result.get('message')}")
            except Exception as e:
                logger.error(f"自动生成报告失败: {str(e)}")

        except Exception as e:
            logger.error(f"定时爬取任务执行失败: {str(e)}")
        finally:
            db.close()

    def list_jobs(self) -> List[Dict[str, Any]]:
        """列出所有任务"""
        jobs = self.scheduler.get_jobs()
        job_list = []

        for job in jobs:
            job_info = {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            job_list.append(job_info)

        return job_list

    def remove_job(self, job_id: str):
        """移除任务"""
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"已移除任务: {job_id}")
            return True
        return False


# 全局调度器实例
scheduler_service = CrawlerSchedulerService()


def setup_default_jobs():
    """设置默认的定时任务"""
    # 每天早上8点爬取一次
    scheduler_service.add_daily_crawl_job(hour=8, minute=0)

    # 每6小时爬取一次热门内容
    for hour in [0, 6, 12, 18]:
        scheduler_service.add_daily_crawl_job(hour=hour, minute=0)

    logger.info("默认定时任务已设置完成")


# 获取调度器信息的API端点
async def get_scheduler_status() -> Dict[str, Any]:
    """获取调度器状态"""
    return {
        "is_running": scheduler_service.is_running,
        "jobs": scheduler_service.list_jobs(),
        "current_time": datetime.now().isoformat()
    }