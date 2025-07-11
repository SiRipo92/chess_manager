from typing import List
from models.match import Match
from datetime import datetime

class Round:
    """
    Représente un tour dans un tournoi.

    Attributs :
        name (str) : Nom du tour (ex : "Round 1").
        matches (List[Match]) : Liste des matchs dans ce tour.
        start_time (str) : Date et heure de début du tour (format ISO).
        end_time (str) : Date et heure de fin du tour (format ISO ou None).
    """

    def __init__(self, name: str, matches: List[Match]) -> None:
        self.name = name
        self.matches = matches
        self.start_time = datetime.now().isoformat()
        self.end_time = None

    def add_match(self, match: Match) -> None:
        """
        Ajoute un match à la liste des matchs du tour.

        Paramètre :
            match (Match) : Le match à ajouter.
        """
        pass

    def end_round(self) -> None:
        """
        Marque la fin du tour en enregistrant l'heure actuelle.
        """
        pass

    def play_all_matches(self) -> None:
        """
        Joue tous les matchs contenus dans ce tour.
        """
        pass