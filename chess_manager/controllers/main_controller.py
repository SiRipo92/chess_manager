import os
from rich.console import Console

from chess_manager.constants.navigation.labels import OPTION_CREATE_NEW_PLAYERS_FILE, OPTION_RETURN_TO_PLAYERS_MENU
from chess_manager.views import main_views
from chess_manager.views import player_views
from chess_manager.controllers.player_controller import PlayerController
from chess_manager.controllers.tournament_controller import handle_creation_of_tournament
from chess_manager.views.tournament_views import show_tournament_main_menu
from chess_manager.controllers.tournament_repository_controller import MENU_ACTIONS
from chess_manager.constants.navigation import labels
from chess_manager.utils.helpers import raise_quit_program

console = Console()

def handle_club_menu(controller: PlayerController) -> None:
    """
    Gère l'affichage et la navigation du menu principal aprés
    qu'un club d'une ville a été saisi.

    Paramètre :
        controller (PlayerController) : Contrôleur principal pour la gestion des joueurs.
    """
    while True:
        choice = main_views.display_club_management_menu(controller.city)
        if choice == labels.OPTION_MANAGE_PLAYERS:
            controller.manage_players()

        elif choice == labels.OPTION_MANAGE_TOURNAMENTS:
            handle_creation_of_tournament()

        elif choice == labels.OPTION_QUIT_PROGRAM:
            raise_quit_program()

        else:
            player_views.display_error_message("Option invalide.")


def handle_tournament_management_menu():
    """
    Affiche le menu de gestion de tournois et gère la navigation.
    """
    while True:
        choice = show_tournament_main_menu()

        if choice.startswith(OPTION_CREATE_NEW_PLAYERS_FILE):
            handle_creation_of_tournament()
        elif choice.startswith(""):
            print("📋 Fonction d’affichage de tournoi à implémenter.")
        elif choice.startswith(""):
            print("✅ Fonction de conclusion de tournoi à implémenter.")
        elif choice.startswith(labels.OPTION_RETURN_TO_STARTING_MENU):
            print("🔙 Retour au menu principal.")
            break


def handle_locations_for_player_database(base_dir: str = "data/players") -> list[str]:
    """
    Retourne une liste triée des répertoires représentant les groupes de joueurs.
    """
    if not os.path.exists(base_dir):
        return []

    return sorted([
        name for name in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, name))
    ])

def handle_menu_selection(selected_option: str):
    action = MENU_ACTIONS.get(selected_option)
    if callable(action):
        return action()
    else:
        console.print(f"[red]Aucune action définie pour : {selected_option}[/red]")
        return None