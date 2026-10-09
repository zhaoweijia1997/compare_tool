"""
文件比较视图 - 双栏对比界面
支持语法高亮、差异高亮、行号显示、同步滚动
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPlainTextEdit,
    QTextEdit, QLabel, QScrollBar, QFrame, QToolBar, QPushButton,
    QFileDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal, QRect, QSize, QTimer
from PySide6.QtGui import (
    QColor, QTextFormat, QPainter, QFont, QTextCharFormat,
    QSyntaxHighlighter, QTextDocument, QTextCursor, QPalette,
    QFontMetrics, QAction, QIcon, QKeySequence
)
from typing import List, Optional, Tuple
import os
import sys
import chardet

# 添加路径以支持不同的运行环境
if getattr(sys, 'frozen', False):
    _base_path = sys._MEIPASS
else:
    _base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _base_path)

from src.core.diff_engine import DiffEngine, DiffBlock, DiffType


class LineNumberArea(QWidget):
    """行号区域 - 包含行号和复制箭头按钮"""

    copy_line_clicked = Signal(int)  # 点击复制箭头时发出的信号，参数为行号
    copy_block_clicked = Signal(int)  # 点击复制整块时发出的信号

    def __init__(self, editor: 'DiffTextEdit'):
        super().__init__(editor)
        self.editor = editor
        self.hover_line = -1  # 鼠标悬停的行号
        self.setMouseTracking(True)  # 启用鼠标追踪

    def sizeHint(self) -> QSize:
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 更新悬停行"""
        block = self.editor.firstVisibleBlock()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())

        while block.isValid() and top <= event.position().y():
            if block.isVisible() and bottom >= event.position().y():
                self.hover_line = block.blockNumber()
                self.update()
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                return
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())

        self.hover_line = -1
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.hover_line = -1
        self.update()

    def mousePressEvent(self, event):
        """鼠标点击事件 - 复制行"""
        if event.button() == Qt.MouseButton.LeftButton and self.hover_line >= 0:
            # 检查点击位置是否在箭头区域
            arrow_width = 20
            if event.position().x() < arrow_width:
                # 点击了箭头区域，复制整个差异块
                self.copy_block_clicked.emit(self.hover_line)
            else:
                # 点击了行号区域，复制单行
                self.copy_line_clicked.emit(self.hover_line)


class DiffTextEdit(QPlainTextEdit):
    """支持差异高亮的文本编辑器"""

    scrolled = Signal(int)  # 滚动信号
    copy_line_to_other = Signal(int)  # 复制当前行到另一侧的信号

    # 颜色主题 (深色主题 - BeyondCompare风格)
    COLORS = {
        'equal': QColor(30, 30, 30),              # 深灰色背景 - 相同
        'insert': QColor(35, 61, 35),             # 深绿色 - 新增
        'delete': QColor(61, 35, 35),             # 深红色 - 删除
        'replace': QColor(90, 40, 40),            # 红褐色 - 完全不同的行
        'char_diff': QColor(120, 50, 50),         # 深红色 - 字符级差异高亮
        'line_number_bg': QColor(37, 37, 38),     # 行号背景
        'line_number_fg': QColor(133, 133, 133),  # 行号前景
        'current_line': QColor(40, 44, 52),       # 当前行高亮
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置等宽字体
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self.setFont(font)

        # 行号区域
        self.line_number_area = LineNumberArea(self)

        # 差异块列表
        self.diff_blocks: List[DiffBlock] = []
        self.is_left = True  # 是否是左侧编辑器
        self.other_editor = None  # 对应的另一侧编辑器

        # 连接信号
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.verticalScrollBar().valueChanged.connect(self.on_scroll)

        # 连接行号区域的复制信号
        self.line_number_area.copy_line_clicked.connect(self.copy_current_line_to_other)
        self.line_number_area.copy_block_clicked.connect(self.copy_diff_block_to_other)

        # 初始化
        self.update_line_number_area_width(0)
        self.highlight_current_line()

        # 设置Tab宽度
        self.setTabStopDistance(QFontMetrics(self.font()).horizontalAdvance(' ') * 4)

        # 启用自定义右键菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        """显示右键菜单"""
        menu = self.createStandardContextMenu()
        menu.addSeparator()

        # 获取当前行号
        cursor = self.cursorForPosition(pos)
        line_num = cursor.blockNumber()

        # 添加复制到另一侧的选项
        if self.is_left:
            copy_action = menu.addAction("➡ 复制此行到右侧")
        else:
            copy_action = menu.addAction("⬅ 复制此行到左侧")
        copy_action.triggered.connect(lambda: self.copy_current_line_to_other(line_num))

        # 添加复制当前差异块的选项
        copy_block_action = menu.addAction("📋 复制当前差异块到另一侧")
        copy_block_action.triggered.connect(lambda: self.copy_diff_block_to_other(line_num))

        menu.exec(self.mapToGlobal(pos))

    def copy_current_line_to_other(self, line_num: int):
        """复制指定行到另一侧编辑器"""
        if self.other_editor:
            # 获取本侧的行内容
            block = self.document().findBlockByNumber(line_num)
            if block.isValid():
                line_text = block.text()
                # 替换另一侧对应行
                other_cursor = QTextCursor(self.other_editor.document().findBlockByNumber(line_num))
                if other_cursor.block().isValid():
                    other_cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                    other_cursor.insertText(line_text)

    def copy_diff_block_to_other(self, line_num: int):
        """复制包含指定行的差异块到另一侧"""
        if not self.other_editor or not self.diff_blocks:
            return

        # 找到包含此行的差异块
        for block in self.diff_blocks:
            if block.diff_type == DiffType.EQUAL:
                continue

            if self.is_left:
                start, end = block.left_start, block.left_end
            else:
                start, end = block.right_start, block.right_end

            if start <= line_num < end:
                # 找到了，复制这个块的所有行
                lines = []
                for i in range(start, end):
                    b = self.document().findBlockByNumber(i)
                    if b.isValid():
                        lines.append(b.text())

                # 替换另一侧对应的行
                if self.is_left:
                    other_start, other_end = block.right_start, block.right_end
                else:
                    other_start, other_end = block.left_start, block.left_end

                # 获取另一侧的光标
                other_doc = self.other_editor.document()
                cursor = QTextCursor(other_doc.findBlockByNumber(other_start))

                # 选择要替换的范围
                for i in range(other_end - other_start):
                    cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor)
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)

                # 替换内容
                cursor.insertText('\n'.join(lines))
                break

    def line_number_area_width(self) -> int:
        """计算行号区域宽度（包含箭头按钮区域）"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        # 箭头区域(20) + 行号区域 + 边距(10)
        arrow_width = 20
        line_number_width = self.fontMetrics().horizontalAdvance('9') * digits + 10
        return arrow_width + line_number_width

    def update_line_number_area_width(self, _):
        """更新行号区域宽度"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """更新行号区域"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """调整大小事件"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(),
                                                 self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        """绘制行号和箭头按钮"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), self.COLORS['line_number_bg'])

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        arrow_width = 20
        hover_line = self.line_number_area.hover_line

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_num = block_number
                number = str(line_num + 1)

                # 绘制行号
                painter.setPen(self.COLORS['line_number_fg'])
                painter.drawText(arrow_width, top, self.line_number_area.width() - arrow_width - 5,
                               self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)

                # 检查这一行是否是差异行
                is_diff_line = False
                for diff_block in self.diff_blocks:
                    if diff_block.diff_type == DiffType.EQUAL:
                        continue
                    if self.is_left:
                        if diff_block.left_start <= line_num < diff_block.left_end:
                            is_diff_line = True
                            break
                    else:
                        if diff_block.right_start <= line_num < diff_block.right_end:
                            is_diff_line = True
                            break

                # 绘制箭头按钮（差异行或悬停行显示）
                if is_diff_line or line_num == hover_line:
                    # 箭头颜色
                    if line_num == hover_line:
                        arrow_color = QColor(100, 180, 255)  # 悬停时蓝色
                    else:
                        arrow_color = QColor(150, 150, 150)  # 普通灰色

                    painter.setPen(arrow_color)
                    font = painter.font()
                    font.setPointSize(10)
                    font.setBold(True)
                    painter.setFont(font)

                    # 绘制箭头 - 左侧编辑器显示 ➡，右侧显示 ⬅
                    arrow_text = "➡" if self.is_left else "⬅"
                    arrow_rect = QRect(2, top, arrow_width - 2, self.fontMetrics().height())
                    painter.drawText(arrow_rect, Qt.AlignmentFlag.AlignCenter, arrow_text)

                    # 恢复字体
                    font.setBold(False)
                    painter.setFont(font)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        """高亮当前行"""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(self.COLORS['current_line'])
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def on_scroll(self, value):
        """滚动时发出信号"""
        self.scrolled.emit(value)

    def set_diff_blocks(self, blocks: List[DiffBlock], is_left: bool = True):
        """设置差异块并高亮"""
        self.diff_blocks = blocks
        self.is_left = is_left
        self.apply_diff_highlighting()

    def apply_diff_highlighting(self):
        """应用差异高亮"""
        extra_selections = []
        cursor = self.textCursor()

        for block in self.diff_blocks:
            if block.diff_type == DiffType.EQUAL:
                continue

            if self.is_left:
                start_line = block.left_start
                end_line = block.left_end
            else:
                start_line = block.right_start
                end_line = block.right_end

            # 选择颜色
            if block.diff_type == DiffType.INSERT:
                color = self.COLORS['insert'] if not self.is_left else self.COLORS['delete']
            elif block.diff_type == DiffType.DELETE:
                color = self.COLORS['delete'] if self.is_left else self.COLORS['insert']
            else:  # REPLACE
                color = self.COLORS['replace']

            # 高亮每一行
            for line_num in range(start_line, end_line):
                doc_block = self.document().findBlockByNumber(line_num)
                if doc_block.isValid():
                    selection = QTextEdit.ExtraSelection()
                    selection.format.setBackground(color)
                    selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
                    selection.cursor = QTextCursor(doc_block)
                    extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def go_to_line(self, line_num: int):
        """跳转到指定行"""
        block = self.document().findBlockByNumber(line_num)
        if block.isValid():
            cursor = QTextCursor(block)
            self.setTextCursor(cursor)
            self.centerCursor()


class DiffNavigator(QWidget):
    """差异导航条 - 显示整体差异分布（类似BeyondCompare的缩略图）"""

    clicked = Signal(int)  # 点击位置信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.diff_blocks: List[DiffBlock] = []
        self.total_lines = 1
        self.current_line = 0  # 当前可见区域
        self.visible_lines = 20  # 可见行数
        self.setFixedWidth(50)  # 导航条宽度
        self.setMinimumHeight(100)
        self.is_left = True
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_diff_blocks(self, blocks: List[DiffBlock], total_lines: int, is_left: bool = True):
        """设置差异块"""
        self.diff_blocks = blocks
        self.total_lines = max(1, total_lines)
        self.is_left = is_left
        self.update()

    def set_viewport(self, current_line: int, visible_lines: int):
        """设置当前可见区域"""
        self.current_line = current_line
        self.visible_lines = visible_lines
        self.update()

    def paintEvent(self, event):
        """绘制差异分布缩略图"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        height = self.height()
        width = self.width()

        # 背景
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        # 绘制差异区域
        if self.total_lines > 0:
            line_height = height / self.total_lines

            for block in self.diff_blocks:
                if block.diff_type == DiffType.EQUAL:
                    continue

                # 使用左侧行号
                start = block.left_start
                end = block.left_end

                y1 = int(start * line_height)
                y2 = int(end * line_height)
                h = max(y2 - y1, 3)  # 最小高度3像素

                # 选择颜色
                if block.diff_type == DiffType.INSERT:
                    color = QColor(80, 180, 80)     # 绿色 - 新增
                elif block.diff_type == DiffType.DELETE:
                    color = QColor(200, 80, 80)     # 红色 - 删除
                else:
                    color = QColor(220, 100, 60)    # 橙红色 - 修改

                # 绘制差异块
                painter.fillRect(6, y1, width - 12, h, color)

        # 绘制当前可见区域指示器（可拖动的框）
        if self.total_lines > 0:
            view_y1 = int(self.current_line / self.total_lines * height)
            view_h = int(self.visible_lines / self.total_lines * height)
            view_h = max(view_h, 20)  # 最小高度

            # 半透明白色框表示当前可见区域
            painter.fillRect(2, view_y1, width - 4, view_h, QColor(255, 255, 255, 40))
            painter.setPen(QColor(100, 150, 255, 200))
            painter.drawRect(2, view_y1, width - 5, view_h - 1)

        # 绘制边框
        painter.setPen(QColor(60, 60, 60))
        painter.drawRect(0, 0, width - 1, height - 1)

    def mousePressEvent(self, event):
        """点击跳转"""
        if event.button() == Qt.MouseButton.LeftButton:
            line = int(event.position().y() / self.height() * self.total_lines)
            self.clicked.emit(line)

    def mouseMoveEvent(self, event):
        """拖动时持续跳转"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            line = int(event.position().y() / self.height() * self.total_lines)
            line = max(0, min(line, self.total_lines - 1))
            self.clicked.emit(line)


class DiffViewWidget(QWidget):
    """文件比较视图主控件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.diff_engine = DiffEngine()
        self.diff_blocks: List[DiffBlock] = []
        self.current_diff_index = 0
        self.left_file_path = ""
        self.right_file_path = ""
        self.left_is_binary = False
        self.right_is_binary = False

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 工具栏
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)

        # 文件路径栏
        path_layout = QHBoxLayout()
        self.left_path_label = QLabel("左侧文件: 未选择")
        self.right_path_label = QLabel("右侧文件: 未选择")
        self.left_path_label.setStyleSheet("padding: 5px; background: #252526; color: #d4d4d4; border: 1px solid #3c3c3c;")
        self.right_path_label.setStyleSheet("padding: 5px; background: #252526; color: #d4d4d4; border: 1px solid #3c3c3c;")
        path_layout.addWidget(self.left_path_label)
        path_layout.addWidget(self.right_path_label)
        layout.addLayout(path_layout)

        # 主分割器
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧编辑器
        self.left_editor = DiffTextEdit()
        self.left_editor.is_left = True

        # 中间操作栏（复制按钮）
        self.center_toolbar = self.create_center_toolbar()

        # 右侧编辑器
        self.right_editor = DiffTextEdit()
        self.right_editor.is_left = False

        # 关联两个编辑器
        self.left_editor.other_editor = self.right_editor
        self.right_editor.other_editor = self.left_editor

        # 右侧导航条（只保留一个）
        self.navigator = DiffNavigator()
        self.navigator.is_left = True  # 显示左侧的行号映射

        main_layout.addWidget(self.left_editor, 1)
        main_layout.addWidget(self.center_toolbar)
        main_layout.addWidget(self.right_editor, 1)
        main_layout.addWidget(self.navigator)

        container = QWidget()
        container.setLayout(main_layout)
        layout.addWidget(container, 1)

        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("padding: 5px; background: #007acc; color: white; border: none;")
        layout.addWidget(self.status_label)

    def create_toolbar(self) -> QToolBar:
        """创建工具栏"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar { background: #2d2d2d; border-bottom: 1px solid #3c3c3c; padding: 2px; }
            QToolButton { background: transparent; color: #d4d4d4; padding: 5px 10px; margin: 2px; border-radius: 3px; }
            QToolButton:hover { background: #3c3c3c; }
            QToolButton:pressed { background: #094771; }
        """)

        # 打开文件按钮
        open_left_action = QAction("📂 左侧文件", self)
        open_left_action.triggered.connect(self.open_left_file)
        toolbar.addAction(open_left_action)

        open_right_action = QAction("📂 右侧文件", self)
        open_right_action.triggered.connect(self.open_right_file)
        toolbar.addAction(open_right_action)

        toolbar.addSeparator()

        # 比较按钮
        compare_action = QAction("🔍 比较", self)
        compare_action.triggered.connect(self.compare_files)
        toolbar.addAction(compare_action)

        toolbar.addSeparator()

        # 导航按钮
        prev_diff_action = QAction("⬆ 上一处差异", self)
        prev_diff_action.setShortcut(QKeySequence("Alt+Up"))
        prev_diff_action.triggered.connect(self.go_to_prev_diff)
        toolbar.addAction(prev_diff_action)

        next_diff_action = QAction("⬇ 下一处差异", self)
        next_diff_action.setShortcut(QKeySequence("Alt+Down"))
        next_diff_action.triggered.connect(self.go_to_next_diff)
        toolbar.addAction(next_diff_action)

        toolbar.addSeparator()

        # 合并按钮
        copy_to_right_action = QAction("➡ 复制到右侧", self)
        copy_to_right_action.triggered.connect(self.copy_to_right)
        toolbar.addAction(copy_to_right_action)

        copy_to_left_action = QAction("⬅ 复制到左侧", self)
        copy_to_left_action.triggered.connect(self.copy_to_left)
        toolbar.addAction(copy_to_left_action)

        toolbar.addSeparator()

        # 保存按钮
        save_left_action = QAction("💾 保存左侧", self)
        save_left_action.triggered.connect(self.save_left_file)
        toolbar.addAction(save_left_action)

        save_right_action = QAction("💾 保存右侧", self)
        save_right_action.triggered.connect(self.save_right_file)
        toolbar.addAction(save_right_action)

        toolbar.addSeparator()

        # 过滤按钮 - 使用 QWidget 容器
        filter_container = QWidget()
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setContentsMargins(5, 0, 5, 0)
        filter_layout.setSpacing(5)

        filter_btn_style = """
            QPushButton {
                background: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                padding: 3px 8px;
                border-radius: 3px;
                min-width: 50px;
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
            QPushButton:checked {
                background: #094771;
                border: 1px solid #0078d4;
                color: white;
            }
        """

        self.filter_all_btn = QPushButton("📋 全部")
        self.filter_all_btn.setCheckable(True)
        self.filter_all_btn.setChecked(True)
        self.filter_all_btn.setStyleSheet(filter_btn_style)
        self.filter_all_btn.clicked.connect(self.show_all_lines)

        self.filter_diff_btn = QPushButton("🔴 差异")
        self.filter_diff_btn.setCheckable(True)
        self.filter_diff_btn.setStyleSheet(filter_btn_style)
        self.filter_diff_btn.clicked.connect(self.show_diff_only)

        self.filter_same_btn = QPushButton("🟢 相同")
        self.filter_same_btn.setCheckable(True)
        self.filter_same_btn.setStyleSheet(filter_btn_style)
        self.filter_same_btn.clicked.connect(self.show_same_only)

        filter_layout.addWidget(self.filter_all_btn)
        filter_layout.addWidget(self.filter_diff_btn)
        filter_layout.addWidget(self.filter_same_btn)

        toolbar.addWidget(filter_container)

        return toolbar

    def create_center_toolbar(self) -> QWidget:
        """创建中间的操作按钮栏"""
        container = QWidget()
        container.setFixedWidth(36)
        container.setStyleSheet("background: #252526; border-left: 1px solid #3c3c3c; border-right: 1px solid #3c3c3c;")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(2, 5, 2, 5)
        layout.setSpacing(5)

        btn_style = """
            QPushButton {
                background: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 3px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #094771;
                border: 1px solid #0078d4;
            }
            QPushButton:pressed {
                background: #0078d4;
            }
        """

        # 复制到右侧按钮
        self.copy_to_right_btn = QPushButton("➡")
        self.copy_to_right_btn.setToolTip("复制当前差异到右侧")
        self.copy_to_right_btn.setStyleSheet(btn_style)
        self.copy_to_right_btn.clicked.connect(self.copy_current_diff_to_right)
        layout.addWidget(self.copy_to_right_btn)

        # 复制到左侧按钮
        self.copy_to_left_btn = QPushButton("⬅")
        self.copy_to_left_btn.setToolTip("复制当前差异到左侧")
        self.copy_to_left_btn.setStyleSheet(btn_style)
        self.copy_to_left_btn.clicked.connect(self.copy_current_diff_to_left)
        layout.addWidget(self.copy_to_left_btn)

        layout.addSpacing(10)

        # 上一处差异
        self.prev_diff_btn = QPushButton("▲")
        self.prev_diff_btn.setToolTip("上一处差异")
        self.prev_diff_btn.setStyleSheet(btn_style)
        self.prev_diff_btn.clicked.connect(self.go_to_prev_diff)
        layout.addWidget(self.prev_diff_btn)

        # 下一处差异
        self.next_diff_btn = QPushButton("▼")
        self.next_diff_btn.setToolTip("下一处差异")
        self.next_diff_btn.setStyleSheet(btn_style)
        self.next_diff_btn.clicked.connect(self.go_to_next_diff)
        layout.addWidget(self.next_diff_btn)

        layout.addStretch()

        return container

    def copy_current_diff_to_right(self):
        """复制当前差异块到右侧"""
        if not self.diff_blocks:
            return

        # 获取当前光标所在行
        cursor = self.left_editor.textCursor()
        current_line = cursor.blockNumber()

        # 找到包含此行的差异块
        for block in self.diff_blocks:
            if block.diff_type == DiffType.EQUAL:
                continue
            if block.left_start <= current_line < block.left_end:
                self.left_editor.copy_diff_block_to_other(current_line)
                self.status_label.setText(f"已复制差异块到右侧 (行 {block.left_start + 1}-{block.left_end})")
                return

        self.status_label.setText("当前行没有差异")

    def copy_current_diff_to_left(self):
        """复制当前差异块到左侧"""
        if not self.diff_blocks:
            return

        # 获取当前光标所在行
        cursor = self.right_editor.textCursor()
        current_line = cursor.blockNumber()

        # 找到包含此行的差异块
        for block in self.diff_blocks:
            if block.diff_type == DiffType.EQUAL:
                continue
            if block.right_start <= current_line < block.right_end:
                self.right_editor.copy_diff_block_to_other(current_line)
                self.status_label.setText(f"已复制差异块到左侧 (行 {block.right_start + 1}-{block.right_end})")
                return

        self.status_label.setText("当前行没有差异")

    def connect_signals(self):
        """连接信号"""
        # 同步滚动
        self.left_editor.scrolled.connect(self.sync_scroll_left)
        self.right_editor.scrolled.connect(self.sync_scroll_right)

        # 导航条点击
        self.navigator.clicked.connect(self.go_to_line)

    def update_navigator_viewport(self):
        """更新导航条的视口指示器位置"""
        # 获取当前可见的第一行
        first_visible_block = self.left_editor.firstVisibleBlock()
        current_line = first_visible_block.blockNumber()

        # 计算可见行数
        viewport_height = self.left_editor.viewport().height()
        line_height = self.left_editor.fontMetrics().lineSpacing()
        visible_lines = max(1, viewport_height // line_height) if line_height > 0 else 20

        # 更新导航条
        self.navigator.set_viewport(current_line, visible_lines)

    def sync_scroll_left(self, value):
        """同步左侧滚动到右侧"""
        self.right_editor.verticalScrollBar().blockSignals(True)
        self.right_editor.verticalScrollBar().setValue(value)
        self.right_editor.verticalScrollBar().blockSignals(False)
        # 更新导航条视口
        self.update_navigator_viewport()

    def sync_scroll_right(self, value):
        """同步右侧滚动到左侧"""
        self.left_editor.verticalScrollBar().blockSignals(True)
        self.left_editor.verticalScrollBar().setValue(value)
        self.left_editor.verticalScrollBar().blockSignals(False)
        # 更新导航条视口
        self.update_navigator_viewport()

    def open_left_file(self):
        """打开左侧文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择左侧文件", "", "所有文件 (*.*)")
        if file_path:
            self.load_left_file(file_path)

    def open_right_file(self):
        """打开右侧文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择右侧文件", "", "所有文件 (*.*)")
        if file_path:
            self.load_right_file(file_path)

    def detect_encoding(self, file_path: str) -> Tuple[str, float]:
        """
        检测文件编码
        返回: (编码名称, 置信度)
        支持: UTF-8, UTF-16, GB2312, GBK, GB18030, Big5, Shift_JIS 等
        """
        # 常见编码列表，按优先级排序
        common_encodings = [
            'utf-8',
            'utf-8-sig',  # 带BOM的UTF-8
            'utf-16',
            'utf-16-le',
            'utf-16-be',
            'gb2312',
            'gbk',
            'gb18030',
            'big5',
            'shift_jis',
            'euc-jp',
            'euc-kr',
            'iso-8859-1',
            'cp1252',  # Windows西欧
        ]

        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()

            # 检查BOM
            if raw_data.startswith(b'\xef\xbb\xbf'):
                return ('utf-8-sig', 1.0)
            elif raw_data.startswith(b'\xff\xfe'):
                return ('utf-16-le', 1.0)
            elif raw_data.startswith(b'\xfe\xff'):
                return ('utf-16-be', 1.0)

            # 使用chardet检测
            result = chardet.detect(raw_data)
            detected_encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0)

            if detected_encoding:
                # 标准化编码名称
                detected_encoding = detected_encoding.lower().replace('-', '_')

                # 处理一些常见的别名
                encoding_map = {
                    'ascii': 'utf-8',  # ASCII是UTF-8的子集
                    'iso_8859_1': 'iso-8859-1',
                    'windows_1252': 'cp1252',
                    'gb2312': 'gb18030',  # 使用更广泛的GB18030
                }

                if detected_encoding in encoding_map:
                    detected_encoding = encoding_map[detected_encoding]

                return (detected_encoding, confidence)

            return ('utf-8', 0.5)  # 默认使用UTF-8

        except Exception:
            return ('utf-8', 0.5)

    def is_binary_file(self, file_path: str) -> bool:
        """
        检测文件是否为二进制文件
        """
        # 已知的二进制文件扩展名
        binary_extensions = {
            # 数据库
            '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.dbf',
            # 可执行文件
            '.exe', '.dll', '.so', '.dylib', '.bin', '.com',
            # 压缩文件
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lz',
            # 图片
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.tiff', '.webp', '.psd',
            # 音频
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
            # 视频
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
            # 文档
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            # 其他
            '.class', '.pyc', '.pyo', '.o', '.obj', '.lib', '.a',
            '.jar', '.war', '.ear', '.dex', '.apk', '.ipa',
            '.ttf', '.otf', '.woff', '.woff2', '.eot',
            '.swf', '.fla',
        }

        _, ext = os.path.splitext(file_path.lower())
        if ext in binary_extensions:
            return True

        # 通过内容检测二进制
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)  # 读取前8KB

            if not chunk:
                return False

            # 检查是否包含NULL字节（二进制文件的常见特征）
            if b'\x00' in chunk:
                return True

            # 计算非文本字符的比例
            # 文本文件通常只包含可打印字符、空格、制表符和换行符
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
            non_text = sum(1 for byte in chunk if byte not in text_chars)

            # 如果非文本字符超过30%，认为是二进制
            if len(chunk) > 0 and (non_text / len(chunk)) > 0.30:
                return True

            return False

        except Exception:
            return False

    def format_binary_as_hex(self, file_path: str, max_size: int = 1024 * 1024) -> Tuple[str, str]:
        """
        将二进制文件转换为十六进制视图
        返回: (十六进制内容, 格式描述)
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read(max_size)

            file_size = os.path.getsize(file_path)
            truncated = file_size > max_size

            lines = []
            bytes_per_line = 16

            for offset in range(0, len(data), bytes_per_line):
                chunk = data[offset:offset + bytes_per_line]

                # 地址
                addr = f"{offset:08X}"

                # 十六进制部分
                hex_parts = []
                for i, byte in enumerate(chunk):
                    if i == 8:
                        hex_parts.append(' ')  # 中间加空格分隔
                    hex_parts.append(f"{byte:02X}")
                hex_str = ' '.join(hex_parts)

                # 补齐到固定宽度
                expected_len = 16 * 3 + 1 - 1  # 16个字节 * 3字符 + 1个中间空格 - 1个末尾空格
                hex_str = hex_str.ljust(expected_len)

                # ASCII部分
                ascii_parts = []
                for byte in chunk:
                    if 32 <= byte < 127:
                        ascii_parts.append(chr(byte))
                    else:
                        ascii_parts.append('.')
                ascii_str = ''.join(ascii_parts)

                lines.append(f"{addr}  {hex_str}  |{ascii_str}|")

            if truncated:
                lines.append(f"\n... (文件被截断，总大小: {file_size:,} 字节，仅显示前 {max_size:,} 字节)")

            format_desc = f"BINARY-HEX ({file_size:,} bytes)"
            return ('\n'.join(lines), format_desc)

        except Exception as e:
            return (f"无法读取二进制文件: {e}", "ERROR")

    def read_file_with_encoding(self, file_path: str) -> Tuple[str, str]:
        """
        智能读取文件，自动检测编码
        返回: (文件内容, 使用的编码)
        """
        encoding, confidence = self.detect_encoding(file_path)

        # 尝试使用检测到的编码读取
        encodings_to_try = [encoding]

        # 如果置信度不高，添加备选编码
        if confidence < 0.8:
            fallback_encodings = ['utf-8', 'gb18030', 'gbk', 'gb2312', 'big5', 'cp1252']
            for enc in fallback_encodings:
                if enc not in encodings_to_try:
                    encodings_to_try.append(enc)

        last_error = None
        for enc in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                return (content, enc)
            except (UnicodeDecodeError, LookupError) as e:
                last_error = e
                continue

        # 如果所有编码都失败，使用errors='replace'强制读取
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return (content, 'utf-8 (fallback)')
        except Exception as e:
            raise Exception(f"无法读取文件: {last_error or e}")

    def load_left_file(self, file_path: str):
        """加载左侧文件"""
        try:
            # 检测是否为二进制文件
            if self.is_binary_file(file_path):
                content, format_desc = self.format_binary_as_hex(file_path)
                self.left_editor.setPlainText(content)
                self.left_file_path = file_path
                self.left_path_label.setText(f"左侧: {os.path.basename(file_path)} [{format_desc}]")
                self.status_label.setText(f"已加载二进制文件: {file_path}")
                self.left_is_binary = True
            else:
                content, encoding = self.read_file_with_encoding(file_path)
                self.left_editor.setPlainText(content)
                self.left_file_path = file_path
                self.left_path_label.setText(f"左侧: {os.path.basename(file_path)} [{encoding.upper()}]")
                self.status_label.setText(f"已加载左侧文件: {file_path} (编码: {encoding})")
                self.left_is_binary = False
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {e}")

    def load_right_file(self, file_path: str):
        """加载右侧文件"""
        try:
            # 检测是否为二进制文件
            if self.is_binary_file(file_path):
                content, format_desc = self.format_binary_as_hex(file_path)
                self.right_editor.setPlainText(content)
                self.right_file_path = file_path
                self.right_path_label.setText(f"右侧: {os.path.basename(file_path)} [{format_desc}]")
                self.status_label.setText(f"已加载二进制文件: {file_path}")
                self.right_is_binary = True
            else:
                content, encoding = self.read_file_with_encoding(file_path)
                self.right_editor.setPlainText(content)
                self.right_file_path = file_path
                self.right_path_label.setText(f"右侧: {os.path.basename(file_path)} [{encoding.upper()}]")
                self.status_label.setText(f"已加载右侧文件: {file_path} (编码: {encoding})")
                self.right_is_binary = False
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {e}")

    def compare_files(self):
        """比较文件"""
        left_text = self.left_editor.toPlainText()
        right_text = self.right_editor.toPlainText()

        if not left_text and not right_text:
            QMessageBox.warning(self, "警告", "请先加载要比较的文件")
            return

        left_lines = left_text.splitlines(keepends=True)
        right_lines = right_text.splitlines(keepends=True)

        # 比较
        self.diff_blocks = self.diff_engine.compare_lines(left_lines, right_lines)

        # 应用高亮
        self.left_editor.set_diff_blocks(self.diff_blocks, is_left=True)
        self.right_editor.set_diff_blocks(self.diff_blocks, is_left=False)

        # 更新导航条
        total_lines = max(len(left_lines), len(right_lines))
        self.navigator.set_diff_blocks(self.diff_blocks, total_lines, is_left=True)

        # 同时将差异块传递给编辑器
        self.left_editor.diff_blocks = self.diff_blocks
        self.right_editor.diff_blocks = self.diff_blocks

        # 统计差异
        diff_count = sum(1 for b in self.diff_blocks if b.diff_type != DiffType.EQUAL)
        similarity = self.diff_engine.get_similarity_ratio(left_lines, right_lines)
        self.status_label.setText(f"发现 {diff_count} 处差异 | 相似度: {similarity:.1%}")

        # 重置当前差异索引
        self.current_diff_index = 0

    def go_to_line(self, line_num: int):
        """跳转到指定行"""
        self.left_editor.go_to_line(line_num)
        self.right_editor.go_to_line(line_num)

    def go_to_next_diff(self):
        """跳转到下一处差异"""
        diff_blocks = [b for b in self.diff_blocks if b.diff_type != DiffType.EQUAL]
        if not diff_blocks:
            return

        self.current_diff_index = (self.current_diff_index + 1) % len(diff_blocks)
        block = diff_blocks[self.current_diff_index]
        self.left_editor.go_to_line(block.left_start)
        self.right_editor.go_to_line(block.right_start)
        self.status_label.setText(f"差异 {self.current_diff_index + 1}/{len(diff_blocks)}")

    def go_to_prev_diff(self):
        """跳转到上一处差异"""
        diff_blocks = [b for b in self.diff_blocks if b.diff_type != DiffType.EQUAL]
        if not diff_blocks:
            return

        self.current_diff_index = (self.current_diff_index - 1) % len(diff_blocks)
        block = diff_blocks[self.current_diff_index]
        self.left_editor.go_to_line(block.left_start)
        self.right_editor.go_to_line(block.right_start)
        self.status_label.setText(f"差异 {self.current_diff_index + 1}/{len(diff_blocks)}")

    def copy_to_right(self):
        """将当前差异从左侧复制到右侧"""
        self._copy_diff(to_right=True)

    def copy_to_left(self):
        """将当前差异从右侧复制到左侧"""
        self._copy_diff(to_right=False)

    def _copy_diff(self, to_right: bool):
        """复制差异"""
        diff_blocks = [b for b in self.diff_blocks if b.diff_type != DiffType.EQUAL]
        if not diff_blocks or self.current_diff_index >= len(diff_blocks):
            return

        block = diff_blocks[self.current_diff_index]

        if to_right:
            # 获取左侧内容
            source_lines = block.left_lines
            target_editor = self.right_editor
            target_start = block.right_start
            target_end = block.right_end
        else:
            # 获取右侧内容
            source_lines = block.right_lines
            target_editor = self.left_editor
            target_start = block.left_start
            target_end = block.left_end

        # 替换目标编辑器中的内容
        cursor = target_editor.textCursor()

        # 选择要替换的行
        start_block = target_editor.document().findBlockByNumber(target_start)
        end_block = target_editor.document().findBlockByNumber(target_end)

        if start_block.isValid():
            cursor.setPosition(start_block.position())
            if end_block.isValid() and target_end > target_start:
                cursor.setPosition(end_block.position(), QTextCursor.MoveMode.KeepAnchor)
            elif target_end > target_start:
                cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)

            cursor.removeSelectedText()
            cursor.insertText(''.join(source_lines))

        # 重新比较
        self.compare_files()

    def save_left_file(self):
        """保存左侧文件"""
        if not self.left_file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "保存左侧文件", "", "所有文件 (*.*)")
            if file_path:
                self.left_file_path = file_path
            else:
                return

        try:
            with open(self.left_file_path, 'w', encoding='utf-8') as f:
                f.write(self.left_editor.toPlainText())
            self.status_label.setText(f"已保存: {self.left_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def save_right_file(self):
        """保存右侧文件"""
        if not self.right_file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "保存右侧文件", "", "所有文件 (*.*)")
            if file_path:
                self.right_file_path = file_path
            else:
                return

        try:
            with open(self.right_file_path, 'w', encoding='utf-8') as f:
                f.write(self.right_editor.toPlainText())
            self.status_label.setText(f"已保存: {self.right_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def load_files(self, left_path: str, right_path: str):
        """加载两个文件并比较"""
        self.load_left_file(left_path)
        self.load_right_file(right_path)
        QTimer.singleShot(100, self.compare_files)

    def _update_filter_buttons(self, active_btn):
        """更新过滤按钮状态"""
        buttons = [self.filter_all_btn, self.filter_diff_btn, self.filter_same_btn]
        for btn in buttons:
            btn.setChecked(btn == active_btn)

    def show_all_lines(self):
        """显示全部内容"""
        self._update_filter_buttons(self.filter_all_btn)
        # 重新比较显示全部
        if self.left_file_path and self.right_file_path:
            self.compare_files()

    def show_diff_only(self):
        """只显示差异部分"""
        self._update_filter_buttons(self.filter_diff_btn)
        if not self.diff_blocks:
            return

        # 构建只包含差异的内容
        left_lines = self.left_editor.toPlainText().split('\n')
        right_lines = self.right_editor.toPlainText().split('\n')

        left_diff_lines = []
        right_diff_lines = []

        for block in self.diff_blocks:
            if block.diff_type != DiffType.EQUAL:
                # 添加差异块的内容
                for i in range(block.left_start, block.left_end):
                    if i < len(left_lines):
                        left_diff_lines.append(f"L{i+1}: {left_lines[i]}")
                for i in range(block.right_start, block.right_end):
                    if i < len(right_lines):
                        right_diff_lines.append(f"R{i+1}: {right_lines[i]}")
                left_diff_lines.append("---")
                right_diff_lines.append("---")

        if left_diff_lines:
            self.left_editor.setPlainText('\n'.join(left_diff_lines))
        else:
            self.left_editor.setPlainText("无差异")

        if right_diff_lines:
            self.right_editor.setPlainText('\n'.join(right_diff_lines))
        else:
            self.right_editor.setPlainText("无差异")

        self.status_label.setText(f"显示 {len(self.diff_blocks)} 处差异")

    def show_same_only(self):
        """只显示相同部分"""
        self._update_filter_buttons(self.filter_same_btn)
        if not self.diff_blocks:
            return

        # 构建只包含相同内容的文本
        left_lines = self.left_editor.toPlainText().split('\n')

        same_lines = []
        for block in self.diff_blocks:
            if block.diff_type == DiffType.EQUAL:
                for i in range(block.left_start, block.left_end):
                    if i < len(left_lines):
                        same_lines.append(f"L{i+1}: {left_lines[i]}")

        if same_lines:
            self.left_editor.setPlainText('\n'.join(same_lines))
            self.right_editor.setPlainText('\n'.join(same_lines))
        else:
            self.left_editor.setPlainText("无相同内容")
            self.right_editor.setPlainText("无相同内容")

        self.status_label.setText("显示相同内容")
