"""
模拟数据生成器 - 用于演示和测试
在实际生产环境中，应该使用合法的数据获取方式
"""
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict
from app.core.config import settings


class MockCrawler:
    """模拟爬虫 - 生成测试数据"""

    def __init__(self):
        # 模拟的关键词库
        self.keywords = [
            "护肤品", "美妆", "时尚", "穿搭", "美食",
            "旅游", "健身", "数码", "家居", "读书"
        ]

        # 模拟的用户名
        self.users = [
            "小红书达人", "美妆博主", "时尚达人", "生活记录者",
            "旅行爱好者", "美食探店", "科技测评", "健身教练"
        ]

        # 模拟的标题模板
        self.title_templates = [
            "分享我的{keyword}心得",
            "超好用的{keyword}推荐",
            "新手必看{keyword}攻略",
            "我的{keyword}日常",
            "{keyword}测评，真实体验",
            "推荐几个{keyword}神器",
            "关于{keyword}的那些事",
            "{keyword}避雷指南"
        ]

        # 模拟的内容模板
        self.content_templates = [
            "今天来分享一下我的{keyword}心得，希望对大家有帮助！",
            "最近发现了一个超棒的{keyword}，一定要推荐给大家！",
            "作为{keyword}爱好者，这个问题困扰我很久，终于找到了解决方案。",
            "新手如何入门{keyword}？我的经验分享。",
            "关于{keyword}的几个误区，很多人都不知道。"
        ]

    def generate_mock_notes(self, keyword: str, count: int = 10) -> List[Dict]:
        """
        生成模拟的小红书笔记数据

        Args:
            keyword: 关键词
            count: 生成数量

        Returns:
            模拟笔记列表
        """
        mock_notes = []

        for i in range(count):
            # 生成随机互动数据
            likes = random.randint(100, 50000)
            collects = random.randint(50, 20000)
            comments = random.randint(10, 5000)
            shares = random.randint(5, 1000)

            # 生成发布时间（最近30天内）
            days_ago = random.randint(0, 30)
            published_time = datetime.now() - timedelta(days=days_ago)

            # 生成标题和内容
            title_template = random.choice(self.title_templates)
            content_template = random.choice(self.content_templates)

            title = title_template.format(keyword=keyword)
            content = content_template.format(keyword=keyword)

            # 添加一些额外内容
            content += f"\n\n{'#' + keyword}\n#推荐 #分享 #日常"

            note = {
                'note_id': f"mock_{keyword}_{int(time.time())}_{i}",
                'title': title,
                'content': content,
                'author': random.choice(self.users),
                'likes': likes,
                'collects': collects,
                'comments': comments,
                'shares': shares,
                'cover_url': f"https://picsum.photos/400/500?random={i}",
                'url': f"https://www.xiaohongshu.com/explore/mock_{keyword}_{i}",
                'published_at': published_time.isoformat(),
                'crawled_at': datetime.now().isoformat()
            }

            mock_notes.append(note)

        # 按热度排序（点赞数 + 收藏数 * 2）
        mock_notes.sort(key=lambda x: x['likes'] + x['collects'] * 2, reverse=True)

        return mock_notes

    def generate_hot_trends(self, keyword: str) -> Dict:
        """
        生成模拟的热点趋势数据

        Args:
            keyword: 关键词

        Returns:
            趋势数据
        """
        # 生成过去7天的数据
        trends = []
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            daily_count = random.randint(50, 200)

            trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': daily_count,
                'avg_likes': random.randint(1000, 10000),
                'avg_collects': random.randint(500, 5000)
            })

        return {
            'keyword': keyword,
            'trends': trends,
            'total_notes': sum(t['count'] for t in trends),
            'hotness_score': random.randint(60, 100)
        }


# 创建全局模拟爬虫实例
mock_crawler = MockCrawler()


def crawl_by_keyword_mock(keyword: str, count: int = 20) -> List[Dict]:
    """
    使用模拟数据抓取

    Args:
        keyword: 关键词
        count: 抓取数量

    Returns:
        模拟笔记列表
    """
    print(f"正在生成关键词 '{keyword}' 的模拟数据...")
    mock_notes = mock_crawler.generate_mock_notes(keyword, count)
    print(f"生成了 {len(mock_notes)} 条模拟笔记")
    return mock_notes


def get_trends_mock(keyword: str) -> Dict:
    """
    获取模拟趋势数据

    Args:
        keyword: 关键词

    Returns:
        趋势数据
    """
    return mock_crawler.generate_hot_trends(keyword)