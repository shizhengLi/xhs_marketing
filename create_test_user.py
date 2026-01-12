"""
创建测试用户
"""
import requests

API_BASE = "http://localhost:8000"

def create_user():
    """创建测试用户"""
    url = f"{API_BASE}/api/v1/auth/register"
    data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password"
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print("✅ 用户创建成功")
            return True
        else:
            print(f"❌ 用户创建失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 用户创建异常: {str(e)}")
        return False

if __name__ == "__main__":
    create_user()