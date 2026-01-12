#!/usr/bin/env python3
"""
测试OpenAI API连接和调用
"""
import sys
import os

# 添加项目路径
sys.path.append('/Users/lishizheng/Desktop/Code/xhs_marketing/backend')

from app.services.openai_service import openai_service

def test_api_connection():
    """测试API连接"""
    print("=== 测试OpenAI API连接 ===\n")

    # 检查配置
    print(f"✅ API Key: {'已配置' if openai_service.api_key else '未配置'}")
    print(f"✅ API Base: {openai_service.api_base}")
    print(f"✅ Model: {openai_service.model}")
    print(f"✅ Client: {'已初始化' if openai_service.client else '未初始化'}")

    if not openai_service.client:
        print("\n❌ 客户端未正确初始化，无法进行API测试")
        return False

    # 测试简单的API调用
    print("\n开始测试API调用...")

    try:
        # 准备测试数据
        test_posts = [
            {
                'title': '2024年最值得入手的平价化妆品推荐',
                'author': '美妆达人小美',
                'likes': 15420,
                'collects': 8930,
                'comments': 1240,
                'shares': 890,
                'content': '今天为大家分享几款超级好用的平价化妆品，性价比超高，学生党必备！',
                'url': 'https://www.xiaohongshu.com/explore/12345'
            },
            {
                'title': '平价好物分享！这些化妆品真的不输大牌',
                'author': '护肤达人小红',
                'likes': 12890,
                'collects': 7650,
                'comments': 980,
                'shares': 650,
                'content': '最近发现了好多宝藏平价化妆品，效果惊人，价格却很亲民！',
                'url': 'https://www.xiaohongshu.com/explore/12346'
            }
        ]

        print(f"📊 测试数据: {len(test_posts)} 条帖子")
        print("🔄 正在进行AI分析...")

        # 调用分析服务
        result = openai_service.analyze_trending_content(test_posts, "平价化妆品")

        if result.get('success'):
            print("🎉 API调用成功！")
            print(f"📈 分析的关键词: {result.get('keyword')}")
            print(f"📊 分析的帖子数量: {result.get('analyzed_count')}")
            print(f"🤖 使用的模型: {result.get('model_used')}")
            print(f"🕐 分析时间: {result.get('analysis_date')}")

            analysis = result.get('analysis', {})
            if 'trend_highlights' in analysis:
                print(f"\n🌟 发现的趋势亮点:")
                for i, trend in enumerate(analysis['trend_highlights'], 1):
                    print(f"   {i}. {trend}")

            return True
        else:
            print(f"❌ API调用失败: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)