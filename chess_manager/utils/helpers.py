from rich.table import Table
from rich.console import Console
from chess_manager.constants.navigation import titles, labels
import questionary
from questionary import confirm
from typing import Optional

console = Console()

def raise_quit_program():
    """Affiche un message de sortie et termine le programme proprement."""
    console.print("\n👋 [bold red]Fermeture du programme...[/bold red]")
    raise SystemExit()


def display_club_menu_title(city: str) -> None:
    """
    Affiche le titre du menu de gestion de club avec le nom de la ville.
    """
    # MENU DE GESTION DU CLUB D’ÉCHECS À {city}
    menu_title = titles.CLUB_MANAGEMENT_MENU_TEMPLATE.format(city=city.upper())
    console.print(menu_title)


def display_club_general_info(city: str, num_players: int, num_tournaments: int = 0) -> None:
    """
    Affiche un tableau récapitulatif des infos du club sélectionné.

    Paramètres :
        city (str) : Nom de la ville.
        nb_joueurs (int) : Nombre de joueurs enregistrés.
        nb_tournois (int) : Nombre de tournois réalisés (non persistant).
    """
    table = Table(title=f"Infos générales sur le Club D'Échecs à {city.title()}", title_style="bold magenta")

    table.add_column("Clé", style="cyan", no_wrap=True)
    table.add_column("Valeur", style="white")

    table.add_row("Ville sélectionnée", city.title())
    table.add_row("Nombre de joueurs", str(num_players))
    table.add_row("Tournois complétés", str(num_tournaments))

    console.print(table)

def display_error_message(reason: str):
    """
    Affiche un message d'erreur avec une raison explicite.
    """
    console.print(f"❌ [red]Erreur : {reason}[/red]")

def prompt_field_with_validation(label: str, validate_func=None) -> Optional[str]:
    """
    Validates input prompts with set views/error messages
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

def ask_yes_no(prompt: str) -> str:
    """
    Ask a yes/no question and return the corresponding label.
    """
    result = confirm(prompt).ask()
    if result is None:
        # treat cancel/interrupt as a "no" (or adjust if you have a distinct sentinel)
        return labels.OPTION_NO
    return labels.OPTION_YES if result else labels.OPTION_NO
