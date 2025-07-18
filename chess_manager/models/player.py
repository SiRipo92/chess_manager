from datetime import datetime
from typing import List, Dict
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
        match_history (list of dictionaries) (format: 'result': 'victoire')
        tournaments_won(): integer (ex. 1)
    """

    def __init__(self, last_name: str, first_name: str, birthdate: str, national_id: str, match_history=None, tournaments_won=0) -> None:
        self.last_name = last_name
        self.first_name = first_name
        self.birthdate = birthdate
        self.national_id = national_id
        self.date_enrolled = datetime.now().strftime("%Y-%m-%d")
        self.match_history = match_history if match_history is not None else []
        self.tournaments_won = tournaments_won

    @property
    def age(self) -> int:
        """
        Calcule l'âge du joueur à partir de sa date de naissance.
        """
        birth = datetime.strptime(self.birthdate, "%Y-%m-%d")
        today = datetime.today()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

    def record_match(self, match_name: str, result: str) -> None:
        """
        Enregistre un résultat de match dans l'historique du joueur.

        Paramètre :
            result (str) : Abréviation en entrée ("V", "D", "N").

        Résultats enregistrés :
            - "victoire"
            - "défaite"
            - "nul"
        """
        result = result.strip().upper()
        mapping = {
            "V": "victoire",
            "D": "défaite",
            "N": "nul"
        }
        if result not in mapping:
            raise ValueError("Résultat invalide. Utilisez 'V' pour victoire, 'D' pour défaite ou 'N' pour nul.")

        self.match_history.append({
            "match": match_name,
            "résultat": mapping[result]
        })

    def get_total_score(self) -> float:
        """
        Calcule le score total du joueur (tous tournois confondus).
        """
        wins = sum(1 for m in self.match_history if m["résultat"] == "victoire")
        draws = sum(1 for m in self.match_history if m["résultat"] == "nul")
        return wins * 1.0 + draws * 0.5


    def get_ranking_score(self, tournament) -> float:
        """
        Calcule un score global basé sur l'historique des matchs.
        ******   À IMPLEMENTER PLUS TARD QUAND LES CLASSES DE TOURNOIS ET TOURS SONT CONNECTÉS
        Paramètre :
            tournament (Tournament) : Le tournoi concerné.
        Retourne :
            float : Total de points accumulés.
        """
        raise NotImplementedError(
            "Le score par tournoi sera implémenté une fois les classes Tournois/Rounds disponibles.")

    def get_stats_summary(self, tournament=None) -> Dict:
        """
        Retourne un résumé des performances du joueur sous forme de dictionnaire.

        Paramètre :
            tournament (Tournament | None) : Optionnel — utilisé plus tard pour filtrer les stats par tournoi.
        Retour :
            dict : Statistiques du joueur.
        """
        total = len(self.match_history)
        wins = sum(1 for m in self.match_history if m["résultat"] == "victoire")
        losses = sum(1 for m in self.match_history if m["résultat"] == "défaite")
        draws = sum(1 for m in self.match_history if m["résultat"] == "nul")
        points = wins * 1 + draws * 0.5

        return {
            "Nom complet": f"{self.first_name} {self.last_name}",
            "Âge": self.age,
            "Date d'inscription": self.date_enrolled,
            "Total de matchs joués": total,
            "✅ Victoires": wins,
            "❌ Défaites": losses,
            "🔁 Nuls": draws,
            "Points cumulés": points,
            "Tournois gagnés": self.tournaments_won,
        }

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
            json.dump([p.to_dict() for p in players], file, indent=4, ensure_ascii=False)

    @staticmethod
    def load_all_players(filepath: str) -> List["Player"]:
        """
        Charge tous les joueurs enregistrés à partir d’un fichier JSON.
        """
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)  # Liste de dictionnaires
            return [Player.from_dict(p) for p in data]  # Transforme chaque dict en instance Player

    def to_dict(self) -> dict:
        """
        Convertit l'objet Player en dictionnaire pour l’enregistrement JSON.
        """
        return {
            "last_name": self.last_name,
            "first_name": self.first_name,
            "birthdate": self.birthdate,
            "national_id": self.national_id,
            "date_enrolled": self.date_enrolled,
            "match_history": self.match_history,
            "tournaments_won": self.tournaments_won,
        }

    @staticmethod
    def from_dict(data: dict) -> "Player":
        """
        Reconstruit un objet Player à partir d’un dictionnaire.
        """
        player = Player(
            last_name=data["last_name"],
            first_name=data["first_name"],
            birthdate=data["birthdate"],
            national_id=data["national_id"],
            match_history = data.get("match_history", []),
            tournaments_won = data.get("tournaments_won", 0)
        )
        # Recharge la date d'inscription si elle existe dans le fichier
        player.date_enrolled = data.get("date_enrolled", datetime.now().strftime("%Y-%m-%d"))
        return player
