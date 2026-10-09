# PyCompare - 文件比较工具

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

一个强大的文件与文件夹比较工具，类似 Beyond Compare 和 WinMerge

[English](README_EN.md) | 简体中文

</div>

## ✨ 特性

- 🔍 **文件比较**
  - 支持文本文件的逐行比较
  - 智能字符级差异高亮显示
  - 多种编码格式自动检测（UTF-8, GBK, GB2312 等）
  - 语法高亮支持（基于 Pygments）
  - 并排双窗格显示，差异同步滚动

- 📁 **文件夹比较**
  - 递归比较整个文件夹结构
  - 快速文件哈希比较
  - 显示文件大小、修改时间等元数据
  - 树形结构展示差异文件
  - 支持只显示差异文件过滤

- 🎨 **用户界面**
  - 现代化深色主题（类似 VS Code）
  - 多标签页支持，可同时比较多组文件
  - 直观的工具栏和快捷键
  - 自适应高 DPI 显示

- ⚡ **性能优化**
  - 高效的差异算法（基于 difflib）
  - 大文件处理优化
  - 快速文件哈希计算

## 📸 截图

*（建议在此处添加应用截图）*

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Windows / Linux / macOS

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

#### 方式一：直接运行（开发模式）

```bash
python main.py
```

#### 方式二：使用启动脚本（Windows）

```bash
run.bat
```

#### 方式三：命令行参数快速比较

```bash
# 比较两个文件
python main.py file1.txt file2.txt

# 比较两个文件夹
python main.py folder1/ folder2/
```

## 📦 打包为可执行文件

使用 PyInstaller 将应用打包为独立的可执行文件：

### Windows

```bash
build.bat
```

或手动执行：

```bash
pyinstaller --noconfirm --onefile --windowed --name "PyCompare" --icon=NONE main.py
```

生成的可执行文件位于 `dist/PyCompare.exe`

### Linux / macOS

```bash
pyinstaller --noconfirm --onefile --windowed --name "PyCompare" main.py
```

## 🛠️ 项目结构

```
compare_tool/
├── main.py                 # 应用入口
├── requirements.txt        # 项目依赖
├── build.bat              # Windows 打包脚本
├── run.bat                # Windows 运行脚本
├── install_and_run.bat    # Windows 一键安装运行脚本
├── src/                   # 源代码目录
│   ├── __init__.py
│   ├── core/              # 核心功能模块
│   │   ├── __init__.py
│   │   └── diff_engine.py # 差异比较引擎
│   ├── ui/                # 用户界面模块
│   │   ├── __init__.py
│   │   ├── main_window.py      # 主窗口
│   │   ├── diff_view.py        # 文件比较视图
│   │   ├── folder_view.py      # 文件夹比较视图
│   │   └── syntax_highlighter.py # 语法高亮
│   └── utils/             # 工具模块
│       └── __init__.py
├── resources/             # 资源文件
│   ├── icons/            # 图标
│   └── themes/           # 主题
└── README.md             # 项目文档
```

## 🎯 使用方法

### 文件比较

1. 点击工具栏的 **"比较文件"** 按钮或使用菜单 `文件 -> 新建文件比较`
2. 在左右两侧分别选择要比较的文件
3. 查看高亮显示的差异
   - 🟢 绿色：新增内容
   - 🔴 红色：删除内容
   - 🟡 黄色：修改内容

### 文件夹比较

1. 点击工具栏的 **"比较文件夹"** 按钮或使用菜单 `文件 -> 新建文件夹比较`
2. 选择要比较的两个文件夹
3. 查看树形结构中的差异文件
   - 双击文件可以打开详细比较
4. 使用过滤器仅显示有差异的文件

### 快捷键

- `Ctrl+N` - 新建文件比较
- `Ctrl+Shift+N` - 新建文件夹比较
- `Ctrl+W` - 关闭当前标签页
- `Ctrl+Q` - 退出应用
- `F5` - 刷新比较
- `Ctrl+F` - 查找（计划中）

## 🔧 技术栈

- **GUI 框架**: PySide6 (Qt for Python)
- **差异算法**: difflib (Python 标准库)
- **语法高亮**: Pygments
- **编码检测**: chardet
- **打包工具**: PyInstaller

## 📝 开发说明

### 添加新功能

1. 核心功能添加到 `src/core/`
2. UI 组件添加到 `src/ui/`
3. 工具函数添加到 `src/utils/`

### 代码规范

- 遵循 PEP 8 编码规范
- 使用类型注解（Type Hints）
- 编写文档字符串（Docstrings）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 灵感来源于 [Beyond Compare](https://www.scootersoftware.com/) 和 [WinMerge](https://winmerge.org/)
- UI 设计参考了 Visual Studio Code 的深色主题

## ☕ 支持 PyCompare

PyCompare 免费使用。如果它帮你省了时间，可以请开发者喝杯咖啡：国内用微信或支付宝，海外用 PayPal。谢谢！

<p align="center">
  <img src="docs/donate/wechat.png" height="240" alt="微信支付收款码">
  <img src="docs/donate/alipay.png" height="240" alt="支付宝收款码">
  <img src="docs/donate/paypal.png" height="240" alt="PayPal 收款码">
</p>

## 📮 联系方式

如有问题或建议，请提交 [Issue](../../issues)
