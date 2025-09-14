from typing import Tuple, Optional, Dict, List
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
# Edit / Search prompts
# --------------------

def prompt_search_player_query() -> Optional[str]:
    """
    Ask for a search query to locate a player.

    Returns:
        Optional[str]: Raw query (national ID or partial name) or None if cancelled.
    """
    return _safe_ask(questionary.text("Rechercher un joueur (ID ou nom) :"))


def prompt_select_player(matches: List[Player]) -> Optional[Player]:
    """
    If multiple players match, let the user pick one.

    Args:
        matches: List of Player matches.

    Returns:
        The selected Player or None if cancelled/no matches.
    """
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]

    choices = [
        {
            "name": f"{p.last_name.upper()}, {p.first_name} ({p.national_id})",
            "value": p.national_id,
        }
        for p in matches
    ]
    nid = questionary.select("Plusieurs résultats, choisissez :", choices=choices).ask()
    if not nid:
        return None
    for p in matches:
        if p.national_id == nid:
            return p
    return None


def prompt_select_field_to_edit() -> Optional[str]:
    """
    Let the user choose a single field to edit, or finish/cancel.

    Returns:
        One of: 'last_name' | 'first_name' | 'birthdate' | 'national_id' |
        'done' | None
    """
    mapping = [
        ("last_name", FIELD_LABELS["last_name"]),
        ("first_name", FIELD_LABELS["first_name"]),
        ("birthdate", FIELD_LABELS["birthdate"]),
        ("national_id", FIELD_LABELS["national_id"]),
    ]
    choices = [{"name": label, "value": key} for key, label in mapping]
    choices.append({"name": "Terminer et enregistrer", "value": "done"})
    choices.append({"name": "Annuler", "value": None})
    return questionary.select("Quel champ souhaitez-vous modifier ?", choices=choices).ask()


def prompt_new_value_for_field(attr_key: str) -> Optional[str]:
    """
    Ask a new value for the selected attribute.
    Behavior:
      - Empty input (just Enter) => cancel and return None (no change).
      - Non-empty => validate using the same rules as creation; re-prompt on invalid.
    Returns:
      str (normalized) or None if cancelled.
    """
    attr_to_label = {
        "last_name": "Nom de famille",
        "first_name": "Prénom",
        "birthdate": "Date de naissance",
        "national_id": "Identifiant national",
    }
    label = attr_to_label[attr_key]
    suffix = " (YYYY-MM-DD)" if attr_key == "birthdate" else ""
    validator = VALIDATION_MAP[label]
    while True:
        raw = _safe_ask(questionary.text(f"{label}{suffix} (laisser vide pour annuler) :"))
        if raw is None:  # Ctrl+C / Esc
            return None
        raw = raw.strip()
        if raw == "":  # user pressed Enter => cancel this field
            return None
        if validator and not validator(raw):
            display_error_message("Format invalide. Veuillez réessayer.")
            continue
        return raw


def confirm_field_change(label_fr: str, ancien: str, nouveau: str) -> bool:
    """
    Confirm a single field change before applying it.

    Returns:
        True if confirmed, False otherwise.
    """
    return bool(
        questionary.confirm(
            f"Confirmer la modification de '{label_fr}' : '{ancien}' → '{nouveau}' ?"
        ).ask()
    )


def confirm_save_changes() -> bool:
    """
    Confirm saving all pending changes to disk.

    Returns:
        True if confirmed, False otherwise.
    """
    return bool(questionary.confirm("Enregistrer ces modifications ?").ask())

# --------------------
# Confirmations / Errors
# --------------------


def confirm_player_added():
    console.print("✅ [green]Le joueur a bien été ajouté à la base de données.[/green]\n")


def display_error_message(reason: str):
    console.print(f"❌ [red]Erreur : {reason}[/red]")

# --------------------
# Notifications
# --------------------


def notify_no_match() -> None:
    """Inform that no player matched the search."""
    console.print("[yellow]Aucun joueur ne correspond à cette recherche.[/yellow]")


def notify_duplicate_id() -> None:
    """Inform that the new national ID would collide with another player."""
    console.print("[red]Cet identifiant national est déjà utilisé par un autre joueur.[/red]")


def notify_saved() -> None:
    """Inform that changes were saved."""
    console.print("✅ [green]Modifications enregistrées.[/green]")

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


def display_all_players(
    players,
    scope: str = "global",
    stats_index=None,
    show_enrollment: bool = False,
    mode: str = "roster",  # "roster" | "summary" | "directory"
):
    """
    Affiche les joueurs.
      - mode="roster"   : pour un tournoi en cours/début (liste simple)
      - mode="summary"  : résumé léger avec points (fin de tournoi si besoin)
      - mode="directory": vue globale (annuaire) sans colonnes inutiles
    """
    if not players:
        console.print("[yellow]Aucun joueur à afficher.[/yellow]")
        return

    titles = {
        "roster": "Joueurs du tournoi courant",
        "summary": "Joueurs — résumé",
        "directory": "Joueurs globaux (base complète)",
    }
    table = Table(title=titles.get(mode, "Joueurs"))

    # ── Colonnes par mode (plus de 'Matchs' ni 'Tournois')
    table.add_column("#", style="cyan", justify="right", no_wrap=True)
    table.add_column("Nom complet", overflow="fold")
    table.add_column("ID", no_wrap=True)

    if mode in ("roster", "directory"):
        table.add_column("Âge", justify="right", no_wrap=True)
        if show_enrollment:
            table.add_column("Inscription", no_wrap=True)

    if mode == "summary":
        # On montre seulement les points (quand utile)
        table.add_column("Points", justify="right", no_wrap=True)

    for idx, p in enumerate(players, 1):
        row = [str(idx), f"{p.last_name.upper()}, {p.first_name}", p.national_id]

        if mode in ("roster", "directory"):
            row.append(str(p.age))
            if show_enrollment:
                row.append(getattr(p, "date_enrolled", "") or "—")

        if mode == "summary":
            # source des points : stats_index (si fourni) sinon total joueur
            pts = None
            if stats_index:
                pts = (stats_index or {}).get(p.national_id, {}).get("points")
            if pts is None:
                pts = p.get_total_score()
            row.append(f"{float(pts):.1f}")

        table.add_row(*row)
    console.print(table)

# --------------------
# Menu
# --------------------


def show_player_main_menu() -> str:
    """
    Retourne :
        '1' => Voir les joueurs
        '2' => Ajouter un joueur
        '3' => Modifier un joueur
        '4' => Retour
        '5' => Quitter le programme
    """
    try:
        choice = questionary.select(
            "---- MENU DES JOUEURS ----",
            choices=[
                {"name": "1. VOIR LES JOUEURS", "value": "1"},
                {"name": "2. AJOUTER UN NOUVEAU JOUEUR", "value": "2"},
                {"name": "3. MODIFIER UN JOUEUR", "value": "3"},
                {"name": "4. RETOUR", "value": "4"},
                {"name": "5. QUITTER LE PROGRAMME", "value": "5"},
            ],
        ).ask()
        return choice or "4"
    except (EOFError, KeyboardInterrupt):
        console.print("\n⛔ [red]Entrée interrompue. Retour au menu principal.[/red]")
        return "4"
