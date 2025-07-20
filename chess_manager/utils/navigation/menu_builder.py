"""
Menu Builder — Assemble and display menus using slugs, titles, and choices.

This module centralizes logic for rendering any menu based on internal keys.
Now includes optional error logging.
"""

import os
import logging
from rich.console import Console
from rich.panel import Panel
import questionary

from chess_manager.constants.navigation.titles import (
    MENU_TITLES,
    CLUB_MANAGEMENT_MENU_TEMPLATE,
)
from chess_manager.constants.navigation.labels import INSTRUCTION_UTILISER_FLECHES
from chess_manager.utils.navigation.menu_map import MENU_STRUCTURE

console = Console()

# ─────────────────────────────────────────────────────────
# OPTIONAL LOGGER SETUP
# ─────────────────────────────────────────────────────────

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "menu_errors.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# ─────────────────────────────────────────────────────────
# MENU RENDERING FUNCTION
# ─────────────────────────────────────────────────────────

def display_menu_from_key(menu_key: str,
    city: str = None,
    log_errors: bool = False,
    custom_title: str = None
    ) -> str | None:
    """
    Displays a menu dynamically based on its internal key and returns the selected option.

    Args:
        menu_key (str): Internal menu slug (e.g., 'starting_menu', 'player_file').
        city (str, optional): Required for club management menu titles.
        log_errors (bool): If True, logs any errors to a file.
        custom_title (str, optional): Optional custom title for menu titles.
    Returns:
        str | None: The selected option string, or None if user cancels or error occurs.
    """

    def log_error(message: str):
        if log_errors:
            logging.error(message)

    # 2. Dynamic or static title rendering
    try:
        if custom_title:
            title = custom_title
        elif menu_key == "club_management_menu":
            if not city:
                error_msg = "Missing city name for club_management_menu"
                console.print(Panel("[bold red]Une ville est requise pour ce menu.[/bold red]", title="Ville manquante",
                                    style="red"))
                log_error(error_msg)
                return None
            title = CLUB_MANAGEMENT_MENU_TEMPLATE.format(city=city.upper())
        else:
            title = MENU_TITLES.get(menu_key)
            if not title:
                raise KeyError(f"Title not found for menu_key '{menu_key}'")
    except Exception as e:
        error_msg = f"Failed to render title for '{menu_key}': {str(e)}"
        console.print(Panel(f"[bold red]{error_msg}[/bold red]", title="Erreur titre", style="red"))
        log_error(error_msg)
        return None

# Display Contextual Menus with added features
def display_contextual_menu(
    title: str,
    choices: list[str],
    log_errors: bool = False
) -> str | None:
    """
    Affiche un menu contextuel personnalisé (par ex. fiche joueur).

    Args:
        title (str): Titre à afficher dans le menu (peut contenir des données dynamiques).
        choices (list[str]): Liste d’options.
        log_errors (bool): Active la journalisation en cas d’erreur.

    Returns:
        str | None: Choix de l'utilisateur ou None si annulé.
    """
    try:
        console.print(title)
        console.print(INSTRUCTION_UTILISER_FLECHES, style="yellow")

        selected = questionary.select(
            "Que souhaitez-vous faire ?",
            choices=choices
        ).ask()

        if selected is None:
            console.print("[bold yellow]Action annulée par l'utilisateur.[/bold yellow]")
        return selected

    except Exception as e:
        if log_errors:
            logging.error(f"Erreur lors de l'affichage du menu contextuel : {str(e)}")
        console.print(Panel(
            f"[bold red]{str(e)}[/bold red]",
            title="Erreur interne",
            style="red"
        ))
        return None
