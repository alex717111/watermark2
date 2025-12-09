# UI 适配指南: Watermark-Combo 功能

## 概述

本文档旨在帮助UI开发者将CLI的 `watermark-combo` 功能适配到图形界面（PyQt6）。该功能支持同时添加Logo和文字水印，是推荐替代旧版 `watermark-text` 的新功能。

## 核心功能

### 1. 两种操作模式

#### 模式一: 合并模式 (推荐)
- **功能**: 将Logo和文字合并为一张图片，作为一个整体水印
- **优势**:
  - Logo自动缩放匹配文字高度
  - 间距固定且美观
  - 只需一个位置参数
  - 整体透明度统一
- **使用场景**: 绝大多数情况，特别是Logo+文字的经典组合

#### 模式二: 分离模式 (高级)
- **功能**: Logo和文字分别定位和渲染
- **优势**: 更灵活，可以放置在不同位置
- **使用场景**: 特殊布局需求，如Logo在左上角，文字在右下角

### 2. 关键参数

#### 必需参数
- `--text, -t`: 水印文字内容 (字符串，必需)

#### Logo相关参数
- `--watermark, -w`: Logo图片路径 (文件路径，可选)
- `--logo-position`: Logo位置 (9个预设位置，默认: top-left)
- `--logo-opacity`: Logo透明度 (0.0-1.0，默认: 0.9)
- `--logo-margin`: Logo边距 (整数，默认: 10)
- `--logo-width`: Logo宽度 (整数，可选)
- `--logo-height`: Logo高度 (整数，可选)
- `--logo-scale-factor`: Logo缩放因子 (浮点数，默认: 1.0)
  - 1.0 = Logo高度匹配文字高度
  - 1.2 = Logo比文字高20%
  - 0.8 = Logo比文字矮20%

#### 文字相关参数
- `--font-size`: 字体大小 (整数，默认: 24)
- `--color`: 文字颜色 (字符串，默认: white)
- `--font`: 字体文件路径 (文件路径，可选)
- `--text-opacity`: 文字透明度 (0.0-1.0，默认: 0.9) **仅分离模式有效**
- `--stroke-width`: 描边宽度 (整数，默认: 1)
- `--stroke-color`: 描边颜色 (字符串，默认: black)
- `--vertical-margin`: 垂直边距 (整数，默认: 10) **仅分离模式有效**

#### 合并模式专用参数
- `--combine-mode`: 启用合并模式 (布尔flag)
- `--combine-layout`: 合并布局 (选择: horizontal/vertical，默认: horizontal)
  - horizontal: Logo在左，文字在右
  - vertical: Logo在上，文字在下
- `--combine-spacing`: 合并间距 (整数，默认: 10)
  - Logo和文字之间的间距（像素）

#### 时间参数
- `--start-time, -s`: 水印开始时间 (字符串，默认: 0)
- `--end-time, -e`: 水印结束时间 (字符串，可选)

## UI设计建议

### 主界面布局

```
┌─────────────────────────────────────────┐
│  组合水印设置 (Watermark Combo)        │
├─────────────────────────────────────────┤
│                                         │
│  [ ] 启用Logo                          │
│      Logo文件: [选择文件...] [浏览]    │
│                                         │
│  文字内容: [_______________________]   │
│                                         │
│  操作模式:                            │
│      (○) 合并模式 (推荐)              │
│      (○) 分离模式 (高级)              │
│                                         │
│  ┌─ 合并模式设置(合并模式时显示) ─┐   │
│  │  Logo缩放: [100%] ▲▼           │   │
│  │  排列方式: (○) 水平  (○) 垂直  │   │
│  │  间距: [10] 像素                │   │
│  └────────────────────────────────┘   │
│                                         │
│  样式设置:                            │
│      字体大小: [24] ▲▼               │
│      文字颜色: [白色] [选择]         │
│      描边宽度: [1] ▲▼                │
│      描边颜色: [黑色] [选择]         │
│                                         │
│  位置和透明度:                        │
│      位置: [右下角 ▼]                │
│      透明度: [90%] ◀───┐            │
│                         ○           │
│                                         │
│  时间范围(可选):                      │
│      开始: [0] 秒                     │
│      结束: [视频结束] 秒             │
│                                         │
│  [生成预览] [应用到视频]              │
└─────────────────────────────────────────┘
```

### 模式切换逻辑

#### 当选择"合并模式"时:
- 显示 "合并模式设置" 区域
- 隐藏 "文字位置" 参数 (使用 Logo位置 作为整体位置)
- 隐藏 "文字透明度" 参数 (使用 Logo透明度 作为整体透明度)
- 隐藏 "垂直边距" 参数

#### 当选择"分离模式"时:
- 隐藏 "合并模式设置" 区域
- 显示 "文字位置" 参数
- 显示 "文字透明度" 参数
- 显示 "垂直边距" 参数

### 控件状态逻辑

1. **Logo未选择时**:
   - 禁用所有Logo相关参数
   - 模式切换不可用（默认为合并模式，但功能等同于纯文字）

2. **Logo已选择时**:
   - 启用所有参数
   - 模式切换可用

3. **实时预览**:
   - 提供 "生成预览" 按钮，快速查看水印效果
   - 预览应显示在视频帧的缩略图上

### 默认值建议

```python
{
    "text": "",
    "watermark_path": None,
    "mode": "combine",  # 推荐默认为合并模式
    "logo_position": "bottom-right",
    "logo_opacity": 0.9,
    "logo_margin": 10,
    "logo_scale_factor": 1.0,
    "font_size": 24,
    "color": "white",
    "stroke_width": 1,
    "combine_layout": "horizontal",
    "combine_spacing": 10,
    "start_time": "0",
    "end_time": None
}
```

## 代码实现参考

### 核心函数签名

```python
from watermark.combo_watermark import add_combo_watermark

add_combo_watermark(
    video_path=str,           # 输入视频路径
    output_path=str,          # 输出视频路径
    text=str,                 # 文字内容（必需）
    watermark_path=str|None,  # Logo路径（可选）
    combine_mode=bool,        # 是否启用合并模式
    combine_layout=str,       # 'horizontal' 或 'vertical'
    combine_spacing=int,      # 间距（像素）
    # ... 其他参数
)
```

### UI调用示例

```python
def apply_combo_watermark(self):
    """应用组合水印"""
    # 获取参数
    params = {
        'video_path': self.input_video_path.text(),
        'output_path': self.output_video_path.text(),
        'text': self.text_edit.toPlainText(),
        'watermark_path': self.logo_path.text() or None,
        'combine_mode': self.combine_mode_checkbox.isChecked(),
        'combine_layout': 'horizontal' if self.horizontal_radio.isChecked() else 'vertical',
        'combine_spacing': self.spacing_spinbox.value(),
        'font_size': self.font_size_spinbox.value(),
        'color': self.color_lineedit.text(),
        # ... 其他参数
    }

    # 调用处理函数
    try:
        add_combo_watermark(**params)
        QMessageBox.information(self, "成功", "水印添加完成！")
    except Exception as e:
        QMessageBox.critical(self, "错误", f"处理失败: {str(e)}")
```

## 测试验证

### 关键测试用例

1. **test_functional_watermark_combo_text**: 仅文字水印
2. **test_functional_watermark_combo_logo**: Logo+文字（合并模式）
3. **test_functional_watermark_combo_combined**: 合并模式测试
4. **test_functional_watermark_combo_combined_vertical**: 垂直合并模式
5. **test_functional_watermark_combo_combined_custom**: 自定义缩放和间距
6. **test_functional_watermark_combo_separate**: 分离模式（高级）

### 运行测试

```bash
# 运行所有CLI测试
python tests/test_cli.py

# 运行组合水印单元测试
python -m pytest tests/test_combo_watermark.py -v

# 运行特定测试
python -m pytest tests/test_cli.py::test_functional_watermark_combo_logo -v
```

## 常见问题

### Q: 为什么推荐使用合并模式？
A: 合并模式将Logo和文字作为一个整体处理，具有以下优势：
- Logo自动缩放匹配文字高度，无需手动调整
- 间距固定且美观
- 只需一个位置参数，操作简单
- 整体透明度统一控制

### Q: 什么情况下使用分离模式？
A: 分离模式适合特殊布局需求，例如：
- Logo固定在左上角，文字在右下角
- 需要完全不同的透明度和样式
- 复杂的分散式水印布局

### Q: Logo缩放因子如何工作？
A: 默认(1.0)时Logo高度自动匹配文字高度。设置为1.2时Logo比文字高20%，0.8时矮20%。配合`--combine-spacing`可以调整整体视觉效果。

### Q: 垂直排列什么时候用？
A: 当Logo形状为方形或竖版，或者希望水印占用更少水平空间时使用。设置为`--combine-layout vertical`即可启用。

## 向后兼容

- 旧版 `watermark-text` 命令仍然可用，但推荐使用 `watermark-combo` 替代
- 新版同时支持Logo+文字组合和纯文字水印
- UI可以设计为平滑迁移，当用户不选择Logo时，功能等同于旧版文字水印

## 文档链接

- 完整README: [README.md](../README.md)
- CLI测试文件: [tests/test_cli.py](../tests/test_cli.py)
- 单元测试文件: [tests/test_combo_watermark.py](../tests/test_combo_watermark.py)
- 实现源码: [src/watermark/combo_watermark.py](../src/watermark/combo_watermark.py)
