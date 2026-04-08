from PIL import Image, ImageDraw, ImageFont
import os

sizes = [16, 32, 64, 128, 256, 512, 1024]
icon_dir = "TalentoSostenibleApp/TalentoSostenible/Assets.xcassets/AppIcon.appiconset"
os.makedirs(icon_dir, exist_ok=True)

for s in sizes:
    img = Image.new("RGB", (s, s), "#15803d")
    draw = ImageDraw.Draw(img)

    margin = int(s * 0.08)
    if s >= 32:
        draw.rounded_rectangle(
            [margin, margin, s - margin, s - margin],
            radius=int(s * 0.2),
            fill="#166534",
        )

    font_size = max(int(s * 0.45), 8)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except Exception:
        font = ImageFont.load_default()

    text = "TS"
    left, top, right, bottom = font.getbbox(text)
    tw = right - left
    th = bottom - top
    x = (s - tw) / 2 - left
    y = (s - th) / 2 - top
    draw.text((x, y), text, fill="white", font=font)

    img.save(os.path.join(icon_dir, f"icon_{s}x{s}.png"))

print("Iconos generados OK")
