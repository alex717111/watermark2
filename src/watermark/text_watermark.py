"""文字水印功能模块"""

import os
from typing import Optional, Tuple

from moviepy import VideoFileClip, TextClip, CompositeVideoClip


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
    end_time: Optional[float] = None
) -> None:
    """向视频添加文字水印

    Args:
        video_path: 输入视频文件路径
        text: 水印文字内容
        output_path: 输出视频文件路径
        position: 水印位置，格式为(horizontal, vertical)
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
    """
    # 加载视频
    video = VideoFileClip(video_path)
    
    # 创建文字水印
    if font_path and os.path.exists(font_path):
        # 使用指定字体
        watermark = TextClip(
            text=text,
            font_size=font_size,
            font=font_path,
            color=color,
            stroke_width=stroke_width,
            stroke_color=stroke_color
        )
    else:
        # 使用默认字体
        watermark = TextClip(
            text=text,
            font_size=font_size,
            color=color,
            stroke_width=stroke_width,
            stroke_color=stroke_color
        )
    
    # 设置水印持续时间
    if start_time is None:
        start_time = 0
    if end_time is None:
        end_time = video.duration
    
    watermark = watermark.with_start(start_time)
    watermark = watermark.with_end(end_time)
    watermark = watermark.with_duration(end_time - start_time)
    
    # 设置水印位置
    position_func = _get_position_function(video, watermark, position, margin=15)
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


def _get_position_function(
    video: VideoFileClip,
    watermark: TextClip,
    position: Tuple[str, str],
    margin: int
):
    """获取水印位置函数

    Args:
        video: 视频对象
        watermark: 水印对象
        position: 位置元组(horizontal, vertical)
        margin: 边距

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
            y = margin
        elif vertical == 'center':
            y = (video.h - watermark.h) / 2
        else:  # bottom
            y = video.h - watermark.h - margin
        
        return (x, y)
    
    return position_func
