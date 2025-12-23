# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-22

### Added
- Initial release of PyCompare
- File comparison with line-by-line diff
- Character-level diff highlighting within lines
- Folder comparison with recursive directory scanning
- Multi-tab interface for comparing multiple file/folder pairs
- Dark theme UI inspired by VS Code
- Syntax highlighting support for various programming languages
- Automatic encoding detection (UTF-8, GBK, GB2312, etc.)
- Side-by-side synchronized scrolling
- File hash-based comparison for folders
- Metadata display (file size, modification time)
- Filter to show only different files in folder view
- Command-line argument support for quick comparison
- Windows batch scripts for easy setup and execution
- PyInstaller build script for creating standalone executable

### Features
- **File Comparison**
  - Line-by-line text comparison
  - Character-level diff within modified lines
  - Color-coded diff display (green for additions, red for deletions, yellow for modifications)
  - Syntax highlighting for code files
  - Multiple encoding support

- **Folder Comparison**
  - Recursive folder structure comparison
  - Fast hash-based file comparison
  - Tree view for directory structure
  - Double-click to open file comparison
  - Filter options

- **User Interface**
  - Modern dark theme
  - Multi-tab support
  - Intuitive toolbar
  - Keyboard shortcuts
  - High DPI support
  - Welcome screen

- **Performance**
  - Efficient diff algorithm
  - Optimized for large files
  - Fast file hashing

### Technical Details
- Built with PySide6 (Qt for Python)
- Uses Python difflib for comparison algorithm
- Pygments for syntax highlighting
- chardet for encoding detection
- Cross-platform support (Windows, Linux, macOS)

## [Unreleased]

### Planned Features
- Search and find within compared files
- Line number navigation
- Copy/paste functionality between panes
- Merge functionality
- 3-way comparison
- Git integration
- Configuration settings
- More theme options
- Plugin system
- Performance improvements for very large files
- Binary file comparison
- Image comparison

---

## Version History

- **1.0.0** (2024-12-22) - Initial public release
