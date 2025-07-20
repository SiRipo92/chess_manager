"""
Titres statiques des menus pour affichage dans l'interface CLI.
Utilise Rich pour mise en forme (couleur, gras, majuscules).
"""

# ─────────────────────────────────────────────────────────
# TITRES DE MENUS STATIQUES
# ─────────────────────────────────────────────────────────

# Affichage :
# ----------------------------------------
# MENU DE DÉMARRAGE
# ----------------------------------------
STARTING_MENU_TITLE = (
    "[bold cyan]\n" + "-" * 40 +
    "\nMENU DE DÉMARRAGE\n" +
    "-" * 40 + "[/bold cyan]"
)

# Affichage :
# ----------------------------------------
# MENU DE GESTION DE JOUEURS
# ----------------------------------------
PLAYER_MANAGEMENT_MENU_TITLE = (
    "[bold cyan]\n" + "-" * 40 +
    "\nMENU DE GESTION DE JOUEURS\n" +
    "-" * 40 + "[/bold cyan]"
)

# Affichage :
# ----------------------------------------
# MENU DE GESTION DES TOURNOIS
# ----------------------------------------
TOURNAMENT_MANAGEMENT_MENU_TITLE = (
    "[bold cyan]\n" + "-" * 40 +
    "\nMENU DE GESTION DES TOURNOIS\n" +
    "-" * 40 + "[/bold cyan]"
)

# Affichage :
# ----------------------------------------
# MENU DE TRI / FILTRAGE DES JOUEURS
# ----------------------------------------
PLAYER_SORT_FILTER_MENU_TITLE = (
    "[bold cyan]\n" + "-" * 40 +
    "\nMENU DE TRI / FILTRAGE DES JOUEURS\n" +
    "-" * 40 + "[/bold cyan]"
)

# Affichage :
# ----------------------------------------
# FICHE DU JOUEUR
# ----------------------------------------
PLAYER_FILE_TITLE = (
    "[bold cyan]\n" + "-" * 40 +
    "\nFICHE DU JOUEUR\n" +
    "-" * 40 + "[/bold cyan]"
)

# Affichage :
# ----------------------------------------
# VALIDATION DE LA MODIFICATION
# ----------------------------------------
PLAYER_MODIFICATION_VALIDATION_MENU_TITLE = (
    "[bold cyan]\n" + "-" * 40 +
    "\nVALIDATION DE LA MODIFICATION\n" +
    "-" * 40 + "[/bold cyan]"
)

# Affichage :
# ----------------------------------------
# AJOUT D’UN NOUVEAU JOUEUR
# ----------------------------------------
ADD_NEW_PLAYER_MENU_TITLE = (
    "[bold cyan]\n" + "-" * 40 +
    "\nAJOUT D’UN NOUVEAU JOUEUR\n" +
    "-" * 40 + "[/bold cyan]"
)

# ─────────────────────────────────────────────────────────
# TEMPLATES AVEC NOM DE VILLE DYNAMIQUE
# ─────────────────────────────────────────────────────────

# Affichage pour Nanterre par exemple :
# ----------------------------------------
# MENU DE GESTION DU CLUB D’ÉCHECS À [VILLE]
# ----------------------------------------
CLUB_MANAGEMENT_MENU_TEMPLATE = (
    "[bold cyan]\n" + "-" * 40 +
    "\nMENU DE GESTION DU CLUB D’ÉCHECS À {city}\n" +
    "-" * 40 + "[/bold cyan]"
)


# ─────────────────────────────────────────────────────────
# VERSIONS ABRÉGÉES POUR LES CONTEXTES (e.g. menus dynamiques)
# ─────────────────────────────────────────────────────────

STARTING_MENU_SHORT = "Menu de démarrage"
PLAYER_MANAGEMENT_MENU_SHORT = "Menu des joueurs"
TOURNAMENT_MANAGEMENT_MENU_SHORT = "Menu des tournois"
PLAYER_SORT_FILTER_MENU_SHORT = "Menu de tri"
PLAYER_FILE_SHORT = "Fiche du joueur"
PLAYER_MODIFICATION_VALIDATION_MENU_SHORT = "Validation modification"
ADD_NEW_PLAYER_MENU_SHORT = "Ajout d’un joueur"
CLUB_MANAGEMENT_MENU_TEMPLATE_SHORT = "Menu club à {city}"

# ─────────────────────────────────────────────────────────
# DICTIONNAIRE DE MAPPING : SLUG → TITRE COMPLET
# ─────────────────────────────────────────────────────────

MENU_TITLES = {
    "starting_menu": STARTING_MENU_TITLE,
    "player_management_menu": PLAYER_MANAGEMENT_MENU_TITLE,
    "tournament_management_menu": TOURNAMENT_MANAGEMENT_MENU_TITLE,
    "player_sort_filter_menu": PLAYER_SORT_FILTER_MENU_TITLE,
    "player_file": PLAYER_FILE_TITLE,
    "player_modification_validation_menu": PLAYER_MODIFICATION_VALIDATION_MENU_TITLE,
    "add_new_player_menu": ADD_NEW_PLAYER_MENU_TITLE,
    # "club_management_menu": handled dynamically in builder
}