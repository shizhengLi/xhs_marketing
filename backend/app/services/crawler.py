"""
小红书内容抓取服务
注意：此实现仅供学习研究使用，请遵守相关法律法规和平台服务条款
"""
import asyncio
import random
import time
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import json
import base64

from app.core.config import settings
from app.services.video_service import process_video_with_retry


class XHSCrawler:
    """小红书内容抓取器 - 实现反爬虫对策"""

    def __init__(self):
        self.base_url = "https://www.xiaohongshu.com"
        self.api_base = "https://edith.xiaohongshu.com/api"

        # 反爬虫配置
        self.headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.xiaohongshu.com/',
            'Origin': 'https://www.xiaohongshu.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        }

        # 请求限制配置
        self.min_delay = 2  # 最小延迟2秒
        self.max_delay = 5  # 最大延迟5秒
        self.max_retries = 3  # 最大重试次数
        self.timeout = 30  # 请求超时时间

        # 代理池（如果使用）
        self.proxies = None

    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        return random.choice(user_agents)

    async def _random_delay(self):
        """随机延迟，避免被识别为机器人"""
        delay = random.uniform(self.min_delay, self.max_delay)
        await asyncio.sleep(delay)

    async def _make_request(self, url: str, params: dict = None, headers: dict = None) -> dict:
        """
        发送HTTP请求，包含反爬虫对策

        Args:
            url: 请求URL
            params: 请求参数
            headers: 自定义请求头

        Returns:
            响应数据
        """
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        # 随机更换User-Agent
        request_headers['User-Agent'] = self._get_random_user_agent()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    # 添加随机延迟
                    await self._random_delay()

                    response = await client.get(
                        url,
                        params=params,
                        headers=request_headers,
                        proxies=self.proxies,
                        follow_redirects=True
                    )

                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 429:
                        # 请求过于频繁，增加延迟
                        await asyncio.sleep(random.uniform(10, 20))
                        continue
                    else:
                        print(f"请求失败，状态码: {response.status_code}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(random.uniform(5, 10))
                            continue

                except httpx.TimeoutException:
                    print(f"请求超时，尝试 {attempt + 1}/{self.max_retries}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(random.uniform(5, 10))
                        continue

                except Exception as e:
                    print(f"请求异常: {str(e)}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(random.uniform(5, 10))
                        continue

        return {}

    async def search_notes_by_keyword(self, keyword: str, page: int = 1, page_size: int = 20) -> List[Dict]:
        """
        根据关键词搜索小红书笔记

        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量

        Returns:
            笔记列表
        """
        try:
            # 注意：实际的API端点可能需要通过抓包分析获得
            search_url = f"{self.api_base}/sns/web/v1/search/notes"

            params = {
                'keyword': keyword,
                'page': page,
                'page_size': page_size,
                'search_id': self._generate_search_id(),
                'sort': 'general'  # 综合排序
            }

            # 添加额外的搜索参数
            params.update({
                'note_type': '0',  # 0:全部, 1:视频, 2:图文
                'filters': ''
            })

            response = await self._make_request(search_url, params)

            if response and 'data' in response:
                notes = response['data'].get('items', [])
                return self._parse_search_results(notes)

        except Exception as e:
            print(f"搜索关键词 '{keyword}' 时出错: {str(e)}")

        return []

    def _generate_search_id(self) -> str:
        """生成搜索ID"""
        import uuid
        return str(uuid.uuid4()).replace('-', '')

    def _parse_search_results(self, raw_results: List) -> List[Dict]:
        """
        解析搜索结果

        Args:
            raw_results: 原始搜索结果

        Returns:
            解析后的笔记列表
        """
        parsed_notes = []

        for item in raw_results:
            try:
                if item.get('model_type') == 'note':
                    note_data = item.get('note_card', {})
                    if note_data:
                        parsed_note = self._parse_note_card(note_data)
                        if parsed_note:
                            parsed_notes.append(parsed_note)
            except Exception as e:
                print(f"解析笔记时出错: {str(e)}")
                continue

        return parsed_notes

    def _parse_note_card(self, note_card: dict) -> Optional[Dict]:
        """
        解析单个笔记卡片

        Args:
            note_card: 笔记卡片数据

        Returns:
            解析后的笔记数据
        """
        try:
            note_id = note_card.get('id', '')
            title = note_card.get('display_title', '')
            desc = note_card.get('desc', '')

            # 用户信息
            user_info = note_card.get('user', {})
            author = user_info.get('nickname', '') if user_info else ''

            # 互动数据
            interact_info = note_card.get('interact_info', {})
            likes = interact_info.get('liked_count', 0)
            collects = interact_info.get('collected_count', 0)
            comments = interact_info.get('comment_count', 0)
            shares = interact_info.get('share_count', 0)

            # 封面图片
            cover_info = note_card.get('cover', {})
            cover_url = cover_info.get('url_default', '') if cover_info else ''

            # 笔记URL
            note_url = f"{self.base_url}/explore/{note_id}" if note_id else ''

            # 视频信息
            video_url = None
            video_content = None

            # 检查是否是视频笔记
            video_info = note_card.get('video', {})
            if video_info:
                # 获取视频URL
                video_url = video_info.get('media', {}).get('stream', {}).get('h264', [{}])[0].get('master_url') if video_info.get('media') else None

                # 如果有视频URL，尝试提取视频内容
                if video_url:
                    print(f"发现视频，正在提取内容: {title}")
                    video_content = process_video_with_retry(video_url, title)
                    if video_content:
                        print(f"视频内容提取成功: {video_content[:100]}...")
                    else:
                        print("视频内容提取失败或视频超过30秒")

            return {
                'note_id': note_id,
                'title': title or desc[:50],  # 如果没有标题，使用描述前50字
                'content': desc,
                'author': author,
                'likes': likes,
                'collects': collects,
                'comments': comments,
                'shares': shares,
                'cover_url': cover_url,
                'url': note_url,
                'video_url': video_url,
                'video_content': video_content,
                'published_at': datetime.now().isoformat(),
                'crawled_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"解析笔记卡片时出错: {str(e)}")
            return None

    async def get_note_detail(self, note_id: str) -> Optional[Dict]:
        """
        获取笔记详情

        Args:
            note_id: 笔记ID

        Returns:
            笔记详情
        """
        try:
            detail_url = f"{self.api_base}/sns/web/v1/feed"

            params = {
                'source_note_id': note_id,
                'image_formats': 'jpg,webp,avif'
            }

            response = await self._make_request(detail_url, params)

            if response and 'data' in response:
                items = response['data'].get('items', [])
                if items and len(items) > 0:
                    note_data = items[0].get('note_card', {})
                    return self._parse_note_detail(note_data)

        except Exception as e:
            print(f"获取笔记详情 '{note_id}' 时出错: {str(e)}")

        return None

    def _parse_note_detail(self, note_data: dict) -> Optional[Dict]:
        """
        解析笔记详情

        Args:
            note_data: 笔记详情数据

        Returns:
            解析后的笔记详情
        """
        try:
            # 基础信息
            note_id = note_data.get('id', '')
            title = note_data.get('title', '')
            desc = note_data.get('desc', '')

            # 用户信息
            user_info = note_data.get('user', {})
            author = user_info.get('nickname', '') if user_info else ''

            # 互动数据
            interact_info = note_data.get('interact_info', {})
            likes = interact_info.get('liked_count', 0)
            collects = interact_info.get('collected_count', 0)
            comments = interact_info.get('comment_count', 0)
            shares = interact_info.get('share_count', 0)

            # 时间信息
            time_info = note_data.get('time', {})
            published_at = time_info.get('display_time', '') if time_info else ''

            # 图片列表
            image_list = note_data.get('image_list', [])
            images = [img.get('url_default', '') for img in image_list]

            return {
                'note_id': note_id,
                'title': title,
                'content': desc,
                'author': author,
                'likes': likes,
                'collects': collects,
                'comments': comments,
                'shares': shares,
                'images': images,
                'url': f"{self.base_url}/explore/{note_id}" if note_id else '',
                'published_at': published_at,
                'crawled_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"解析笔记详情时出错: {str(e)}")
            return None


# 创建全局爬虫实例
crawler = XHSCrawler()


async def crawl_by_keyword(keyword: str, max_pages: int = 3) -> List[Dict]:
    """
    根据关键词抓取小红书内容

    Args:
        keyword: 关键词
        max_pages: 最大抓取页数

    Returns:
        抓取的内容列表
    """
    all_notes = []

    for page in range(1, max_pages + 1):
        try:
            print(f"正在抓取关键词 '{keyword}' 的第 {page} 页...")

            notes = await crawler.search_notes_by_keyword(keyword, page=page)

            if notes:
                all_notes.extend(notes)
                print(f"第 {page} 页抓取到 {len(notes)} 条笔记")
            else:
                print(f"第 {page} 页没有抓取到内容")
                break

        except Exception as e:
            print(f"抓取第 {page} 页时出错: {str(e)}")
            continue

    return all_notes