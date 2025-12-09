"""组合水印功能测试"""

import pytest
import os
import sys
import tempfile
from pathlib import Path

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from watermark.combo_watermark import create_text_image, add_combo_watermark


@pytest.fixture
def test_video():
    """创建测试视频"""
    temp_dir = tempfile.gettempdir()
    video_path = os.path.join(temp_dir, "test_video.mp4")

    if not os.path.exists(video_path):
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
    output_path = os.path.join(tempfile.gettempdir(), "test_output")
    os.makedirs(output_path, exist_ok=True)
    return output_path


@pytest.fixture
def test_logo():
    """创建测试Logo"""
    from PIL import Image, ImageDraw, ImageFont
    temp_dir = tempfile.gettempdir()
    logo_path = os.path.join(temp_dir, "test_logo.png")

    if not os.path.exists(logo_path):
        # 创建方形Logo
        size = 100
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 绘制圆形Logo
        margin = 10
        draw.ellipse(
            [(margin, margin), (size-margin, size-margin)],
            fill='blue',
            outline='white',
            width=2
        )

        # 添加文字"T"
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", size//2)
        except:
            font = ImageFont.load_default()

        text = "T"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        draw.text((x, y), text, fill='white', font=font)

        img.save(logo_path)

    return logo_path


def test_create_text_image():
    """测试创建文本图片"""
    image, text_height = create_text_image(
        text="Test Watermark",
        font_path=None,
        font_size=48,
        color="white",
        stroke_width=2,
        stroke_color="black",
        bg_padding=20
    )

    assert image is not None
    assert isinstance(text_height, int)
    assert text_height > 0
    assert image.mode == "RGBA"
    assert image.width > 0
    assert image.height > 0


def test_combo_watermark_text_only(test_video, output_dir):
    """测试仅文字的组组合水印"""
    output_path = os.path.join(output_dir, "combo_text_only.mp4")

    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="Text Only Test",
        watermark_path=None,  # 无logo
        text_position=("center", "center"),
        font_size=48,
        color="red",
        text_opacity=0.8,
        stroke_width=2,
        stroke_color="white"
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_combo_watermark_with_logo(test_video, output_dir, test_logo):
    """测试文字 + Logo的组合水印"""
    output_path = os.path.join(output_dir, "combo_with_logo.mp4")

    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="Logo + Text",
        watermark_path=test_logo,
        logo_position=("left", "top"),
        logo_opacity=0.9,
        logo_margin=10,
        text_position=("right", "bottom"),
        font_size=36,
        color="white",
        text_opacity=0.9,
        stroke_width=1,
        stroke_color="black"
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_combo_watermark_logo_scaling(test_video, output_dir, test_logo):
    """测试Logo自动缩放功能"""
    output_path = os.path.join(output_dir, "combo_logo_scaling.mp4")

    # 使用较大的字体，测试logo是否能匹配
    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="Large Font Test",
        watermark_path=test_logo,
        logo_scale_factor=1.0,  # 1倍缩放，应匹配文字高度
        text_position=("center", "center"),
        font_size=72,  # 大字体
        color="yellow"
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_combo_watermark_logo_scale_factor(test_video, output_dir, test_logo):
    """测试Logo缩放因子"""
    output_path = os.path.join(output_dir, "combo_scale_factor.mp4")

    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="Scale 1.5x",
        watermark_path=test_logo,
        logo_scale_factor=1.5,  # 1.5倍缩放
        logo_position=("right", "top"),
        text_position=("left", "bottom"),
        font_size=48
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_combo_watermark_custom_size(test_video, output_dir, test_logo):
    """测试自定义Logo尺寸（覆盖自动缩放）"""
    output_path = os.path.join(output_dir, "combo_custom_size.mp4")

    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="Custom Size",
        watermark_path=test_logo,
        logo_width=150,  # 指定宽度，覆盖自动缩放
        logo_height=150,  # 指定高度
        text_position=("center", "bottom"),
        font_size=36
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_combo_watermark_different_positions(test_video, output_dir, test_logo):
    """测试不同的Logo和文字位置组合"""
    positions = [
        ("top-left", "bottom-right"),
        ("top-right", "bottom-left"),
        ("center", "center"),
    ]

    for i, (logo_pos_name, text_pos_name) in enumerate(positions):
        output_path = os.path.join(output_dir, f"combo_positions_{i}.mp4")

        # 转换位置名称
        logo_positions = {
            "top-left": ("left", "top"),
            "top-right": ("right", "top"),
            "center": ("center", "center"),
            "bottom-left": ("left", "bottom"),
            "bottom-right": ("right", "bottom"),
        }

        add_combo_watermark(
            video_path=test_video,
            output_path=output_path,
            text=f"Pos {i+1}",
            watermark_path=test_logo,
            logo_position=logo_positions[logo_pos_name],
            text_position=logo_positions[text_pos_name],
            font_size=24
        )

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0


def test_combo_watermark_time_range(test_video, output_dir):
    """测试指定时间范围的组合水印"""
    output_path = os.path.join(output_dir, "combo_time_range.mp4")

    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="Time Range",
        watermark_path=None,
        text_position=("left", "top"),
        font_size=36,
        start_time=1.0,
        end_time=2.0
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_combo_watermark_gjpqy_letters(test_video, output_dir, test_logo):
    """测试包含上下延字母的组合水印"""
    output_path = os.path.join(output_dir, "combo_gjpqy.mp4")

    # 测试包含g, j, p, q, y的文本
    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="Testing: gjpqy Letters",
        watermark_path=test_logo,
        logo_position=("left", "bottom"),
        text_position=("right", "top"),
        font_size=48,
        vertical_margin=15  # 增加垂直边距
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_combo_watermark_no_logo_file(test_video, output_dir):
    """测试指定不存在的Logo文件"""
    output_path = os.path.join(output_dir, "combo_no_logo.mp4")

    # 应该能正常处理（仅显示文字）
    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="No Logo File",
        watermark_path="/nonexistent/path/to/logo.png",  # 不存在的路径
        text_position=("center", "center"),
        font_size=36
    )

    # 应该仍然生成输出文件（仅文字水印）
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_combo_watermark_stroke_options(test_video, output_dir, test_logo):
    """测试描边选项"""
    output_path = os.path.join(output_dir, "combo_stroke.mp4")

    # 无描边
    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="No Stroke",
        watermark_path=test_logo,
        font_size=48,
        stroke_width=0  # 无描边
    )

    assert os.path.exists(output_path)

    # 有描边
    output_path2 = os.path.join(output_dir, "combo_with_stroke.mp4")
    add_combo_watermark(
        video_path=test_video,
        output_path=output_path2,
        text="With Stroke",
        watermark_path=test_logo,
        font_size=48,
        stroke_width=3,  # 粗描边
        stroke_color="red"
    )

    assert os.path.exists(output_path2)


def test_combine_images_horizontal():
    """测试水平合并图片"""
    from PIL import Image
    from watermark.combo_watermark import combine_images

    # 创建测试图片
    logo = Image.new('RGBA', (50, 50), (255, 0, 0, 255))  # 红色方块
    text = Image.new('RGBA', (100, 40), (0, 255, 0, 255))  # 绿色方块

    # 水平合并
    combined = combine_images(logo, text, layout='horizontal', spacing=10)

    assert combined.width == 50 + 10 + 100  # logo + spacing + text
    assert combined.height == max(50, 40)  # 最大高度


def test_combine_images_vertical():
    """测试垂直合并图片"""
    from PIL import Image
    from watermark.combo_watermark import combine_images

    # 创建测试图片
    logo = Image.new('RGBA', (50, 50), (255, 0, 0, 255))  # 红色方块
    text = Image.new('RGBA', (100, 40), (0, 255, 0, 255))  # 绿色方块

    # 垂直合并
    combined = combine_images(logo, text, layout='vertical', spacing=10)

    assert combined.width == max(50, 100)  # 最大宽度
    assert combined.height == 50 + 10 + 40  # logo + spacing + text


def test_combo_watermark_combine_mode(test_video, output_dir, test_logo):
    """测试合并模式"""
    output_path = os.path.join(output_dir, "combo_mode.mp4")

    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="Combined Test",
        watermark_path=test_logo,
        combine_mode=True,  # 启用合并模式
        combine_layout='horizontal',  # 水平排列
        logo_position=("right", "bottom"),
        font_size=36,
        color="white"
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_combo_watermark_combine_mode_vertical(test_video, output_dir, test_logo):
    """测试垂直合并模式"""
    output_path = os.path.join(output_dir, "combo_mode_vertical.mp4")

    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="Vertical Test",
        watermark_path=test_logo,
        combine_mode=True,  # 启用合并模式
        combine_layout='vertical',  # 垂直排列
        logo_position=("center", "center"),
        font_size=32,
        color="cyan"
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_combo_watermark_combine_with_spacing(test_video, output_dir, test_logo):
    """测试合并模式的间距设置"""
    output_path = os.path.join(output_dir, "combine_spacing.mp4")

    add_combo_watermark(
        video_path=test_video,
        output_path=output_path,
        text="Spacing Test",
        watermark_path=test_logo,
        combine_mode=True,
        combine_spacing=30,  # 30像素间距
        logo_scale_factor=1.5,  # Logo大一些
        font_size=48
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
