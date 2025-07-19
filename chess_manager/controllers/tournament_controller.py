# Validate input
#
# Create a Tournament object
#
# Call TournamentRepository.add_tournament()
#
# Confirm success to the user

from chess_manager.views.tournament_views import  prompt_tournament_info
from chess_manager.models.tournament_models import Tournament
from chess_manager.models.tournament_repository import TournamentRepository

def handle_creation_of_tournament():
    """
    Gère le flux de création d’un nouveau tournoi depuis l’interface CLI.
    """
    print("=== Création d’un nouveau tournoi ===")

    tournament_data = prompt_tournament_info()

    tournament = Tournament(
        location=tournament_data["location"],
        start_date=tournament_data["start_date"],
        end_date=tournament_data["end_date"],
        description=tournament_data["description"],
        number_rounds=tournament_data["rounds"]
    )

    repository = TournamentRepository()
    repository.add_tournament(tournament)

    print(f"✅ Tournoi '{tournament.name}' créé et sauvegardé avec succès.")

def manage_tournament():
    """
    handles displays of tournament management view show_tournament_main_menu()
    """