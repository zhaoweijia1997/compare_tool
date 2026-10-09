"""
文件夹比较视图
支持递归比较、树状结构显示、文件状态显示、批量操作
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QToolBar, QPushButton, QFileDialog, QMessageBox,
    QProgressDialog, QMenu, QSplitter, QHeaderView, QApplication
)
from PySide6.QtCore import Qt, Signal, QThread, QSize
from PySide6.QtGui import QColor, QBrush, QIcon, QAction, QFont
import os
import shutil
from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import Enum

import sys

# 添加路径以支持不同的运行环境
if getattr(sys, 'frozen', False):
    _base_path = sys._MEIPASS
else:
    _base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _base_path)

from src.core.diff_engine import FolderDiffEngine


class FileStatus(Enum):
    """文件状态"""
    SAME = "same"
    DIFFERENT = "different"
    LEFT_ONLY = "left_only"
    RIGHT_ONLY = "right_only"


@dataclass
class TreeNode:
    """树节点数据"""
    name: str
    is_dir: bool
    status: str
    left_path: Optional[str]
    right_path: Optional[str]
    left_size: Optional[int]
    right_size: Optional[int]
    children: Dict[str, 'TreeNode'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = {}


class CompareWorker(QThread):
    """后台比较线程"""
    progress = Signal(str)
    finished = Signal(object)  # 返回树结构
    error = Signal(str)

    def __init__(self, left_path: str, right_path: str):
        super().__init__()
        self.left_path = left_path
        self.right_path = right_path
        self.engine = FolderDiffEngine()

    def run(self):
        try:
            # 构建树状结构
            root = TreeNode(
                name="",
                is_dir=True,
                status="same",
                left_path=self.left_path,
                right_path=self.right_path,
                left_size=None,
                right_size=None
            )
            self._build_tree(self.left_path, self.right_path, root)
            self.finished.emit(root)
        except Exception as e:
            self.error.emit(str(e))

    def _build_tree(self, left_dir: str, right_dir: str, parent_node: TreeNode):
        """递归构建比较树"""
        self.progress.emit(f"正在扫描: {left_dir or right_dir}")

        # 获取左右两侧的文件列表
        left_items = set()
        right_items = set()

        if left_dir and os.path.isdir(left_dir):
            try:
                left_items = set(os.listdir(left_dir))
            except PermissionError:
                pass

        if right_dir and os.path.isdir(right_dir):
            try:
                right_items = set(os.listdir(right_dir))
            except PermissionError:
                pass

        # 合并所有项目名
        all_items = left_items | right_items

        for name in sorted(all_items):
            left_path = os.path.join(left_dir, name) if left_dir and name in left_items else None
            right_path = os.path.join(right_dir, name) if right_dir and name in right_items else None

            # 确定是否是目录
            is_dir = False
            if left_path and os.path.isdir(left_path):
                is_dir = True
            elif right_path and os.path.isdir(right_path):
                is_dir = True

            # 确定状态
            if left_path and right_path:
                if is_dir:
                    # 目录先标记为same，后面根据子项更新
                    status = "same"
                else:
                    # 比较文件内容
                    status = self._compare_files(left_path, right_path)
            elif left_path:
                status = "left_only"
            else:
                status = "right_only"

            # 获取文件大小
            left_size = None
            right_size = None
            if left_path and os.path.isfile(left_path):
                try:
                    left_size = os.path.getsize(left_path)
                except:
                    pass
            if right_path and os.path.isfile(right_path):
                try:
                    right_size = os.path.getsize(right_path)
                except:
                    pass

            # 创建节点
            node = TreeNode(
                name=name,
                is_dir=is_dir,
                status=status,
                left_path=left_path,
                right_path=right_path,
                left_size=left_size,
                right_size=right_size
            )

            # 如果是目录，递归处理
            if is_dir:
                self._build_tree(left_path, right_path, node)
                # 更新目录状态（根据子项）
                node.status = self._calc_dir_status(node)

            parent_node.children[name] = node

    def _compare_files(self, left: str, right: str) -> str:
        """比较两个文件"""
        try:
            # 先比较大小
            left_size = os.path.getsize(left)
            right_size = os.path.getsize(right)
            if left_size != right_size:
                return "different"

            # 比较内容（使用MD5）
            import hashlib

            def get_hash(path):
                h = hashlib.md5()
                with open(path, 'rb') as f:
                    while chunk := f.read(8192):
                        h.update(chunk)
                return h.hexdigest()

            if get_hash(left) == get_hash(right):
                return "same"
            else:
                return "different"
        except:
            return "different"

    def _calc_dir_status(self, node: TreeNode) -> str:
        """计算目录状态"""
        if not node.children:
            return "same"

        has_diff = False
        has_left_only = False
        has_right_only = False

        for child in node.children.values():
            if child.status == "different":
                has_diff = True
            elif child.status == "left_only":
                has_left_only = True
            elif child.status == "right_only":
                has_right_only = True

        if has_diff or has_left_only or has_right_only:
            return "different"
        return "same"


class FolderTreeWidget(QTreeWidget):
    """文件夹树形控件"""

    item_double_clicked = Signal(str, str)  # left_path, right_path

    # 颜色定义 - 深色主题
    COLORS = {
        'same': QColor(30, 30, 30),              # 深灰色
        'different': QColor(90, 70, 40),         # 深黄色
        'left_only': QColor(90, 40, 40),         # 深红色
        'right_only': QColor(40, 70, 40),        # 深绿色
    }

    # 状态图标
    STATUS_ICONS = {
        'same': "✓",
        'different': "≠",
        'left_only': "←",
        'right_only': "→",
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置列
        self.setHeaderLabels(["名称", "状态", "左侧大小", "右侧大小", "左侧路径", "右侧路径"])
        self.setColumnCount(6)

        # 设置列宽
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 60)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 100)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 100)

        # 隐藏路径列（但保留数据）
        self.setColumnHidden(4, True)
        self.setColumnHidden(5, True)

        # 设置字体
        font = QFont("Consolas", 10)
        self.setFont(font)

        # 启用排序
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # 启用多选
        self.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)

        # 右键菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # 双击事件
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

    def build_tree_from_node(self, node: TreeNode, parent_item=None):
        """从树节点构建显示树"""
        for name in sorted(node.children.keys()):
            child_node = node.children[name]
            item = self._create_item(child_node, parent_item)

            # 如果是目录且有子项，递归构建
            if child_node.is_dir and child_node.children:
                self.build_tree_from_node(child_node, item)

    def _create_item(self, node: TreeNode, parent_item=None) -> QTreeWidgetItem:
        """创建树项"""
        if parent_item:
            item = QTreeWidgetItem(parent_item)
        else:
            item = QTreeWidgetItem(self)

        # 名称 (带图标)
        icon = "📁 " if node.is_dir else "📄 "
        item.setText(0, icon + node.name)

        # 状态
        status_icon = self.STATUS_ICONS.get(node.status, "?")
        item.setText(1, status_icon)

        # 大小
        if node.left_size is not None:
            item.setText(2, self._format_size(node.left_size))
        if node.right_size is not None:
            item.setText(3, self._format_size(node.right_size))

        # 路径
        item.setText(4, node.left_path or "")
        item.setText(5, node.right_path or "")

        # 背景色
        color = self.COLORS.get(node.status, QColor(30, 30, 30))
        for col in range(6):
            item.setBackground(col, QBrush(color))

        # 存储数据
        item.setData(0, Qt.ItemDataRole.UserRole, node)

        return item

    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """双击项目"""
        node = item.data(0, Qt.ItemDataRole.UserRole)
        if node and not node.is_dir:
            self.item_double_clicked.emit(node.left_path or "", node.right_path or "")

    def show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.itemAt(pos)
        if not item:
            return

        node = item.data(0, Qt.ItemDataRole.UserRole)
        if not node:
            return

        menu = QMenu(self)

        if not node.is_dir:
            compare_action = menu.addAction("🔍 比较文件")
            compare_action.triggered.connect(lambda: self.item_double_clicked.emit(
                node.left_path or "", node.right_path or ""))

        menu.addSeparator()

        if node.status in ['left_only', 'different']:
            copy_right = menu.addAction("➡ 复制到右侧")
            copy_right.triggered.connect(lambda: self.copy_to_right(node))

        if node.status in ['right_only', 'different']:
            copy_left = menu.addAction("⬅ 复制到左侧")
            copy_left.triggered.connect(lambda: self.copy_to_left(node))

        menu.addSeparator()

        if node.left_path:
            delete_left = menu.addAction("🗑 删除左侧")
            delete_left.triggered.connect(lambda: self.delete_file(node.left_path))

        if node.right_path:
            delete_right = menu.addAction("🗑 删除右侧")
            delete_right.triggered.connect(lambda: self.delete_file(node.right_path))

        # 展开/折叠
        if node.is_dir:
            menu.addSeparator()
            if item.isExpanded():
                collapse_action = menu.addAction("📁 折叠")
                collapse_action.triggered.connect(lambda: item.setExpanded(False))
            else:
                expand_action = menu.addAction("📂 展开")
                expand_action.triggered.connect(lambda: item.setExpanded(True))

            expand_all = menu.addAction("📂 展开所有子项")
            expand_all.triggered.connect(lambda: self._expand_recursive(item, True))

            collapse_all = menu.addAction("📁 折叠所有子项")
            collapse_all.triggered.connect(lambda: self._expand_recursive(item, False))

        menu.exec(self.mapToGlobal(pos))

    def _expand_recursive(self, item: QTreeWidgetItem, expand: bool):
        """递归展开/折叠"""
        item.setExpanded(expand)
        for i in range(item.childCount()):
            self._expand_recursive(item.child(i), expand)

    def copy_to_right(self, node: TreeNode):
        """复制到右侧"""
        if not node.left_path or not node.right_path:
            return
        try:
            if node.is_dir:
                shutil.copytree(node.left_path, node.right_path, dirs_exist_ok=True)
            else:
                os.makedirs(os.path.dirname(node.right_path), exist_ok=True)
                shutil.copy2(node.left_path, node.right_path)
            QMessageBox.information(self, "成功", "复制完成")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制失败: {e}")

    def copy_to_left(self, node: TreeNode):
        """复制到左侧"""
        if not node.left_path or not node.right_path:
            return
        try:
            if node.is_dir:
                shutil.copytree(node.right_path, node.left_path, dirs_exist_ok=True)
            else:
                os.makedirs(os.path.dirname(node.left_path), exist_ok=True)
                shutil.copy2(node.right_path, node.left_path)
            QMessageBox.information(self, "成功", "复制完成")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制失败: {e}")

    def delete_file(self, path: str):
        """删除文件"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {path} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                QMessageBox.information(self, "成功", "删除完成")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除失败: {e}")

    def filter_items(self, statuses: Optional[List[str]]):
        """过滤显示项目"""
        self._filter_recursive(self.invisibleRootItem(), statuses)

    def _filter_recursive(self, parent_item: QTreeWidgetItem, statuses: Optional[List[str]]) -> bool:
        """递归过滤项目，返回是否有可见子项"""
        has_visible_child = False

        for i in range(parent_item.childCount()):
            item = parent_item.child(i)
            node = item.data(0, Qt.ItemDataRole.UserRole)

            if node:
                # 如果是目录，先检查子项
                if node.is_dir:
                    child_visible = self._filter_recursive(item, statuses)
                    # 目录：如果有匹配的子项则显示，或者目录本身状态匹配
                    if statuses is None:
                        item.setHidden(False)
                        has_visible_child = True
                    elif child_visible or node.status in statuses:
                        item.setHidden(False)
                        has_visible_child = True
                    else:
                        item.setHidden(True)
                else:
                    # 文件：根据状态过滤
                    if statuses is None or node.status in statuses:
                        item.setHidden(False)
                        has_visible_child = True
                    else:
                        item.setHidden(True)

        return has_visible_child

    def count_items(self) -> Dict[str, int]:
        """统计各状态项目数量"""
        counts = {'same': 0, 'different': 0, 'left_only': 0, 'right_only': 0, 'total': 0}
        self._count_recursive(self.invisibleRootItem(), counts)
        return counts

    def _count_recursive(self, parent_item: QTreeWidgetItem, counts: Dict[str, int]):
        """递归统计"""
        for i in range(parent_item.childCount()):
            item = parent_item.child(i)
            node = item.data(0, Qt.ItemDataRole.UserRole)
            if node:
                # 只统计文件，不统计目录
                if not node.is_dir:
                    counts['total'] += 1
                    if node.status in counts:
                        counts[node.status] += 1
                # 递归统计子项
                self._count_recursive(item, counts)


class FolderViewWidget(QWidget):
    """文件夹比较视图主控件"""

    open_file_compare = Signal(str, str)  # 打开文件比较信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.left_folder = ""
        self.right_folder = ""
        self.compare_worker: Optional[CompareWorker] = None
        self.root_node: Optional[TreeNode] = None

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 工具栏
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)

        # 文件夹路径栏
        path_layout = QHBoxLayout()

        self.left_path_label = QLabel("左侧文件夹: 未选择")
        self.left_path_label.setStyleSheet("padding: 5px; background: #252526; color: #d4d4d4; border: 1px solid #3c3c3c;")
        path_layout.addWidget(self.left_path_label)

        self.right_path_label = QLabel("右侧文件夹: 未选择")
        self.right_path_label.setStyleSheet("padding: 5px; background: #252526; color: #d4d4d4; border: 1px solid #3c3c3c;")
        path_layout.addWidget(self.right_path_label)

        layout.addLayout(path_layout)

        # 文件树
        self.tree = FolderTreeWidget()
        self.tree.item_double_clicked.connect(self.on_file_double_clicked)
        layout.addWidget(self.tree, 1)

        # 状态栏
        status_layout = QHBoxLayout()

        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("padding: 5px;")
        status_layout.addWidget(self.status_label, 1)

        # 过滤按钮样式
        filter_btn_style = """
            QPushButton {
                background: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                padding: 4px 8px;
                border-radius: 3px;
                min-width: 60px;
            }
            QPushButton:hover {
                background: #4a4a4a;
                border: 1px solid #666;
            }
            QPushButton:checked {
                background: #094771;
                border: 1px solid #0078d4;
                color: white;
            }
        """

        # 过滤按钮
        self.filter_all_btn = QPushButton("📋 全部")
        self.filter_all_btn.setCheckable(True)
        self.filter_all_btn.setChecked(True)
        self.filter_all_btn.setStyleSheet(filter_btn_style)
        self.filter_all_btn.clicked.connect(self.show_all)

        self.filter_diff_btn = QPushButton("🔴 不同")
        self.filter_diff_btn.setCheckable(True)
        self.filter_diff_btn.setChecked(False)
        self.filter_diff_btn.setStyleSheet(filter_btn_style)
        self.filter_diff_btn.clicked.connect(self.show_different_only)

        self.filter_same_btn = QPushButton("🟢 相同")
        self.filter_same_btn.setCheckable(True)
        self.filter_same_btn.setChecked(False)
        self.filter_same_btn.setStyleSheet(filter_btn_style)
        self.filter_same_btn.clicked.connect(self.show_same_only)

        self.filter_left_btn = QPushButton("⬅ 仅左")
        self.filter_left_btn.setCheckable(True)
        self.filter_left_btn.setChecked(False)
        self.filter_left_btn.setStyleSheet(filter_btn_style)
        self.filter_left_btn.clicked.connect(self.show_left_only)

        self.filter_right_btn = QPushButton("➡ 仅右")
        self.filter_right_btn.setCheckable(True)
        self.filter_right_btn.setChecked(False)
        self.filter_right_btn.setStyleSheet(filter_btn_style)
        self.filter_right_btn.clicked.connect(self.show_right_only)

        status_layout.addWidget(self.filter_all_btn)
        status_layout.addWidget(self.filter_diff_btn)
        status_layout.addWidget(self.filter_same_btn)
        status_layout.addWidget(self.filter_left_btn)
        status_layout.addWidget(self.filter_right_btn)

        status_container = QWidget()
        status_container.setLayout(status_layout)
        status_container.setStyleSheet("background: #252526; border-top: 1px solid #3c3c3c;")
        layout.addWidget(status_container)

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

        # 打开文件夹按钮
        open_left = QAction("📂 左侧文件夹", self)
        open_left.triggered.connect(self.open_left_folder)
        toolbar.addAction(open_left)

        open_right = QAction("📂 右侧文件夹", self)
        open_right.triggered.connect(self.open_right_folder)
        toolbar.addAction(open_right)

        toolbar.addSeparator()

        # 比较按钮
        compare = QAction("🔍 比较", self)
        compare.triggered.connect(self.compare_folders)
        toolbar.addAction(compare)

        # 刷新按钮
        refresh = QAction("🔄 刷新", self)
        refresh.triggered.connect(self.compare_folders)
        toolbar.addAction(refresh)

        toolbar.addSeparator()

        # 展开/折叠按钮
        expand_all = QAction("📂 全部展开", self)
        expand_all.triggered.connect(self.expand_all)
        toolbar.addAction(expand_all)

        collapse_all = QAction("📁 全部折叠", self)
        collapse_all.triggered.connect(self.collapse_all)
        toolbar.addAction(collapse_all)

        toolbar.addSeparator()

        # 批量操作
        sync_left = QAction("⬅ 同步到左侧", self)
        sync_left.triggered.connect(self.sync_to_left)
        toolbar.addAction(sync_left)

        sync_right = QAction("➡ 同步到右侧", self)
        sync_right.triggered.connect(self.sync_to_right)
        toolbar.addAction(sync_right)

        return toolbar

    def expand_all(self):
        """展开所有项"""
        self.tree.expandAll()

    def collapse_all(self):
        """折叠所有项"""
        self.tree.collapseAll()

    def open_left_folder(self):
        """选择左侧文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择左侧文件夹")
        if folder:
            self.left_folder = folder
            self.left_path_label.setText(f"左侧: {folder}")
            self.status_label.setText("已选择左侧文件夹")

    def open_right_folder(self):
        """选择右侧文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择右侧文件夹")
        if folder:
            self.right_folder = folder
            self.right_path_label.setText(f"右侧: {folder}")
            self.status_label.setText("已选择右侧文件夹")

    def compare_folders(self):
        """开始比较文件夹"""
        if not self.left_folder or not self.right_folder:
            QMessageBox.warning(self, "警告", "请先选择两个文件夹")
            return

        # 清空当前结果
        self.tree.clear()
        self.root_node = None

        # 创建后台线程进行比较
        self.compare_worker = CompareWorker(self.left_folder, self.right_folder)
        self.compare_worker.progress.connect(self.on_compare_progress)
        self.compare_worker.finished.connect(self.on_compare_finished)
        self.compare_worker.error.connect(self.on_compare_error)
        self.compare_worker.start()

        self.status_label.setText("正在比较...")

    def on_compare_progress(self, message: str):
        """比较进度"""
        self.status_label.setText(message)

    def on_compare_finished(self, root_node: TreeNode):
        """比较完成"""
        self.root_node = root_node

        # 构建树形显示
        self.tree.build_tree_from_node(root_node)

        # 默认展开第一层
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setExpanded(True)

        # 统计
        counts = self.tree.count_items()
        self.status_label.setText(
            f"比较完成: {counts['total']} 个文件 | "
            f"✓相同: {counts['same']} | ≠不同: {counts['different']} | "
            f"←仅左侧: {counts['left_only']} | →仅右侧: {counts['right_only']}"
        )

    def on_compare_error(self, error: str):
        """比较错误"""
        QMessageBox.critical(self, "错误", f"比较失败: {error}")
        self.status_label.setText("比较失败")

    def _update_filter_buttons(self, active_btn):
        """更新过滤按钮状态，实现单选效果"""
        buttons = [self.filter_all_btn, self.filter_diff_btn, self.filter_same_btn,
                   self.filter_left_btn, self.filter_right_btn]
        for btn in buttons:
            btn.setChecked(btn == active_btn)

    def show_all(self):
        """显示全部"""
        self._update_filter_buttons(self.filter_all_btn)
        self.tree.filter_items(None)

    def show_different_only(self):
        """只显示不同的"""
        self._update_filter_buttons(self.filter_diff_btn)
        self.tree.filter_items(['different', 'left_only', 'right_only'])

    def show_same_only(self):
        """只显示相同的"""
        self._update_filter_buttons(self.filter_same_btn)
        self.tree.filter_items(['same'])

    def show_left_only(self):
        """只显示仅左侧有的"""
        self._update_filter_buttons(self.filter_left_btn)
        self.tree.filter_items(['left_only'])

    def show_right_only(self):
        """只显示仅右侧有的"""
        self._update_filter_buttons(self.filter_right_btn)
        self.tree.filter_items(['right_only'])

    def on_file_double_clicked(self, left_path: str, right_path: str):
        """双击文件"""
        self.open_file_compare.emit(left_path, right_path)

    def sync_to_left(self):
        """同步选中项到左侧"""
        selected = self.tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择要同步的项目")
            return

        reply = QMessageBox.question(
            self, "确认同步",
            f"确定要将 {len(selected)} 个项目同步到左侧吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for item in selected:
                node = item.data(0, Qt.ItemDataRole.UserRole)
                if node and node.right_path:
                    self.tree.copy_to_left(node)

    def sync_to_right(self):
        """同步选中项到右侧"""
        selected = self.tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择要同步的项目")
            return

        reply = QMessageBox.question(
            self, "确认同步",
            f"确定要将 {len(selected)} 个项目同步到右侧吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for item in selected:
                node = item.data(0, Qt.ItemDataRole.UserRole)
                if node and node.left_path:
                    self.tree.copy_to_right(node)

    def load_folders(self, left: str, right: str):
        """加载文件夹并比较"""
        self.left_folder = left
        self.right_folder = right
        self.left_path_label.setText(f"左侧: {left}")
        self.right_path_label.setText(f"右侧: {right}")
        self.compare_folders()

    def stop_worker(self):
        """停止后台比较线程"""
        if self.compare_worker and self.compare_worker.isRunning():
            self.compare_worker.terminate()
            self.compare_worker.wait(1000)  # 等待最多1秒
            self.compare_worker = None
