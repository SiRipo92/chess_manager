from datetime import datetime
from typing import List, Optional

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

    def __init__(self, last_name: str, first_name: str, birth_date: str, national_id: str) -> None:
        self.last_name = last_name
        self.first_name = first_name
        self.birth_date = birth_date
        self.national_id = national_id
        self.date_enrolled = datetime.now().strftime("%Y-%m-%d")

    @property
    def age(self) -> int:
        """
        Calcule l'âge du joueur à partir de sa date de naissance.
        """
        birth = datetime.strptime(self.birth_date, "%Y-%m-%d")
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
        pass

    @staticmethod
    def load_all_players(filepath: str) -> List["Player"]:
        """
        Charge tous les joueurs enregistrés à partir d’un fichier JSON.
        Paramètre :
            filepath (str) : Chemin du fichier contenant les données.
        Retourne :
            List[Player] : Liste des joueurs chargés.
        """
        pass
