"""
定时任务调度API
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.services.scheduler_service import scheduler_service, get_scheduler_status

router = APIRouter()


class ScheduleCreate(BaseModel):
    """创建定时任务请求"""
    hour: int  # 小时 (0-23)
    minute: int  # 分钟 (0-59)
    keyword_id: int | None = None  # 指定关键词ID，None表示所有关键词
    schedule_type: str = "daily"  # daily-每日, interval-间隔
    max_results: int = 15  # 每个关键词最大爬取结果数量，默认15条


class ScheduleResponse(BaseModel):
    """定时任务响应"""
    is_running: bool
    jobs: List[Dict[str, Any]]
    current_time: str


@router.post("/setup", response_model=Dict[str, Any])
async def setup_schedule(schedule: ScheduleCreate):
    """
    设置定时爬取任务

    Args:
        schedule: 定时任务配置

    Returns:
        设置结果
    """
    try:
        # 验证时间参数
        if not (0 <= schedule.hour <= 23):
            raise HTTPException(
                status_code=400,
                detail="小时必须在0-23之间"
            )

        if not (0 <= schedule.minute <= 59):
            raise HTTPException(
                status_code=400,
                detail="分钟必须在0-59之间"
            )

        # 启动调度器（如果未启动）
        if not scheduler_service.is_running:
            scheduler_service.start()

        # 添加任务
        if schedule.schedule_type == "daily":
            scheduler_service.add_daily_crawl_job(
                hour=schedule.hour,
                minute=schedule.minute,
                keyword_id=schedule.keyword_id,
                max_results=schedule.max_results
            )
        elif schedule.schedule_type == "interval":
            # 计算间隔分钟数
            interval_minutes = schedule.hour * 60 + schedule.minute
            if interval_minutes > 0:
                scheduler_service.add_interval_crawl_job(
                    minutes=interval_minutes,
                    keyword_id=schedule.keyword_id,
                    max_results=schedule.max_results
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="间隔时间必须大于0"
                )

        return {
            "success": True,
            "message": f"定时任务已设置: 每天 {schedule.hour:02d}:{schedule.minute:02d}",
            "schedule_time": f"{schedule.hour:02d}:{schedule.minute:02d}",
            "keyword_id": schedule.keyword_id,
            "schedule_type": schedule.schedule_type,
            "max_results": schedule.max_results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"设置定时任务失败: {str(e)}"
        )


@router.get("/status", response_model=ScheduleResponse)
async def get_schedule_status():
    """
    获取调度器状态

    Returns:
        调度器状态信息
    """
    try:
        return await get_scheduler_status()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取调度器状态失败: {str(e)}"
        )


@router.delete("/jobs/{job_id}")
async def delete_schedule_job(job_id: str):
    """
    删除定时任务

    Args:
        job_id: 任务ID

    Returns:
        删除结果
    """
    try:
        success = scheduler_service.remove_job(job_id)

        if success:
            return {
                "success": True,
                "message": f"任务 {job_id} 已删除"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"任务 {job_id} 不存在"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除任务失败: {str(e)}"
        )


@router.post("/start")
async def start_scheduler():
    """
    启动调度器

    Returns:
        启动结果
    """
    try:
        if not scheduler_service.is_running:
            scheduler_service.start()
            return {
                "success": True,
                "message": "调度器已启动"
            }
        else:
            return {
                "success": True,
                "message": "调度器已在运行"
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"启动调度器失败: {str(e)}"
        )


@router.post("/stop")
async def stop_scheduler():
    """
    停止调度器

    Returns:
        停止结果
    """
    try:
        if scheduler_service.is_running:
            scheduler_service.stop()
            return {
                "success": True,
                "message": "调度器已停止"
            }
        else:
            return {
                "success": True,
                "message": "调度器未运行"
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"停止调度器失败: {str(e)}"
        )


@router.post("/test-crawl/{keyword_id}")
async def test_crawl_keyword(keyword_id: int):
    """
    测试爬取指定关键词

    Args:
        keyword_id: 关键词ID

    Returns:
        爬取结果
    """
    from app.database import SessionLocal
    from app.models.keyword import Keyword as KeywordModel

    db = SessionLocal()
    try:
        keyword = db.query(KeywordModel).filter(
            KeywordModel.id == keyword_id
        ).first()

        if not keyword:
            raise HTTPException(
                status_code=404,
                detail="关键词不存在"
            )

        # 执行测试爬取
        from app.services.mediacrawler_service import crawl_trending_content
        notes = await crawl_trending_content(keyword.keyword, 5)

        return {
            "success": True,
            "keyword": keyword.keyword,
            "crawled_count": len(notes),
            "sample_data": notes[:3] if notes else []
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"测试爬取失败: {str(e)}"
        )
    finally:
        db.close()