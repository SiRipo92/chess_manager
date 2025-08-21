from typing import List, Tuple, Optional, Dict
import questionary
from rich.console import Console
from rich.table import Table
from chess_manager.models.player_models import Player
from chess_manager.constants.player_fields import FIELD_CHOICES, FIELD_LABELS, VALIDATION_MAP

console = Console()

PLAYER_CREATION_KEYS = FIELD_CHOICES  # order used for constructing Player


def _safe_ask(prompt_callable, default: Optional[str] = None) -> Optional[str]:
    try:
        answer = prompt_callable.ask()
        return answer if answer is not None else default
    except (EOFError, KeyboardInterrupt):
        console.print("\n⛔ [red]Entrée interrompue.[/red]")
        return default


# --------------------
# Input / Creation
# --------------------
def prompt_new_player_inputs_with_review() -> Optional[Tuple[str, str, str, str]]:
    field_values: Dict[str, str] = {}

    for label in PLAYER_CREATION_KEYS:
        suffix = " (YYYY-MM-DD)" if "naissance" in label.lower() else ""
        value = prompt_field_with_validation(f"{label}{suffix} :", VALIDATION_MAP[label])
        if value is None:
            return None
        field_values[label] = value

    # review loop
    while True:
        temp_player = Player(
            *[field_values[label] for label in PLAYER_CREATION_KEYS]
        )
        console.print("[green]Récapitulatif des données saisies :[/green]")
        display_player_brief_info(temp_player)

        action = questionary.select(
            "Souhaitez-vous enregistrer ce joueur ?",
            choices=[
                {"name": "1. Confirmer", "value": "confirm"},
                {"name": "2. Modifier un champ", "value": "edit"},
                {"name": "3. Annuler", "value": "cancel"},
            ],
        ).ask()

        if action == "confirm":
            return tuple(field_values[label] for label in PLAYER_CREATION_KEYS)  # type: ignore
        elif action == "cancel":
            return None
        elif action == "edit":
            # let user re-enter one field
            field_to_edit = questionary.select(
                "Quel champ modifier ?",
                choices=[{"name": label, "value": label} for label in PLAYER_CREATION_KEYS],
            ).ask()
            if not field_to_edit:
                continue
            suffix = " (YYYY-MM-DD)" if "naissance" in field_to_edit.lower() else ""
            new_value = prompt_field_with_validation(f"{field_to_edit}{suffix} :", VALIDATION_MAP[field_to_edit])
            if new_value:
                field_values[field_to_edit] = new_value
        else:
            display_error_message("Choix invalide.")


def prompt_field_with_validation(label: str, validate_func=None) -> Optional[str]:
    while True:
        value = _safe_ask(questionary.text(label))
        if value is None:
            return None
        if not value.strip():
            display_error_message("Ce champ ne peut pas être vide.")
            continue
        if validate_func and not validate_func(value):
            display_error_message("Format invalide. Veuillez réessayer.")
            continue
        return value.strip()


def prompt_player_national_id(prompt: str = "Entrez l'identifiant national d'échecs du joueur : ") -> str:
    value = _safe_ask(questionary.text(prompt))
    return (value or "").strip().upper()


# --------------------
# Confirmations / Errors
# --------------------
def confirm_player_added():
    console.print("✅ [green]Le joueur a bien été ajouté à la base de données.[/green]\n")


def display_error_message(reason: str):
    console.print(f"❌ [red]Erreur : {reason}[/red]")


# --------------------
# Displays
# --------------------
def display_player_brief_info(player: Player) -> None:
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Champ")
    table.add_column("Valeur", justify="center")

    for attr_key, label in FIELD_LABELS.items():
        value = getattr(player, attr_key, "")
        table.add_row(label, str(value))
    console.print(table)


def display_all_players(players: List[Player]):
    if not players:
        console.print("[yellow]Aucun joueur enregistré.[/yellow]")
        return

    table = Table(title="Joueurs enregistrés")
    table.add_column("#", style="cyan")
    table.add_column("Nom complet")
    table.add_column("ID")
    table.add_column("Naissance")
    table.add_column("Âge")
    table.add_column("Inscription")

    for idx, player in enumerate(players, 1):
        table.add_row(
            str(idx),
            f"{player.last_name.upper()}, {player.first_name}",
            player.national_id,
            player.birthdate,
            str(player.age),
            player.date_enrolled,
        )
    console.print(table)


# --------------------
# Menu
# --------------------
def show_player_main_menu() -> str:
    """
    Retourne :
        '1' => Voir les joueurs
        '2' => Ajouter un joueur
        '3' => Retour
        '4' => Quitter le programme
    """
    try:
        choice = questionary.select(
            "---- MENU DES JOUEURS ----",
            choices=[
                {"name": "1. VOIR LES JOUEURS", "value": "1"},
                {"name": "2. AJOUTER UN NOUVEAU JOUEUR", "value": "2"},
                {"name": "3. RETOUR", "value": "3"},
                {"name": "4. QUITTER LE PROGRAMME", "value": "4"},
            ],
        ).ask()
        return choice or "3"
    except (EOFError, KeyboardInterrupt):
        console.print("\n⛔ [red]Entrée interrompue. Retour au menu principal.[/red]")
        return "3"