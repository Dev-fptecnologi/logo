# DEVMARK – logos

- `logos/` — SVG (vectorial, transparente) + PNG de cada versión: `horizontal`, `vertical`, `icon`, `wordmark`
  × `color` (fondo claro), `color-dark` (fondo oscuro), `white`, `black`. Más `devmark-app-icon` y `favicon-32.png`. `_preview.png` es la hoja resumen.
- `source/icon-original.png` — logo original; `source/icon-path.json` — ícono vectorizado.
- `tools/vectorize_icon.py`, `tools/build_logos.py` — regeneran todo (`pip install potracer fonttools cairosvg pillow numpy`).

## Fuente Braze
Coloca la fuente en `fonts/Braze.otf` (o `.ttf`/`.woff`) y ejecuta `python3 -I tools/build_logos.py`.
Mientras no exista, el texto usa **Poppins Bold como respaldo provisional**.

Colores: primario `#3253CD`, oscuro `#0E1739`, sobre oscuro `#5772D6`.
