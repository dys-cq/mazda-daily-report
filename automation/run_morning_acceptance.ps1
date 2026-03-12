Param(
  [string]$BaseDir = "daily-results",
  [string]$Date = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Date)) {
  $Date = Get-Date -Format "yyyy-MM-dd"
}

$logDir = Join-Path (Join-Path $BaseDir $Date) "logs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$morningLog = Join-Path $logDir "morning-check.log"

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] morning acceptance start" | Out-File -FilePath $morningLog -Encoding utf8 -Append
uv run python automation/check_nightly_outputs.py --date $Date --strict
$exitCode = $LASTEXITCODE
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] morning acceptance end, code=$exitCode" | Out-File -FilePath $morningLog -Encoding utf8 -Append

exit $exitCode
