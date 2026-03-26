# 使用 ffmpeg 合成视频
# 创建素材列表文件

$work = "C:\Users\Administrator\.openclaw\workspace\output\video_remix_full\work"
$output = "C:\Users\Administrator\.openclaw\workspace\output\video_remix_full"

# 创建 concat 文件
$concat = "$output\concat_list.txt"
@"
file '$work\asset_开头钩子.mp4'
file '$work\asset_痛点引入.mp4'
file '$work\asset_产品介绍.mp4'
file '$work\asset_卖点展示.mp4'
file '$work\asset_行动号召.mp4'
"@ | Set-Content $concat -Encoding UTF8

Write-Host "Created concat list: $concat"
Get-Content $concat
