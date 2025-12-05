# 视频水印工具

一个简单易用的跨平台视频处理工具，支持向视频添加水印和插入视频片段。

## 功能特性

- 🖼️ **图片水印**：支持PNG透明背景图片
- ✏️ **文字水印**：自定义文字、字体、颜色、描边
- 📹 **视频插入**：将视频插入到指定位置
- 🎛️ **灵活配置**：支持位置、透明度、大小、持续时间等参数
- 🖥️ **跨平台**：支持Windows和Linux
- 🎯 **易用性**：命令行和UI双接口（CLI已实现，UI开发中）

## 快速开始

### 环境要求

- Python 3.8+
- FFmpeg 4.0+（必须）

### 安装FFmpeg

**Windows:**
1. 下载：https://ffmpeg.org/download.html
2. 解压并添加bin目录到系统PATH

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 方式一：使用虚拟环境（推荐）

#### Linux/macOS:
```bash
git clone <repository>
cd video-watermark-tool

# 自动设置虚拟环境并安装依赖
./setup_venv.sh

# 或者手动设置:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Windows:
```bat
git clone <repository>
cd video-watermark-tool

REM 自动设置虚拟环境并安装依赖
setup_venv.bat

REM 或者手动设置:
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 方式二：直接安装（不推荐）

```bash
pip install -r requirements.txt
```

**注意**: 直接安装在系统Python中可能导致依赖冲突，建议使用虚拟环境。

## 命令行使用

### 1. 添加图片水印

**默认模式（推荐）**：水印图片将与视频同尺寸，水印的透明度和位置由图片本身决定
```bash
# 基本用法（默认全尺寸模式）
python main.py watermark -i input.mp4 -o output.mp4 -w watermark.png
```

**缩放模式**（兼容旧版本）：将水印缩放到视频宽度的1/6，支持位置设置
```bash
# 使用缩放模式（类似旧版本行为）
python main.py watermark \
  -i input.mp4 \
  -o output.mp4 \
  -w logo.png \
  --scaled \
  -p top-right \
  --margin 20
```

**其他常用参数：**
```bash
# 指定时间范围（在全尺寸和缩放模式下都有效）
python main.py watermark \
  -i input.mp4 \
  -o output.mp4 \
  -w watermark.png \
  --start-time 10 \
  --end-time 60 \
  --opacity 0.9

# 在缩放模式下自定义大小
python main.py watermark \
  -i input.mp4 \
  -o output.mp4 \
  -w logo.png \
  --scaled \
  --width 300 \
  --height 100
```

**参数说明：**
- `-i, --input`: 输入视频文件
- `-o, --output`: 输出视频文件
- `-w, --watermark`: 水印图片文件（支持PNG透明）
- `--scaled`: 使用缩放模式（可选），默认是全尺寸模式
- `-p, --position`: 水印位置（仅在缩放模式下有效）
  - `top-left`, `top-center`, `top-right`
  - `center-left`, `center`, `center-right`
  - `bottom-left`, `bottom-center`, `bottom-right`（默认）
- `--opacity`: 透明度 0.0-1.0（默认：0.8）
- `--margin`: 边距像素（默认：10，仅在缩放模式下有效）
- `--start-time`: 开始时间（秒或HH:MM:SS，默认：0）
- `--end-time`: 结束时间（秒或HH:MM:SS，默认：视频结束）
- `--width`: 水印宽度（像素，仅在缩放模式下有效）
- `--height`: 水印高度（像素，仅在缩放模式下有效）

**全尺寸模式建议：**
- 创建与视频同尺寸的PNG图片（如1920x1080）
- 在图片编辑软件中设计水印位置和透明度
- 支持复杂效果：渐变、阴影、多元素组合
- 处理质量更高，无缩放失真

### 2. 添加文字水印

```bash
# 基本用法
python main.py watermark-text -i input.mp4 -o output.mp4 -t "Copyright 2025"

# 自定义样式
python main.py watermark-text \
  -i input.mp4 \
  -o output.mp4 \
  -t "My Watermark" \
  -p top-left \
  --font-size 36 \
  --color red \
  --stroke-width 2 \
  --stroke-color black \
  --opacity 0.9

# 使用自定义字体
python main.py watermark-text \
  -i input.mp4 \
  -o output.mp4 \
  -t "特殊字体" \
  --font /path/to/font.ttf \
  --font-size 48
```

**参数说明：**
- `-t, --text`: 水印文字内容
- `--font-size`: 字体大小（默认：24）
- `--color`: 文字颜色（默认：white，支持颜色名称或十六进制）
- `--font`: 字体文件路径（TTF格式）
- `--stroke-width`: 描边宽度（默认：1，0表示无描边）
- `--stroke-color`: 描边颜色（默认：black）

### 3. 插入视频

```bash
# 基本用法
python main.py insert -m main.mp4 -i insert.mp4 -o output.mp4 -p 30

# 音频处理选项
python main.py insert \
  -m main.mp4 \
  -i insert.mp4 \
  -o output.mp4 \
  -p 01:30 \
  --audio-mode mix \
  --crossfade 0.5

# 仅保留主视频音频
python main.py insert \
  -m main.mp4 \
  -i insert.mp4 \
  -o output.mp4 \
  -p 45s \
  --audio-mode keep
```

**参数说明：**
- `-m, --main`: 主视频文件
- `-i, --insert`: 要插入的视频文件
- `-p, --position`: 插入位置（秒或HH:MM:SS）
- `--audio-mode`: 音频处理方式
  - `keep`: 保留主视频音频（默认）
  - `replace`: 使用插入视频音频
  - `mix`: 混合音频
  - `mute`: 静音
- `--crossfade`: 交叉淡入淡出时长（秒，默认：0）

### 4. 查看位置选项

```bash
python main.py positions
```

### 时间格式支持

所有时间参数支持以下格式：
- 秒数：`60`
- 时分秒：`01:30:45`
- 分秒：`30:45`
- 带后缀：`1.5h`, `30m`, `45s`

## 示例

### 示例1：使用全尺寸水印（默认，推荐）
```bash
# 这是最简单的用法，fullsize_watermark.png与视频同尺寸
python main.py watermark \
  -i input.mp4 \
  -o output_with_watermark.mp4 \
  -w fullsize_watermark.png \
  --opacity 0.9
```
**优点**：
- 水印位置在图片中已精确设计
- 支持复杂的视觉效果（渐变、阴影、多元素组合）
- 处理质量更高（无缩放失真）
- 使用简单，无需位置参数

### 示例2：使用缩放模式（兼容简单logo）
```bash
# 如果水印是小logo，可以使用缩放模式
python main.py watermark \
  -i input.mp4 \
  -o output_with_logo.mp4 \
  -w logo.png \
  --scaled \
  -p bottom-right \
  --opacity 0.6 \
  --margin 20
```
用于简单的logo或不需要复杂设计的水印。

### 示例3：在视频开头添加版权声明
```bash
python main.py watermark-text \
  -i input.mp4 \
  -o output_with_text.mp4 \
  -t "Copyright © 2025" \
  -p top-left \
  --font-size 20 \
  --color yellow \
  --stroke-width 1 \
  --end-time 5
```

### 示例3：在视频中间插入广告
```bash
python main.py insert \
  -m main_video.mp4 \
  -i ad_video.mp4 \
  -o output_with_ad.mp4 \
  -p 60 \
  --audio-mode replace \
  --crossfade 1.0
```

## 日志功能

所有命令（CLI和UI）都支持日志记录，日志文件自动保存在程序目录的 `logs/` 子目录中。

### 查看日志文件

```bash
# 实时查看日志（Linux/macOS）
tail -f logs/video_watermark.log

# 或使用cat查看
 cat logs/video_watermark.log
```

### 指定日志级别

```bash
# DEBUG级别（最详细，用于调试）
python main.py watermark -i input.mp4 -o output.mp4 -w logo.png --log-level DEBUG

# INFO级别（默认，记录关键信息）
python main.py watermark -i input.mp4 -o output.mp4 -w logo.png --log-level INFO

# WARNING级别（仅警告和错误）
python main.py watermark -i input.mp4 -o output.mp4 -w logo.png --log-level WARNING

# 支持的级别：DEBUG, INFO, WARNING, ERROR
```

### 日志输出示例

```bash
# 控制台输出（用户看到）
正在添加水印到视频...
  输入: video.mp4
  水印: logo.png
  模式: 全尺寸水印
✅ 水印添加成功: output.mp4

# 同时写入: logs/video_watermark.log
# 2025-12-05 15:30:26 - video_watermark - INFO - 开始处理：图片水印
# 2025-12-05 15:30:26 - video_watermark - INFO - 输入文件: video.mp4
# 2025-12-05 15:30:26 - video_watermark - INFO - 水印文件: logo.png
# 2025-12-05 15:30:26 - video_watermark - INFO - 模式: 全尺寸
# 2025-12-05 15:30:45 - video_watermark - INFO - 处理完成
```

### 日志特性

- ✅ **自动轮转**：单文件最大2MB，超过自动清空重新开始
- ✅ **双输出**：同时输出到控制台和日志文件
- ✅ **统一管理**：CLI和UI使用同一套日志系统
- ✅ **UTF-8编码**：支持中文和特殊字符

## 版本更新说明

### 2025-12-05 重大更新：全尺寸水印成为默认行为

#### 变更内容

**CLI接口变更：**
- ❌ 移除 `--fullsize` 参数
- ✅ 新增 `--scaled` 参数（用于启用旧的缩放模式）

**默认行为变更：**
- **变更前**：默认将水印缩放到视频宽度的1/8，支持9个位置选项
- **变更后**：默认使用全尺寸模式（水印图片与视频同尺寸），水印位置、透明度在图片中预先设计

#### 迁移指南

**场景1：继续使用简单logo（快速迁移）**
```bash
# 旧命令
python main.py watermark -i video.mp4 -o output.mp4 -w logo.png -p bottom-right

# 新命令（添加 --scaled 参数）
python main.py watermark -i video.mp4 -o output.mp4 -w logo.png --scaled -p bottom-right
```

**场景2：迁移到全尺寸模式（推荐）**
```bash
# 创建与视频同尺寸的水印（使用Photoshop/GIMP等工具）
# 然后使用（无需位置参数）
python main.py watermark -i video.mp4 -o output.mp4 -w watermark.png
```

**优势：**
- ✅ 支持复杂水印设计（渐变、阴影、多元素组合）
- ✅ 位置精确控制，所见即所得
- ✅ 无缩放失真，处理质量更高
- ✅ 支持更多视觉效果

**性能影响：**
- 输出文件大小：增加1-5%（可忽略）
- 处理速度：慢10-30%（仍在可接受范围）
- 内存占用：增加50-100%（处理大视频时需注意）

## 开发计划

### 已完成功能
- [x] CLI命令行接口
- [x] 图片水印功能（支持全尺寸模式）
- [x] 文字水印功能
- [x] 视频插入功能
- [x] UI基础框架（PyQt6）

### 开发中
- [x] UI界面（基础功能已完成）
- [ ] 视频预览功能
- [ ] 批量处理队列
- [ ] 可视化时间轴
- [ ] 水印图片可视化编辑器

### 计划中
- [ ] 预设配置
- [ ] 实时预览
- [ ] Windows/Linux打包测试

## 技术栈

- **MoviePy**：视频处理核心库
- **Click**：命令行框架
- **PyInstaller**：打包工具

## 常见问题

**Q: 为什么使用虚拟环境？**
A: 虚拟环境隔离项目依赖，避免与系统Python包冲突，便于管理和部署。

**Q: 虚拟环境如何激活？**
A: 
- Linux/macOS: `source venv/bin/activate`
- Windows: `venv\Scripts\activate.bat`

**Q: 退出虚拟环境？**
A: 运行 `deactivate` 命令

**Q: 每次使用都需要激活虚拟环境吗？**
A: 是的，每次打开新终端都需要激活虚拟环境

**Q: 处理大文件时很慢？**
A: 视频处理需要大量计算，处理时间取决于视频长度、分辨率和硬件性能。可以在write_videofile时调整codec参数优化速度。

**Q: 水印图片支持哪些格式？**
A: 推荐使用PNG格式（支持透明背景），也支持JPG等常见格式。

**Q: 全尺寸水印对视频文件大小有影响吗？**
A: 影响非常小，通常只增加1-5%的文件大小。因为PNG的透明区域在视频编码时会被高效压缩，H.264/H.265编码器会智能处理相似/重复像素。

**Q: 全尺寸水印和缩放模式有什么区别？**
A: 全尺寸水印模式：水印图片与视频同尺寸，水印位置、透明度在图片中预先设计，支持复杂效果（渐变、阴影等），质量更高。缩放模式：水印自动缩放到视频宽度的1/6，支持9个预设位置，适用于简单logo。

**Q: 字体文件放在哪里？**
- Windows: `C:\\Windows\\Fonts\\`
- Linux: `/usr/share/fonts/` 或 `~/.fonts/`

**Q: 如何打包成可执行文件？**
```bash
# Windows（生成.exe）
pyinstaller --onefile --add-binary "ffmpeg.exe;./" main.py

# Linux（生成.bin）
pyinstaller --onefile main.py
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
