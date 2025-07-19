from typing import List, Tuple, Optional, cast
import questionary
from rich.console import Console
from rich.table import Table
from chess_manager.models.player_models import Player
from chess_manager.constants.player_fields import FIELD_CHOICES, FIELD_LABELS, VALIDATION_MAP

console = Console()


# Utilise les champs dans l’ordre attendu pour créer un joueur
PLAYER_CREATION_KEYS = FIELD_CHOICES


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


def prompt_new_player_inputs_with_review() -> Optional[Tuple[str, str, str, str]]:
    """
    Gère la saisie et correction d’un joueur avec résumé et validation.
    """
    field_values: dict[str, str] = {}
    for label in PLAYER_CREATION_KEYS:
        suffix = " (YYYY-MM-DD)" if "naissance" in label.lower() else ""
        value = prompt_field_with_validation(
            f"{label}{suffix} :",
            VALIDATION_MAP[label]
        )
        field_values[label] = cast(str, value)

    while True:
        temp_player = Player(
            *[field_values[label] for label in PLAYER_CREATION_KEYS]
        )
        console.print("[green]Récapitulatif des données saisies : [green]")
        display_player_brief_info(temp_player)

        action = questionary.select(
            "Souhaitez-vous enregistrer ce joueur ?",
            choices=["Confirmer", "Modifier un champ", "Annuler"]
        ).ask()

        if action == "Confirmer":
            return tuple(field_values[label] for label in PLAYER_CREATION_KEYS)  # type: ignore
        elif action == "Annuler":
            return None
        elif action == "Modifier un champ":
            field_to_edit = prompt_edit_player_field_choice()
            if field_to_edit == "Annuler":
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
        if not value:
            display_error_message("Ce champ ne peut pas être vide.")
            continue
        if validate_func and not validate_func(value):
            display_error_message("Format invalide. Veuillez réessayer.")
            continue
        return value


def confirm_player_added():
    """
    Affiche un message de confirmation après l'ajout d’un joueur.
    """
    console.print("✅ [green]Le joueur a bien été ajouté à la base de données.[/green]\n")


def display_error_message(reason: str):
    """
    Affiche un message d'erreur avec une raison explicite.
    """
    console.print(f"❌ [red]Erreur : {reason}[/red]")


def display_all_players(players: List[Player]):
    """
    Affiche la liste des joueurs enregistrés avec leurs informations principales.

    Paramètre :
        players (List[Player]) : Liste d'objets Player à afficher.
    """
    if not players:
        console.print("[yellow]Aucun joueur enregistré.[/yellow]")
        return

    table = Table(title="📋 Joueurs enregistrés")
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
            player.date_enrolled
        )
    console.print(table)


def prompt_player_national_id(prompt="Entrez l'identifiant national d'échecs du joueur : ") -> str:
    """
    Invite l'utilisateur à saisir un identifiant national.
    """
    return questionary.text(prompt).ask().strip().upper()


def prompt_player_bio_update_choice(player: Player) -> str:
    """
    Affiche les champs modifiables pour un joueur.
    """
    display_player_brief_info(player)  # 👈 Preview before asking
    console.print(
        "\n[blue]Modifier les informations de {} {}[blue]"
        .format(player.first_name, player.last_name))
    return questionary.select(
        "Quel champ souhaitez-vous modifier ?",
        choices=[
            "Nom de famille",
            "Prénom",
            "Date de naissance",
            "Identifiant national",
            "Annuler"
        ]
    ).ask()


def prompt_field_update(field_name: str) -> str:
    if field_name == "Date de naissance":
        field_name += " (YYYY-MM-DD)"
    return questionary.text(f"Nouvelle valeur pour {field_name} :").ask()


def confirm_field_update(field_name: str, new_value: str) -> str:
    """
    Demande confirmation avant de sauvegarder une modification.
    """
    return questionary.select(
        f"[{field_name}] sera mis à jour avec : {new_value}. Confirmer ?",
        choices=["Confirmer", "Réessayer", "Annuler"]
    ).ask()


def confirm_player_updated() -> None:
    console.print("✅ [green]Les informations du joueur ont été mises à jour avec succès.[/green]\n")


def display_player_brief_info(player: Player) -> None:
    """
    Affiche un aperçu simple des informations modifiable du joueur.
    """
    console.print("\n[bold]📋 Informations actuelles du joueur :[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Champ")
    table.add_column("Valeur", justify="center")

    for attr_key in FIELD_LABELS:
        label = FIELD_LABELS[attr_key]
        value = getattr(player, attr_key)
        table.add_row(label, value)

    console.print(table)


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


def show_player_main_menu() -> str:
    """
    Affiche le menu principal de la gestion des joueurs et attend le choix de l'utilisateur.

    Gestion des erreurs :
        Intercepte EOFError ou KeyboardInterrupt pour retourner à un état sûr.
    """
    try:
        return questionary.select(
            "---- MENU DES JOUEURS ----",
            choices=[
                "1. VOIR LES JOUEURS",
                "2. FILTRER / TRIER LES JOUEURS",
                "3. VOIR FICHE D'UN JOUEUR",
                "4. AJOUTER UN NOUVEAU JOUEUR",
                "5. RETOUR AU MENU PRINCIPAL"
            ]
        ).ask()[0]  # return the first character (e.g. '1')
    except (EOFError, KeyboardInterrupt):
        console.print("\n⛔ [red]Entrée interrompue. Retour au menu principal.[/red]")
        return "7"


def show_player_sort_filter_menu() -> str:
    """
    Affiche le menu pour trier ou filtrer les joueurs selon divers critères.

    Retour :
        str : Choix de l’utilisateur.
    """
    try:
        return questionary.select(
            "-- MENU DE FILTRAGE OU TRI DES JOUEURS  --",
            choices=[
                "1. TRIER PAR NOM (A-Z)",
                "2. TRIER PAR NOM (Z-A)",
                "3. TRIER PAR CLASSEMENT",
                "4. RECHERCHER UN JOUEUR PAR ID (PARTIEL)",
                "5. RECHERCHER UN JOUEUR PAR NOM",
                "6. VOIR LE FICHE D'UN JOUEUR",
                "7. RETOUR AU MENU DE GESTION DES JOUEURS",
                "8. QUITTER LE PROGRAMME"
            ]
        ).ask()[0]
    except (EOFError, KeyboardInterrupt):
        console.print("\n⛔ [red]Entrée interrompue. Retour au menu principal.[/red]")
        return "8"


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
    stats = player.get_stats_summary()

    table = Table(title=f"📇 Fiche de {player.first_name} {player.last_name}", show_lines=True)
    table.add_column("Champ", style="bold cyan")
    table.add_column("Valeur", style="white")

    # Données personnelles dynamiques
    label_map = {
        "Nom complet": f"{player.first_name} {player.last_name}",
        "ID national": player.national_id,
        "Date de naissance": player.birthdate,
        "Âge": str(player.age),
        "Date d'inscription": player.date_enrolled
    }
    for key, value in label_map.items():
        table.add_row(key, value)

    # Statistiques dynamiques
    for stat_label, value in stats.items():
        table.add_row(stat_label, str(value))

    console.print(table)


def display_user_action_menu_for_player_page(player: Player) -> str:
    """
    Affiche les actions possibles sur un joueur (fiche individuelle).

    Paramètre :
        player (Player) : Le joueur actuellement sélectionné.

    Retour :
        str : Choix de l’utilisateur.
    """
    try:
        return questionary.select(
            f"---- FICHE JOUEUR : {player.first_name} {player.last_name} (ID: {player.national_id}) ----",
            choices=[
                "1. MODIFIER LES INFO D'UN JOUEUR",
                "2. RETOUR AU MENU DES JOUEURS",
                "3. RETOUR AU MENU PRINCIPAL"
            ]
        ).ask()[0]
    except (EOFError, KeyboardInterrupt):
        console.print("\n⛔ [red]Entrée interrompue.[/red]")
        return "2"
