# 快速启动指南

## 环境设置（使用虚拟环境）

### Linux/macOS:
```bash
# 1. 自动设置（推荐）
./setup_venv.sh

# 2. 或者手动设置
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows:
```bat
REM 1. 自动设置（推荐）
setup_venv.bat

REM 2. 或者手动设置
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## 基础使用流程

### 激活虚拟环境

**每次使用前都需要激活：**

- Linux/macOS:
```bash
source venv/bin/activate
```

- Windows:
```bat
venv\Scripts\activate.bat
```

### 验证安装

```bash
# 查看帮助
python main.py --help

# 查看可用位置
python main.py positions
```

## 常见操作示例

### 1. 添加图片水印
```bash
python main.py watermark \
  -i input.mp4 \
  -o output.mp4 \
  -w logo.png \
  -p bottom-right \
  --opacity 0.8
```

### 2. 添加文字水印
```bash
python main.py watermark-text \
  -i input.mp4 \
  -o output.mp4 \
  -t "Copyright 2025" \
  --font-size 36 \
  --color white
```

### 3. 插入视频
```bash
python main.py insert \
  -m main.mp4 \
  -i insert.mp4 \
  -o output.mp4 \
  -p 30 \
  --audio-mode mix
```

## 退出虚拟环境

```bash
deactivate
```

## 故障排除

### 问题1: "未找到命令"
**解决**：先激活虚拟环境

```bash
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate.bat  # Windows
```

### 问题2: "No module named 'moviepy'"
**解决**：在虚拟环境中安装依赖

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 问题3: "ImageMagick not found"
**解决**：安装ImageMagick

- Windows: 下载并安装 https://imagemagick.org/
- Linux: `sudo apt install imagemagick`

### 问题4: FFmpeg相关问题
**解决**：确保FFmpeg在PATH中

```bash
# 检查FFmpeg
ffmpeg -version

# 如果未找到，安装：
# Windows: 下载并添加PATH
# Linux: sudo apt install ffmpeg
```

## 使用您的测试视频

```bash
# 激活虚拟环境
source venv/bin/activate

# 添加文字水印
python main.py watermark-text \
  -i ~/Downloads/126.mp4 \
  -o output_text.mp4 \
  -t "Test Video" \
  -p bottom-right \
  --font-size 48

# 查看输出
ls -lh output_text.mp4
```

## 项目结构

```
video-watermark-tool/
├── venv/                    # 虚拟环境目录
├── src/                     # 源代码
│   ├── cli.py              # 命令行接口
│   ├── watermark/          # 水印模块
│   └── insert/             # 插入模块
├── resources/              # 资源文件
├── tests/                  # 测试文件
├── requirements.txt        # 依赖列表
├── main.py                # 主入口
├── setup_venv.sh          # Linux虚拟环境脚本
├── setup_venv.bat         # Windows虚拟环境脚本
├── README.md              # 完整文档
└── QUICKSTART.md          # 本文件
```

## 常用命令速查

| 操作 | 命令 |
|------|------|
| 激活虚拟环境 | `source venv/bin/activate` |
| 退出虚拟环境 | `deactivate` |
| 查看帮助 | `python main.py --help` |
| 图片水印 | `python main.py watermark -i in.mp4 -o out.mp4 -w logo.png` |
| 文字水印 | `python main.py watermark-text -i in.mp4 -o out.mp4 -t "Text"` |
| 插入视频 | `python main.py insert -m main.mp4 -i insert.mp4 -o out.mp4 -p 30` |

## 打包应用（可选）

在虚拟环境中打包：

```bash
source venv/bin/activate
cd build
./build_linux.sh  # Linux
# 或
build_windows.bat  # Windows
```

输出文件在 `dist/` 目录下。
