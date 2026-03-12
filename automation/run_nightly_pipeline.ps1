Param(
  [string]$BaseDir = "daily-results"
)

$ErrorActionPreference = "Stop"

$today = Get-Date -Format "yyyy-MM-dd"
$dayDir = Join-Path $BaseDir $today
$dirs = @("original", "rewrite", "skills", "reports", "logs")

New-Item -ItemType Directory -Path $dayDir -Force | Out-Null
foreach ($d in $dirs) {
  New-Item -ItemType Directory -Path (Join-Path $dayDir $d) -Force | Out-Null
}

$startLog = Join-Path $dayDir "logs/run-start.log"
$endLog = Join-Path $dayDir "logs/run-end.log"
$summary = Join-Path $dayDir "reports/daily-summary.md"

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] run start" | Out-File -FilePath $startLog -Encoding utf8 -Append

if (-not (Test-Path $summary)) {
  $lines = @(
    "# Daily Summary ($today)",
    "",
    "- Status: scaffold initialized.",
    "- Note: nightly collection/rewrite/skill steps pending integration."
  )
  $lines -join "`r`n" | Out-File -FilePath $summary -Encoding utf8
}

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] run end" | Out-File -FilePath $endLog -Encoding utf8 -Append
Write-Output "Nightly scaffold ready: $dayDir"
