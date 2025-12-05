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

        panel.setLayout(layout)
        return panel

    def create_file_selection_area(self):
        """创建文件选择区域"""
        group = QGroupBox("文件选择（支持拖拽）")
        layout = QVBoxLayout()

        # 输入文件
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("输入视频："))
        self.input_edit = QLineEdit()
        self.input_edit.setAcceptDrops(True)
        self.input_edit.setPlaceholderText("拖拽视频文件到这里，或点击浏览...")
        input_layout.addWidget(self.input_edit)

        self.btn_browse_input = QPushButton("📁 浏览...")
        self.btn_browse_input.clicked.connect(lambda: self.browse_file('input'))
        input_layout.addWidget(self.btn_browse_input)

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
            QMessageBox.warning(self, "警告", "请选择输入视频文件！")
            return

        if not self.output_edit.text():
            self.logger.warning("UI: 未选择输出视频文件")
            QMessageBox.warning(self, "警告", "请选择输出视频文件！")
            return

        # 获取当前标签页
        current_tab = self.tab_widget.currentIndex()
        self.logger.debug(f"UI: 当前标签页索引: {current_tab}")

        if current_tab == 0:  # 图片水印
            if not self.watermark_edit.text():
                QMessageBox.warning(self, "警告", "请选择水印图片文件！")
                return

            params = {
                'video_path': self.input_edit.text(),
                'watermark_path': self.watermark_edit.text(),
                'output_path': self.output_edit.text(),
                'opacity': self.opacity_spin.value(),
                'start_time': float(self.start_time_edit.text() or 0),
            }

            if self.end_time_edit.text():
                params['end_time'] = float(self.end_time_edit.text())

            task_type = 'watermark'

        elif current_tab == 1:  # 文字水印
            params = {
                'video_path': self.input_edit.text(),
                'text': self.text_edit.text(),
                'output_path': self.output_edit.text(),
                'font_size': self.font_size_spin.value(),
                'color': self.color_edit.text(),
                'opacity': self.text_opacity_spin.value(),
                'stroke_width': self.stroke_width_spin.value(),
                'stroke_color': self.stroke_color_edit.text(),
            }

            if self.end_time_edit.text():
                params['end_time'] = float(self.end_time_edit.text())

            task_type = 'watermark_text'

        else:  # 插入视频
            if not self.insert_video_edit.text():
                QMessageBox.warning(self, "警告", "请选择要插入的视频文件！")
                return

            params = {
                'main_video_path': self.input_edit.text(),
                'insert_video_path': self.insert_video_edit.text(),
                'output_path': self.output_edit.text(),
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
        # TODO: 实现添加到队列功能
        QMessageBox.information(self, "提示", "批量处理功能开发中...")

    def clear_queue(self):
        """清空队列"""
        self.queue_list.clear()

    def batch_process(self):
        """批量处理"""
        # TODO: 实现批量处理功能
        QMessageBox.information(self, "提示", "批量处理功能开发中...")

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.logger.info("UI: 用户关闭窗口")
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
