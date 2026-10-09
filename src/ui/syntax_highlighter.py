"""
语法高亮器
支持多种编程语言的语法高亮
"""
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextDocument
)
from typing import Dict, List, Tuple
import os


class SyntaxHighlighter(QSyntaxHighlighter):
    """通用语法高亮器"""

    def __init__(self, document: QTextDocument, language: str = ""):
        super().__init__(document)
        self.language = language.lower()
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.setup_formats()
        self.setup_rules()

    def setup_formats(self):
        """设置格式"""
        # 关键字格式
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#0000FF"))
        self.keyword_format.setFontWeight(QFont.Weight.Bold)

        # 类名格式
        self.class_format = QTextCharFormat()
        self.class_format.setForeground(QColor("#2B91AF"))
        self.class_format.setFontWeight(QFont.Weight.Bold)

        # 函数格式
        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor("#795E26"))

        # 字符串格式
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#A31515"))

        # 注释格式 (BeyondCompare风格 - 蓝色)
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#0066CC"))  # 蓝色注释
        self.comment_format.setFontItalic(True)

        # 数字格式
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#098658"))

        # 装饰器格式
        self.decorator_format = QTextCharFormat()
        self.decorator_format.setForeground(QColor("#AF00DB"))

        # 运算符格式
        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor("#000000"))

    def setup_rules(self):
        """设置语法规则"""
        self.highlighting_rules = []

        if self.language in ["python", "py"]:
            self._setup_python_rules()
        elif self.language in ["javascript", "js", "typescript", "ts"]:
            self._setup_javascript_rules()
        elif self.language in ["c", "cpp", "c++", "h", "hpp"]:
            self._setup_cpp_rules()
        elif self.language in ["java"]:
            self._setup_java_rules()
        elif self.language in ["html", "htm", "xml"]:
            self._setup_html_rules()
        elif self.language in ["css"]:
            self._setup_css_rules()
        elif self.language in ["json"]:
            self._setup_json_rules()
        elif self.language in ["sql"]:
            self._setup_sql_rules()
        elif self.language in ["batch", "bat", "cmd"]:
            self._setup_batch_rules()
        elif self.language in ["shell", "sh", "bash", "zsh"]:
            self._setup_shell_rules()
        elif self.language in ["ini", "conf", "cfg"]:
            self._setup_ini_rules()
        elif self.language in ["yaml", "yml"]:
            self._setup_yaml_rules()
        elif self.language in ["markdown", "md"]:
            self._setup_markdown_rules()
        elif self.language in ["powershell", "ps1", "psm1"]:
            self._setup_powershell_rules()
        elif self.language in ["properties", "env"]:
            self._setup_properties_rules()

    def _setup_python_rules(self):
        """Python语法规则"""
        # 关键字
        keywords = [
            "and", "as", "assert", "async", "await", "break", "class", "continue",
            "def", "del", "elif", "else", "except", "finally", "for", "from",
            "global", "if", "import", "in", "is", "lambda", "nonlocal", "not",
            "or", "pass", "raise", "return", "try", "while", "with", "yield",
            "True", "False", "None"
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, self.keyword_format))

        # 装饰器
        pattern = QRegularExpression(r"@\w+")
        self.highlighting_rules.append((pattern, self.decorator_format))

        # 类名
        pattern = QRegularExpression(r"\bclass\s+(\w+)")
        self.highlighting_rules.append((pattern, self.class_format))

        # 函数
        pattern = QRegularExpression(r"\bdef\s+(\w+)")
        self.highlighting_rules.append((pattern, self.function_format))

        # 数字
        pattern = QRegularExpression(r"\b[0-9]+\.?[0-9]*\b")
        self.highlighting_rules.append((pattern, self.number_format))

        # 字符串 (单引号)
        pattern = QRegularExpression(r"'[^']*'")
        self.highlighting_rules.append((pattern, self.string_format))

        # 字符串 (双引号)
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, self.string_format))

        # 多行字符串
        pattern = QRegularExpression(r'""".*?"""', QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, self.string_format))

        pattern = QRegularExpression(r"'''.*?'''", QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, self.string_format))

        # 注释
        pattern = QRegularExpression(r"#.*$")
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_javascript_rules(self):
        """JavaScript/TypeScript语法规则"""
        keywords = [
            "break", "case", "catch", "class", "const", "continue", "debugger",
            "default", "delete", "do", "else", "export", "extends", "finally",
            "for", "function", "if", "import", "in", "instanceof", "let", "new",
            "return", "super", "switch", "this", "throw", "try", "typeof", "var",
            "void", "while", "with", "yield", "async", "await", "of",
            "true", "false", "null", "undefined", "NaN", "Infinity"
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, self.keyword_format))

        # 类型 (TypeScript)
        types = ["string", "number", "boolean", "any", "void", "never", "unknown", "object"]
        for t in types:
            pattern = QRegularExpression(f"\\b{t}\\b")
            self.highlighting_rules.append((pattern, self.class_format))

        # 函数
        pattern = QRegularExpression(r"\bfunction\s+(\w+)")
        self.highlighting_rules.append((pattern, self.function_format))

        # 数字
        pattern = QRegularExpression(r"\b[0-9]+\.?[0-9]*\b")
        self.highlighting_rules.append((pattern, self.number_format))

        # 字符串
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, self.string_format))

        pattern = QRegularExpression(r"'[^']*'")
        self.highlighting_rules.append((pattern, self.string_format))

        pattern = QRegularExpression(r"`[^`]*`")
        self.highlighting_rules.append((pattern, self.string_format))

        # 单行注释
        pattern = QRegularExpression(r"//.*$")
        self.highlighting_rules.append((pattern, self.comment_format))

        # 多行注释
        pattern = QRegularExpression(r"/\*.*?\*/", QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_cpp_rules(self):
        """C/C++语法规则"""
        keywords = [
            "auto", "break", "case", "char", "const", "continue", "default", "do",
            "double", "else", "enum", "extern", "float", "for", "goto", "if",
            "int", "long", "register", "return", "short", "signed", "sizeof", "static",
            "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while",
            "class", "public", "private", "protected", "virtual", "override", "new", "delete",
            "try", "catch", "throw", "namespace", "using", "template", "typename",
            "true", "false", "nullptr", "bool"
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, self.keyword_format))

        # 预处理器
        pattern = QRegularExpression(r"#\w+")
        self.highlighting_rules.append((pattern, self.decorator_format))

        # 数字
        pattern = QRegularExpression(r"\b[0-9]+\.?[0-9]*[fFlL]?\b")
        self.highlighting_rules.append((pattern, self.number_format))

        # 字符串
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, self.string_format))

        # 字符
        pattern = QRegularExpression(r"'.'")
        self.highlighting_rules.append((pattern, self.string_format))

        # 单行注释
        pattern = QRegularExpression(r"//.*$")
        self.highlighting_rules.append((pattern, self.comment_format))

        # 多行注释
        pattern = QRegularExpression(r"/\*.*?\*/", QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_java_rules(self):
        """Java语法规则"""
        keywords = [
            "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char",
            "class", "const", "continue", "default", "do", "double", "else", "enum",
            "extends", "final", "finally", "float", "for", "goto", "if", "implements",
            "import", "instanceof", "int", "interface", "long", "native", "new", "package",
            "private", "protected", "public", "return", "short", "static", "strictfp", "super",
            "switch", "synchronized", "this", "throw", "throws", "transient", "try", "void",
            "volatile", "while", "true", "false", "null"
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, self.keyword_format))

        # 注解
        pattern = QRegularExpression(r"@\w+")
        self.highlighting_rules.append((pattern, self.decorator_format))

        # 数字
        pattern = QRegularExpression(r"\b[0-9]+\.?[0-9]*[fFdDlL]?\b")
        self.highlighting_rules.append((pattern, self.number_format))

        # 字符串
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, self.string_format))

        # 单行注释
        pattern = QRegularExpression(r"//.*$")
        self.highlighting_rules.append((pattern, self.comment_format))

        # 多行注释
        pattern = QRegularExpression(r"/\*.*?\*/", QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_html_rules(self):
        """HTML/XML语法规则"""
        # 标签名
        pattern = QRegularExpression(r"</?(\w+)")
        self.highlighting_rules.append((pattern, self.keyword_format))

        # 属性名
        pattern = QRegularExpression(r'\s(\w+)=')
        self.highlighting_rules.append((pattern, self.class_format))

        # 属性值
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, self.string_format))

        pattern = QRegularExpression(r"'[^']*'")
        self.highlighting_rules.append((pattern, self.string_format))

        # 注释
        pattern = QRegularExpression(r"<!--.*?-->", QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_css_rules(self):
        """CSS语法规则"""
        # 选择器
        pattern = QRegularExpression(r"[\.\#]?\w+(?=\s*\{)")
        self.highlighting_rules.append((pattern, self.keyword_format))

        # 属性名
        pattern = QRegularExpression(r"[\w-]+(?=\s*:)")
        self.highlighting_rules.append((pattern, self.class_format))

        # 属性值
        pattern = QRegularExpression(r":\s*([^;]+)")
        self.highlighting_rules.append((pattern, self.string_format))

        # 数字
        pattern = QRegularExpression(r"\b[0-9]+\.?[0-9]*(px|em|rem|%|vh|vw)?\b")
        self.highlighting_rules.append((pattern, self.number_format))

        # 注释
        pattern = QRegularExpression(r"/\*.*?\*/", QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_json_rules(self):
        """JSON语法规则"""
        # 键名
        pattern = QRegularExpression(r'"[^"]*"\s*:')
        self.highlighting_rules.append((pattern, self.keyword_format))

        # 字符串值
        pattern = QRegularExpression(r':\s*"[^"]*"')
        self.highlighting_rules.append((pattern, self.string_format))

        # 数字
        pattern = QRegularExpression(r"\b-?[0-9]+\.?[0-9]*\b")
        self.highlighting_rules.append((pattern, self.number_format))

        # 布尔和null
        pattern = QRegularExpression(r"\b(true|false|null)\b")
        self.highlighting_rules.append((pattern, self.class_format))

    def _setup_sql_rules(self):
        """SQL语法规则"""
        keywords = [
            "SELECT", "FROM", "WHERE", "AND", "OR", "NOT", "IN", "IS", "NULL",
            "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE", "CREATE",
            "TABLE", "DROP", "ALTER", "INDEX", "VIEW", "JOIN", "LEFT", "RIGHT",
            "INNER", "OUTER", "ON", "AS", "ORDER", "BY", "GROUP", "HAVING",
            "DISTINCT", "LIMIT", "OFFSET", "UNION", "ALL", "EXISTS", "BETWEEN",
            "LIKE", "ASC", "DESC", "PRIMARY", "KEY", "FOREIGN", "REFERENCES"
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b", QRegularExpression.PatternOption.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, self.keyword_format))

        # 数字
        pattern = QRegularExpression(r"\b[0-9]+\.?[0-9]*\b")
        self.highlighting_rules.append((pattern, self.number_format))

        # 字符串
        pattern = QRegularExpression(r"'[^']*'")
        self.highlighting_rules.append((pattern, self.string_format))

        # 单行注释
        pattern = QRegularExpression(r"--.*$")
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_batch_rules(self):
        """批处理文件(.bat/.cmd)语法规则"""
        keywords = [
            "echo", "set", "if", "else", "for", "goto", "call", "exit",
            "rem", "pause", "cls", "cd", "dir", "copy", "move", "del",
            "mkdir", "rmdir", "type", "find", "findstr", "sort", "more",
            "start", "tasklist", "taskkill", "net", "ping", "ipconfig",
            "setlocal", "endlocal", "enabledelayedexpansion", "errorlevel",
            "exist", "defined", "not", "equ", "neq", "lss", "leq", "gtr", "geq",
            "nul", "con", "prn", "aux", "off", "on"
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b", QRegularExpression.PatternOption.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, self.keyword_format))

        # 变量 %var% 或 !var!
        pattern = QRegularExpression(r"%[^%\s]+%")
        self.highlighting_rules.append((pattern, self.class_format))
        pattern = QRegularExpression(r"![^!\s]+!")
        self.highlighting_rules.append((pattern, self.class_format))

        # 参数 %0-%9, %*
        pattern = QRegularExpression(r"%[0-9*~]")
        self.highlighting_rules.append((pattern, self.number_format))

        # 标签 :label
        pattern = QRegularExpression(r"^:\w+", QRegularExpression.PatternOption.MultilineOption)
        self.highlighting_rules.append((pattern, self.decorator_format))

        # 字符串
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, self.string_format))

        # 注释 REM 或 ::
        pattern = QRegularExpression(r"(?:^|\s)(?:REM|rem|::).*$", QRegularExpression.PatternOption.MultilineOption)
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_shell_rules(self):
        """Shell脚本(.sh/.bash)语法规则"""
        keywords = [
            "if", "then", "else", "elif", "fi", "case", "esac", "for", "while",
            "do", "done", "in", "function", "return", "exit", "break", "continue",
            "export", "local", "readonly", "declare", "typeset", "unset",
            "source", "alias", "unalias", "eval", "exec", "trap", "shift",
            "echo", "printf", "read", "cd", "pwd", "ls", "cat", "grep", "sed",
            "awk", "find", "xargs", "sort", "uniq", "wc", "head", "tail",
            "mkdir", "rmdir", "rm", "cp", "mv", "chmod", "chown", "ln",
            "true", "false", "test"
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, self.keyword_format))

        # 变量 $var 或 ${var}
        pattern = QRegularExpression(r"\$\{?[a-zA-Z_][a-zA-Z0-9_]*\}?")
        self.highlighting_rules.append((pattern, self.class_format))

        # 特殊变量 $0-$9, $@, $*, $#, $$, $?, $!
        pattern = QRegularExpression(r"\$[0-9@*#$?!]")
        self.highlighting_rules.append((pattern, self.number_format))

        # 函数定义
        pattern = QRegularExpression(r"\bfunction\s+(\w+)")
        self.highlighting_rules.append((pattern, self.function_format))

        # 字符串
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, self.string_format))
        pattern = QRegularExpression(r"'[^']*'")
        self.highlighting_rules.append((pattern, self.string_format))

        # 注释
        pattern = QRegularExpression(r"#.*$")
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_ini_rules(self):
        """INI/配置文件语法规则"""
        # 节 [section]
        pattern = QRegularExpression(r"^\[.+\]$", QRegularExpression.PatternOption.MultilineOption)
        self.highlighting_rules.append((pattern, self.keyword_format))

        # 键名
        pattern = QRegularExpression(r"^[^=\[\]#;]+(?==)")
        self.highlighting_rules.append((pattern, self.class_format))

        # 值
        pattern = QRegularExpression(r"=(.*)$")
        self.highlighting_rules.append((pattern, self.string_format))

        # 注释
        pattern = QRegularExpression(r"[#;].*$")
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_yaml_rules(self):
        """YAML语法规则"""
        # 键名
        pattern = QRegularExpression(r"^[\s]*[a-zA-Z_][a-zA-Z0-9_]*(?=\s*:)")
        self.highlighting_rules.append((pattern, self.keyword_format))

        # 布尔和null
        pattern = QRegularExpression(r"\b(true|false|yes|no|on|off|null|~)\b", QRegularExpression.PatternOption.CaseInsensitiveOption)
        self.highlighting_rules.append((pattern, self.class_format))

        # 数字
        pattern = QRegularExpression(r"\b-?[0-9]+\.?[0-9]*\b")
        self.highlighting_rules.append((pattern, self.number_format))

        # 字符串
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, self.string_format))
        pattern = QRegularExpression(r"'[^']*'")
        self.highlighting_rules.append((pattern, self.string_format))

        # 锚点和别名
        pattern = QRegularExpression(r"[&*][a-zA-Z_][a-zA-Z0-9_]*")
        self.highlighting_rules.append((pattern, self.decorator_format))

        # 注释
        pattern = QRegularExpression(r"#.*$")
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_markdown_rules(self):
        """Markdown语法规则"""
        # 标题 # ## ### 等
        pattern = QRegularExpression(r"^#{1,6}\s.*$", QRegularExpression.PatternOption.MultilineOption)
        self.highlighting_rules.append((pattern, self.keyword_format))

        # 粗体 **text** 或 __text__
        pattern = QRegularExpression(r"\*\*[^*]+\*\*")
        self.highlighting_rules.append((pattern, self.class_format))
        pattern = QRegularExpression(r"__[^_]+__")
        self.highlighting_rules.append((pattern, self.class_format))

        # 斜体 *text* 或 _text_
        pattern = QRegularExpression(r"\*[^*]+\*")
        self.highlighting_rules.append((pattern, self.decorator_format))
        pattern = QRegularExpression(r"_[^_]+_")
        self.highlighting_rules.append((pattern, self.decorator_format))

        # 代码块 `code`
        pattern = QRegularExpression(r"`[^`]+`")
        self.highlighting_rules.append((pattern, self.string_format))

        # 链接 [text](url)
        pattern = QRegularExpression(r"\[([^\]]+)\]\([^\)]+\)")
        self.highlighting_rules.append((pattern, self.function_format))

        # 列表项 - * +
        pattern = QRegularExpression(r"^[\s]*[-*+]\s", QRegularExpression.PatternOption.MultilineOption)
        self.highlighting_rules.append((pattern, self.number_format))

    def _setup_powershell_rules(self):
        """PowerShell语法规则"""
        keywords = [
            "if", "else", "elseif", "switch", "for", "foreach", "while", "do",
            "until", "break", "continue", "return", "exit", "throw", "try",
            "catch", "finally", "trap", "function", "filter", "param", "begin",
            "process", "end", "class", "enum", "using", "workflow", "parallel",
            "sequence", "inlinescript"
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b", QRegularExpression.PatternOption.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, self.keyword_format))

        # Cmdlet风格的命令 Verb-Noun
        pattern = QRegularExpression(r"\b[A-Z][a-z]+-[A-Z][a-zA-Z]+\b")
        self.highlighting_rules.append((pattern, self.function_format))

        # 变量 $var
        pattern = QRegularExpression(r"\$[a-zA-Z_][a-zA-Z0-9_]*")
        self.highlighting_rules.append((pattern, self.class_format))

        # 自动变量
        pattern = QRegularExpression(r"\$(?:_|true|false|null|args|input|host|home|pid|pwd|error)")
        self.highlighting_rules.append((pattern, self.number_format))

        # 字符串
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, self.string_format))
        pattern = QRegularExpression(r"'[^']*'")
        self.highlighting_rules.append((pattern, self.string_format))

        # 注释
        pattern = QRegularExpression(r"#.*$")
        self.highlighting_rules.append((pattern, self.comment_format))

    def _setup_properties_rules(self):
        """Properties文件语法规则 (.properties, .env)"""
        # 键名
        pattern = QRegularExpression(r"^[^=#\s][^=]*(?==)")
        self.highlighting_rules.append((pattern, self.keyword_format))

        # 值
        pattern = QRegularExpression(r"=(.*)$")
        self.highlighting_rules.append((pattern, self.string_format))

        # 注释
        pattern = QRegularExpression(r"[#!].*$")
        self.highlighting_rules.append((pattern, self.comment_format))

    def highlightBlock(self, text: str):
        """高亮文本块"""
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


def get_language_from_filename(filename: str) -> str:
    """根据文件名获取语言"""
    ext_map = {
        # Python
        ".py": "python",
        ".pyw": "python",
        ".pyx": "python",
        ".pxd": "python",
        # JavaScript/TypeScript
        ".js": "javascript",
        ".jsx": "javascript",
        ".mjs": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        # C/C++
        ".c": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".hxx": "cpp",
        # Java
        ".java": "java",
        # Web
        ".html": "html",
        ".htm": "html",
        ".xml": "xml",
        ".xhtml": "html",
        ".svg": "xml",
        ".css": "css",
        ".scss": "css",
        ".less": "css",
        # Data
        ".json": "json",
        ".sql": "sql",
        # 批处理/脚本
        ".bat": "batch",
        ".cmd": "batch",
        ".sh": "shell",
        ".bash": "shell",
        ".zsh": "shell",
        ".fish": "shell",
        # PowerShell
        ".ps1": "powershell",
        ".psm1": "powershell",
        ".psd1": "powershell",
        # 配置文件
        ".ini": "ini",
        ".conf": "ini",
        ".cfg": "ini",
        ".config": "ini",
        ".inf": "ini",
        ".reg": "ini",
        # YAML
        ".yaml": "yaml",
        ".yml": "yaml",
        # Markdown
        ".md": "markdown",
        ".markdown": "markdown",
        ".mdown": "markdown",
        # Properties
        ".properties": "properties",
        ".env": "properties",
        # 其他常见格式
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".pl": "perl",
        ".pm": "perl",
        ".lua": "lua",
        ".r": "r",
        ".R": "r",
        ".swift": "swift",
        ".kt": "kotlin",
        ".kts": "kotlin",
        ".gradle": "gradle",
        ".groovy": "groovy",
        ".scala": "scala",
        ".clj": "clojure",
        ".cs": "csharp",
        ".vb": "vb",
        ".fs": "fsharp",
        ".dart": "dart",
        ".vue": "vue",
        ".svelte": "svelte",
        # 文本文件
        ".txt": "text",
        ".log": "text",
        ".csv": "text",
        ".tsv": "text",
    }
    _, ext = os.path.splitext(filename.lower())
    return ext_map.get(ext, "")
