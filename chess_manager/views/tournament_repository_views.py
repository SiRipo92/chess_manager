import questionary
from questionary import Choice, select
from typing import List
from rich.console import Console
from chess_manager.constants.tournament_repository import (
    OPTION_ADD_PLAYERS,
    OPTION_IMPORT_PLAYERS,
    OPTION_QUIT
)
from chess_manager.constants.navigation.labels import (
    INSTRUCTION_UTILISER_FLECHES,
    USER_CANCEL_MESSAGE,
)
console = Console()



def prompt_user_for_location_selection(existing_locations: List[str]) -> str | None:
    """
    Affiche les groupes de joueurs (en MAJUSCULES) + actions (sans couleurs).
    Retourne une chaîne représentant soit un nom de ville, soit une action.
    """

    # Format city names in uppercase and match value
    try:
        # 1. Crée les choix de villes
        city_choices = [
            Choice(title=city.upper(), value=city.upper())
            for city in sorted(existing_locations)
        ]

        # 2. Crée les actions disponibles
        action_choices = [
            Choice(title=OPTION_ADD_PLAYERS, value=OPTION_ADD_PLAYERS),
            Choice(title=OPTION_IMPORT_PLAYERS, value=OPTION_IMPORT_PLAYERS),
            Choice(title=OPTION_QUIT, value=OPTION_QUIT),
        ]

        # 3. Affiche un message s’il n’y a aucun groupe existant
        if not existing_locations:
            console.print("\n[yellow]⚠️ Aucun groupe de joueurs trouvé.[/yellow]")
            return select(
                "Aucune base de joueurs disponible. Que souhaitez-vous faire ?",
                choices=action_choices
            ).ask()

        # 4. Affiche le menu complet : villes + actions
        console.print("\n[bold cyan]--- SÉLECTION DU GROUPE DE JOUEURS ---[/bold cyan]")
        console.print(INSTRUCTION_UTILISER_FLECHES, style="yellow")

        return select(
            "Choisissez un groupe existant ou une action :",
            choices=city_choices + action_choices
        ).ask()

    except (EOFError, KeyboardInterrupt):
        console.print(USER_CANCEL_MESSAGE, style="red")
        return None
