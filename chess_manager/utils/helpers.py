from rich.table import Table
from rich.console import Console
from chess_manager.constants.navigation.titles import CLUB_MANAGEMENT_MENU_TEMPLATE

console = Console()

def display_club_menu_title(city: str) -> None:
    """
    Affiche le titre du menu de gestion de club avec le nom de la ville.
    """
    # MENU DE GESTION DU CLUB D’ÉCHECS À {city}
    menu_title = CLUB_MANAGEMENT_MENU_TEMPLATE.format(city=city.upper())
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
