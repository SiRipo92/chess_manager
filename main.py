import os
from chess_manager.controllers.player_controller import PlayerController
from chess_manager.controllers.main_controller import handle_main_menu


def main() -> None:
    """
    Point d'entrée principal de l'application. Initialise le contrôleur principal et démarre le menu.
    """
    print("\n\u265F\ufe0f Bienvenue dans le Chess Tournament Manager (v0.1)")
    os.makedirs("data", exist_ok=True)
    player_controller = PlayerController(file_path="data/players.json")

    handle_main_menu(player_controller)


if __name__ == "__main__":
    main()
