import os
import time
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv
from typing import Optional

# 加载环境变量
load_dotenv()

# 初始化豆包客户端
client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=os.getenv('ARK_API_KEY'),
)


def get_video_duration(video_url: str) -> Optional[int]:
    """
    获取视频时长（秒）
    这里需要实现获取视频时长的逻辑
    可以使用视频处理库或者第三方API
    """
    # TODO: 实现视频时长获取
    # 目前暂时返回None，表示无法获取时长
    return None


def extract_video_content(video_url: str, title: str, max_duration: int = 30) -> Optional[str]:
    """
    使用豆包大模型提取视频内容

    Args:
        video_url: 视频URL
        title: 视频标题
        max_duration: 最大允许时长（秒），超过此时长的视频不处理

    Returns:
        提取的视频内容描述，如果失败或超过时长则返回None
    """
    try:
        # 检查视频时长
        duration = get_video_duration(video_url)
        if duration and duration > max_duration:
            print(f"视频时长 {duration}秒 超过限制 {max_duration}秒，跳过处理")
            return None

        # 使用豆包API处理视频
        response = client.responses.create(
            model="doubao-seed-1-8-251228",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_video",
                            "video_url": video_url,
                            "fps": 1
                        },
                        {
                            "type": "input_text",
                            "text": f"请详细描述这个视频的内容。视频标题是：{title}。请描述视频中展示的产品外观、材质、使用场景、设计特点等关键信息。"
                        }
                    ],
                }
            ]
        )

        # 等待响应完成
        if hasattr(response, 'status') and response.status != 'completed':
            max_wait = 60
            wait_time = 0
            while response.status != 'completed' and wait_time < max_wait:
                time.sleep(2)
                wait_time += 2
                if hasattr(response, 'status'):
                    break

        # 提取生成的文本内容
        if not response or not hasattr(response, 'output') or not response.output:
            return None

        # 遍历 output 列表，找到 type='message' 的项
        for output_item in response.output:
            if hasattr(output_item, 'type') and output_item.type == 'message':
                if hasattr(output_item, 'content') and output_item.content:
                    for content_item in output_item.content:
                        if hasattr(content_item, 'text') and content_item.text:
                            return content_item.text

        # 兼容处理：如果没找到 message 类型，尝试直接访问
        for output_item in response.output:
            if hasattr(output_item, 'content') and output_item.content:
                for content_item in output_item.content:
                    if hasattr(content_item, 'text') and content_item.text:
                        return content_item.text

        return None

    except Exception as e:
        print(f"处理视频 {video_url} 时出错: {str(e)}")
        return None


def process_video_with_retry(video_url: str, title: str, max_retries: int = 2) -> Optional[str]:
    """
    带重试机制的视频内容提取

    Args:
        video_url: 视频URL
        title: 视频标题
        max_retries: 最大重试次数

    Returns:
        提取的视频内容描述，失败返回None
    """
    for attempt in range(max_retries):
        try:
            content = extract_video_content(video_url, title)
            if content:
                return content

            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries - 1:
                time.sleep(3)

        except Exception as e:
            print(f"第 {attempt + 1} 次尝试失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(3)

    return None