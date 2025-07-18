from chess_manager.views.main_views import display_main_menu
from chess_manager.views import player_views
from chess_manager.controllers.player_controller import PlayerController


def handle_main_menu(controller: PlayerController) -> None:
    """
    Gère l'affichage et la navigation du menu principal.

    Paramètre :
        controller (PlayerController) : Contrôleur principal pour la gestion des joueurs.
    """
    while True:
        choice = display_main_menu()

        if choice == "1":
            controller.manage_players()

        elif choice == "2":
            print("\n\U0001F6E0️ La gestion des tournois n'est pas encore disponible.")

        elif choice == "3":
            print("\n👋 Au revoir !")
            break

        else:
            player_views.display_error_message("Option invalide.")
