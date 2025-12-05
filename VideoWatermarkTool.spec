# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os
import glob

datas = [('src', 'src')]
binaries = []
hiddenimports = [
    'src.cli',
    'src.watermark',
    'src.watermark.text_watermark_v2',
    'src.watermark.text_watermark',
    'src.watermark.image_watermark',
    'src.watermark',
    'src.insert',
    'src.insert.video_insert',
    'src.ui_app',
    'src.ui',
    'src.ui.main_window',
    'src.logger_config'
]
tmp_ret = collect_all('imageio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('imageio_ffmpeg')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# 收集 FFmpeg 二进制文件（如果存在）
print("正在查找 FFmpeg 二进制文件...")

# 查找常见位置的 FFmpeg
spec_path = os.getcwd()
ffmpeg_paths = [
    r'C:\Program Files\FFmpeg\bin\ffmpeg.exe',
    r'C:\Program Files (x86)\FFmpeg\bin\ffmpeg.exe',
    r'C:\Users\*\AppData\Local\Programs\FFmpeg\bin\ffmpeg.exe',
    os.path.join(spec_path, 'ffmpeg', 'bin', 'ffmpeg.exe'),
    os.path.join(spec_path, 'resources', 'ffmpeg', 'bin', 'ffmpeg.exe')
]

ffmpeg_found = False
for pattern in ffmpeg_paths:
    try:
        if '*' in pattern:
            matches = glob.glob(pattern)
        else:
            matches = [pattern] if os.path.exists(pattern) else []

        for match in matches:
            if os.path.exists(match):
                print(f"找到 FFmpeg: {match}")
                ffmpeg_dir = os.path.dirname(match)
                dest_dir = 'ffmpeg/bin' if 'Program Files' in match else 'ffmpeg'
                binaries.append((os.path.join(ffmpeg_dir, 'ffmpeg.exe'), dest_dir))
                binaries.append((os.path.join(ffmpeg_dir, 'ffprobe.exe'), dest_dir))
                binaries.append((os.path.join(ffmpeg_dir, 'ffplay.exe'), dest_dir))
                ffmpeg_found = True
                break
    except Exception as e:
        print(f"搜索路径 {pattern} 时出错: {e}")

    if ffmpeg_found:
        break

# 如果通过 imageio_ffmpeg 安装了 FFmpeg，确保它被包含
import imageio_ffmpeg
binary_path = imageio_ffmpeg.get_ffmpeg_exe()
if binary_path and os.path.exists(binary_path):
    print(f"找到 imageio_ffmpeg: {binary_path}")
    binaries.append((binary_path, './imageio_ffmpeg'))


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VideoWatermarkTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
