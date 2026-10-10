"""Vectoriza source/icon-original.png (blanco sobre negro) -> source/icon-path.json
(path SVG normalizado, origen en 0,0, con ancho/alto)."""
import json, sys
import numpy as np
from PIL import Image, ImageFilter
import potrace

SRC = "source/icon-original.png"
SCALE = 8

im = Image.open(SRC).convert("L")
a = np.array(im)
ys, xs = np.where(a > 128)
x0, x1, y0, y1 = xs.min() - 4, xs.max() + 5, ys.min() - 4, ys.max() + 5
im = im.crop((x0, y0, x1, y1))
im = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS).filter(ImageFilter.GaussianBlur(SCALE * 0.6))
bm = potrace.Bitmap(np.array(im) <= 128)  # potracer traza los píxeles "False"
plist = bm.trace(turdsize=50, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
                 alphamax=1.0, opticurve=True, opttolerance=0.4)

def f(p): return f"{p.x / SCALE:.2f} {p.y / SCALE:.2f}"
d = []
for c in plist:
    d.append(f"M{f(c.start_point)}")
    for s in c.segments:
        if s.is_corner:
            d.append(f"L{f(s.c)}L{f(s.end_point)}")
        else:
            d.append(f"C{f(s.c1)} {f(s.c2)} {f(s.end_point)}")
    d.append("Z")
json.dump({"d": "".join(d), "w": im.width / SCALE, "h": im.height / SCALE}, open("source/icon-path.json", "w"))
print("paths:", len(plist), "size:", im.width / SCALE, im.height / SCALE)
