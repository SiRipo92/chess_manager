from typing import Tuple

class Match:
    """
    Représente un match entre deux joueurs.

    Attributs :
        player1_id (str) : Identifiant du premier joueur (référence à Player.national_id).
        player2_id (str) : Identifiant du deuxième joueur (référence à Player.national_id).
        score1 (float) : Score du joueur 1 (1.0, 0.5 ou 0.0).
        score2 (float) : Score du joueur 2 (1.0, 0.5 ou 0.0).
    """

    def __init__(self, player1_id: str, player2_id: str) -> None:
        self.player1_id = player1_id
        self.player2_id = player2_id

        # Scores par defaut (match non-joué)
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
        """Retourne ('win', 'loss') ou ('draw', 'draw') selon les scores."""
        pass