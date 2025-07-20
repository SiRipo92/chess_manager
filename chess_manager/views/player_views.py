from typing import List, Tuple, Optional, cast
import questionary
from rich.console import Console
from rich.table import Table
from chess_manager.models.player_models import Player
from chess_manager.constants.player_fields import FIELD_CHOICES, FIELD_LABELS, VALIDATION_MAP
from chess_manager.constants.navigation.menu_keys import CONFIRM_NEW_PLAYER_MENU, ADD_NEW_PLAYER_MENU
from chess_manager.constants.navigation.labels import (
    OPTION_VALIDATE_NEW_PLAYER,
    OPTION_MODIFY_PLAYER_FIELD,
    OPTION_CANCEL_NEW_PLAYER,
    OPTION_YES,
    OPTION_NO
)
from chess_manager.utils.navigation.menu_builder import display_menu_from_key, display_contextual_menu
from chess_manager.constants.navigation.menu_keys import (
    PLAYER_MANAGEMENT_MENU,
    PLAYER_SORT_FILTER_MENU,
    PLAYER_MODIFICATION_VALIDATION_MENU,
    PLAYER_FILE_RETURN_MENU,
    YES_NO_MENU
)

console = Console()

# Utilise les champs dans l’ordre attendu pour créer un joueur
PLAYER_CREATION_KEYS = FIELD_CHOICES


# ==================
# 1. Input Prompts
# ==================

def prompt_new_player_inputs_with_review() -> Optional[Tuple[str, str, str, str]]:
    """
    Gère la saisie et correction d’un joueur avec résumé et validation.
    """
    field_values: dict[str, str] = {}
    # Collecte les données pour chaque champ requis
    for label in PLAYER_CREATION_KEYS:
        suffix = " (YYYY-MM-DD)" if "naissance" in label.lower() else ""
        value = prompt_field_with_validation(
            f"{label}{suffix} :",
            VALIDATION_MAP[label]
        )
        field_values[label] = cast(str, value)
    # Affiche un résumé des données et permet la modification ou confirmation
    while True:
        # Création temporaire du joueur pour affichage du résumé
        temp_player = Player(
            *[field_values[label] for label in PLAYER_CREATION_KEYS]
        )
        console.print("[green]Récapitulatif des données saisies : [green]")
        display_player_brief_info(temp_player)

        # Choix de l'utilisateur : enregistrer, modifier un champ, ou annuler
        action = display_menu_from_key(menu_key=CONFIRM_NEW_PLAYER_MENU)
        if action == OPTION_VALIDATE_NEW_PLAYER:
            return tuple(field_values[label] for label in FIELD_CHOICES)  # type: ignore
        elif action == OPTION_CANCEL_NEW_PLAYER:
            return None
        elif action == OPTION_MODIFY_PLAYER_FIELD:
            field_to_edit = prompt_edit_player_field_choice()
            if field_to_edit == OPTION_CANCEL_NEW_PLAYER:
                continue

            suffix = " (YYYY-MM-DD)" if "naissance" in field_to_edit.lower() else ""
            new_value = prompt_field_with_validation(
                f"{field_to_edit}{suffix} :",
                VALIDATION_MAP[field_to_edit]
            )
            field_values[field_to_edit] = cast(str, new_value)


def prompt_field_with_validation(label: str, validate_func=None) -> Optional[str]:
    """
    Prompt for entering a valid format in player creation/modification
    """
    while True:
        value = questionary.text(label).ask()

        # Vérifie que la saisie n'est pas vide
        if not value:
            display_error_message("Ce champ ne peut pas être vide.")
            continue
        # Vérifie la validité du format si une fonction de validation est fournie
        if validate_func and not validate_func(value):
            display_error_message("Format invalide. Veuillez réessayer.")
            continue
        return value


def prompt_edit_player_field_choice() -> str:
    """
    Propose à l'utilisateur de choisir dynamiquement un champ à modifier
    en se basant sur les labels dans FIELD_LABELS.

    Retour :
        str : Le label du champ sélectionné.
    """
    return questionary.select(
        "Quel champ souhaitez-vous modifier ?",
        choices=PLAYER_CREATION_KEYS + ["Annuler"]
    ).ask()


def prompt_player_bio_update_choice(player: Player) -> str:
    """
    Affiche les champs modifiables pour un joueur, en utilisant les constantes FIELD_CHOICES.
    """
    display_player_brief_info(player)
    console.print(
        f"\n[blue]Modifier les informations de {player.first_name} {player.last_name}[/blue]"
    )
    return questionary.select(
        "Quel champ souhaitez-vous modifier ?",
        choices=FIELD_CHOICES + ["Annuler"]
    ).ask()


def prompt_player_national_id(prompt="Entrez l'identifiant national d'échecs du joueur : ") -> str:
    """
    Invite l'utilisateur à saisir un identifiant national.
    """
    return questionary.text(prompt).ask().strip().upper()


def prompt_match_result() -> Tuple[str, str]:
    """
    À terme, ce formulaire sera remplacé par une sélection de match
    (suggérée automatiquement par le système via la ronde en cours).

    Retour :
        Tuple contenant le nom du match et le résultat abrégé (V, D, N).
    """
    try:
        match_name = questionary.text("Nom du match (ex: 'Ronde 1')").ask()
        result = questionary.select(
            "Résultat",
            choices=["V", "D", "N"]
        ).ask()
        return match_name, result
    except (EOFError, KeyboardInterrupt):
        # EOFError : saisie interrompue via redirection ou fin de fichier
        # KeyboardInterrupt : interruption clavier (ex: Ctrl+C)
        console.print("\n⛔ [red]Entrée interrompue.[/red]")
        return "", ""


def prompt_player_name_filter():
    """
    Invite à saisir un nom ou une chaîne de caractères pour filtrer les joueurs.
    """
    return questionary.text("Entrez une chaîne pour trouver un joueur par nom de famille :").ask()

# ==================
# 2. Confirmations
# ==================


def confirm_player_added():
    """
    Affiche un message de confirmation après l'ajout d’un joueur.
    """
    console.print("✅ [green]Le joueur a bien été ajouté à la base de données.[/green]\n")


def confirm_field_update(field_name: str, new_value: str) -> str:
    """
    Demande confirmation avant de sauvegarder une modification.
    Utilise le menu contextuel défini dans les constantes.
    """
    message = f"[{field_name}] sera mis à jour avec : {new_value}. Confirmer ?"
    return display_menu_from_key(
        menu_key=PLAYER_MODIFICATION_VALIDATION_MENU,
        custom_title=message
    )


def confirm_player_updated() -> None:
    console.print("✅ [green]Les informations du joueur ont été mises à jour avec succès.[/green]\n")

# =========================
# 3. Display Functions
# =========================


def display_error_message(reason: str):
    """
    Affiche un message d'erreur avec une raison explicite.
    """
    console.print(f"❌ [red]Erreur : {reason}[/red]")


def display_player_brief_info(player: Player) -> None:
    """
    Affiche un aperçu simple des informations modifiable du joueur.
    """
    console.print("\n[bold]📋 Informations actuelles du joueur :[/bold]")

    # Création d’une table riche avec les champs principaux du joueur
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Champ")
    table.add_column("Valeur", justify="center")

    for attr_key in FIELD_LABELS:
        # Parcourir les "Field Labels", obtenir leurs valeurs pour le joueur, et créer une rangée
        label = FIELD_LABELS[attr_key]
        value = getattr(player, attr_key)
        table.add_row(label, value)

    console.print(table)


def display_all_players(players: List[Player]):
    """
    Affiche la liste des joueurs enregistrés avec leurs informations principales.

    Paramètre :
        players (List[Player]) : Liste d'objets Player à afficher.
    """
    if not players:
        # Avertit si aucun joueur n’est enregistré
        console.print("[yellow]Aucun joueur enregistré.[/yellow]")
        return

    # Construction de la table d'affichage
    table = Table(title="📋 Joueurs enregistrés")
    table.add_column("#", style="cyan")
    table.add_column("Nom complet")
    table.add_column("ID")
    table.add_column("Naissance")
    table.add_column("Âge")
    table.add_column("Inscription")

    # Remplit la table avec chaque joueur
    for idx, player in enumerate(players, 1):
        table.add_row(
            str(idx),
            f"{player.last_name.upper()}, {player.first_name}",
            player.national_id,
            player.birthdate,
            str(player.age),
            player.date_enrolled
        )
    console.print(table)


def display_stats_summary(stats: dict):
    """
    Affiche proprement les statistiques retournées par get_stats_summary().
    """
    table = Table(title="Statistiques du joueur")
    table.add_column("Statut")
    table.add_column("Valeur")
    for key, value in stats.items():
        table.add_row(key, str(value))
    console.print(table)


def display_full_player_profile(player: Player):
    """
    Affiche toutes les informations d’un joueur sous forme de table enrichie.

    Paramètre :
        player (Player) : Le joueur à afficher.
    """

    # Récupère les stats synthétiques du joueur via méthode du modèle
    stats = player.get_stats_summary(None)

    # Construction de la table enrichie avec lignes séparatrices
    table = Table(title=f"📇 Fiche de {player.first_name} {player.last_name}", show_lines=True)
    table.add_column("Champ", style="bold cyan")
    table.add_column("Valeur", style="white")

    # Ajout des données personnelles principales
    label_map = {
        "Nom complet": f"{player.first_name} {player.last_name}",
        "ID national": player.national_id,
        "Date de naissance": player.birthdate,
        "Âge": str(player.age),
        "Date d'inscription": player.date_enrolled
    }
    # Parcourir les 'label_map' et leur valeurs
    for key, value in label_map.items():
        table.add_row(key, value)

    # Ajout des statistiques calculées
    for stat_label, value in stats.items():
        table.add_row(stat_label, str(value))

    console.print(table)

# =========================
# 4. Player Menu Navigations
# =========================


def display_player_management_menu() -> str | None:
    """
    Affiche dynamiquement le menu principal de gestion des joueurs.
    """
    return display_menu_from_key(menu_key=PLAYER_MANAGEMENT_MENU)


def show_player_sort_filter_menu() -> str:
    """
    Affiche dynamiquement le menu de tri et de filtrage des joueurs.
    """
    return display_menu_from_key(menu_key=PLAYER_SORT_FILTER_MENU)


def display_player_file_menu(player: Player) -> str | None:
    """
    Affiche le profil complet d’un joueur et propose à l'utilisateur
    de modifier ses informations ou de choisir où retourner ensuite.

    Retour :
        - Le choix final de menu sous forme de clé (menu_key).
        - Ou une action déclenchée (modification).
    """

    # 1. Affiche le titre et la fiche complète du joueur
    console.print("\n[bold cyan]--- FICHE JOUEUR ---[/bold cyan]\n")
    display_full_player_profile(player)

    # 2. Demande à l'utilisateur s’il souhaite modifier ce joueur
    console.print("\n[blue]Souhaitez-vous modifier ce joueur ?[/blue]\n")
    action = display_menu_from_key(menu_key=YES_NO_MENU)

    if action == OPTION_YES:
        # This menu should have the player_fields to edit
        # With a modification escape sequence menu
        return prompt_player_bio_update_choice(player)

    elif action == OPTION_NO:
        # 3. Si NON : proposer où retourner ensuite
        console.print("\n[blue]Où souhaitez-vous retourner dans le programme ?[/blue]\n")
        next_action = display_menu_from_key(menu_key=PLAYER_FILE_RETURN_MENU)

        return next_action
