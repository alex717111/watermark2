"""图片水印功能模块"""

import os
from typing import Optional, Tuple

from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.video.fx.all import mask_color


def add_image_watermark(
    video_path: str,
    watermark_path: str,
    output_path: str,
    position: Tuple[str, str] = ('right', 'bottom'),
    opacity: float = 0.8,
    margin: int = 10,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> None:
    """向视频添加图片水印

    Args:
        video_path: 输入视频文件路径
        watermark_path: 水印图片文件路径（支持PNG透明背景）
        output_path: 输出视频文件路径
        position: 水印位置，格式为(horizontal, vertical)
                 horizontal: 'left', 'center', 'right'
                 vertical: 'top', 'center', 'bottom'
        opacity: 水印透明度（0.0-1.0）
        margin: 水印边距（像素）
        start_time: 水印开始显示时间（秒），默认从视频开始
        end_time: 水印结束显示时间（秒），默认到视频结束
        width: 水印宽度（像素），保持宽高比
        height: 水印高度（像素），保持宽高比
    """
    # 加载视频
    video = VideoFileClip(video_path)
    
    # 加载水印图片
    watermark = ImageClip(watermark_path)
    
    # 调整水印大小
    if width or height:
        if width and height:
            watermark = watermark.resize((width, height))
        elif width:
            watermark = watermark.resize(width=width)
        else:
            watermark = watermark.resize(height=height)
    else:
        # 默认调整水印大小为视频宽度的1/8
        watermark = watermark.resize(width=int(video.w / 8))
    
    # 设置水印持续时间
    if start_time is None:
        start_time = 0
    if end_time is None:
        end_time = video.duration
    
    watermark = watermark.set_start(start_time)
    watermark = watermark.set_end(end_time)
    watermark = watermark.set_duration(end_time - start_time)
    
    # 设置水印位置
    position_func = _get_position_function(video, watermark, position, margin)
    watermark = watermark.set_position(position_func)
    
    # 设置透明度
    watermark = watermark.set_opacity(opacity)
    
    # 合成视频
    final_video = CompositeVideoClip([video, watermark], size=video.size)
    
    # 写出视频
    # 使用原视频的编解码器参数
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        threads=os.cpu_count(),
        logger=None  # 禁用日志输出
    )
    
    # 释放资源
    video.close()
    watermark.close()
    final_video.close()


def _get_position_function(
    video: VideoFileClip,
    watermark: ImageClip,
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
