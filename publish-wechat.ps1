param([string]$AccessToken,[string]$ThumbMediaId)
$markdown=Get-Content "C:\Users\Administrator\.openclaw\workspace\mazda-skyactiv-article.md" -Raw -Encoding UTF8
$html=$markdown
$html=$html -replace '^# (.*?)$','<h1>$1</h1>'
$html=$html -replace '^## (.*?)$','<h2>$1</h2>'
$html=$html -replace '^### (.*?)$','<h3>$1</h3>'
$html=$html -replace '\*\*(.*?)\*\*','<strong>$1</strong>'
$html=$html -replace '\n---\n','<hr/>'
$html=$html -replace '\n\n','</p><p>'
$html="<div><p>$html</p></div>"
$html=$html -replace '`',''
$htmlEscaped=$html -replace '\\','\\\\' -replace '"','\"' -replace "`n",'' -replace "`r",''
$payload='{"articles":[{"title":"14:1 de magic: Mazda Skyactiv","author":"Nice","digest":"Mazda Skyactiv technology analysis","content":"'+$htmlEscaped+'","thumb_media_id":"'+$ThumbMediaId+'","need_open_comment":1,"only_fans_can_comment":0}]}'
$url="https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$AccessToken"
Write-Host "Publishing..."
$response=Invoke-RestMethod -Uri $url -Method Post -Body $payload -ContentType "application/json"
Write-Output "Result: $($response | ConvertTo-Json)"
