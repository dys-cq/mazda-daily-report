param([string]$AccessToken)
$coverPath="C:\Users\Administrator\.openclaw\media\browser\b2637157-63e4-42f7-b9f2-fba65a631488.png"
$boundary="----WebKitFormBoundary"+[Guid]::NewGuid().ToString("N")
$fileBytes=[System.IO.File]::ReadAllBytes($coverPath)
$formData=[System.Text.Encoding]::UTF8.GetBytes("--$boundary`r`n"+'Content-Disposition: form-data; name="media"; filename="mazda-cover.png"'+"`r`n"+"Content-Type: image/png`r`n`r`n")
$endData=[System.Text.Encoding]::UTF8.GetBytes("`r`n--$boundary--`r`n")
$allBytes=New-Object byte[] ($formData.Length+$fileBytes.Length+$endData.Length)
[System.Buffer]::BlockCopy($formData,0,$allBytes,0,$formData.Length)
[System.Buffer]::BlockCopy($fileBytes,0,$allBytes,$formData.Length,$fileBytes.Length)
[System.Buffer]::BlockCopy($endData,0,$allBytes,$formData.Length+$fileBytes.Length,$endData.Length)
$url="https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=$AccessToken"
$headers=@{"Content-Type"="multipart/form-data; boundary=$boundary"}
$response=Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $allBytes
Write-Output "Media ID: $($response.media_id)"
Write-Output "URL: $($response.url)"
$response.media_id|Out-File "C:\Users\Administrator\.openclaw\workspace\new-cover-media-id.txt" -Encoding UTF8
