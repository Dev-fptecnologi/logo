"""Genera todas las versiones del logo DEVMARK (SVG + PNG) a partir de:
  - source/icon-path.json   (ícono vectorizado, ver vectorize_icon.py)
  - fonts/Braze.(otf|ttf|woff)  (fuente del logotipo; si falta se usa un respaldo Poppins Bold)
Uso:  python3 -I tools/build_logos.py
"""
import glob, json, os, sys
import cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

TEXT = "DEVMARK"
TRACKING = 0.08          # espaciado entre letras (em)
OUT = "logos"

# Paleta de marca
P500, P400, P900, P950, WHITE, BLACK = "#3253CD", "#5772D6", "#0E1739", "#050815", "#FFFFFF", "#000000"
# variante -> (color ícono, color texto, fondo recomendado)
VARIANTS = {
    "color":       (P500, P900, "fondo claro"),
    "color-dark":  (P400, WHITE, "fondo oscuro"),
    "white":       (WHITE, WHITE, "fondo de color / foto"),
    "black":       (BLACK, BLACK, "una tinta, fondo claro"),
}

icon = json.load(open("source/icon-path.json"))
IW, IH, ID = icon["w"], icon["h"], icon["d"]

found = sorted(glob.glob("fonts/Braze*.[ot]tf") + glob.glob("fonts/Braze*.woff"))
FONT = found[0] if found else "fonts/Poppins-Bold-fallback.woff"
USING_FALLBACK = not found
print("Fuente:", FONT, "(RESPALDO, falta Braze)" if USING_FALLBACK else "")

font = TTFont(FONT)
gs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
hmtx = font["hmtx"]

_geo = {}
def geometry(txt):
    """(glifos con x, margen izq, ancho de tinta, alto mayúscula, base) en unidades de fuente."""
    if txt in _geo: return _geo[txt]
    x, items = 0, []
    for ch in txt:
        g = cmap[ord(ch)]
        items.append((g, x))
        x += hmtx[g][0] + TRACKING * upm
    bp = BoundsPen(gs); gs[cmap[ord("D")]].draw(bp)
    b0 = BoundsPen(gs); gs[items[0][0]].draw(b0)
    b1 = BoundsPen(gs); gs[items[-1][0]].draw(b1)
    left = b0.bounds[0]
    _geo[txt] = (items, left, items[-1][1] + b1.bounds[2] - left, bp.bounds[3] - bp.bounds[1], bp.bounds[1])
    return _geo[txt]

def text_path(cap_h, tx, ty, txt=TEXT):
    """Path SVG del texto con altura de mayúscula cap_h, esquina sup-izq de la tinta en (tx, ty)."""
    items, left, tw, cap, base = geometry(txt)
    s = cap_h / cap
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}")
    for g, gx in items:
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, tx + (gx - left) * s, ty + (base + cap) * s)))
    return pen.getCommands(), tw * s

def chevron(direction, x, cy, cap):
    """Chevron sólido < o > de altura 0.92*cap centrado en cy; devuelve (path, ancho)."""
    h, d, k = cap * 0.43, cap * 0.46, cap * 0.25
    pts = [(d, -h), (0, 0), (d, h), (d, h - k), (k * d / h, 0), (d, -h + k)]
    if direction == ">": pts = [(d - px, py) for px, py in pts]
    return "M" + "L".join(f"{x + px:.2f} {cy + py:.2f}" for px, py in pts) + "Z", d

def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" '
            f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="DEVMARK">{body}</svg>\n')

def icon_el(ic, x=0, y=0, scale=1):
    return f'<path fill="{ic}" fill-rule="evenodd" transform="translate({x:.2f} {y:.2f}) scale({scale:.4f})" d="{ID}"/>'

def text_el(tc, cap, x, y, txt=TEXT):
    d, w = text_path(cap, x, y, txt)
    return f'<path fill="{tc}" d="{d}"/>', w

def build(kind, ic, tc):
    if kind == "icon":
        return IW, IH, icon_el(ic)
    if kind == "wordmark":
        cap = 100
        el, w = text_el(tc, cap, 0, 0)
        return w, cap, el
    if kind == "horizontal":
        cap = IH * 0.40; gap = IH * 0.30
        el, w = text_el(tc, cap, IW + gap, (IH - cap) / 2)
        return IW + gap + w, IH, icon_el(ic) + el
    if kind == "vertical":
        gap = IH * 0.28
        _, w1 = text_path(100, 0, 0)
        cap = 100 * (IW * 1.08) / w1            # texto un poco más ancho que el ícono
        el, w = text_el(tc, cap, 0, 0)
        W = max(IW, w)
        el, _ = text_el(tc, cap, (W - w) / 2, IH + gap)
        return W, IH + gap + cap, icon_el(ic, (W - IW) / 2) + el
    if kind in ("brackets", "brackets-icon"):
        cap = 100; g = cap * 0.14
        x0 = IW + IH * 0.30 if kind == "brackets-icon" else 0
        H = IH if kind == "brackets-icon" else cap
        cy = H / 2
        l, dw = chevron("<", x0, cy, cap)
        el, w = text_el(tc, cap, x0 + dw + g, cy - cap / 2)
        r, _ = chevron(">", x0 + dw + g + w + g, cy, cap)
        body = (icon_el(ic, 0, 0, 1) if kind == "brackets-icon" else "")
        return x0 + 2 * dw + 2 * g + w, H, body + f'<path fill="{ic}" d="{l}{r}"/>' + el
    if kind == "social":
        S = 600; line = 6
        cap = S * 0.115
        _, w = text_path(cap, 0, 0, "MARK")
        k = S * 0.66 / w; cap *= k
        iw = S * 0.52; isc = iw / IW; ih = IH * isc
        gap1, gap2 = S * 0.08, cap * 0.38
        total = ih + gap1 + 2 * cap + gap2
        y = (S - total) / 2
        e1, w1 = text_el(tc, cap, 0, 0, "DEV"); e1, _ = text_el(tc, cap, (S - w1) / 2, y + ih + gap1, "DEV")
        e2, w2 = text_el(tc, cap, 0, 0, "MARK"); e2, _ = text_el(tc, cap, (S - w2) / 2, y + ih + gap1 + cap + gap2, "MARK")
        frame = f'<rect x="{line/2}" y="{line/2}" width="{S-line}" height="{S-line}" fill="none" stroke="{tc}" stroke-width="{line}"/>'
        return S, S, frame + icon_el(ic, (S - iw) / 2, y, isc) + e1 + e2
    raise ValueError(kind)

os.makedirs(OUT, exist_ok=True)
KINDS = ["horizontal", "vertical", "icon", "wordmark", "brackets", "brackets-icon", "social"]
made = {}
for kind in KINDS:
    for var, (ic, tc, _) in VARIANTS.items():
        w, h, body = build(kind, ic, tc)
        name = f"devmark-{kind}-{var}"
        path = f"{OUT}/{name}"
        open(path + ".svg", "w").write(svg(w, h, body))
        cairosvg.svg2png(bytestring=svg(w, h, body).encode(), write_to=path + ".png",
                         output_width=int(max(1600, w * 4) if kind != "icon" else 1024))
        made[(kind, var)] = (w, h, body)

# Ícono de app / favicon: ícono blanco sobre cuadrado de marca redondeado
s = 512
sc = s * 0.56 / IW
app = (f'<rect width="{s}" height="{s}" rx="{s*0.22:.0f}" fill="{P500}"/>'
       + icon_el(WHITE, (s - IW * sc) / 2, (s - IH * sc) / 2, sc))
open(f"{OUT}/devmark-app-icon.svg", "w").write(svg(s, s, app))
cairosvg.svg2png(bytestring=svg(s, s, app).encode(), write_to=f"{OUT}/devmark-app-icon.png", output_width=512)
cairosvg.svg2png(bytestring=svg(s, s, app).encode(), write_to=f"{OUT}/favicon-32.png", output_width=32)

# Hoja de presentación
bgs = {"color": "#FFFFFF", "color-dark": P900, "white": P500, "black": "#EAEEFA"}
cols = ["color", "color-dark", "white", "black"]
CW, CH, PAD = 560, 300, 40
sheet = [f'<rect width="{CW*4}" height="{CH*len(KINDS)}" fill="#fff"/>']
for r, kind in enumerate(KINDS):
    for c, var in enumerate(cols):
        w, h, body = made[(kind, var)]
        sc = min((CW - 2 * PAD) / w, (CH - 2 * PAD) / h)
        x, y = c * CW, r * CH
        sheet.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" fill="{bgs[var]}"/>')
        sheet.append(f'<g transform="translate({x + (CW - w*sc)/2:.1f} {y + (CH - h*sc)/2:.1f}) scale({sc:.4f})">{body}</g>')
open(f"{OUT}/_preview.svg", "w").write(svg(CW * 4, CH * len(KINDS), "".join(sheet)))
cairosvg.svg2png(bytestring=svg(CW * 4, CH * len(KINDS), "".join(sheet)).encode(), write_to=f"{OUT}/_preview.png", output_width=1800)  # hoja
print("Listo:", len(os.listdir(OUT)), "archivos en", OUT, "| RESPALDO" if USING_FALLBACK else "")
