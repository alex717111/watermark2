#!/usr/bin/env python3
"""主入口文件"""

import sys
import os

# 将项目根目录添加到系统路径
sys.path.insert(0, os.path.dirname(__file__))

# 使用 -m 参数运行src.cli模块来避免相对导入问题
if __name__ == '__main__':
    # 运行CLI模块
    import runpy
    runpy.run_module('src.cli', run_name='__main__')
