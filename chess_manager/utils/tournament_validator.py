import re
from datetime import datetime
from chess_manager.constants.datetime_formats import DATE_FORMAT


def is_valid_location(location: str) -> bool:
    """"Vérifie que le nom de lieu est non vide et alphabétique (espaces autorisés)."""
    return bool(re.fullmatch(r"[A-Za-zÀ-ÿ\s\-]+", location.strip()))


def is_valid_date(date_str: str) -> bool:
    """Vérifie que la date est au format YYYY-MM-DD et est une date valide."""
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except ValueError:
        return False


def is_valid_number_of_rounds(n: str) -> bool:
    """Vérifie que le nombre de rounds est un entier positif."""
    return n.isdigit() and 1 <= int(n) <= 20  # max 20 for sanity
