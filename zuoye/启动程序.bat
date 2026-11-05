@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   智能数据分析智能体 - 启动中...
echo   浏览器将自动打开 http://localhost:8501
echo   停止服务：在本窗口按 Ctrl+C
echo ============================================
python -m streamlit run app.py
pause
