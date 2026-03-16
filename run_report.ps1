#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  马自达 KPI 每日全维度分析报告生成器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置数据目录（可修改）
$DAILY_DIR = "E:\每日分析数据源"
$WORKSPACE = "C:\Users\Administrator\.openclaw\workspace"

Write-Host "数据目录：$DAILY_DIR"
Write-Host "工作区目录：$WORKSPACE"
Write-Host ""

# 执行报告生成脚本
& uv run python "C:\Users\Administrator\.openclaw\skills\mazda-daily-report\scripts\generate_report.py" --daily-dir $DAILY_DIR --workspace $WORKSPACE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 报告生成完成！" -ForegroundColor Green
    Write-Host "  输出位置：$DAILY_DIR\[日期]-统计\" -ForegroundColor Gray
    Write-Host "  工作区镜像：$WORKSPACE\" -ForegroundColor Gray
} else {
    Write-Host "  ✗ 报告生成失败，请检查错误信息" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan
