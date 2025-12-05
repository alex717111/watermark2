"""文字水印功能模块"""

import os
from typing import Optional, Tuple

from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip


def add_text_watermark(
    video_path: str,
    text: str,
    output_path: str,
    position: Tuple[str, str] = ('right', 'bottom'),
    font_size: int = 24,
    color: str = 'white',
    font_path: Optional[str] = None,
    opacity: float = 0.9,
    stroke_width: int = 1,
    stroke_color: str = 'black',
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    vertical_margin: int = 10
) -> None:
    """向视频添加文字水印

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
        stroke_width: 描边宽度（0表示无描边）
        stroke_color: 描边颜色
        start_time: 水印开始显示时间（秒），默认从视频开始
        end_time: 水印结束显示时间（秒），默认到视频结束
        vertical_margin: 上下垂直留空（像素，默认：10），避免因字母上下延被截断
    """
    # 加载视频
    video = VideoFileClip(video_path)

    # 创建文字水印（先创建，获取尺寸）
    if font_path and os.path.exists(font_path):
        # 使用指定字体
        text_clip = TextClip(
            text=text,
            font_size=font_size,
            font=font_path,
            color=color,
            stroke_width=stroke_width,
            stroke_color=stroke_color
        )
    else:
        # 使用默认字体
        text_clip = TextClip(
            text=text,
            font_size=font_size,
            color=color,
            stroke_width=stroke_width,
            stroke_color=stroke_color
        )

    # 获取文本尺寸
    text_w, text_h = text_clip.size

    # 创建背景层（比文本大一些，避免截断）
    # 高度增加 80% 给字母上下延留出足够空间（修复底部截断问题）
    bg_width = int(text_w * 1.2)  # 宽度增加 20%
    bg_height = int(text_h * 1.8)  # 高度增加 80%（原来是40%，现在增加到80%）
    background = ColorClip(
        size=(bg_width, bg_height),
        color=(0, 0, 0)  # 黑色背景
    )
    background = background.with_opacity(0)  # 设置背景为完全透明

    # 将文本居中放在背景上
    text_clip = text_clip.with_position('center')

    # 组合文本和背景
    watermark = CompositeVideoClip([background, text_clip], size=(bg_width, bg_height))
    
    # 设置水印持续时间
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
    position_func = _get_position_function(video, watermark, position, margin=15, vertical_margin=vertical_margin)
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
    
    # 释放资源
    video.close()
    watermark.close()
    final_video.close()


def _validate_position_tuple(position: Tuple[str, str]):
    """验证位置元组是否合法

    Args:
        position: 位置元组(horizontal, vertical)

    Raises:
        ValueError: 如果位置不合法
    """
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
    watermark: TextClip,
    position: Tuple[str, str],
    margin: int,
    vertical_margin: int = 10
):
    """获取水印位置函数

    Args:
        video: 视频对象
        watermark: 水印对象
        position: 位置元组(horizontal, vertical)
        margin: 边距（水平方向）
        vertical_margin: 垂直留空（避免因字母上下延被截断）

    Returns:
        位置函数
    """
    horizontal, vertical = position

    def position_func(t):
        # 计算水印位置
        if horizontal == 'left':
            x = margin
        elif horizontal == 'center':
            x = (video.w - watermark.w) / 2
        else:  # right
            x = video.w - watermark.w - margin

        if vertical == 'top':
            y = margin + vertical_margin
        elif vertical == 'center':
            y = (video.h - watermark.h) / 2
        else:  # bottom
            y = video.h - watermark.h - margin - vertical_margin

        return (x, y)
    
    return position_func
