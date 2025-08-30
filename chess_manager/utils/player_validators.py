from datetime import datetime
import re

DATE_FORMAT = "%Y-%m-%d"
MIN_YEAR = 1915
MAX_DATE_YEAR = datetime.now().year


def is_valid_birthdate(birthdate: str) -> bool:
    """
    Validate a birthdate string.

    Rules:
      - Must match YYYY-MM-DD.
      - Must be strictly before today (no future/today dates).
      - Year must be between MIN_YEAR and MAX_DATE_YEAR (inclusive of bounds).

    Returns:
      bool: True if valid, False otherwise.
    """
    try:
        birth = datetime.strptime(birthdate, DATE_FORMAT).date()
        today = datetime.today().date()

        # Must be strictly in the past
        if birth >= today:
            return False
        # Enforce reasonable year bounds
        if birth.year < MIN_YEAR or birth.year > MAX_DATE_YEAR:
            return False
        return True
    except ValueError:
        return False


def is_valid_name(name: str) -> bool:
    """
    Validate that a first/last name:
      - Contains no digits.
      - Contains no unusual special characters.
      - Allows apostrophes, accents, spaces, and hyphens.

    Returns:
      bool: True if valid, False otherwise.
    """
    # Accept letters (ASCII + common accents), apostrophes, spaces, and hyphens
    return bool(re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$", name.strip()))


def is_valid_id(national_id: str) -> bool:
    """
    Validate the national ID format: two letters followed by five digits.

    Example:
      - Valid: AB12345
      - Invalid: A12345, ABC1234, ab-12345

    Returns:
      bool: True if valid, False otherwise.
    """
    return bool(re.match(r"^[A-Za-z]{2}\d{5}$", national_id))
