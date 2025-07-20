"""
Maps internal menu slugs (keys) to their associated option lists.
Used for dynamically rendering choices with Questionary.
"""

import os

from chess_manager.constants.player_fields import PLAYER_BIO_MODIFICATION_CHOICES
from chess_manager.constants.navigation.menu_keys import (
    STARTING_MENU,
    CLUB_MANAGEMENT_MENU,
    PLAYER_MANAGEMENT_MENU,
    TOURNAMENT_MANAGEMENT_MENU,
    PLAYER_SORT_FILTER_MENU,
    PLAYER_FILE_MENU,
    PLAYER_MODIFICATION_VALIDATION_MENU,
    YES_NO_MENU,
    CONFIRM_CANCEL_MENU,
    CONFIRM_NEW_PLAYER_MENU,
    CONFIRM_PLAYER_EDIT_MENU,
    PLAYER_FILE_BIO_MODIFICATIONS_MENU
)

from chess_manager.constants.navigation.labels import (
    # Generic menus
    BLACK_OR_WHITE_CHOICES,
    CONFIRMATION_CHOICES,

    # GO BACK menu option
    OPTION_GO_BACK,

    # Contextual menus
    CONFIRM_PLAYER_MODIFICATION,
    CONFIRM_NEW_PLAYER,

    # Starting Menu
    OPTION_CREATE_NEW_PLAYERS_FILE,
    OPTION_IMPORT_FILE,
    OPTION_QUIT_PROGRAM,

    # Club Management Menu
    OPTION_MANAGE_PLAYERS,
    OPTION_MANAGE_TOURNAMENTS,

    # Player Management Menu
    OPTION_SHOW_PLAYERS,
    OPTION_SORT_PLAYERS,
    OPTION_SHOW_PLAYER_FILE,
    OPTION_ADD_NEW_PLAYER,

    # Tournament Menu
    OPTION_VIEW_ONGOING_TOURNAMENTS,
    OPTION_CREATE_NEW_TOURNAMENT,
    OPTION_FINALIZE_TOURNAMENT,
    OPTION_SHOW_WINNERS,

    # Sort / Filter Menu
    OPTION_SORT_BY_NAME_ASC,
    OPTION_SORT_BY_NAME_DESC,
    OPTION_SORT_BY_RANKING,
    OPTION_SEARCH_BY_ID,
    OPTION_SEARCH_BY_NAME,
    OPTION_VIEW_PLAYER_FILE,

    # Player File / Modification
    OPTION_MODIFY_PLAYER_FIELD,

    # Escape sequences
    STANDARD_ESCAPE_SEQUENCE,
    PLAYER_FILE_ESCAPE_SEQUENCE,
    NEW_PLAYER_ESCAPE_SEQUENCE,
    OPTION_CANCEL_PLAYER_MODIFICATION,
)

MENU_STRUCTURE = {

    STARTING_MENU: [
        OPTION_CREATE_NEW_PLAYERS_FILE,
        OPTION_IMPORT_FILE,
        OPTION_QUIT_PROGRAM,
    ],

    CLUB_MANAGEMENT_MENU: [
        OPTION_MANAGE_PLAYERS,
        OPTION_MANAGE_TOURNAMENTS,
        *STANDARD_ESCAPE_SEQUENCE,
    ],

    PLAYER_MANAGEMENT_MENU: [
        OPTION_SHOW_PLAYERS,
        OPTION_SORT_PLAYERS,
        OPTION_SHOW_PLAYER_FILE,
        OPTION_ADD_NEW_PLAYER,
        *STANDARD_ESCAPE_SEQUENCE,
    ],

    TOURNAMENT_MANAGEMENT_MENU: [
        OPTION_VIEW_ONGOING_TOURNAMENTS,
        OPTION_CREATE_NEW_TOURNAMENT,
        OPTION_FINALIZE_TOURNAMENT,
        OPTION_SHOW_WINNERS,
        *STANDARD_ESCAPE_SEQUENCE,
    ],

    PLAYER_SORT_FILTER_MENU: [
        OPTION_SORT_BY_NAME_ASC,
        OPTION_SORT_BY_NAME_DESC,
        OPTION_SORT_BY_RANKING,
        OPTION_SEARCH_BY_ID,
        OPTION_SEARCH_BY_NAME,
        OPTION_VIEW_PLAYER_FILE,
        *PLAYER_FILE_ESCAPE_SEQUENCE,
    ],

    PLAYER_FILE_MENU: [
        OPTION_MODIFY_PLAYER_FIELD,
        *PLAYER_FILE_ESCAPE_SEQUENCE,
    ],

    PLAYER_MODIFICATION_VALIDATION_MENU: [
        *CONFIRM_PLAYER_MODIFICATION,
        OPTION_CANCEL_PLAYER_MODIFICATION
    ],

    CONFIRM_NEW_PLAYER_MENU: [
        *CONFIRM_NEW_PLAYER,
        *NEW_PLAYER_ESCAPE_SEQUENCE
    ],

    YES_NO_MENU: [
        *BLACK_OR_WHITE_CHOICES,
    ],

    CONFIRM_CANCEL_MENU: [
        *CONFIRMATION_CHOICES,
    ],

    CONFIRM_PLAYER_EDIT_MENU: [
        *CONFIRM_PLAYER_MODIFICATION,
    ],

    PLAYER_FILE_ESCAPE_SEQUENCE: [
        *PLAYER_FILE_ESCAPE_SEQUENCE
    ],

    PLAYER_FILE_BIO_MODIFICATIONS_MENU: [
        *PLAYER_BIO_MODIFICATION_CHOICES,
        OPTION_GO_BACK
    ]
}

def get_dynamic_starting_menu(base_dir: str = "data/players") -> list[str]:
    """
    Construit dynamiquement le menu de démarrage en listant les répertoires de joueurs
    et en ajoutant les options fixes.
    """
    dynamic_folders = []
    if os.path.exists(base_dir):
        dynamic_folders = sorted([
            name for name in os.listdir(base_dir)
            if os.path.isdir(os.path.join(base_dir, name))
        ])

    return [
        *dynamic_folders,
        OPTION_CREATE_NEW_PLAYERS_FILE,
        OPTION_IMPORT_FILE,
        OPTION_QUIT_PROGRAM,
    ]
