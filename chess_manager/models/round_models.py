from datetime import datetime
from typing import List, Dict
from chess_manager.models.match_models import Match


class Round:
    """
    Représente un tour d’un tournoi d’échecs.

    Attributs :
        start_time (str) : Date et heure de début du tour (format ISO).
        end_time (str) : Date et heure de fin du tour (format ISO).
        matches (List[Match]) : Liste des matchs de ce tour.
    """

    def __init__(self, round_number: int) -> None:
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
        self.matches.append(match)

    def end_round(self) -> None:
        """
        Marque la fin du tour en enregistrant l’heure actuelle comme heure de fin.
        """
        self.end_time = datetime.now().isoformat()

    def play_all_matches(self) -> None:
        """
        Exécute tous les matchs du tour (simulation ou saisie manuelle des résultats).
        À implémenter : logique de simulation ou saisie manuelle.
        """
        # Placeholder. Implement when scoring logic enters scope.
        for match in self.matches:
            pass  # no-op

    def to_dict(self) -> Dict:
        """
        Sérialise l’objet Round en dictionnaire pour stockage JSON.

        Retour :
            dict : Représentation sérialisée du tour.
        """
        return {
            "round_number": self.round_number,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "matches": [match.to_dict() for match in self.matches],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Round":
        round_instance = cls(round_number=data["round_number"])
        round_instance.start_time = data.get("start_time", "")
        round_instance.end_time = data.get("end_time", "")
        round_instance.matches = [Match.from_dict(m) for m in data.get("matches", [])]
        return round_instance
