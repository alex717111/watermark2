# 视频水印工具项目需求文档

## 项目概述
创建一个跨平台的视频处理工具，支持向视频中添加水印和插入视频片段功能。

## 核心功能

### 1. 视频水印功能
- [x] **图片水印**：支持PNG透明背景图片
- [x] **文字水印**：自定义文字、字体、颜色、大小
- [ ] 水印位置：支持9个常见位置（左上、中上、右上、左中、中心、右中、左下、中下、右下）
- [ ] 水印透明度调节
- [ ] 水印持续时间设置（指定开始和结束时间）
- [ ] 多段水印支持（不同时间段不同水印）

### 2. 视频插入功能
- [x] **插入整个视频片段**：在主视频的指定时间点插入另一个完整视频
- [ ] 插入位置：指定时间戳（秒或HH:MM:SS格式）
- [ ] 自动调整分辨率和帧率（可选）
- [ ] 音频合并选项（保留主音频/插入音频/混合）

### 3. 命令行接口（CLI）
**水印命令**：
```bash
video_tool.exe watermark \
  --input input.mp4 \
  --output output.mp4 \
  --watermark logo.png \
  --position top-right \
  --opacity 0.8 \
  --start-time 0 \
  --end-time 60
```

文字水印：
```bash
video_tool.exe watermark-text \
  --input input.mp4 \
  --output output.mp4 \
  --text "Copyright 2025" \
  --font-size 24 \
  --color white \
  --position bottom-right
```

**插入命令**：
```bash
video_tool.exe insert \
  --main main.mp4 \
  --insert insert.mp4 \
  --output output.mp4 \
  --position 30s \
  --audio-mode mix
```

### 4. UI界面
- 使用PyQt6或Dear PyGui构建
- 支持文件拖拽
- 实时预览（首帧截图）
- 可视化时间轴
- 参数配置面板
- 批量处理队列

### 5. 跨平台支持
- **Windows**：生成.exe可执行文件，支持Windows 10/11
- **Linux**：生成.bin可执行文件，支持Ubuntu 20.04+
- **依赖管理**：使用FFmpeg，自动检测或提示安装

### 6. 打包部署
- 使用PyInstaller打包
- 单文件可执行程序
- 包含必要的依赖库

## 技术栈
- 核心库：MoviePy（基于FFmpeg）
- CLI框架：Click或argparse
- UI框架：PyQt6（推荐）或Dear PyGui
- 打包工具：PyInstaller

## 项目结构
```
video-watermark-tool/
├── src/
│   ├── __init__.py
│   ├── main.py                  # 主入口
│   ├── cli.py                   # 命令行接口
│   ├── ui.py                    # UI界面
│   ├── watermark/               # 水印模块
│   │   ├── __init__.py
│   │   ├── image_watermark.py
│   │   └── text_watermark.py
│   ├── insert/                  # 视频插入模块
│   │   ├── __init__.py
│   └── └── video_insert.py
├── resources/                   # 资源文件
│   ├── fonts/                   # 字体文件
│   └── samples/                 # 示例文件
├── tests/                       # 测试文件
├── build/                       # 打包配置
├── requirements.txt
├── README.md
└── Claude.md                    # 本项目文档
```

## 开发计划

### 第一阶段：核心功能
- [ ] 实现基础视频水印功能
- [ ] 实现基础视频插入功能
- [ ] 添加CLI命令行接口

### 第二阶段：UI开发
- [ ] 设计UI界面
- [ ] 实现文件选择和预览
- [ ] 集成核心功能

### 第三阶段：跨平台适配
- [ ] Windows测试和打包
- [ ] Linux测试和打包
- [ ] 依赖管理优化

### 第四阶段：优化和文档
- [ ] 性能优化
- [ ] 错误处理和日志
- [ ] 完整文档和示例

## 环境要求
- Python 3.8+
- FFmpeg 4.0+

## 依赖包
```
moviepy>=1.0.3
pillow>=9.0.0
numpy>=1.21.0
click>=8.0.0
PyQt6>=6.4.0  # UI版本
PyInstaller>=5.0
```

## 备注
- 支持常见视频格式：mp4, avi, mov, mkv等
- 水印图片建议使用PNG格式以支持透明背景
- 处理大文件时可能需要足够的内存空间
