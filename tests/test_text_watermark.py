"""文字水印功能测试"""

import pytest
import os
import sys
import tempfile
from pathlib import Path

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from watermark import add_text_watermark
from watermark.text_watermark_v2 import create_text_image


@pytest.fixture
def test_video():
    """创建测试视频"""
    # 使用跨平台的临时目录
    temp_dir = tempfile.gettempdir()
    video_path = os.path.join(temp_dir, "test_video.mp4")

    if not os.path.exists(video_path):
        # 跨平台的ffmpeg命令（隐藏输出）
        if os.name == 'nt':  # Windows
            null_output = "nul"
            cmd = f'ffmpeg -f lavfi -i testsrc=duration=3:size=1280x720:rate=30 -y "{video_path}" 2>{null_output}'
        else:  # Linux/macOS
            null_output = "/dev/null"
            cmd = f'ffmpeg -f lavfi -i testsrc=duration=3:size=1280x720:rate=30 -y "{video_path}" 2>{null_output}'
        os.system(cmd)
    return video_path


@pytest.fixture
def output_dir():
    """创建输出目录"""
    # 使用跨平台的临时目录
    output_path = os.path.join(tempfile.gettempdir(), "test_output")
    os.makedirs(output_path, exist_ok=True)
    return output_path


def test_create_text_image():
    """测试创建文本图片"""
    # 创建简单文本图片
    image = create_text_image(
        text="Test Watermark",
        font_path=None,
        font_size=48,
        color="white",
        stroke_width=2,
        stroke_color="black",
        bg_padding=20
    )

    assert image is not None
    assert image.mode == "RGBA"
    assert image.width > 0
    assert image.height > 0


def test_text_watermark_gjpqy(test_video, output_dir):
    """测试包含上下延字母的文本水印"""
    output_path = os.path.join(output_dir, "test_gjpqy.mp4")

    # 测试包含g, j, p, q, y的文本
    add_text_watermark(
        video_path=test_video,
        text="Testing: gjpqy Letters",
        output_path=output_path,
        position=("left", "top"),
        font_size=64,
        color="white",
        opacity=0.9,
        stroke_width=2,
        stroke_color="black",
        margin=10
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_text_watermark_large_font(test_video, output_dir):
    """测试大字体文本水印"""
    output_path = os.path.join(output_dir, "test_large_font.mp4")

    add_text_watermark(
        video_path=test_video,
        text="Large Font Test",
        output_path=output_path,
        position=("right", "bottom"),
        font_size=96,
        color="yellow",
        opacity=0.8,
        stroke_width=3,
        stroke_color="red",
        margin=20
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_text_watermark_center_position(test_video, output_dir):
    """测试居中位置的文本水印"""
    output_path = os.path.join(output_dir, "test_center.mp4")

    add_text_watermark(
        video_path=test_video,
        text="Center Position",
        output_path=output_path,
        position=("center", "center"),
        font_size=48,
        color="white",
        opacity=0.9,
        stroke_width=0,
        margin=15
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_text_watermark_time_range(test_video, output_dir):
    """测试指定时间范围的文本水印"""
    output_path = os.path.join(output_dir, "test_time_range.mp4")

    add_text_watermark(
        video_path=test_video,
        text="Time Range Test",
        output_path=output_path,
        position=("right", "top"),
        font_size=36,
        color="cyan",
        opacity=0.7,
        stroke_width=1,
        stroke_color="blue",
        start_time=1.0,
        end_time=2.0,
        margin=10
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
