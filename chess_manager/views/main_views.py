from rich.console import Console
import questionary
from chess_manager.constants.navigation.menu_keys import CLUB_MANAGEMENT_MENU
from chess_manager.utils.navigation.menu_builder import display_menu_from_key

console = Console()


def display_club_management_menu(city: str) -> str:
    """
    Affiche le menu de gestion du club d’échecs pour une ville donnée.
    Utilise la structure de menu dynamique avec un titre contextualisé.

    Args:
        city (str): Nom de la ville pour personnaliser le titre du menu.
    Returns:
        str | None: L'option sélectionnée ou None si annulée.
    """
    console.print(f"\n[bold cyan]---- MENU DE GESTION DU CLUB À {city.upper()} ----[/bold cyan]")
    return display_menu_from_key(menu_key=CLUB_MANAGEMENT_MENU, city=city)
