from questionary import Choice, select
from typing import List
from rich.console import Console
from chess_manager.constants.navigation import labels, titles

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
            Choice(title=labels.OPTION_CREATE_NEW_PLAYERS_FILE),
            Choice(title=labels.OPTION_IMPORT_FILE),
            Choice(title=labels.OPTION_QUIT_PROGRAM),
        ]

        # 3. Affiche un message s’il n’y a aucun groupe existant
        if not existing_locations:
            console.print("\n[yellow]⚠️ Aucun groupe de joueurs trouvé.[/yellow]")
            return select(
                "Aucune base de joueurs disponible. Que souhaitez-vous faire ?",
                choices=action_choices
            ).ask()

        # 4. Affiche le menu complet : villes + actions
        console.print(titles.STARTING_TITLE_FOR_EXISTING_PLAYER_DATA)
        console.print(labels.INSTRUCTION_UTILISER_FLECHES, style="yellow")

        return select(
            "Choisissez un groupe existant ou une action :",
            choices=city_choices + action_choices
        ).ask()

    except (EOFError, KeyboardInterrupt):
        console.print(labels.USER_CANCEL_MESSAGE, style="red")
        return None
