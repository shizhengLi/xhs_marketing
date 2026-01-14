#!/usr/bin/env python3
"""
检查MediaCrawler数据中的视频链接
"""
import json
import os
from pathlib import Path
from collections import defaultdict

def check_video_in_json_files():
    """检查所有JSON文件中的视频链接"""

    json_dir = Path("/Users/lishizheng/Desktop/Code/xhs_marketing/MediaCrawler/data/xhs/json")

    # 查找所有search_contents_*.json文件
    content_files = list(json_dir.glob("search_contents_*.json"))

    print(f"=== 小红书数据视频链接检查 ===\n")
    print(f"找到 {len(content_files)} 个内容文件")

    total_notes = 0
    video_notes = 0
    image_notes = 0
    empty_media_notes = 0
    file_statistics = defaultdict(dict)

    for file_path in sorted(content_files):
        print(f"\n📄 分析文件: {file_path.name}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                print(f"   ⚠️  文件格式不是列表，跳过")
                continue

            file_notes_count = len(data)
            file_video_count = 0
            file_image_count = 0
            file_empty_count = 0

            print(f"   📊 总笔记数: {file_notes_count}")

            for note in data:
                total_notes += 1
                video_url = note.get('video_url', '').strip()
                image_list = note.get('image_list', '').strip()
                note_type = note.get('type', 'unknown')
                title = note.get('title', '无标题')[:50]

                # 检查媒体类型
                if video_url:  # 有视频链接
                    video_notes += 1
                    file_video_count += 1
                    if file_video_count <= 3:  # 只显示前3个例子
                        print(f"   🎬 视频笔记: {title}...")
                        print(f"      视频链接: {video_url[:80]}...")

                elif image_list:  # 有图片链接
                    image_notes += 1
                    file_image_count += 1

                else:  # 没有媒体内容
                    empty_media_notes += 1
                    file_empty_count += 1

            # 保存文件统计信息
            file_statistics[file_path.name] = {
                'total': file_notes_count,
                'video': file_video_count,
                'image': file_image_count,
                'empty': file_empty_count,
                'video_rate': f"{file_video_count/file_notes_count*100:.1f}%" if file_notes_count > 0 else "0%"
            }

            print(f"   🎬 视频笔记: {file_video_count} ({file_video_count/file_notes_count*100:.1f}%)")
            print(f"   📷 图片笔记: {file_image_count} ({file_image_count/file_notes_count*100:.1f}%)")
            print(f"   📭 无媒体: {file_empty_count} ({file_empty_count/file_notes_count*100:.1f}%)")

        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")

    # 总体统计
    print(f"\n{'='*50}")
    print(f"📊 总体统计")
    print(f"{'='*50}")
    print(f"📄 分析文件数: {len(content_files)}")
    print(f"📝 总笔记数: {total_notes}")
    print(f"🎬 视频笔记数: {video_notes} ({video_notes/total_notes*100:.1f}%)")
    print(f"📷 图片笔记数: {image_notes} ({image_notes/total_notes*100:.1f}%)")
    print(f"📭 无媒体笔记数: {empty_media_notes} ({empty_media_notes/total_notes*100:.1f}%)")

    # 按文件详细统计
    print(f"\n{'='*50}")
    print(f"📋 各文件视频统计")
    print(f"{'='*50}")

    # 按视频比例排序
    sorted_files = sorted(file_statistics.items(),
                         key=lambda x: x[1]['video'],
                         reverse=True)

    for filename, stats in sorted_files:
        print(f"\n📁 {filename}")
        print(f"   总数: {stats['total']} | "
              f"视频: {stats['video']} ({stats['video_rate']}) | "
              f"图片: {stats['image']} | "
              f"空: {stats['empty']}")

    # 视频详情分析
    if video_notes > 0:
        print(f"\n{'='*50}")
        print(f"🎬 视频内容分析")
        print(f"{'='*50}")
        print(f"✅ 发现 {video_notes} 个包含视频的笔记")
        print(f"📈 视频占比: {video_notes/total_notes*100:.1f}%")

        if video_notes/total_notes*100 < 5:
            print(f"⚠️  视频内容较少，主要侧重于图文内容")
        elif video_notes/total_notes*100 < 20:
            print(f"📊 视频内容适中，图文视频并重")
        else:
            print(f"🎬 视频内容丰富，视频为主要形式")
    else:
        print(f"\n{'='*50}")
        print(f"🎬 视频内容分析")
        print(f"{'='*50}")
        print(f"❌ 未发现任何包含视频的笔记")
        print(f"📷 所有内容都是基于图片的图文笔记")

if __name__ == "__main__":
    check_video_in_json_files()