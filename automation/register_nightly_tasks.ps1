$ErrorActionPreference = "Stop"

$workspace = "C:\Users\Administrator\.openclaw\workspace"
$nightlyScript = Join-Path $workspace "automation\run_nightly_pipeline.ps1"
$morningScript = Join-Path $workspace "automation\run_morning_acceptance.ps1"

$nightlyAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$nightlyScript`""
$nightlyTrigger = New-ScheduledTaskTrigger -Daily -At 00:00
$nightlyPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$nightlySettings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask -TaskName "OpenClaw-Nightly-Pipeline" -Action $nightlyAction -Trigger $nightlyTrigger -Principal $nightlyPrincipal -Settings $nightlySettings -Force | Out-Null

$morningAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$morningScript`""
$morningTrigger = New-ScheduledTaskTrigger -Daily -At 08:05
$morningPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$morningSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask -TaskName "OpenClaw-Morning-Acceptance" -Action $morningAction -Trigger $morningTrigger -Principal $morningPrincipal -Settings $morningSettings -Force | Out-Null

Write-Output "Registered tasks: OpenClaw-Nightly-Pipeline, OpenClaw-Morning-Acceptance"
