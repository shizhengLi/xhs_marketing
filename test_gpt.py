"""
验证 OpenAI 模型能否正常输出
"""
import os
from openai import OpenAI

# 尝试从 .env 文件加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("提示: 安装 python-dotenv 可以自动从 .env 文件加载配置: pip install python-dotenv")

# 从环境变量中读取配置
api_key = os.getenv("OPENAI_API_KEY") 
api_base = os.getenv("OPENAI_API_BASE")

if not api_key:
    raise ValueError("请设置 OPENAI_API_KEY 或 API_KEY 环境变量")
if not api_base:
    raise ValueError("请设置 OPENAI_API_BASE 或 API_BASE 环境变量")

# 创建OpenAI客户端
client = OpenAI(
    api_key=api_key,
    base_url=api_base
)


def test_openai_model():
    """
    验证 OpenAI 模型能否正常输出一句话
    """
    try:
        print("正在测试 OpenAI 模型...")
        
        # 调用模型，只生成一句话
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {
                    "role": "user",
                    "content": "请说一句话。"
                }
            ],
            max_tokens=50
        )

        if response.choices and response.choices[0].message.content:
            output = response.choices[0].message.content
            print(f"✅ 模型输出成功: {output}")
            return True
        else:
            print("❌ 模型未返回有效内容")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    test_openai_model()