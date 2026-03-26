param(
    [string]$AccessToken
)

# Create a simple cover image using a placeholder
$coverUrl = "https://picsum.photos/800/450"
$coverPath = "C:\Users\Administrator\.openclaw\workspace\mazda-cover-temp.jpg"

# Download image
Invoke-WebRequest -Uri $coverUrl -OutFile $coverPath -UseBasicParsing
Write-Host "Downloaded cover image: $coverPath"

# Upload to WeChat
$boundary = "----WebKitFormBoundary" + [Guid]::NewGuid().ToString("N")
$fileBytes = [System.IO.File]::ReadAllBytes($coverPath)

# Build multipart form data
$formData = [System.Text.Encoding]::UTF8.GetBytes(
    "--$boundary`r`n" +
    'Content-Disposition: form-data; name="media"; filename="cover.jpg"' + "`r`n" +
    "Content-Type: image/jpeg`r`n`r`n"
)

$endData = [System.Text.Encoding]::UTF8.GetBytes(
    "`r`n--$boundary--`r`n"
)

# Combine all parts
$allBytes = New-Object byte[] ($formData.Length + $fileBytes.Length + $endData.Length)
[System.Buffer]::BlockCopy($formData, 0, $allBytes, 0, $formData.Length)
[System.Buffer]::BlockCopy($fileBytes, 0, $allBytes, $formData.Length, $fileBytes.Length)
[System.Buffer]::BlockCopy($endData, 0, $allBytes, $formData.Length + $fileBytes.Length, $endData.Length)

# Upload
$url = "https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=$AccessToken"
$headers = @{"Content-Type" = "multipart/form-data; boundary=$boundary"}

try {
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $allBytes
    Write-Output "鉁?Upload Success!"
    Write-Output "Media ID: $($response.media_id)"
    Write-Output "URL: $($response.url)"
    
    # Save media_id for next step
    $response.media_id | Out-File "C:\Users\Administrator\.openclaw\workspace\media_id.txt" -Encoding UTF8
} catch {
    Write-Output "鉂?Upload Error: $_"
}
