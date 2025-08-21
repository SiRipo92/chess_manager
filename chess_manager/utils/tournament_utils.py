import os
import re
import unicodedata
from datetime import datetime
import fnmatch
from typing import Optional

import questionary
from rich.console import Console

console = Console()

def datetime_formatting(timestamp:str | None):
    """Format the timestamp in a readable format"""
    if not timestamp:
        return ""
    try:
        # Works with 'YYYY-MM-DDTHH:MM:SS' and with microseconds
        datetime_obj = datetime.fromisoformat(timestamp)
        return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        # if already friendly, just return
        return timestamp.replace("T", " ")

def slugify_location(loc: str) -> str:
    """Take the user input and strip it and lowercase it for file naming"""
    s = loc.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def generate_tournament_name(location: str, existing_tournaments: list) -> str:
    """Uses slugify location to generate a tournament name"""
    slug = slugify_location(location)
    date_part = datetime.now().strftime("%Y-%m-%d")
    pattern = re.compile(r"^tournament_(\d+)_")
    max_id = 0
    for t in existing_tournaments:
        name = ""
        if isinstance(t, dict):
            name = t.get("name", "")
        elif hasattr(t, "name"):
            name = getattr(t, "name")
        m = pattern.match(name)
        if m:
            try:
                val = int(m.group(1))
                if val > max_id:
                    max_id = val
            except ValueError:
                continue
    next_id = max_id + 1
    return f"tournament_{next_id}_{slug}_{date_part}"


def browse_for_file(start_dir: str = ".", file_glob: str = "*.json") -> Optional[str]:
    """
    Minimal CLI browser to navigate directories and select a file matching `file_glob`.
    Returns the absolute path or None if cancelled.
    """
    current = os.path.abspath(start_dir)
    while True:
        try:
            entries = list(os.scandir(current))
        except PermissionError:
            console.print(f"[red]Permission refusée sur {current}, remontée automatique.[/red]")
            current = os.path.dirname(current)
            continue

        dirs = sorted([e.name for e in entries if e.is_dir()])
        files = sorted([e.name for e in entries if e.is_file() and fnmatch.fnmatch(e.name, file_glob)])

        choices = []
        if os.path.dirname(current) != current:
            choices.append({"name": "../ (remonter)", "value": {"action": "up"}})
        for d in dirs:
            choices.append(
                {"name": f"[DIR] {d}", "value": {"action": "cd", "path": os.path.join(current, d)}}
            )
        for f in files:
            choices.append(
                {"name": f, "value": {"action": "select", "path": os.path.join(current, f)}}
            )
        choices.append({"name": "Annuler", "value": {"action": "cancel"}})

        prompt_label = f"Parcourir : {current} (filtre: {file_glob})"
        selection = questionary.select(prompt_label, choices=choices, use_shortcuts=True).ask()
        if not selection:
            return None

        act = selection.get("action")
        if act == "up":
            current = os.path.dirname(current)
        elif act == "cd":
            current = selection["path"]
        elif act == "select":
            return selection["path"]
        elif act == "cancel":
            return None
