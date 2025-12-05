"""CLI测试"""

import os
import tempfile
import pytest
from click.testing import CliRunner

# 将src目录添加到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cli import cli


def test_help():
    """测试帮助命令"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert '视频水印工具' in result.output


def test_positions():
    """测试位置列表命令"""
    runner = CliRunner()
    result = runner.invoke(cli, ['positions'])
    assert result.exit_code == 0
    assert 'top-left' in result.output


if __name__ == '__main__':
    test_help()
    test_positions()
    print("所有测试通过！")
