#!/usr/bin/env python3
"""Main entry point - runs UI by default"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == '__main__':
    # Import and run UI directly
    try:
        from src.ui_app import main as ui_main
        ui_main()
    except ImportError as e:
        print('❌ 错误: 无法启动UI界面')
        print(f'原因: {str(e)}')
        print('')
        print('解决方法:')
        print('  1. 确保已激活虚拟环境')
        print('  2. 安装PyQt6: pip install PyQt6')
        print('  3. 重新安装依赖: pip install -r requirements.txt')
        sys.exit(1)
    except Exception as e:
        print(f'❌ 启动失败: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
