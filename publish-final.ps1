param([string]$AccessToken,[string]$ThumbMediaId)
$lines=Get-Content "C:\Users\Administrator\.openclaw\workspace\mazda-skyactiv-article.md" -Encoding UTF8
$htmlLines=@()
foreach($line in $lines){
    if($line -match '^# (.+)$'){$htmlLines+="<h1 style='text-align:center;font-size:20px;font-weight:bold;margin:30px 0 20px 0;color:#333;'>$($matches[1])</h1>"}
    elseif($line -match '^## (.+)$'){$htmlLines+="<h2 style='font-size:17px;font-weight:bold;margin:25px 0 15px 0;color:#07c160;border-left:4px solid #07c160;padding-left:12px;'>$($matches[1])</h2>"}
    elseif($line -match '^### (.+)$'){$htmlLines+="<h3 style='font-size:16px;font-weight:bold;margin:20px 0 12px 0;color:#444;'>$($matches[1])</h3>"}
    elseif($line -eq '---'){$htmlLines+='<hr style="border:none;border-top:1px solid #e0e0e0;margin:25px 0;" />'}
    elseif($line -match '^> (.+)$'){$htmlLines+="<blockquote style='margin:15px 0;padding:10px 15px;background:#f5f5f5;border-left:3px solid #ccc;color:#666;'>$($matches[1])</blockquote>"}
    elseif($line -match '^\s*[-*]\s+(.+)'){$htmlLines+="鈥?$($matches[1])<br/>"}
    elseif($line -match '\*\*(.+?)\*\*'){$line=$line -replace '\*\*(.+?)\*\*','<strong>$1</strong>';$htmlLines+="<p style='margin:12px 0;line-height:1.8;font-size:15px;color:#333;'>$line</p>"}
    elseif($line -match '\S'){$htmlLines+="<p style='margin:12px 0;line-height:1.8;font-size:15px;color:#333;'>$line</p>"}
    else{$htmlLines+='<br/>'}
}
$html="<section>$($htmlLines -join "`n")</section>"
$html=$html -replace '\\','\\\\' -replace '"','\"'
$json=@"
{"articles":[{"title":"14:1 magic Mazda","author":"Nice","digest":"Mazda Skyactiv technology","content":"$html","thumb_media_id":"$ThumbMediaId","need_open_comment":1,"only_fans_can_comment":0}]}
"@
$url="https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$AccessToken"
Write-Host "Publishing with new cover..."
$response=Invoke-RestMethod -Uri $url -Method Post -Body $json -ContentType "application/json; charset=utf-8"
Write-Output "Media ID: $($response.media_id)"
