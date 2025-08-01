"""
Constantes de navigation réutilisables dans tous les menus CLI.
Chaque option est décrite par une chaîne de caractères lisible, incluant des emojis pour l'UX.
"""

# ─────────────────────────────────────────────────────────
# INSTRUCTIONS GÉNÉRALES
# ─────────────────────────────────────────────────────────

# À utiliser avec console.print() pour afficher les instructions standard de navigation
INSTRUCTION_UTILISER_FLECHES = "Utilisez les flèches ↑ ↓ et [bold]Entrée[/bold] pour faire votre choix."

USER_CANCEL_MESSAGE = "⛔ Sélection annulée."

# ─────────────────────────────────────────────────────────
# ÉTIQUETTES GÉNÉRALES
# ─────────────────────────────────────────────────────────

OPTION_YES = "✅ Oui"
OPTION_NO = "❌ Non"

CONFIRM_CHOICE = "✅ Confirmer"
CANCEL_CHOICE = "❌ Annuler"


# ─────────────────────────────────────────────────────────
# CHOIX DE RETOUR AUX MENUS PRÉCÉDENTS
# ─────────────────────────────────────────────────────────

OPTION_RETURN_TO_CLUB_MENU = "↩ Retour de la club menu"
OPTION_RETURN_TO_PLAYERS_MENU = "👥 Retour à la gestion des joueurs"
OPTION_RETURN_TO_STARTING_MENU = "🏠 Retour au menu de démarrage"
OPTION_GO_BACK = "🔙 Retour à l’étape précédente"
OPTION_RETURN_TO_PLAYER_SORT_FILTER_MENU = "🔍 Retour au menu de tri/filtrage"
OPTION_RETURN_TO_PLAYER_FILE = "↩️ Revoir la fiche du joueur"
OPTION_QUIT_PROGRAM = "❌ Quitter le programme"

# ─────────────────────────────────────────────────────────
# MENU DE DÉMARRAGE
# ─────────────────────────────────────────────────────────

OPTION_CREATE_NEW_PLAYERS_FILE = "🆕 Créer un nouveau groupe de joueurs"
OPTION_IMPORT_FILE = "📁 Importer un fichier 'players.json'"

# ─────────────────────────────────────────────────────────
# MENU CLUB
# ─────────────────────────────────────────────────────────

OPTION_MANAGE_PLAYERS = "👥 Gérer les joueurs"
OPTION_MANAGE_TOURNAMENTS = "🏆 Gérer les tournois"

# ─────────────────────────────────────────────────────────
# MENU JOUEURS
# ─────────────────────────────────────────────────────────

OPTION_SHOW_PLAYERS = "📋 Voir les joueurs"
OPTION_SORT_PLAYERS = "🔍 Filtrer / Trier les joueurs"
OPTION_SHOW_PLAYER_FILE = "👤 Voir la fiche d'un joueur"
OPTION_ADD_NEW_PLAYER = "➕ Ajouter un nouveau joueur"

# ─────────────────────────────────────────────────────────
# # MENU CONFIRMATION & VALIDATION
# # DU FORMULAIRE DE CRÉATION D'UN NOUVEAU JOUEUR
# ─────────────────────────────────────────────────────────

OPTION_VALIDATE_NEW_PLAYER = "✅ Confirmer"
OPTION_MODIFY_PLAYER_FIELD = "✏️ Modifier un champ"
OPTION_CANCEL_NEW_PLAYER = "❌ Annuler"

# ─────────────────────────────────────────────────────────
# MENU MODIFICATION JOUEUR
# ─────────────────────────────────────────────────────────
OPTION_VALIDATE_PLAYER_MODIFICATION = "✅ Confirmer"
OPTION_TRY_AGAIN = "🔁 Réessayer"
OPTION_CANCEL_PLAYER_MODIFICATION = "❌ Annuler"

# ─────────────────────────────────────────────────────────
# CHAMPS MODIFIABLE D'UN JOUEUR
# ─────────────────────────────────────────────────────────
FIELD_ID = "Identifiant national"
FIELD_LAST_NAME = "Nom de famille"
FIELD_FIRST_NAME = "Prénom"
FIELD_BIRTHDATE = "Date de naissance"

# ─────────────────────────────────────────────────────────
# MENU TRI / FILTRAGE JOUEURS
# ─────────────────────────────────────────────────────────

OPTION_SORT_BY_NAME_ASC = "🔤 Trier par nom (A-Z)"
OPTION_SORT_BY_NAME_DESC = "🔡 Trier par nom (Z-A)"
OPTION_SORT_BY_RANKING = "📊 Trier par classement"
OPTION_SEARCH_BY_ID = "🆔 Rechercher un joueur par ID"
OPTION_SEARCH_BY_NAME = "🔎 Rechercher un joueur par nom"
OPTION_VIEW_PLAYER_FILE = "👤 Voir la fiche d’un joueur"

# ─────────────────────────────────────────────────────────
# MENU TOURNOIS
# ─────────────────────────────────────────────────────────

OPTION_VIEW_ONGOING_TOURNAMENTS = "🕒 Voir les tournois en cours"
OPTION_CREATE_NEW_TOURNAMENT = "🆕 Créer un nouveau tournoi"
OPTION_FINALIZE_TOURNAMENT = "🏁 Clôturer un tournoi"
OPTION_SHOW_WINNERS = "🏆 Afficher les gagnants"

# ─────────────────────────────────────────────────────────
# GROUPES DE SÉQUENCES DE NAVIGATION
# ─────────────────────────────────────────────────────────

STANDARD_ESCAPE_SEQUENCE = [
    OPTION_GO_BACK,
    OPTION_QUIT_PROGRAM,
]

NEW_PLAYER_ESCAPE_SEQUENCE = [
    OPTION_CANCEL_NEW_PLAYER,
    OPTION_RETURN_TO_PLAYERS_MENU,
    OPTION_RETURN_TO_STARTING_MENU,
    OPTION_QUIT_PROGRAM,
]

PLAYER_MODIFICATION_ESCAPE_SEQUENCE = [
    OPTION_CANCEL_PLAYER_MODIFICATION,
    OPTION_RETURN_TO_PLAYER_FILE,
    OPTION_RETURN_TO_STARTING_MENU,
    OPTION_QUIT_PROGRAM,
]

PLAYER_FILE_ESCAPE_SEQUENCE = [
    OPTION_RETURN_TO_PLAYER_FILE,
    OPTION_RETURN_TO_PLAYER_SORT_FILTER_MENU,
    OPTION_RETURN_TO_PLAYERS_MENU,
    OPTION_RETURN_TO_CLUB_MENU,
    OPTION_RETURN_TO_STARTING_MENU,
    OPTION_QUIT_PROGRAM
]

SORT_PLAYERS_ESCAPE_SEQUENCE_MENU = [
    OPTION_RETURN_TO_PLAYERS_MENU,
    OPTION_QUIT_PROGRAM,
]

# ─────────────────────────────────────────────────────────
# CHOIX DE CONFIRMATION RÉUTILISABLES
# ─────────────────────────────────────────────────────────

BLACK_OR_WHITE_CHOICES = [
    OPTION_YES,
    OPTION_NO,
]

CONFIRMATION_CHOICES = [
   CONFIRM_CHOICE,
    CANCEL_CHOICE,
]

CONFIRM_PLAYER_MODIFICATION = [
    OPTION_VALIDATE_PLAYER_MODIFICATION,
    OPTION_MODIFY_PLAYER_FIELD,
]

CONFIRM_NEW_PLAYER = [
    OPTION_VALIDATE_NEW_PLAYER,
    OPTION_MODIFY_PLAYER_FIELD,
]
