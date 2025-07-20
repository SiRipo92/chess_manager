import os
from chess_manager.views import main_views
from chess_manager.views import player_views
from chess_manager.controllers.player_controller import PlayerController
from chess_manager.controllers.tournament_controller import handle_creation_of_tournament
from chess_manager.views.tournament_views import show_tournament_main_menu


def handle_main_menu(controller: PlayerController) -> None:
    """
    Gère l'affichage et la navigation du menu principal.

    Paramètre :
        controller (PlayerController) : Contrôleur principal pour la gestion des joueurs.
    """
    while True:
        choice = main_views.display_main_menu()

        if choice == "1":
            controller.manage_players()  # ✅ Use the method on the controller instance

        elif choice == "2":
            handle_creation_of_tournament()

        elif choice == "3":
            print("\n👋 Au revoir !")
            break

        else:
            player_views.display_error_message("Option invalide.")


def display_tournament_management_menu():
    """
    Affiche le menu de gestion de tournois et gère la navigation.
    """
    while True:
        choice = show_tournament_main_menu()

        if choice.startswith("1"):
            handle_creation_of_tournament()
        elif choice.startswith("2"):
            print("📋 Fonction d’affichage de tournoi à implémenter.")
        elif choice.startswith("3"):
            print("✅ Fonction de conclusion de tournoi à implémenter.")
        elif choice.startswith("4"):
            print("🔙 Retour au menu principal.")
            break


def display_locations_for_player_database(base_dir: str = "data/players") -> list[str]:
    """
    Retourne une liste triée des répertoires représentant les groupes de joueurs.
    """
    if not os.path.exists(base_dir):
        return []

    return sorted([
        name for name in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, name))
    ])
