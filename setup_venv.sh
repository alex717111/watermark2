#!/bin/bash
# Linux/macOS 虚拟环境设置脚本

echo "=========================================="
echo "视频水印工具 - 虚拟环境设置"
echo "=========================================="

# 检查Python3.12
if ! command -v python3.12 &> /dev/null; then
    echo "错误: 未找到Python3.12"
    exit 1
fi

echo "Python版本:"
python3.12 --version

# 创建虚拟环境
echo ""
echo "创建虚拟环境..."
python3.12 -m venv venv

if [ $? -ne 0 ]; then
    echo "错误: 虚拟环境创建失败"
    exit 1
fi

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo ""
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "安装项目依赖..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "错误: 依赖安装失败"
    deactivate
    exit 1
fi

echo ""
echo "=========================================="
echo "虚拟环境设置完成！"
echo "=========================================="
echo ""
echo "激活虚拟环境:"
echo "  source venv/bin/activate"
echo ""
echo "退出虚拟环境:"
echo "  deactivate"
echo ""
echo "测试工具:"
echo "  python main.py --help"
echo ""
echo "打包应用:"
echo "  cd build && ./build_linux.sh"
echo "=========================================="

# 保持激活状态
echo ""
echo "虚拟环境已激活，可以开始使用！"
