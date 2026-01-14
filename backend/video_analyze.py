import os
from volcenginesdkarkruntime import Ark

import os
from openai import OpenAI

# 加载.env文件
try:
    from dotenv import load_dotenv
    # 指定.env文件路径（相对于当前文件）
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path)
except ImportError:
    pass

# 从环境变量中获取您的API KEY，配置方法见：https://www.volcengine.com/docs/82379/1399008
api_key = os.getenv('ARK_API_KEY')

if not api_key:
    print("❌ 错误: 未找到 ARK_API_KEY 环境变量")
    print("   请确保在 backend/.env 文件中设置了 ARK_API_KEY")
    exit(1)

client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=os.getenv('ARK_API_KEY'),
)

# response = client.responses.create(
#     model="doubao-seed-1-8-251228",
#     input=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "input_image",
#                     "image_url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/ark_demo_img_1.png"
#                 },
#                 {
#                     "type": "input_text",
#                     "text": "支持输入图片的模型系列是哪个？"
#                 },
#             ],
#         }
#     ]
# )

# print(response)

# response = client.responses.create(
#     model="doubao-seed-1-6-251015",
#     input=[
#         {
#             "role": "user",
#             "content": [
#                 {    
#                     "type": "input_video",
#                     "video_url": "https://ark-project.tos-cn-beijing.volces.com/doc_video/ark_vlm_video_input.mp4",
#                     "fps":1
#                 }
#             ],
#         }
#     ]
# )

# print(response)


response = client.responses.create(
    model="doubao-seed-1-8-251228",
    input=[
        {
            "role": "user",
            "content": [
                {    
                    "type": "input_video",
                    "video_url": "http://sns-video-hs.xhscdn.com/stream/79/110/259/01e95b8c3821fd74010370039b8d9c1254_259.mp4",
                    # 
                    # http://sns-video-hs.xhscdn.com/stream/79/110/259/01e7d95fb60d726a0103700395a927012e_259.mp4
                    "fps":1
                }
            ],
        }
    ]
)

print(response)