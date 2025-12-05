#!/usr/bin/env python3
"""UI应用程序入口

使用方法：
    python main.py ui          # 启动图形界面
    python src/ui_app.py       # 直接启动UI
"""

import sys
import os

# 将项目根目录添加到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.main_window import VideoWatermarkWindow
    from PyQt6.QtWidgets import QApplication
except ImportError as e:
    print(f"错误：缺少必要的依赖包: {e}")
    print("请确保已安装PyQt6:")
    print("  pip install PyQt6")
    sys.exit(1)


def main():
    """UI应用主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("视频水印工具")
    app.setOrganizationName("VideoWatermark")

    # 设置应用程序样式
    app.setStyle("Fusion")

    # 创建并显示主窗口
    window = VideoWatermarkWindow()
    window.show()

    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
