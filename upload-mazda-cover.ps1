param([string]$AccessToken)
$coverPath="C:\Users\Administrator\.openclaw\workspace\mazda-cover-generated.jpg"
$boundary="----WebKitFormBoundary"+[Guid]::NewGuid().ToString("N")
$fileBytes=[System.IO.File]::ReadAllBytes($coverPath)
$formData=[System.Text.Encoding]::UTF8.GetBytes("--$boundary`r`n"+'Content-Disposition: form-data; name="media"; filename="mazda-cover.jpg"'+"`r`n"+"Content-Type: image/jpeg`r`n`r`n")
$endData=[System.Text.Encoding]::UTF8.GetBytes("`r`n--$boundary--`r`n")
$allBytes=New-Object byte[] ($formData.Length+$fileBytes.Length+$endData.Length)
[System.Buffer]::BlockCopy($formData,0,$allBytes,0,$formData.Length)
[System.Buffer]::BlockCopy($fileBytes,0,$allBytes,$formData.Length,$fileBytes.Length)
[System.Buffer]::BlockCopy($endData,0,$allBytes,$formData.Length+$fileBytes.Length,$endData.Length)
$url="https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=$AccessToken"
$headers=@{"Content-Type"="multipart/form-data; boundary=$boundary"}
try{
$response=Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $allBytes
Write-Output "鉁?Upload Success"
Write-Output "Media ID: $($response.media_id)"
Write-Output "URL: $($response.url)"
$response.media_id|Out-File "C:\Users\Administrator\.openclaw\workspace\mazda-cover-media-id.txt" -Encoding UTF8
}catch{
Write-Output "鉂?Error: $_"
}
