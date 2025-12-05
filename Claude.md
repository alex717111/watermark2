# 视频水印工具项目需求文档

## 项目概述
创建一个跨平台的视频处理工具，支持向视频中添加水印和插入视频片段功能。

## 项目状态
**当前阶段**: ✅ 第一阶段 - CLI版本已完成（重大更新：全尺寸水印成为默认行为）
**完成状态**: 核心功能全部实现，测试通过
**最近更新**: 2025-12-05 - 图片水印默认使用全尺寸模式（`--scaled`参数保留旧行为）

## 核心功能

### 1. 视频水印功能
- [x] **图片水印**：支持PNG透明背景图片（默认全尺寸模式，推荐使用与视频同尺寸的水印图片）
- [x] **文字水印**：自定义文字、字体、颜色、大小、描边效果
- [x] **水印位置**：支持9个常见位置（仅缩放模式有效）
- [x] **水印透明度调节**：支持0.0-1.0透明度设置
- [x] **水印持续时间设置**：支持指定开始和结束时间
- [x] **尺寸调整**：支持自定义水印宽度和高度（仅缩放模式有效）
- [x] **全尺寸水印模式**：水印图片与视频同尺寸，位置由图片本身决定（推荐，默认行为）
- [x] **缩放模式**：兼容旧版本行为，水印缩放到视频宽度的1/6
- [ ] 多段水印支持（不同时间段不同水印）

**推荐用法**: 创建与视频同尺寸的PNG图片作为水印，在图像编辑软件中精确设计水印位置和效果，支持复杂图文组合、渐变、阴影等高级效果。对于简单logo，可使用缩放模式。

### 2. 视频插入功能
- [x] **插入整个视频片段**：在主视频的指定时间点插入另一个完整视频
- [x] **插入位置**：支持秒数、HH:MM:SS格式、1.5h、30m等多种时间格式
- [x] **自动分辨率适配**：自动调整插入视频分辨率匹配主视频
- [x] **音频处理选项**：支持keep（保留主音频）、replace（替换）、mix（混合）、mute（静音）
- [x] **交叉淡入淡出**：支持设置交叉过渡时长

### 3. 命令行接口（CLI）
已实现以下命令，全部通过测试：

**图片水印命令**:
```bash
# 默认全尺寸模式（推荐，水印图片与视频同尺寸）
python main.py watermark \
  -i input.mp4 \
  -o output.mp4 \
  -w watermark.png \
  --opacity 0.9

# 缩放模式（兼容旧版本，水印缩放到视频宽度1/6）
python main.py watermark \
  -i input.mp4 \
  -o output.mp4 \
  -w logo.png \
  --scaled \
  -p bottom-right \
  --opacity 0.8 \
  --margin 20
```

**文字水印命令**:
```bash
python main.py watermark-text \
  -i input.mp4 \
  -o output.mp4 \
  -t "Copyright 2025" \
  -p top-right \
  --font-size 36 \
  --color white \
  --stroke-width 2 \
  --opacity 0.9
```

**插入视频命令**:
```bash
python main.py insert \
  -m main.mp4 \
  -i insert.mp4 \
  -o output.mp4 \
  -p 30 \
  --audio-mode mix \
  --crossfade 1.0
```

**辅助命令**:
```bash
python main.py positions    # 查看所有可用位置（缩放模式有效）
python main.py --help       # 查看主帮助
python main.py COMMAND --help  # 查看具体命令帮助
```

### 4. UI界面（待开发）
- [ ] 使用PyQt6或Dear PyGui构建
- [ ] 支持文件拖拽
- [ ] 实时预览（首帧截图）
- [ ] 可视化时间轴
- [ ] 参数配置面板
- [ ] 批量处理队列
- [ ] 水印图片可视化编辑器

### 5. 跨平台支持
- [x] **虚拟环境支持**：Python 3.12，提供setup_venv.sh和setup_venv.bat
- [x] **依赖管理**：requirements.txt包含所有依赖
- [ ] **Windows**：生成.exe可执行文件（待测试）
- [ ] **Linux**：生成.bin可执行文件（待测试）

### 6. 打包部署
- [x] PyInstaller配置（build/pyinstaller.spec）
- [x] Windows打包脚本（build/build_windows.bat）
- [x] Linux打包脚本（build/build_linux.sh）
- [ ] 生成可执行文件并测试

## 技术栈
- **核心库**：MoviePy 2.x（基于FFmpeg）
  - 已适配MoviePy 2.x API变更（set_*→with_*，fx→with_effects）
- **CLI框架**：Click 9.0+
- **测试框架**：pytest 9.0+
- **虚拟环境**：venv（Python 3.12）
- **打包工具**：PyInstaller 6.0+
- **图像处理**：Pillow 11.0+

## 项目结构
```
video-watermark-tool/
├── src/                          # 源代码
│   ├── __init__.py
│   ├── main.py                  # 主入口（使用runpy解决相对导入）
│   ├── cli.py                   # CLI接口（Click框架）
│   ├── watermark/               # 水印模块
│   │   ├── __init__.py
│   │   ├── image_watermark.py   # 图片水印实现（支持全尺寸模式）
│   │   └── text_watermark.py    # 文字水印实现
│   └── insert/                  # 视频插入模块
│       ├── __init__.py
│       └── video_insert.py      # 视频插入实现
├── resources/                   # 资源文件
│   ├── fonts/                   # 字体文件
│   └── samples/                 # 示例文件
├── tests/                       # 测试文件
│   └── test_cli.py              # CLI功能测试
├── build/                       # 打包配置
│   ├── pyinstaller.spec         # PyInstaller配置
│   ├── build_windows.bat        # Windows打包脚本
│   └── build_linux.sh           # Linux打包脚本
├── venv/                        # 虚拟环境（自动创建）
├── requirements.txt             # 项目依赖
├── main.py                      # 程序入口
├── .gitignore                   # Git忽略规则
├── setup_venv.sh                # Linux虚拟环境设置脚本
├── setup_venv.bat               # Windows虚拟环境设置脚本
├── test_example.py              # 示例演示脚本
├── TEST_GUIDE.md                # 测试指南
├── TEST_REPORT.md               # 测试报告
├── QUICKSTART.md                # 快速启动指南
├── PROJECT_SUMMARY.md           # 项目总结
├── README.md                    # 使用文档
├── Claude.md                    # 本项目文档
├── BREAKING_CHANGES.md          # 重大变更说明（2025-12-05）
├── FULLSIZE_MODE_GUIDE.md       # 全尺寸模式详细指南
└── USAGE_SUMMARY.md             # 图片水印功能完善总结
```

## 开发计划

### 第一阶段：核心功能 ✅ 已完成
- [x] 实现基础视频水印功能（图片和文字）
- [x] 实现基础视频插入功能
- [x] 添加CLI命令行接口（Click框架）
- [x] 适配MoviePy 2.x API变更
- [x] 解决相对导入问题（使用runpy模块）
- [x] 创建虚拟环境配置脚本
- [x] 编写单元测试（pytest）
- [x] 所有测试通过（5/5）

**测试覆盖**：
- 测试1: 主命令帮助信息 ✅
- 测试2: 位置选项列表 ✅
- 测试3: 图片水印命令帮助 ✅
- 测试4: 文字水印命令帮助 ✅
- 测试5: 插入视频命令帮助 ✅

### 第二阶段：功能验证和优化（进行中）
- [x] **优化图片水印功能**：全尺寸水印成为默认行为（2025-12-05）
  - [x] CLI接口变更（移除`--fullsize`，添加`--scaled`）
  - [x] 更新文档（README.md, Claude.md）
  - [x] 适配测试（test_cli.py）
  - [x] 编写迁移指南（BREAKING_CHANGES.md）
  - [x] 创建全尺寸水印工具（create_fullsize_watermark_demo.py）
- [ ] 使用实际视频文件测试全尺寸水印功能
- [ ] 使用实际视频文件测试视频插入功能
- [ ] 性能优化（大文件处理）
- [ ] 错误处理和用户反馈优化
- [ ] 添加日志系统

### 第三阶段：UI开发
- [ ] 选择UI框架（PyQt6推荐）
- [ ] 设计界面布局
- [ ] 实现文件拖拽和预览
- [ ] 集成核心功能到UI
- [ ] 添加可视化时间轴
- [ ] 实现批量处理队列

### 第四阶段：跨平台适配
- [ ] Windows测试和打包
- [ ] Linux测试和打包
- [ ] FFmpeg依赖自动检测
- [ ] 创建安装程序

### 第五阶段：文档和发布
- [ ] 完整的使用文档
- [ ] API文档
- [ ] 性能基准测试
- [ ] GitHub发布包
- [ ] 支持社区反馈

## 关键技术决策

### 1. MoviePy 2.x 适配
MoviePy 2.x引入了破坏性变更，已进行适配：
- 导入方式：`from moviepy.editor import X` → `from moviepy import X`
- 方法命名：`.set_*()` → `.with_*()`
- 效果系统：`.fx()` → `.with_effects()`
- 变换方法：`resize()` → `resized()`, `crop()` → `cropped()`

### 2. 相对导入解决方案
使用 `runpy.run_module()` 优雅解决相对导入问题，无需修改src/目录下的代码结构。

### 3. 水印策略
**【重要更新】全尺寸水印成为默认行为（2025-12-05）**

图片水印默认使用全尺寸模式：
- 水印图片与视频同尺寸，直接叠加
- 水印的透明度、位置、效果在图片中预先设计
- 优点：
  - 支持复杂设计（渐变、阴影、多元素组合）
  - 位置精确控制，所见即所得
  - 无缩放失真，处理质量更高
- 使用方式：直接提供与视频同尺寸的PNG水印图片

保留缩放模式（兼容旧版本）：
- 使用 `--scaled` 参数启用
- 水印缩放到视频宽度的1/6
- 支持9个位置选项
- 适用于简单logo或快速处理场景

## 环境要求
- **Python版本**: 3.12+（已测试Python 3.12.11）
- **FFmpeg**: 4.0+（必须）
- **虚拟环境**: venv（推荐使用setup_venv.sh或setup_venv.bat自动配置）

## 依赖包
```
moviepy>=2.2.1           # 视频处理核心库
pillow>=11.0.0           # 图像处理
numpy>=2.3.5             # 数值计算
click>=8.3.1             # CLI框架
pytest>=9.0.1            # 测试框架
PyInstaller>=6.17.0      # 打包工具
```

## 快速开始

### 1. 创建虚拟环境（推荐）
```bash
# Linux/macOS
./setup_venv.sh

# Windows
setup_venv.bat
```

### 2. 运行测试
```bash
./venv/bin/python -m pytest tests/test_cli.py -v
```

### 3. 使用工具
```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate.bat  # Windows

# 查看帮助
python main.py --help

# 添加图片水印（默认全尺寸模式，推荐使用与视频同尺寸的水印）
python main.py watermark -i input.mp4 -o output.mp4 -w watermark.png

# 添加图片水印（缩放模式，兼容简单logo）
python main.py watermark -i input.mp4 -o output.mp4 -w logo.png --scaled -p bottom-right

# 添加文字水印
python main.py watermark-text -i input.mp4 -o output.mp4 -t "Copyright"

# 插入视频片段
python main.py insert -m main.mp4 -i insert.mp4 -o output.mp4 -p 30
```

## 测试方法

### 自动化测试
```bash
# 运行所有测试
./venv/bin/python -m pytest tests/ -v

# 直接运行测试脚本
./venv/bin/python tests/test_cli.py
```

### 功能测试
```bash
# 创建测试视频
ffmpeg -f lavfi -i testsrc=duration=10:size=1280x720:rate=30 test.mp4

# 创建测试水印图片（全尺寸模式，推荐）
# 方法：手动创建简单水印或使用专业工具创建复杂水印
python -c "
from PIL import Image, ImageDraw
img = Image.new('RGBA', (200, 80), (255, 0, 0, 128))
draw = ImageDraw.Draw(img)
draw.text((10, 10), 'WATERMARK', fill=(255, 255, 255, 255))
img.save('logo.png')
"
# 或使用Photoshop/GIMP等工具创建与视频同尺寸的PNG水印

# 测试水印功能（全尺寸模式 - 假设已有全尺寸水印）
./venv/bin/python main.py watermark -i test.mp4 -o output.mp4 -w fullsize_watermark.png

# 测试水印功能（缩放模式）
./venv/bin/python main.py watermark -i test.mp4 -o output.mp4 -w logo.png --scaled -p bottom-right
```

## 使用您的测试视频

```bash
# 激活虚拟环境后
source venv/bin/activate

# 使用全尺寸水印（需要先创建与视频同尺寸的水印图片）
# 可以使用Photoshop、GIMP等工具创建，或在测试时手动创建
./venv/bin/python main.py watermark \
  -i ~/Downloads/126.mp4 \
  -o output_watermark.mp4 \
  -w watermark_1280x720.png \
  --opacity 0.9

# 测试添加文字水印
./venv/bin/python main.py watermark-text \
  -i ~/Downloads/126.mp4 \
  -o output_text.mp4 \
  -t "Test Video" \
  -p bottom-right \
  --font-size 48
```

## 备注
- 支持常见视频格式：mp4, avi, mov, mkv, webm等
- 水印图片建议使用PNG格式（支持透明背景）
- **重要更新**：图片水印默认使用全尺寸模式（水印图片与视频同尺寸）
  - 优点：支持复杂设计（渐变、阴影、多元素），位置精确，无缩放失真
  - 如需旧行为，请使用 `--scaled` 参数
- 处理大文件时需要足够的内存空间
- 文字水印需要系统字体或TTF字体文件
- 推荐**全尺寸水印图片**方案：创建与视频同尺寸的PNG图片，在图像编辑软件中设计水印位置

## 下一步计划
1. 使用实际视频验证全尺寸水印功能
2. 使用实际视频验证插入功能
3. 性能优化（大文件处理）
4. 根据需求决定是否开发UI界面
5. 打包生成可执行文件

## 已知问题和解决方案

### 1. SSL证书问题
**问题**: pip安装时可能出现SSL证书错误
**解决**: 使用国内镜像源或配置代理

### 2. ImageMagick依赖
**问题**: 文字水印可能需要ImageMagick
**解决**:
- Linux: `sudo apt install imagemagick`
- Windows: 下载安装 https://imagemagick.org/

### 3. FFmpeg未找到
**问题**: MoviePy需要FFmpeg
**解决**:
- Linux: `sudo apt install ffmpeg`
- Windows: 下载并添加到PATH

## 最佳实践
1. **使用虚拟环境**：避免依赖冲突
2. **测试驱动**：修改后运行测试确保功能正常
3. **文档同步**：更新代码同时更新相关文档
4. **版本控制**：使用Git管理代码变更
5. **水印设计**：使用全尺寸PNG方案，在Photoshop/GIMP等工具中精确设计水印位置、透明度和效果
6. **性能考虑**：批量处理大文件时，确保系统有足够内存（全尺寸模式需要更多内存）
