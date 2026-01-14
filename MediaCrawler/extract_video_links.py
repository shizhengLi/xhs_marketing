#!/usr/bin/env python3
"""
提取小红书数据中的视频链接
"""
import json
from pathlib import Path
from collections import defaultdict

def extract_video_links():
    """提取所有视频链接"""

    json_dir = Path("/Users/lishizheng/Desktop/Code/xhs_marketing/MediaCrawler/data/xhs/json")
    content_files = list(json_dir.glob("search_contents_*.json"))

    print(f"=== 小红书视频链接提取 ===\n")

    all_video_data = []

    for file_path in sorted(content_files):
        print(f"📄 处理文件: {file_path.name}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for note in data:
                video_url = note.get('video_url', '').strip()
                if video_url:
                    video_info = {
                        'title': note.get('title', ''),
                        'note_id': note.get('note_id', ''),
                        'video_url': video_url,
                        'note_url': note.get('note_url', ''),
                        'liked_count': note.get('liked_count', ''),
                        'author': note.get('nickname', ''),
                        'source_keyword': note.get('source_keyword', ''),
                        'file_source': file_path.name
                    }
                    all_video_data.append(video_info)

        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")

    # 保存视频链接到文件
    output_file = json_dir.parent / "video_links_extracted.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_video_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 成功提取 {len(all_video_data)} 个视频链接")
    print(f"📁 保存到: {output_file}")

    # 显示一些统计信息
    print(f"\n📊 视频链接统计:")

    # 按关键词统计
    keyword_stats = defaultdict(int)
    for video in all_video_data:
        keyword = video.get('source_keyword', 'unknown')
        keyword_stats[keyword] += 1

    print(f"\n🎯 按关键词分类:")
    for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   {keyword}: {count} 个视频")

    # 显示前5个视频链接示例
    print(f"\n🔗 视频链接示例 (前5个):")
    for i, video in enumerate(all_video_data[:5], 1):
        print(f"\n{i}. {video['title'][:40]}...")
        print(f"   作者: {video['author']}")
        print(f"   点赞: {video['liked_count']}")
        print(f"   关键词: {video['source_keyword']}")
        print(f"   视频: {video['video_url'][:80]}...")

if __name__ == "__main__":
    extract_video_links()