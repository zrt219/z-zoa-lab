"""Generate complete favicon suite with high-contrast white background for Z-ZOA Lab."""

from __future__ import annotations

import base64
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

src_path = Path("docs/favicon_source_white.jpg")
if not src_path.exists():
    src_path = Path("frontend/public/favicon.svg")
if not src_path.exists():
    raise FileNotFoundError("Source asset docs/favicon_source_white.jpg not found.")

img = Image.open(src_path).convert("RGB")
w, h = img.size
print(f"Loaded source image: {w}x{h}")

# 1. Clean background: clamp near-white pixels (compression noise) to pure #FFFFFF
arr = np.array(img, dtype=np.float32)
mask_white = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
arr[mask_white] = 255.0
clean_rgb = Image.fromarray(arr.astype(np.uint8))

# 2. Prepare squircle (rounded rectangle) mask for browser favicons
# Radius ~ 22% matches modern iOS / macOS app squircle curvature
radius = int(w * 0.22)
squircle_mask = Image.new("L", (w, h), 0)
draw_mask = ImageDraw.Draw(squircle_mask)
draw_mask.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)

squircle_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
squircle_img.paste(clean_rgb.convert("RGBA"), (0, 0), mask=squircle_mask)

pub_dir = Path("frontend/public")
pub_dir.mkdir(parents=True, exist_ok=True)

# 3. Save master 512x512 PNGs (squircle with pure white fill)
squircle_512 = squircle_img.resize((512, 512), Image.Resampling.LANCZOS)
squircle_512.save(pub_dir / "favicon.png", format="PNG")
squircle_512.save(pub_dir / "favicon-512x512.png", format="PNG")

# 4. Apple Touch Icon (180x180, square solid white - iOS automatically masks corners)
square_180 = clean_rgb.resize((180, 180), Image.Resampling.LANCZOS)
square_180.save(pub_dir / "apple-touch-icon.png", format="PNG")

# 5. Standard small favicon PNGs (32x32 and 16x16)
squircle_32 = squircle_img.resize((32, 32), Image.Resampling.LANCZOS)
squircle_32.save(pub_dir / "favicon-32x32.png", format="PNG")

squircle_16 = squircle_img.resize((16, 16), Image.Resampling.LANCZOS)
squircle_16.save(pub_dir / "favicon-16x16.png", format="PNG")

# 6. Multi-resolution favicon.ico
squircle_img.save(
    pub_dir / "favicon.ico",
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)

# 7. Scalable favicon.svg embedding the high-res 512x512 PNG
with open(pub_dir / "favicon-512x512.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("ascii")

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <clipPath id="squircle-clip">
      <rect x="0" y="0" width="512" height="512" rx="112" ry="112" />
    </clipPath>
  </defs>
  <rect x="0" y="0" width="512" height="512" rx="112" ry="112" fill="#FFFFFF" />
  <image href="data:image/png;base64,{b64}" width="512" height="512" clip-path="url(#squircle-clip)" />
</svg>
'''
with open(pub_dir / "favicon.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

print("All white-background favicons generated successfully in frontend/public:")
for item in sorted(pub_dir.glob("favicon*")):
    print(f"  - {item.name} ({item.stat().st_size} bytes)")
print(f"  - apple-touch-icon.png ({(pub_dir / 'apple-touch-icon.png').stat().st_size} bytes)")
