"""
Clés internes pour identifier les menus dans le code.
Utilisées pour le routage logique et les correspondances.
"""

from chess_manager.constants.player_fields import PLAYER_BIO_MODIFICATION_CHOICES

STARTING_MENU = "starting_menu"
CLUB_MANAGEMENT_MENU = "club_management_menu"
PLAYER_MANAGEMENT_MENU = "player_management_menu"
TOURNAMENT_MANAGEMENT_MENU = "tournament_management_menu"
PLAYER_SORT_FILTER_MENU = "player_sort_filter_menu"
PLAYER_FILE_MENU = "player_file_options"
PLAYER_MODIFICATION_VALIDATION_MENU = "player_modification_validation_menu"
PLAYER_FILE_RETURN_MENU = "player_modification_return_menu"
ADD_NEW_PLAYER_MENU = "add_new_player_menu"
PLAYER_FILE_BIO_MODIFICATIONS_MENU = "player_bio_modify_menu"
# ─────────────────────────────────────────────────────────
# MENUS GÉNÉRIQUES ET VALIDATION
# ─────────────────────────────────────────────────────────

YES_NO_MENU = "yes_no_menu"
CONFIRM_CANCEL_MENU = "confirm_cancel_menu"

# ─────────────────────────────────────────────────────────
# MENUS LIÉS AUX JOUEURS
# ─────────────────────────────────────────────────────────
CONFIRM_NEW_PLAYER_MENU = "confirm_new_player_menu"
CONFIRM_PLAYER_EDIT_MENU = "confirm_player_edit_menu"


# ─────────────────────────────────────────────────────────
# MENUS DE SEQUENCES D'ECHAPPEMENT
# ─────────────────────────────────────────────────────────
SORT_PLAYERS_ESCAPE_SEQUENCE_MENU = "escape_sort_player_filter_menu"
PLAYER_FILE_ESCAPE_SEQUENCE = "escape_player_file_menu"
PLAYER_MODIFICATION_ESCAPE_SEQUENCE = "escape_player_modification_menu"