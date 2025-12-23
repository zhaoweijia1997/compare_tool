@echo off
chcp 65001 >nul
echo ========================================
echo   PyCompare 打包脚本
echo ========================================
echo.

cd /d "%~dp0"

echo 正在打包...
pyinstaller --noconfirm --onefile --windowed --name "PyCompare" --icon=NONE main.py

echo.
echo 打包完成！
echo 可执行文件位置: dist\PyCompare.exe
echo.
pause
