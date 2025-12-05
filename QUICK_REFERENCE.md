# 视频水印工具 - 快速参考

## 项目状态
✅ **第一阶段完成**: CLI版本已完全实现并测试通过

## 核心功能

### 1. 图片水印
在视频上添加图片水印（支持PNG透明背景）

```bash
./venv/bin/python main.py watermark \
  -i input.mp4 \
  -o output.mp4 \
  -w logo.png \
  -p bottom-right \
  --opacity 0.9
```

**参数说明**:
- `-i, --input`: 输入视频
- `-o, --output`: 输出视频
- `-w, --watermark`: 水印图片（PNG推荐）
- `-p, --position`: 位置（top-left, top-center, top-right, center-left, center, center-right, bottom-left, bottom-center, bottom-right）
- `--opacity`: 透明度（0.0-1.0）
- `--margin`: 边距（像素）
- `--start-time`: 开始时间（秒或HH:MM:SS）
- `--end-time`: 结束时间
- `--width, --height`: 水印尺寸

### 2. 文字水印
在视频上添加文字水印

```bash
./venv/bin/python main.py watermark-text \
  -i input.mp4 \
  -o output.mp4 \
  -t "Copyright 2025" \
  --font-size 48 \
  --color white \
  -p top-right \
  --opacity 0.9 \
  --stroke-width 2 \
  --stroke-color black
```

**参数说明**:
- `-t, --text`: 水印文字
- `--font-size`: 字体大小（默认：24）
- `--color`: 文字颜色（名称或#RRGGBB）
- `--font`: 字体文件路径（TTF）
- `--stroke-width`: 描边宽度（0表示无描边）
- `--stroke-color`: 描边颜色

### 3. 视频插入
在视频指定位置插入另一个视频（**默认无缝，无黑屏**）

```bash
./venv/bin/python main.py insert \
  -m main.mp4 \
  -i insert.mp4 \
  -o output.mp4 \
  -p 30 \
  --audio-mode keep
```

**参数说明**:
- `-m, --main`: 主视频
- `-i, --insert`: 要插入的视频
- `-p, --position`: 插入位置（秒或HH:MM:SS格式）
- `--audio-mode`: 音频处理（keep/replace/mix/mute）
- `--seamless`: 无缝插入模式（**默认启用**，无黑屏）
- `--no-seamless`: 禁用无缝模式（会有黑屏过渡）
- `--crossfade`: 交叉淡入淡出时长（秒，与无缝模式冲突）

**重要**: 默认启用 `--seamless`，确保插入时无黑屏。

## 快速开始

### 1. 设置虚拟环境
```bash
# Linux/macOS
./setup_venv.sh

# Windows
setup_venv.bat
```

### 2. 激活虚拟环境
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate.bat
```

### 3. 运行测试
```bash
# 运行所有测试（生成测试文件在 test_output/）
./venv/bin/python tests/test_cli.py

# 查看测试输出
cd test_output
ffplay output_watermark.mp4
ffplay output_text.mp4
ffplay output_insert.mp4
```

### 4. 使用您的视频
```bash
# 使用您的测试视频
./venv/bin/python main.py watermark-text \
  -i ~/Downloads/126.mp4 \
  -o output_text.mp4 \
  -t "My Video" \
  -p bottom-right \
  --font-size 48

# 添加图片水印
./venv/bin/python main.py watermark \
  -i ~/Downloads/126.mp4 \
  -o output_logo.mp4 \
  -w test_output/test_watermark.png \
  --opacity 0.8
```

## 文件结构

```
video-watermark-tool/
├── main.py                      # 程序入口
├── src/                         # 源代码
│   ├── cli.py                  # CLI接口
│   ├── watermark/              # 水印模块
│   └── insert/                 # 插入模块
├── test_output/                # 测试输出
│   ├── test_video.mp4          # 测试视频
│   ├── test_watermark.png      # 测试水印
│   ├── output_watermark.mp4    # 图片水印结果
│   ├── output_text.mp4         # 文字水印结果
│   ├── output_insert.mp4       # 视频插入结果
│   └── README.md               # 输出说明
├── requirements.txt            # 依赖
└── README.md                   # 完整文档
```

## 最佳实践

### 水印设计
**推荐全尺寸水印方案**:
1. 创建与视频同尺寸的PNG图片
2. 在图片中精确设计水印位置和内容
3. 保存带透明图层
4. 使用该图片作为水印

优点：
- ✅ 无需计算绝对位置
- ✅ 支持复杂设计（多文字、logo、图形）
- ✅ 可视化编辑更直观
- ✅ 一致性好

### 视频插入
**总是使用无缝模式**（默认已启用）:
```bash
# 正确（默认无缝）
python main.py insert -m main.mp4 -i insert.mp4 -o out.mp4 -p 30

# 等同于
python main.py insert -m main.mp4 -i insert.mp4 -o out.mp4 -p 30 --seamless
```

### 使用场景
- **添加水印**: 品牌logo、版权声明、水印文字
- **视频插入**: 插入片头/片尾、插入说明片段、合并视频

## 故障排除

### FFmpeg未找到
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# 下载: https://ffmpeg.org/download.html
# 添加bin到PATH
```

### 虚拟环境问题
```bash
# 重新创建虚拟环境
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 测试失败
```bash
# 检查FFmpeg
ffmpeg -version

# 运行测试
./venv/bin/python tests/test_cli.py
```

## 技术支持

- **MoviePy**: 2.2.1 (已适配2.x API)
- **Python**: 3.12+
- **FFmpeg**: 4.0+

## 下一步

可选功能：
- UI界面（PyQt6）
- 批量处理
- 预设配置
- 实时预览

## 测试结果

✅ 所有测试通过（5/5单元测试 + 3/3功能测试）
- 图片水印：正常
- 文字水印：正常
- 视频插入：无缝，无黑屏

测试输出：`test_output/` 目录
