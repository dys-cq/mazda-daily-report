param([string]$AccessToken,[string]$ThumbMediaId)

# Read HTML
$htmlPath="C:\Users\Administrator\.openclaw\workspace\mazda-skyactiv-article.html"
$html=Get-Content $htmlPath -Raw -Encoding UTF8

# Extract body content only
$start=$html.IndexOf('<body>')
$end=$html.IndexOf('</body>')
if($start -ge 0 -and $end -gt $start){
    $content=$html.Substring($start+6,$end-$start-6).Trim()
}else{
    $content=$html
}

# Remove comments
$content=$content -replace '<!--.*?-->',''

# Escape for JSON
$content=$content -replace '\\','\\\\' -replace '"','\"'

# Build JSON
$json=@"
{"articles":[{"title":"14:1 鐨勯瓟娉曪細椹嚜杈惧浣曠敤鏈€绗ㄧ殑鍐呯噧鏈烘妧鏈紝鍦ㄧ數鍔ㄦ椂浠ｆ潃鍑轰竴鏉¤璺紵","author":"Nice 鍝?,"digest":"椹嚜杈惧垱椹拌摑澶╂妧鏈繁搴﹁В鏋?,"content":"$content","thumb_media_id":"$ThumbMediaId","need_open_comment":1,"only_fans_can_comment":0}]}
"@

$url="https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$AccessToken"
Write-Host "Publishing with wechat-article-formatter tech theme (proper extraction)..."
Write-Host "Content length: $($content.Length) chars"
$response=Invoke-RestMethod -Uri $url -Method Post -Body $json -ContentType "application/json; charset=utf-8"
if($response.media_id){
    Write-Output "鉁?Published successfully!"
    Write-Output "Media ID: $($response.media_id)"
}else{
    Write-Output "鉂?Failed: $($response.errmsg)"
}
