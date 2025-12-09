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

### 2. 添加组合水印（Logo + 文字）

**推荐使用合并模式**：将Logo和文字合并为一张图片，Logo自动缩放匹配文字高度，作为一个整体水印添加到视频中。

**两种模式：**

**模式一：合并模式（推荐）**
- 使用 `--combine-mode` 将Logo和文字合并为一张图片
- Logo自动缩放匹配文字高度
- 只需要一个位置参数（`--logo-position`）
- Logo在左，文字在右（或垂直排列）

**模式二：分离模式（高级）**
- Logo和文字分别定位（使用 `--logo-position` 和 `--text-position`）
- 更灵活，可以放置在不同位置
- 适合特殊布局需求

```bash
# 仅文字水印（替代watermark-text）
python main.py watermark-combo -i input.mp4 -o output.mp4 -t "Copyright 2025"

# 合并模式：Logo + 文字（推荐）
python main.py watermark-combo \
  -i input.mp4 \
  -o output.mp4 \
  -w logo.png \
  -t "My Channel" \
  --combine-mode \
  --logo-position bottom-right \
  --font-size 36

# 合并模式：调整Logo大小和间距
python main.py watermark-combo \
  -i input.mp4 \
  -o output.mp4 \
  -w logo.png \
  -t "Copyright 2025" \
  --combine-mode \
  --logo-scale-factor 1.2 \
  --combine-spacing 20 \
  --font-size 32

# 合并模式：垂直排列（Logo在上，文字在下）
python main.py watermark-combo \
  -i input.mp4 \
  -o output.mp4 \
  -w logo.png \
  -t "My Channel" \
  --combine-mode \
  --combine-layout vertical \
  --logo-position center

# 指定时间范围
python main.py watermark-combo \
  -i input.mp4 \
  -o output.mp4 \
  -w logo.png \
  -t "Copyright 2025" \
  --combine-mode \
  --start-time 10 \
  --end-time 60

# 分离模式：自定义位置（高级，Logo和文字分别定位）
python main.py watermark-combo \
  -i input.mp4 \
  -o output.mp4 \
  -w logo.png \
  -t "My Watermark" \
  --logo-position top-left \
  --text-position bottom-right \
  --font-size 36 \
  --color red
```

**参数说明：**
- `-t, --text`: 水印文字内容（必需）
- `-w, --watermark`: Logo图片路径（可选，支持PNG透明背景）
- `--combine-mode`: 合并Logo和文字为一张图片
- `--combine-layout`: 合并布局（horizontal: 水平排列，vertical: 垂直排列）
- `--combine-spacing`: 合并时Logo和文字之间的间距（像素，默认：10）
- `--logo-position`: Logo位置（默认：top-left，在合并模式中为整体位置）
- `--logo-opacity`: Logo透明度 0.0-1.0（默认：0.9，在合并模式中为整体透明度）
- `--logo-margin`: Logo边距（默认：10）
- `--logo-width`: Logo宽度（像素，指定则覆盖自动缩放）
- `--logo-height`: Logo高度（像素，指定则覆盖自动缩放）
- `--logo-scale-factor`: Logo相对于字体高度的缩放因子（默认：1.0）
- `--text-position`: 文字位置（分离模式使用，默认：bottom-right）
- `--font-size`: 字体大小（默认：24）
- `--color`: 文字颜色（默认：white）
- `--font`: 字体文件路径（TTF格式）
- `--text-opacity`: 文字透明度 0.0-1.0（分离模式使用，默认：0.9）
- `--stroke-width`: 描边宽度（默认：1，0表示无描边）
- `--stroke-color`: 描边颜色（默认：black）
- `--vertical-margin`: 文字垂直边距像素（分离模式使用，默认：10）
- `--start-time`: 水印开始时间（秒或HH:MM:SS，默认：0）
- `--end-time`: 水印结束时间（秒或HH:MM:SS，默认：视频结束）

**Logo自动缩放说明：**
- 默认情况下，Logo高度会自动匹配文字高度
- 使用 `--logo-scale-factor` 可以调整相对大小，例如 `1.2` 表示比文字高20%
- 如果手动指定 `--logo-width` 或 `--logo-height`，则自动缩放失效

**合并模式优势：**
- Logo和文字作为一个整体，间距固定且美观
- 只需指定一个位置参数（`--logo-position`）
- Logo自动缩放匹配文字高度，无需手动调整
- 整体透明度统一控制

### 3. 添加文字水印（兼容旧版）

**推荐使用 `watermark-combo` 命令替代**，此命令仅为向后兼容保留。

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

# 调整垂直留空（避免字母上下延被截断）
python main.py watermark-text \
  -i input.mp4 \
  -o output.mp4 \
  -t "gjpqy Letters" \
  --font-size 48 \
  --vertical-margin 15
```

**参数说明：**
- `-t, --text`: 水印文字内容
- `--font-size`: 字体大小（默认：24）
- `--color`: 文字颜色（默认：white，支持颜色名称或十六进制）
- `--font`: 字体文件路径（TTF格式）
- `--stroke-width`: 描边宽度（默认：1，0表示无描边）
- `--stroke-color`: 描边颜色（默认：black）
- `--vertical-margin`: 上下垂直留空（像素，默认：10），避免因字母上下延（g, j, p, q, y 等）被截断

**提示**：如果文字水印的顶部或底部被截断（特别是包含 g, j, p, q, y 等字母时），请增加 `--vertical-margin` 参数的值。

### 4. 插入视频

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

### 5. 查看位置选项

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

### 示例3：使用组合水印（Logo + 文字）
```bash
# Logo在左上，文字在右下（默认布局）
python main.py watermark-combo \
  -i input.mp4 \
  -o output_with_combo.mp4 \
  -w logo.png \
  -t "Copyright 2025" \
  --logo-scale-factor 1.2

# 仅添加文字（替代watermark-text）
python main.py watermark-combo \
  -i input.mp4 \
  -o output_text_only.mp4 \
  -t "My Watermark" \
  --font-size 48 \
  --color yellow \
  --stroke-width 2 \
  --text-position center
```

### 示例4：在视频开头添加版权声明
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

### 示例5：在视频中间插入广告
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

## 项目打包

### 打包整个项目（不包含.git）

如果需要将整个项目打包分发（不包含git历史），可以使用以下命令：

**Linux/macOS:**
```bash
# 方法1: 使用git archive（推荐）
git archive --format=zip --output=video-watermark-tool.zip HEAD

# 方法2: 使用tar排除.git目录
tar -czf video-watermark-tool.tar.gz --exclude=.git *

# 方法3: 使用zip命令
zip -r video-watermark-tool.zip . -x "*.git*"
```

**Windows:**
```powershell
# PowerShell方法
Compress-Archive -Path * -DestinationPath video-watermark-tool.zip
# 注意：PowerShell Compress-Archive会自动排除.git目录

# 或者使用7-Zip（如果已安装）
7z a -tzip video-watermark-tool.zip . -xr!.git
```

```batch
# CMD批处理方法（需要手动排除）
@echo off
setlocal enabledelayedexpansion

set "zipfile=video-watermark-tool.zip"
echo 正在打包项目，排除.git目录...

:: 删除旧的zip文件
if exist "%zipfile%" del "%zipfile%"

:: 使用PowerShell打包（如果可用）
powershell -Command "Get-ChildItem -Path '.' -Force | Where-Object { $_.Name -ne '.git' } | Compress-Archive -DestinationPath '%zipfile%' -Force"

if errorlevel 1 (
    echo ❌ 打包失败
    echo 请手动使用7-Zip或其他工具打包，排除.git目录
) else (
    echo ✅ 打包完成: %zipfile%
)
```

生成的 `video-watermark-tool.zip` 文件包含了完整的项目代码、资源文件和配置，可以在其他机器上解压后直接使用。
