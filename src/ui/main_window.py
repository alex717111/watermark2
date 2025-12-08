"""主窗口模块"""

import sys
import os
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
    QTabWidget, QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QListWidget, QProgressBar, QTextEdit,
    QSplitter, QFrame, QScrollArea, QStackedLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QIcon, QColor
from PyQt6.QtWidgets import QColorDialog

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.watermark import add_image_watermark, add_text_watermark
from src.insert import insert_video
from src.logger_config import setup_logger
from src.cli import POSITIONS


# 中文位置到元组的映射（已弃用，仅用于旧数据兼容）
POSITION_MAP = {
    '左上': ('left', 'top'),
    '中上': ('center', 'top'),
    '右上': ('right', 'top'),
    '左中': ('left', 'center'),
    '正中': ('center', 'center'),
    '右中': ('right', 'center'),
    '左下': ('left', 'bottom'),
    '中下': ('center', 'bottom'),
    '右下': ('right', 'bottom'),
}


def _convert_position_value(position_value):
    """将UI的英文位置值转换为位置元组"""
    if position_value in POSITIONS:
        return POSITIONS[position_value]
    # 如果已经是元组格式（旧数据兼容）或中文（非常旧的UI），直接返回
    if position_value in POSITION_MAP:
        return POSITION_MAP[position_value]
    return position_value

# 设置日志
logger = setup_logger('video_watermark_ui')


class ColorButton(QPushButton):
    """颜色选择按钮"""

    def __init__(self, color="#FFFFFF", parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.set_color(self.color)
        self.clicked.connect(self.choose_color)

    def set_color(self, color):
        """设置颜色"""
        self.color = QColor(color)
        # 固定背景色为白色，固定字体颜色为黑色，确保任何颜色值都清晰可见
        self.setStyleSheet("background-color: #FFFFFF; border: 1px solid #555; min-height: 20px; color: #000000;")
        self.setText(self.color.name())

    def get_color(self):
        """获取颜色名称"""
        return self.color.name()

    def choose_color(self):
        """弹出颜色选择器"""
        color = QColorDialog.getColor(self.color, self, "选择颜色")
        if color.isValid():
            self.set_color(color)


class ProcessingThread(QThread):
    """处理线程类"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, task_type, params):
        super().__init__()
        self.task_type = task_type
        self.params = params
        self.logger = logging.getLogger('video_watermark_ui')

    def run(self):
        try:
            self.logger.info(f"后台线程开始处理: {self.task_type}")

            if self.task_type == 'watermark':
                self.logger.debug("调用图片水印函数")
                add_image_watermark(**self.params)
            elif self.task_type == 'watermark_text':
                self.logger.debug("调用文字水印函数")
                add_text_watermark(**self.params)
            elif self.task_type == 'insert':
                self.logger.debug("调用视频插入函数")
                insert_video(**self.params)

            self.logger.info("后台线程处理完成")
            self.finished.emit(True, "处理完成！")
        except Exception as e:
            self.logger.exception(f"后台线程处理失败: {str(e)}")
            self.finished.emit(False, str(e))


class VideoWatermarkWindow(QMainWindow):
    """视频水印工具主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频水印工具 v1.0")
        self.setMinimumSize(1200, 800)
        self.logger = logging.getLogger('video_watermark_ui')

        # 取消标志
        self.cancel_requested = False

        self.logger.info("=" * 60)
        self.logger.info("UI界面启动")
        self.logger.info(f"窗口大小: {self.size().width()}x{self.size().height()}")

        # 初始化UI
        self.init_ui()

        self.logger.info("UI初始化完成")

    def init_ui(self):
        """初始化UI（简洁版）"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setSpacing(15)

        # 功能选择（简化版）
        self.create_function_selection()

        # 主面板（中间的所有内容）
        main_panel = self.create_main_panel()
        self.main_layout.addWidget(main_panel)

        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")

        # 设置窗口接受拖拽
        self.setAcceptDrops(True)

        # 初始化显示文字水印参数（默认功能）
        self.on_function_changed(0)

    def create_function_selection(self):
        """创建功能选择区域（简化版） - 仅保留文字水印，隐藏选择控件"""
        # 功能选择标签
        func_label = QLabel("文字水印工具")
        func_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #1976D2;")
        self.main_layout.addWidget(func_label)

        # 隐藏功能选择下拉菜单（只保留文字水印，不需要切换）
        self.function_combo = QComboBox()
        self.function_combo.setMinimumHeight(40)
        self.function_combo.addItems(["📝 文字水印"])  # 只保留文字水印
        self.function_combo.setCurrentIndex(0)
        self.function_combo.currentIndexChanged.connect(self.on_function_changed)
        self.function_combo.setVisible(False)  # 隐藏下拉菜单
        self.main_layout.addWidget(self.function_combo)

    def create_main_panel(self):
        """创建主面板（简洁版）"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # 文件选择区域
        file_group = self.create_file_selection_area()
        layout.addWidget(file_group)

        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # 功能参数配置
        self.function_params_widget = QWidget()
        self.function_params_layout = QStackedLayout(self.function_params_widget)

        # 图片水印参数
        self.image_tab = self.create_image_watermark_tab()
        self.function_params_layout.addWidget(self.image_tab)

        # 文字水印参数
        self.text_tab = self.create_text_watermark_tab()
        self.function_params_layout.addWidget(self.text_tab)

        # 插入视频参数
        self.insert_tab = self.create_insert_video_tab()
        self.function_params_layout.addWidget(self.insert_tab)

        layout.addWidget(self.function_params_widget)

        # 添加分隔线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setToolTip("显示处理进度")
        layout.addWidget(self.progress_bar)

        # 处理按钮
        self.btn_process = QPushButton("🚀 开始处理")
        self.btn_process.clicked.connect(self.start_processing)
        self.btn_process.setMinimumHeight(45)
        self.btn_process.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.btn_process)

        return panel

    def create_file_selection_area(self):
        """创建文件选择区域"""
        group = QGroupBox("文件选择（支持拖拽文件或文件夹）")
        layout = QVBoxLayout()

        # 输入文件
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("输入视频："))
        self.input_edit = QLineEdit()
        self.input_edit.setAcceptDrops(True)
        self.input_edit.setPlaceholderText("拖拽视频文件或文件夹到这里，或点击浏览...")
        input_layout.addWidget(self.input_edit)

        self.btn_browse_input = QPushButton("📁 浏览...")
        self.btn_browse_input.clicked.connect(lambda: self.browse_file('input'))
        input_layout.addWidget(self.btn_browse_input)

        # 添加选择文件夹按钮
        self.btn_browse_folder = QPushButton("📂 选择文件夹...")
        self.btn_browse_folder.clicked.connect(lambda: self.browse_file('input_folder'))
        input_layout.addWidget(self.btn_browse_folder)

        layout.addLayout(input_layout)

        # 输出文件
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出视频："))
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("自动生成为 输入文件名_wmarked.mp4")
        output_layout.addWidget(self.output_edit)

        self.btn_browse_output = QPushButton("📁 浏览...")
        self.btn_browse_output.clicked.connect(lambda: self.browse_file('output'))
        output_layout.addWidget(self.btn_browse_output)

        layout.addLayout(output_layout)

        # 水印图片（仅在图片水印标签页显示）
        self.watermark_layout = QHBoxLayout()
        self.watermark_layout.addWidget(QLabel("水印图片："))
        self.watermark_edit = QLineEdit()
        self.watermark_edit.setAcceptDrops(True)
        self.watermark_edit.setPlaceholderText("拖拽PNG水印图片到这里...")
        self.watermark_layout.addWidget(self.watermark_edit)

        self.btn_browse_watermark = QPushButton("📁 浏览...")
        self.btn_browse_watermark.clicked.connect(lambda: self.browse_file('watermark'))
        self.watermark_layout.addWidget(self.btn_browse_watermark)

        layout.addLayout(self.watermark_layout)

        group.setLayout(layout)
        return group

    def create_image_watermark_tab(self):
        """创建图片水印参数标签页"""
        widget = QWidget()
        layout = QFormLayout()

        # 模式选择
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["全尺寸模式（推荐）", "缩放模式（兼容）"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        layout.addRow("处理模式：", self.mode_combo)

        # 缩放模式下的参数
        self.scaled_params_widget = QWidget()
        scaled_layout = QFormLayout(self.scaled_params_widget)

        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(0.0, 1.0)
        self.opacity_spin.setValue(0.9)
        self.opacity_spin.setSingleStep(0.1)
        scaled_layout.addRow("透明度：", self.opacity_spin)

        self.scaled_params_widget.setEnabled(False)
        layout.addRow(self.scaled_params_widget)

        # 时间范围
        self.start_time_edit = QLineEdit("0")
        layout.addRow("开始时间：", self.start_time_edit)

        self.end_time_edit = QLineEdit()
        layout.addRow("结束时间（留空则为视频结尾）：", self.end_time_edit)

        widget.setLayout(layout)
        return widget

    def create_text_watermark_tab(self):
        """创建文字水印参数标签页"""
        widget = QWidget()
        layout = QFormLayout()

        # 水印文字
        self.text_edit = QLineEdit("Sample Watermark")
        layout.addRow("水印文字：", self.text_edit)

        # 字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 200)
        self.font_size_spin.setValue(48)
        layout.addRow("字体大小：", self.font_size_spin)

        # 文字颜色（使用颜色选择器）
        self.color_button = ColorButton("white")
        layout.addRow("文字颜色：", self.color_button)

        # 描边宽度
        self.stroke_width_spin = QSpinBox()
        self.stroke_width_spin.setRange(0, 10)
        self.stroke_width_spin.setValue(2)
        layout.addRow("描边宽度：", self.stroke_width_spin)

        # 描边颜色（使用颜色选择器）
        self.stroke_color_button = ColorButton("black")
        layout.addRow("描边颜色：", self.stroke_color_button)

        # 透明度
        self.text_opacity_spin = QDoubleSpinBox()
        self.text_opacity_spin.setRange(0.0, 1.0)
        self.text_opacity_spin.setValue(0.9)
        self.text_opacity_spin.setSingleStep(0.1)
        layout.addRow("透明度：", self.text_opacity_spin)

        # 位置选择（显示中文，内部使用英文值）
        self.position_combo = QComboBox()
        position_items = [
            ("左上", "top-left"),
            ("中上", "top-center"),
            ("右上", "top-right"),
            ("左中", "center-left"),
            ("正中", "center"),
            ("右中", "center-right"),
            ("左下", "bottom-left"),
            ("中下", "bottom-center"),
            ("右下", "bottom-right")
        ]
        for display_text, internal_value in position_items:
            self.position_combo.addItem(display_text, internal_value)
        self.position_combo.setCurrentText("右下")  # 默认右下
        layout.addRow("水印位置：", self.position_combo)

        # 垂直留空
        self.vertical_margin_spin = QSpinBox()
        self.vertical_margin_spin.setRange(0, 50)
        self.vertical_margin_spin.setValue(10)
        self.vertical_margin_spin.setSingleStep(5)
        self.vertical_margin_spin.setSuffix(" 像素")
        layout.addRow("垂直留空：", self.vertical_margin_spin)

        widget.setLayout(layout)
        return widget

    def create_insert_video_tab(self):
        """创建插入视频参数标签页"""
        widget = QWidget()
        layout = QFormLayout()

        # 插入视频文件
        self.insert_video_edit = QLineEdit()
        self.insert_video_edit.setPlaceholderText("选择要插入的视频文件...")
        layout.addRow("插入视频：", self.insert_video_edit)

        self.btn_browse_insert = QPushButton("📁 浏览...")
        self.btn_browse_insert.clicked.connect(lambda: self.browse_file('insert'))
        layout.addRow("", self.btn_browse_insert)

        # 插入位置
        self.insert_position_edit = QLineEdit("30")
        layout.addRow("插入位置（秒）：", self.insert_position_edit)

        # 音频模式
        self.audio_mode_combo = QComboBox()
        self.audio_mode_combo.addItems(["keep", "replace", "mix", "mute"])
        layout.addRow("音频模式：", self.audio_mode_combo)

        widget.setLayout(layout)
        return widget

    def on_function_changed(self, index):
        """功能选择改变事件 - 简化版：只显示文字水印"""
        self.logger.info(f"UI: 功能选择切换到索引: {index}")
        # 只显示文字水印参数（索引1）
        self.function_params_layout.setCurrentIndex(1)

        # 隐藏水印文件选择相关控件
        self.watermark_layout.itemAt(0).widget().setVisible(False)
        self.watermark_edit.setVisible(False)
        self.btn_browse_watermark.setVisible(False)

    def on_mode_changed(self, index):
        """处理模式切换"""
        is_fullsize = index == 0
        self.scaled_params_widget.setEnabled(not is_fullsize)

    def browse_file(self, file_type):
        """浏览文件"""
        self.logger.debug(f"浏览文件类型: {file_type}")

        if file_type == 'input':
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择输入视频", "", "视频文件 (*.mp4 *.avi *.mov *.mkv *.webm);;所有文件 (*.*)"
            )
            if file_path:
                self.logger.info(f"选择输入视频: {file_path}")
                self.input_edit.setText(file_path)
                # 自动生成输出文件名
                if not self.output_edit.text():
                    path = Path(file_path)
                    output_path = path.parent / f"{path.stem}_wmarked.mp4"
                    self.output_edit.setText(str(output_path))
                    self.logger.info(f"自动生成输出路径: {output_path}")

        elif file_type == 'input_folder':
            folder_path = QFileDialog.getExistingDirectory(
                self, "选择包含视频的文件夹"
            )
            if folder_path:
                self.logger.info(f"选择输入文件夹: {folder_path}")
                self.input_edit.setText(folder_path)
                # 自动生成输出文件夹
                if not self.output_edit.text():
                    path = Path(folder_path)
                    output_path = path.parent / f"{path.name}_wmarked"
                    self.output_edit.setText(str(output_path))
                    self.logger.info(f"自动生成输出文件夹: {output_path}")

        elif file_type == 'output':
            file_path, _ = QFileDialog.getSaveFileName(
                self, "选择输出视频", "", "MP4文件 (*.mp4);;所有文件 (*.*)"
            )
            if file_path:
                self.logger.info(f"选择输出视频: {file_path}")
                self.output_edit.setText(file_path)

        elif file_type == 'watermark':
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择水印图片", "", "图片文件 (*.png *.jpg *.jpeg);;所有文件 (*.*)"
            )
            if file_path:
                self.logger.info(f"选择水印图片: {file_path}")
                self.watermark_edit.setText(file_path)

        elif file_type == 'insert':
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择插入视频", "", "视频文件 (*.mp4 *.avi *.mov *.mkv *.webm);;所有文件 (*.*)"
            )
            if file_path:
                self.logger.info(f"选择插入视频: {file_path}")
                self.insert_video_edit.setText(file_path)

    def start_processing(self):
        """开始处理"""
        self.logger.info("UI: 用户点击开始处理按钮")

        # 验证输入
        if not self.input_edit.text():
            self.logger.warning("UI: 未选择输入视频文件")
            QMessageBox.warning(self, "警告", "请选择输入视频文件或文件夹！")
            return

        input_path = Path(self.input_edit.text())

        # 检查输入是文件还是文件夹
        if input_path.is_file():
            self.logger.debug("UI: 输入类型是单个文件")
            # 检查输出路径是否设置
            if not self.output_edit.text():
                self.logger.warning("UI: 未选择输出视频文件")
                QMessageBox.warning(self, "警告", "请选择输出视频文件路径！")
                return
            output_path = self.output_edit.text()
        elif input_path.is_dir():
            self.logger.debug("UI: 输入类型是文件夹")
            # 自动生成输出文件夹路径
            output_path = str(input_path.parent / f"{input_path.name}_wmarked")
            msg = QMessageBox.question(
                self,
                "批量处理确认",
                f"输入路径是一个文件夹: {input_path.name}\n"
                f"将批量处理所有视频文件到: {Path(output_path).name}\n"
                f"是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if msg != QMessageBox.StandardButton.Yes:
                self.logger.info("UI: 用户取消批量处理")
                return
        else:
            QMessageBox.warning(self, "警告", "输入路径不存在！")
            return

        # 获取当前功能索引
        current_tab = self.function_params_layout.currentIndex()
        self.logger.debug(f"UI: 当前功能索引: {current_tab}")

        # 处理单个文件
        if input_path.is_file():
            self.logger.debug("UI: 进入单文件处理模式")

            if current_tab == 0:  # 图片水印
                if not self.watermark_edit.text():
                    QMessageBox.warning(self, "警告", "请选择水印图片文件！")
                    return

                position_value = self.position_combo.currentData()
                position_tuple = _convert_position_value(position_value)
                params = {
                    'video_path': str(input_path),
                    'watermark_path': self.watermark_edit.text(),
                    'output_path': output_path,
                    'opacity': self.opacity_spin.value(),
                    'start_time': float(self.start_time_edit.text() or 0),
                    'position': position_tuple,
                }

                if self.end_time_edit.text():
                    params['end_time'] = float(self.end_time_edit.text())

                task_type = 'watermark'

            elif current_tab == 1:  # 文字水印
                position_value = self.position_combo.currentData()
                position_tuple = _convert_position_value(position_value)
                params = {
                    'video_path': str(input_path),
                    'text': self.text_edit.text(),
                    'output_path': output_path,
                    'font_size': self.font_size_spin.value(),
                    'color': self.color_button.get_color(),
                    'opacity': self.text_opacity_spin.value(),
                    'stroke_width': self.stroke_width_spin.value(),
                    'stroke_color': self.stroke_color_button.get_color(),
                    'position': position_tuple,
                }

                if self.end_time_edit.text():
                    params['end_time'] = float(self.end_time_edit.text())

                task_type = 'watermark_text'

            else:  # 插入视频
                if not self.insert_video_edit.text():
                    QMessageBox.warning(self, "警告", "请选择要插入的视频文件！")
                    return

                params = {
                    'main_video_path': str(input_path),
                    'insert_video_path': self.insert_video_edit.text(),
                    'output_path': output_path,
                    'insert_position': float(self.insert_position_edit.text()),
                    'audio_mode': self.audio_mode_combo.currentText(),
                }

                task_type = 'insert'

            self.logger.info(f"UI: 准备启动后台线程，任务类型: {task_type}")
            self.logger.debug(f"UI: 参数: {params}")

            # 禁用处理按钮
            self.btn_process.setEnabled(False)
            self.btn_process.setText("⏳ 处理中...")
            self.status_bar.showMessage("正在处理...")

            # 启动处理线程
            self.logger.info("UI: 启动处理线程")
            self.processing_thread = ProcessingThread(task_type, params)
            self.processing_thread.finished.connect(self.on_processing_finished)
            self.processing_thread.start()

        else:  # 处理文件夹
            self.logger.debug("UI: 进入批量处理模式")

            # 扫描文件夹中的视频文件
            video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
            video_files_to_process = []

            for ext in video_extensions:
                video_files_to_process.extend(input_path.glob(f"*{ext}"))

            if not video_files_to_process:
                QMessageBox.warning(self, "警告", "文件夹中没有找到视频文件！")
                return

            self.logger.info(f"UI: 找到 {len(video_files_to_process)} 个视频文件需要处理")

            # 确保输出文件夹存在
            Path(output_path).mkdir(parents=True, exist_ok=True)
            self.logger.info(f"UI: 输出文件夹已创建/已存在: {output_path}")

            # 初始化批量处理状态
            self.cancel_requested = False

            # 禁用按钮
            self.btn_process.setEnabled(False)
            self.btn_process.setText("⏳ 批量处理中...")
            self.btn_browse_input.setEnabled(False)
            self.btn_browse_folder.setEnabled(False)
            self.status_bar.showMessage("批量处理中...")

            # 清空进度条
            self.progress_bar.setValue(0)

            # 批量处理每个视频
            success_count = 0
            fail_count = 0

            for i, video_file in enumerate(video_files_to_process):
                # 检查是否请求取消
                if self.cancel_requested:
                    self.logger.info("UI: 用户请求取消批量处理")
                    self.status_bar.showMessage("批量处理已取消")
                    break

                try:
                    self.logger.info(f"处理第 {i+1}/{len(video_files_to_process)} 个视频: {video_file}")
                    self.status_bar.showMessage(f"处理中: {video_file.name} ({i+1}/{len(video_files_to_process)})")

                    # 生成输出文件名
                    output_file_path = Path(output_path) / f"{video_file.stem}_wmarked.mp4"

                    # 根据当前标签页准备参数并处理
                    if current_tab == 0:  # 图片水印
                        position_value = self.position_combo.currentData()
                        position_tuple = _convert_position_value(position_value)
                        params = {
                            'video_path': str(video_file),
                            'watermark_path': self.watermark_edit.text(),
                            'output_path': str(output_file_path),
                            'opacity': self.opacity_spin.value(),
                            'start_time': float(self.start_time_edit.text() or 0),
                            'position': position_tuple,
                        }
                        if self.end_time_edit.text():
                            params['end_time'] = float(self.end_time_edit.text())
                        add_image_watermark(**params)

                    elif current_tab == 1:  # 文字水印
                        position_value = self.position_combo.currentData()
                        position_tuple = _convert_position_value(position_value)
                        params = {
                            'video_path': str(video_file),
                            'text': self.text_edit.text(),
                            'output_path': str(output_file_path),
                            'font_size': self.font_size_spin.value(),
                            'color': self.color_button.get_color(),  # 使用颜色选择器
                            'opacity': self.text_opacity_spin.value(),
                            'stroke_width': self.stroke_width_spin.value(),
                            'stroke_color': self.stroke_color_button.get_color(),  # 使用颜色选择器
                            'position': position_tuple,  # 使用转换后的元组
                            'margin': self.vertical_margin_spin.value(),  # 参数名改为 margin（与新的 PIL 实现兼容）
                        }
                        if self.end_time_edit.text():
                            params['end_time'] = float(self.end_time_edit.text())
                        add_text_watermark(**params)

                    else:  # 插入视频
                        params = {
                            'main_video_path': str(video_file),
                            'insert_video_path': self.insert_video_edit.text(),
                            'output_path': str(output_file_path),
                            'insert_position': float(self.insert_position_edit.text()),
                            'audio_mode': self.audio_mode_combo.currentText(),
                        }
                        insert_video(**params)

                    success_count += 1
                    self.logger.info(f"成功处理: {video_file.name}")

                except Exception as e:
                    fail_count += 1
                    self.logger.exception(f"处理失败 {video_file.name}: {str(e)}")
                    QMessageBox.warning(self, "警告", f"处理失败: {video_file.name}\n错误: {str(e)}")

                # 更新进度条
                progress = int((i + 1) / len(video_files_to_process) * 100)
                self.progress_bar.setValue(progress)
                QApplication.processEvents()  # 处理UI事件

            # 恢复按钮状态
            self.restore_buttons()

            # 显示结果
            if self.cancel_requested:
                QMessageBox.information(self, "批量处理已取消", f"批量处理已取消！\n成功处理: {success_count} 个\n失败: {fail_count} 个")
                self.status_bar.showMessage("批量处理已取消")
                self.logger.info(f"UI: 批量处理取消, 成功: {success_count}, 失败: {fail_count}")
            elif fail_count == 0:
                QMessageBox.information(self, "完成", f"批量处理完成！\n成功: {success_count}/{len(video_files_to_process)}")
                self.status_bar.showMessage("批量处理完成")
            else:
                QMessageBox.warning(self, "完成(有错误)", f"批量处理完成！\n成功: {success_count}\n失败: {fail_count}")
                self.status_bar.showMessage(f"批量处理完成, {fail_count}个失败")

    def on_processing_finished(self, success, message):
        """处理完成回调"""
        self.btn_process.setEnabled(True)
        self.btn_process.setText("🚀 开始处理")

        if success:
            self.logger.info("UI: 处理成功")
            QMessageBox.information(self, "完成", message)
            self.status_bar.showMessage("处理完成")
        else:
            self.logger.error(f"UI: 处理失败 - {message}")
            QMessageBox.critical(self, "错误", f"处理失败：{message}")
            self.status_bar.showMessage("处理失败")

    def restore_buttons(self):
        """恢复所有按钮状态"""
        self.btn_process.setEnabled(True)
        self.btn_process.setText("🚀 开始处理")
        self.btn_browse_input.setEnabled(True)
        self.btn_browse_folder.setEnabled(True)
        self.cancel_requested = False

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.logger.info(f"拖拽接收到: {file_path}")

            if Path(file_path).is_file():
                # 单个文件
                if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                    self.input_edit.setText(file_path)
                    # 自动生成输出文件名
                    if not self.output_edit.text():
                        path = Path(file_path)
                        output_path = path.parent / f"{path.stem}_wmarked.mp4"
                        self.output_edit.setText(str(output_path))
                    self.logger.info(f"拖拽设置输入文件: {file_path}")
                else:
                    QMessageBox.warning(self, "提示", "请选择视频文件！")

            elif Path(file_path).is_dir():
                # 文件夹
                self.input_edit.setText(file_path)
                # 自动生成输出文件夹
                if not self.output_edit.text():
                    path = Path(file_path)
                    output_path = path.parent / f"{path.name}_wmarked"
                    self.output_edit.setText(str(output_path))
                self.logger.info(f"拖拽设置输入文件夹: {file_path}")
                QMessageBox.information(self, "提示", f"已选择文件夹: {Path(file_path).name}\n将批量处理所有视频文件")

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.logger.info("UI: 用户关闭窗口")

        # 如果有正在进行的处理，请求取消
        if not self.btn_process.isEnabled() and not self.cancel_requested:
            self.logger.info("UI: 检测到正在进行的处理，请求取消")
            self.cancel_requested = True
            QMessageBox.information(self, "提示", "正在取消处理，请稍候...")

        self.logger.info("=" * 60)
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle("Fusion")

    window = VideoWatermarkWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
