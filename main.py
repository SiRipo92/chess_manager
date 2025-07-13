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
    display_all_players
)


def main() -> None:
    print("♟️ Bienvenue dans le Chess Tournament Manager (v0.1)")
    os.makedirs("data", exist_ok=True)
    controller = PlayerController(filepath="data/players.json")

    while True:
        print("\nMenu principal :")
        print("1. Ajouter un joueur (US01)")
        print("2. Voir la liste des joueurs (US02)")
        print("3. Quitter")
        choice = input("Choix : ")

        if choice == "1":
            last_name, first_name, birthdate, national_id = prompt_new_player()
            success = controller.add_player(last_name, first_name, birthdate, national_id)
            if success:
                confirm_player_added()
            else:
                display_error_message("Format de l’identifiant invalide ou ID déjà existant.")

        elif choice == "2":
            players = controller.load_all_players()
            display_all_players(players)

        elif choice == "3":
            print("👋 Au revoir !")
            break

        else:
            display_error_message("Choix invalide. Veuillez sélectionner 1, 2 ou 3.")


if __name__ == "__main__":
    main()
