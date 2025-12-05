#!/usr/bin/env python3
"""示例：演示如何使用视频水印工具"""

import os
import sys

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from watermark import add_image_watermark, add_text_watermark
from insert import insert_video

def demo_image_watermark():
    """演示图片水印"""
    print("=== 示例1：添加图片水印 ===")
    print("命令：")
    print("python main.py watermark \\")
    print("  -i input.mp4 \\")
    print("  -o output_with_logo.mp4 \\")
    print("  -w logo.png \\")
    print("  -p bottom-right \\")
    print("  --opacity 0.6")
    print()

def demo_text_watermark():
    """演示文字水印"""
    print("=== 示例2：添加文字水印 ===")
    print("命令：")
    print("python main.py watermark-text \\")
    print("  -i input.mp4 \\")
    print("  -o output_with_text.mp4 \\")
    print("  -t \"Copyright © 2025\" \\")
    print("  -p top-left \\")
    print("  --font-size 24")
    print("  --color white")
    print()

def demo_video_insert():
    """演示视频插入"""
    print("=== 示例3：插入视频 ===")
    print("命令：")
    print("python main.py insert \\")
    print("  -m main.mp4 \\")
    print("  -i insert.mp4 \\")
    print("  -o output_inserted.mp4 \\")
    print("  -p 30")
    print("  --audio-mode mix")
    print()

if __name__ == '__main__':
    print("视频水印工具 - 示例命令演示")
    print("=" * 50)
    print()
    
    demo_image_watermark()
    demo_text_watermark()
    demo_video_insert()
    
    print("=" * 50)
    print("运行帮助查看所有选项：python main.py --help")
    print("查看位置选项：python main.py positions")
