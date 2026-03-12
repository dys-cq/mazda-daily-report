Param(
  [string]$BaseDir = "daily-results",
  [string]$Date = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Date)) {
  $Date = Get-Date -Format "yyyy-MM-dd"
}

$dayDir = Join-Path $BaseDir $Date
$logDir = Join-Path $dayDir "logs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$runLog = Join-Path $logDir "pipeline-run.log"

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] nightly wrapper start" | Out-File -FilePath $runLog -Encoding utf8 -Append
uv run python automation/nightly_content_pipeline.py --date $Date --base-dir $BaseDir --max-articles 4
$exitCode = $LASTEXITCODE
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] nightly wrapper end, code=$exitCode" | Out-File -FilePath $runLog -Encoding utf8 -Append

exit $exitCode
