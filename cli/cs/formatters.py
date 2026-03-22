from __future__ import annotations

import json
from typing import Any

from rich import box
from rich.console import Console
from rich.table import Table


console = Console(highlight=False, color_system=None)


def print_json(data: Any) -> None:
    console.print(json.dumps(data, indent=2, ensure_ascii=True, default=_json_default))


def print_table(title: str, headers: list[str], rows: list[list[Any]]) -> None:
    table = Table(title=title, box=box.ASCII, show_lines=False)
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*["" if value is None else str(value) for value in row])
    console.print(table)


def print_mapping(title: str, values: dict[str, Any]) -> None:
    rows = []
    for key, value in values.items():
        rows.append([key, _stringify(value)])
    print_table(title, ["Field", "Value"], rows)


def shorten(value: Any, *, width: int = 50) -> str:
    text = _stringify(value)
    if len(text) <= width:
        return text
    return text[: max(0, width - 3)] + "..."


def _stringify(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=True, default=_json_default)
    if value is None:
        return ""
    return str(value)


def _json_default(value: Any) -> str:
    return str(value)
