"""
主窗口 - PyCompare 文件比较工具
支持多标签页、文件/文件夹比较、设置等
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QMenuBar, QMenu, QToolBar, QStatusBar, QLabel, QFileDialog,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QCheckBox,
    QSpinBox, QComboBox, QApplication, QSplashScreen, QPushButton
)
from PySide6.QtCore import Qt, QSettings, QSize, QTimer
from PySide6.QtGui import QAction, QKeySequence, QIcon, QPixmap, QFont, QColor

import sys
import os

# 添加路径以支持不同的运行环境
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后的环境
    _base_path = sys._MEIPASS
else:
    # 开发环境
    _base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, _base_path)

from src.ui.diff_view import DiffViewWidget
from src.ui.folder_view import FolderViewWidget


class WelcomeWidget(QWidget):
    """欢迎页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 标题
        title = QLabel("PyCompare")
        title.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        title.setStyleSheet("color: #569cd6;")  # 深色主题蓝色
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("强大的文件与文件夹比较工具")
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setStyleSheet("color: #9cdcfe;")  # 浅蓝色
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(40)

        # 快捷操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        file_btn = QPushButton("📄 比较文件")
        file_btn.setFixedSize(150, 50)
        file_btn.setStyleSheet("""
            QPushButton {
                background: #2d7d46;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #369950;
            }
        """)
        file_btn.clicked.connect(self.parent().new_file_compare)
        btn_layout.addWidget(file_btn)

        folder_btn = QPushButton("📁 比较文件夹")
        folder_btn.setFixedSize(150, 50)
        folder_btn.setStyleSheet("""
            QPushButton {
                background: #0e639c;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #1177bb;
            }
        """)
        folder_btn.clicked.connect(self.parent().new_folder_compare)
        btn_layout.addWidget(folder_btn)

        layout.addLayout(btn_layout)

        layout.addSpacing(40)

        # 提示
        tips = QLabel("提示: 可以直接拖放文件或文件夹到窗口进行比较")
        tips.setStyleSheet("color: #808080;")  # 灰色
        tips.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tips)


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        # 比较选项
        self.ignore_whitespace = QCheckBox("忽略空白字符")
        form.addRow("", self.ignore_whitespace)

        self.ignore_case = QCheckBox("忽略大小写")
        form.addRow("", self.ignore_case)

        self.ignore_blank_lines = QCheckBox("忽略空行")
        form.addRow("", self.ignore_blank_lines)

        # 显示选项
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(10)
        form.addRow("字体大小:", self.font_size)

        self.tab_width = QSpinBox()
        self.tab_width.setRange(2, 8)
        self.tab_width.setValue(4)
        form.addRow("Tab宽度:", self.tab_width)

        # 主题
        self.theme = QComboBox()
        self.theme.addItems(["浅色", "深色"])
        form.addRow("主题:", self.theme)

        layout.addLayout(form)

        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCompare - 文件比较工具")
        self.setMinimumSize(1200, 800)

        # 设置
        self.settings = QSettings("PyCompare", "PyCompare")

        # 初始化UI
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()

        # 恢复窗口状态
        self.restore_state()

        # 启用拖放
        self.setAcceptDrops(True)

    def setup_ui(self):
        """设置UI"""
        # 中央控件 - 标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # 添加欢迎页
        welcome = WelcomeWidget(self)
        self.tab_widget.addTab(welcome, "🏠 欢迎")

        self.setCentralWidget(self.tab_widget)

    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        new_file = QAction("新建文件比较(&N)", self)
        new_file.setShortcut(QKeySequence("Ctrl+N"))
        new_file.triggered.connect(self.new_file_compare)
        file_menu.addAction(new_file)

        new_folder = QAction("新建文件夹比较(&D)", self)
        new_folder.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_folder.triggered.connect(self.new_folder_compare)
        file_menu.addAction(new_folder)

        file_menu.addSeparator()

        open_left = QAction("打开左侧文件...", self)
        open_left.setShortcut(QKeySequence("Ctrl+O"))
        open_left.triggered.connect(self.open_left_file)
        file_menu.addAction(open_left)

        open_right = QAction("打开右侧文件...", self)
        open_right.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_right.triggered.connect(self.open_right_file)
        file_menu.addAction(open_right)

        file_menu.addSeparator()

        save = QAction("保存(&S)", self)
        save.setShortcut(QKeySequence("Ctrl+S"))
        save.triggered.connect(self.save_current)
        file_menu.addAction(save)

        file_menu.addSeparator()

        close_tab = QAction("关闭标签页(&W)", self)
        close_tab.setShortcut(QKeySequence("Ctrl+W"))
        close_tab.triggered.connect(lambda: self.close_tab(self.tab_widget.currentIndex()))
        file_menu.addAction(close_tab)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")

        undo = QAction("撤销(&U)", self)
        undo.setShortcut(QKeySequence("Ctrl+Z"))
        edit_menu.addAction(undo)

        redo = QAction("重做(&R)", self)
        redo.setShortcut(QKeySequence("Ctrl+Y"))
        edit_menu.addAction(redo)

        edit_menu.addSeparator()

        find = QAction("查找(&F)", self)
        find.setShortcut(QKeySequence("Ctrl+F"))
        edit_menu.addAction(find)

        replace = QAction("替换(&H)", self)
        replace.setShortcut(QKeySequence("Ctrl+H"))
        edit_menu.addAction(replace)

        # 比较菜单
        compare_menu = menubar.addMenu("比较(&C)")

        refresh = QAction("刷新比较(&R)", self)
        refresh.setShortcut(QKeySequence("F5"))
        refresh.triggered.connect(self.refresh_compare)
        compare_menu.addAction(refresh)

        compare_menu.addSeparator()

        next_diff = QAction("下一处差异(&N)", self)
        next_diff.setShortcut(QKeySequence("Alt+Down"))
        next_diff.triggered.connect(self.go_to_next_diff)
        compare_menu.addAction(next_diff)

        prev_diff = QAction("上一处差异(&P)", self)
        prev_diff.setShortcut(QKeySequence("Alt+Up"))
        prev_diff.triggered.connect(self.go_to_prev_diff)
        compare_menu.addAction(prev_diff)

        compare_menu.addSeparator()

        copy_right = QAction("复制到右侧(&R)", self)
        copy_right.setShortcut(QKeySequence("Alt+Right"))
        copy_right.triggered.connect(self.copy_to_right)
        compare_menu.addAction(copy_right)

        copy_left = QAction("复制到左侧(&L)", self)
        copy_left.setShortcut(QKeySequence("Alt+Left"))
        copy_left.triggered.connect(self.copy_to_left)
        compare_menu.addAction(copy_left)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")

        sync_scroll = QAction("同步滚动", self)
        sync_scroll.setCheckable(True)
        sync_scroll.setChecked(True)
        view_menu.addAction(sync_scroll)

        view_menu.addSeparator()

        show_line_numbers = QAction("显示行号", self)
        show_line_numbers.setCheckable(True)
        show_line_numbers.setChecked(True)
        view_menu.addAction(show_line_numbers)

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")

        settings = QAction("设置(&S)...", self)
        settings.triggered.connect(self.show_settings)
        tools_menu.addAction(settings)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about = QAction("关于(&A)", self)
        about.triggered.connect(self.show_about)
        help_menu.addAction(about)

    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        toolbar.setStyleSheet("""
            QToolBar { background: #2d2d2d; border-bottom: 1px solid #3c3c3c; padding: 5px; }
            QToolButton { background: transparent; color: #d4d4d4; padding: 8px; margin: 2px; border-radius: 4px; }
            QToolButton:hover { background: #3c3c3c; }
            QToolButton:pressed { background: #094771; }
        """)

        # 新建
        new_file_action = QAction("📄 文件比较", self)
        new_file_action.triggered.connect(self.new_file_compare)
        toolbar.addAction(new_file_action)

        new_folder_action = QAction("📁 文件夹比较", self)
        new_folder_action.triggered.connect(self.new_folder_compare)
        toolbar.addAction(new_folder_action)

        toolbar.addSeparator()

        # 刷新
        refresh_action = QAction("🔄 刷新", self)
        refresh_action.triggered.connect(self.refresh_compare)
        toolbar.addAction(refresh_action)

        toolbar.addSeparator()

        # 导航
        prev_action = QAction("⬆ 上一处", self)
        prev_action.triggered.connect(self.go_to_prev_diff)
        toolbar.addAction(prev_action)

        next_action = QAction("⬇ 下一处", self)
        next_action.triggered.connect(self.go_to_next_diff)
        toolbar.addAction(next_action)

        toolbar.addSeparator()

        # 合并
        copy_right_action = QAction("➡ 复制到右侧", self)
        copy_right_action.triggered.connect(self.copy_to_right)
        toolbar.addAction(copy_right_action)

        copy_left_action = QAction("⬅ 复制到左侧", self)
        copy_left_action.triggered.connect(self.copy_to_left)
        toolbar.addAction(copy_left_action)

    def setup_statusbar(self):
        """设置状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.status_label = QLabel("就绪")
        self.statusbar.addWidget(self.status_label, 1)

        self.encoding_label = QLabel("UTF-8")
        self.statusbar.addPermanentWidget(self.encoding_label)

    def restore_state(self):
        """恢复窗口状态"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)

    def closeEvent(self, event):
        """关闭事件"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        # 关闭所有标签页，确保后台线程停止
        for i in range(self.tab_widget.count() - 1, -1, -1):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, FolderViewWidget):
                widget.stop_worker()

        event.accept()
        # 确保应用程序完全退出
        QApplication.quit()

    def new_file_compare(self):
        """新建文件比较标签页"""
        diff_view = DiffViewWidget()
        index = self.tab_widget.addTab(diff_view, "📄 文件比较")
        self.tab_widget.setCurrentIndex(index)
        self.status_label.setText("新建文件比较")

    def new_folder_compare(self):
        """新建文件夹比较标签页"""
        folder_view = FolderViewWidget()
        folder_view.open_file_compare.connect(self.open_file_compare_from_folder)
        index = self.tab_widget.addTab(folder_view, "📁 文件夹比较")
        self.tab_widget.setCurrentIndex(index)
        self.status_label.setText("新建文件夹比较")

    def open_file_compare_from_folder(self, left_path: str, right_path: str):
        """从文件夹视图打开文件比较"""
        diff_view = DiffViewWidget()
        name = os.path.basename(left_path) if left_path else os.path.basename(right_path)
        index = self.tab_widget.addTab(diff_view, f"📄 {name}")
        self.tab_widget.setCurrentIndex(index)

        if left_path:
            diff_view.load_left_file(left_path)
        if right_path:
            diff_view.load_right_file(right_path)

        QTimer.singleShot(100, diff_view.compare_files)

    def close_tab(self, index: int):
        """关闭标签页"""
        if index > 0:  # 不关闭欢迎页
            self.tab_widget.removeTab(index)

    def open_left_file(self):
        """打开左侧文件"""
        current = self.tab_widget.currentWidget()
        if isinstance(current, DiffViewWidget):
            current.open_left_file()

    def open_right_file(self):
        """打开右侧文件"""
        current = self.tab_widget.currentWidget()
        if isinstance(current, DiffViewWidget):
            current.open_right_file()

    def save_current(self):
        """保存当前"""
        current = self.tab_widget.currentWidget()
        if isinstance(current, DiffViewWidget):
            current.save_left_file()
            current.save_right_file()

    def refresh_compare(self):
        """刷新比较"""
        current = self.tab_widget.currentWidget()
        if isinstance(current, DiffViewWidget):
            current.compare_files()
        elif isinstance(current, FolderViewWidget):
            current.compare_folders()

    def go_to_next_diff(self):
        """跳转到下一处差异"""
        current = self.tab_widget.currentWidget()
        if isinstance(current, DiffViewWidget):
            current.go_to_next_diff()

    def go_to_prev_diff(self):
        """跳转到上一处差异"""
        current = self.tab_widget.currentWidget()
        if isinstance(current, DiffViewWidget):
            current.go_to_prev_diff()

    def copy_to_right(self):
        """复制到右侧"""
        current = self.tab_widget.currentWidget()
        if isinstance(current, DiffViewWidget):
            current.copy_to_right()

    def copy_to_left(self):
        """复制到左侧"""
        current = self.tab_widget.currentWidget()
        if isinstance(current, DiffViewWidget):
            current.copy_to_left()

    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 保存设置
            pass

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 PyCompare",
            """<h2>PyCompare</h2>
            <p>版本 1.0.0</p>
            <p>一个强大的文件与文件夹比较工具</p>
            <p>功能特点:</p>
            <ul>
                <li>文件内容对比与合并</li>
                <li>文件夹递归比较</li>
                <li>语法高亮显示</li>
                <li>差异导航与合并</li>
                <li>支持多种编码</li>
            </ul>
            <p>基于 PySide6 (Qt6) 开发</p>
            """
        )

    def dragEnterEvent(self, event):
        """拖入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """放下事件"""
        urls = event.mimeData().urls()
        if not urls:
            return

        paths = [url.toLocalFile() for url in urls]

        if len(paths) == 2:
            # 两个文件/文件夹
            if os.path.isdir(paths[0]) and os.path.isdir(paths[1]):
                # 两个文件夹
                folder_view = FolderViewWidget()
                folder_view.open_file_compare.connect(self.open_file_compare_from_folder)
                index = self.tab_widget.addTab(folder_view, "📁 文件夹比较")
                self.tab_widget.setCurrentIndex(index)
                folder_view.load_folders(paths[0], paths[1])
            else:
                # 两个文件
                diff_view = DiffViewWidget()
                index = self.tab_widget.addTab(diff_view, "📄 文件比较")
                self.tab_widget.setCurrentIndex(index)
                diff_view.load_files(paths[0], paths[1])
        elif len(paths) == 1:
            # 单个文件/文件夹 - 智能处理
            path = paths[0]
            current = self.tab_widget.currentWidget()
            is_dir = os.path.isdir(path)
            is_file = os.path.isfile(path)

            # 判断当前标签页类型是否匹配
            if is_file and isinstance(current, DiffViewWidget):
                # 当前是文件比较标签页，判断放入左侧还是右侧
                if not current.left_file_path:
                    current.load_left_file(path)
                    self.status_label.setText("已加载左侧文件，请拖入右侧文件")
                elif not current.right_file_path:
                    current.load_right_file(path)
                    # 两边都有了，自动开始比较
                    QTimer.singleShot(100, current.compare_files)
                else:
                    # 两边都有文件，替换左侧并重新比较
                    current.load_left_file(path)
                    QTimer.singleShot(100, current.compare_files)
            elif is_dir and isinstance(current, FolderViewWidget):
                # 当前是文件夹比较标签页，判断放入左侧还是右侧
                if not current.left_folder:
                    current.left_folder = path
                    current.left_path_label.setText(f"左侧: {path}")
                    self.status_label.setText("已加载左侧文件夹，请拖入右侧文件夹")
                elif not current.right_folder:
                    current.right_folder = path
                    current.right_path_label.setText(f"右侧: {path}")
                    # 两边都有了，自动开始比较
                    QTimer.singleShot(100, current.compare_folders)
                else:
                    # 两边都有文件夹，替换左侧并重新比较
                    current.left_folder = path
                    current.left_path_label.setText(f"左侧: {path}")
                    QTimer.singleShot(100, current.compare_folders)
            else:
                # 类型不匹配或当前是欢迎页，创建新的标签页
                if is_dir:
                    folder_view = FolderViewWidget()
                    folder_view.open_file_compare.connect(self.open_file_compare_from_folder)
                    index = self.tab_widget.addTab(folder_view, "📁 文件夹比较")
                    self.tab_widget.setCurrentIndex(index)
                    folder_view.left_folder = path
                    folder_view.left_path_label.setText(f"左侧: {path}")
                    self.status_label.setText("已加载左侧文件夹，请拖入右侧文件夹")
                elif is_file:
                    diff_view = DiffViewWidget()
                    index = self.tab_widget.addTab(diff_view, "📄 文件比较")
                    self.tab_widget.setCurrentIndex(index)
                    diff_view.load_left_file(path)
                    self.status_label.setText("已加载左侧文件，请拖入右侧文件")
