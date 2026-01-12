"""
OpenAI GPT分析服务 - 分析小红书热点内容
"""
import os
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI库未安装，GPT分析功能将不可用")

logger = logging.getLogger(__name__)

class OpenAIAnalysisService:
    """OpenAI GPT分析服务"""

    def __init__(self):
        # 从环境变量中读取配置
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE")
        # 支持多种模型配置环境变量名称
        self.model = os.getenv("OPENAI_MODEL") or os.getenv("AI_MODEL", "gpt-4o-mini")
        self.client = None

        # 提供更详细的错误信息
        if not self.api_key:
            logger.warning(
                "请设置 OPENAI_API_KEY 环境变量\n"
                "可以通过以下方式设置:\n"
                "1. 在 backend/.env 文件中添加: OPENAI_API_KEY=your-key-here\n"
                "2. 或设置系统环境变量: export OPENAI_API_KEY=your-key-here"
            )
        if not self.api_base:
            logger.warning(
                "请设置 OPENAI_API_BASE 环境变量\n"
                "可以通过以下方式设置:\n"
                "1. 在 backend/.env 文件中添加: OPENAI_API_BASE=https://api.openai.com/v1\n"
                "2. 或设置系统环境变量: export OPENAI_API_BASE=https://api.openai.com/v1"
            )

        # 创建OpenAI客户端
        if OPENAI_AVAILABLE and self.api_key and self.api_base:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base
                )
                logger.info(f"OpenAI服务初始化成功，使用模型: {self.model}")
            except Exception as e:
                logger.error(f"OpenAI初始化失败: {str(e)}")
        else:
            logger.warning("OpenAI服务不可用：未配置API Key、API Base或未安装库")

    def analyze_trending_content(self, posts: List[Dict[str, Any]], keyword: str) -> Dict[str, Any]:
        """
        深度分析热点内容，按关键词领域进行专业分析

        Args:
            posts: 热点帖子列表
            keyword: 关键词

        Returns:
            分析结果
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI服务不可用"
            }

        try:
            if len(posts) == 0:
                return {
                    "success": False,
                    "error": "没有可分析的内容"
                }

            # 准备分析数据
            content_data = self._prepare_enhanced_content_data(posts, keyword)

            # 构建深度分析提示
            prompt = self._build_enhanced_analysis_prompt(content_data, keyword)

            # 调用配置的模型进行深度分析
            response = self.client.chat.completions.create(
                model=self.model,  # 使用环境变量配置的模型
                messages=[
                    {
                        "role": "system",
                        "content": """你是一位资深的社交媒体内容分析师和趋势专家，专精于：
1. 小红书平台内容生态深度分析
2. 用户行为和互动模式洞察
3. 跨领域趋势发现和机会识别
4. 商业变现策略和内容创作指导

你的分析风格：数据驱动、洞察深刻、建议实用、前瞻性强。"""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )

            analysis_text = response.choices[0].message.content

            # 解析分析结果
            analysis_result = self._parse_enhanced_analysis_result(analysis_text, keyword, posts)

            return {
                "success": True,
                "keyword": keyword,
                "analysis": analysis_result,
                "analyzed_count": len(posts),
                "analysis_date": datetime.now().isoformat(),
                "model_used": self.model
            }

        except Exception as e:
            logger.error(f"GPT分析失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _prepare_enhanced_content_data(self, posts: List[Dict[str, Any]], keyword: str) -> Dict[str, Any]:
        """准备增强的用于分析的内容数据"""
        # 按互动数排序，计算综合热度
        def calculate_engagement_score(post):
            return post.get('likes', 0) * 1.0 + post.get('collects', 0) * 1.5 + post.get('comments', 0) * 2.0

        sorted_posts = sorted(posts, key=calculate_engagement_score, reverse=True)[:15]

        # 计算统计数据
        total_likes = sum(p.get('likes', 0) for p in posts)
        total_comments = sum(p.get('comments', 0) for p in posts)
        avg_likes = total_likes // len(posts) if posts else 0
        avg_comments = total_comments // len(posts) if posts else 0

        content_data = {
            "keyword": keyword,
            "total_posts": len(posts),
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "top_posts": []
        }

        for post in sorted_posts:
            content_data["top_posts"].append({
                "title": post.get('title', ''),
                "author": post.get('author', ''),
                "likes": post.get('likes', 0),
                "collects": post.get('collects', 0),
                "comments": post.get('comments', 0),
                "shares": post.get('shares', 0),
                "content": post.get('content', '')[:300],  # 增加到300字符
                "engagement_score": calculate_engagement_score(post)
            })

        return content_data

    def _build_enhanced_analysis_prompt(self, content_data: Dict[str, Any], keyword: str) -> str:
        """构建增强的GPT分析提示"""
        prompt = f"""
# 🎯 小红书"{keyword}"领域深度分析任务

## 📊 数据概况
- **分析领域**: {keyword}
- **数据规模**: {content_data['total_posts']}条内容
- **平均互动**: 点赞{content_data['avg_likes']} | 评论{content_data['avg_comments']}
- **分析样本**: TOP{len(content_data['top_posts'])}高热度内容

## 🔥 热门内容数据
```json
{json.dumps(content_data['top_posts'], ensure_ascii=False, indent=2)}
```

## 🎪 深度分析要求

请以小红书内容专家的身份，从以下维度进行深度分析：

### 1. 🌟 内容趋势识别
- 当前{keyword}领域的3-5个核心热点话题
- 新兴趋势和爆发性话题（如有）
- 内容形式偏好（图文/视频/合集等）

### 2. 👥 用户画像与偏好
- 目标用户群体特征（年龄、性别、兴趣）
- 用户痛点和需求分析
- 高互动内容的共同特征

### 3. 💡 内容创作密码
- 标题和文案的成功模式
- 视觉呈现和风格偏好
- 发布时间和时机策略

### 4. 🚀 商业价值评估
- 潜在商业变现机会
- 品牌合作可能性
- 产品/服务推广切入点

### 5. 🎯 竞争格局分析
- 内容创作者竞争强度
- 差异化机会点
- 长期发展潜力

## 📋 输出格式
请严格按照以下JSON结构返回分析结果：
```json
{{
    "trend_highlights": [
        "核心热点1",
        "核心热点2",
        "核心热点3"
    ],
    "emerging_trends": [
        "新兴趋势1",
        "新兴趋势2"
    ],
    "user_persona": {{
        "target_audience": "目标用户描述",
        "pain_points": ["痛点1", "痛点2"],
        "engagement_drivers": ["驱动因素1", "驱动因素2"]
    }},
    "content_success_patterns": {{
        "title_patterns": ["标题模式1", "标题模式2"],
        "visual_preferences": ["视觉偏好1"],
        "posting_strategy": "发布策略建议"
    }},
    "commercial_opportunities": [
        {{
            "opportunity": "机会描述",
            "feasibility": "high/medium/low",
            "estimated_value": "预估价值"
        }}
    ],
    "competitive_insights": {{
        "competition_level": "high/medium/low",
        "differentiation_opportunities": ["差异化机会1"],
        "long_term_potential": "长期潜力评估"
    }},
    "actionable_recommendations": [
        "具体建议1",
        "具体建议2",
        "具体建议3"
    ],
    "strategic_summary": "总结性战略洞察"
}}
```

⚠️ 重要提醒：
- 基于实际数据进行分析，不要凭空臆造
- 发现真正的洞察，而非泛泛而谈
- 建议要具体可执行
- 考虑小红书平台特性和用户习惯
"""

        return prompt

    def _parse_enhanced_analysis_result(self, analysis_text: str, keyword: str, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """解析增强的GPT分析结果"""
        try:
            # 尝试提取JSON
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = analysis_text[json_start:json_end]
                result = json.loads(json_str)

                # 添加分析元数据
                result['keyword'] = keyword
                result['analysis_date'] = datetime.now().isoformat()
                result['data_sample_size'] = len(posts)

                # 添加数据质量评分
                if len(posts) >= 10:
                    result['data_quality'] = 'high'
                elif len(posts) >= 5:
                    result['data_quality'] = 'medium'
                else:
                    result['data_quality'] = 'low'

                return result
            else:
                # 如果无法提取JSON，返回原始文本
                return {
                    "raw_analysis": analysis_text,
                    "keyword": keyword,
                    "analysis_date": datetime.now().isoformat(),
                    "data_sample_size": len(posts),
                    "parsing_failed": True
                }
        except Exception as e:
            logger.error(f"解析分析结果失败: {str(e)}")
            return {
                "raw_analysis": analysis_text,
                "keyword": keyword,
                "analysis_date": datetime.now().isoformat(),
                "data_sample_size": len(posts),
                "parse_error": str(e),
                "parsing_failed": True
            }

    def generate_comprehensive_daily_report(self, all_analyses: List[Dict[str, Any]], report_date: str = None) -> str:
        """
        生成综合性每日热点分析报告，按关键词领域分别分析

        Args:
            all_analyses: 所有关键词的分析结果
            report_date: 报告日期，默认为今天

        Returns:
            详细报告文本
        """
        if not self.client:
            return "❌ OpenAI服务不可用，无法生成报告"

        try:
            if not all_analyses:
                return "❌ 没有分析数据，无法生成报告"

            # 过滤掉分析失败的结果
            valid_analyses = [a for a in all_analyses if a.get('success', False)]

            if not valid_analyses:
                return "❌ 所有分析都失败了，无法生成报告"

            # 构建报告提示
            prompt = self._build_comprehensive_report_prompt(valid_analyses, report_date)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一位顶级的社交媒体内容策略师和趋势报告专家。
你擅长：
1. 整合多领域数据形成全局洞察
2. 发现跨领域的共同趋势和差异
3. 提供战略性的商业建议
4. 撰写结构清晰、洞察深刻的报告

报告风格：专业、数据驱动、洞察深刻、建议具体。
格式要求：使用Markdown格式，层次清晰，重点突出。"""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=4000
            )

            report = response.choices[0].message.content

            return report

        except Exception as e:
            logger.error(f"生成报告失败: {str(e)}")
            return f"❌ 报告生成失败: {str(e)}"

    def _build_comprehensive_report_prompt(self, valid_analyses: List[Dict[str, Any]], report_date: str = None) -> str:
        """构建综合性报告生成提示"""
        if not report_date:
            report_date = datetime.now().strftime("%Y年%m月%d日")

        # 按关键词组织分析数据
        keywords_data = {}
        for analysis in valid_analyses:
            keyword = analysis.get('keyword', '未知领域')
            keywords_data[keyword] = analysis.get('analysis', {})

        prompt = f"""
# 📊 小红书热点趋势综合分析报告

## 📅 报告信息
- **报告日期**: {report_date}
- **分析领域数**: {len(valid_analyses)}个
- **分析领域**: {', '.join(keywords_data.keys())}

## 🎯 分析数据
```json
{json.dumps(keywords_data, ensure_ascii=False, indent=2)}
```

## 📋 报告撰写要求

请撰写一份专业的小红书热点趋势分析报告，包含以下部分：

### 1. 🎪 执行摘要
- 整体趋势概述（1-2段）
- 核心发现（3-5个关键洞察）
- 战略建议摘要

### 2. 🌍 分领域深度分析
对每个关键词领域进行详细分析：
- **{', '.join(keywords_data.keys())}**

每个领域包含：
- 领域热点和趋势
- 用户画像和偏好
- 商业机会评估
- 创作建议

### 3. 🔍 跨领域对比分析
- 不同领域的共同趋势
- 各领域的独特特征
- 差异化策略机会

### 4. 💡 综合战略建议
- 内容创作策略
- 商业变现路径
- 长期发展规划

### 5. 📈 数据洞察总结
- 数据质量评估
- 关键数据指标
- 后续跟踪建议

## 🎨 报告格式要求：
```markdown
# 🎯 小红书热点趋势综合分析报告
**📅 {report_date}**

## 1. 🎪 执行摘要
[整体趋势概述]

### 🔑 核心发现
1. [关键洞察1]
2. [关键洞察2]
...

## 2. 🌍 分领域深度分析

### 📊 领域一：[关键词1]
#### 🌟 趋势洞察
[具体分析]

#### 👥 用户特征
[用户画像]

#### 🚀 商业机会
[机会分析]

#### 💡 创作建议
[具体建议]

### 📊 领域二：[关键词2]
[同样结构...]

## 3. 🔍 跨领域对比分析
[跨领域分析]

## 4. 💡 综合战略建议
[战略建议]

## 5. 📈 数据洞察总结
[数据总结]

---
*本报告基于小红书平台真实数据，由GPT-4o-mini智能分析生成*
```

⚠️ 重要提醒：
- 保持专业性和洞察深度
- 确保每个领域都有独立完整的分析
- 突出跨领域的比较和综合洞察
- 建议要具体可操作
- 用数据和发现支撑观点
- 使用适当的emoji增强可读性
"""

        return prompt


# 全局实例
openai_service = OpenAIAnalysisService()


def test_openai_service():
    """测试OpenAI服务配置"""
    print("=== 测试OpenAI分析服务配置 ===\n")

    print(f"API Key: {'已配置' if openai_service.api_key else '未配置'}")
    print(f"API Base: {openai_service.api_base or '未配置'}")
    print(f"Model: {openai_service.model}")
    print(f"Client Status: {'已初始化' if openai_service.client else '未初始化'}")

    if openai_service.client:
        print("\n✅ OpenAI服务配置正确！")
        print(f"将使用模型: {openai_service.model}")
        print(f"API地址: {openai_service.api_base}")
    else:
        print("\n❌ OpenAI服务配置有问题，请检查环境变量")


if __name__ == "__main__":
    test_openai_service()