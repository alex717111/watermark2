"""Command-line interface for video watermark tool."""

import os
import sys
from pathlib import Path

import click

from .watermark import add_image_watermark, add_text_watermark
from .insert import insert_video


# 定义位置选项常量
POSITIONS = {
    'top-left': ('left', 'top'),
    'top-center': ('center', 'top'),
    'top-right': ('right', 'top'),
    'center-left': ('left', 'center'),
    'center': ('center', 'center'),
    'center-right': ('right', 'center'),
    'bottom-left': ('left', 'bottom'),
    'bottom-center': ('center', 'bottom'),
    'bottom-right': ('right', 'bottom'),
}

AUDIO_MODES = ['keep', 'replace', 'mix', 'mute']


@click.group()
@click.version_option(version='1.0.0', prog_name='Video Watermark Tool')
def cli():
    """视频水印工具 - 添加水印和插入视频片段"""
    pass


@cli.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True),
              help='输入视频文件路径')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='输出视频文件路径')
@click.option('--watermark', '-w', required=True, type=click.Path(exists=True),
              help='水印图片路径（支持PNG透明背景）')
@click.option('--position', '-p', default='bottom-right',
              type=click.Choice(list(POSITIONS.keys()), case_sensitive=False),
              help='水印位置（默认：bottom-right）')
@click.option('--opacity', type=click.FloatRange(0.0, 1.0), default=0.8,
              help='水印透明度 0.0-1.0（默认：0.8）')
@click.option('--margin', type=int, default=10,
              help='水印边距（像素，默认：10）')
@click.option('--start-time', '-s', type=str, default='0',
              help='水印开始时间（秒或HH:MM:SS，默认：0）')
@click.option('--end-time', '-e', type=str, default=None,
              help='水印结束时间（秒或HH:MM:SS，默认：视频结束）')
@click.option('--width', type=int, default=None,
              help='水印宽度（像素，保持宽高比）')
@click.option('--height', type=int, default=None,
              help='水印高度（像素，保持宽高比）')
def watermark(input, output, watermark, position, opacity, margin,
              start_time, end_time, width, height):
    """向视频添加图片水印"""
    try:
        # 检查输入文件
        if not os.path.isfile(input):
            click.echo(f'错误：输入文件不存在: {input}', err=True)
            sys.exit(1)
        
        if not os.path.isfile(watermark):
            click.echo(f'错误：水印文件不存在: {watermark}', err=True)
            sys.exit(1)
        
        # 转换位置参数
        position_h, position_v = POSITIONS[position]
        
        # 转换时间
        start_sec = _time_str_to_seconds(start_time)
        end_sec = _time_str_to_seconds(end_time) if end_time else None
        
        click.echo(f'正在添加水印到视频...')
        click.echo(f'  输入: {input}')
        click.echo(f'  水印: {watermark}')
        click.echo(f'  位置: {position}')
        click.echo(f'  输出: {output}')
        
        # 调用水印函数
        add_image_watermark(
            video_path=input,
            watermark_path=watermark,
            output_path=output,
            position=(position_h, position_v),
            opacity=opacity,
            margin=margin,
            start_time=start_sec,
            end_time=end_sec,
            width=width,
            height=height
        )
        
        click.echo(f'✅ 水印添加成功: {output}')
        
    except Exception as e:
        click.echo(f'❌ 错误: {str(e)}', err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True),
              help='输入视频文件路径')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='输出视频文件路径')
@click.option('--text', '-t', required=True, type=str,
              help='水印文字内容')
@click.option('--position', '-p', default='top-right',
              type=click.Choice(list(POSITIONS.keys()), case_sensitive=False),
              help='水印位置（默认：top-right）')
@click.option('--font-size', type=int, default=24,
              help='字体大小（默认：24）')
@click.option('--color', type=str, default='white',
              help='文字颜色（默认：white，支持颜色名称或十六进制如#FF0000）')
@click.option('--font', type=str, default=None,
              help='字体文件路径（TTF格式）')
@click.option('--opacity', type=click.FloatRange(0.0, 1.0), default=0.9,
              help='文字透明度 0.0-1.0（默认：0.9）')
@click.option('--stroke-width', type=int, default=1,
              help='描边宽度（默认：1，0表示无描边）')
@click.option('--stroke-color', type=str, default='black',
              help='描边颜色（默认：black）')
@click.option('--start-time', '-s', type=str, default='0',
              help='水印开始时间（秒或HH:MM:SS，默认：0）')
@click.option('--end-time', '-e', type=str, default=None,
              help='水印结束时间（秒或HH:MM:SS，默认：视频结束）')
def watermark_text(input, output, text, position, font_size, color, font,
                   opacity, stroke_width, stroke_color, start_time, end_time):
    """向视频添加文字水印"""
    try:
        # 检查输入文件
        if not os.path.isfile(input):
            click.echo(f'错误：输入文件不存在: {input}', err=True)
            sys.exit(1)
        
        if font and not os.path.isfile(font):
            click.echo(f'错误：字体文件不存在: {font}', err=True)
            sys.exit(1)
        
        # 转换位置参数
        position_h, position_v = POSITIONS[position]
        
        # 转换时间
        start_sec = _time_str_to_seconds(start_time)
        end_sec = _time_str_to_seconds(end_time) if end_time else None
        
        click.echo(f'正在添加文字水印到视频...')
        click.echo(f'  输入: {input}')
        click.echo(f'  文字: {text}')
        click.echo(f'  位置: {position}')
        click.echo(f'  大小: {font_size}px')
        click.echo(f'  输出: {output}')
        
        # 调用文字水印函数
        add_text_watermark(
            video_path=input,
            text=text,
            output_path=output,
            position=(position_h, position_v),
            font_size=font_size,
            color=color,
            font_path=font,
            opacity=opacity,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            start_time=start_sec,
            end_time=end_sec
        )
        
        click.echo(f'✅ 文字水印添加成功: {output}')
        
    except Exception as e:
        click.echo(f'❌ 错误: {str(e)}', err=True)
        sys.exit(1)


@cli.command()
@click.option('--main', '-m', required=True, type=click.Path(exists=True),
              help='主视频文件路径')
@click.option('--insert', '-i', required=True, type=click.Path(exists=True),
              help='要插入的视频文件路径')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='输出视频文件路径')
@click.option('--position', '-p', type=str, required=True,
              help='插入位置（秒或HH:MM:SS）')
@click.option('--audio-mode', type=click.Choice(AUDIO_MODES), default='keep',
              help='音频处理方式：keep（保留主音频）、replace（使用插入音频）、' +
                   'mix（混合音频）、mute（静音）')
@click.option('--crossfade', type=click.FloatRange(0.0, 5.0), default=0.0,
              help='交叉淡入淡出时长（秒，默认：0.0）')
def insert(main, insert, output, position, audio_mode, crossfade):
    """将视频插入到主视频的指定位置"""
    try:
        # 检查输入文件
        for f in [main, insert]:
            if not os.path.isfile(f):
                click.echo(f'错误：文件不存在: {f}', err=True)
                sys.exit(1)
        
        # 转换插入位置
        insert_pos = _time_str_to_seconds(position)
        
        click.echo(f'正在插入视频...')
        click.echo(f'  主视频: {main}')
        click.echo(f'  插入视频: {insert}')
        click.echo(f'  位置: {position}（{insert_pos}秒）')
        click.echo(f'  音频模式: {audio_mode}')
        click.echo(f'  输出: {output}')
        
        # 调用视频插入函数
        insert_video(
            main_video_path=main,
            insert_video_path=insert,
            output_path=output,
            insert_position=insert_pos,
            audio_mode=audio_mode,
            crossfade_duration=crossfade
        )
        
        click.echo(f'✅ 视频插入成功: {output}')
        
    except Exception as e:
        click.echo(f'❌ 错误: {str(e)}', err=True)
        sys.exit(1)


@cli.command()
def positions():
    """显示可用的水印位置选项"""
    click.echo('可用的水印位置：')
    click.echo('')
    for pos_name, (h, v) in POSITIONS.items():
        click.echo(f'  {pos_name:15s} - 水平: {h:8s}  垂直: {v}')


def _time_str_to_seconds(time_str):
    """将时间字符串转换为秒数
    
    支持格式：
    - 纯秒数：60
    - 时分秒：01:30:45
    - 分秒：30:45
    - 小时后缀：1.5h
    - 分钟后缀：30m
    - 秒后缀：45s
    """
    if time_str is None:
        return None
    
    time_str = str(time_str).strip()
    
    # 时间后缀
    if time_str.endswith('h'):
        return float(time_str[:-1]) * 3600
    elif time_str.endswith('m'):
        return float(time_str[:-1]) * 60
    elif time_str.endswith('s'):
        return float(time_str[:-1])
    
    # 时分秒格式
    parts = time_str.split(':')
    if len(parts) == 3:  # HH:MM:SS
        h, m, s = map(float, parts)
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:  # MM:SS
        m, s = map(float, parts)
        return m * 60 + s
    elif len(parts) == 1:  # 纯秒数
        return float(parts[0])
    else:
        raise ValueError(f'无效的时间格式: {time_str}')


if __name__ == '__main__':
    cli()
