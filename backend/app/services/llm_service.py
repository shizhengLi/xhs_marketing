"""
LLM服务 - 使用GPT-5.1模型进行关键词扩展
"""
import os
from typing import List
from openai import OpenAI

# 加载.env文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 从环境变量中读取配置
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

# 提供更详细的错误信息
if not api_key:
    raise ValueError(
        "请设置 OPENAI_API_KEY 环境变量\n"
        "可以通过以下方式设置:\n"
        "1. 在 backend/.env 文件中添加: OPENAI_API_KEY=your-key-here\n"
        "2. 或设置系统环境变量: export OPENAI_API_KEY=your-key-here"
    )
if not api_base:
    raise ValueError(
        "请设置 OPENAI_API_BASE 环境变量\n"
        "可以通过以下方式设置:\n"
        "1. 在 backend/.env 文件中添加: OPENAI_API_BASE=https://api.openai.com/v1\n"
        "2. 或设置系统环境变量: export OPENAI_API_BASE=https://api.openai.com/v1"
    )

# 创建OpenAI客户端
client = OpenAI(
    api_key=api_key,
    base_url=api_base
)


def expand_keywords_with_llm(base_keyword: str, count: int = 3) -> List[str]:
    """
    使用LLM扩展关键词

    Args:
        base_keyword: 基础关键词
        count: 需要生成的相关关键词数量，默认2-3个

    Returns:
        相关关键词列表
    """
    try:
        print(f"正在使用LLM扩展关键词: {base_keyword}")

        # 构建提示词
        prompt = f"""
请为关键词"{base_keyword}"生成{count}个相关的、相似的或者扩展的关键词。

要求：
1. 生成的关键词应该与原关键词在语义上相关
2. 关键词应该适合用于小红书内容搜索
3. 关键词长度最好在2-6个字之间
4. 只返回关键词列表，不要其他解释

请直接返回{count}个关键词，用逗号分隔。
"""

        # 调用GPT-5.1模型
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的小红书关键词分析专家，擅长生成相关的搜索关键词。请根据用户的需求生成准确、有价值的相关关键词。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,  # 稍高的温度以获得更多样化的关键词
            max_tokens=500
        )

        # 解析响应
        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content.strip()
            print(f"LLM原始响应: {content}")

            # 处理返回的关键词
            # 支持多种分隔符：逗号、换行、顿号等
            keywords = []
            for separator in [',', '\n', '、', '，', ';', '；']:
                if separator in content:
                    keywords = [kw.strip() for kw in content.split(separator) if kw.strip()]
                    break

            # 如果没有找到分隔符，尝试按行分割
            if not keywords:
                keywords = [line.strip() for line in content.split('\n') if line.strip()]

            # 清理关键词，移除序号等
            cleaned_keywords = []
            for kw in keywords:
                # 移除数字序号
                kw = kw.lstrip('0123456789.-*•· ')
                # 移除引号
                kw = kw.strip('"\'""''')
                if kw and len(kw) >= 2:  # 至少2个字符
                    cleaned_keywords.append(kw)

            # 限制数量
            result_keywords = cleaned_keywords[:count]

            print(f"解析得到的关键词: {result_keywords}")
            return result_keywords
        else:
            print("⚠️ LLM返回空响应，使用备选方案")
            return get_fallback_keywords(base_keyword, count)

    except Exception as e:
        print(f"❌ LLM调用失败: {str(e)}")
        return get_fallback_keywords(base_keyword, count)


def get_fallback_keywords(base_keyword: str, count: int = 3) -> List[str]:
    """
    备选关键词生成方案

    Args:
        base_keyword: 基础关键词
        count: 需要生成的关键词数量

    Returns:
        相关关键词列表
    """
    # 简单的备选关键词生成规则
    fallback_patterns = [
        f"{base_keyword}推荐",
        f"{base_keyword}测评",
        f"{base_keyword}心得",
        f"好用的{base_keyword}",
        f"{base_keyword}种草",
        f"{base_keyword}攻略"
    ]

    return fallback_patterns[:count]


def test_llm_service():
    """测试LLM服务"""
    test_keywords = ["美妆", "运动鞋", "护肤"]

    print("=== 测试LLM关键词扩展服务 ===\n")

    for keyword in test_keywords:
        print(f"测试关键词: {keyword}")
        expanded = expand_keywords_with_llm(keyword, 3)
        print(f"扩展结果: {expanded}")
        print("-" * 50)


if __name__ == "__main__":
    test_llm_service()