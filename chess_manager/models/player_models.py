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
    Represents a chess player.

    Attributes:
        last_name (str): Player's last name.
        first_name (str): Player's first name.
        birthdate (str): Date of birth in YYYY-MM-DD format.
        national_id (str): Unique national identifier (e.g., AB12345).
        date_enrolled (str): Enrollment date in YYYY-MM-DD format.
        match_history (list[dict]): List of match records, each as {"match": str, "résultat": "victoire|défaite|nul"}.
        tournaments_won (int): Count of tournaments won (including ties for first).
    """

    # ===========================
    # Initialization & Properties
    # ===========================

    def __init__(self, last_name: str, first_name: str, birthdate: str, national_id: str, match_history=None,
                 tournaments_won=0) -> None:
        """
        Initialize a Player instance and validate core fields.
        Raises ValueError with French messages if any field is invalid.
        """
        # Validate using functions defined in VALIDATION_MAP (display text remains French)
        if not VALIDATION_MAP["Nom de famille"](last_name):
            raise ValueError("Nom de famille invalide.")
        if not VALIDATION_MAP["Prénom"](first_name):
            raise ValueError("Prénom invalide.")
        if not VALIDATION_MAP["Date de naissance"](birthdate):
            raise ValueError("Date de naissance invalide.")
        if not VALIDATION_MAP["Identifiant national"](national_id):
            raise ValueError("Identifiant national invalide.")

        # Normalize text fields (code comments in English, UI/errors remain French)
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
        Compute age in whole years from birthdate.
        """
        birth = datetime.strptime(self.birthdate, DATE_FORMAT)
        today = datetime.today()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

    # ===========================
    # Player Stat Management
    # ===========================

    def record_match_result(self, match_name: str, result_code: str) -> None:
        """
        Append a match result to the player's history.

        Args:
            match_name (str): Match label or identifier.
            result_code (str): One-letter code 'V'|'D'|'N' (victoire|défaite|nul).
        """
        # Normalize the code then validate ('V', 'D', 'N')
        normalized_code = result_code.strip().upper()
        if not is_valid_match_result_code(normalized_code):
            raise ValueError("Code de résultat invalide. Utilisez 'V', 'D' ou 'N'.")

        # Translate the code to the canonical French label used in storage
        result_label = MATCH_RESULT_CODES[normalized_code]

        # Persist the record in French to keep JSON consistent
        self.match_history.append({
            "match": match_name,
            "résultat": result_label
        })

    def record_tournament_win(self):
        """
        Increase the count of tournaments won (includes ties for first place).
        """
        self.tournaments_won += 1

    def get_total_score(self) -> float:
        """
        Compute total points across all recorded matches using MATCH_RESULT_POINTS.
        """
        return sum(MATCH_RESULT_POINTS.get(m["résultat"], 0.0) for m in self.match_history)

    def get_ranking_score(self, tournament) -> float:
        """
        Placeholder for a future tournament-scoped ranking computation.

        Args:
            tournament: Tournament instance for context (not used yet).

        Returns:
            float: Intended to be the tournament-scope score.

        Raises:
            NotImplementedError: Will be implemented once tournaments/rounds are integrated end-to-end.
        """
        raise NotImplementedError(
            "Le score par tournoi sera implémenté une fois les classes Tournois/Rounds disponibles.")

    def get_stats_summary(self, _) -> Dict:
        """
        Return a summary of player performance as a dictionary (keys remain in French for display/JSON consistency).

        Returns:
            dict: Human-friendly stat labels (French) mapped to computed values.
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
        Update last name after validating with the same French validator used at creation.
        """
        if not VALIDATION_MAP["Nom de famille"](last_name):
            raise ValueError("Nom de famille invalide.")
        self.last_name = last_name.strip().title()

    def set_first_name(self, first_name: str) -> None:
        """
        Update first name after validating with the same French validator used at creation.
        """
        if not VALIDATION_MAP["Prénom"](first_name):
            raise ValueError("Prénom invalide.")
        self.first_name = first_name.strip().title()

    def set_birthdate(self, birthdate: str) -> None:
        """
        Update birthdate after validating with the same French validator used at creation.
        """
        if not VALIDATION_MAP["Date de naissance"](birthdate):
            raise ValueError("Date de naissance invalide.")
        self.birthdate = birthdate

    def set_national_id(self, national_id: str) -> None:
        """
        Update national ID after validating with the same French validator used at creation.
        """
        if not VALIDATION_MAP["Identifiant national"](national_id):
            raise ValueError("Identifiant national invalide.")
        self.national_id = national_id.strip().upper()

    # ===========================
    # Serialization
    # ===========================
    def to_dict(self) -> dict:
        """
        Serialize Player to a JSON-friendly dict. Keys remain in English for fields and in French for data values that
        are intentionally French (e.g., match_history 'résultat').
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
        Reconstruct a Player from a dict produced by `to_dict`.
        """
        player = Player(
            last_name=data["last_name"],
            first_name=data["first_name"],
            birthdate=data["birthdate"],
            national_id=data["national_id"],
            match_history=data.get("match_history", []),
            tournaments_won=data.get("tournaments_won", 0)
        )
        # Keep enrollment date if provided; otherwise initialize now
        player.date_enrolled = data.get("date_enrolled", datetime.now().strftime(DATE_FORMAT))
        return player

    # ===========================
    # Static Loading & Saving
    # ===========================

    def save_to_file(self, filepath: str) -> None:
        """
        Append this player to the JSON file (creating or extending the list).
        """
        try:
            players = Player.load_all_players(filepath)
        except (FileNotFoundError, json.JSONDecodeError):
            # Start from an empty list if file does not exist or is empty/invalid
            players = []
        players.append(self)
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump([p.to_dict() for p in players], file, indent=4, ensure_ascii=False)  # type: ignore

    @staticmethod
    def load_all_players(filepath: str) -> List["Player"]:
        """
        Load all players from a JSON file and return `Player` instances.
        """
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)  # List of dicts
            return [Player.from_dict(p) for p in data]
