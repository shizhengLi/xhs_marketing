"""
基于MediaCrawler逻辑的小红书爬虫服务
集成MediaCrawler的核心功能，实现定时抓取
"""
import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

# 添加MediaCrawler路径
mediacrawler_path = Path(__file__).parent.parent.parent.parent / "MediaCrawler"
sys.path.insert(0, str(mediacrawler_path))

logger = logging.getLogger(__name__)


class XiaohongshuCrawlerService:
    """小红书爬虫服务"""

    def __init__(self):
        self.crawler = None
        self.is_initialized = False

    async def initialize(self):
        """初始化爬虫"""
        try:
            if not self.is_initialized:
                # 动态导入MediaCrawler
                from main import CrawlerFactory
                from media_platform.xhs import XiaoHongShuCrawler

                logger.info("正在初始化小红书爬虫...")
                self.crawler = CrawlerFactory.create_crawler(platform="xhs")
                self.is_initialized = True
                logger.info("小红书爬虫初始化成功")

        except Exception as e:
            logger.error(f"初始化小红书爬虫失败: {str(e)}")
            # 降级到简化爬虫
            self._initialize_fallback_crawler()

    def _initialize_fallback_crawler(self):
        """初始化简化爬虫（备用方案）"""
        logger.info("使用简化版爬虫作为备用方案")
        from app.services.real_crawler import RealXiaohongshuCrawler
        self.crawler = RealXiaohongshuCrawler()
        self.is_initialized = True

    async def search_hot_notes_by_keyword(
        self,
        keyword: str,
        sort_type: str = "popularity_descending",
        count: int = 20
    ) -> List[Dict[str, Any]]:
        """
        根据关键词搜索热门笔记

        Args:
            keyword: 搜索关键词
            sort_type: 排序方式 (popularity_descending-热度降序, time_descending-时间降序)
            count: 获取数量

        Returns:
            笔记列表
        """
        try:
            await self.initialize()

            if hasattr(self.crawler, 'search_notes'):
                # 使用MediaCrawler的搜索功能
                notes_data = await self.crawler.search_notes(
                    keyword=keyword,
                    page=1,
                    sort=SortType.popularity_descending if sort_type == "popularity_descending" else SortType.time_descending
                )

                # 转换数据格式
                return self._convert_notes_data(notes_data[:count])
            else:
                # 使用简化爬虫
                return await self.crawler.search_by_keyword(keyword, count)

        except Exception as e:
            logger.error(f"搜索笔记失败: {str(e)}")
            return []

    def _convert_notes_data(self, notes_data: List) -> List[Dict[str, Any]]:
        """转换笔记数据格式"""
        converted_notes = []

        for note in notes_data:
            try:
                converted_note = {
                    "title": note.get("title", ""),
                    "content": note.get("desc", ""),
                    "author": note.get("user", {}).get("nickname", "匿名用户"),
                    "likes": note.get("liked_count", 0),
                    "collects": note.get("collected_count", 0),
                    "comments": note.get("comment_count", 0),
                    "shares": note.get("share_count", 0),
                    "image_url": note.get("cover", {}).get("url_default", ""),
                    "note_url": f"https://www.xiaohongshu.com/explore/{note.get('note_id', '')}",
                    "note_id": note.get("note_id", ""),
                    "published_at": note.get("time", datetime.now().isoformat()),
                    "crawl_time": datetime.now().isoformat()
                }
                converted_notes.append(converted_note)
            except Exception as e:
                logger.warning(f"转换笔记数据失败: {str(e)}")
                continue

        return converted_notes

    async def get_trending_notes(
        self,
        keyword: str,
        time_range: str = "daily",
        min_likes: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        获取趋势笔记（高赞、高互动内容）

        Args:
            keyword: 关键词
            time_range: 时间范围 (daily-每日, weekly-每周, monthly-每月)
            min_likes: 最小点赞数

        Returns:
            热门笔记列表
        """
        try:
            # 搜索并排序
            notes = await self.search_hot_notes_by_keyword(
                keyword=keyword,
                sort_type="popularity_descending",
                count=50
            )

            # 过滤条件
            filtered_notes = []
            for note in notes:
                if note["likes"] >= min_likes:
                    # 时间过滤
                    if self._is_within_time_range(note["published_at"], time_range):
                        filtered_notes.append(note)

            return filtered_notes[:20]  # 返回前20条

        except Exception as e:
            logger.error(f"获取趋势笔记失败: {str(e)}")
            return []

    def _is_within_time_range(self, publish_time: str, time_range: str) -> bool:
        """检查是否在时间范围内"""
        try:
            now = datetime.now()
            if time_range == "daily":
                threshold = now - timedelta(days=1)
            elif time_range == "weekly":
                threshold = now - timedelta(weeks=1)
            elif time_range == "monthly":
                threshold = now - timedelta(days=30)
            else:
                return True

            # 解析发布时间
            if isinstance(publish_time, str):
                publish_dt = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
            else:
                publish_dt = publish_time

            return publish_dt >= threshold

        except Exception as e:
            logger.warning(f"时间范围检查失败: {str(e)}")
            return True

    async def close(self):
        """关闭爬虫"""
        if self.crawler and hasattr(self.crawler, 'close'):
            try:
                await self.crawler.close()
            except Exception as e:
                logger.warning(f"关闭爬虫时出错: {str(e)}")


# 全局爬虫实例
xiaohongshu_crawler = XiaohongshuCrawlerService()


async def crawl_trending_content(keyword: str, count: int = 20) -> List[Dict[str, Any]]:
    """
    抓取趋势内容的便捷函数

    Args:
        keyword: 关键词
        count: 数量

    Returns:
        笔记列表
    """
    try:
        logger.info(f"开始抓取关键词 '{keyword}' 的趋势内容")
        notes = await xiaohongshu_crawler.get_trending_notes(
            keyword=keyword,
            time_range="daily",
            min_likes=100
        )
        logger.info(f"成功抓取 {len(notes)} 条趋势内容")
        return notes[:count]

    except Exception as e:
        logger.error(f"抓取趋势内容失败: {str(e)}")
        return []


# 新增：MediaCrawler自动化服务
class MediaCrawlerAutomationService:
    """MediaCrawler自动化服务"""

    def __init__(self):
        # MediaCrawler 项目路径
        self.mediacrawler_path = Path(__file__).parent.parent.parent.parent / "MediaCrawler"
        self.config_path = self.mediacrawler_path / "config"

        # 配置文件路径
        self.base_config_path = self.config_path / "base_config.py"
        self.xhs_config_path = self.config_path / "xhs_config.py"

    def update_keywords_in_config(self, keywords: List[str]) -> bool:
        """
        更新配置文件中的关键词

        Args:
            keywords: 关键词列表

        Returns:
            更新是否成功
        """
        try:
            import re
            # 读取base_config.py文件
            with open(self.base_config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换KEYWORDS配置
            keywords_str = ",".join(keywords)
            pattern = r'KEYWORDS = ".*?"'
            replacement = f'KEYWORDS = "{keywords_str}"'
            new_content = re.sub(pattern, replacement, content)

            # 写回文件
            with open(self.base_config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            logger.info(f"已更新关键词配置: {keywords_str}")
            return True

        except Exception as e:
            logger.error(f"更新关键词配置失败: {str(e)}")
            return False

    def update_login_type(self, login_type: str = "qrcode") -> bool:
        """
        更新登录方式配置

        Args:
            login_type: 登录方式 (qrcode/phone/cookie)

        Returns:
            更新是否成功
        """
        try:
            import re
            # 读取base_config.py文件
            with open(self.base_config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换LOGIN_TYPE配置
            pattern = r'LOGIN_TYPE = ".*?"'
            replacement = f'LOGIN_TYPE = "{login_type}"'
            new_content = re.sub(pattern, replacement, content)

            # 写回文件
            with open(self.base_config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            logger.info(f"已更新登录方式配置: {login_type}")
            return True

        except Exception as e:
            logger.error(f"更新登录方式配置失败: {str(e)}")
            return False

    def update_crawler_count(self, count: int = 15) -> bool:
        """
        更新爬取数量配置

        Args:
            count: 每个关键词爬取的数量

        Returns:
            更新是否成功
        """
        try:
            import re
            # 读取base_config.py文件
            with open(self.base_config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换CRAWLER_MAX_NOTES_COUNT配置
            pattern = r'CRAWLER_MAX_NOTES_COUNT = \d+'
            replacement = f'CRAWLER_MAX_NOTES_COUNT = {count}'
            new_content = re.sub(pattern, replacement, content)

            # 写回文件
            with open(self.base_config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            logger.info(f"已更新爬取数量配置: {count}")
            return True

        except Exception as e:
            logger.error(f"更新爬取数量配置失败: {str(e)}")
            return False

    def ensure_headless_off(self) -> bool:
        """
        确保浏览器显示模式（关闭无头模式）
        这样用户可以看到扫码二维码

        Returns:
            设置是否成功
        """
        try:
            import re
            # 读取base_config.py文件
            with open(self.base_config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换HEADLESS配置
            content = re.sub(r'HEADLESS = (True|False)', 'HEADLESS = False', content)

            # 禁用CDP模式，确保浏览器正常显示
            content = re.sub(r'ENABLE_CDP_MODE = (True|False)', 'ENABLE_CDP_MODE = False', content)

            # 添加强制显示浏览器配置
            if 'FORCE_SHOW_BROWSER' not in content:
                content = content.replace('HEADLESS = False',
                                        'HEADLESS = False\n\n# 强制显示浏览器，不管其他设置\nFORCE_SHOW_BROWSER = True')

            # 写回文件
            with open(self.base_config_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info("已设置浏览器显示模式并禁用CDP模式")
            return True

        except Exception as e:
            logger.error(f"设置浏览器显示模式失败: {str(e)}")
            return False

    async def start_xhs_crawler(self, keywords: List[str], count: int = 15) -> Dict[str, Any]:
        """
        启动小红书爬虫

        Args:
            keywords: 关键词列表
            count: 每个关键词爬取的数量

        Returns:
            启动结果
        """
        try:
            # 1. 更新配置
            self.update_keywords_in_config(keywords)
            self.update_crawler_count(count)
            self.update_login_type("qrcode")  # 默认使用扫码登录
            self.ensure_headless_off()  # 确保显示浏览器

            # 2. 准备启动命令
            command = [
                "uv", "run", "main.py"
            ]

            logger.info(f"启动命令: {' '.join(command)}")
            logger.info(f"工作目录: {self.mediacrawler_path}")

            # 3. 启动爬虫进程
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=str(self.mediacrawler_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )

            logger.info(f"MediaCrawler进程已启动，PID: {process.pid}")

            return {
                "success": True,
                "message": "MediaCrawler已启动，浏览器将自动打开，请扫描二维码登录",
                "process_id": process.pid,
                "keywords": keywords,
                "count": count
            }

        except Exception as e:
            logger.error(f"启动MediaCrawler失败: {str(e)}")
            return {
                "success": False,
                "message": f"启动失败: {str(e)}",
                "error": str(e)
            }

    async def check_and_start_browser(self) -> Dict[str, Any]:
        """
        仅启动浏览器登录（不进行爬取）
        用于用户首次登录

        Returns:
            启动结果
        """
        try:
            # 设置为扫码登录
            self.update_login_type("qrcode")
            self.ensure_headless_off()

            # 使用最小配置启动（空关键词）
            self.update_keywords_in_config([""])

            command = [
                "uv", "run", "main.py"
            ]

            logger.info(f"启动浏览器登录: {' '.join(command)}")

            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=str(self.mediacrawler_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )

            return {
                "success": True,
                "message": "浏览器已启动，请扫描二维码登录",
                "process_id": process.pid
            }

        except Exception as e:
            logger.error(f"启动浏览器登录失败: {str(e)}")
            return {
                "success": False,
                "message": f"启动失败: {str(e)}",
                "error": str(e)
            }

    def get_config_info(self) -> Dict[str, Any]:
        """
        获取当前配置信息

        Returns:
            配置信息
        """
        try:
            import re
            # 读取配置
            with open(self.base_config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取配置信息
            keywords_match = re.search(r'KEYWORDS = "(.*?)"', content)
            login_type_match = re.search(r'LOGIN_TYPE = "(.*?)"', content)
            headless_match = re.search(r'HEADLESS = (True|False)', content)
            count_match = re.search(r'CRAWLER_MAX_NOTES_COUNT = (\d+)', content)

            return {
                "success": True,
                "keywords": keywords_match.group(1) if keywords_match else "",
                "login_type": login_type_match.group(1) if login_type_match else "qrcode",
                "headless": headless_match.group(1) if headless_match else "False",
                "max_count": int(count_match.group(1)) if count_match else 15,
                "project_path": str(self.mediacrawler_path)
            }

        except Exception as e:
            logger.error(f"获取配置信息失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# 全局自动化服务实例
mediacrawler_automation = MediaCrawlerAutomationService()