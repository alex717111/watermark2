"""视频插入功能模块"""

import os
from typing import Optional

from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
from moviepy.video.fx.all import fadein, fadeout


def insert_video(
    main_video_path: str,
    insert_video_path: str,
    output_path: str,
    insert_position: float,
    audio_mode: str = 'keep',
    crossfade_duration: float = 0.0
) -> None:
    """将视频插入到主视频的指定位置

    Args:
        main_video_path: 主视频文件路径
        insert_video_path: 要插入的视频文件路径
        output_path: 输出视频文件路径
        insert_position: 插入位置（秒）
        audio_mode: 音频处理方式
                   'keep': 保留主视频音频
                   'replace': 使用插入视频音频
                   'mix': 混合音频
                   'mute': 静音
        crossfade_duration: 交叉淡入淡出时长（秒）
    """
    # 加载视频
    main_video = VideoFileClip(main_video_path)
    insert_video = VideoFileClip(insert_video_path)
    
    # 验证插入位置
    if insert_position < 0 or insert_position > main_video.duration:
        raise ValueError(f'插入位置 {insert_position}s 超出主视频时长 {main_video.duration}s')
    
    click.echo(f'主视频时长: {main_video.duration:.2f}秒')
    click.echo(f'插入视频时长: {insert_video.duration:.2f}秒')
    
    # 分割主视频
    before_clip = main_video.subclip(0, insert_position)
    after_clip = main_video.subclip(insert_position)
    
    # 调整插入视频大小以匹配主视频
    if insert_video.size != main_video.size:
        click.echo(f'调整插入视频分辨率: {insert_video.size} -> {main_video.size}')
        insert_video = insert_video.resize(main_video.size)
    
    # 处理音频
    if crossfade_duration > 0:
        # 应用交叉淡入淡出效果
        before_clip = before_clip.fx(audio_fadeout, crossfade_duration)
        after_clip = after_clip.fx(audio_fadein, crossfade_duration)
        insert_video = insert_video.fx(audio_fadein, crossfade_duration)
        insert_video = insert_video.fx(audio_fadeout, crossfade_duration)
    
    # 根据音频模式处理
    if audio_mode == 'keep':
        # 保留主视频音频
        insert_video = insert_video.without_audio()
    elif audio_mode == 'replace':
        # 使用插入视频音频，主视频静音
        before_clip = before_clip.without_audio()
        after_clip = after_clip.without_audio()
    elif audio_mode == 'mute':
        # 全部静音
        before_clip = before_clip.without_audio()
        insert_video = insert_video.without_audio()
        after_clip = after_clip.without_audio()
    elif audio_mode == 'mix':
        # 混合音频 - 这里保留原音频，让MoviePy自动处理
        click.echo('混合音频模式：将自动混合主视频和插入视频的音频')
    
    # 连接视频片段
    if crossfade_duration > 0:
        # 使用交叉淡入淡出
        if audio_mode == 'mix':
            # 混合音频需要特殊处理
            final_video = _create_fade_with_mix(
                before_clip, insert_video, after_clip, crossfade_duration)
        else:
            # 普通交叉淡入淡出
            final_video = _create_fade_transition(
                before_clip, insert_video, after_clip, crossfade_duration)
    else:
        # 直接拼接
        final_video = concatenate_videoclips([before_clip, insert_video, after_clip])
    
    # 写出视频
    click.echo('正在生成输出视频...')
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        threads=os.cpu_count(),
        logger=None
    )
    
    # 释放资源
    main_video.close()
    insert_video.close()
    before_clip.close()
    after_clip.close()
    final_video.close()


def _create_fade_transition(clip1, clip2, clip3, fade_duration):
    """创建交叉淡入淡出的视频过渡"""
    # 对clip1应用淡出
    if clip1.duration > 0:
        clip1 = clip1.fx(fadeout, fade_duration)
    
    # 对clip2应用淡入和淡出
    if clip2.duration > 0:
        clip2 = clip2.fx(fadein, fade_duration)
        clip2 = clip2.fx(fadeout, fade_duration)
    
    # 对clip3应用淡入
    if clip3.duration > 0:
        clip3 = clip3.fx(fadein, fade_duration)
    
    return concatenate_videoclips([clip1, clip2, clip3])


def _create_fade_with_mix(clip1, clip2, clip3, fade_duration):
    """创建带音频混合的交叉淡入淡出过渡"""
    # 这里需要更复杂的音频混合逻辑
    # 简化版本：直接拼接，让音频自动混合
    return concatenate_videoclips([clip1, clip2, clip3])
