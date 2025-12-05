#!/usr/bin/env python3
"""
UI功能简单测试

运行此脚本测试UI是否正常工作：
    python3 test_ui.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.ui.main_window import VideoWatermarkWindow
    from PyQt6.QtWidgets import QApplication

    print("✅ UI模块导入成功")
    print("✅ PyQt6已正确安装")

    # 创建应用但不显示窗口（测试用）
    app = QApplication(sys.argv)
    window = VideoWatermarkWindow()

    print("✅ 主窗口创建成功")
    print("✅ UI基本功能正常")

    print("\n" + "="*60)
    print("UI测试通过！")
    print("可通过以下命令启动完整UI界面：")
    print("  python3 main.py ui")
    print("="*60)

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n请确保已安装PyQt6:")
    print("  pip install PyQt6")
    sys.exit(1)
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
