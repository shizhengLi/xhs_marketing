#!/usr/bin/env python3
"""
筛选出时长小于1分钟的视频
"""
import json
import subprocess
import os
import requests
import struct
from typing import List, Dict, Any, Optional
from pathlib import Path

def get_video_duration_ffprobe(video_url: str) -> Optional[float]:
    """
    使用ffprobe获取视频时长（秒）
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_url
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            return duration
        return None
    except Exception:
        return None

def parse_mp4_duration(data: bytes) -> Optional[float]:
    """
    解析MP4文件数据，提取视频时长
    查找moov atom中的mvhd box
    """
    try:
        i = 0
        while i < len(data) - 8:
            # 读取atom大小和类型
            if i + 8 > len(data):
                break
                
            size = struct.unpack('>I', data[i:i+4])[0]
            atom_type = data[i+4:i+8].decode('ascii', errors='ignore')
            
            if size == 0 or size > len(data) - i:
                i += 1
                continue
            
            # 查找moov atom
            if atom_type == 'moov':
                moov_data = data[i:i+size]
                j = 8  # 跳过moov header
                
                while j < len(moov_data) - 8:
                    mvhd_size = struct.unpack('>I', moov_data[j:j+4])[0]
                    mvhd_type = moov_data[j+4:j+8].decode('ascii', errors='ignore')
                    
                    if mvhd_type == 'mvhd':
                        # mvhd box包含时长信息
                        version = moov_data[j+8]
                        
                        if version == 0:
                            # Version 0: 32-bit timescale and duration
                            timescale = struct.unpack('>I', moov_data[j+20:j+24])[0]
                            duration = struct.unpack('>I', moov_data[j+24:j+28])[0]
                        else:
                            # Version 1: 64-bit timescale and duration
                            timescale = struct.unpack('>I', moov_data[j+28:j+32])[0]
                            duration = struct.unpack('>Q', moov_data[j+32:j+40])[0]
                        
                        if timescale > 0:
                            return duration / timescale
                        break
                    
                    if mvhd_size == 0 or mvhd_size > len(moov_data) - j:
                        break
                    j += mvhd_size
            
            if size == 1:  # Extended size
                if i + 16 > len(data):
                    break
                size = struct.unpack('>Q', data[i+8:i+16])[0]
                i += size
            else:
                i += size
    except Exception:
        pass
    
    return None

def get_video_duration_mp4_parse(video_url: str) -> Optional[float]:
    """
    通过下载MP4文件的一部分并解析来获取视频时长
    先尝试下载文件末尾（moov atom通常在末尾），如果失败则下载开头
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        # 先获取文件大小
        head_response = requests.head(video_url, headers=headers, timeout=10, allow_redirects=True)
        content_length = head_response.headers.get('Content-Length')
        
        if not content_length:
            # 如果无法获取Content-Length，尝试下载最后64KB
            headers['Range'] = 'bytes=-65536'
            response = requests.get(video_url, headers=headers, timeout=15, stream=True)
            if response.status_code == 206:
                data = response.content
                duration = parse_mp4_duration(data)
                if duration:
                    return duration
        else:
            file_size = int(content_length)
            
            # 尝试下载最后128KB（通常包含moov atom）
            end_bytes = min(131072, file_size)
            headers['Range'] = f'bytes={file_size-end_bytes}-{file_size-1}'
            response = requests.get(video_url, headers=headers, timeout=15, stream=True)
            
            if response.status_code == 206:
                data = response.content
                duration = parse_mp4_duration(data)
                if duration:
                    return duration
            
            # 如果末尾没有找到，尝试下载开头64KB
            headers['Range'] = 'bytes=0-65535'
            response = requests.get(video_url, headers=headers, timeout=15, stream=True)
            if response.status_code == 206:
                data = response.content
                duration = parse_mp4_duration(data)
                if duration:
                    return duration
        
        return None
    except Exception as e:
        return None

def get_video_duration(video_url: str, use_ffprobe: bool = True) -> Optional[float]:
    """
    获取视频时长（秒）
    优先使用ffprobe，如果不可用则尝试解析MP4文件头
    """
    # 优先使用ffprobe（最准确）
    if use_ffprobe:
        duration = get_video_duration_ffprobe(video_url)
        if duration is not None:
            return duration
    
    # 如果ffprobe不可用，尝试解析MP4文件头
    duration = get_video_duration_mp4_parse(video_url)
    if duration is not None:
        return duration
    
    return None

def filter_short_videos(
    input_file: str,
    output_file: str = None,
    max_duration: int = 60,
    show_progress: bool = True
) -> List[Dict[str, Any]]:
    """
    筛选出时长小于指定秒数的视频
    
    Args:
        input_file: 输入的JSON文件路径
        output_file: 输出的JSON文件路径（如果为None，则自动生成）
        max_duration: 最大时长（秒），默认60秒（1分钟）
        show_progress: 是否显示进度
    
    Returns:
        筛选后的视频列表
    """
    # 检查ffprobe是否可用
    ffprobe_available = False
    try:
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
        ffprobe_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  警告: 未找到 ffprobe 工具")
        print("   建议安装 ffmpeg 以获取准确的视频时长:")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu: sudo apt-get install ffmpeg")
        print("   Windows: 下载并安装 https://ffmpeg.org/download.html")
        print("\n   将尝试使用其他方法，但可能无法准确获取时长...\n")
    
    # 读取JSON文件
    print(f"📖 读取文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    print(f"📊 总共 {len(videos)} 个视频")
    print(f"🎯 筛选条件: 时长 < {max_duration} 秒（{max_duration//60}分钟）\n")
    
    short_videos = []
    failed_videos = []
    
    for i, video in enumerate(videos, 1):
        video_url = video.get('video_url', '')
        title = video.get('title', '未知标题')[:30]
        
        if not video_url:
            print(f"⚠️  [{i}/{len(videos)}] 跳过: 无视频URL")
            continue
        
        if show_progress:
            print(f"🔍 [{i}/{len(videos)}] 检查: {title}...", end=' ', flush=True)
        
        # 获取视频时长
        duration = get_video_duration(video_url, use_ffprobe=ffprobe_available)
        
        if duration is None:
            failed_videos.append(video)
            if show_progress:
                print("❌ 失败")
            continue
        
        # 格式化时长显示
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        duration_str = f"{minutes}:{seconds:02d}"
        
        if show_progress:
            print(f"⏱️  {duration_str} ({duration:.1f}秒)")
        
        # 筛选小于指定时长的视频（保留所有原始信息）
        if duration < max_duration:
            # 使用copy()保留所有原始字段，只添加时长信息
            video_with_duration = video.copy()
            video_with_duration['duration'] = duration  # 添加时长（秒）
            video_with_duration['duration_str'] = duration_str  # 添加格式化的时长字符串
            short_videos.append(video_with_duration)
    
    print(f"\n✅ 筛选完成!")
    print(f"   - 符合条件的视频: {len(short_videos)} 个")
    print(f"   - 获取时长失败: {len(failed_videos)} 个")
    print(f"   - 总视频数: {len(videos)} 个")
    
    # 保存结果
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_short_videos.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(short_videos, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存到: {output_file}")
    
    # 显示统计信息
    if short_videos:
        durations = [v['duration'] for v in short_videos]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration_found = max(durations)
        
        print(f"\n📈 统计信息:")
        print(f"   - 平均时长: {avg_duration:.1f} 秒 ({int(avg_duration//60)}:{int(avg_duration%60):02d})")
        print(f"   - 最短时长: {min_duration:.1f} 秒 ({int(min_duration//60)}:{int(min_duration%60):02d})")
        print(f"   - 最长时长: {max_duration_found:.1f} 秒 ({int(max_duration_found//60)}:{int(max_duration_found%60):02d})")
    
    return short_videos

if __name__ == '__main__':
    import sys
    
    # 默认输入文件
    input_file = '/Users/lishizheng/Desktop/Code/xhs_marketing/MediaCrawler/data/xhs/video_links_extracted.json'
    
    # 如果提供了命令行参数，使用参数作为输入文件
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    
    # 执行筛选
    short_videos = filter_short_videos(
        input_file=input_file,
        max_duration=60,  # 1分钟 = 60秒
        show_progress=True
    )
    
    print(f"\n🎉 完成! 找到 {len(short_videos)} 个时长小于1分钟的视频")
