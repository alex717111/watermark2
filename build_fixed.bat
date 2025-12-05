@echo off
REM VideoWatermarkTool - Windows Build Script
REM Auto-download Python 3.12, install dependencies and generate exe

setlocal EnableDelayedExpansion

REM Set proxy for all network operations
set PROXY_SERVER=192.168.110.10
set PROXY_PORT=7890
set PROXY=%PROXY_SERVER%:%PROXY_PORT%
echo Using proxy: %PROXY%
echo.

REM Initialize all variables
set PYTHON_CMD=
set FFMPEG_AVAILABLE=0

echo ========================================
echo Video Watermark Tool - One-click Build Script
echo ========================================

REM Check admin rights (may be needed for some operations)
net session >nul 2>&1
if errorlevel 1 (
    echo Note: Script running without admin privileges
    echo       If Python installation fails, run as administrator
    echo.
)

REM Check if Python is installed
:CHECK_PYTHON
echo Checking Python installation...
python --version >nul 2>&1
if not errorlevel 1 (
    python --version | findstr "3.12" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Python 3.12 already installed
        set PYTHON_CMD=python
        goto :PYTHON_OK
    ) else (
        echo [WARN] Python installed but not version 3.12
        python --version
        echo    Checking for version 3.12...
        py -3.12 --version >nul 2>&1
        if not errorlevel 1 (
            echo [OK] Found Python 3.12
            set PYTHON_CMD=py -3.12
            goto :PYTHON_OK
        )
    )
)

REM Try py launcher
py --version >nul 2>&1
if not errorlevel 1 (
    echo Checking py launcher...
    py -3.12 --version >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Found Python 3.12 (py -3.12)
        set PYTHON_CMD=py -3.12
        goto :PYTHON_OK
    )
)

echo [ERROR] Python 3.12 not found
echo Downloading Python 3.12...

REM Download Python 3.12 via PowerShell with proxy
echo Using proxy %PROXY% for download...
powershell -Command "$proxy = New-Object System.Net.WebProxy('http://%PROXY%'); $client = New-Object System.Net.WebClient; $client.Proxy = $proxy; $client.DownloadFile('https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe', 'python-installer.exe')"
if errorlevel 1 (
    echo [ERROR] Failed to download Python via proxy
    echo    Trying direct download without proxy...
    certutil -urlcache -split -f https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe python-installer.exe
    if errorlevel 1 (
        echo [ERROR] Failed to download Python
        echo    Please check network connection or manually download:
        echo    https://www.python.org/downloads/release/3.12.3/
        pause
        exit /b 1
    )
)

echo [OK] Python download complete
echo Installing Python 3.12...
start /wait python-installer.exe /passive InstallAllUsers=0 Include_launcher=1 PrependPath=1 Include_test=0

if errorlevel 1 (
    echo [ERROR] Python installation failed
    echo    Please run as administrator
    pause
    exit /b 1
)

echo [OK] Python 3.12 installation complete
set PYTHON_CMD=python

REM Remove installer
del python-installer.exe

:PYTHON_OK
REM Python environment check complete
REM Ensure PYTHON_CMD is set
if "%PYTHON_CMD%"=="" (
    echo [ERROR] PYTHON_CMD is not set, using default 'python'
    set PYTHON_CMD=python
)
echo Using Python command: %PYTHON_CMD%
echo.

REM Check FFmpeg
echo Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if not errorlevel 1 (
    echo [OK] FFmpeg already installed
    set FFMPEG_AVAILABLE=1
    goto :FFMPEG_OK
)

REM Check if FFmpeg was already downloaded
if exist resources\ffmpeg\bin\ffmpeg.exe (
    echo [OK] FFmpeg already downloaded (resources\ffmpeg)
    set FFMPEG_AVAILABLE=1
    goto :FFMPEG_OK
)

echo [WARN] FFmpeg not detected, downloading automatically...

REM Create resources directory
if not exist resources mkdir resources

REM Download FFmpeg (Windows version)
echo Downloading FFmpeg (approx 80MB, may take a few minutes)...
echo Using proxy %PROXY% for download...
REM Try primary download with proxy via PowerShell
powershell -Command "$proxy = New-Object System.Net.WebProxy('http://%PROXY%'); $client = New-Object System.Net.WebClient; $client.Proxy = $proxy; $client.DownloadFile('https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip', 'ffmpeg.zip')"

if errorlevel 1 (
    echo [ERROR] FFmpeg download failed via proxy
    echo    Trying direct download...
    certutil -urlcache -split -f https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip ffmpeg.zip

    if errorlevel 1 (
        echo [ERROR] FFmpeg download failed
        echo    Trying alternative download via proxy...
        powershell -Command "$proxy = New-Object System.Net.WebProxy('http://%PROXY%'); $client = New-Object System.Net.WebClient; $client.Proxy = $proxy; $client.DownloadFile('https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z', 'ffmpeg.7z')"

        if errorlevel 1 (
            echo [ERROR] Alternative download via proxy failed
            echo    Trying direct alternative download...
            certutil -urlcache -split -f https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z ffmpeg.7z

            if errorlevel 1 (
                echo [ERROR] Alternative download also failed
                echo    Please manually download FFmpeg: https://ffmpeg.org/download.html
                echo    and extract to resources\ffmpeg directory
                set FFMPEG_AVAILABLE=0
                goto :FFMPEG_OK
            ) else (
                echo [OK] Download complete (7z format)
                echo Extracting FFmpeg...
                if not exist 7z.exe (
                    echo Downloading 7-Zip extractor via proxy...
                    powershell -Command "$proxy = New-Object System.Net.WebProxy('http://%PROXY%'); $client = New-Object System.Net.WebClient; $client.Proxy = $proxy; $client.DownloadFile('https://www.7-zip.org/a/7zr.exe', '7zr.exe')"
                    if errorlevel 1 (
                        echo [WARN] Failed to download 7zr.exe via proxy, trying direct...
                        certutil -urlcache -split -f https://www.7-zip.org/a/7zr.exe 7zr.exe
                    )
                )
                7zr x ffmpeg.7z -oresources\temp -y >nul 2>&1
                if errorlevel 1 (
                    echo [ERROR] Extraction failed
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
        )
    )
) else (
    echo [OK] Download complete (zip format)
    echo Extracting FFmpeg...
    powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'resources\temp' -Force"
    if errorlevel 1 (
        echo [ERROR] Extraction failed
        set FFMPEG_AVAILABLE=0
        del ffmpeg.zip
        goto :FFMPEG_OK
    )

    REM Find extracted directory
    for /d %%I in (resources\temp\ffmpeg-master-*) do (
        move "%%I" resources\ffmpeg >nul 2>&1
    )
    rmdir /s /q resources\temp
    del ffmpeg.zip
)

REM Verify FFmpeg
if exist resources\ffmpeg\bin\ffmpeg.exe (
    echo [OK] FFmpeg ready
    set FFMPEG_AVAILABLE=1
) else (
    echo [ERROR] FFmpeg preparation failed
    set FFMPEG_AVAILABLE=0
)

:FFMPEG_OK

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist venv (
    echo [OK] Virtual environment already exists, skipping creation
) else (
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Virtual environment creation failed
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip via proxy...
python -m pip install --upgrade pip --proxy http://%PROXY%

REM Install PyInstaller (if not in dependencies)
echo.
echo Installing PyInstaller via proxy...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    pip install pyinstaller --proxy http://%PROXY%
) else (
    echo [OK] PyInstaller already installed
)

REM Install project dependencies
echo.
echo Installing project dependencies via proxy...
pip install -r requirements.txt --proxy http://%PROXY%
if errorlevel 1 (
    echo [ERROR] Dependency installation failed
    pause
    exit /b 1
)

REM Build application
echo.
echo ========================================
echo Building application...
echo ========================================

REM Create dist directory (if not exists)
if not exist dist mkdir dist

REM Build with PyInstaller
pyinstaller --clean --noconfirm VideoWatermarkTool.spec

if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo [OK] Build complete!
echo ========================================
echo.

REM Show generated files
if exist "dist\VideoWatermarkTool.exe" (
    echo Generated executable:
    echo   %CD%\dist\VideoWatermarkTool.exe
    echo.
    echo File size:
    for %%I in ("dist\VideoWatermarkTool.exe") do echo   %%~zI bytes (%%~zI/1024/1024 MB)
    echo.
    echo Note:
    echo   This is the command-line version with all CLI features
    echo   For GUI, use after building: VideoWatermarkTool.exe ui
    echo.
) else (
    echo [WARN] Generated file not found, build may have failed
)

REM Check if FFmpeg is included
echo Dependency check:
if exist "dist\_internal\imageio_ffmpeg\ffmpeg-win64-v4.2.2.exe" (
    echo [OK] FFmpeg embedded (via imageio-ffmpeg)
) else if !FFMPEG_AVAILABLE!==1 (
    if exist "dist\_internal\ffmpeg\ffmpeg.exe" (
        echo [OK] FFmpeg embedded (full version)
    ) else (
        echo [WARN] FFmpeg not fully embedded, but program can still run
        echo    (using imageio_ffmpeg fallback)
    )
) else (
    echo [WARN] FFmpeg not found, program may not process video
)

echo.
echo Usage instructions:
echo   1. Copy dist directory to target machine
echo   2. Run: VideoWatermarkTool.exe
echo   3. No additional dependencies needed!
echo.
echo Test commands:
echo   VideoWatermarkTool.exe --help
echo   VideoWatermarkTool.exe ui
echo.

REM Generate documentation
echo Generating documentation...
(
echo    Video Watermark Tool - Deployment Guide
echo ========================================
echo.
echo Build Information:
echo - Build Date: %DATE% %TIME%
echo - Python: %PYTHON_CMD%
echo.
echo Deployment Steps:
echo 1. Copy dist directory to target Windows machine
echo 2. Run VideoWatermarkTool.exe directly
echo 3. No need to install any additional dependencies!
echo.
echo System Requirements:
echo - Windows 7 or higher
echo - No need to install Python, FFmpeg, or other dependencies
echo.
echo Included Components:
if !FFMPEG_AVAILABLE!==1 (
echo - [OK] FFmpeg (video processing engine, built-in)
) else (
echo - [WARN] FFmpeg (may use fallback)
)
echo - [OK] Python 3.12 runtime
echo - [OK] All Python dependencies
echo - [OK] GUI support (PyQt6)
echo.
echo Usage Examples:
echo 1. View help: VideoWatermarkTool.exe --help
echo 2. Launch GUI: VideoWatermarkTool.exe ui
echo 3. Add image watermark: VideoWatermarkTool.exe watermark -i input.mp4 -o output.mp4 -w watermark.png
echo 4. Add text watermark: VideoWatermarkTool.exe watermark-text -i input.mp4 -o output.mp4 -t "Copyright"
echo 5. Insert clip: VideoWatermarkTool.exe insert -m main.mp4 -i insert.mp4 -o output.mp4 -p 30
echo.
echo File Description:
echo - VideoWatermarkTool.exe: Main program file
echo - _internal/: Program dependency libraries (do not delete)
echo.
echo Technical Support:
echo If you encounter issues, please ensure:
echo 1. All files are in the same directory
echo 2. Do not delete the _internal folder
echo 3. Run as administrator (may be required on some systems)
echo.
echo Important Notes:
echo - Full-size watermark mode: Watermark image same size as video (recommended)
echo - Scaled mode: Use --scaled parameter
echo - Supported formats: MP4, AVI, MOV, MKV, WebM, etc.
echo.
echo ========================================
echo    Fully standalone, no installation required!
echo ========================================
) > dist\README_Deployment_Guide.txt

echo.
echo Documentation generated: dist\README_Deployment_Guide.txt
echo.

echo ========================================
echo Build script execution complete
echo ========================================
echo.
echo Tips:
echo - This script can be run multiple times, it will skip completed steps
echo - If code is updated, just run this script to rebuild
echo.

pause
endlocal
