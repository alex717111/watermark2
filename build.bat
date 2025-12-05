@echo off
REM VideoWatermarkTool - 完整打包脚本 (Windows)
REM 自动下载 Python 3.12、安装依赖并生成 exe

setlocal EnableDelayedExpansion

echo ========================================
echo 视频水印工具 - 一键打包脚本
echo ========================================

REM 检查管理员权限（某些操作可能需要）
net session >nul 2>&1
if errorlevel 1 (
    echo 注意: 脚本未以管理员权限运行
    echo        如果安装 Python 失败，请以管理员身份运行
    echo.
)

REM 检查Python是否已安装
:CHECK_PYTHON
echo 检查 Python 安装...
python --version >nul 2>&1
if not errorlevel 1 (
    python --version | findstr "3.12" >nul 2>&1
    if not errorlevel 1 (
        echo ✅ 已安装 Python 3.12
        goto :PYTHON_OK
    ) else (
        echo ⚠️  已安装 Python，但不是 3.12 版本
        python --version
        echo    正在检查 3.12 版本...
        py -3.12 --version >nul 2>&1
        if not errorlevel 1 (
            echo ✅ 找到 Python 3.12
            set PYTHON_CMD=py -3.12
            goto :PYTHON_OK
        )
    )
)

REM 尝试检查 py 启动器
py --version >nul 2>&1
if not errorlevel 1 (
    echo 检查 py 启动器...
    py -3.12 --version >nul 2>&1
    if not errorlevel 1 (
        echo ✅ 找到 Python 3.12 (py -3.12)
        set PYTHON_CMD=py -3.12
        goto :PYTHON_OK
    )
)

echo ❌ 未找到 Python 3.12
echo 正在下载 Python 3.12...

REM 下载 Python 3.12
certutil -urlcache -split -f https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe python-installer.exe
if errorlevel 1 (
    echo ❌ 下载 Python 失败
    echo    请检查网络连接或手动下载:
    echo    https://www.python.org/downloads/ release/3.12.3/
    pause
    exit /b 1
)

echo ✅ Python 下载完成
echo 正在安装 Python 3.12...
start /wait python-installer.exe /passive InstallAllUsers=0 Include_launcher=1 PrependPath=1 Include_test=0

if errorlevel 1 (
    echo ❌ Python 安装失败
    echo    请以管理员身份运行此脚本
    pause
    exit /b 1
)

echo ✅ Python 3.12 安装完成
set PYTHON_CMD=python

REM 删除安装程序
del python-installer.exe

:PYTHON_OK
REM Python 环境检查完成
echo.

REM 检查 FFmpeg
echo 检查 FFmpeg 安装...
ffmpeg -version >nul 2>&1
if not errorlevel 1 (
    echo ✅ FFmpeg 已安装
    set FFMPEG_AVAILABLE=1
    goto :FFMPEG_OK
)

REM 检查是否已经下载了 FFmpeg
if exist resources\ffmpeg\bin\ffmpeg.exe (
    echo ✅ FFmpeg 已下载 (resources\ffmpeg)
    set FFMPEG_AVAILABLE=1
    goto :FFMPEG_OK
)

echo ⚠️  未检测到 FFmpeg，正在自动下载...

REM 创建 resources 目录
if not exist resources mkdir resources

REM 下载 FFmpeg (Windows 版本)
echo 正在下载 FFmpeg (约 80MB，可能需要几分钟)...
certutil -urlcache -split -f https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip ffmpeg.zip

if errorlevel 1 (
    echo ❌ FFmpeg 下载失败
    echo    尝试备用下载地址...
    certutil -urlcache -split -f https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z ffmpeg.7z

    if errorlevel 1 (
        echo ❌ 备用下载也失败
        echo    请手动下载 FFmpeg：https://ffmpeg.org/download.html
        echo    并解压到 resources\ffmpeg 目录
        set FFMPEG_AVAILABLE=0
        goto :FFMPEG_OK
    ) else (
        echo ✅ 下载完成 (7z 格式)
        echo 解压 FFmpeg...
        if not exist 7z.exe (
            echo 正在下载 7-Zip 解压工具...
            certutil -urlcache -split -f https://www.7-zip.org/a/7zr.exe 7zr.exe
        )
        7zr x ffmpeg.7z -oresources\temp -y >nul 2>&1
        if errorlevel 1 (
            echo ❌ 解压失败
            set FFMPEG_AVAILABLE=0
            del ffmpeg.7z
            goto :FFMPEG_OK
        )
        for /d %%I in (resources\temp\ffmpeg-*) do (
            move "%%I" resources\ffmpeg >nul 2>&1
        )
        rmdir /s /q resources\temp
        del ffmpeg.7z
        if exist 7zr.exe del 7zr.exe
    )
) else (
    echo ✅ 下载完成 (zip 格式)
    echo 解压 FFmpeg...
    powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'resources\temp' -Force"
    if errorlevel 1 (
        echo ❌ 解压失败
        set FFMPEG_AVAILABLE=0
        del ffmpeg.zip
        goto :FFMPEG_OK
    )

    REM 查找解压后的目录
    for /d %%I in (resources\temp\ffmpeg-master-*) do (
        move "%%I" resources\ffmpeg >nul 2>&1
    )
    rmdir /s /q resources\temp
    del ffmpeg.zip
)

REM 验证 FFmpeg
if exist resources\ffmpeg\bin\ffmpeg.exe (
    echo ✅ FFmpeg 准备完成
    set FFMPEG_AVAILABLE=1
) else (
    echo ❌ FFmpeg 准备失败
    set FFMPEG_AVAILABLE=0
)

:FFMPEG_OK

REM 创建虚拟环境
echo.
echo 创建虚拟环境...
if exist venv (
    echo ✅ 虚拟环境已存在，跳过创建
) else (
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo ❌ 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建完成
)

REM 激活虚拟环境
echo.
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级 pip
echo.
echo 升级 pip...
python -m pip install --upgrade pip

REM 安装 PyInstaller（如果不在依赖中）
echo.
echo 安装 PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    pip install pyinstaller
) else (
    echo ✅ PyInstaller 已安装
)

REM 安装项目依赖
echo.
echo 安装项目依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

REM 打包应用
echo.
echo ========================================
echo 开始打包应用...
echo ========================================

REM 创建 dist 目录（如果不存在）
if not exist dist mkdir dist

REM 使用 PyInstaller 打包
pyinstaller --clean --noconfirm VideoWatermarkTool.spec

if errorlevel 1 (
    echo ❌ 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 打包完成！
echo ========================================
echo.

REM 显示生成的文件
if exist "dist\VideoWatermarkTool.exe" (
    echo 生成的可执行文件:
    echo   %CD%\dist\VideoWatermarkTool.exe
    echo.
    echo 文件大小:
    for %%I in ("dist\VideoWatermarkTool.exe") do echo   %%~zI bytes (%%~zI/1024/1024 MB)
    echo.
    echo 说明:
    echo   这是命令行版本，支持所有 CLI 功能
    echo   如需使用图形界面，请在打包后手动使用: VideoWatermarkTool.exe ui
    echo.
) else (
    echo ⚠️  生成的文件不存在，可能打包失败
)

REM 检查是否包含 FFmpeg
echo 依赖检查:
if exist "dist\_internal\imageio_ffmpeg\ffmpeg-win64-v4.2.2.exe" (
    echo ✅ FFmpeg 已嵌入 (通过 imageio-ffmpeg)
) else if %FFMPEG_AVAILABLE%==1 (
    if exist "dist\_internal\ffmpeg\ffmpeg.exe" (
        echo ✅ FFmpeg 已嵌入 (完整版)
    ) else (
        echo ⚠️  FFmpeg 未完全嵌入，但程序仍可运行
        echo    （使用了 imageio_ffmpeg 的回退机制）
    )
) else (
    echo ⚠️  FFmpeg 未找到，程序可能无法处理视频
)

echo.
echo 使用说明:
echo   1. 将 dist 目录复制到目标机器
echo   2. 运行: VideoWatermarkTool.exe
echo   3. 无需额外安装任何依赖！
echo.
echo 测试命令:
echo   VideoWatermarkTool.exe --help
echo   VideoWatermarkTool.exe ui
echo.

REM 生成使用说明文档
echo 生成使用说明...
(
echo    视频水印工具 - 使用说明
echo ========================================
echo.
echo 打包信息:
echo - 版本: %DATE% %TIME%
echo - Python: %PYTHON_CMD%
echo.
echo 部署步骤:
echo 1. 将 dist 目录复制到目标 Windows 机器
echo 2. 直接运行 VideoWatermarkTool.exe
echo 3. 无需安装任何额外依赖！
echo.
echo 系统要求:
echo - Windows 7 或更高版本
echo - 无需安装 Python、FFmpeg 或其他依赖
echo.
echo 包含的组件:
if %FFMPEG_AVAILABLE%==1 (
echo - ✅ FFmpeg (视频处理引擎，已内置)
) else (
echo - ⚠️  FFmpeg (可能使用备用方案)
)
echo - ✅ Python 3.12 运行时
echo - ✅ 所有 Python 依赖包
echo - ✅ 图形界面支持 (PyQt6)
echo.
echo 使用示例:
echo 1. 查看命令帮助: VideoWatermarkTool.exe --help
echo 2. 启动图形界面: VideoWatermarkTool.exe ui
echo 3. 添加图片水印: VideoWatermarkTool.exe watermark -i input.mp4 -o output.mp4 -w watermark.png
echo 4. 添加文字水印: VideoWatermarkTool.exe watermark-text -i input.mp4 -o output.mp4 -t "Copyright"
echo 5. 插入视频片段: VideoWatermarkTool.exe insert -m main.mp4 -i insert.mp4 -o output.mp4 -p 30
echo.
echo 文件说明:
echo - VideoWatermarkTool.exe: 主程序文件
echo - _internal/: 程序依赖的库文件 (不要删除)
echo.
echo 技术支持:
echo 如有问题，请确保:
echo 1. 所有文件都在同一目录下
echo 2. 不要删除 _internal 文件夹
echo 3. 以管理员身份运行 (某些系统可能需要)
echo.
echo 重要提示:
echo - 全尺寸水印模式: 水印图片与视频同尺寸，推荐用法
echo - 缩放模式: 使用 --scaled 参数
echo - 支持的格式: MP4, AVI, MOV, MKV, WebM 等
echo.
echo ========================================
echo    完全独立运行，无需额外安装！
echo ========================================
) > dist\README_部署说明.txt

echo.
echo 已生成部署说明文档: dist\README_部署说明.txt
echo.

echo ========================================
echo 打包脚本执行完成
echo ========================================
echo.
echo 提示:
echo - 此脚本可以重复运行，会自动跳过已完成的步骤
echo - 如果代码有更新，直接运行此脚本即可重新打包
echo.

pause
endlocal
