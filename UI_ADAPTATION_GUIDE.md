# UI 适配指南: Watermark-Combo 功能

## 概述

本文档旨在帮助UI开发者将CLI的 `watermark-combo` 功能适配到图形界面（PyQt6）。该功能支持同时添加Logo和文字水印，是推荐替代旧版 `watermark-text` 的新功能。

## 实现状态

✅ **已完成** - 合并模式已在UI中实现

UI已经成功适配了合并模式功能，以下是实现细节：

## 核心功能

### 1. 操作模式: 合并模式 (已实现)

- **功能**: 将Logo和文字合并为一张图片，作为一个整体水印
- **优势**:
  - Logo自动缩放匹配文字高度
  - 间距固定且美观
  - 只需一个位置参数
  - 整体透明度统一
- **使用场景**: 绝大多数情况，特别是Logo+文字的经典组合

### 未来扩展: 分离模式 (计划中)
- 作为高级功能在后续版本中实现

## UI实现特性

### 实现的功能

1. **Logo选择**: 支持拖拽或浏览选择Logo文件（PNG/JPEG格式）
2. **Logo选项启用**: 当选择Logo后，自动启用Logo透明度等选项
3. **合并模式设置**: 实现了以下参数调节：
   - Logo缩放因子（0.1-5.0）
   - 排列方式（水平/垂直）
   - 间距（0-100像素）
4. **文字设置**: 保持原有的文字水印设置
5. **时间范围**: 支持设置水印开始和结束时间
6. **智能判断**: 根据是否选择Logo自动使用文字水印或组合水印

### 界面布局

```
┌─────────────────────────────────────────┐
│  Logo设置（可选）                      │
├─────────────────────────────────────────┤
│  Logo文件: [____________] [浏览]       │
│                                         │
│  Logo透明度: [0.9]                      │
├─────────────────────────────────────────┤
│  合并模式设置（推荐）                   │
├─────────────────────────────────────────┤
│  Logo缩放: [1.0 ▲▼]                     │
│  排列方式: (○) 水平  (○) 垂直           │
│  间距: [10] 像素                        │
├─────────────────────────────────────────┤
│  文字设置                              │
├─────────────────────────────────────────┤
│  水印文字: [Sample Watermark]          │
│  字体大小: [48 ▲▼]                      │
│  文字颜色: [□ #FFFFFF] [选择]          │
│  描边宽度: [2 ▲▼]                       │
│  描边颜色: [□ #000000] [选择]          │
├─────────────────────────────────────────┤
│  位置和透明度                          │
├─────────────────────────────────────────┤
│  水印位置: [右下角 ▼]                   │
│  开始时间: [0]                          │
│  结束时间: [________________] 秒       │
└─────────────────────────────────────────┘
```

### 动态行为

1. **Logo选择**:
   - 未选择Logo时：只显示文字水印设置，功能等同于原有的文字水印功能
   - 选择Logo后：启用所有Logo相关选项和合并模式设置

2. **智能处理**:
   - 无Logo：使用 `add_text_watermark` 函数
   - 有Logo：使用 `add_combo_watermark` 函数（合并模式）

3. **参数映射**:
   - Logo透明度 = 整体透明度（合并模式下）

## 关键参数映射

### 必需参数
- `--text, -t`: 水印文字内容 (字符串，必需)

### Logo相关参数
- `--watermark, -w`: Logo图片路径 (文件路径，可选) → Logo文件选择
- `--logo-opacity`: Logo透明度 (0.0-1.0) → Logo透明度微调框
- `--logo-scale-factor`: Logo缩放因子 → Logo缩放微调框

### 合并模式专用参数
- `--combine-mode`: 固定为True（始终启用合并模式）
- `--combine-layout`: 合并布局 → 排列方式下拉框
- `--combine-spacing`: 合并间距 → 间距微调框

### 文字相关参数
- `--font-size`: 字体大小 → 字体大小微调框
- `--color`: 文字颜色 → 文字颜色选择器
- `--stroke-width`: 描边宽度 → 描边宽度微调框
- `--stroke-color`: 描边颜色 → 描边颜色选择器

### 时间参数
- `--start-time, -s`: 水印开始时间 → 开始时间输入框
- `--end-time, -e`: 水印结束时间 → 结束时间输入框

## 代码实现

### 函数导入
```python
from src.watermark.combo_watermark import add_combo_watermark
```

### 处理逻辑
UI根据是否选择Logo自动判断调用哪个函数：

**纯文字水印（无Logo）**:
```python
add_text_watermark(
    video_path=video_path,
    text=text,
    output_path=output_path,
    font_size=font_size,
    color=color,
    opacity=0.9,
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    start_time=start_time,
    end_time=end_time,
    position=position
)
```

**组合水印（有Logo，合并模式）**:
```python
add_combo_watermark(
    video_path=video_path,
    output_path=output_path,
    text=text,
    watermark_path=logo_path,  # 有Logo
    combine_mode=True,         # 启用合并模式
    combine_layout='horizontal'/'vertical',
    combine_spacing=spacing,
    font_size=font_size,
    color=color,
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    start_time=start_time,
    end_time=end_time,
    logo_position=logo_position,
    logo_opacity=logo_opacity,
    logo_scale_factor=logo_scale_factor
)
```

### 处理流程
1. 用户选择视频和Logo（可选）
2. 设置文字、样式、位置等参数
3. 点击"开始处理"
4. 系统检查是否选择了Logo
5.
   - 无Logo：调用 `add_text_watermark` → 纯文字水印
   - 有Logo：调用 `add_combo_watermark` → Logo+文字组合水印（合并模式）
6. 显示处理结果

## 测试验证

### 可用的测试用例

1. **test_functional_watermark_combo_text**: 仅文字水印
2. **test_functional_watermark_combo_logo**: Logo+文字（合并模式）
3. **test_functional_watermark_combo_combined**: 合并模式测试
4. **test_functional_watermark_combo_combined_vertical**: 垂直合并模式
5. **test_functional_watermark_combo_combined_custom**: 自定义缩放和间距

### 运行测试

```bash
# 运行CLI测试
python tests/test_cli.py

# 运行组合水印单元测试
python -m pytest tests/test_combo_watermark.py -v

# 运行特定测试
python -m pytest tests/test_cli.py::test_functional_watermark_combo_logo -v
```

## 使用示例

### 场景1: 纯文字水印
1. 输入视频路径
2. 输入文字内容（如"Sample Watermark"）
3. 设置字体大小、颜色等参数
4. 不选择Logo文件
5. 点击"开始处理"

结果: 只添加文字水印

### 场景2: Logo+文字组合水印
1. 输入视频路径
2. 输入文字内容（如"My Company"）
3. 选择Logo文件（如company_logo.png）
4. 设置合并模式参数（Logo缩放、排列方式、间距）
5. 设置水印位置（Logo和文字整体位置）和Logo透明度
6. 点击"开始处理"

结果: Logo和文字合并为一张图片，作为一个整体水印添加到视频

### 场景3: 批量处理
1. 选择输入文件夹
2. 设置文字和Logo（可选）
3. 点击"开始处理"

结果: 文件夹内所有视频批量添加水印

## 常见问题

### Q: 为什么推荐使用合并模式？
A: 合并模式将Logo和文字作为一个整体处理，具有以下优势：
- Logo自动缩放匹配文字高度，无需手动调整
- 间距固定且美观
- 只需一个位置参数，操作简单
- 整体透明度统一控制

### Q: Logo缩放因子如何工作？
A: 默认(1.0)时Logo高度自动匹配文字高度。设置为1.2时Logo比文字高20%，0.8时矮20%。配合间距设置可以调整整体视觉效果。

### Q: 垂直排列什么时候用？
A: 当Logo形状为方形或竖版，或者希望水印占用更少水平空间时使用。在排列方式中选择"垂直"即可启用。

### Q: 如何实现纯文字水印？
A: 不选择Logo文件，直接输入文字内容和设置样式即可，系统自动使用文字水印功能。

## 向后兼容

- 旧版 `watermark-text` 命令仍然可用
- UI适配后同时支持Logo+文字组合和纯文字水印
- 当用户不选择Logo时，功能完全等同于旧版文字水印（平滑迁移）

## 实现文件

- UI主文件: `src/ui/main_window.py`
- CLI适配文件: `src/cli.py`
- 底层实现: `src/watermark/combo_watermark.py`
- 测试文件: `tests/test_combo_watermark.py`

## 更新日志

### 2025-12-08
- ✅ 完成合并模式UI适配
- ✅ 实现Logo文件选择和拖拽功能
- ✅ 实现合并模式参数调节（缩放、布局、间距）
- ✅ 实现智能判断（自动选择文字水印或组合水印）
- ✅ 更新批量处理支持组合水印
- ✅ 更新UI_ADAPTATION_GUIDE.md文档
