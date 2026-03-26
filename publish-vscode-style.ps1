param([string]$AccessToken,[string]$ThumbMediaId)

# Read markdown
$md=Get-Content "C:\Users\Administrator\.openclaw\workspace\mazda-skyactiv-article.md" -Raw -Encoding UTF8
$lines=$md -split "`r?`n"

# Build HTML with VSCode blue tech style
$html=@()

# Container start
$html+='<div style="font-family:-apple-system,BlinkMacSystemFont,Helvetica Neue,PingFang SC,Microsoft YaHei,sans-serif;line-height:1.8;color:#333;padding:15px;max-width:100%;box-sizing:border-box;background-color:#ffffff;text-indent:0;">'

$isFirstPara=$true
$sectionNum=1

foreach($line in $lines){
    # Skip H1 (article title)
    if($line -match '^# '){continue}
    
    # H2 -> Chapter title with number
    if($line -match '^## (.+)$'){
        $title=$matches[1]
        $html+="<h2 style='margin:40px 0 20px;text-align:left;line-height:32px;'>"
        $html+="<span style='display:inline-block;background-color:#007acc;color:#fff;width:28px;height:28px;border-radius:50%;text-align:center;line-height:28px;font-size:14px;vertical-align:middle;'>$( '{0:D2}' -f $sectionNum)</span>"
        $html+="<span style='display:inline-block;font-size:20px;color:#007acc;font-weight:bold;vertical-align:middle;margin-left:8px;'>$title</span>"
        $html+="</h2>"
        $sectionNum++
    }
    # H3 -> Subsection title
    elseif($line -match '^### (.+)$'){
        $title=$matches[1]
        $html+="<h3 style='margin:30px 0 15px;font-size:17px;color:#007acc;font-weight:bold;border-left:3px solid #007acc;padding-left:12px;'>$title</h3>"
    }
    # Blockquote -> Lead/summary box
    elseif($line -match '^> (.+)$'){
        $text=$matches[1]
        $html+="<table style='width:100%;border-collapse:collapse;margin:20px 0;'><tr><td style='background-color:#f0f7ff;border-left:5px solid #007acc;padding:20px;text-align:left;'>"
        $html+="<p style='margin:0;font-size:15px;color:#444;text-indent:0;text-align:left;'>$text</p></td></tr></table>"
    }
    # Horizontal rule
    elseif($line -eq '---'){
        $html+="<hr style='border:none;border-top:1px dashed #007acc;margin:30px 0;opacity:0.6;' />"
    }
    # Bold emphasis -> Key point card
    elseif($line -match '^\*\*(.+)\*\*$'){
        $text=$matches[1]
        $html+="<table style='width:100%;border-collapse:collapse;margin:15px 0;'><tr><td style='background-color:#fffaf0;border-left:5px solid #ff9800;padding:15px;font-size:15px;color:#666;text-indent:0;'>"
        $html+="<p style='margin:0;text-indent:0;'>$text</p></td></tr></table>"
    }
    # Normal paragraph
    elseif($line -match '\S'){
        # Process bold in paragraph
        $line=$line -replace '\*\*(.+?)\*\*','<strong style="color:#007acc;">$1</strong>'
        if($isFirstPara){
            $html+="<p style='margin-bottom:20px;text-indent:0;text-align:left;font-size:15px;'>$line</p>"
            $isFirstPara=$false
        }else{
            $html+="<p style='margin-bottom:15px;text-indent:0;text-align:left;font-size:15px;'>$line</p>"
        }
    }
}

$html+='</div>'
$finalHtml=$html -join "`n"

# Escape for JSON
$finalHtml=$finalHtml -replace '\\','\\\\' -replace '"','\"'

# Build JSON
$json=@"
{"articles":[{"title":"14:1 鐨勯瓟娉曪細椹嚜杈惧浣曠敤鏈€绗ㄧ殑鍐呯噧鏈烘妧鏈紝鍦ㄧ數鍔ㄦ椂浠ｆ潃鍑轰竴鏉¤璺紵","author":"Nice 鍝?,"digest":"椹嚜杈惧垱椹拌摑澶╂妧鏈繁搴﹁В鏋?,"content":"$finalHtml","thumb_media_id":"$ThumbMediaId","need_open_comment":1,"only_fans_can_comment":0}]}
"@

$url="https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$AccessToken"
Write-Host "Publishing with VSCode blue tech style..."
$response=Invoke-RestMethod -Uri $url -Method Post -Body $json -ContentType "application/json; charset=utf-8"
Write-Output "鉁?Published!"
Write-Output "Media ID: $($response.media_id)"
