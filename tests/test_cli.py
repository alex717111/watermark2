"""CLI测试

本测试文件包含两个部分：
1. 命令行接口测试（help、参数等）
2. 功能测试（实际处理视频，生成可验证的文件）

输出文件保存在 test_output/ 目录：
test_output/
├── test_video.mp4              # 原始测试视频
test_output/
├── test_watermark.png          # 测试水印图片
test_output/
├── output_watermark.mp4        # 图片水印结果
test_output/
├── output_text.mp4             # 文字水印结果
test_output/
└── output_insert.mp4           # 视频插入结果
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from click.testing import CliRunner

# 将项目根目录添加到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 创建test_output目录
TEST_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'test_output')
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

# =======================================
# 测试文件命名规范
# =======================================
OUTPUT_VIDEO_WATERMARK = os.path.join(TEST_OUTPUT_DIR, 'output_watermark.mp4')
OUTPUT_VIDEO_TEXT = os.path.join(TEST_OUTPUT_DIR, 'output_text.mp4')
OUTPUT_VIDEO_INSERT = os.path.join(TEST_OUTPUT_DIR, 'output_insert.mp4')
TEST_VIDEO = os.path.join(TEST_OUTPUT_DIR, 'test_video.mp4')
TEST_WATERMARK = os.path.join(TEST_OUTPUT_DIR, 'test_watermark.png')
TEST_INSERT_VIDEO = os.path.join(TEST_OUTPUT_DIR, 'test_insert.mp4')


# =======================================
# 单元测试：命令行接口
# =======================================


def test_help():
    """测试帮助命令"""
    from src.cli import cli
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert '视频水印工具' in result.output


def test_positions():
    """测试位置列表命令"""
    from src.cli import cli
    runner = CliRunner()
    result = runner.invoke(cli, ['positions'])
    assert result.exit_code == 0
    assert 'top-left' in result.output


def test_watermark_help():
    """测试图片水印命令帮助"""
    from src.cli import cli
    runner = CliRunner()
    result = runner.invoke(cli, ['watermark', '--help'])
    assert result.exit_code == 0
    assert '--input' in result.output
    assert '--watermark' in result.output


def test_watermark_text_help():
    """测试文字水印命令帮助"""
    from src.cli import cli
    runner = CliRunner()
    result = runner.invoke(cli, ['watermark-text', '--help'])
    assert result.exit_code == 0
    assert '--text' in result.output
    assert '--font-size' in result.output


def test_insert_help():
    """测试插入视频命令帮助"""
    from src.cli import cli
    runner = CliRunner()
    result = runner.invoke(cli, ['insert', '--help'])
    assert result.exit_code == 0
    assert '--main' in result.output
    assert '--insert' in result.output


# =======================================
# 功能测试：实际视频处理（生成可查看的文件）
# =======================================

def create_test_video(output_path, duration=5, width=1280, height=720):
    """创建测试视频（使用FFmpeg）"""
    cmd = f'ffmpeg -f lavfi -i testsrc=duration={duration}:size={width}x{height}:rate=30 -pix_fmt yuv420p {output_path} -y'
    ret = os.system(cmd)
    if ret != 0:
        raise RuntimeError(f"创建测试视频失败: {output_path}")
    print(f"✅ 创建测试视频: {output_path} ({width}x{height}, {duration}s)")


def create_test_watermark(output_path, width=200, height=80):
    """创建测试水印图片"""
    from PIL import Image, ImageDraw, ImageFont

    # 创建带透明的图片
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 绘制半透明背景
    draw.rectangle([(0, 0), (width, height)], fill=(0, 0, 0, 180))

    # 添加文字
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
    except:
        font = ImageFont.load_default()

    text = "WATERMARK"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), text, fill='white', font=font)

    img.save(output_path)
    print(f"✅ 创建测试水印: {output_path} ({width}x{height})")


def create_fullsize_watermark(video_path, output_path):
    """创建全尺寸水印图片（推荐方案）"""
    import subprocess

    # 获取视频尺寸
    cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 {video_path}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("无法获取视频尺寸")

    width, height = map(int, result.stdout.strip().split('x'))

    # 创建全尺寸透明图片
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 绘制水印（右下角）
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()

    text = "TEST WATERMARK"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 右下角位置，留边距
    margin = 50
    x = width - text_width - margin
    y = height - text_height - margin

    # 添加半透明背景
    bg_margin = 20
    draw.rectangle(
        [(x - bg_margin, y - bg_margin),
         (x + text_width + bg_margin, y + text_height + bg_margin)],
        fill=(0, 0, 0, 180)
    )

    draw.text((x, y), text, fill='white', font=font)

    img.save(output_path)
    print(f"✅ 创建全尺寸水印: {output_path} ({width}x{height})")


def test_functional_watermark():
    """功能测试：实际添加图片水印，生成可查看的文件"""
    from src.cli import cli
    runner = CliRunner()

    print("\n" + "="*60)
    print("功能测试：添加图片水印")
    print("="*60)

    # 删除旧文件
    for f in [TEST_VIDEO, TEST_WATERMARK, OUTPUT_VIDEO_WATERMARK]:
        if os.path.exists(f):
            os.remove(f)

    # 创建测试文件
    try:
        create_test_video(TEST_VIDEO, duration=3)
        create_fullsize_watermark(TEST_VIDEO, TEST_WATERMARK)
    except Exception as e:
        print(f"❌ 创建测试文件失败: {e}")
        print("跳过实际功能测试")
        return

    # 运行水印命令（默认全尺寸模式）
    result = runner.invoke(cli, [
        'watermark',
        '--input', TEST_VIDEO,
        '--output', OUTPUT_VIDEO_WATERMARK,
        '--watermark', TEST_WATERMARK,
        '--opacity', '0.9'
    ])

    # 检查结果
    if result.exit_code == 0:
        if os.path.exists(OUTPUT_VIDEO_WATERMARK):
            file_size = os.path.getsize(OUTPUT_VIDEO_WATERMARK)
            print(f"✅ 水印添加成功: {OUTPUT_VIDEO_WATERMARK}")
            print(f"📁 文件大小: {file_size / 1024:.2f} KB")
            print(f"👉 请手动播放查看效果")
        else:
            print(f"❌ 输出文件未生成")
            print(result.output)
    else:
        print(f"❌ 水印命令失败")
        print(f"返回码: {result.exit_code}")
        print(f"输出: {result.output}")


def test_functional_watermark_text():
    """功能测试：添加文字水印"""
    from src.cli import cli
    runner = CliRunner()

    print("\n" + "="*60)
    print("功能测试：添加文字水印")
    print("="*60)

    # 删除旧文件
    if os.path.exists(OUTPUT_VIDEO_TEXT):
        os.remove(OUTPUT_VIDEO_TEXT)

    # 使用之前创建的测试视频
    if not os.path.exists(TEST_VIDEO):
        create_test_video(TEST_VIDEO, duration=3)

    # 运行文字水印命令
    result = runner.invoke(cli, [
        'watermark-text',
        '--input', TEST_VIDEO,
        '--output', OUTPUT_VIDEO_TEXT,
        '--text', 'Test Video',
        '--font-size', '48',
        '--color', 'white',
        '--position', 'top-right',
        '--opacity', '0.9'
    ])

    # 检查结果
    if result.exit_code == 0:
        if os.path.exists(OUTPUT_VIDEO_TEXT):
            file_size = os.path.getsize(OUTPUT_VIDEO_TEXT)
            print(f"✅ 文字水印添加成功: {OUTPUT_VIDEO_TEXT}")
            print(f"📁 文件大小: {file_size / 1024:.2f} KB")
            print(f"👉 请手动播放查看效果")
        else:
            print(f"❌ 输出文件未生成")
            print(result.output)
    else:
        print(f"❌ 文字水印命令失败")
        print(f"返回码: {result.exit_code}")
        print(f"输出: {result.output}")


def test_functional_insert():
    """功能测试：插入视频片段"""
    from src.cli import cli
    runner = CliRunner()

    print("\n" + "="*60)
    print("功能测试：插入视频片段（无缝模式）")
    print("="*60)

    # 删除旧文件
    for f in [TEST_INSERT_VIDEO, OUTPUT_VIDEO_INSERT]:
        if os.path.exists(f):
            os.remove(f)

    # 创建主视频（5秒）
    if not os.path.exists(TEST_VIDEO):
        create_test_video(TEST_VIDEO, duration=5)

    # 创建插入视频（2秒，不同颜色）
    cmd = f'ffmpeg -f lavfi -i testsrc=duration=2:size=1280x720:rate=30 -vf hue=s=0 -pix_fmt yuv420p {TEST_INSERT_VIDEO} -y'
    ret = os.system(cmd)
    if ret != 0:
        print(f"❌ 创建插入视频失败")
        return
    print(f"✅ 创建插入视频: {TEST_INSERT_VIDEO}")

    # 运行插入命令（在第2秒插入，默认使用无缝模式）
    result = runner.invoke(cli, [
        'insert',
        '--main', TEST_VIDEO,
        '--insert', TEST_INSERT_VIDEO,
        '--output', OUTPUT_VIDEO_INSERT,
        '--position', '2',
        '--audio-mode', 'keep'
        # 不再指定 --seamless，因为现在是默认行为
    ])

    # 检查结果
    if result.exit_code == 0:
        if os.path.exists(OUTPUT_VIDEO_INSERT):
            file_size = os.path.getsize(OUTPUT_VIDEO_INSERT)
            print(f"✅ 视频插入成功: {OUTPUT_VIDEO_INSERT}")
            print(f"📁 文件大小: {file_size / 1024:.2f} KB")
            print(f"👉 请手动播放查看效果（应无黑屏）")
        else:
            print(f"❌ 输出文件未生成")
            print(result.output)
    else:
        print(f"❌ 插入命令失败")
        print(f"返回码: {result.exit_code}")
        print(f"输出: {result.output}")


# =======================================
# 主函数：运行所有测试
# =======================================


if __name__ == '__main__':
    print("\n" + "="*60)
    print("视频水印工具 - 完整测试")
    print("="*60 + "\n")

    # 创建输出目录（如果不存在）
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    print(f"📁 输出目录: {TEST_OUTPUT_DIR}")
    print(f"   所有测试文件将保存在此目录\n")

    # 运行单元测试
    print("【单元测试】")
    try:
        test_help()
        print("✅ 测试1通过: help命令")
        test_positions()
        print("✅ 测试2通过: positions命令")
        test_watermark_help()
        print("✅ 测试3通过: watermark帮助命令")
        test_watermark_text_help()
        print("✅ 测试4通过: watermark-text帮助命令")
        test_insert_help()
        print("✅ 测试5通过: insert帮助命令")
    except Exception as e:
        print(f"❌ 单元测试失败: {e}")
        sys.exit(1)

    print("\n【功能测试】")
    print("注意：功能测试需要FFmpeg支持")
    print(f"- 所有文件将保存在: {TEST_OUTPUT_DIR}")
    print("\n")

    # 检查FFmpeg
    if os.system('ffmpeg -version > /dev/null 2>&1') != 0:
        print("⚠️  FFmpeg未找到，跳过功能测试")
        print("   请安装FFmpeg: sudo apt install ffmpeg\n")
    else:
        try:
            test_functional_watermark()
            test_functional_watermark_text()
            test_functional_insert()
        except Exception as e:
            print(f"❌ 功能测试失败: {e}")

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n生成的文件：")
    if os.path.exists(TEST_VIDEO):
        print(f"✅ {TEST_VIDEO} - 测试视频（3秒）")
    if os.path.exists(TEST_WATERMARK):
        print(f"✅ {TEST_WATERMARK} - 水印图片（全尺寸）")
    if os.path.exists(TEST_INSERT_VIDEO):
        print(f"✅ {TEST_INSERT_VIDEO} - 插入视频（2秒）")
    if os.path.exists(OUTPUT_VIDEO_WATERMARK):
        print(f"✅ {OUTPUT_VIDEO_WATERMARK} - 图片水印结果")
    if os.path.exists(OUTPUT_VIDEO_TEXT):
        print(f"✅ {OUTPUT_VIDEO_TEXT} - 文字水印结果")
    if os.path.exists(OUTPUT_VIDEO_INSERT):
        print(f"✅ {OUTPUT_VIDEO_INSERT} - 视频插入结果")
    print("\n🎬 请使用播放器查看.mp4文件确认效果")
    print("="*60)

