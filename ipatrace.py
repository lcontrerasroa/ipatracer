# -*- coding: utf-8 -*-
"""
ipatrace_optimized.py
Génération de pochoirs SVG IPA depuis la police Andika (SIL).
Optimisé pour Google Colab — colle et exécute dans une seule cellule.
"""

# ── 0. Dépendances ────────────────────────────────────────────────────────────
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "fonttools"], check=True)

import os, unicodedata, zipfile, urllib.request, logging
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── 1. Symboles à exporter ────────────────────────────────────────────────────
# Ajout/suppression ici — un symbole par ligne.
SYMBOLS = """\
a æ ɑ ɒ ɔ e ə ɜ ʌ i ɪ u ʊ
p b t d k ɡ f v θ ð s z ʃ ʒ h
m n ŋ l ɫ r ɹ j w ɾ ʔ
ˈ ˌ ː
""".split()

# Note : on utilise ɡ (U+0261, lettre minuscule script) et non g (U+0067)
# car Andika (et la norme IPA) utilise la forme à boucle unique.

# ── 2. Paramètres ─────────────────────────────────────────────────────────────
ANDIKA_URL  = "https://software.sil.org/downloads/r/andika/Andika-6.200.zip"
FONT_DIR    = Path("/content/fonts")
OUTDIR      = Path("/content/svgs_andika_filled")
ZIP_OUT     = Path("/content/ipa_andika_filled.zip")

VIEWBOX_EM  = 1000      # unités internes du viewBox
PADDING_PCT = 6.0       # % de marge autour du glyphe
INFLATE_PX  = 6         # épaississement du contour (Dice plus tolérant)
FILL_COLOR  = "#000000"


# ── 3. Téléchargement de la police ───────────────────────────────────────────
def get_andika_ttf(font_dir: Path, url: str) -> Path:
    font_dir.mkdir(parents=True, exist_ok=True)
    zip_path = font_dir / "andika.zip"

    if not zip_path.exists():
        log.info("Téléchargement Andika…")
        urllib.request.urlretrieve(url, zip_path)
    else:
        log.info("Archive déjà présente, extraction directe.")

    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(font_dir)

    # On préfère la variante Regular (pas Bold/Italic) — tri pour stabilité
    candidates = sorted(font_dir.rglob("Andika-Regular.ttf"))
    if not candidates:
        candidates = sorted(font_dir.rglob("Andika*.ttf"))
    if not candidates:
        raise FileNotFoundError("Aucun fichier Andika*.ttf trouvé.")
    chosen = candidates[0]
    log.info("Police sélectionnée : %s", chosen)
    return chosen


# ── 4. Carte de caractères ───────────────────────────────────────────────────
def build_cmap(tt: TTFont) -> dict[int, str]:
    """
    Retourne {codepoint: glyph_name}.
    Priorité : getBestCmap() (table Unicode la plus complète), puis fallback
    sur toutes les tables Unicode pour couvrir les plans supplémentaires.
    Correction : on ne tente pas de traiter les valeurs comme des entiers —
    elles sont *toujours* des str dans fontTools.
    """
    cmap: dict[int, str] = {}
    # Fallback tables d'abord (priorité basse)
    for table in tt["cmap"].tables:
        if table.isUnicode():
            cmap.update({cp: name for cp, name in table.cmap.items()
                         if isinstance(name, str)})
    # getBestCmap() écrase avec la table la plus fiable
    best = tt.getBestCmap()
    if best:
        cmap.update(best)
    return cmap


def char_to_glyph(tt: TTFont, ch: str, cmap: dict[int, str]) -> str | None:
    """
    Résolution : codepoint direct → décomposition NFD → None.
    Pour les diacritiques IPA combinants, on essaie aussi le premier
    caractère de base de la décomposition (ex. ɫ → l si non présent).
    """
    cp = ord(ch)
    if cp in cmap:
        return cmap[cp]

    # Décomposition NFD : tente le caractère de base uniquement
    nfd = unicodedata.normalize("NFD", ch)
    if nfd != ch and nfd:
        base_cp = ord(nfd[0])
        if base_cp in cmap:
            log.warning("U+%04X '%s' : utilisation du caractère de base NFD U+%04X.",
                        cp, ch, base_cp)
            return cmap[base_cp]

    log.warning("U+%04X '%s' (%s) : glyphe introuvable dans la police.",
                cp, ch, unicodedata.name(ch, "?"))
    return None


# ── 5. Extraction du chemin SVG et des bornes ─────────────────────────────────
def glyph_path_d(tt: TTFont, glyph_name: str) -> str | None:
    gs = tt.getGlyphSet()
    if glyph_name not in gs:
        return None
    pen = SVGPathPen(gs)
    gs[glyph_name].draw(pen)
    cmds = pen.getCommands()
    return cmds if cmds else None   # chaîne vide → None


def glyph_bounds(tt: TTFont, glyph_name: str) -> tuple[float, float, float, float]:
    gs = tt.getGlyphSet()
    pen = BoundsPen(gs)
    gs[glyph_name].draw(pen)
    return pen.bounds or (0.0, 0.0, 1.0, 1.0)   # évite div/0


# ── 6. Transformation géométrique commune ────────────────────────────────────
def common_transform(
    tt: TTFont, glyph_name: str,
    viewbox_em: int = 1000, padding_pct: float = 6.0
) -> tuple[float, float, float, float, float]:
    """
    Retourne (vb_w, vb_h, scale, tx, ty) pour un transform SVG
    translate(tx, ty) scale(scale, -scale).
    Échelle UNIFORME : max(gw, gh) → viewbox_em.
    """
    xmin, ymin, xmax, ymax = glyph_bounds(tt, glyph_name)
    gw = max(1.0, xmax - xmin)
    gh = max(1.0, ymax - ymin)
    pad = viewbox_em * (padding_pct / 100.0)
    vb_w = viewbox_em + 2 * pad
    vb_h = viewbox_em + 2 * pad
    scale = viewbox_em / max(gw, gh)                    # uniforme
    tx = pad + (viewbox_em - gw * scale) / 2 - xmin * scale
    ty = pad + (viewbox_em - gh * scale) / 2 + ymax * scale  # flip Y
    return vb_w, vb_h, scale, tx, ty


# ── 7. Écriture du SVG ────────────────────────────────────────────────────────
def write_svg(
    d_path: str, tt: TTFont, glyph_name: str, out_path: Path,
    viewbox_em: int = 1000, padding_pct: float = 6.0,
    fill_color: str = "#000", inflate_px: int = 0
) -> None:
    vb_w, vb_h, scale, tx, ty = common_transform(
        tt, glyph_name, viewbox_em, padding_pct
    )
    stroke_attrs = (
        f' stroke="{fill_color}" stroke-width="{inflate_px}"'
        f' stroke-linejoin="round" stroke-linecap="round"'
    ) if inflate_px > 0 else ""

    svg = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg width="{vb_w:.0f}" height="{vb_h:.0f}" '
        f'viewBox="0 0 {vb_w:.3f} {vb_h:.3f}" '
        f'xmlns="http://www.w3.org/2000/svg">\n'
        f'  <rect x="0" y="0" width="{vb_w:.3f}" height="{vb_h:.3f}" fill="white"/>\n'
        f'  <g transform="translate({tx:.3f},{ty:.3f}) scale({scale:.5f},{-scale:.5f})">\n'
        f'    <path d="{d_path}" fill="{fill_color}"{stroke_attrs}/>\n'
        f'  </g>\n'
        f'</svg>\n'
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")


def safe_stem(ch: str) -> str:
    """Nom de fichier sûr : caractère si imprimable et non spécial, sinon uXXXX."""
    unsafe = set(r'\/:*?"<>| ')
    return ch if (ch.isprintable() and ch not in unsafe) else f"u{ord(ch):04X}"


# ── 8. Export principal ───────────────────────────────────────────────────────
def export_all(
    font_path: Path, symbols: list[str], outdir: Path,
    viewbox_em: int = 1000, padding_pct: float = 6.0, inflate_px: int = 0,
    fill_color: str = "#000"
) -> tuple[int, int]:
    """
    Exporte les SVG pour tous les symboles. Retourne (ok, miss).
    La police est chargée une seule fois (gain de temps notable sur 40+ symboles).
    """
    tt = TTFont(font_path)
    cmap = build_cmap(tt)

    ok = miss = 0
    for ch in symbols:
        gname = char_to_glyph(tt, ch, cmap)
        if not gname:
            miss += 1
            continue
        d = glyph_path_d(tt, gname)
        if not d:
            log.warning("'%s' → glyphe vide.", ch)
            miss += 1
            continue
        out = outdir / f"{safe_stem(ch)}.svg"
        write_svg(d, tt, gname, out,
                  viewbox_em=viewbox_em, padding_pct=padding_pct,
                  inflate_px=inflate_px, fill_color=fill_color)
        log.info("[OK] U+%04X '%s' → %s", ord(ch), ch, out.name)
        ok += 1

    return ok, miss


# ── 9. Point d'entrée ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    font_path = get_andika_ttf(FONT_DIR, ANDIKA_URL)

    ok, miss = export_all(
        font_path, SYMBOLS, OUTDIR,
        viewbox_em=VIEWBOX_EM,
        padding_pct=PADDING_PCT,
        inflate_px=INFLATE_PX,
        fill_color=FILL_COLOR,
    )
    log.info("Terminé : %d SVG générés, %d manquants.", ok, miss)

    # ── ZIP + téléchargement (Colab) ──────────────────────────────────────────
    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for svg_file in sorted(OUTDIR.glob("*.svg")):
            zf.write(svg_file, arcname=svg_file.name)
    log.info("Archive : %s", ZIP_OUT)

    try:
        from google.colab import files
        files.download(str(ZIP_OUT))
    except ImportError:
        log.info("(Hors Colab — téléchargement manuel depuis %s)", ZIP_OUT)
