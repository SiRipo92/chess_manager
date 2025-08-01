from chess_manager.controllers.main_controller import handle_club_menu
from chess_manager.controllers.player_controller import PlayerController
from chess_manager.controllers.tournament_repository_controller import load_players_for_tournament_group


def main():
    result = load_players_for_tournament_group()
    if result is None:
        # User selected "❌ QUITTER LE PROGRAMME" explicitly
        print("\n👋 Vous avez choisi de quitter le programme. Goodbye :) \n")
        return  # Exit cleanly

    city, filepath, players = result

    controller = PlayerController(players, filepath, city)
    handle_club_menu(controller)

if __name__ == "__main__":
    main()