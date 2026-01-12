#!/usr/bin/env python3
"""
重置数据库并导入JSON数据
"""
import sys
import os
import json
from datetime import datetime

# 添加项目路径到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models.post import Post
from app.models.keyword import Keyword

def clean_database():
    """清空数据库中的所有帖子数据"""
    print("🗑️  正在清空数据库...")
    db = SessionLocal()
    try:
        # 删除所有帖子
        deleted_count = db.query(Post).delete()
        db.commit()
        print(f"✅ 已删除 {deleted_count} 条帖子数据")
        return True
    except Exception as e:
        print(f"❌ 清空数据库失败: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def parse_count_string(count_str):
    """将小红书的数量字符串转换为数字"""
    if not count_str:
        return 0

    if isinstance(count_str, int):
        return count_str

    count_str = str(count_str).strip()

    # 处理 "10万+" 这样的格式
    if '万' in count_str:
        number_part = count_str.replace('万', '').replace('+', '').strip()
        try:
            return int(float(number_part) * 10000)
        except ValueError:
            return 0

    # 处理纯数字
    try:
        return int(count_str)
    except ValueError:
        return 0

def import_json_data(json_file_path):
    """导入JSON数据到数据库"""
    print(f"📖 正在读取JSON文件: {json_file_path}")

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"✅ JSON文件包含 {len(data)} 条数据")

        db = SessionLocal()
        try:
            imported_count = 0
            skipped_count = 0
            error_count = 0

            for item in data:
                try:
                    # 获取关键词
                    source_keyword = item.get('source_keyword', '未知关键词')

                    # 查找或创建关键词
                    keyword = db.query(Keyword).filter(Keyword.keyword == source_keyword).first()
                    if not keyword:
                        # 如果关键词不存在，需要先创建一个默认用户，然后创建关键词
                        from app.models.user import User
                        default_user = db.query(User).first()
                        if not default_user:
                            # 如果没有用户，创建一个默认用户
                            default_user = User(
                                username="admin",
                                email="admin@example.com",
                                hashed_password="placeholder"  # 实际使用中需要正确的密码哈希
                            )
                            db.add(default_user)
                            db.flush()
                            print(f"➕ 创建默认用户: {default_user.username}")

                        # 创建关键词
                        keyword = Keyword(
                            user_id=default_user.id,
                            keyword=source_keyword,
                            group_name="自动导入",
                            is_active=True
                        )
                        db.add(keyword)
                        db.flush()  # 获取ID
                        print(f"➕ 创建新关键词: {source_keyword}")

                    # 检查是否已存在（根据note_url）
                    note_url = item.get('note_url', '')
                    existing_post = db.query(Post).filter(Post.url == note_url).first()

                    if existing_post:
                        skipped_count += 1
                        continue

                    # 解析数量字段
                    likes = parse_count_string(item.get('liked_count', '0'))
                    collects = parse_count_string(item.get('collected_count', '0'))
                    comments = parse_count_string(item.get('comment_count', '0'))
                    shares = parse_count_string(item.get('share_count', '0'))

                    # 创建新帖子
                    new_post = Post(
                        keyword_id=keyword.id,
                        title=item.get('title', ''),
                        content=item.get('desc', ''),
                        author=item.get('nickname', ''),
                        likes=likes,
                        collects=collects,
                        comments=comments,
                        shares=shares,
                        url=note_url,
                        published_at=datetime.now(),
                        crawled_at=datetime.now()
                    )

                    db.add(new_post)
                    imported_count += 1

                except Exception as e:
                    print(f"⚠️  导入单条数据时出错: {str(e)}")
                    error_count += 1
                    continue

            db.commit()

            print(f"\n📊 导入完成:")
            print(f"   ✅ 成功导入: {imported_count} 条")
            print(f"   ⏭️  跳过重复: {skipped_count} 条")
            print(f"   ❌ 导入失败: {error_count} 条")

            return True

        except Exception as e:
            print(f"❌ 导入数据失败: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()

    except Exception as e:
        print(f"❌ 读取JSON文件失败: {str(e)}")
        return False

def verify_data():
    """验证导入的数据"""
    print("\n🔍 正在验证导入的数据...")
    db = SessionLocal()
    try:
        total_posts = db.query(Post).count()
        print(f"📈 数据库中总共有 {total_posts} 条帖子")

        # 按关键词统计
        from sqlalchemy import func
        stats = db.query(
            Keyword.keyword,
            func.count(Post.id).label('post_count'),
            func.sum(Post.likes).label('total_likes')
        ).join(Post, Keyword.id == Post.keyword_id).group_by(Keyword.keyword).all()

        print("\n📊 按关键词统计:")
        for keyword, count, likes in stats:
            print(f"   🏷️  {keyword}: {count} 条帖子, 总点赞 {likes or 0}")

        # 显示最新的几条数据
        latest = db.query(Post).order_by(Post.crawled_at.desc()).limit(3).all()
        print(f"\n📝 最新导入的3条数据:")
        for i, post in enumerate(latest, 1):
            keyword = db.query(Keyword).filter(Keyword.id == post.keyword_id).first()
            print(f"   {i}. {post.title[:40]}... ({keyword.keyword if keyword else '未知关键词'})")
            print(f"      👍 {post.likes} | ⭐ {post.collects} | 💬 {post.comments}")

        return True

    except Exception as e:
        print(f"❌ 验证数据失败: {str(e)}")
        return False
    finally:
        db.close()

def main():
    """主函数"""
    print("🚀 开始重置数据库并导入数据\n")

    # 0. 初始化数据库表
    print("🔧 正在初始化数据库表...")
    try:
        from app.database import init_db
        init_db()
        print("✅ 数据库表初始化完成")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {str(e)}")
        return

    # 1. 清空数据库
    if not clean_database():
        print("❌ 清空数据库失败，终止操作")
        return

    # 2. 导入JSON数据
    json_file = "/Users/lishizheng/Desktop/Code/xhs_marketing/MediaCrawler/data/xhs/json/search_contents_2026-01-11.json"
    if not import_json_data(json_file):
        print("❌ 导入数据失败，终止操作")
        return

    # 3. 验证数据
    if not verify_data():
        print("❌ 验证数据失败")
        return

    print("\n✅ 数据重置和导入完成！")
    print("🎯 现在可以在前端页面查看真实的数据统计了")

if __name__ == "__main__":
    main()