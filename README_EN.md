# PyCompare - File Comparison Tool

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

A powerful file and folder comparison tool, similar to Beyond Compare and WinMerge

English | [简体中文](README.md)

</div>

## ✨ Features

- 🔍 **File Comparison**
  - Line-by-line text file comparison
  - Intelligent character-level diff highlighting
  - Automatic encoding detection (UTF-8, GBK, GB2312, etc.)
  - Syntax highlighting support (powered by Pygments)
  - Side-by-side dual-pane view with synchronized scrolling

- 📁 **Folder Comparison**
  - Recursive folder structure comparison
  - Fast file hash-based comparison
  - Display file size, modification time, and other metadata
  - Tree structure view for diff files
  - Filter to show only different files

- 🎨 **User Interface**
  - Modern dark theme (VS Code-like)
  - Multi-tab support for comparing multiple file pairs
  - Intuitive toolbar and keyboard shortcuts
  - High DPI display support

- ⚡ **Performance**
  - Efficient diff algorithm (based on difflib)
  - Optimized for large files
  - Fast file hash calculation

## 📸 Screenshots

*(Add application screenshots here)*

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- Windows / Linux / macOS

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

#### Method 1: Direct Run (Development Mode)

```bash
python main.py
```

#### Method 2: Using Launcher Script (Windows)

```bash
run.bat
```

#### Method 3: Quick Compare via Command Line

```bash
# Compare two files
python main.py file1.txt file2.txt

# Compare two folders
python main.py folder1/ folder2/
```

## 📦 Build Executable

Package the application as a standalone executable using PyInstaller:

### Windows

```bash
build.bat
```

Or manually:

```bash
pyinstaller --noconfirm --onefile --windowed --name "PyCompare" --icon=NONE main.py
```

The executable will be located at `dist/PyCompare.exe`

### Linux / macOS

```bash
pyinstaller --noconfirm --onefile --windowed --name "PyCompare" main.py
```

## 🛠️ Project Structure

```
compare_tool/
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
├── build.bat              # Windows build script
├── run.bat                # Windows run script
├── install_and_run.bat    # Windows one-click install & run
├── src/                   # Source code directory
│   ├── __init__.py
│   ├── core/              # Core functionality modules
│   │   ├── __init__.py
│   │   └── diff_engine.py # Diff comparison engine
│   ├── ui/                # User interface modules
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main window
│   │   ├── diff_view.py        # File comparison view
│   │   ├── folder_view.py      # Folder comparison view
│   │   └── syntax_highlighter.py # Syntax highlighting
│   └── utils/             # Utility modules
│       └── __init__.py
├── resources/             # Resource files
│   ├── icons/            # Icons
│   └── themes/           # Themes
└── README.md             # Project documentation
```

## 🎯 Usage

### File Comparison

1. Click the **"Compare Files"** button on the toolbar or use menu `File -> New File Comparison`
2. Select files to compare on the left and right sides
3. View highlighted differences
   - 🟢 Green: Added content
   - 🔴 Red: Deleted content
   - 🟡 Yellow: Modified content

### Folder Comparison

1. Click the **"Compare Folders"** button on the toolbar or use menu `File -> New Folder Comparison`
2. Select two folders to compare
3. View diff files in the tree structure
   - Double-click a file to open detailed comparison
4. Use filters to show only different files

### Keyboard Shortcuts

- `Ctrl+N` - New file comparison
- `Ctrl+Shift+N` - New folder comparison
- `Ctrl+W` - Close current tab
- `Ctrl+Q` - Quit application
- `F5` - Refresh comparison
- `Ctrl+F` - Find (planned)

## 🔧 Tech Stack

- **GUI Framework**: PySide6 (Qt for Python)
- **Diff Algorithm**: difflib (Python standard library)
- **Syntax Highlighting**: Pygments
- **Encoding Detection**: chardet
- **Packaging Tool**: PyInstaller

## 📝 Development

### Adding New Features

1. Add core functionality to `src/core/`
2. Add UI components to `src/ui/`
3. Add utility functions to `src/utils/`

### Code Style

- Follow PEP 8 coding standards
- Use type hints
- Write docstrings

## 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Inspired by [Beyond Compare](https://www.scootersoftware.com/) and [WinMerge](https://winmerge.org/)
- UI design inspired by Visual Studio Code's dark theme

## ☕ Support PyCompare

PyCompare is free. If it saved you some time, you can buy the developer a coffee — WeChat Pay or Alipay in China, PayPal anywhere. Thank you!

<p align="center">
  <img src="docs/donate/wechat.png" height="240" alt="WeChat Pay QR code">
  <img src="docs/donate/alipay.png" height="240" alt="Alipay QR code">
  <img src="docs/donate/paypal.png" height="240" alt="PayPal QR code">
</p>

## 📮 Contact

For questions or suggestions, please submit an [Issue](../../issues)
