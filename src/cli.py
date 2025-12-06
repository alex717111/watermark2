"""Command-line interface for video watermark tool."""

import logging
import os
import sys
from pathlib import Path

import click

from .watermark import add_image_watermark
from .watermark.text_watermark_v2 import add_text_watermark as add_text_watermark_v2
from .insert import insert_video
from .logger_config import setup_logger, get_logger

# 设置日志
logger = setup_logger('video_watermark')


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


@click.group(invoke_without_command=True)
@click.version_option(version='1.0.0', prog_name='Video Watermark Tool')
@click.pass_context
def cli(ctx):
    """视频水印工具 - 添加水印和插入视频片段

    不输入任何命令将启动图形界面
    """
    # 如果没有提供子命令，启动 UI
    if ctx.invoked_subcommand is None:
        ui()


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
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help='日志级别（默认：INFO）')
def watermark(input, output, watermark, position, opacity, margin,
              start_time, end_time, width, height, log_level):
    """向视频添加图片水印"""
    # 设置日志级别
    logger.setLevel(getattr(logging, log_level))
    logger.info("=" * 60)
    logger.info("开始处理：图片水印")
    logger.info(f"输入文件: {input}")
    logger.info(f"水印文件: {watermark}")
    logger.info(f"输出文件: {output}")

    try:
        # 检查输入文件
        if not os.path.isfile(input):
            error_msg = f'错误：输入文件不存在: {input}'
            logger.error(error_msg)
            click.echo(f'{error_msg}', err=True)
            sys.exit(1)

        if not os.path.isfile(watermark):
            error_msg = f'错误：水印文件不存在: {watermark}'
            logger.error(error_msg)
            click.echo(f'{error_msg}', err=True)
            sys.exit(1)

        logger.debug("输入文件验证通过")

        # 转换位置参数
        position_h, position_v = POSITIONS[position]
        logger.debug(f"位置: {position} -> ({position_h}, {position_v})")

        # 转换时间
        start_sec = _time_str_to_seconds(start_time)
        end_sec = _time_str_to_seconds(end_time) if end_time else None
        logger.debug(f"时间范围: {start_sec}s - {end_sec}s")

        click.echo(f'正在添加水印到视频...')
        click.echo(f'  输入: {input}')
        click.echo(f'  水印: {watermark}')
        click.echo(f'  位置: {position}')
        click.echo(f'  透明度: {opacity}')
        click.echo(f'  输出: {output}')

        logger.info(f"位置: {position}")
        logger.info(f"透明度: {opacity}")
        logger.info("开始调用处理函数...")

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

        logger.info("处理完成")
        click.echo(f'✅ 水印添加成功: {output}')

    except Exception as e:
        error_msg = f'处理失败: {str(e)}'
        logger.exception(error_msg)
        click.echo(f'❌ 错误: {str(e)}', err=True)
        sys.exit(1)
    finally:
        logger.info("=" * 60)


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
@click.option('--vertical-margin', type=int, default=10,
              help='上下垂直留空（像素，默认：10），避免字母上下延被截断')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help='日志级别（默认：INFO）')
def watermark_text(input, output, text, position, font_size, color, font,
                   opacity, stroke_width, stroke_color, start_time, end_time, vertical_margin, log_level):
    """向视频添加文字水印"""
    # 设置日志级别
    logger.setLevel(getattr(logging, log_level))
    logger.info("=" * 60)
    logger.info("开始处理：文字水印")
    logger.info(f"输入文件: {input}")
    logger.info(f"水印文字: {text}")
    logger.info(f"输出文件: {output}")

    try:
        # 检查输入文件
        if not os.path.isfile(input):
            error_msg = f'错误：输入文件不存在: {input}'
            logger.error(error_msg)
            click.echo(f'{error_msg}', err=True)
            sys.exit(1)

        if font and not os.path.isfile(font):
            error_msg = f'错误：字体文件不存在: {font}'
            logger.error(error_msg)
            click.echo(f'{error_msg}', err=True)
            sys.exit(1)

        logger.debug("输入文件验证通过")

        # 转换位置参数
        position_h, position_v = POSITIONS[position]
        logger.debug(f"位置: {position} -> ({position_h}, {position_v})")

        # 转换时间
        start_sec = _time_str_to_seconds(start_time)
        end_sec = _time_str_to_seconds(end_time) if end_time else None
        logger.debug(f"时间范围: {start_sec}s - {end_sec}s")

        click.echo(f'正在添加文字水印到视频...')
        click.echo(f'  输入: {input}')
        click.echo(f'  文字: {text}')
        click.echo(f'  位置: {position}')
        click.echo(f'  大小: {font_size}px')
        click.echo(f'  垂直留空: {vertical_margin}px')
        click.echo(f'  输出: {output}')

        logger.info(f"位置: {position}")
        logger.info(f"字体大小: {font_size}px")
        logger.info(f"颜色: {color}")
        if font:
            logger.info(f"字体: {font}")
        logger.info(f"透明度: {opacity}")
        logger.info(f"垂直留空: {vertical_margin}px")

        # 调用文字水印函数（使用PIL实现）
        add_text_watermark_v2(
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
            end_time=end_sec,
            margin=vertical_margin
        )

        logger.info("处理完成")
        click.echo(f'✅ 文字水印添加成功: {output}')

    except Exception as e:
        error_msg = f'处理失败: {str(e)}'
        logger.exception(error_msg)
        click.echo(f'❌ 错误: {str(e)}', err=True)
        sys.exit(1)
    finally:
        logger.info("=" * 60)


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
              help='交叉淡入淡出时长（秒）')
@click.option('--seamless', is_flag=True, default=True,
              help='无缝插入模式（无交叉淡入淡出，直接拼接）[默认启用]')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help='日志级别（默认：INFO）')
def insert(main, insert, output, position, audio_mode, crossfade, seamless, log_level):
    """将视频插入到主视频的指定位置"""
    # 设置日志级别
    logger.setLevel(getattr(logging, log_level))
    logger.info("=" * 60)
    logger.info("开始处理：插入视频")
    logger.info(f"主视频: {main}")
    logger.info(f"插入视频: {insert}")
    logger.info(f"输出文件: {output}")

    try:
        # 检查输入文件
        for f in [main, insert]:
            if not os.path.isfile(f):
                error_msg = f'错误：文件不存在: {f}'
                logger.error(error_msg)
                click.echo(f'{error_msg}', err=True)
                sys.exit(1)

        logger.debug("输入文件验证通过")

        # 转换插入位置
        insert_pos = _time_str_to_seconds(position)
        logger.debug(f"插入位置: {position} -> {insert_pos}秒")

        click.echo(f'正在插入视频...')
        click.echo(f'  主视频: {main}')
        click.echo(f'  插入视频: {insert}')
        click.echo(f'  位置: {position}（{insert_pos}秒）')
        click.echo(f'  音频模式: {audio_mode}')
        if not seamless:
            click.echo(f'  模式: 有缝插入（带过渡效果）')
        elif crossfade > 0:
            click.echo(f'  模式: 交叉淡入淡出（{crossfade}秒）')
        else:
            click.echo(f'  模式: 无缝插入（直接拼接）')
        click.echo(f'  输出: {output}')

        logger.info(f"插入位置: {insert_pos}秒")
        logger.info(f"音频模式: {audio_mode}")
        if crossfade > 0:
            logger.info(f"交叉淡入淡出: {crossfade}秒")

        # 调用视频插入函数
        insert_video(
            main_video_path=main,
            insert_video_path=insert,
            output_path=output,
            insert_position=insert_pos,
            audio_mode=audio_mode,
            crossfade_duration=crossfade,
            seamless=seamless
        )

        logger.info("处理完成")
        click.echo(f'✅ 视频插入成功: {output}')

    except Exception as e:
        error_msg = f'处理失败: {str(e)}'
        logger.exception(error_msg)
        click.echo(f'❌ 错误: {str(e)}', err=True)
        sys.exit(1)
    finally:
        logger.info("=" * 60)


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


@cli.command()
def ui():
    """启动图形界面（PyQt6）"""
    try:
        from .ui_app import main as ui_main
        ui_main()
    except ImportError as e:
        click.echo('❌ 错误: 无法启动UI界面', err=True)
        click.echo(f'原因: {str(e)}', err=True)
        click.echo('', err=True)
        click.echo('解决方法:', err=True)
        click.echo('  1. 确保已激活虚拟环境', err=True)
        click.echo('  2. 安装PyQt6: pip install PyQt6', err=True)
        click.echo('  3. 重新安装依赖: pip install -r requirements.txt', err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
