from chess_manager.views.main_views import display_main_menu
from chess_manager.views import player_views
from chess_manager.models.player import Player
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
            manage_players(controller)  # ✅ Correct

        elif choice == "2":
            print("\n\U0001F6E0️ La gestion des tournois n'est pas encore disponible.")

        elif choice == "3":
            print("\n👋 Au revoir !")
            break

        else:
            player_views.display_error_message("Option invalide.")


def manage_players(controller: PlayerController) -> None:
    """
    Gère la navigation du sous-menu de gestion des joueurs.
    """
    while True:
        subchoice = player_views.show_player_main_menu()

        if subchoice == "1":
            players = controller.load_all_players()
            player_views.display_all_players(players)

        elif subchoice == "2":
            result = handle_player_sort_filter_menu(controller)
            if result == "return_to_main":
                return
            elif result == "return_to_players":
                continue

        elif subchoice == "3":
            player_id = player_views.prompt_player_national_id()
            player = controller.get_player_by_id(player_id)
            if not player:
                player_views.display_error_message("Aucun joueur trouvé avec cet ID.")
            else:
                player_views.display_player_identity(player)

                # ✅ Capture action result
                action_result = handle_player_actions(controller, player)

                if action_result == "return_to_main":
                    return  # Exit to main menu

                # Else, return to manage_players loop

        elif subchoice == "4":
            last_name, first_name, birthdate, national_id = player_views.prompt_new_player()
            success = controller.add_new_player(last_name, first_name, birthdate, national_id)
            if success:
                player_views.confirm_player_added()
            else:
                player_views.display_error_message("Format de l’identifiant invalide ou ID déjà existant.")

        elif subchoice == "5":
            break  # Go back to main menu

        else:
            player_views.display_error_message("Option invalide.")

def handle_player_actions(controller: PlayerController, player: Player) -> str:
    """
    Affiche le menu d'action pour un joueur sélectionné.

    Paramètre :
        controller (PlayerController) : Contrôleur de gestion des joueurs.
        player (Player) : Le joueur actuellement sélectionné.

    Retour :
        str : 'return_to_players' ou 'return_to_main'
    """
    while True:
        action = player_views.display_player_action_menu(player) # makes it context visible to player

        if action == "1":
            print("🛠️ Fonction de modification à implémenter.")

        elif action == "2":
            try:
                stats = player.get_stats_summary(None)
                player_views.display_player_stats(stats)
            except Exception as e:
                player_views.display_error_message(f"Erreur lors de l'affichage des stats : {e}")

        elif action == "3":
            controller.record_match_for_player()

        elif action == "4":
            return "return_to_players"

        elif action == "5":
            return "return_to_main"

        else:
            player_views.display_error_message("Option invalide.")


def handle_player_sort_filter_menu(controller: PlayerController) -> str:
    """
    Affiche le menu de tri/filtrage et retourne vers le menu précédent ou quitte.
    """
    while True:
        players = controller.load_all_players()
        choice = player_views.show_player_sort_filter_menu()

        if choice == "1":
            sorted_players = controller.sort_players_by_name(players)
            player_views.display_all_players(sorted_players)

        elif choice == "2":
            sorted_players = controller.sort_players_by_name(players, reverse=True)
            player_views.display_all_players(sorted_players)

        elif choice == "3":
            ranked_players = controller.sort_players_by_ranking(players)
            player_views.display_all_players(ranked_players)

        elif choice == "4":
            partial_id = player_views.prompt_player_national_id("Entrez une partie de l’ID à rechercher : ")
            filtered_players = controller.find_players_by_id(players, partial_id)
            player_views.display_all_players(filtered_players)

        elif choice == "5":
            partial_name = player_views.prompt_player_name_filter()
            filtered_players = controller.find_players_by_name(players, partial_name)
            player_views.display_all_players(filtered_players)


        elif choice == "6":

            player_id = player_views.prompt_player_national_id()
            player = controller.get_player_by_id(player_id)

            if player:
                player_views.display_player_identity(player)
                result = handle_player_actions(controller, player)
                if result == "return_to_main":
                    return "return_to_main"
                elif result == "return_to_players":
                    return "return_to_players"

            else:
                player_views.display_error_message("Aucun joueur trouvé avec cet ID.")

        elif choice == "7":
            return "return_to_players"

        elif choice == "8":
            exit()

        else:
            player_views.display_error_message("Option invalide.")
