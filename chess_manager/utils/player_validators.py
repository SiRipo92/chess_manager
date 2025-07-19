from datetime import datetime
import re

DATE_FORMAT = "%Y-%m-%d"
MIN_YEAR = 1915
MAX_DATE_YEAR = datetime.now().year


def is_valid_birthdate(birthdate: str) -> bool:
    """
    Valide une date de naissance :
    - Format YYYY-MM-DD
    - Née avant aujourd'hui
    - Année comprise entre MIN_YEAR et MAX_DATE_YEAR
    """
    try:
        birth = datetime.strptime(birthdate, DATE_FORMAT).date()
        today = datetime.today().date()

        # Must be strictly in the past
        if birth >= today:
            return False
        if birth.year < MIN_YEAR or birth.year > MAX_DATE_YEAR:
            return False
        return True
    except ValueError:
        return False


def is_valid_name(name: str) -> bool:
    """
    Valide que le nom/prénom :
    - Ne contient pas de chiffres
    - Ne contient pas de caractères spéciaux inhabituels
    - Autorise les apostrophes, accents, traits d’union
    """
    return bool(re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$", name.strip()))


def is_valid_id(national_id: str) -> bool:
    """
    Vérifie que l'identifiant national est composé de 2 lettres suivies de 5 chiffres.
    Exemple valide : AB12345
    """
    return bool(re.match(r"^[A-Za-z]{2}\d{5}$", national_id))
