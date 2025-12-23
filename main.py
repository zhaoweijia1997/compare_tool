#!/usr/bin/env python3
"""
PyCompare - 文件比较工具
一个类似 BeyondCompare/WinMerge 的文件和文件夹比较工具
"""
import sys
import os

# 确保能够导入src模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor

from src.ui.main_window import MainWindow


def setup_dark_style(app: QApplication):
    """设置深色主题样式"""
    # 设置默认字体
    font = QFont("Microsoft YaHei UI", 9)
    app.setFont(font)

    # 深色主题样式表
    app.setStyleSheet("""
        /* 主窗口 */
        QMainWindow {
            background: #1e1e1e;
            color: #d4d4d4;
        }
        QWidget {
            background: #1e1e1e;
            color: #d4d4d4;
        }

        /* 标签页 */
        QTabWidget::pane {
            border: 1px solid #3c3c3c;
            background: #252526;
        }
        QTabBar::tab {
            background: #2d2d2d;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: #1e1e1e;
            border-bottom: 2px solid #0078d4;
        }
        QTabBar::tab:hover {
            background: #383838;
        }
        QTabBar::close-button {
            subcontrol-position: right;
            margin: 2px;
            padding: 2px;
        }
        QTabBar::close-button:hover {
            background: #c42b1c;
            border-radius: 3px;
        }

        /* 菜单栏 */
        QMenuBar {
            background: #2d2d2d;
            color: #d4d4d4;
            border-bottom: 1px solid #3c3c3c;
        }
        QMenuBar::item:selected {
            background: #094771;
        }
        QMenu {
            background: #252526;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
        }
        QMenu::item:selected {
            background: #094771;
        }
        QMenu::separator {
            height: 1px;
            background: #3c3c3c;
        }

        /* 工具栏 */
        QToolBar {
            background: #2d2d2d;
            border-bottom: 1px solid #3c3c3c;
            padding: 2px;
            spacing: 3px;
        }
        QToolButton {
            background: transparent;
            color: #d4d4d4;
            border: none;
            padding: 5px 10px;
            margin: 2px;
            border-radius: 3px;
        }
        QToolButton:hover {
            background: #3c3c3c;
        }
        QToolButton:pressed {
            background: #094771;
        }

        /* 状态栏 */
        QStatusBar {
            background: #007acc;
            color: white;
            border: none;
        }

        /* 滚动条 */
        QScrollBar:vertical {
            background: #1e1e1e;
            width: 14px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background: #5a5a5a;
            min-height: 30px;
            border-radius: 5px;
            margin: 2px;
        }
        QScrollBar::handle:vertical:hover {
            background: #787878;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
        QScrollBar:horizontal {
            background: #1e1e1e;
            height: 14px;
            margin: 0;
        }
        QScrollBar::handle:horizontal {
            background: #5a5a5a;
            min-width: 30px;
            border-radius: 5px;
            margin: 2px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #787878;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0;
        }

        /* 分割器 */
        QSplitter::handle {
            background: #3c3c3c;
        }
        QSplitter::handle:horizontal {
            width: 3px;
        }
        QSplitter::handle:vertical {
            height: 3px;
        }

        /* 文本编辑器 */
        QPlainTextEdit {
            background: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
            selection-background-color: #264f78;
            selection-color: #ffffff;
        }

        /* 树形控件 */
        QTreeWidget {
            background: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
            alternate-background-color: #252526;
        }
        QTreeWidget::item {
            padding: 4px;
        }
        QTreeWidget::item:selected {
            background: #094771;
            color: white;
        }
        QTreeWidget::item:hover {
            background: #2a2d2e;
        }
        QHeaderView::section {
            background: #2d2d2d;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
            padding: 5px;
        }

        /* 按钮 */
        QPushButton {
            background: #0e639c;
            color: white;
            border: none;
            padding: 6px 16px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background: #1177bb;
        }
        QPushButton:pressed {
            background: #094771;
        }
        QPushButton:checked {
            background: #094771;
        }

        /* 标签 */
        QLabel {
            color: #d4d4d4;
            background: transparent;
        }

        /* 输入框 */
        QLineEdit {
            background: #3c3c3c;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
            padding: 5px;
            border-radius: 3px;
        }
        QLineEdit:focus {
            border: 1px solid #0078d4;
        }

        /* 复选框和下拉框 */
        QCheckBox {
            color: #d4d4d4;
        }
        QComboBox {
            background: #3c3c3c;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
            padding: 5px;
            border-radius: 3px;
        }
        QComboBox:hover {
            border: 1px solid #0078d4;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background: #252526;
            color: #d4d4d4;
            selection-background-color: #094771;
        }

        /* 数字输入框 */
        QSpinBox {
            background: #3c3c3c;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
            padding: 3px;
        }

        /* 对话框按钮 */
        QDialogButtonBox QPushButton {
            min-width: 80px;
        }

        /* 消息框 */
        QMessageBox {
            background: #252526;
        }
        QMessageBox QLabel {
            color: #d4d4d4;
        }
    """)


def main():
    """主函数"""
    # 高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("PyCompare")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PyCompare")

    # 设置深色主题
    setup_dark_style(app)

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 处理命令行参数
    args = sys.argv[1:]
    if len(args) >= 2:
        # 两个参数 - 自动比较
        left_path = args[0]
        right_path = args[1]
        if os.path.isdir(left_path) and os.path.isdir(right_path):
            window.new_folder_compare()
            folder_view = window.tab_widget.currentWidget()
            folder_view.load_folders(left_path, right_path)
        elif os.path.isfile(left_path) and os.path.isfile(right_path):
            window.new_file_compare()
            diff_view = window.tab_widget.currentWidget()
            diff_view.load_files(left_path, right_path)

    # 运行
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
