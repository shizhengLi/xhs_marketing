import os
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv

# 加载环境变量
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# 初始化豆包客户端
client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=os.getenv('ARK_API_KEY'),
)

# 测试视频URL
video_url = "http://sns-video-hs.xhscdn.com/stream/1/110/259/01e95ce6da070f66010370039b92e65e08_259.mp4"

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
                    "text": "请详细描述这个视频的内容。"
                }
            ],
        }
    ]
)

print("=" * 80)
print("响应对象类型:", type(response))
print("=" * 80)
print("\n响应对象属性:")
for attr in dir(response):
    if not attr.startswith('_'):
        try:
            value = getattr(response, attr)
            if not callable(value):
                print(f"  {attr}: {type(value).__name__} = {value}")
        except:
            pass

print("\n" + "=" * 80)
print("response.output 结构:")
print("=" * 80)
if hasattr(response, 'output') and response.output:
    print(f"output 类型: {type(response.output)}")
    print(f"output 长度: {len(response.output)}")
    
    for i, item in enumerate(response.output):
        print(f"\noutput[{i}] 类型: {type(item)}")
        print(f"output[{i}] 属性:")
        for attr in dir(item):
            if not attr.startswith('_'):
                try:
                    value = getattr(item, attr)
                    if not callable(value):
                        print(f"    {attr}: {type(value).__name__} = {value}")
                except:
                    pass
        
        if hasattr(item, 'content') and item.content:
            print(f"\n  content 类型: {type(item.content)}")
            print(f"  content 长度: {len(item.content)}")
            for j, content_item in enumerate(item.content):
                print(f"\n  content[{j}] 类型: {type(content_item)}")
                print(f"  content[{j}] 属性:")
                for attr in dir(content_item):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(content_item, attr)
                            if not callable(value):
                                print(f"      {attr}: {type(value).__name__} = {value}")
                        except:
                            pass
else:
    print("response.output 为空或不存在")

print("\n" + "=" * 80)
print("尝试提取文本:")
print("=" * 80)
try:
    if response.output and len(response.output) > 0:
        output_msg = response.output[0]
        if hasattr(output_msg, 'content') and output_msg.content:
            for content in output_msg.content:
                if hasattr(content, 'text'):
                    print(f"找到文本: {content.text[:200]}...")
                    break
except Exception as e:
    print(f"提取失败: {e}")
