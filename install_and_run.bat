@echo off
chcp 65001 >nul
echo ========================================
echo   PyCompare 文件比较工具 - 安装与启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/2] 正在安装依赖...
pip install PySide6 chardet Pygments -q

if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo [2/2] 依赖安装完成!
echo.
echo 正在启动 PyCompare...
echo.

cd /d "%~dp0"
python main.py

pause
