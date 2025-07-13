from typing import Tuple, Dict
from models.player import Player

class Match:
    """
    Représente un match entre deux joueurs d’un tournoi.

    Attributs :
        player1 (Player) : Premier joueur.
        player2 (Player) : Deuxième joueur.
        score1 (float) : Score du joueur 1 (1.0, 0.5 ou 0.0).
        score2 (float) : Score du joueur 2 (1.0, 0.5 ou 0.0).
    """

    def __init__(self, player1: Player, player2: Player) -> None:
        self.player1 = player1
        self.player2 = player2
        self.score1 = 0.0
        self.score2 = 0.0

    def play_match(self, score1: float, score2: float) -> None:
        """
        Joue un match en enregistrant les scores des deux joueurs.

        Paramètres :
            score1 (float) : Score du joueur 1.
            score2 (float) : Score du joueur 2.
        """
        pass

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

        Retour :
            dict : Représentation du match.
        """
        pass

    @classmethod
    def from_dict(cls, data: Dict, player_lookup: Dict[str, Player]) -> "Match":
        """
        Reconstruit un objet Match à partir de données JSON.

        Paramètres :
            data (dict) : Données du match.
            player_lookup (dict) : Dictionnaire des joueurs {national_id: Player}.

        Retour :
            Match : Instance reconstruite.
        """
        pass
