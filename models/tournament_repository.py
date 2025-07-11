from typing import List
from models.tournament import Tournament

class TournamentRepository:
    """
    Repository class responsible for managing Tournament data.

    Attributes:
        dir_path (str): Directory where tournament JSON files are stored.
        tournaments (List[Tournament]): List of loaded tournaments.
    """

    def __init__(self, dir_path: str) -> None:
        self.dir_path: str = dir_path
        self.tournaments: List[Tournament] = []

    def save_tournament(self, tournament: Tournament) -> None:
        """Save a Tournament instance to a JSON file."""
        pass

    def load_all_tournaments(self) -> None:
        """Load all tournaments from the specified directory."""
        pass

    def get_tournament_by_name(self, name: str) -> Tournament:
        """Retrieve a tournament by its name."""
        pass

    def get_tournament_by_location(self, location: str) -> List[Tournament]:
        """Retrieve tournaments held in a specific location."""
        pass

    def get_all_tournaments(self) -> List[Tournament]:
        """Return all tournaments loaded in memory."""
        pass