"""
MediaCrawler数据导入服务
将MediaCrawler爬取的JSON数据导入到项目数据库中
"""
import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import logging

from app.models.post import Post
from app.models.keyword import Keyword
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class MediaCrawlerDataImporter:
    """MediaCrawler数据导入器"""

    def __init__(self):
        # MediaCrawler数据目录
        self.mediacrawler_data_dir = Path(__file__).parent.parent.parent.parent / "MediaCrawler" / "data" / "xhs" / "json"
        logger.info(f"MediaCrawler数据目录: {self.mediacrawler_data_dir}")

    def get_latest_data_file(self) -> Optional[Path]:
        """获取最新的数据文件"""
        try:
            if not self.mediacrawler_data_dir.exists():
                logger.warning(f"数据目录不存在: {self.mediacrawler_data_dir}")
                return None

            # 查找所有search_contents开头的JSON文件
            data_files = list(self.mediacrawler_data_dir.glob("search_contents_*.json"))

            if not data_files:
                logger.warning("没有找到搜索内容数据文件")
                return None

            # 按修改时间排序，获取最新的文件
            latest_file = max(data_files, key=lambda f: f.stat().st_mtime)
            logger.info(f"找到最新数据文件: {latest_file}")
            return latest_file

        except Exception as e:
            logger.error(f"获取最新数据文件失败: {str(e)}")
            return None

    def parse_interaction_count(self, count_str: str) -> int:
        """解析互动数字符串，转换为整数"""
        try:
            if not count_str:
                return 0

            count_str = str(count_str).strip()

            # 处理"1.3万"这种格式
            if '万' in count_str:
                number = float(count_str.replace('万', '')) * 10000
                return int(number)

            # 处理纯数字
            return int(count_str)

        except (ValueError, TypeError):
            return 0

    def convert_mediacrawler_to_post(self, item: Dict[str, Any], keyword_id: int) -> Dict[str, Any]:
        """将MediaCrawler数据格式转换为项目Post模型格式"""
        try:
            # 提取数据
            note_id = item.get('note_id', '')
            title = item.get('title', '')
            desc = item.get('desc', '')
            nickname = item.get('nickname', '匿名用户')
            time_ms = item.get('time', 0)
            liked_count = item.get('liked_count', 0)
            collected_count = item.get('collected_count', 0)
            comment_count = item.get('comment_count', 0)
            share_count = item.get('share_count', 0)

            # 转换数据格式
            published_at = None
            if time_ms:
                try:
                    published_at = datetime.fromtimestamp(time_ms / 1000, tz=timezone.utc)
                except:
                    pass

            # 构建URL - 优先使用原始URL，没有则构建
            note_url = item.get('note_url', '')
            if note_url:
                url = note_url
            else:
                url = f"https://www.xiaohongshu.com/explore/{note_id}" if note_id else ""

            return {
                'keyword_id': keyword_id,
                'title': title or desc[:200] if desc else '',
                'content': desc,
                'author': nickname,
                'likes': self.parse_interaction_count(liked_count),
                'collects': self.parse_interaction_count(collected_count),
                'comments': self.parse_interaction_count(comment_count),
                'shares': self.parse_interaction_count(share_count),
                'url': url,
                'published_at': published_at,
            }

        except Exception as e:
            logger.error(f"转换数据失败: {str(e)}")
            raise

    def find_keyword_by_name(self, db: Session, keyword_name: str) -> Optional[Keyword]:
        """根据关键词名称查找关键词"""
        try:
            return db.query(Keyword).filter(Keyword.keyword == keyword_name).first()
        except Exception as e:
            logger.error(f"查找关键词失败: {str(e)}")
            return None

    def import_data_to_db(self, keyword_name: str) -> Dict[str, Any]:
        """导入数据到数据库"""
        db = None
        try:
            # 获取数据库会话
            db = SessionLocal()

            # 查找关键词
            keyword = self.find_keyword_by_name(db, keyword_name)
            if not keyword:
                logger.error(f"关键词不存在: {keyword_name}")
                return {
                    'success': False,
                    'message': f'关键词不存在: {keyword_name}',
                    'total_crawled': 0,
                    'new_saved': 0,
                    'updated': 0
                }

            # 获取最新数据文件
            data_file = self.get_latest_data_file()
            if not data_file:
                return {
                    'success': False,
                    'message': '没有找到可用的数据文件',
                    'total_crawled': 0,
                    'new_saved': 0,
                    'updated': 0
                }

            # 读取数据
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"读取到 {len(data)} 条数据")

            # 统计数据
            total_crawled = len(data)
            new_saved = 0
            updated = 0
            skipped = 0

            # 导入数据 - 只导入匹配关键词的数据
            for item in data:
                try:
                    # 检查数据项的source_keyword是否匹配当前关键词
                    item_keyword = item.get('source_keyword', '').strip()
                    if item_keyword != keyword_name:
                        skipped += 1
                        continue

                    # 转换数据格式
                    post_data = self.convert_mediacrawler_to_post(item, keyword.id)

                    # 检查是否已存在（基于URL去重）
                    existing_post = db.query(Post).filter(
                        Post.url == post_data['url'],
                        Post.keyword_id == keyword.id  # 同一关键词下去重
                    ).first()

                    if existing_post:
                        # 跳过已存在的数据，不重复导入
                        skipped += 1
                        continue

                    # 创建新数据
                    new_post = Post(**post_data)
                    db.add(new_post)
                    new_saved += 1

                except Exception as e:
                    logger.error(f"导入单条数据失败: {str(e)}")
                    skipped += 1
                    continue

            # 提交事务
            try:
                db.commit()
                logger.info(f"数据导入成功: 新增 {new_saved} 条，更新 {updated} 条，跳过 {skipped} 条")
            except IntegrityError as e:
                db.rollback()
                logger.error(f"数据库提交失败: {str(e)}")
                return {
                    'success': False,
                    'message': f'数据库提交失败: {str(e)}',
                    'total_crawled': total_crawled,
                    'new_saved': new_saved,
                    'updated': updated
                }

            # 关闭数据库连接
            db.close()

            return {
                'success': True,
                'message': f'数据导入成功',
                'total_crawled': total_crawled,
                'new_saved': new_saved,
                'updated': updated,
                'skipped': skipped
            }

        except Exception as e:
            logger.error(f"导入数据失败: {str(e)}")
            if db is not None:
                db.close()
            return {
                'success': False,
                'message': f'导入数据失败: {str(e)}',
                'total_crawled': 0,
                'new_saved': 0,
                'updated': 0
            }

    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据摘要信息"""
        try:
            data_file = self.get_latest_data_file()
            if not data_file:
                return {
                    'success': False,
                    'message': '没有找到数据文件',
                    'file_count': 0,
                    'latest_file': None,
                    'file_size': 0
                }

            # 只获取文件信息，不读取整个内容
            file_size = data_file.stat().st_size
            modified_time = datetime.fromtimestamp(data_file.stat().st_mtime).isoformat()

            # 快速估算行数（读取前几行）
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    # 读取文件开头来判断格式
                    first_lines = []
                    for i, line in enumerate(f):
                        if i < 10:  # 只读前10行
                            first_lines.append(line)
                        else:
                            break

                    # 如果是JSON数组，估算元素数量
                    if first_lines and first_lines[0].strip().startswith('['):
                        # 简单估算：假设平均每条记录100字符
                        estimated_count = max(1, file_size // 100)
                    else:
                        estimated_count = 0

            except Exception:
                estimated_count = 0

            return {
                'success': True,
                'file_count': estimated_count,
                'latest_file': str(data_file.name),
                'file_size': file_size,
                'modified_time': modified_time
            }

        except Exception as e:
            logger.error(f"获取数据摘要失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取数据摘要失败: {str(e)}',
                'file_count': 0,
                'latest_file': None,
                'file_size': 0
            }


# 全局导入器实例
media_importer = MediaCrawlerDataImporter()