"""
测试登录
"""
import requests

API_BASE = "http://localhost:8000"

def test_login():
    """测试登录"""
    url = f"{API_BASE}/api/v1/auth/login"
    params = {
        "username": "test_user",
        "password": "test_password"
    }

    try:
        response = requests.post(url, params=params)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 登录成功")
            print(f"Token: {data.get('access_token')}")
            return data.get('access_token')
        else:
            print(f"❌ 登录失败")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return None

if __name__ == "__main__":
    test_login()