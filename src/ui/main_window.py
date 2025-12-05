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
    QSplitter, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QIcon

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.watermark import add_image_watermark, add_text_watermark
from src.insert import insert_video
from src.logger_config import setup_logger

# 设置日志
logger = setup_logger('video_watermark_ui')


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
        """初始化UI"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)

        # 左侧面板（功能选择）
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # 中间面板（预览和参数）
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 2)

        # 右侧面板（批量队列）
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)

        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")

        # 设置窗口接受拖拽
        self.setAcceptDrops(True)

    def create_left_panel(self):
        """创建左侧面板"""
        panel = QGroupBox("功能选择")
        layout = QVBoxLayout()

        # 图片水印按钮
        self.btn_image_watermark = QPushButton("📷 图片水印")
        self.btn_image_watermark.setCheckable(True)
        self.btn_image_watermark.setChecked(True)
        self.btn_image_watermark.clicked.connect(lambda: self.switch_tab(0))
        layout.addWidget(self.btn_image_watermark)

        # 文字水印按钮
        self.btn_text_watermark = QPushButton("📝 文字水印")
        self.btn_text_watermark.setCheckable(True)
        self.btn_text_watermark.clicked.connect(lambda: self.switch_tab(1))
        layout.addWidget(self.btn_text_watermark)

        # 插入视频按钮
        self.btn_insert_video = QPushButton("➕ 插入视频")
        self.btn_insert_video.setCheckable(True)
        self.btn_insert_video.clicked.connect(lambda: self.switch_tab(2))
        layout.addWidget(self.btn_insert_video)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_center_panel(self):
        """创建中间面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 文件选择区域
        file_group = self.create_file_selection_area()
        layout.addWidget(file_group)

        # 标签页（不同功能的参数配置）
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBarAutoHide(True)

        # 图片水印标签页
        self.image_tab = self.create_image_watermark_tab()
        self.tab_widget.addTab(self.image_tab, "图片水印")

        # 文字水印标签页
        self.text_tab = self.create_text_watermark_tab()
        self.tab_widget.addTab(self.text_tab, "文字水印")

        # 插入视频标签页
        self.insert_tab = self.create_insert_video_tab()
        self.tab_widget.addTab(self.insert_tab, "插入视频")

        layout.addWidget(self.tab_widget)

        # 处理按钮
        self.btn_process = QPushButton("🚀 开始处理")
        self.btn_process.clicked.connect(self.start_processing)
        self.btn_process.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
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

    def create_right_panel(self):
        """创建右侧面板"""
        panel = QGroupBox("批量处理队列")
        layout = QVBoxLayout()

        # 队列列表
        self.queue_list = QListWidget()
        self.queue_list.setAcceptDrops(True)
        self.queue_list.setDefaultDropAction(Qt.DropAction.CopyAction)
        layout.addWidget(self.queue_list)

        # 队列操作按钮
        btn_layout = QHBoxLayout()

        self.btn_add_queue = QPushButton("➕ 添加到队列")
        self.btn_add_queue.clicked.connect(self.add_to_queue)
        btn_layout.addWidget(self.btn_add_queue)

        self.btn_clear_queue = QPushButton("🗑️ 清空队列")
        self.btn_clear_queue.clicked.connect(self.clear_queue)
        btn_layout.addWidget(self.btn_clear_queue)

        layout.addLayout(btn_layout)

        # 批量处理按钮
        self.btn_batch_process = QPushButton("📦 批量处理所有")
        self.btn_batch_process.clicked.connect(self.batch_process)
        layout.addWidget(self.btn_batch_process)

        # 进度条
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # 取消按钮
        self.btn_cancel = QPushButton("⏹️ 取消批量处理")
        self.btn_cancel.clicked.connect(self.cancel_batch_process)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.btn_cancel)

        panel.setLayout(layout)
        return panel

    def clear_queue(self):
        """清空队列"""
        self.logger.info("UI: 清空队列")
        self.queue_list.clear()

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

        # 文字颜色
        self.color_edit = QLineEdit("white")
        layout.addRow("文字颜色：", self.color_edit)

        # 描边宽度
        self.stroke_width_spin = QSpinBox()
        self.stroke_width_spin.setRange(0, 10)
        self.stroke_width_spin.setValue(2)
        layout.addRow("描边宽度：", self.stroke_width_spin)

        # 描边颜色
        self.stroke_color_edit = QLineEdit("black")
        layout.addRow("描边颜色：", self.stroke_color_edit)

        # 透明度
        self.text_opacity_spin = QDoubleSpinBox()
        self.text_opacity_spin.setRange(0.0, 1.0)
        self.text_opacity_spin.setValue(0.9)
        self.text_opacity_spin.setSingleStep(0.1)
        layout.addRow("透明度：", self.text_opacity_spin)

        # 位置选择
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            "左上",
            "中上",
            "右上",
            "左中",
            "正中",
            "右中",
            "左下",
            "中下",
            "右下"
        ])
        self.position_combo.setCurrentText("右下")  # 默认右下
        layout.addRow("水印位置：", self.position_combo)

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

    def switch_tab(self, index):
        """切换标签页"""
        self.tab_widget.setCurrentIndex(index)

        # 更新按钮状态
        buttons = [self.btn_image_watermark, self.btn_text_watermark, self.btn_insert_video]
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)

        # 显示/隐藏水印文件选择
        self.watermark_layout.itemAt(0).widget().setVisible(index == 0)
        self.watermark_edit.setVisible(index == 0)
        self.btn_browse_watermark.setVisible(index == 0)

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

        # 获取当前标签页
        current_tab = self.tab_widget.currentIndex()
        self.logger.debug(f"UI: 当前标签页索引: {current_tab}")

        # 处理单个文件
        if input_path.is_file():
            self.logger.debug("UI: 进入单文件处理模式")

            if current_tab == 0:  # 图片水印
                if not self.watermark_edit.text():
                    QMessageBox.warning(self, "警告", "请选择水印图片文件！")
                    return

                params = {
                    'video_path': str(input_path),
                    'watermark_path': self.watermark_edit.text(),
                    'output_path': output_path,
                    'opacity': self.opacity_spin.value(),
                    'start_time': float(self.start_time_edit.text() or 0),
                }

                if self.end_time_edit.text():
                    params['end_time'] = float(self.end_time_edit.text())

                task_type = 'watermark'

            elif current_tab == 1:  # 文字水印
                params = {
                    'video_path': str(input_path),
                    'text': self.text_edit.text(),
                    'output_path': output_path,
                    'font_size': self.font_size_spin.value(),
                    'color': self.color_edit.text(),
                    'opacity': self.text_opacity_spin.value(),
                    'stroke_width': self.stroke_width_spin.value(),
                    'stroke_color': self.stroke_color_edit.text(),
                    'position': self.position_combo.currentText(),
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
            self.btn_add_queue.setEnabled(False)
            self.btn_clear_queue.setEnabled(False)
            self.btn_browse_input.setEnabled(False)
            self.btn_browse_folder.setEnabled(False)
            self.btn_cancel.setEnabled(True)
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
                        params = {
                            'video_path': str(video_file),
                            'watermark_path': self.watermark_edit.text(),
                            'output_path': str(output_file_path),
                            'opacity': self.opacity_spin.value(),
                            'start_time': float(self.start_time_edit.text() or 0),
                        }
                        if self.end_time_edit.text():
                            params['end_time'] = float(self.end_time_edit.text())
                        add_image_watermark(**params)

                    elif current_tab == 1:  # 文字水印
                        params = {
                            'video_path': str(video_file),
                            'text': self.text_edit.text(),
                            'output_path': str(output_file_path),
                            'font_size': self.font_size_spin.value(),
                            'color': self.color_edit.text(),
                            'opacity': self.text_opacity_spin.value(),
                            'stroke_width': self.stroke_width_spin.value(),
                            'stroke_color': self.stroke_color_edit.text(),
                            'position': self.position_combo.currentText(),
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
            self.restore_process_buttons()

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

    def add_to_queue(self):
        """添加到队列"""
        self.logger.info("UI: 用户点击添加到队列按钮")

        input_path = self.input_edit.text()
        if not input_path:
            self.logger.warning("UI: 未选择输入文件或文件夹")
            QMessageBox.warning(self, "警告", "请选择输入视频文件或文件夹！")
            return

        # 获取当前参数配置
        current_tab = self.tab_widget.currentIndex()
        task_name = f"{'图片水印' if current_tab == 0 else '文字水印' if current_tab == 1 else '插入视频'}"

        # 检查输入是文件还是文件夹
        if Path(input_path).is_file():
            # 单个文件
            self.queue_list.addItem(f"📄 {task_name}: {Path(input_path).name}")
            self.logger.info(f"UI: 添加单个文件到队列 - {input_path}")
        elif Path(input_path).is_dir():
            # 文件夹 - 扫描视频文件并批量添加
            video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
            video_files = []

            for ext in video_extensions:
                video_files.extend(Path(input_path).glob(f"*{ext}"))

            if not video_files:
                QMessageBox.warning(self, "警告", "文件夹中没有找到视频文件！")
                return

            for video_file in video_files:
                self.queue_list.addItem(f"📁 {task_name}: {video_file.name}")

            self.logger.info(f"UI: 添加文件夹到队列 - {input_path}, 共 {len(video_files)} 个视频文件")
            QMessageBox.information(self, "提示", f"已添加 {len(video_files)} 个视频文件到队列")
        else:
            QMessageBox.warning(self, "警告", "输入路径不存在！")

    def cancel_batch_process(self):
        """取消批量处理"""
        self.logger.info("UI: 用户点击取消批量处理按钮")
        self.cancel_requested = True
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setText("⏹️ 正在取消...")
        self.status_bar.showMessage("正在取消...")

    def restore_process_buttons(self):
        """恢复单个处理相关按钮状态"""
        self.btn_process.setEnabled(True)
        self.btn_process.setText("🚀 开始处理")
        self.btn_add_queue.setEnabled(True)
        self.btn_clear_queue.setEnabled(True)
        self.btn_browse_input.setEnabled(True)
        self.btn_browse_folder.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.cancel_cancel()

    def restore_batch_buttons(self):
        """恢复批量处理相关按钮状态"""
        self.btn_batch_process.setEnabled(True)
        self.btn_batch_process.setText("📦 批量处理所有")
        self.btn_add_queue.setEnabled(True)
        self.btn_clear_queue.setEnabled(True)
        self.btn_browse_input.setEnabled(True)
        self.btn_browse_folder.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.cancel_cancel()

    def cancel_cancel(self):
        """重置取消相关状态"""
        self.btn_cancel.setText("⏹️ 取消批量处理")
        self.cancel_requested = False

    def batch_process(self):
        """批量处理队列中的所有视频"""
        self.logger.info("UI: 用户点击批量处理按钮")

        # 检查队列是否为空
        if self.queue_list.count() == 0:
            QMessageBox.warning(self, "警告", "队列为空，请先添加视频到队列！")
            self.logger.warning("UI: 队列为空，无法批量处理")
            return

        # 获取当前参数配置
        current_tab = self.tab_widget.currentIndex()
        self.logger.info(f"UI: 当前任务类型: {'图片水印' if current_tab == 0 else '文字水印' if current_tab == 1 else '插入视频'}")

        # 验证共用参数
        if current_tab == 0 and not self.watermark_edit.text():
            QMessageBox.warning(self, "警告", "请选择水印图片文件！")
            return

        if current_tab == 1 and not self.text_edit.text():
            QMessageBox.warning(self, "警告", "请输入水印文字！")
            return

        if current_tab == 2 and not self.insert_video_edit.text():
            QMessageBox.warning(self, "警告", "请选择要插入的视频文件！")
            return

        # 重置取消标志
        self.cancel_requested = False

        # 禁用按钮
        self.btn_batch_process.setEnabled(False)
        self.btn_batch_process.setText("⏳ 批量处理中...")
        self.btn_add_queue.setEnabled(False)
        self.btn_clear_queue.setEnabled(False)
        self.btn_browse_input.setEnabled(False)
        self.btn_browse_folder.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.status_bar.showMessage("批量处理中...")

        # 清空进度条
        self.progress_bar.setValue(0)

        # 获取基础输入路径
        base_input_path = self.input_edit.text()
        if not base_input_path:
            QMessageBox.warning(self, "警告", "没有选择基础输入路径！")
            return

        # 收集所有要处理的视频文件
        video_files_to_process = []

        # 检查基础输入是文件还是文件夹
        if Path(base_input_path).is_file():
            # 单个文件
            video_files_to_process.append(Path(base_input_path))
        elif Path(base_input_path).is_dir():
            # 文件夹 - 扫描所有视频文件
            video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
            for ext in video_extensions:
                video_files_to_process.extend(Path(base_input_path).glob(f"*{ext}"))

        if not video_files_to_process:
            QMessageBox.warning(self, "警告", "没有找到任何视频文件！")
            return

        self.logger.info(f"UI: 准备批量处理 {len(video_files_to_process)} 个视频文件")

        # 创建输出文件夹
        output_folder = Path(self.output_edit.text())
        output_folder.mkdir(parents=True, exist_ok=True)

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
                self.logger.info(f"批量处理第 {i+1}/{len(video_files_to_process)} 个视频: {video_file}")
                self.status_bar.showMessage(f"处理中: {video_file.name} ({i+1}/{len(video_files_to_process)})")

                # 生成输出文件名
                output_path = output_folder / f"{video_file.stem}_wmarked.mp4"

                # 根据当前标签页准备参数
                if current_tab == 0:  # 图片水印
                    params = {
                        'video_path': str(video_file),
                        'watermark_path': self.watermark_edit.text(),
                        'output_path': str(output_path),
                        'opacity': self.opacity_spin.value(),
                        'start_time': float(self.start_time_edit.text() or 0),
                    }
                    if self.end_time_edit.text():
                        params['end_time'] = float(self.end_time_edit.text())
                    add_image_watermark(**params)

                elif current_tab == 1:  # 文字水印
                    params = {
                        'video_path': str(video_file),
                        'text': self.text_edit.text(),
                        'output_path': str(output_path),
                        'font_size': self.font_size_spin.value(),
                        'color': self.color_edit.text(),
                        'opacity': self.text_opacity_spin.value(),
                        'stroke_width': self.stroke_width_spin.value(),
                        'stroke_color': self.stroke_color_edit.text(),
                        'position': self.position_combo.currentText(),
                    }
                    add_text_watermark(**params)

                else:  # 插入视频
                    params = {
                        'main_video_path': str(video_file),
                        'insert_video_path': self.insert_video_edit.text(),
                        'output_path': str(output_path),
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
        self.restore_batch_buttons()

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

        # 如果有正在进行的批量处理，请求取消
        if self.btn_batch_process.isEnabled() == False and self.cancel_requested == False:
            self.logger.info("UI: 检测到正在进行的批量处理，请求取消")
            self.cancel_requested = True
            QMessageBox.information(self, "提示", "正在取消批量处理，请稍候...")

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
