"""日志配置模块

提供统一的日志配置，支持文件轮转和控制台输出
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = None, log_level: str = "INFO") -> logging.Logger:
    """设置并获取日志记录器

    Args:
        name: 日志记录器名称，如果为None则返回根记录器
        log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）

    Returns:
        配置好的日志记录器
    """
    # 获取程序所在目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        prog_dir = Path(sys.executable).parent
    else:
        # 如果是脚本运行
        prog_dir = Path(__file__).parent.parent

    # 创建日志目录
    log_dir = prog_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    # 日志文件路径
    log_file = log_dir / "video_watermark.log"

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # 如果记录器已经有处理器，则先清除
    if logger.handlers:
        logger.handlers.clear()

    # 日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件处理器（轮转日志）
    # maxBytes=2MB, backupCount=0表示只保留一个文件
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=2 * 1024 * 1024,  # 2MB
        backupCount=0,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器
    """
    return logging.getLogger(name)
