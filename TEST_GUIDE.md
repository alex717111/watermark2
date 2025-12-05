# 测试指南

## 环境准备

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 检查FFmpeg

必须安装FFmpeg才能处理视频。

**检查FFmpeg是否已安装：**
```bash
ffmpeg -version
```

**安装FFmpeg：**

**Windows:**
1. 从 https://ffmpeg.org/download.html 下载Windows版本
2. 解压并将bin目录添加到系统PATH

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

## 测试步骤

### 1. 快速测试CLI

```bash
# 查看帮助
python main.py --help

# 查看可用位置
python main.py positions

# 如果看到正确的输出，说明CLI工作正常
```

### 2. 准备测试文件

如果要从零创建测试文件：

```bash
# 创建简单的测试视频（需要FFmpeg）
ffmpeg -f lavfi -i testsrc=duration=10:size=1280x720:rate=30 -pix_fmt yuv420p test_video.mp4

# 创建测试水印图片
python -c "
from PIL import Image, ImageDraw
img = Image.new('RGBA', (200, 80), (255, 0, 0, 128))
draw = ImageDraw.Draw(img)
draw.text((10, 10), 'WATERMARK', fill=(255, 255, 255, 255))
img.save('logo.png')
"
```

或者使用现有的测试视频：
- 用户提供的: `~/Downloads/126.mp4`
- 复制到当前目录: `cp ~/Downloads/126.mp4 test_video.mp4`

### 3. 测试图片水印

```bash
# 基本测试
python main.py watermark \
  -i test_video.mp4 \
  -o test_output_image.mp4 \
  -w logo.png

# 如果logo.png不存在，先创建一个
```

### 4. 测试文字水印

```bash
# 创建文字水印
python main.py watermark-text \
  -i test_video.mp4 \
  -o test_output_text.mp4 \
  -t "Test Watermark" \
  --font-size 36
```

### 5. 创建插入视频测试

```bash
# 创建5秒的插入视频（需要先创建）
ffmpeg -f lavfi -i testsrc=duration=5:size=1280x720:rate=30 -pix_fmt yuv420p test_insert.mp4

# 插入视频
python main.py insert \
  -m test_video.mp4 \
  -i test_insert.mp4 \
  -o test_output_insert.mp4 \
  -p 3
```

## 使用用户提供的视频测试

如果你有一个视频在 `~/Downloads/126.mp4`：

```bash
# 复制到当前目录（可选）
cp ~/Downloads/126.mp4 test_main.mp4

# 测试1：添加文字水印
python main.py watermark-text \
  -i ~/Downloads/126.mp4 \
  -o output_text.mp4 \
  -t "My Video" \
  -p bottom-right \
  --font-size 48

# 测试2：创建简单水印图片并应用
python -c "
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGBA', (300, 100), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.text((10, 10), 'WATERMARK', fill=(255, 255, 255, 200), font_size=40)
img.save('test_logo.png')
"

python main.py watermark \
  -i ~/Downloads/126.mp4 \
  -o output_logo.mp4 \
  -w test_logo.png \
  --opacity 0.8
```

## 预期输出

成功处理后，你会看到类似输出：

```
正在添加水印到视频...
  输入: test_video.mp4
  水印: logo.png
  位置: bottom-right
  输出: test_output.mp4
✅ 水印添加成功: test_output.mp4
```

## 常见问题

**问题："未找到MoviePy"**
- 解决：`pip install moviepy`

**问题："未找到FFmpeg"**
- 解决：安装FFmpeg并添加到PATH

**问题："ImageMagick未安装"**
- 解决：
  - Windows：下载安装ImageMagick https://imagemagick.org/
  - Linux：`sudo apt install imagemagick`

**问题：处理时间长**
- 这是正常的，视频处理需要时间
- 可以在输出视频中看到进度

## 测试检查清单

- [ ] 安装所有依赖
- [ ] FFmpeg可用
- [ ] CLI帮助显示正常
- [ ] 图片水印功能正常
- [ ] 文字水印功能正常
- [ ] 视频插入功能正常
- [ ] 输出视频可播放

## 示例测试文件结构

```
video-watermark-tool/
├── main.py
├── test_video.mp4          # 主测试视频
├── test_logo.png           # 测试水印图片
├── test_insert.mp4         # 测试插入视频
├── output_image.mp4        # 图片水印输出
├── output_text.mp4         # 文字水印输出
└── output_insert.mp4       # 插入视频输出
```
