#!/usr/bin/env python3
"""主入口文件"""

import sys
import os

# 将src目录添加到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cli import cli

if __name__ == '__main__':
    cli()
