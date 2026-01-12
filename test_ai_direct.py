"""
直接测试AI扩展API（不需要认证）
"""
import requests

API_BASE = "http://localhost:8000"

def test_ai_expand_direct():
    """直接测试AI扩展API"""
    url = f"{API_BASE}/api/v1/keywords/ai-expand"
    data = {
        "base_keyword": "美妆",
        "count": 3
    }

    try:
        print(f"🔄 正在测试AI关键词扩展...")
        print(f"关键词: {data['base_keyword']}")
        print(f"数量: {data['count']}")

        response = requests.post(url, json=data)
        print(f"\n状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ AI扩展成功:")
            print(f"   原始关键词: {result['original']}")
            print(f"   推荐关键词: {result['suggested_keywords']}")
            return result['suggested_keywords']
        else:
            print(f"\n❌ AI扩展失败")
            return None
    except Exception as e:
        print(f"❌ AI扩展异常: {str(e)}")
        return None

def test_multiple_keywords():
    """测试多个关键词"""
    test_cases = [
        ("美妆", 3),
        ("运动鞋", 3),
        ("护肤", 2),
        ("数码产品", 3)
    ]

    print("=== 测试AI关键词扩展功能 ===\n")

    results = {}
    for keyword, count in test_cases:
        print(f"\n{'='*40}")
        url = f"{API_BASE}/api/v1/keywords/ai-expand"
        data = {
            "base_keyword": keyword,
            "count": count
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                suggested = result['suggested_keywords']
                results[keyword] = suggested
                print(f"✅ {keyword} → {', '.join(suggested)}")
            else:
                print(f"❌ {keyword} 扩展失败: {response.status_code}")
        except Exception as e:
            print(f"❌ {keyword} 扩展异常: {str(e)}")

    # 输出总结
    print(f"\n{'='*40}")
    print(f"测试总结:")
    print(f"{'='*40}")
    for keyword, suggested in results.items():
        print(f"{keyword} → {', '.join(suggested)}")

    print(f"\n✅ 成功测试了 {len(results)} 个关键词的AI扩展")

if __name__ == "__main__":
    test_multiple_keywords()