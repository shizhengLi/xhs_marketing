import sys
import os
import json
from datetime import datetime

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.post import Post
from app.models.keyword import Keyword

def parse_like_count(liked_count_str):
    """解析点赞数字符串，转换为数字"""
    if isinstance(liked_count_str, int):
        return liked_count_str

    if not liked_count_str or not isinstance(liked_count_str, str):
        return 0

    liked_count_str = liked_count_str.strip()

    if '万' in liked_count_str:
        # 处理"2.5万"这种情况
        number_part = liked_count_str.replace('万', '').strip()
        try:
            return int(float(number_part) * 10000)
        except ValueError:
            return 0
    else:
        # 直接是数字字符串
        try:
            return int(liked_count_str.replace(',', ''))
        except ValueError:
            return 0

def import_video_data():
    """导入视频数据到数据库"""

    # 读取JSON文件
    json_file = "/Users/lishizheng/Desktop/Code/xhs_marketing/MediaCrawler/data/xhs/video_desk_content.json"

    print(f"正在读取文件: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        video_data = json.load(f)

    print(f"文件包含 {len(video_data)} 条视频数据")

    # 创建数据库会话
    db = SessionLocal()

    try:
        # 查找或创建"桌子"关键词
        keyword = db.query(Keyword).filter(Keyword.keyword == "桌子").first()
        if not keyword:
            print("创建'桌子'关键词...")
            keyword = Keyword(keyword="桌子")
            db.add(keyword)
            db.commit()
            db.refresh(keyword)
            print(f"创建关键词成功，ID: {keyword.id}")
        else:
            print(f"找到关键词'桌子'，ID: {keyword.id}")

        # 导入视频数据
        imported_count = 0
        updated_count = 0
        skipped_count = 0

        for item in video_data:
            try:
                # 检查是否已存在（根据note_id）
                existing_post = db.query(Post).filter(
                    Post.url == item.get('note_url')
                ).first()

                # 准备数据
                post_data = {
                    'keyword_id': keyword.id,
                    'title': item.get('title', ''),
                    'content': item.get('ai_generated_content', ''),
                    'author': item.get('author', ''),
                    'likes': parse_like_count(item.get('liked_count', 0)),
                    'collects': 0,  # JSON中没有这个字段
                    'comments': 0,  # JSON中没有这个字段
                    'shares': 0,    # JSON中没有这个字段
                    'url': item.get('note_url', ''),
                    'video_url': item.get('video_url', ''),  # 确保视频URL存入
                    'video_content': item.get('ai_generated_content', ''),  # AI分析内容
                    'published_at': datetime.now(),  # JSON中没有具体发布时间
                }

                if existing_post:
                    # 更新现有记录
                    updated = False
                    for key, value in post_data.items():
                        if key != 'keyword_id' and hasattr(existing_post, key):
                            setattr(existing_post, key, value)
                            updated = True

                    if updated:
                        updated_count += 1
                        print(f"✓ 更新: {item.get('title', '')[:50]}")
                    else:
                        skipped_count += 1

                else:
                    # 创建新记录
                    new_post = Post(**post_data)
                    db.add(new_post)
                    imported_count += 1
                    print(f"✓ 导入: {item.get('title', '')[:50]}")

            except Exception as e:
                print(f"✗ 导入失败: {item.get('title', 'Unknown')} - 错误: {str(e)}")
                continue

        # 提交更改
        db.commit()

        print(f"\n导入完成！")
        print(f"- 新导入: {imported_count} 条")
        print(f"- 更新: {updated_count} 条")
        print(f"- 跳过: {skipped_count} 条")
        print(f"- 关键词ID: {keyword.id}")

        # 验证数据
        print("\n验证数据...")
        video_posts = db.query(Post).filter(
            Post.keyword_id == keyword.id,
            Post.video_url != None,
            Post.video_url != ''
        ).all()

        print(f"数据库中'桌子'关键词的视频帖子数量: {len(video_posts)}")
        if video_posts:
            print("示例数据:")
            for post in video_posts[:3]:
                print(f"  - 标题: {post.title}")
                print(f"    视频URL: {post.video_url[:80]}...")
                print(f"    AI内容: {post.video_content[:100] if post.video_content else 'None'}...")
                print()

    except Exception as e:
        print(f"导入过程中出错: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import_video_data()