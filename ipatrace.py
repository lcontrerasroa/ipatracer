# -*- coding: utf-8 -*-
"""
ipatrace.py
Génération des pochoirs SVG IPA pour toutes les polices de l'application.

Usage (depuis la racine du dépôt) :
    uv run --with fonttools python ipatrace.py            # toutes les polices
    uv run --with fonttools python ipatrace.py andika     # une seule

Échelle COMMUNE par police : tous les glyphes d'une police partagent la même
échelle et la même ligne de base, donc ˈ reste petit et haut, ɪ reste plus
petit que l, etc. Le script écrit aussi docs/svgs/<police>/metrics.json
(ligne de base et hauteur d'x, en fraction de la hauteur du pochoir), que
l'application utilise pour tracer les lignes de guidage.
"""

import json, unicodedata, zipfile, urllib.request, logging, sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent

# ── 1. Symboles à exporter ────────────────────────────────────────────────────
# Ajout/suppression ici, puis mettre à jour docs/symbols.json.
# On utilise ɡ (U+0261, g script de l'API) et non g (U+0067).
SYMBOLS = """\
a æ ɑ ɒ ɔ e ə ɜ ʌ i ɪ u ʊ
p b t d k ɡ f v θ ð s z ʃ ʒ h
m n ŋ l ɫ r ɹ j w ɾ ʔ
ˈ ˌ ː
""".split()

# ── 2. Polices ────────────────────────────────────────────────────────────────
ANDIKA_URL = "https://software.sil.org/downloads/r/andika/Andika-6.200.zip"
FONT_DIR   = ROOT / "fonts"
FONTS = {
    "andika": FONT_DIR / "Andika-Regular.ttf",
    "mplus":  FONT_DIR / "MPLUS1p-Thin.ttf",
    "arimo":  FONT_DIR / "Arimo-Regular.ttf",
    "dejavu": FONT_DIR / "DejaVuSans.ttf",
    "cmu":    FONT_DIR / "CMU Bright.otf",
}
OUTDIR = ROOT / "docs" / "svgs"

# Glyphes imposés : le « a » par défaut d'Andika est à un étage (forme
# d'alphabétisation), indiscernable de ɑ. On prend la variante à deux étages.
GLYPH_OVERRIDES = {
    "andika": {"a": "a.2StorySItal"},
}

VIEWBOX_EM  = 1000      # unités internes du viewBox
PADDING_PCT = 6.0       # % de marge autour du glyphe
INFLATE_PX  = 6         # épaississement du contour
FILL_COLOR  = "#000000"


# ── 3. Téléchargement d'Andika si absente ────────────────────────────────────
def ensure_andika(dest: Path) -> None:
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    zip_path = dest.parent / "andika.zip"
    log.info("Téléchargement Andika…")
    urllib.request.urlretrieve(ANDIKA_URL, zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        name = next(n for n in zf.namelist() if n.endswith("/Andika-Regular.ttf"))
        dest.write_bytes(zf.read(name))
    zip_path.unlink()


# ── 4. Carte de caractères ───────────────────────────────────────────────────
def build_cmap(tt: TTFont) -> dict[int, str]:
    """{codepoint: glyph_name}, toutes tables Unicode puis getBestCmap()."""
    cmap: dict[int, str] = {}
    for table in tt["cmap"].tables:
        if table.isUnicode():
            cmap.update({cp: name for cp, name in table.cmap.items()
                         if isinstance(name, str)})
    best = tt.getBestCmap()
    if best:
        cmap.update(best)
    return cmap


def char_to_glyph(ch: str, cmap: dict[int, str]) -> str | None:
    """Résolution : codepoint direct → base de la décomposition NFD → None."""
    cp = ord(ch)
    if cp in cmap:
        return cmap[cp]
    nfd = unicodedata.normalize("NFD", ch)
    if nfd != ch and ord(nfd[0]) in cmap:
        log.warning("U+%04X '%s' : caractère de base NFD utilisé.", cp, ch)
        return cmap[ord(nfd[0])]
    log.warning("U+%04X '%s' (%s) : glyphe introuvable.",
                cp, ch, unicodedata.name(ch, "?"))
    return None


# ── 5. Chemin SVG et bornes ───────────────────────────────────────────────────
def glyph_path_d(gs, glyph_name: str) -> str | None:
    pen = SVGPathPen(gs)
    gs[glyph_name].draw(pen)
    return pen.getCommands() or None


def glyph_bounds(gs, glyph_name: str):
    pen = BoundsPen(gs)
    gs[glyph_name].draw(pen)
    return pen.bounds


# ── 6. Export d'une police ────────────────────────────────────────────────────
def export_font(key: str, font_path: Path, outdir: Path) -> tuple[int, int]:
    tt = TTFont(font_path)
    gs = tt.getGlyphSet()
    cmap = build_cmap(tt)

    glyphs = {}   # ch -> (glyph_name, d, bounds)
    for ch in SYMBOLS:
        gname = GLYPH_OVERRIDES.get(key, {}).get(ch) or char_to_glyph(ch, cmap)
        if not gname or gname not in gs:
            continue
        d = glyph_path_d(gs, gname)
        b = glyph_bounds(gs, gname)
        if not d or not b:
            log.warning("[%s] '%s' → glyphe vide.", key, ch)
            continue
        glyphs[ch] = (gname, d, b)

    # Boîte commune : extension verticale de tout le jeu, largeur max
    ymin = min(b[1] for _, _, b in glyphs.values())
    ymax = max(b[3] for _, _, b in glyphs.values())
    wmax = max(b[2] - b[0] for _, _, b in glyphs.values())
    span = max(ymax - ymin, wmax)
    scale = VIEWBOX_EM / span
    pad = VIEWBOX_EM * PADDING_PCT / 100.0
    vb = VIEWBOX_EM + 2 * pad
    ty = pad + (VIEWBOX_EM - (ymax - ymin) * scale) / 2 + ymax * scale  # flip Y

    stroke = (f' stroke="{FILL_COLOR}" stroke-width="{INFLATE_PX}"'
              f' stroke-linejoin="round" stroke-linecap="round"') if INFLATE_PX else ""

    fontdir = outdir / key
    fontdir.mkdir(parents=True, exist_ok=True)
    for old in fontdir.glob("*.svg"):
        old.unlink()

    for ch, (gname, d, (x0, _, x1, _)) in glyphs.items():
        tx = vb / 2 - (x0 + x1) / 2 * scale     # centrage horizontal
        svg = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg width="{vb:.0f}" height="{vb:.0f}" viewBox="0 0 {vb:.3f} {vb:.3f}" '
            f'xmlns="http://www.w3.org/2000/svg">\n'
            f'  <rect x="0" y="0" width="{vb:.3f}" height="{vb:.3f}" fill="white"/>\n'
            f'  <g transform="translate({tx:.3f},{ty:.3f}) scale({scale:.5f},{-scale:.5f})">\n'
            f'    <path d="{d}" fill="{FILL_COLOR}"{stroke}/>\n'
            f'  </g>\n'
            f'</svg>\n'
        )
        (fontdir / f"{safe_stem(ch)}.svg").write_text(svg, encoding="utf-8")

    # Métriques pour les lignes de guidage (fractions de la hauteur)
    xh = getattr(tt["OS/2"], "sxHeight", 0) or 0
    if not xh and ord("x") in cmap:
        xh = glyph_bounds(gs, cmap[ord("x")])[3]
    metrics = {"baseline": round(ty / vb, 4),
               "xheight": round((ty - xh * scale) / vb, 4) if xh else None}
    (fontdir / "metrics.json").write_text(json.dumps(metrics) + "\n", encoding="utf-8")

    miss = len(SYMBOLS) - len(glyphs)
    log.info("[%s] %d SVG, %d manquants, %s", key, len(glyphs), miss, metrics)
    return len(glyphs), miss


def safe_stem(ch: str) -> str:
    """Nom de fichier sûr : caractère si imprimable et non spécial, sinon uXXXX."""
    unsafe = set(r'\/:*?"<>| ')
    return ch if (ch.isprintable() and ch not in unsafe) else f"u{ord(ch):04X}"


# ── 7. Point d'entrée ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    keys = sys.argv[1:] or list(FONTS)
    ensure_andika(FONTS["andika"])
    for k in keys:
        export_font(k, FONTS[k], OUTDIR)
