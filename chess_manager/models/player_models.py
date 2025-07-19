# ===========================
# Player Model Structure Map
# ===========================
#
# 1. Initialization & Properties
#    - __init__, @property methods
#
# 2. Player Stat Management
#    - record_match_result, record_tournament_win
#    - get_stats_summary
#
# 3. Player Attribute Mutators
#    - set_last_name, set_first_name, set_birthdate, set_national_id
#
# 4. Serialization
#    - to_dict, from_dict
#
# 5. Static Loading & Saving
#    - load_all_players, save_all_players

from datetime import datetime
from typing import List, Dict
import json
from chess_manager.constants.player_fields import VALIDATION_MAP
from chess_manager.utils.player_validators import DATE_FORMAT
from chess_manager.constants.match_results import (
    MATCH_RESULT_CODES,
    MATCH_RESULT_POINTS
)
from chess_manager.utils.match_validators import is_valid_match_result_code


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

    # ===========================
    # Initialization & Properties
    # ===========================

    def __init__(self, last_name: str, first_name: str, birthdate: str, national_id: str, match_history=None,
                 tournaments_won=0) -> None:
        """
        Initialise une instance de joueur avec validation des champs principaux.
        """
        # Validation de chaque champ via les fonctions définies dans VALIDATION_MAP
        if not VALIDATION_MAP["Nom de famille"](last_name):
            raise ValueError("Nom de famille invalide.")
        if not VALIDATION_MAP["Prénom"](first_name):
            raise ValueError("Prénom invalide.")
        if not VALIDATION_MAP["Date de naissance"](birthdate):
            raise ValueError("Date de naissance invalide.")
        if not VALIDATION_MAP["Identifiant national"](national_id):
            raise ValueError("Identifiant national invalide.")

        # Normalisation des champs texte
        self.last_name = last_name.strip().title()
        self.first_name = first_name.strip().title()
        self.birthdate = birthdate
        self.national_id = national_id.strip().upper()
        self.date_enrolled = datetime.now().strftime(DATE_FORMAT)
        self.match_history = match_history if match_history is not None else []
        self.tournaments_won = tournaments_won

    @property
    def age(self) -> int:
        """
        Calcule l'âge du joueur à partir de sa date de naissance.
        """
        birth = datetime.strptime(self.birthdate, DATE_FORMAT)
        today = datetime.today()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

    # ===========================
    # Player Stat Management
    # ===========================

    def record_match_result(self, match_name: str, result_code: str) -> None:
        """
        Enregistre un résultat de match pour le joueur.

        Paramètres :
            match_name (str) : Nom ou identifiant du match.
            result_code (str) : Code de résultat ('V', 'D', 'N').
        """
        # Normalisation : on met en majuscules et supprime les espaces
        normalized_code = result_code.strip().upper()

        # Vérification si le code est valide ('V', 'D' ou 'N')
        if not is_valid_match_result_code(normalized_code):
            raise ValueError("Code de résultat invalide. Utilisez 'V', 'D' ou 'N'.")

        # Conversion en libellé standardisé ('victoire', 'défaite', 'nul')
        result_label = MATCH_RESULT_CODES[normalized_code]

        # Enregistrement du résultat dans l'historique du joueur
        self.match_history.append({
            "match": match_name,
            "résultat": result_label
        })

    def record_tournament_win(self):
        """
        Increases the count of tournaments won
        """
        self.tournaments_won += 1

    def get_total_score(self) -> float:
        """
        Calcule le score total du joueur (tous tournois confondus).
        """
        return sum(MATCH_RESULT_POINTS.get(m["résultat"], 0.0) for m in self.match_history)

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

    def get_stats_summary(self, _) -> Dict:
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
        points = self.get_total_score()

        return {
            "Nom complet": f"{self.first_name} {self.last_name}",
            "Âge": self.age,
            "Date d'inscription": self.date_enrolled,
            "Total de matchs joués": total,
            "Victoires": wins,
            "Défaites": losses,
            "Nuls": draws,
            "Points cumulés": points,
            "Tournois gagnés": self.tournaments_won,
        }

    # ===========================
    # Player Attribute Mutators
    # ===========================

    def set_last_name(self, last_name: str) -> None:
        """
        Méthode utilisé afin de modifier le nom de famille du joueur.
        """
        if not VALIDATION_MAP["Nom de famille"](last_name):
            raise ValueError("Nom de famille invalide.")
        self.last_name = last_name.strip().title()

    def set_first_name(self, first_name: str) -> None:
        """
        Méthode utilisé afin de modifier le prénom du joueur.
        """
        if not VALIDATION_MAP["Prénom"](first_name):
            raise ValueError("Prénom invalide.")
        self.first_name = first_name.strip().title()

    def set_birthdate(self, birthdate: str) -> None:
        """
        Méthode utilisé afin de modifier la date de naissance du joueur.
        """
        if not VALIDATION_MAP["Date de naissance"](birthdate):
            raise ValueError("Date de naissance invalide.")
        self.birthdate = birthdate

    def set_national_id(self, national_id: str) -> None:
        """
        Méthode utilisé afin de modifier l'ID national du joueur.
        """
        if not VALIDATION_MAP["Identifiant national"](national_id):
            raise ValueError("Identifiant national invalide.")
        self.national_id = national_id.strip().upper()

    # ===========================
    # Serialization
    # ===========================
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
            match_history=data.get("match_history", []),
            tournaments_won=data.get("tournaments_won", 0)
        )
        # Recharge la date d'inscription si elle existe dans le fichier
        player.date_enrolled = data.get("date_enrolled", datetime.now().strftime(DATE_FORMAT))
        return player

    # ===========================
    # Static Loading & Saving
    # ===========================

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
            json.dump([p.to_dict() for p in players], file, indent=4, ensure_ascii=False) # type: ignore

    @staticmethod
    def load_all_players(filepath: str) -> List["Player"]:
        """
        Charge tous les joueurs enregistrés à partir d’un fichier JSON.
        """
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)  # Liste de dictionnaires
            return [Player.from_dict(p) for p in data]  # Transforme chaque dict en instance Player


