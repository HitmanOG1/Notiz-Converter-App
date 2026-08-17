import flet as ft
from flet import Page, Column, Row, TextField, ElevatedButton, Text, ListView, Card, icons, Checkbox, FilePicker, FilePickerResultEvent, ProgressBar, Dropdown, DropdownItem
import db
import crypto
import converter
import json
import os

# Global state
STATE = {
    "selected_note": None,
    "master_verified": False,
    "fernet": None,
    "ffmpeg_path": None
}


def main(page: Page):
    page.title = "Notiz & Converter App"
    page.window_width = 1200
    page.window_height = 760
    page.theme_mode = ft.ThemeMode.DARK

    # Suche und Notizenliste
    search = TextField(label="Suche", expand=True)
    notes_list = ListView(expand=True, spacing=6)

    def refresh_list(e=None):
        notes_list.controls.clear()
        q = (search.value or "").strip()
        if q:
            items = db.search_notes(q)
        else:
            items = db.list_notes(500)
        for it in items:
            title = it.get("title") or "(ohne Titel)"
            encrypted = it.get("encrypted", 0)
            card = Card(ft.Container(ft.Row([
                Text(title, expand=True),
                Text(it.get("tags") or "", color=ft.colors.GRAY),
                ft.Icon(icons.LOCK) if encrypted else ft.Icon(icons.NOTE)
            ], vertical_alignment="center")), padding=8, on_click=lambda e, nid=it["id"]: load_note(nid))
            notes_list.controls.append(card)
        page.update()

    def new_note(e=None):
        STATE["selected_note"] = None
        title_field.value = ""
        editor.value = ""
        tags_field.value = ""
        encrypted_checkbox.value = True
        preview_markdown.value = ""
        refresh_list()
        page.update()

    def load_note(note_id: int):
        row = db.get_note(note_id)
        if not row:
            return
        if row.get("encrypted"):
            if not STATE["master_verified"]:
                page.dialog = password_dialog
                password_field.value = ""
                page.dialog.open = True
                page.update()
                page.client_storage.set("pending_load", str(note_id))
                return
            body = crypto.decrypt_bytes(row["body"], STATE["fernet"]).decode("utf-8")
        else:
            try:
                body = row["body"].decode("utf-8")
            except Exception:
                body = str(row["body"]) if row["body"] is not None else ""
        STATE["selected_note"] = note_id
        title_field.value = row.get("title") or ""
        editor.value = body
        tags_field.value = row.get("tags") or ""
        encrypted_checkbox.value = bool(row.get("encrypted", 0))
        preview_markdown.value = editor.value
        page.update()

    def save_note(e=None):
        title = (title_field.value or "").strip()
        body = editor.value or ""
        tags = [t.strip() for t in (tags_field.value or "").split(",") if t.strip()]
        encrypted = encrypted_checkbox.value
        body_bytes = body.encode("utf-8")
        if encrypted:
            if not STATE["master_verified"]:
                page.dialog = password_dialog
                password_field.value = ""
                page.dialog.open = True
                page.update()
                page.client_storage.set("pending_save", json.dumps({"title": title, "body": body, "tags": tags, "enc": True}))
                return
            body_bytes = crypto.encrypt_bytes(body_bytes, STATE["fernet"])
        if STATE["selected_note"]:
            db.update_note(STATE["selected_note"], title, body_bytes, tags, encrypted)
        else:
            nid = db.add_note(title, body_bytes, tags, encrypted)
            STATE["selected_note"] = nid
        refresh_list()
        page.snack_bar = ft.SnackBar(Text("Gespeichert"))
        page.snack_bar.open = True
        page.update()

    def delete_current(e=None):
        if STATE["selected_note"]:
            db.delete_note(STATE["selected_note"])
            new_note()
            refresh_list()

    # Editor und Vorschau
    title_field = TextField(label="Titel", expand=True)
    editor = TextField(label="Inhalt (Markdown)", multiline=True, expand=True)
    preview_markdown = ft.Markdown(value="", expand=True, selectable=True)
    tags_field = TextField(label="Tags (Komma getrennt)", expand=True)
    encrypted_checkbox = Checkbox(label="Verschlüsseln (Master‑Passwort)", value=True)

    def on_edit(e):
        preview_markdown.value = editor.value or ""
        page.update()

    editor.on_change = on_edit

    # Passwort‑Dialog
    password_field = TextField(label="Master‑Passwort", password=True)

    def verify_and_continue(e):
        pw = password_field.value or ""
        if not crypto.verify_master(pw):
            page.dialog = ft.AlertDialog(title=Text("Falsches Passwort"), content=Text("Das Master‑Passwort ist falsch."))
            page.dialog.open = True
            page.update()
            return
        STATE["fernet"] = crypto.get_fernet(pw)
        STATE["master_verified"] = True
        page.dialog.open = False
        page.update()
        pending_load = page.client_storage.get("pending_load")
        if pending_load:
            page.client_storage.remove("pending_load")
            load_note(int(pending_load))
        pending_save = page.client_storage.get("pending_save")
        if pending_save:
            page.client_storage.remove("pending_save")
            obj = json.loads(pending_save)
            body_bytes = obj["body"].encode("utf-8")
            body_bytes = crypto.encrypt_bytes(body_bytes, STATE["fernet"])
            nid = db.add_note(obj["title"], body_bytes, obj["tags"], True)
            STATE["selected_note"] = nid
            refresh_list()
        page.update()

    password_dialog = ft.AlertDialog(
        title=Text("Master‑Passwort erforderlich"),
        content=Column([password_field]),
        actions=[ElevatedButton("Bestätigen", on_click=verify_and_continue), ElevatedButton("Abbrechen", on_click=lambda e: setattr(page, "dialog", None))],
        actions_alignment=ft.MainAxisAlignment.END
    )

    # Konverter Dialog
    file_picker = FilePicker(on_result=lambda e: None)
    page.overlay.append(file_picker)
    input_file = TextField(label="Eingabedatei", expand=True)
    output_file = TextField(label="Ausgabedatei", expand=True)
    format_select = Dropdown(label="Format", width=200, value="mp3", options=[DropdownItem("mp3"), DropdownItem("wav"), DropdownItem("mp4"), DropdownItem("ogg")])
    conv_progress = ProgressBar(width=300, value=0)

    def on_file_result(e: FilePickerResultEvent):
        if e.files:
            input_file.value = e.files[0].path
            base, _ = os.path.splitext(e.files[0].path)
            output_file.value = base + "." + (format_select.value or "mp3")
            page.update()

    file_picker.on_result = on_file_result

    def start_convert(e):
        inp = (input_file.value or "").strip()
        out = (output_file.value or "").strip()
        if not inp or not out:
            page.snack_bar = ft.SnackBar(Text("Bitte Eingabe und Ausgabe angeben"))
            page.snack_bar.open = True
            page.update()
            return
        conv_progress.value = 0
        page.update()

        def progress_cb(info, percent):
            if percent is not None:
                conv_progress.value = percent / 100.0
                page.update()

        def run():
            try:
                converter.convert(inp, out, ffmpeg_path=STATE["ffmpeg_path"], progress_callback=progress_cb)
                page.snack_bar = ft.SnackBar(Text("Konvertierung fertig"))
            except Exception as ex:
                page.snack_bar = ft.SnackBar(Text("Fehler: " + str(ex)))
            page.snack_bar.open = True
            page.update()

        import threading
        threading.Thread(target=run, daemon=True).start()

    conv_dialog = ft.AlertDialog(
        title=Text("Konverter"),
        content=Column([
            Row([input_file, ElevatedButton("Öffnen...", on_click=lambda e: file_picker.pick_files())]),
            Row([output_file, format_select]),
            conv_progress
        ]),
        actions=[ElevatedButton("Start", on_click=start_convert), ElevatedButton("Schließen", on_click=lambda e: setattr(page, "dialog", None))],
        actions_alignment=ft.MainAxisAlignment.END
    )

    # Buttons
    new_btn = ElevatedButton("Neu", on_click=new_note, icon=icons.ADD)
    save_btn = ElevatedButton("Speichern", on_click=save_note, icon=icons.SAVE)
    del_btn = ElevatedButton("Löschen", on_click=delete_current, icon=icons.DELETE)
    conv_btn = ElevatedButton("Converter", on_click=lambda e: (setattr(page, "dialog", conv_dialog), setattr(page.dialog, "open", True), page.update()), icon=icons.SYNC)

    left_col = Column([Row([search, new_btn]), notes_list], width=320, expand=False)
    mid_col = Column([title_field, Row([tags_field, encrypted_checkbox]), editor, Row([save_btn, del_btn, conv_btn])], expand=True)
    right_col = Column([Text("Vorschau"), preview_markdown], width=380)

    page.add(ft.Row([left_col, mid_col, right_col], expand=True))
    page.update()

    # Initial
    page.client_storage.set("pending_load", "")
    page.client_storage.set("pending_save", "")
    refresh_list()


if __name__ == "__main__":
    ft.app(target=main)
