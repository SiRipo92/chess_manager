from typing import Tuple, Dict
from chess_manager.models.player_models import Player


class Match:
    """
    Représente un match entre deux joueurs d’un tournoi.

    Attributs :
        player1 (Player) : Premier joueur.
        player2 (Player) : Deuxième joueur.
        score1 (float) : Score du joueur 1 (1.0, 0.5 ou 0.0).
        score2 (float) : Score du joueur 2 (1.0, 0.5 ou 0.0).
    """

    def __init__(self, player1: Player = None, player2: Player = None,
                 player1_id: str = None, player2_id: str = None) -> None:
        if player1 and player2:
            self.player1 = player1
            self.player2 = player2
            self.player1_id = player1.national_id
            self.player2_id = player2.national_id
        else:
            # Lightweight construction: just IDs for now
            self.player1 = None
            self.player2 = None
            self.player1_id = player1_id
            self.player2_id = player2_id

        self.score1 = 0.0
        self.score2 = 0.0

    def play_match(self, score1: float, score2: float) -> None:
        """
        Joue un match en enregistrant les scores des deux joueurs.

        Paramètres :
            score1 (float) : Score du joueur 1.
            score2 (float) : Score du joueur 2.
        """
        self.score1 = score1
        self.score2 = score2

    def get_result(self) -> Tuple[str, str]:
        """
        Retourne le résultat du match sous forme de tuple :
        ("win", "loss") ou ("draw", "draw"), etc.

        Retour :
            Tuple[str, str] : Résultats des deux joueurs.
        """
        pass

    def to_dict(self) -> Dict:
        """
        Sérialise le match en dictionnaire pour sauvegarde JSON.
        """
        return {
            "player1_id": self.player1_id,
            "player2_id": self.player2_id,
            "score1": self.score1,
            "score2": self.score2,
        }

    @classmethod
    def from_dict(cls, data: Dict, player_lookup: Dict[str, Player]) -> "Match":
        """
        Reconstruit un objet Match à partir de données JSON.
        """
        match = cls(player1_id=data["player1_id"], player2_id=data["player2_id"])
        match.score1 = data.get("score1", 0.0)
        match.score2 = data.get("score2", 0.0)
        return match
