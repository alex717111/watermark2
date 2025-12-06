"""文字水印功能模块 - 使用 PIL 生成文本图片"""

import os
import sys
import tempfile
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from moviepy import VideoFileClip, ImageClip, CompositeVideoClip


def create_text_image(
    text: str,
    font_path: Optional[str],
    font_size: int,
    color: str,
    stroke_width: int = 0,
    stroke_color: str = 'black',
    bg_padding: int = 20
) -> Image.Image:
    """创建文本图片（使用PIL）

    Args:
        text: 文本内容
        font_path: 字体文件路径
        font_size: 字体大小
        color: 文本颜色
        stroke_width: 描边宽度
        stroke_color: 描边颜色
        bg_padding: 背景内边距

    Returns:
        PIL Image 对象（带透明背景）
    """
    # 创建字体对象
    if font_path and os.path.exists(font_path):
        font = ImageFont.truetype(font_path, font_size)
    else:
        # 使用系统默认字体（跨平台）
        font = None
        if os.name == 'nt':  # Windows
            # 尝试多个常见的Windows字体
            windows_fonts = [
                "C:\\Windows\\Fonts\\arial.ttf",
                "C:\\Windows\\Fonts\\segoeui.ttf",
                "C:\\Windows\\Fonts\\calibri.ttf",
                "C:\\Windows\\Fonts\\tahoma.ttf",
                "C:\\Windows\\Fonts\\verdana.ttf"
            ]
            for win_font in windows_fonts:
                try:
                    font = ImageFont.truetype(win_font, font_size)
                    break
                except:
                    continue
        else:  # Linux/macOS
            # 尝试多个常见的Linux字体
            linux_fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/System/Library/Fonts/Arial.ttf"  # macOS
            ]
            for linux_font in linux_fonts:
                try:
                    font = ImageFont.truetype(linux_font, font_size)
                    break
                except:
                    continue

        # 如果都找不到，使用默认字体
        if font is None:
            try:
                # 尝试从系统加载默认字体
                font = ImageFont.load_default()
                # 对于默认字体，我们无法控制大小，需要调整图像缩放
                # 所以最好创建一个默认大小的字体然后缩放
                if hasattr(font, 'size') and font.size != font_size:
                    # 记录警告
                    print(f"警告：使用默认字体，无法精确控制字体大小为{font_size}")
            except:
                # 最后的手段：创建位图字体
                font = ImageFont.load_default()

    # 创建临时图像来测量文本尺寸
    temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)

    # 获取文本边界框
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 添加额外的垂直空间给字母上下延（g, j, p, q, y）
    # 增加字体大小的 40% 作为额外空间
    extra_vertical = int(font_size * 0.4)

    # 计算最终图像尺寸（包含内边距和额外空间）
    img_width = text_width + bg_padding * 2
    img_height = text_height + bg_padding * 2 + extra_vertical

    # 创建透明背景图像
    image = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 计算文本位置（垂直居中，考虑额外空间）
    x = bg_padding - bbox[0]
    y = bg_padding - bbox[1] + extra_vertical // 2

    # 绘制描边（如果需要）
    if stroke_width > 0:
        # PIL 的 textstroke 需要 Pillow 8.0+
        try:
            draw.text(
                (x, y), text, font=font, fill=color,
                stroke_width=stroke_width, stroke_fill=stroke_color
            )
        except:
            # 如果不支持 stroke，使用简单描边
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
            draw.text((x, y), text, font=font, fill=color)
    else:
        draw.text((x, y), text, font=font, fill=color)

    return image


def add_text_watermark(
    video_path: str,
    text: str,
    output_path: str,
    position: Tuple[str, str] = ('right', 'bottom'),
    font_size: int = 24,
    color: str = 'white',
    font_path: Optional[str] = None,
    opacity: float = 0.9,
    stroke_width: int = 0,
    stroke_color: str = 'black',
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    margin: int = 15
) -> None:
    """向视频添加文字水印（使用PIL生成图片）

    Args:
        video_path: 输入视频文件路径
        text: 水印文字内容
        output_path: 输出视频文件路径
        position: 水印位置元组(horizontal, vertical)
                 horizontal: 'left', 'center', 'right'
                 vertical: 'top', 'center', 'bottom'
        font_size: 字体大小（像素）
        color: 文字颜色（支持颜色名称或十六进制如#FF0000）
        font_path: 字体文件路径（TTF格式），默认使用系统字体
        opacity: 文字透明度（0.0-1.0）
        stroke_width: 描边宽度（默认0，表示无描边）
        stroke_color: 描边颜色
        start_time: 水印开始显示时间（秒），默认从视频开始
        end_time: 水印结束显示时间（秒），默认到视频结束
        margin: 边距（像素，默认：15）
    """
    # 加载视频
    video = VideoFileClip(video_path)

    # 创建文本图片
    text_image = create_text_image(
        text=text,
        font_path=font_path,
        font_size=font_size,
        color=color,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        bg_padding=20
    )

    # 保存临时图片（跨平台兼容）
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    temp_image_path = temp_file.name
    temp_file.close()
    text_image.save(temp_image_path, "PNG")

    # 创建水印剪辑
    watermark = ImageClip(temp_image_path)

    # 设置持续时间
    if start_time is None:
        start_time = 0
    if end_time is None:
        end_time = video.duration

    watermark = watermark.with_start(start_time)
    watermark = watermark.with_end(end_time)
    watermark = watermark.with_duration(end_time - start_time)

    # 验证位置参数
    _validate_position_tuple(position)

    # 设置水印位置
    position_func = _get_position_function(video, watermark, position, margin=margin)
    watermark = watermark.with_position(position_func)

    # 设置透明度
    watermark = watermark.with_opacity(opacity)

    # 合成视频
    final_video = CompositeVideoClip([video, watermark], size=video.size)

    # 写出视频
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        threads=os.cpu_count(),
        logger=None
    )

    # 清理临时文件
    try:
        os.remove(temp_image_path)
    except:
        pass

    # 释放资源
    video.close()
    watermark.close()
    final_video.close()


def _validate_position_tuple(position: Tuple[str, str]):
    """验证位置元组是否合法"""
    valid_horizontal = ['left', 'center', 'right']
    valid_vertical = ['top', 'center', 'bottom']

    if len(position) != 2:
        raise ValueError(f"位置必须是包含2个元素的元组， got {len(position)}")

    horizontal, vertical = position

    if horizontal not in valid_horizontal:
        raise ValueError(f"水平位置必须是 {valid_horizontal} 之一， got '{horizontal}'")

    if vertical not in valid_vertical:
        raise ValueError(f"垂直位置必须是 {valid_vertical} 之一， got '{vertical}'")

    return position


def _get_position_function(
    video: VideoFileClip,
    watermark: ImageClip,
    position: Tuple[str, str],
    margin: int
):
    """获取水印位置函数"""
    horizontal, vertical = position

    def position_func(t):
        if horizontal == 'left':
            x = margin
        elif horizontal == 'center':
            x = (video.w - watermark.w) / 2
        else:  # right
            x = video.w - watermark.w - margin

        if vertical == 'top':
            y = margin
        elif vertical == 'center':
            y = (video.h - watermark.h) / 2
        else:  # bottom
            y = video.h - watermark.h - margin

        return (x, y)

    return position_func
