@echo off
chcp 65001 >nul
echo ========================================
echo   马自达 KPI 每日全维度分析报告生成器
echo ========================================
echo.

REM 设置数据目录（可修改）
set DAILY_DIR=E:\每日分析数据源
set WORKSPACE=C:\Users\Administrator\.openclaw\workspace

echo 数据目录：%DAILY_DIR%
echo 工作区目录：%WORKSPACE%
echo.

REM 执行报告生成脚本
uv run python "C:\Users\Administrator\.openclaw\skills\mazda-daily-report\scripts\generate_report.py" --daily-dir "%DAILY_DIR%" --workspace "%WORKSPACE%"

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo   报告生成完成！
    echo   输出位置：%DAILY_DIR%\[日期]-统计\
    echo   工作区镜像：%WORKSPACE%\
) else (
    echo   报告生成失败，请检查错误信息
)
echo ========================================
pause
