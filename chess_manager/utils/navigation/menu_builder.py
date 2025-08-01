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
from chess_manager.utils.navigation.menu_map import MENU_REGISTRY
from chess_manager.constants.navigation import labels, titles

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
    Affiche dynamiquement un menu à partir de MENU_REGISTRY.

    Args:
        menu_key (str): Clé du menu.
        city (str, optional): Ville (pour menus dynamiques).
        log_errors (bool): Active les logs d’erreurs.
        custom_title (str): Titre forcé.

    Returns:
        str | None: Option choisie ou None si échappée.
    """
    def log_error(message: str):
        if log_errors:
            logging.error(message)

    try:
        menu_data = MENU_REGISTRY.get(menu_key)
        if not menu_data:
            raise KeyError(f"Menu inconnu pour la clé '{menu_key}'")

        # Titre dynamique
        if custom_title:
            title = custom_title
        elif menu_key == "club_management_menu":
            if not city:
                raise ValueError("Le menu 'club_management_menu' nécessite un nom de ville.")
            title = titles.CLUB_MANAGEMENT_MENU_TEMPLATE.format(city=city.upper())
        else:
            title = menu_data["title"]

        console.print(title)
        console.print(labels.INSTRUCTION_UTILISER_FLECHES, style="yellow")

        selected = questionary.select(
            "Que souhaitez-vous faire ?",
            choices=menu_data["choices"]
        ).ask()

        if selected is None:
            console.print("[bold yellow]Action annulée par l'utilisateur.[/bold yellow]")
        return selected

    except Exception as e:
        error_msg = f"[Menu Error] {str(e)}"
        console.print(Panel(f"[bold red]{error_msg}[/bold red]", title="Erreur menu", style="red"))
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
        console.print(labels.INSTRUCTION_UTILISER_FLECHES, style="yellow")

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

# ======================
# Menu Construction Utility functions
# ======================

def is_escape_option_from_key(option: str, menu_key: str) -> bool:
    return option in MENU_REGISTRY.get(menu_key, {}).get("escape_actions", [])

def handle_menu_from_key(menu_key: str, escape_sequence: list[str], city: str = None) -> str | None:
    """
    Affiche un menu via sa clé et retourne le choix si ce n’est pas une sortie.

    Args:
        menu_key (str): Clé interne du menu.
        escape_sequence (list[str]): Options considérées comme échappement.
        city (str): Nom de ville si nécessaire (pour menus dynamiques).

    Returns:
        str | None: L’option choisie si elle ne fait pas partie d’une séquence d’échappement.
                    Sinon, retourne None.
    """
    selected = display_menu_from_key(menu_key, city=city)
    if selected in escape_sequence:
        return None
    return selected
