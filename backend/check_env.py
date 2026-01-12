#!/usr/bin/env python3
"""
环境变量检查脚本
验证OpenAI API配置是否正确
"""
import os
import sys

def check_env_vars():
    """检查环境变量配置"""
    print("🔍 检查OpenAI API环境变量配置...")
    print("-" * 50)

    # 尝试加载.env文件
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ python-dotenv 已安装，.env文件已加载")
    except ImportError:
        print("⚠️  python-dotenv 未安装，使用系统环境变量")

    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    ai_model = os.getenv("AI_MODEL", "gpt-3.5-turbo")

    # 检查结果
    if api_key:
        print(f"✅ OPENAI_API_KEY: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ OPENAI_API_KEY: 未设置")
        print("   请在 .env 文件中设置: OPENAI_API_KEY=your-key-here")

    if api_base:
        print(f"✅ OPENAI_API_BASE: {api_base}")
    else:
        print("❌ OPENAI_API_BASE: 未设置")
        print("   请在 .env 文件中设置: OPENAI_API_BASE=https://api.openai.com/v1")

    print(f"✅ AI_MODEL: {ai_model}")

    # 验证配置
    if api_key and api_base:
        print("\n🎉 环境变量配置完整！")
        return True
    else:
        print("\n❌ 环境变量配置不完整，请检查上述配置")
        return False

def test_openai_connection():
    """测试OpenAI连接"""
    print("\n🔍 测试OpenAI API连接...")
    print("-" * 50)

    try:
        from openai import OpenAI
        import os

        # 确保加载了环境变量
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")

        if not api_key or not api_base:
            print("❌ 无法测试连接：环境变量配置不完整")
            return False

        # 创建客户端
        client = OpenAI(api_key=api_key, base_url=api_base)
        print("✅ OpenAI客户端创建成功")

        # 测试简单调用
        print("🧪 测试API调用...")
        response = client.chat.completions.create(
            model=os.getenv("AI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )

        if response.choices:
            print("✅ API调用成功")
            return True
        else:
            print("❌ API调用失败：未返回有效响应")
            return False

    except Exception as e:
        print(f"❌ API调用失败: {str(e)}")
        return False

def test_llm_service():
    """测试LLM服务"""
    print("\n🔍 测试LLM服务...")
    print("-" * 50)

    try:
        from app.services.llm_service import expand_keywords_with_llm
        print("✅ LLM服务导入成功")

        # 测试关键词扩展
        print("🧪 测试关键词扩展...")
        result = expand_keywords_with_llm("双肩包", count=2)
        print(f"✅ 关键词扩展成功: {result}")
        return True

    except Exception as e:
        print(f"❌ LLM服务测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 检查环境变量
    env_ok = check_env_vars()

    if env_ok:
        # 如果环境变量配置正确，测试连接
        connection_ok = test_openai_connection()

        if connection_ok:
            # 如果连接成功，测试LLM服务
            test_llm_service()

    print("\n" + "=" * 50)
    print("检查完成！")
    print("=" * 50)