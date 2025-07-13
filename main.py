"""
Point d'entrée principal du gestionnaire de tournois d'échecs.

Ce fichier initialise les composants nécessaires et lance l'ajout d'un joueur (US01).
"""

import os
from chess_manager.controllers.player_controller import PlayerController
from chess_manager.views.player_views import (
    prompt_new_player,
    confirm_player_added,
    display_error_message,
    display_all_players,
    prompt_id_filter
)
from chess_manager.views.main_views import display_main_menu, display_filter_sort_menu


def main() -> None:
    print("♟️ Bienvenue dans le Chess Tournament Manager (v0.1)")
    os.makedirs("data", exist_ok=True)
    controller = PlayerController(filepath="data/players.json")

    while True:
        choice = display_main_menu()

        if choice == "1":
            last_name, first_name, birthdate, national_id = prompt_new_player()
            success = controller.add_player(last_name, first_name, birthdate, national_id)
            confirm_player_added() if success else display_error_message(
                "Format de l’identifiant invalide ou ID déjà existant.")

        elif choice == "2":
            players = controller.load_all_players()
            display_all_players(players)

        elif choice == "3":
            players = controller.load_all_players()
            sub_choice = display_filter_sort_menu()
            if sub_choice == "1":
                sorted_players = controller.sort_players_by_name(players)
                display_all_players(sorted_players)
            elif sub_choice == "2":
                partial_id = prompt_id_filter()
                filtered_players = controller.filter_players_by_id(players, partial_id)
                display_all_players(filtered_players)
            else:
                display_error_message("Option invalide.")

        elif choice == "4":
            print("👋 Au revoir !")
            break

        else:
            display_error_message("Option invalide.")


if __name__ == "__main__":
    main()
