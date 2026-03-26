param([string]$AccessToken,[string]$ThumbMediaId)

# Read markdown
$md=Get-Content "C:\Users\Administrator\.openclaw\workspace\mazda-skyactiv-article.md" -Raw -Encoding UTF8

# WeChat-style HTML conversion with grace theme
$html=$md

# Title
$html=$html -replace '^# (.*?)$','<section><section style="text-align:center;margin:30px 0 20px 0;"><h1 style="display:inline-block;padding:10px 25px;background:linear-gradient(135deg,#07c160,#06ad56);color:#fff;font-size:20px;font-weight:bold;border-radius:8px;box-shadow:0 4px 15px rgba(7,193,96,0.3);">$1</h1></section></section>'

# H2 with green border
$html=$html -replace '^## (.*?)$','<section><section style="margin:35px 0 15px 0;padding:12px 15px;background:#f8f8f8;border-left:5px solid #07c160;border-radius:4px;"><h2 style="margin:0;font-size:17px;font-weight:bold;color:#333;">$1</h2></section></section>'

# H3
$html=$html -replace '^### (.*?)$','<section><h3 style="margin:25px 0 12px 0;font-size:16px;font-weight:bold;color:#444;">$1</h3></section>'

# Bold with color
$html=$html -replace '\*\*(.*?)\*\*','<strong style="color:#07c160;font-weight:bold;">$1</strong>'

# Blockquote
$html=$html -replace '^> (.*?)$','<section><section style="margin:20px 0;padding:15px 20px;background:#f6f6f6;border-left:4px solid #999;border-radius:3px;"><p style="margin:0;color:#666;font-style:italic;line-height:1.7;">$1</p></section></section>'

# Horizontal rule
$html=$html -replace '\n---\n','<section><hr style="border:none;border-top:2px dashed #07c160;margin:30px 0;opacity:0.6;" /></section>'

# Paragraphs
$html=$html -replace '\n\n','</p></section><section><p style="margin:15px 0;line-height:1.9;font-size:15px;color:#3f3f3f;text-align:justify;">'

# Lists
$html=$html -replace '\n[-*] ','<br/>馃敼 '

# Clean markdown
$html=$html -replace '```.*?```' -replace '`'

# Wrap
$html="<section style='max-width:100%;box-sizing:border-box;background:#fff;'><section><p style='margin:15px 0;line-height:1.9;font-size:15px;color:#3f3f3f;text-align:justify;'>$html</p></section></section>"

# Escape
$htmlEscaped=$html -replace '\\','\\\\' -replace '"','\"' -replace "`n",'' -replace "`r",''

# Payload
$payload='{"articles":[{"title":"14:1 de magic: Mazda","author":"Nice","digest":"Mazda Skyactiv technology","content":"'+$htmlEscaped+'","thumb_media_id":"'+$ThumbMediaId+'","need_open_comment":1,"only_fans_can_comment":0}]}'

$url="https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$AccessToken"
Write-Host "Publishing with styled HTML..."
$response=Invoke-RestMethod -Uri $url -Method Post -Body $payload -ContentType "application/json"
Write-Output "Result: $($response | ConvertTo-Json)"
