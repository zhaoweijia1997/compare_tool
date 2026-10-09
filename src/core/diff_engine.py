"""
核心文件比较引擎
支持行级、字符级差异比较
"""
import difflib
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional
import hashlib


class DiffType(Enum):
    """差异类型"""
    EQUAL = "equal"       # 相同
    INSERT = "insert"     # 新增
    DELETE = "delete"     # 删除
    REPLACE = "replace"   # 修改


@dataclass
class DiffBlock:
    """差异块"""
    diff_type: DiffType
    left_start: int       # 左侧起始行号 (0-indexed)
    left_end: int         # 左侧结束行号
    right_start: int      # 右侧起始行号
    right_end: int        # 右侧结束行号
    left_lines: List[str] = field(default_factory=list)   # 左侧行内容
    right_lines: List[str] = field(default_factory=list)  # 右侧行内容

    @property
    def left_count(self) -> int:
        return self.left_end - self.left_start

    @property
    def right_count(self) -> int:
        return self.right_end - self.right_start


@dataclass
class CharDiff:
    """字符级差异"""
    diff_type: DiffType
    text: str


@dataclass
class LineDiff:
    """行级差异，包含字符级细节"""
    line_num: int
    diff_type: DiffType
    text: str
    char_diffs: List[CharDiff] = field(default_factory=list)


class DiffEngine:
    """文件差异比较引擎"""

    def __init__(self):
        self.ignore_whitespace = False
        self.ignore_case = False
        self.ignore_blank_lines = False
        self.align_similar_lines = True  # 对齐相似行

    def compare_files(self, file1_path: str, file2_path: str) -> List[DiffBlock]:
        """比较两个文件"""
        try:
            with open(file1_path, 'r', encoding='utf-8', errors='replace') as f:
                lines1 = f.readlines()
            with open(file2_path, 'r', encoding='utf-8', errors='replace') as f:
                lines2 = f.readlines()
        except Exception as e:
            raise Exception(f"读取文件失败: {e}")

        return self.compare_lines(lines1, lines2)

    def compare_lines(self, lines1: List[str], lines2: List[str]) -> List[DiffBlock]:
        """比较两个行列表，支持跨空行对齐"""
        # 预处理
        processed1 = self._preprocess_lines(lines1)
        processed2 = self._preprocess_lines(lines2)

        # 使用改进的比较算法
        if self.align_similar_lines:
            # 使用带权重的比较，让相似行更容易对齐
            matcher = difflib.SequenceMatcher(
                lambda x: x.strip() == '',  # 将空行视为垃圾字符，提高对齐效果
                processed1,
                processed2,
                autojunk=False  # 禁用自动垃圾检测以获得更精确的结果
            )
        else:
            matcher = difflib.SequenceMatcher(None, processed1, processed2)

        opcodes = matcher.get_opcodes()

        blocks = []
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                diff_type = DiffType.EQUAL
            elif tag == 'insert':
                diff_type = DiffType.INSERT
            elif tag == 'delete':
                diff_type = DiffType.DELETE
            else:  # replace
                diff_type = DiffType.REPLACE

            block = DiffBlock(
                diff_type=diff_type,
                left_start=i1,
                left_end=i2,
                right_start=j1,
                right_end=j2,
                left_lines=lines1[i1:i2],
                right_lines=lines2[j1:j2]
            )
            blocks.append(block)

        # 合并优化：对于较大的replace块，尝试细分以找到更多匹配
        blocks = self._optimize_replace_blocks(blocks, lines1, lines2)

        return blocks

    def _optimize_replace_blocks(self, blocks: List[DiffBlock], lines1: List[str], lines2: List[str]) -> List[DiffBlock]:
        """优化replace块，尝试在其中找到更多匹配的行"""
        optimized = []

        for block in blocks:
            if block.diff_type == DiffType.REPLACE and block.left_count > 1 and block.right_count > 1:
                # 对于较大的replace块，尝试更精细的匹配
                sub_blocks = self._refine_replace_block(block, lines1, lines2)
                optimized.extend(sub_blocks)
            else:
                optimized.append(block)

        return optimized

    def _refine_replace_block(self, block: DiffBlock, lines1: List[str], lines2: List[str]) -> List[DiffBlock]:
        """细化replace块，寻找其中相同的行"""
        left_lines = block.left_lines
        right_lines = block.right_lines

        # 使用更细粒度的比较
        matcher = difflib.SequenceMatcher(
            lambda x: x.strip() == '',
            [l.strip() for l in left_lines],
            [l.strip() for l in right_lines],
            autojunk=False
        )

        sub_opcodes = matcher.get_opcodes()

        # 如果细化后只有一个块，直接返回原块
        if len(sub_opcodes) == 1:
            return [block]

        result = []
        for tag, i1, i2, j1, j2 in sub_opcodes:
            if tag == 'equal':
                diff_type = DiffType.EQUAL
            elif tag == 'insert':
                diff_type = DiffType.INSERT
            elif tag == 'delete':
                diff_type = DiffType.DELETE
            else:
                diff_type = DiffType.REPLACE

            sub_block = DiffBlock(
                diff_type=diff_type,
                left_start=block.left_start + i1,
                left_end=block.left_start + i2,
                right_start=block.right_start + j1,
                right_end=block.right_start + j2,
                left_lines=left_lines[i1:i2],
                right_lines=right_lines[j1:j2]
            )
            result.append(sub_block)

        return result

    def _preprocess_lines(self, lines: List[str]) -> List[str]:
        """预处理行内容"""
        result = []
        for line in lines:
            processed = line
            if self.ignore_whitespace:
                processed = ' '.join(processed.split())
            if self.ignore_case:
                processed = processed.lower()
            result.append(processed)

        if self.ignore_blank_lines:
            result = [l for l in result if l.strip()]

        return result

    def get_char_diff(self, line1: str, line2: str) -> Tuple[List[CharDiff], List[CharDiff]]:
        """获取两行之间的字符级差异"""
        matcher = difflib.SequenceMatcher(None, line1, line2)
        opcodes = matcher.get_opcodes()

        left_diffs = []
        right_diffs = []

        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                left_diffs.append(CharDiff(DiffType.EQUAL, line1[i1:i2]))
                right_diffs.append(CharDiff(DiffType.EQUAL, line2[j1:j2]))
            elif tag == 'insert':
                right_diffs.append(CharDiff(DiffType.INSERT, line2[j1:j2]))
            elif tag == 'delete':
                left_diffs.append(CharDiff(DiffType.DELETE, line1[i1:i2]))
            else:  # replace
                left_diffs.append(CharDiff(DiffType.REPLACE, line1[i1:i2]))
                right_diffs.append(CharDiff(DiffType.REPLACE, line2[j1:j2]))

        return left_diffs, right_diffs

    def get_similarity_ratio(self, lines1: List[str], lines2: List[str]) -> float:
        """计算两个文件的相似度 (0.0 - 1.0)"""
        text1 = ''.join(lines1)
        text2 = ''.join(lines2)
        return difflib.SequenceMatcher(None, text1, text2).ratio()


class FolderDiffEngine:
    """文件夹差异比较引擎"""

    @dataclass
    class FileInfo:
        """文件信息"""
        name: str
        path: str
        size: int
        modified_time: float
        is_dir: bool

    @dataclass
    class CompareResult:
        """比较结果"""
        name: str
        left_path: Optional[str]
        right_path: Optional[str]
        status: str  # 'same', 'different', 'left_only', 'right_only'
        is_dir: bool
        left_size: Optional[int] = None
        right_size: Optional[int] = None
        relative_path: str = ""  # 相对路径（用于递归比较）

    def __init__(self):
        self.include_hidden = False
        self.compare_content = True  # True: 比较内容, False: 只比较大小和时间

    def compare_folders(self, folder1: str, folder2: str) -> List['FolderDiffEngine.CompareResult']:
        """比较两个文件夹"""
        results = []

        # 获取两个文件夹的内容
        items1 = self._get_folder_items(folder1)
        items2 = self._get_folder_items(folder2)

        names1 = {item.name: item for item in items1}
        names2 = {item.name: item for item in items2}

        all_names = set(names1.keys()) | set(names2.keys())

        for name in sorted(all_names):
            item1 = names1.get(name)
            item2 = names2.get(name)

            if item1 and item2:
                # 两边都有
                if item1.is_dir and item2.is_dir:
                    status = 'same'  # 目录暂时标记为相同
                elif item1.is_dir != item2.is_dir:
                    status = 'different'  # 一个是文件一个是目录
                else:
                    # 都是文件，比较内容
                    if self.compare_content:
                        status = 'same' if self._files_equal(item1.path, item2.path) else 'different'
                    else:
                        status = 'same' if item1.size == item2.size else 'different'

                results.append(self.CompareResult(
                    name=name,
                    left_path=item1.path,
                    right_path=item2.path,
                    status=status,
                    is_dir=item1.is_dir,
                    left_size=item1.size,
                    right_size=item2.size
                ))
            elif item1:
                # 只在左边
                results.append(self.CompareResult(
                    name=name,
                    left_path=item1.path,
                    right_path=None,
                    status='left_only',
                    is_dir=item1.is_dir,
                    left_size=item1.size
                ))
            else:
                # 只在右边
                results.append(self.CompareResult(
                    name=name,
                    left_path=None,
                    right_path=item2.path,
                    status='right_only',
                    is_dir=item2.is_dir,
                    right_size=item2.size
                ))

        return results

    def _get_folder_items(self, folder: str) -> List['FolderDiffEngine.FileInfo']:
        """获取文件夹中的所有项目"""
        items = []
        try:
            for name in os.listdir(folder):
                if not self.include_hidden and name.startswith('.'):
                    continue

                path = os.path.join(folder, name)
                try:
                    stat = os.stat(path)
                    items.append(self.FileInfo(
                        name=name,
                        path=path,
                        size=stat.st_size if not os.path.isdir(path) else 0,
                        modified_time=stat.st_mtime,
                        is_dir=os.path.isdir(path)
                    ))
                except OSError:
                    continue
        except OSError:
            pass

        return items

    def _files_equal(self, file1: str, file2: str) -> bool:
        """比较两个文件是否相同（使用MD5）"""
        try:
            return self._file_hash(file1) == self._file_hash(file2)
        except:
            return False

    def _file_hash(self, filepath: str) -> str:
        """计算文件MD5"""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
