from typing import List
from datetime import datetime
import json
from json.decoder import JSONDecodeError
from chess_manager.models.player_models import Player
from chess_manager.models.round_models import Round
from chess_manager.constants.datetime_formats import TIME_FORMAT


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
        self.start_time = ""
        self.end_time = ""
        self.is_completed = False
        self.winner_id = None
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

    def load_players_from_json(self, file_path:str) -> None:
        """
        Charge une liste de joueurs depuis un fichier JSON et les ajoute au tournoi.

        Paramètre :
            filepath (str) : Chemin du fichier JSON contenant les joueurs.

        Lève :
            ValueError si le fichier est vide ou les données sont mal formatées.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                if not isinstance(data, list):
                    raise ValueError("Le fichier JSON doit contenir une liste de joueurs.")

                for player_dict in data:
                    player = Player(
                        last_name=player_dict["last_name"],
                        first_name=player_dict["first_name"],
                        birthdate=player_dict["birthdate"],
                        national_id=player_dict["national_id"],
                        match_history=player_dict.get("match_history", []),
                        tournaments_won=player_dict.get("tournaments_won", 0)
                    )
                    self.players.append(player)

        except FileNotFoundError:
            print(f"❌ Fichier {file_path} introuvable.")
        except (JSONDecodeError, KeyError, ValueError) as e:
            print(f"❌ Erreur lors du chargement des joueurs : {e}")

    def start_a_tournament(self) -> None:
        """
        Marque le tournoi comme lancé et enregistre l'heure de début réelle (HH:MM).
        """
        self.start_time = datetime.now().strftime(TIME_FORMAT)

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

    def conclude_tournament(self, winner_id: str) -> None:
        """
        Marque le tournoi comme terminé, enregistre l’heure de fin et l’identifiant du gagnant.

        Paramètre :
            winner_id (str) : Identifiant national du joueur gagnant.
        """
        self.end_time = datetime.now().strftime(TIME_FORMAT)
        self.is_completed = True
        self.winner_id = winner_id


    def save_tournament_to_dict(self) -> dict:
        return {
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "description": self.description,
            "number_rounds": self.number_rounds,
            "current_round_number": self.current_round_number,
            "players": [p.to_dict() for p in self.players],
            "rounds": [r.to_dict() for r in self.rounds],
            "is_completed": self.is_completed,
            "winner_id": self.winner_id,
        }

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

    @staticmethod
    def from_dict(data: dict) -> "Tournament":
        tournament = Tournament(
            location=data["location"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            description=data["description"],
            number_rounds=data.get("number_rounds", 4)
        )
        tournament.current_round_number = data.get("current_round_number", 0)
        tournament.players = [Player.from_dict(p) for p in data.get("players", [])]
        tournament.rounds = [Round.from_dict(r) for r in data.get("rounds", [])]

        # Load completion state
        tournament.end_time = data.get("end_time", "")
        tournament.is_completed = data.get("is_completed", False)
        tournament.winner_id = data.get("winner_id", None)

        return tournament
