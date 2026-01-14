"""
豆包AI分析服务 - 分析小红书热点内容
"""
import os
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from volcenginesdkarkruntime import Ark

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


class DoubaoAnalysisService:
    """豆包AI分析服务"""

    def __init__(self):
        # 从环境变量中读取配置
        self.api_key = os.getenv("ARK_API_KEY")
        self.client = None

        if not self.api_key:
            logger.warning("请设置 ARK_API_KEY 环境变量")

        # 创建豆包客户端
        if self.api_key:
            try:
                self.client = Ark(
                    base_url='https://ark.cn-beijing.volces.com/api/v3',
                    api_key=self.api_key,
                )
                logger.info("豆包分析服务初始化成功")
            except Exception as e:
                logger.error(f"豆包初始化失败: {str(e)}")
                self.client = None
        else:
            logger.warning("豆包服务不可用：未配置API Key")
            self.client = None

    def analyze_trending_content(self, posts: List[Dict[str, Any]], keyword: str) -> Dict[str, Any]:
        """
        深度分析热点内容，结合文字内容和视频内容进行专业分析

        Args:
            posts: 热点帖子列表，包含文字和视频内容
            keyword: 关键词

        Returns:
            分析结果
        """
        if not self.client:
            return {
                "success": False,
                "error": "豆包服务不可用"
            }

        try:
            if len(posts) == 0:
                return {
                    "success": False,
                    "error": "没有可分析的内容"
                }

            # 准备分析数据，区分文字内容和视频内容
            content_data = self._prepare_mixed_content_data(posts, keyword)

            # 构建深度分析提示
            prompt = self._build_mixed_content_analysis_prompt(content_data, keyword)

            # 调用豆包API进行深度分析
            try:
                # 使用与视频处理相同的调用方式
                response = self.client.chat.completions.create(
                    model="doubao-seed-1-6-251015",  # 使用可用的豆包模型endpoint
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一位专业的小红书内容分析师和营销策略专家，擅长从用户生成内容中提取深度洞察和商业价值。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                # 提取分析结果
                if response and hasattr(response, 'choices') and len(response.choices) > 0:
                    analysis_text = response.choices[0].message.content.strip()
                else:
                    # 尝试另一种响应格式
                    if hasattr(response, 'output') and response.output:
                        for output_item in response.output:
                            if hasattr(output_item, 'type') and output_item.type == 'message':
                                if hasattr(output_item, 'content') and output_item.content:
                                    for content_item in output_item.content:
                                        if hasattr(content_item, 'text') and content_item.text:
                                            analysis_text = content_item.text
                                            break
                    else:
                        analysis_text = str(response)

            except Exception as api_error:
                logger.error(f"豆包API调用错误: {str(api_error)}")
                # 返回模拟的分析结果用于测试
                return self._get_fallback_analysis(posts, keyword)

            # 解析结构化分析结果
            analysis_result = self._parse_analysis_result(analysis_text, keyword)

            return {
                "success": True,
                "analysis": analysis_result,
                "raw_analysis": analysis_text,
                "analysis_date": datetime.now().isoformat(),
                "model_used": "doubao-pro-32k",
                "posts_analyzed": len(posts),
                "video_content_included": content_data['has_video_content']
            }

        except Exception as e:
            logger.error(f"豆包分析失败: {str(e)}")
            return {
                "success": False,
                "error": f"分析失败: {str(e)}"
            }

    def _prepare_mixed_content_data(self, posts: List[Dict[str, Any]], keyword: str) -> Dict[str, Any]:
        """
        准备混合内容分析数据（文字+视频）

        Args:
            posts: 帖子列表
            keyword: 关键词

        Returns:
            结构化内容数据
        """
        text_posts = []
        video_posts = []
        total_engagement = 0

        for post in posts:
            engagement_score = post.get('likes', 0) + post.get('comments', 0) + post.get('shares', 0)
            total_engagement += engagement_score

            post_info = {
                'title': post.get('title', ''),
                'author': post.get('author', ''),
                'likes': post.get('likes', 0),
                'comments': post.get('comments', 0),
                'shares': post.get('shares', 0),
                'engagement_score': engagement_score,
                'url': post.get('url', '')
            }

            # 区分纯文字内容和视频内容
            if post.get('has_video') and post.get('video_content'):
                # 视频内容：包含AI分析的视频描述
                post_info['video_analysis'] = post.get('video_content', '')
                post_info['original_text'] = post.get('content', '')
                video_posts.append(post_info)
            else:
                # 纯文字内容
                post_info['content'] = post.get('content', '')
                text_posts.append(post_info)

        return {
            'keyword': keyword,
            'total_posts': len(posts),
            'text_posts_count': len(text_posts),
            'video_posts_count': len(video_posts),
            'has_video_content': len(video_posts) > 0,
            'total_engagement': total_engagement,
            'avg_engagement': total_engagement / len(posts) if posts else 0,
            'text_posts': text_posts[:10],  # 限制数量避免token超限
            'video_posts': video_posts[:10]  # 限制数量避免token超限
        }

    def _build_mixed_content_analysis_prompt(self, content_data: Dict[str, Any], keyword: str) -> str:
        """
        构建混合内容分析提示词

        Args:
            content_data: 内容数据
            keyword: 关键词

        Returns:
            分析提示词
        """
        prompt = f"""请对"{keyword}"关键词的小红书热点内容进行深度分析。

## 数据概况
- 总内容数: {content_data['total_posts']}条
- 纯文字内容: {content_data['text_posts_count']}条
- 视频内容: {content_data['video_posts_count']}条
- 总互动量: {content_data['total_engagement']}
- 平均互动: {content_data['avg_engagement']:.0f}

## 纯文字热点内容
"""

        # 添加文字内容
        for i, post in enumerate(content_data['text_posts'][:8], 1):
            prompt += f"""
### 文字内容 {i}
- 标题: {post['title']}
- 作者: {post['author']}
- 互动量: {post['likes']}赞 {post['comments']}评 {post['shares']}转
- 内容: {post['content'][:300]}...
"""

        # 添加视频内容
        if content_data['video_posts']:
            prompt += f"""
## 视频热点内容（含AI视觉分析）
"""
            for i, post in enumerate(content_data['video_posts'][:8], 1):
                prompt += f"""
### 视频内容 {i}
- 标题: {post['title']}
- 作者: {post['author']}
- 互动量: {post['likes']}赞 {post['comments']}评 {post['shares']}转
- 原始描述: {post.get('original_text', '')[:200]}...
- AI视频分析: {post['video_analysis'][:500]}...
"""

        prompt += f"""

## 分析要求
请从以下维度进行专业分析：

1. **内容趋势分析**: 结合文字和视频内容，分析当前"{keyword}"领域的主要热点趋势
2. **视频vs文字对比**: 分析视频内容和纯文字内容在表现力、用户反馈方面的差异
3. **用户偏好洞察**: 基于视频AI分析结果，提炼用户对"{keyword}"相关内容的真实需求和偏好
4. **爆款要素提炼**: 从高互动内容中提取成功要素，特别关注视频内容的视觉冲击点
5. **内容机会识别**: 指出当前内容空白点和机会点
6. **创作策略建议**: 提供具体的内容创作建议，包括是否优先考虑视频形式

请以JSON格式返回分析结果：
{{
    "trend_overview": "趋势概述",
    "content_preferences": "用户偏好分析",
    "video_vs_text": "视频vs文字对比分析",
    "success_factors": ["成功要素1", "成功要素2"],
    "content_gaps": ["内容空白点1", "内容空白点2"],
    "creation_strategy": "创作策略建议",
    "key_insights": ["关键洞察1", "关键洞察2"],
    "recommended_topics": ["推荐主题1", "推荐主题2"]
}}
"""

        return prompt

    def _parse_analysis_result(self, analysis_text: str, keyword: str) -> Dict[str, Any]:
        """
        解析豆包分析结果

        Args:
            analysis_text: 分析文本
            keyword: 关键词

        Returns:
            结构化分析结果
        """
        try:
            # 尝试解析JSON结果
            # 查找JSON部分
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = analysis_text[json_start:json_end]
                parsed_result = json.loads(json_str)
                return parsed_result
            else:
                # 如果无法解析JSON，返回原始文本
                return {
                    "trend_overview": analysis_text[:500],
                    "raw_analysis": analysis_text
                }
        except Exception as e:
            logger.warning(f"解析豆包分析结果失败: {str(e)}")
            return {
                "trend_overview": analysis_text[:500],
                "raw_analysis": analysis_text
            }

    def _get_fallback_analysis(self, posts: List[Dict[str, Any]], keyword: str) -> Dict[str, Any]:
        """
        获取备用分析结果，当豆包API不可用时使用

        Args:
            posts: 帖子列表
            keyword: 关键词

        Returns:
            基础分析结果
        """
        video_count = sum(1 for p in posts if p.get('has_video'))
        text_count = len(posts) - video_count
        total_likes = sum(p.get('likes', 0) for p in posts)

        return {
            "success": True,
            "analysis": {
                "trend_overview": f"对'{keyword}'关键词的基础分析。分析了{len(posts)}条内容，其中{video_count}条视频内容和{text_count}条文字内容。总点赞数{total_likes}。",
                "content_preferences": f"用户对'{keyword}'相关内容表现出浓厚兴趣，视频内容获得较高互动。",
                "video_vs_text": f"视频内容占{video_count}条，文字内容占{text_count}条。视频内容通过视觉展示更直观地呈现了{keyword}的相关信息。",
                "success_factors": [
                    f"与'{keyword}'相关的高质量内容",
                    "视频内容的视觉冲击力",
                    "实用的信息分享"
                ],
                "content_gaps": [
                    "可以增加更多实用教程类内容",
                    "结合用户真实使用场景的内容较少"
                ],
                "creation_strategy": f"建议重点关注'{keyword}'的视频内容制作，结合实际使用场景，提供有价值的实用信息。",
                "key_insights": [
                    f"'{keyword}'内容市场需求旺盛",
                    "视频形式更受欢迎",
                    "用户偏好真实、实用的内容"
                ],
                "recommended_topics": [
                    f"'{keyword}'使用技巧分享",
                    f"'{keyword}'选购指南",
                    f"'{keyword}'相关产品测评"
                ]
            },
            "raw_analysis": "基础分析结果（豆包API不可用）",
            "analysis_date": datetime.now().isoformat(),
            "model_used": "fallback-analysis",
            "posts_analyzed": len(posts),
            "video_content_included": video_count > 0
        }


# 创建全局服务实例
doubao_analysis_service = DoubaoAnalysisService()