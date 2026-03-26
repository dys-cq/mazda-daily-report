param([string]$AccessToken,[string]$ThumbMediaId)

# Read markdown
$md=Get-Content "C:\Users\Administrator\.openclaw\workspace\mazda-skyactiv-article.md" -Raw -Encoding UTF8

# Simple HTML conversion
$html=$md
$html=$html -replace '^# (.*?)$','<h1 style="text-align:center;font-size:20px;font-weight:bold;margin:30px 0 20px 0;color:#333;">$1</h1>'
$html=$html -replace '^## (.*?)$','<h2 style="font-size:17px;font-weight:bold;margin:25px 0 15px 0;color:#07c160;border-left:4px solid #07c160;padding-left:12px;">$1</h2>'
$html=$html -replace '^### (.*?)$','<h3 style="font-size:16px;font-weight:bold;margin:20px 0 12px 0;color:#444;">$1</h3>'
$html=$html -replace '\*\*(.*?)\*\*','<strong>$1</strong>'
$html=$html -replace '\n---\n','<hr style="border:none;border-top:1px solid #e0e0e0;margin:25px 0;" />'
$html=$html -replace '\r\n\r\n','</p><p style="margin:15px 0;line-height:1.8;font-size:15px;color:#333;">'
$html=$html -replace '\n\n','</p><p style="margin:15px 0;line-height:1.8;font-size:15px;color:#333;">'
$html="<section>$html</section>"
$html=$html -replace '`',''

# Escape quotes and backslashes for JSON
$html=$html -replace '\\','\\\\'
$html=$html -replace '"','\"'

# Build JSON
$json=@"
{
  "articles": [
    {
      "title": "14:1 magic Mazda",
      "author": "Nice",
      "digest": "Mazda Skyactiv technology",
      "content": "$html",
      "thumb_media_id": "$ThumbMediaId",
      "need_open_comment": 1,
      "only_fans_can_comment": 0
    }
  ]
}
"@

$url="https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$AccessToken"
Write-Host "Publishing..."
$response=Invoke-RestMethod -Uri $url -Method Post -Body $json -ContentType "application/json; charset=utf-8"
Write-Output "Result: $($response|ConvertTo-Json)"
