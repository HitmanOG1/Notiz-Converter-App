#!/usr/bin/env python3
"""
tools/generate_icon.py

Erzeugt assets/icon.ico aus assets/icon.svg (benötigt: cairosvg + pillow)
"""
import os
from pathlib import Path

try:
    from cairosvg import svg2png
    from PIL import Image
except Exception as e:
    print("Fehlende Abhängigkeiten. Installiere: pip install cairosvg pillow")
    raise

BASE = Path(__file__).resolve().parents[1]
SVG = BASE / "assets" / "icon.svg"
ICO = BASE / "assets" / "icon.ico"
PNG_TMP = BASE / "assets" / "icon_tmp.png"

if not SVG.exists():
    print("assets/icon.svg nicht gefunden")
    raise SystemExit(1)

# Render PNG from SVG
svg2png(url=str(SVG), write_to=str(PNG_TMP), output_width=512, output_height=512)

# Create multi-size ICO
png = Image.open(PNG_TMP).convert('RGBA')
sizes = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
icons = [png.resize(s, Image.LANCZOS) for s in sizes]
icons[0].save(ICO, format='ICO', sizes=sizes)

# Cleanup
PNG_TMP.unlink()
print(f"Erstellt: {ICO}")
