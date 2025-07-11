from typing import List, Dict
from models.player import Player
from models.round import Round

class Tournament:
    """
    Représente un tournoi d'échecs.

    Attributs :
        name (str) : Nom du tournoi.
        location (str) : Lieu du tournoi.
        start_date (str) : Date de début.
        end_date (str) : Date de fin.
        number_rounds (int) : Nombre de tours (défaut : 4).
        actual_round_number (int) : Numéro du tour en cours.
        players (List[Player]) : Liste des joueurs inscrits.
        rounds (List[Round]) : Liste des tours joués.
        player_scores (Dict[str, float]) : Scores individuels des joueurs dans ce tournoi.
        description (str) : Remarques du directeur du tournoi.
    """

    def __init__(
            self,
            name: str,
            location: str,
            start_date: str,
            end_date: str,
            description: str,
            number_rounds: int = 4
    ) -> None:
        self.name = name
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.number_rounds = number_rounds
        self.actual_round_number = 0
        self.players = List[Player] = []
        self.rounds = List[Round] = []

    def add_player(self, player: Player) -> None:
        """
        Ajoute un joueur à la liste des participants et initialise son score à 0.

        Paramètre :
            player (Player) : L'objet joueur à inscrire.
        """
        pass

    def start_first_round(self) -> Round:
        """
        Crée et retourne le premier tour du tournoi avec des paires aléatoires.

        Retour :
            Round : Instance du premier tour.
        """
        pass

    def start_next_round(self) -> Round:
        """
        Crée et retourne un tour basé sur les scores du tournoi.

        Retour :
            Round : Instance du tour suivant.
        """
        pass

    def update_scores_from_matches(self, tournament_round: Round) -> None:
        """
        Met à jour les scores des joueurs selon les résultats du tour donné.

        Paramètre :
            round (Round) : Le tour dont on veut extraire les résultats.
        """
        pass

    def determine_winner(self) -> Player:
        """
        Détermine le joueur avec le plus grand score dans le tournoi.

        Retour :
            Player : Le joueur gagnant.
        """
        pass

