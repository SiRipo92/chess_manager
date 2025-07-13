from datetime import datetime
from typing import List, Dict
from models.match import Match

class Round:
    """
    Représente un tour d’un tournoi d’échecs.

    Attributs :
        start_time (str) : Date et heure de début du tour (format ISO).
        end_time (str) : Date et heure de fin du tour (format ISO).
        matches (List[Match]) : Liste des matchs de ce tour.
    """

    def __init__(self, round_number:int) -> None:
        self.round_number = round_number
        self.start_time = datetime.now().isoformat()
        self.end_time = ""
        self.matches: List[Match] = []

    @property
    def name(self) -> str:
        """
        Génère un nom automatique pour le tour (ex: "Round 1").
        """
        return f"Round {self.round_number}"

    def add_match(self, match: Match) -> None:
        """
        Ajoute un match à la liste des matchs de ce tour.

        Paramètre :
            match (Match) : Le match à ajouter.
        """
        pass

    def end_round(self) -> None:
        """
        Marque la fin du tour en enregistrant l’heure actuelle comme heure de fin.
        """
        pass

    def play_all_matches(self) -> None:
        """
        Exécute tous les matchs du tour (simulation ou saisie manuelle des résultats).
        """
        pass

    def to_dict(self) -> Dict:
        """
        Sérialise l’objet Round en dictionnaire pour stockage JSON.

        Retour :
            dict : Représentation sérialisée du tour.
        """
        pass

    @classmethod
    def from_dict(cls, data: Dict) -> "Round":
        """
        Crée une instance de Round à partir d’un dictionnaire (données JSON).

        Paramètre :
            data (dict) : Données sérialisées du tour.

        Retour :
            Round : Instance reconstituée.
        """
        pass