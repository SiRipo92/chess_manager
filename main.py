"""
Point d'entrée principal du gestionnaire de tournois d'échecs.

Ce fichier initialise les composants nécessaires et lance l'ajout d'un joueur (US01).
"""

import os
from controllers.player_controller import PlayerController
from views.player_views import prompt_new_player, confirm_player_added, display_error_message

def main() -> None:
    print("♟️ Bienvenue dans le Chess Tournament Manager (v0.1)")
    print("---- Menu US01 : Ajout d’un joueur ----")

    # S'assure que le dossier data/ existe
    os.makedirs("data", exist_ok=True)

    # Initialise le contrôleur avec le chemin du fichier JSON
    controller = PlayerController(filepath="data/players.json")

    # Demande les informations du joueur
    last_name, first_name, birthdate, national_id = prompt_new_player()

    # Tente d'ajouter le joueur
    success = controller.add_player(last_name, first_name, birthdate, national_id)

    # Affiche un message selon le résultat
    if success:
        confirm_player_added()
    else:
        display_error_message("Format de l’identifiant invalide ou ID déjà existant.")

if __name__ == "__main__":
    main()
