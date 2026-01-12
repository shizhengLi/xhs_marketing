"""
测试定时调度器功能
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_scheduler_api():
    """测试调度器API"""
    print("=== 测试定时调度器功能 ===\n")

    # 1. 启动调度器
    print("1. 启动调度器...")
    response = requests.post(f"{API_BASE}/api/v1/scheduler/start")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")

    # 2. 设置定时任务
    print("\n2. 设置定时任务 (每天8:00)...")
    schedule_data = {
        "hour": 8,
        "minute": 0,
        "keyword_id": None,  # 所有关键词
        "schedule_type": "daily"
    }
    # 使用JSON dumps正确处理None值
    json_data = json.dumps(schedule_data)
    response = requests.post(f"{API_BASE}/api/v1/scheduler/setup",
                           data=json_data,
                           headers={"Content-Type": "application/json"})
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")

    # 3. 查看调度器状态
    print("\n3. 查看调度器状态...")
    response = requests.get(f"{API_BASE}/api/v1/scheduler/status")
    print(f"   状态码: {response.status_code}")
    status_data = response.json()
    print(f"   是否运行: {status_data['is_running']}")
    print(f"   当前时间: {status_data['current_time']}")
    print(f"   任务数量: {len(status_data['jobs'])}")

    for job in status_data['jobs']:
        print(f"   - 任务: {job['name']}")
        print(f"     下次运行: {job['next_run_time']}")

    # 4. 测试爬取功能
    print("\n4. 测试爬取功能...")
    test_data = {
        "hour": 0,
        "minute": 1,  # 设置为1分钟后测试
        "keyword_id": 1,  # 假设有关键词ID为1
        "schedule_type": "daily"
    }

    response = requests.post(f"{API_BASE}/api/v1/scheduler/setup", json=test_data)
    print(f"   设置测试任务: {response.json()}")

    print("\n5. 等待1分钟后观察任务执行...")
    time.sleep(60)

    # 再次查看状态
    response = requests.get(f"{API_BASE}/api/v1/scheduler/status")
    status_data = response.json()
    print(f"   任务数量: {len(status_data['jobs'])}")

    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_scheduler_api()