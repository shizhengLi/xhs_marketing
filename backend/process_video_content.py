import os
import json
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv
import time

# 加载环境变量
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# 初始化豆包客户端
client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=os.getenv('ARK_API_KEY'),
)

def generate_video_description(video_url, title):
    """
    使用豆包大模型为视频生成描述内容
    """
    try:
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
                            "text": f"请详细描述这个视频的内容。视频标题是：{title}。视频时长是：{duration}秒。"
                        }
                    ],
                }
            ]
        )
        
        # 检查响应状态，如果需要等待完成
        if hasattr(response, 'status') and response.status != 'completed':
            # 等待响应完成（如果需要）
            max_wait = 60  # 最多等待60秒
            wait_time = 0
            while response.status != 'completed' and wait_time < max_wait:
                time.sleep(2)
                wait_time += 2
                # 这里可能需要重新获取响应，但先尝试直接检查
                if hasattr(response, 'status'):
                    break

        # 提取生成的文本内容
        # 根据调试输出，响应结构是：
        # response.output 是一个列表，可能包含：
        #   - ResponseReasoningItem (type='reasoning') - 推理过程
        #   - ResponseOutputMessage (type='message') - 实际消息内容
        # 需要找到 type='message' 的项，然后访问其 content[0].text
        
        if not response or not hasattr(response, 'output') or not response.output:
            return "无法生成视频描述"
        
        # 遍历 output 列表，找到 type='message' 的项
        for output_item in response.output:
            # 检查是否是消息类型（ResponseOutputMessage）
            if hasattr(output_item, 'type') and output_item.type == 'message':
                # 提取消息内容
                if hasattr(output_item, 'content') and output_item.content:
                    for content_item in output_item.content:
                        # 检查是否是文本类型
                        if hasattr(content_item, 'text') and content_item.text:
                            return content_item.text
        
        # 如果没找到 message 类型，尝试直接访问所有有 content 的项（兼容处理）
        for output_item in response.output:
            if hasattr(output_item, 'content') and output_item.content:
                for content_item in output_item.content:
                    if hasattr(content_item, 'text') and content_item.text:
                        return content_item.text
        
        return "无法生成视频描述"

    except Exception as e:
        print(f"处理视频 {video_url} 时出错: {str(e)}")
        return f"生成失败: {str(e)}"

def process_videos():
    """
    处理视频数据：过滤、生成描述、保存
    """
    # 读取原始数据
    input_file = "/Users/lishizheng/Desktop/Code/xhs_marketing/MediaCrawler/data/xhs/video_links_extracted_short_videos.json"
    output_file = "/Users/lishizheng/Desktop/Code/xhs_marketing/MediaCrawler/data/xhs/video_desk_content.json"

    print(f"正在读取数据文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        all_videos = json.load(f)

    print(f"总共有 {len(all_videos)} 个视频")

    # 过滤出source_keyword为"桌子"的视频
    desk_videos = [video for video in all_videos if video.get('source_keyword') == '桌子']
    print(f"找到 {len(desk_videos)} 个与'桌子'相关的视频")

    # 为每个视频生成描述内容
    processed_videos = []
    for i, video in enumerate(desk_videos):
        print(f"\n正在处理第 {i+1}/{len(desk_videos)} 个视频...")
        print(f"视频标题: {video['title']}")
        print(f"视频URL: {video['video_url']}")

        # 生成视频描述
        description = generate_video_description(video['video_url'], video['title'])

        # 在原有数据基础上添加新字段
        video_with_description = video.copy()
        video_with_description['ai_generated_content'] = description

        processed_videos.append(video_with_description)

        print(f"生成的描述: {description[:100]}...")

        # 添加延迟避免API调用过快
        if i < len(desk_videos) - 1:
            time.sleep(2)

    # 保存处理后的数据
    print(f"\n正在保存处理后的数据到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_videos, f, ensure_ascii=False, indent=2)

    print(f"完成！已保存 {len(processed_videos)} 个视频的数据")
    return processed_videos

if __name__ == "__main__":
    process_videos()