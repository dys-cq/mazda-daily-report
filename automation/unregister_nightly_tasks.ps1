$ErrorActionPreference = "SilentlyContinue"
Unregister-ScheduledTask -TaskName "OpenClaw-Nightly-Pipeline" -Confirm:$false
Unregister-ScheduledTask -TaskName "OpenClaw-Morning-Acceptance" -Confirm:$false
Write-Output "Unregistered tasks (if existed)."
