from datetime import datetime
from typing import List, Optional
import json

class Player:
    """
    Représente un joueur d'échecs dans le système.

    Attributs :
        last_name (str) : Nom de famille du joueur.
        first_name (str) : Prénom du joueur.
        birth_date (str) : Date de naissance (format YYYY-MM-DD).
        national_id (str) : Identifiant national unique (ex : AB12345).
        date_enrolled (str) : Date d'inscription (format YYYY-MM-DD).
    """

    def __init__(self, last_name: str, first_name: str, birthdate: str, national_id: str) -> None:
        self.last_name = last_name
        self.first_name = first_name
        self.birthdate = birthdate
        self.national_id = national_id
        self.date_enrolled = datetime.now().strftime("%Y-%m-%d")

    @property
    def age(self) -> int:
        """
        Calcule l'âge du joueur à partir de sa date de naissance.
        """
        birth = datetime.strptime(self.birthdate, "%Y-%m-%d")
        today = datetime.today()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

    def record_match(self, result: str) -> None:
        """
        Réagit à un résultat de match individuel (victoire, défaite, nul).
        Cette fonction peut être utilisée pour des notifications ou journalisation.

        Paramètre :
            result (str) : Résultat du match ("win", "loss", "draw").
        """
        pass

    def get_ranking_score(self, tournament) -> float:
        """
        Calcule le score total du joueur dans un tournoi donné.
        Paramètre :
            tournament (Tournament) : Le tournoi concerné.
        Retourne :
            float : Total de points accumulés.
        """
        pass

    def get_stats_summary(self, tournament) -> str:
        """
        Retourne un résumé des performances du joueur dans un tournoi.
        Paramètre :
            tournament (Tournament) : Le tournoi concerné.
        Retourne :
            str : Statistiques sous forme de chaîne.
        """
        pass

    def save_to_file(self, filepath: str) -> None:
        """
        Sauvegarde les informations du joueur dans un fichier JSON.
        Paramètre :
            filepath (str) : Chemin du fichier de destination.
        """
        try:
            # Tente de charger tous les joueurs existants depuis le fichier
            players = Player.load_all_players(filepath)
        except (FileNotFoundError, json.JSONDecodeError):
            # Si le fichier n'existe pas ou est vide, on démarre avec une liste vide
            players = []

            # Ajoute ce joueur à la liste
        players.append(self)

        # Réécrit le fichier avec tous les joueurs, y compris le nouveau
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump([p._to_dict() for p in players], file, indent=4, ensure_ascii=False)

    @staticmethod
    def load_all_players(filepath: str) -> List["Player"]:
        """
        Charge tous les joueurs enregistrés à partir d’un fichier JSON.
        """
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)  # Liste de dictionnaires
            return [Player._from_dict(p) for p in data]  # Transforme chaque dict en instance Player

    def _to_dict(self) -> dict:
        """
        Convertit l'objet Player en dictionnaire pour l’enregistrement JSON.
        """
        return {
            "last_name": self.last_name,
            "first_name": self.first_name,
            "birthdate": self.birthdate,
            "national_id": self.national_id,
            "date_enrolled": self.date_enrolled,
        }

    @staticmethod
    def _from_dict(data: dict) -> "Player":
        """
        Reconstruit un objet Player à partir d’un dictionnaire.
        """
        player = Player(
            last_name=data["last_name"],
            first_name=data["first_name"],
            birthdate=data["birthdate"],
            national_id=data["national_id"],
        )
        # Recharge la date d'inscription si elle existe dans le fichier
        player.date_enrolled = data.get("date_enrolled", datetime.now().strftime("%Y-%m-%d"))
        return player
