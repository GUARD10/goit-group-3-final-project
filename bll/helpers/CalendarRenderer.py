from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, datetime
from io import StringIO
from typing import Iterable

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bll.helpers.DateHelper import DateHelper
from dal.entities.Record import Record


def render_calendar_with_clock(
    records: Iterable[Record],
    *,
    month: int | None = None,
    year: int | None = None,
    now: datetime | None = None,
) -> str:
    now = now or datetime.now()
    today = now.date()
    resolved_year = year or today.year
    resolved_month = month or today.month

    birthday_map = _collect_birthdays(records, resolved_year)

    buffer = StringIO()
    console = Console(
        record=True,
        force_terminal=True,
        color_system="truecolor",
        width=110,
        file=buffer,
    )

    console.print(_build_clock_panel(now))
    console.print(
        _build_calendar_table(
            resolved_month,
            resolved_year,
            today=today,
            birthdays=birthday_map.get(resolved_month, {}),
        )
    )

    console.print(_build_legend_panel())

    return console.export_text(clear=True, styles=True).rstrip()


def _build_clock_panel(now: datetime) -> Panel:
    timestamp = now.strftime("%A, %d %B %Y • %H:%M:%S")
    text = Text(timestamp, style="bold cyan")
    return Panel(
        text,
        title="Current Time",
        padding=(0, 1),
        border_style="cyan",
    )


def _build_calendar_table(
    month: int,
    year: int,
    *,
    today: date,
    birthdays: dict[int, list[str]],
) -> Table:
    table = Table(
        title=f"{calendar.month_name[month]} {year}",
        box=box.SQUARE,
        expand=True,
        show_edge=False,
        show_lines=True,
        header_style="bold white",
    )

    for idx, name in enumerate(calendar.day_abbr):
        style = "bold red" if idx in (5, 6) else "bold white"
        table.add_column(name, justify="center", style=style, no_wrap=True)

    calendar_weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)

    for week in calendar_weeks:
        cells: list[Text] = []
        for day in week:
            if day == 0:
                cells.append(Text(" ", style="dim"))
                continue

            is_today = today.year == year and today.month == month and today.day == day
            labels = birthdays.get(day, [])
            cells.append(_build_day_cell(day, labels, is_today))

        table.add_row(*cells)

    return table


def _build_day_cell(day: int, labels: list[str], is_today: bool) -> Text:
    if is_today:
        base_style = "bold white on dark_green"
    elif labels:
        base_style = "bold magenta"
    else:
        base_style = "white"

    cell = Text(f"{day:2d}", style=base_style, justify="center")

    if labels:
        display_names = labels[:3]
        for name in display_names:
            cell.append("\n")
            cell.append(name, style="magenta")

        if len(labels) > len(display_names):
            remaining = len(labels) - len(display_names)
            cell.append("\n")
            cell.append(f"+{remaining} more", style="dim")

    return cell


def _build_legend_panel() -> Panel:
    grid = Table.grid(padding=(0, 1))
    grid.add_column(style="bold white", justify="right", no_wrap=True)
    grid.add_column()
    grid.add_row("[bold white on dark_green]Today[/]", "Current date")
    grid.add_row("[bold magenta]Birthdays[/]", "Contacts celebrating")
    grid.add_row("[white]Day[/]", "No events")

    return Panel(grid, title="Legend", border_style="white", padding=(0, 1))


def _collect_birthdays(
    records: Iterable[Record],
    year: int,
) -> dict[int, dict[int, list[str]]]:
    birthdays: dict[int, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))

    for record in records:
        bday_field = getattr(record, "birthday", None)
        if not bday_field or not getattr(bday_field, "value", None):
            continue

        original_date = bday_field.value
        adjusted_date = DateHelper.set_date_with_feb_edge_case(original_date, year)

        month_bucket = birthdays[adjusted_date.month]
        month_bucket[adjusted_date.day].append(record.name.value)

    for month_bucket in birthdays.values():
        for day in month_bucket:
            month_bucket[day].sort()

    return {month: dict(days) for month, days in birthdays.items()}
