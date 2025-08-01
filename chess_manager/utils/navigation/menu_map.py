"""
Maps internal menu slugs (keys) to their associated option lists.
Used for dynamically rendering choices with Questionary.
"""

import os

from chess_manager.constants.player_fields import PLAYER_BIO_MODIFICATION_CHOICES
from chess_manager.constants.navigation import menu_keys
from chess_manager.constants.navigation.titles import MENU_TITLES
from chess_manager.constants.navigation import labels

MENU_STRUCTURE = {

    menu_keys.STARTING_MENU: [
        labels.OPTION_CREATE_NEW_PLAYERS_FILE,
        labels.OPTION_IMPORT_FILE,
        labels.OPTION_QUIT_PROGRAM,
    ],

    menu_keys.CLUB_MANAGEMENT_MENU: [
        labels.OPTION_MANAGE_PLAYERS,
        labels.OPTION_MANAGE_TOURNAMENTS,
        *labels.STANDARD_ESCAPE_SEQUENCE,
    ],

    menu_keys.PLAYER_MANAGEMENT_MENU: [
        labels.OPTION_SHOW_PLAYERS,
        labels.OPTION_SORT_PLAYERS,
        labels.OPTION_SHOW_PLAYER_FILE,
        labels.OPTION_ADD_NEW_PLAYER,
        *labels.STANDARD_ESCAPE_SEQUENCE,
    ],

    menu_keys.TOURNAMENT_MANAGEMENT_MENU: [
        labels.OPTION_VIEW_ONGOING_TOURNAMENTS,
        labels.OPTION_CREATE_NEW_TOURNAMENT,
        labels.OPTION_FINALIZE_TOURNAMENT,
        labels.OPTION_SHOW_WINNERS,
        *labels.STANDARD_ESCAPE_SEQUENCE,
    ],

    menu_keys.PLAYER_SORT_FILTER_MENU: [
        labels.OPTION_SORT_BY_NAME_ASC,
        labels.OPTION_SORT_BY_NAME_DESC,
        labels.OPTION_SORT_BY_RANKING,
        labels.OPTION_SEARCH_BY_ID,
        labels.OPTION_SEARCH_BY_NAME,
        labels.OPTION_VIEW_PLAYER_FILE,
        *labels.PLAYER_FILE_ESCAPE_SEQUENCE,
    ],

    menu_keys.SORT_PLAYERS_ESCAPE_SEQUENCE_MENU: [
        *labels.SORT_PLAYERS_ESCAPE_SEQUENCE_MENU
    ],

    menu_keys.PLAYER_FILE_MENU: [
        labels.OPTION_MODIFY_PLAYER_FIELD,
        *labels.PLAYER_FILE_ESCAPE_SEQUENCE,
    ],

    menu_keys.PLAYER_MODIFICATION_VALIDATION_MENU: [
        *labels.CONFIRM_PLAYER_MODIFICATION,
        labels.OPTION_CANCEL_PLAYER_MODIFICATION
    ],

    menu_keys.CONFIRM_NEW_PLAYER_MENU: [
        *labels.CONFIRM_NEW_PLAYER,
        *labels.NEW_PLAYER_ESCAPE_SEQUENCE
    ],

    menu_keys.YES_NO_MENU: [
        *labels.BLACK_OR_WHITE_CHOICES,
    ],

    menu_keys.CONFIRM_CANCEL_MENU: [
        *labels.CONFIRMATION_CHOICES,
    ],

    menu_keys.CONFIRM_PLAYER_EDIT_MENU: [
        *labels.CONFIRM_PLAYER_MODIFICATION,
    ],

    menu_keys.PLAYER_FILE_ESCAPE_SEQUENCE: [
        *labels.PLAYER_FILE_ESCAPE_SEQUENCE
    ],

    menu_keys.PLAYER_MODIFICATION_ESCAPE_SEQUENCE: [
        labels.OPTION_CANCEL_PLAYER_MODIFICATION,
        labels.OPTION_RETURN_TO_PLAYER_FILE,
        labels.OPTION_RETURN_TO_STARTING_MENU,
        labels.OPTION_QUIT_PROGRAM,
    ],

    menu_keys.PLAYER_FILE_BIO_MODIFICATIONS_MENU: [
        *PLAYER_BIO_MODIFICATION_CHOICES,
        labels.OPTION_GO_BACK
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
        labels.OPTION_CREATE_NEW_PLAYERS_FILE,
        labels.OPTION_IMPORT_FILE,
        labels.OPTION_QUIT_PROGRAM,
    ]


MENU_REGISTRY = {
    key: {
        "title": MENU_TITLES.get(key, f"Menu inconnu: {key}"),
        "choices": MENU_STRUCTURE.get(key, []),
        "escape_actions": [
            opt for opt in MENU_STRUCTURE.get(key, [])
            if opt in labels.STANDARD_ESCAPE_SEQUENCE
        ],
        # You can define controller mappings gradually here:
        # "handlers": {
        #     labels.OPTION_SHOW_PLAYERS: "show_players",
        #     ...
        # }
    }
    for key in MENU_STRUCTURE
}

# ensure cancel is treated as escape for the modification escape menu
MENU_REGISTRY[menu_keys.PLAYER_MODIFICATION_ESCAPE_SEQUENCE]["escape_actions"] = [
    labels.OPTION_CANCEL_PLAYER_MODIFICATION
]