"""
测试AI关键词扩展功能
"""
import requests
import json

# 配置
API_BASE = "http://localhost:8000"
USERNAME = "test_user"
PASSWORD = "test_password"

def login_and_get_token():
    """登录并获取token"""
    login_url = f"{API_BASE}/api/v1/auth/login"
    params = {
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
        response = requests.post(login_url, params=params)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ 登录成功")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return None

def test_ai_expand_keywords(token, keyword, count=3):
    """测试AI关键词扩展"""
    url = f"{API_BASE}/api/v1/keywords/ai-expand"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "base_keyword": keyword,
        "count": count
    }

    try:
        print(f"\n🔄 正在测试关键词: {keyword}")
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI扩展成功:")
            print(f"   原始关键词: {result['original']}")
            print(f"   推荐关键词: {result['suggested_keywords']}")
            return result['suggested_keywords']
        else:
            print(f"❌ AI扩展失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ AI扩展异常: {str(e)}")
        return None

def main():
    """主测试函数"""
    print("=== 测试AI关键词扩展功能 ===\n")

    # 登录
    token = login_and_get_token()
    if not token:
        print("无法获取token，退出测试")
        return

    # 测试多个关键词
    test_keywords = [
        ("美妆", 3),
        ("运动鞋", 3),
        ("护肤", 2),
        ("数码产品", 3)
    ]

    print("\n" + "="*50)
    print("开始测试AI关键词扩展...")
    print("="*50)

    results = {}
    for keyword, count in test_keywords:
        suggested = test_ai_expand_keywords(token, keyword, count)
        if suggested:
            results[keyword] = suggested

    # 输出总结
    print("\n" + "="*50)
    print("测试总结:")
    print("="*50)
    for keyword, suggested in results.items():
        print(f"{keyword} → {', '.join(suggested)}")

    print(f"\n✅ 成功测试了 {len(results)} 个关键词的AI扩展")

if __name__ == "__main__":
    main()