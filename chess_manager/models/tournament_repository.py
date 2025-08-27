import json
import os
from typing import List, Optional

try:
    from chess_manager.models.tournament_models import Tournament
except ImportError:  # pragma: no cover
    Tournament = None  # type: ignore


class TournamentRepository:
    """
    Gère la persistance des tournois : chargement, sauvegarde et recherche.
    Stocke tous les tournois dans un seul fichier JSON sous forme de liste de dicts.
    """

    def __init__(self, dir_path: str = "data/tournaments") -> None:
        self.dir_path = dir_path
        os.makedirs(self.dir_path, exist_ok=True)
        self._file_path = os.path.join(self.dir_path, "tournaments.json")
        if not os.path.exists(self._file_path):
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
        self.tournaments = self._load_raw()  # in-memory list of dicts

    def _load_raw(self) -> List[dict]:
        """Load the raw data from the tournament repository"""
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    def _persist(self) -> None:
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(self.tournaments, f, indent=2, ensure_ascii=False)

    def load_all_tournaments(self) -> List[dict]:
        """
        Retourne tous les tournois, en tentant de les convertir en objets Tournament si possible.
        """
        return list(self.tournaments)

    def save_tournament(self, tournament: dict) -> None:
        """Save the tournament in the json"""
        # Require a stable "name" key to upsert
        name = (tournament.get("name") or "").strip().lower()
        if not name:
            # if no name, just append
            self.tournaments.append(tournament)
            self._persist()
            return

        for idx, existing in enumerate(self.tournaments):
            if (existing.get("name") or "").strip().lower() == name:
                self.tournaments[idx] = tournament
                self._persist()
                return
        # not found -> append
        self.tournaments.append(tournament)
        self._persist()

    def add_tournament(self, tournament: dict) -> None:
        """Add new tournament into tournament dictionary"""
        self.save_tournament(tournament)

    def get_tournament_by_name(self, name: str) -> Optional[dict]:
        """Retrieve a tournament by its name"""
        key = name.strip().lower()
        for t in self.tournaments:
            if (t.get("name") or "").strip().lower() == key:
                return dict(t)  # shallow copy
        return None
