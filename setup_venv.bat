@echo off
REM Windows 虚拟环境设置脚本

echo ========================================
echo 视频水印工具 - 虚拟环境设置
echo ========================================

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    exit /b 1
)

echo Python版本:
python --version

REM 创建虚拟环境
echo.
echo 创建虚拟环境...
python -m venv venv

if errorlevel 1 (
    echo 错误: 虚拟环境创建失败
    exit /b 1
)

REM 激活虚拟环境
echo.
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo.
echo 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo.
echo 安装项目依赖...
pip install -r requirements.txt

if errorlevel 1 (
    echo 错误: 依赖安装失败
    call deactivate
    exit /b 1
)

echo.
echo ========================================
echo 虚拟环境设置完成！
echo ========================================
echo.
echo 激活虚拟环境:
echo   venv\Scripts\activate.bat
echo.
echo 退出虚拟环境:
echo   deactivate
echo.
echo 测试工具:
echo   python main.py --help
echo.
echo 打包应用:
echo   cd build ^&^& build_windows.bat
echo ========================================

REM 保持激活状态
echo.
echo 虚拟环境已激活，可以开始使用！
