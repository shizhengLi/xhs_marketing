import sys
import os
import sqlite3

# 数据库文件路径
db_path = "/Users/lishizheng/Desktop/Code/xhs_marketing/backend/xhs_monitoring.db"

def migrate_database():
    """添加新字段到现有数据库表"""

    print(f"正在迁移数据库: {db_path}")

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查表结构
        cursor.execute("PRAGMA table_info(posts)")
        columns = [column[1] for column in cursor.fetchall()]

        print(f"当前posts表的字段: {columns}")

        # 添加video_url字段（如果不存在）
        if 'video_url' not in columns:
            print("添加video_url字段...")
            cursor.execute("ALTER TABLE posts ADD COLUMN video_url VARCHAR(500)")
            print("✓ video_url字段添加成功")
        else:
            print("video_url字段已存在")

        # 添加video_content字段（如果不存在）
        if 'video_content' not in columns:
            print("添加video_content字段...")
            cursor.execute("ALTER TABLE posts ADD COLUMN video_content TEXT")
            print("✓ video_content字段添加成功")
        else:
            print("video_content字段已存在")

        # 提交更改
        conn.commit()

        # 验证更改
        cursor.execute("PRAGMA table_info(posts)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"更新后的posts表字段: {new_columns}")

        print("数据库迁移完成！")

    except Exception as e:
        print(f"数据库迁移失败: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()