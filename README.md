# Notiz & Converter App

[![Build Windows EXE](https://github.com/HitmanOG1/Notiz-Converter-App/actions/workflows/build-windows.yml/badge.svg)](https://github.com/HitmanOG1/Notiz-Converter-App/actions)

Lokale Notizen‑App (Deutsch) mit integriertem Audio/Video‑Konverter für Windows.

Kurzüberblick
- Modernes Desktop‑UI mit Flet
- Markdown‑Editor mit Live‑Vorschau
- Volltextsuche (SQLite FTS5, Fallback auf LIKE)
- Tags, Anhänge und Revisionen
- Optionale Verschlüsselung (Master‑Passwort)
- Konverter für Audio/Video (mp3, wav, mp4, ogg ...) via ffmpeg

Wichtig: ffmpeg wird aus Lizenz‑/Größen‑Gründen nicht im Repo gespeichert. Lade eine passende `ffmpeg.exe` herunter und lege sie neben der fertigen `.exe` oder gib den Pfad in den Einstellungen an.

Inhalt dieses READMEs
- Voraussetzungen
- Installation (Entwicklung)
- App lokal starten (Entwicklung)
- Master‑Passwort (Verschlüsselung)
- EXE (Windows) lokal erzeugen — Schritt für Schritt
- GitHub Actions — wie der CI‑Build funktioniert und wie du Logs/Artefakte findest
- Icon erzeugen
- Häufige Fehler & Troubleshooting
- Code‑Signing (optional)
- Nächste Schritte / Empfehlungen
- Kontakt & Support


Voraussetzungen
- Windows 10/11 (für EXE) oder plattformunabhängig für Entwicklung
- Python 3.10+
- Git
- (Für EXE) PyInstaller
- ffmpeg (ffmpeg.exe) für Konvertierungen


Installation (Entwicklung)
1) Repo klonen

   git clone https://github.com/HitmanOG1/Notiz-Converter-App.git
   cd Notiz-Converter-App

2) Virtuelle Umgebung erstellen und aktivieren

   python -m venv .venv
   .venv\Scripts\activate

3) Abhängigkeiten installieren

   pip install --upgrade pip
   pip install -r requirements.txt


App lokal starten (Entwicklung)

   python app.py

Die App öffnet ein Flet Desktop‑Fenster. Falls Module fehlen, installiere sie mit pip.


Master‑Passwort (Verschlüsselung)
- Die App unterstützt optionale Verschlüsselung für Notizen.
- Ein Master‑Passwort wird sicher per PBKDF2 + Fernet abgeleitet und in der lokalen DB als Salt/Verifier gespeichert.

Master setzen (einmalig):

   from crypto import generate_master
   generate_master("DeinSicheresPasswort")

Verifizieren / Fernet erhalten (im Code):

   from crypto import verify_master, get_fernet
   verify_master("DeinSicheresPasswort")
   f = get_fernet("DeinSicheresPasswort")

WICHTIG: Wenn du das Master‑Passwort verlierst, sind verschlüsselte Notizen NICHT wiederherstellbar.


EXE (Windows) lokal erzeugen — Schritt für Schritt

1) Voraussetzungen
- Python 3.10+ installiert & aktivierte virtuelle Umgebung
- pyinstaller installiert: `pip install pyinstaller`
- ffmpeg.exe heruntergeladen und verfügbar (siehe unten)

2) ffmpeg herunterladen
- Empfohlene Quellen (statische Builds):
  - https://www.gyan.dev/ffmpeg/builds/
  - https://ffmpeg.org/download.html
- Entpacke das Archiv und kopiere die ffmpeg.exe in das Projektverzeichnis (oder merke dir den Pfad).

3) EXE bauen (einfach)

   pyinstaller --onefile --add-data "ffmpeg.exe;." --noconfirm --name NotizConverterApp app.py

Erläuterung wichtiger Flags:
- --onefile: erzeugt eine einzelne ausführbare Datei (.exe)
- --add-data "ffmpeg.exe;.": packt ffmpeg.exe in das Bundle (Windows: getrennte Pfadangabe beachten)
- --noconfirm: überschreibt alte Builds ohne Nachfrage
- --name: Name der Ausgabedatei

4) Ergebnis
- Die fertige EXE liegt in `dist\NotizConverterApp.exe`.
- Teste die EXE lokal: kopiere bei Bedarf eine ffmpeg.exe ins gleiche Verzeichnis wie die EXE oder stelle sicher, dass ffmpeg im PATH ist.
- Starte die EXE und prüfe: Editor öffnen, Notiz speichern, Konvertierung mit einer kurzen Testdatei.


Optional: Icon einbinden
- Wenn du eine .ico einbinden möchtest, erzeuge `assets/icon.ico` aus `assets/icon.svg`:

   pip install cairosvg pillow
   python tools/generate_icon.py

- Beim Build mit PyInstaller kannst du das Icon angeben:

   pyinstaller --onefile --icon=assets/icon.ico --add-data "ffmpeg.exe;." --noconfirm --name NotizConverterApp app.py


GitHub Actions — CI Build & Artefakte

Was der Workflow macht
- Läuft bei Push auf `main` oder `master`
- Installiert Python, Abhängigkeiten und PyInstaller
- Versucht, einen statischen ffmpeg‑Build herunterzuladen und ffmpeg.exe zu extrahieren
- Baut mit PyInstaller eine Einzeldatei‑EXE
- Packt EXE + ffmpeg in ein ZIP und erstellt einen Release‑Draft mit dem ZIP als Asset

Logs & Artefakte ansehen
1) Gehe zur Actions‑Seite des Repos: https://github.com/HitmanOG1/Notiz-Converter-App/actions
2) Wähle den letzten Run des Workflows `Build Windows EXE and Release`
3) Öffne die Schritte und schaue dir die ausführlichen Logs an. Bei Fehlern kopiere die relevanten Logabschnitte hierher — ich helfe beim Interpretieren.
4) Wenn der Workflow erfolgreich war, findest du das ZIP als Release‑Asset im Draft Release (Releases → Drafts) oder als herunterladbares Artefakt im Workflow‑Run.

Tipps für Debugging von Actions‑Builds
- Fehlender ffmpeg: Workflow konnte die ZIP nicht entpacken oder ffmpeg.exe nicht finden. Prüfe den Schritt "Download ffmpeg" in den Logs.
- PyInstaller Fehlermeldungen: oft fehlen Module oder Hooks (z. B. Flet). Suche nach Tracebacks in den Logs. Häufige Lösung: explizite hidden‑imports oder zusätzliche Dateien via --add-data.
- Antivirus / Windows Defender: kann die erzeugte EXE blockieren. Signieren hilft (siehe weiter unten).


Häufige Fehler & Troubleshooting

1) Fehler: "ffmpeg nicht gefunden"
- Ursache: ffmpeg.exe nicht im PATH oder nicht neben der EXE
- Lösung: lade ffmpeg herunter und lege ffmpeg.exe ins gleiche Verzeichnis wie die EXE oder setze PATH.

2) Fehler beim Import von cryptography oder PBKDF2
- Ursache: fehlende Abhängigkeiten oder veraltete wheel/Compiler auf Windows
- Lösung: pip install --upgrade pip setuptools wheel; pip install -r requirements.txt

3) PyInstaller: fehlende Modules / "ModuleNotFoundError"
- Ursache: PyInstaller verpackt nicht automatisch manche dynamisch geladene Module
- Lösung: Füge hidden-imports hinzu, z. B. `pyinstaller --onefile app.py --hidden-import modulename --add-data "ffmpeg.exe;." --name NotizConverterApp` oder erstelle eine spec‑Datei und ergänze.

4) FTS5 nicht verfügbar in SQLite
- Symptom: Suche funktioniert nicht mit FTS5 und fällt zurück auf LIKE
- Hinweis: Windows‑Python hat meist FTS5; falls nicht, ist das FTS5‑Fallback bereits implementiert.

5) Workflow schlägt fehl, weil ffmpeg nicht extrahiert werden kann
- Prüfe den Schritt "Download ffmpeg" in Actions logs. Manchmal ändert sich die Struktur der ZIP (Unterordner). Ich kann den Workflow anpassen, wenn du mir die Logs zeigst.

6) Antivirus markiert EXE als Malware
- Signiere die EXE (Code Signing Certificate) oder teste lokal/externe Maschinen; False‑Positives sind bei selbstgebauten EXEs häufig.


Code Signing (optional, empfohlen für Releases)
- Für geringere False‑Positives und mehr Vertrauen: erwirb ein Code Signing Zertifikat und signiere die EXE.
- Windows: SignTool.exe (Teil des Windows SDK) oder SignTool via Publisher

Signieren lokal (kurz):
- Installiere Windows SDK (SignTool)
- Beispiel: signtool sign /a /tr http://timestamp.digicert.com /td sha256 /fd sha256 "dist\NotizConverterApp.exe"


Nächste Schritte / Empfehlungen
- Teste erstmal lokal: `python app.py` — das ist wertvoll, bevor du EXE‑Bündel baust.
- Wenn der Actions‑Build fehlschlägt: sende mir die Log‑Abschnitte. Ich analysiere und gebe konkrete Fixes.
- Ich kann das Workflow‑Script weiter anpassen (z. B. robustere ffmpeg‑Suche, weitere Release‑Optionen, Signieren mithilfe eines Secret/Signer Action).


Kontakt & Support
Wenn du beim lokalen Build oder bei Workflow‑Fehlern Unterstützung brauchst, poste hier die Fehlerausgabe oder den Link zum fehlschlagenden Workflow‑Run. Ich helfe beim Debugging.


---

Repo: https://github.com/HitmanOG1/Notiz-Converter-App
