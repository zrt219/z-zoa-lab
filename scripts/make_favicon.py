from PIL import Image, ImageDraw
import base64
from pathlib import Path

src_path = Path(r"C:\Users\Zhane\.gemini\antigravity\brain\37f6f95f-e727-446f-8df3-ca806ec5ad9e\z_zoa_favicon_1789525819851.jpg")
img = Image.open(src_path).convert("RGBA")
w, h = img.size
print(f"Loaded source image: {w}x{h}")

# Create smooth circular mask
mask = Image.new("L", (w, h), 0)
draw = ImageDraw.Draw(mask)
margin = int(w * 0.008)
draw.ellipse((margin, margin, w - margin, h - margin), fill=255)

# Apply mask with transparent corners
circ_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
circ_img.paste(img, (0, 0), mask=mask)

pub_dir = Path("frontend/public")
pub_dir.mkdir(parents=True, exist_ok=True)

# 1. High-res master PNGs
circ_512 = circ_img.resize((512, 512), Image.Resampling.LANCZOS)
circ_512.save(pub_dir / "favicon.png", format="PNG")
circ_512.save(pub_dir / "favicon-512x512.png", format="PNG")

# 2. Apple Touch Icon (180x180)
circ_180 = circ_img.resize((180, 180), Image.Resampling.LANCZOS)
circ_180.save(pub_dir / "apple-touch-icon.png", format="PNG")

# 3. Standard favicon sizes
circ_32 = circ_img.resize((32, 32), Image.Resampling.LANCZOS)
circ_32.save(pub_dir / "favicon-32x32.png", format="PNG")

circ_16 = circ_img.resize((16, 16), Image.Resampling.LANCZOS)
circ_16.save(pub_dir / "favicon-16x16.png", format="PNG")

# 4. Multi-resolution favicon.ico
circ_img.save(
    pub_dir / "favicon.ico",
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)

# 5. Scalable favicon.svg embedding the high-res 512x512 PNG
with open(pub_dir / "favicon-512x512.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("ascii")

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <clipPath id="circle-clip">
      <circle cx="256" cy="256" r="252" />
    </clipPath>
  </defs>
  <image href="data:image/png;base64,{b64}" width="512" height="512" clip-path="url(#circle-clip)" />
</svg>
'''
with open(pub_dir / "favicon.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

print("All favicons generated successfully in frontend/public:")
for item in pub_dir.glob("favicon*"):
    print(f"  - {item.name} ({item.stat().st_size} bytes)")
print(f"  - apple-touch-icon.png ({(pub_dir / 'apple-touch-icon.png').stat().st_size} bytes)")
