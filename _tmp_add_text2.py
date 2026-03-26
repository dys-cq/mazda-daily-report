from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

img_path = r"C:\Users\Administrator\Downloads\imgs\cover_base.png"
out_path = r"C:\Users\Administrator\Downloads\imgs\cover_final.png"

img = Image.open(img_path).convert("RGBA")
W, H = img.size

font_candidates = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
]
font_path = None
for p in font_candidates:
    if Path(p).exists():
        font_path = p
        break
if not font_path:
    raise FileNotFoundError("No Chinese font found (msyh/simhei)")

# Text
title = "百度搜索系列技能安装指南"
subtitle = "让你免费使用三个月的专业技能"

font_title = ImageFont.truetype(font_path, int(H * 0.085))
font_sub = ImageFont.truetype(font_path, int(H * 0.05))

draw = ImageDraw.Draw(img)

bbox_t = draw.textbbox((0, 0), title, font=font_title)
text_w_t = bbox_t[2] - bbox_t[0]
text_h_t = bbox_t[3] - bbox_t[1]

bbox_s = draw.textbbox((0, 0), subtitle, font=font_sub)
text_w_s = bbox_s[2] - bbox_s[0]
text_h_s = bbox_s[3] - bbox_s[1]

margin_x = int(W * 0.06)
margin_y = int(H * 0.08)
line_gap = int(H * 0.05)

bar_h = text_h_t + text_h_s + line_gap + int(H * 0.06)
bar_w = max(text_w_t, text_w_s) + int(W * 0.10)
bar = Image.new("RGBA", (bar_w, bar_h), (0, 0, 0, 90))
img.alpha_composite(bar, (margin_x - int(W * 0.02), margin_y - int(H * 0.02)))

text_color = (255, 255, 255, 245)

x = margin_x
y = margin_y

draw.text((x, y), title, font=font_title, fill=text_color)

y2 = y + text_h_t + line_gap

draw.text((x, y2), subtitle, font=font_sub, fill=text_color)

img.convert("RGB").save(out_path)
print(out_path)
