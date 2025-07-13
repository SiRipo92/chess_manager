from typing import List, Dict
from models.player import Player
from models.round import Round

class Tournament:
    """
    Représente un tournoi d'échecs.

    Attributs :
        location (str) : Lieu du tournoi.
        start_date (str) : Date de début (format YYYY-MM-DD).
        end_date (str) : Date de fin (format YYYY-MM-DD).
        number_rounds (int) : Nombre total de tours (défaut : 4).
        current_round_number (int) : Numéro du tour actuel.
        description (str) : Commentaires du directeur.
        players (List[Player]) : Liste des joueurs inscrits.
        rounds (List[Round]) : Liste des tours du tournoi.
    """

    def __init__(
        self,
        location: str,
        start_date: str,
        end_date: str,
        description: str,
        number_rounds: int = 4
    ) -> None:
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.number_rounds = number_rounds
        self.current_round_number = 0
        self.players: List[Player] = []
        self.rounds: List[Round] = []

    @property
    def name(self) -> str:
        """
        Génère automatiquement le nom du tournoi à partir du lieu et de la date.
        Exemple : "Paris_2025-07-01"
        """
        return f"{self.location}_{self.start_date}"

    def add_player_to_tournament(self, player: Player) -> None:
        """
        Ajoute un joueur à la liste des participants.

        Paramètre :
            player (Player) : L'objet joueur à inscrire.
        """
        pass

    def start_first_round(self) -> Round:
        """
        Démarre le premier tour avec des paires aléatoires.

        Retour :
            Round : Le premier tour créé.
        """
        pass

    def start_next_round(self) -> Round:
        """
        Démarre un nouveau tour en fonction du classement actuel.

        Retour :
            Round : Le nouveau tour créé.
        """
        pass

    def update_scores_from_matches(self, tournament_round: Round) -> None:
        """
        Met à jour les scores des joueurs en fonction des résultats du tour.

        Paramètre :
            tournament_round (Round) : Le tour concerné.
        """
        pass

    def determine_winner(self) -> Player:
        """
        Retourne le joueur avec le score le plus élevé.

        Retour :
            Player : Le gagnant du tournoi.
        """
        pass

    def save_tournament_to_dict(self) -> Dict:
        """
        Sérialise le tournoi sous forme de dictionnaire pour l’enregistrement JSON.

        Retour :
            dict : Représentation sérialisée du tournoi.
        """
        pass

    @staticmethod
    def load_all_tournaments(filepath: str) -> List["Tournament"]:
        """
        Charge tous les tournois sauvegardés depuis un fichier JSON.

        Paramètre :
            filepath (str) : Chemin du fichier.
        Retour :
            List[Tournament] : Liste des objets tournoi.
        """
        pass
