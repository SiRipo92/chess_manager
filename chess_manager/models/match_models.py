from __future__ import annotations

from typing import Optional, Tuple, Dict
from chess_manager.models.player_models import Player
from chess_manager.constants.match_results import MATCH_RESULT_CODES, MATCH_RESULT_POINTS


class Match:
    """
    Représente un match entre deux joueurs.

    Attributs :
        player1 (Player) : Premier joueur.
        player2 (Optional[Player]) : Second joueur, peut être None si 'bye'.
        score1 (float) : Score du joueur 1 (1.0, 0.5, 0.0).
        score2 (float) : Score du joueur 2 (1.0, 0.5, 0.0). 0.0 si 'bye'.
        is_exempt (bool) : True si le match est un 'exempt' (joueur2 absent).

    """

    def __init__(self, player1: Player, player2: Optional[Player], is_exempt: bool = False) -> None:
        self.player1 = player1
        self.player2 = player2   # Will be "none" if exempt

        # Scores numériques
        self.score1: float = 0.0
        self.score2: float = 0.0

        # Résultats des matchs
        self.result1: Optional[str] = None  # 'victoire' | 'défaite' | 'nul' | 'exempt' | None
        self.result2: Optional[str] = None

        # Applique automatiquement l'exempt si besoin
        if self.is_exempt:
            self._auto_set_exempt()

    @property
    def is_exempt(self) -> bool:
        """True si aucun adversaire assigné (player2 is None)."""
        return self.player2 is None

    def _auto_set_exempt(self) -> None:
        """
        Attribue automatiquement l’exempt au joueur 1 :
        - result1 = 'exempt' (1.0 point)
        - result2 = None, score2 = 0.0 (il n'y a pas de joueur 2)
        """
        self.result1 = "exempt"
        self.score1 = MATCH_RESULT_POINTS["exempt"]  # généralement 1.0
        self.result2 = None
        self.score2 = 0.0

    def play_match(self, score1: float, score2: float) -> None:
        """
        Variante numérique : définit le résultat à partir de scores (1.0/0.0 ou 0.5/0.5).
        Utilisez plutôt set_result_by_code dans l’IHM si possible.
        """
        if self.is_exempt:
            self._auto_set_exempt()
            return

        # Normalise et vérifie les combinaisons valides
        s1, s2 = float(score1), float(score2)
        if (s1, s2) == (1.0, 0.0):
            self.result1, self.result2 = "victoire", "défaite"
        elif (s1, s2) == (0.0, 1.0):
            self.result1, self.result2 = "défaite", "victoire"
        elif (s1, s2) == (0.5, 0.5):
            self.result1 = self.result2 = "nul"
        else:
            raise ValueError("Scores invalides. Utilisez (1.0,0.0), (0.0,1.0) ou (0.5,0.5).")

        self.score1, self.score2 = s1, s2

    def set_result_by_code(self, code_for_p1: str) -> None:
        """
        Définit le résultat via un code pour player1 :
        - 'V' => player1 victoire / player2 défaite
        - 'D' => player1 défaite / player2 victoire
        - 'N' => nul / nul
        - 'E' => exempt (utile si vous voulez forcer un exempt manuellement)
        """
        code = (code_for_p1 or "").strip().upper()
        label = MATCH_RESULT_CODES.get(code)
        if not label:
            raise ValueError("Code résultat invalide. Utilisez V, D, N (ou E pour exempt).")

        if label == "exempt":
            # Même sur un match normal, si on force 'E' on applique l'exempt (sécurité/ui)
            self._auto_set_exempt()
            return

        if self.is_exempt:
            # Sécurité : un match bye ne doit pas recevoir V/D/N ; on garde l'exempt.
            self._auto_set_exempt()
            return

        # Affecte les labels symétriques
        if label == "victoire":
            self.result1, self.result2 = "victoire", "défaite"
        elif label == "défaite":
            self.result1, self.result2 = "défaite", "victoire"
        else:  # 'nul'
            self.result1 = self.result2 = "nul"

        # Déduit les points depuis la table
        self.score1 = MATCH_RESULT_POINTS[self.result1]
        self.score2 = MATCH_RESULT_POINTS[self.result2]

    def get_result(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Retourne les libellés de résultat ('victoire' | 'défaite' | 'nul' | 'exempt' | None)
        pour (player1, player2).
        """
        return self.result1, self.result2

    def to_dict(self) -> Dict:
        """Sérialise le match pour stockage JSON."""
        return {
            "player1": self.player1.national_id,
            "player2": self.player2.national_id if self.player2 else None,
            "score1": self.score1,
            "score2": self.score2,
            "result1": self.result1,
            "result2": self.result2,
        }

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
        p1 = player_lookup[data["player1"]]
        p2 = player_lookup.get(data.get("player2")) if data.get("player2") else None
        match = cls(p1, p2)
        # Recharger les résultats si déjà joués
        match.score1 = data.get("score1", 0.0)
        match.score2 = data.get("score2", 0.0)
        match.result1 = data.get("result1")
        match.result2 = data.get("result2")
        return match
