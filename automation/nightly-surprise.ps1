param(
  [string]$Workspace = "C:\Users\Administrator\.openclaw\workspace"
)

$ErrorActionPreference = "SilentlyContinue"
$now = Get-Date
$date = $now.ToString('yyyy-MM-dd')
$stamp = $now.ToString('yyyyMMdd-HHmmss')

$base = Join-Path $Workspace ("daily-results\" + $date)
$dirs = @("original","rewrite","skills","reports","logs")
foreach ($d in $dirs) {
  New-Item -ItemType Directory -Force -Path (Join-Path $base $d) | Out-Null
}

function Get-PlainTextFromUrl {
  param([string]$Url)
  try {
    $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 40
    $html = $resp.Content
    if (-not $html) { return $null }

    $title = [regex]::Match($html, '<title[^>]*>(.*?)</title>', 'IgnoreCase').Groups[1].Value
    $text = $html -replace '<script[\s\S]*?</script>',' '
    $text = $text -replace '<style[\s\S]*?</style>',' '
    $text = $text -replace '<[^>]+>',' '
    $text = $text -replace '&nbsp;',' '
    $text = $text -replace '&amp;','&'
    $text = $text -replace '&lt;','<'
    $text = $text -replace '&gt;','>'
    $text = ($text -replace '\s+',' ').Trim()
    if ($text.Length -gt 8000) { $text = $text.Substring(0,8000) }

    return [PSCustomObject]@{ Title = $title; Text = $text; Url = $Url }
  } catch {
    return $null
  }
}

$sources = @(
  "https://zapier.com/blog/what-you-should-automate/",
  "https://www.notion.com/help/guides/create-streamlined-project-management-workflow-using-database-automations",
  "https://www.notion.com/help/guides/share-social-media-posts-from-notion-with-webhook-actions"
)

$collected = @()
foreach ($u in $sources) {
  $it = Get-PlainTextFromUrl -Url $u
  if ($it -ne $null) { $collected += $it }
}

$idx = 1
foreach ($c in $collected) {
  $safe = ("article-$stamp-{0:d2}" -f $idx)
  $origPath = Join-Path $base ("original\$safe-original.md")
  $rwPath = Join-Path $base ("rewrite\$safe-wechat.md")

  $origLines = @(
    "# Source Article Archive",
    "",
    "- Title: $($c.Title)",
    "- URL: $($c.Url)",
    "- Time: $($now.ToString('yyyy-MM-dd HH:mm:ss'))",
    "",
    "## Extract",
    "",
    $c.Text
  )
  Set-Content -Path $origPath -Value ($origLines -join "`r`n") -Encoding UTF8

  $rwLines = @(
    "# Night Efficiency Upgrade",
    "",
    "Source: $($c.Url)",
    "",
    "## One-line takeaway",
    "Turn repeated actions into trigger-based workflows.",
    "",
    "## 3 quick steps",
    "1. Find actions repeated >=3 times per week",
    "2. Define trigger conditions",
    "3. Define exact outputs and owners",
    "",
    "## Expected impact",
    "- Fewer misses",
    "- Faster response",
    "- More deep-work time",
    "",
    "## Action checklist",
    "- [ ] Build lead-alert automation",
    "- [ ] Build status-change notification automation",
    "- [ ] Build approved-content publish automation",
    "",
    "---",
    "> Auto-generated night draft. Review and polish in the morning."
  )
  Set-Content -Path $rwPath -Value ($rwLines -join "`r`n") -Encoding UTF8

  $idx++
}

$skillPath = Join-Path $base ("skills\$stamp-new-skill-ideas.md")
$skillLines = @(
  "# New Skill Candidates (Auto)",
  "",
  "## 1) skill-nightly-skill-scout",
  "- Use case: scan high-value automation cases at night",
  "- Input: keywords, platforms, industry",
  "- Output: source archive + actionable checklist + workflow suggestions",
  "",
  "## 2) skill-wechat-explosive-rewriter",
  "- Use case: rewrite method articles into WeChat-style viral posts",
  "- Input: source markdown",
  "- Output: title options, hook intro, body, action list, CTA",
  "",
  "## 3) skill-ops-autopilot-lab",
  "- Use case: generate Trigger/Condition/Action blueprints for office workflows",
  "- Input: process description",
  "- Output: automation blueprint, field definitions, fallback rules"
)
Set-Content -Path $skillPath -Value ($skillLines -join "`r`n") -Encoding UTF8

$reportPath = Join-Path $base "reports\nightly-summary.md"
$reportLines = @(
  "# Night Run Summary",
  "",
  "- Run time: $($now.ToString('yyyy-MM-dd HH:mm:ss'))",
  "- Collected sources: $($collected.Count)",
  "- Outputs:",
  "  - original files: $($collected.Count)",
  "  - rewrite files: $($collected.Count)",
  "  - new skill ideas: 1",
  "",
  "## Next",
  "- Review rewrite drafts in the morning",
  "- Pick one skill idea for implementation"
)
Set-Content -Path $reportPath -Value ($reportLines -join "`r`n") -Encoding UTF8

$logPath = Join-Path $base "logs\nightly-run.log"
Add-Content -Path $logPath -Value "[$($now.ToString('yyyy-MM-dd HH:mm:ss'))] run ok, sources=$($collected.Count), stamp=$stamp"
