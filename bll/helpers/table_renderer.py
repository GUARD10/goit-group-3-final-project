from __future__ import annotations

from datetime import datetime
from io import StringIO
from typing import Iterable

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from dal.entities.note import Note
from dal.entities.record import Record
from dal.entities.tag import Tag


def render_contacts_table(
    records: Iterable[Record], *, title: str | None = None
) -> str:
    table = Table(
        title=title or "Contacts",
        box=box.SQUARE,
        expand=True,
        highlight=True,
        show_lines=True,
        header_style="bold white",
    )

    table.add_column("Name", style="bold cyan", no_wrap=True)
    table.add_column("Phone", style="green", overflow="fold")
    table.add_column("Email", style="magenta", overflow="fold")
    table.add_column("Birthday", style="yellow", no_wrap=True)
    table.add_column("Address", style="blue", overflow="fold")

    for record in records:
        table.add_row(
            record.name.value,
            _join_field_values([phone.value for phone in record.phones]),
            _join_field_values([email.value for email in record.emails]),
            str(record.birthday) if record.birthday else "—",
            str(record.address) if record.address else "—",
        )

    return _render_table(table)


def render_contact_details(record: Record, *, title: str | None = None) -> str:
    resolved_title = title or f"Contact: {record.name.value}"
    return render_contacts_table([record], title=resolved_title)


def render_notes_table(notes: Iterable[Note], *, title: str | None = None) -> str:
    table = Table(
        title=title or "Notes",
        box=box.SQUARE,
        expand=True,
        highlight=True,
        show_lines=True,
        header_style="bold white",
    )

    table.add_column("Name", style="bold cyan", no_wrap=True)
    table.add_column("Title", style="bold green", overflow="fold")
    table.add_column("Tags", style="magenta", overflow="fold")
    table.add_column("Created", style="yellow", no_wrap=True)
    table.add_column("Updated", style="yellow", no_wrap=True)
    table.add_column("Content", style="dim", overflow="fold")

    for note in notes:
        created_at = getattr(note, "created_at", None)
        updated_at = getattr(note, "updated_at", None)
        tags = getattr(note, "tags", [])

        table.add_row(
            note.name.value,
            str(note.title),
            _format_tags(tags),
            _format_datetime(note, created_at),
            _format_datetime(note, updated_at),
            _format_content(str(note.content)),
        )

    return _render_table(table)


def render_note_details(note: Note, *, title: str | None = None) -> str:
    resolved_title = title or f"Note: {note.title.value}"
    return render_notes_table([note], title=resolved_title)


def _render_table(table: Table) -> str:
    buffer = StringIO()
    console = Console(
        record=True,
        force_terminal=True,
        color_system="truecolor",
        width=120,
        file=buffer,
    )
    console.print(table)
    return console.export_text(clear=True, styles=True).rstrip()


def _join_field_values(values: list[str]) -> str:
    clean = [value for value in values if value]
    return "\n".join(clean) if clean else "—"


def _format_tags(tags: Iterable[Tag]) -> Text:
    tag_list = list(tags)
    if not tag_list:
        return Text("—", style="dim")

    text = Text()
    for idx, tag in enumerate(tag_list):
        style = f"bold {tag.color}" if tag.color else "bold magenta"
        text.append(tag.value, style=style)
        if idx < len(tag_list) - 1:
            text.append(", ", style="dim")
    return text


def _format_content(content: str) -> Text:
    if not content:
        return Text("—", style="dim")
    lines = [line.rstrip() for line in content.splitlines()]
    normalized = "\n".join(lines)
    return Text(normalized)


def _format_datetime(note: Note, value: datetime | None) -> str:
    if not value:
        return "—"
    date_format = getattr(note, "DATETIME_FORMAT", Note.DATETIME_FORMAT)
    return value.strftime(date_format)
