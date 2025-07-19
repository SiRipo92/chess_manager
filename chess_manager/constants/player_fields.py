from chess_manager.utils.player_validators import is_valid_birthdate, is_valid_id, is_valid_name

FIELD_LAST_NAME = "Nom de famille"
FIELD_FIRST_NAME = "Prénom"
FIELD_BIRTHDATE = "Date de naissance"
FIELD_NATIONAL_ID = "Identifiant national"

FIELD_CHOICES = [
    FIELD_LAST_NAME,
    FIELD_FIRST_NAME,
    FIELD_BIRTHDATE,
    FIELD_NATIONAL_ID,
]

# For display in recap table or validation mapping
FIELD_LABELS = {
    "last_name": FIELD_LAST_NAME,
    "first_name": FIELD_FIRST_NAME,
    "birthdate": FIELD_BIRTHDATE,
    "national_id": FIELD_NATIONAL_ID,
}

# For input validation mapping
VALIDATION_MAP = {
    FIELD_LAST_NAME: is_valid_name,
    FIELD_FIRST_NAME: is_valid_name,
    FIELD_BIRTHDATE: is_valid_birthdate,
    FIELD_NATIONAL_ID: is_valid_id,
}
