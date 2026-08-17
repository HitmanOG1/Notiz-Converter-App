# Notiz & Converter App

[![Build Windows EXE](https://github.com/HitmanOG1/Notiz-Converter-App/actions/workflows/build-windows.yml/badge.svg)](https://github.com/HitmanOG1/Notiz-Converter-App/actions)

Lokale Notizen‑App (Deutsch) mit integriertem Audio/Video‑Konverter für Windows.

Features
- Moderner Desktop‑UI (Flet)
- Markdown‑Editor mit Live‑Vorschau
- Volltextsuche (SQLite FTS5, Fallback auf LIKE)
- Tags, Anhänge und Revisionen
- Optionale Verschlüsselung (Master‑Passwort)
- Konverter für Audio/Video (mp3, wav, mp4, ogg ...) via ffmpeg

Wichtig: ffmpeg wird aus Lizenz‑/Größen‑Gründen nicht im Repo gespeichert. Lade eine passende `ffmpeg.exe` herunter und lege sie neben der fertigen `.exe` oder gib den Pfad in den Einstellungen an.

Schnellstart (Entwicklung)

1) Klone das Repo:

   git clone https://github.com/HitmanOG1/Notiz-Converter-App.git
   cd Notiz-Converter-App

2) Virtuelle Umgebung und Abhängigkeiten:

   python -m venv .venv
   .venv\\Scripts\\activate
   pip install -r requirements.txt

3) App starten:

   python app.py

Build (Windows)

- Die GitHub Actions Workflow `build-windows.yml` versucht bei Push eine EXE mit PyInstaller zu bauen und lädt ein Release‑Draft mit dem Artefakt hoch. Lokales Testen ist empfohlen.
- Um lokal eine EXE zu erzeugen:

   pip install pyinstaller
   pyinstaller --onefile --add-data "ffmpeg.exe;." --name NotizConverterApp app.py

Icon

- Ein SVG‑Icon liegt in `assets/icon.svg`. Ein kleines Hilfs‑Script `tools/generate_icon.py` erzeugt ein `assets/icon.ico` aus der SVG, falls du das lokal möchtest.

Support

Wenn der Workflow fehlschlägt, öffne die Actions‑Seite in deinem Repo, lade die Logs herunter und sende sie mir — ich helfe beim Debuggen.
