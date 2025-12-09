"""组合水印功能模块 - 支持图片(可选) + 文字(必选)"""

import os
import tempfile
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip


def combine_images(
    logo_image: Image.Image,
    text_image: Image.Image,
    layout: str = 'horizontal',
    spacing: int = 10
) -> Image.Image:
    """合并Logo和文字图片

    Args:
        logo_image: Logo图片
        text_image: 文字图片
        layout: 布局方式 ('horizontal' 水平, 'vertical' 垂直)
        spacing: 图片之间的间距（像素）

    Returns:
        合并后的图片
    """
    if layout == 'horizontal':
        # 水平排列：logo在左，文字在右
        total_width = logo_image.width + text_image.width + spacing
        total_height = max(logo_image.height, text_image.height)

        # 创建新图片（透明背景）
        combined = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))

        # 计算垂直居中位置
        logo_y = (total_height - logo_image.height) // 2
        text_y = (total_height - text_image.height) // 2

        # 粘贴图片
        combined.paste(logo_image, (0, logo_y), logo_image)
        combined.paste(text_image, (logo_image.width + spacing, text_y), text_image)

    else:  # vertical
        # 垂直排列：logo在上，文字在下
        total_width = max(logo_image.width, text_image.width)
        total_height = logo_image.height + text_image.height + spacing

        # 创建新图片（透明背景）
        combined = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))

        # 计算水平居中位置
        logo_x = (total_width - logo_image.width) // 2
        text_x = (total_width - text_image.width) // 2

        # 粘贴图片
        combined.paste(logo_image, (logo_x, 0), logo_image)
        combined.paste(text_image, (text_x, logo_image.height + spacing), text_image)

    return combined


def create_text_image(
    text: str,
    font_path: Optional[str],
    font_size: int,
    color: str,
    stroke_width: int = 0,
    stroke_color: str = 'black',
    bg_padding: int = 20
) -> Tuple[Image.Image, int]:
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
        Tuple[PIL Image 对象, 文本高度]
    """
    # 创建字体对象
    if font_path and os.path.exists(font_path):
        font = ImageFont.truetype(font_path, font_size)
    else:
        # 使用系统默认字体（跨平台）
        font = None
        if os.name == 'nt':  # Windows
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
            linux_fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Arial.ttf"
            ]
            for linux_font in linux_fonts:
                try:
                    font = ImageFont.truetype(linux_font, font_size)
                    break
                except:
                    continue

        if font is None:
            try:
                font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()

    # 创建临时图像来测量文本尺寸
    temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)

    # 获取文本边界框
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 添加额外的垂直空间给字母上下延
    extra_vertical = int(font_size * 0.4)

    # 计算最终图像尺寸
    img_width = text_width + bg_padding * 2
    img_height = text_height + bg_padding * 2 + extra_vertical

    # 创建透明背景图像
    image = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 计算文本位置
    x = bg_padding - bbox[0]
    y = bg_padding - bbox[1] + extra_vertical // 2

    # 绘制描边
    if stroke_width > 0:
        try:
            draw.text(
                (x, y), text, font=font, fill=color,
                stroke_width=stroke_width, stroke_fill=stroke_color
            )
        except:
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
            draw.text((x, y), text, font=font, fill=color)
    else:
        draw.text((x, y), text, font=font, fill=color)

    return image, text_height


def add_combo_watermark(
    video_path: str,
    output_path: str,
    text: str,
    watermark_path: Optional[str] = None,
    logo_position: Tuple[str, str] = ('left', 'top'),
    logo_opacity: float = 0.9,
    logo_margin: int = 10,
    logo_width: Optional[int] = None,
    logo_height: Optional[int] = None,
    logo_scale_factor: float = 1.0,
    text_position: Tuple[str, str] = ('right', 'bottom'),
    font_size: int = 24,
    color: str = 'white',
    font_path: Optional[str] = None,
    text_opacity: float = 0.9,
    stroke_width: int = 1,
    stroke_color: str = 'black',
    vertical_margin: int = 10,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    combine_mode: bool = False,
    combine_layout: str = 'horizontal',
    combine_spacing: int = 10
) -> None:
    """向视频添加组合水印（图片 + 文字）

    Args:
        video_path: 输入视频文件路径
        output_path: 输出视频文件路径
        text: 水印文字内容（必需）
        watermark_path: 水印图片文件路径（可选）
        logo_position: Logo位置元组(horizontal, vertical)（分离模式使用）
        logo_opacity: Logo透明度
        logo_margin: Logo边距（分离模式使用）
        logo_width: Logo宽度（指定则覆盖自动缩放）
        logo_height: Logo高度（指定则覆盖自动缩放）
        logo_scale_factor: Logo相对于字体高度的缩放因子
        text_position: 文字位置元组(horizontal, vertical)（分离模式使用）
        font_size: 字体大小
        color: 文字颜色
        font_path: 字体文件路径
        text_opacity: 文字透明度
        stroke_width: 描边宽度
        stroke_color: 描边颜色
        vertical_margin: 文字垂直边距（分离模式使用）
        start_time: 水印开始时间
        end_time: 水印结束时间
        combine_mode: 是否合并Logo和文字为一张图片
        combine_layout: 合并布局 ('horizontal' 水平, 'vertical' 垂直)
        combine_spacing: 合并时的间距（像素）
    """
    # 加载视频
    video = VideoFileClip(video_path)

    # 设置持续时间
    if start_time is None:
        start_time = 0
    if end_time is None:
        end_time = video.duration

    # 准备视频层列表
    layers = [video]

    # 如果提供了logo且处于合并模式，将logo和文字合并为一张图片
    if watermark_path and os.path.exists(watermark_path) and combine_mode:
        # 创建文本图片并获取文本高度
        text_image, text_height = create_text_image(
            text=text,
            font_path=font_path,
            font_size=font_size,
            color=color,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            bg_padding=20
        )

        # 加载并调整logo大小
        from PIL import Image
        logo_image = Image.open(watermark_path)

        # 调整logo大小
        if logo_width or logo_height:
            # 使用指定尺寸
            if logo_width and logo_height:
                logo_image = logo_image.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            elif logo_width:
                ratio = logo_width / logo_image.width
                new_height = int(logo_image.height * ratio)
                logo_image = logo_image.resize((logo_width, new_height), Image.Resampling.LANCZOS)
            else:
                ratio = logo_height / logo_image.height
                new_width = int(logo_image.width * ratio)
                logo_image = logo_image.resize((new_width, logo_height), Image.Resampling.LANCZOS)
        else:
            # 自动缩放到文本高度
            target_height = int(text_height * logo_scale_factor)
            ratio = target_height / logo_image.height
            new_width = int(logo_image.width * ratio)
            logo_image = logo_image.resize((new_width, target_height), Image.Resampling.LANCZOS)

        # 合并logo和文字
        combined_image = combine_images(
            logo_image=logo_image,
            text_image=text_image,
            layout=combine_layout,
            spacing=combine_spacing
        )

        # 保存合并后的图片到临时文件
        temp_combined_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_combined_path = temp_combined_file.name
        temp_combined_file.close()
        combined_image.save(temp_combined_path, "PNG")

        # 创建水印剪辑
        watermark = ImageClip(temp_combined_path)
        watermark = watermark.with_start(start_time)
        watermark = watermark.with_end(end_time)
        watermark = watermark.with_duration(end_time - start_time)
        watermark = watermark.with_opacity(logo_opacity)  # 使用logo透明度作为整体透明度

        # 设置位置（使用logo_position）
        watermark = watermark.with_position(
            _get_position_function(video, watermark, logo_position, logo_margin)
        )

        # 添加到图层
        layers.append(watermark)

    elif watermark_path and os.path.exists(watermark_path):
        # 分离模式：分别处理logo和文字

        # 创建文本图片并获取文本高度
        text_image, text_height = create_text_image(
            text=text,
            font_path=font_path,
            font_size=font_size,
            color=color,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            bg_padding=20
        )

        # 保存文本图片到临时文件
        temp_text_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_text_path = temp_text_file.name
        temp_text_file.close()
        text_image.save(temp_text_path, "PNG")

        # 创建文字水印剪辑
        text_watermark = ImageClip(temp_text_path)
        text_watermark = text_watermark.with_start(start_time)
        text_watermark = text_watermark.with_end(end_time)
        text_watermark = text_watermark.with_duration(end_time - start_time)
        text_watermark = text_watermark.with_opacity(text_opacity)
        text_watermark = text_watermark.with_position(
            _get_position_function(video, text_watermark, text_position, vertical_margin)
        )
        layers.append(text_watermark)

        # 创建logo水印
        logo = ImageClip(watermark_path)

        # 调整logo大小
        if logo_width or logo_height:
            if logo_width and logo_height:
                logo = logo.resized((logo_width, logo_height))
            elif logo_width:
                logo = logo.resized(width=logo_width)
            else:
                logo = logo.resized(height=logo_height)
        else:
            target_height = int(text_height * logo_scale_factor)
            logo = logo.resized(height=target_height)

        logo = logo.with_start(start_time)
        logo = logo.with_end(end_time)
        logo = logo.with_duration(end_time - start_time)
        logo = logo.with_opacity(logo_opacity)
        logo = logo.with_position(
            _get_position_function(video, logo, logo_position, logo_margin)
        )
        layers.insert(1, logo)

    else:
        # 只有文字，没有logo
        # 创建文本图片
        text_image, _ = create_text_image(
            text=text,
            font_path=font_path,
            font_size=font_size,
            color=color,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            bg_padding=20
        )

        # 保存文本图片到临时文件
        temp_text_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_text_path = temp_text_file.name
        temp_text_file.close()
        text_image.save(temp_text_path, "PNG")

        # 创建文字水印剪辑
        text_watermark = ImageClip(temp_text_path)
        text_watermark = text_watermark.with_start(start_time)
        text_watermark = text_watermark.with_end(end_time)
        text_watermark = text_watermark.with_duration(end_time - start_time)
        text_watermark = text_watermark.with_opacity(text_opacity)
        text_watermark = text_watermark.with_position(
            _get_position_function(video, text_watermark, text_position, vertical_margin)
        )
        layers.append(text_watermark)

    # 合成视频
    final_video = CompositeVideoClip(layers, size=video.size)

    # 写出视频
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        threads=os.cpu_count(),
        logger=None
    )

    # 清理资源
    video.close()
    text_watermark.close()
    if watermark_path and os.path.exists(watermark_path):
        logo.close()
    final_video.close()

    # 删除临时文件
    try:
        os.remove(temp_text_path)
    except:
        pass


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
