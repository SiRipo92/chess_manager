from __future__ import annotations
import random
from datetime import datetime, date
from typing import List, Dict, Optional, Set, FrozenSet
from chess_manager.models.player_models import Player
from chess_manager.models.round_models import Round
from chess_manager.models.match_models import Match

class Tournament:
    """
    Représente un tournoi d'échecs.

    Attributs principaux :
        location (str)
        start_date (str, YYYY-MM-DD)  -> fixé au lancement
        end_date (str, YYYY-MM-DD)    -> fixé à la fin
        started_at (str, ISO)         -> timestamp précis du lancement
        finished_at (str, ISO)        -> timestamp précis de fin
        description (str)
        number_rounds (int)
        current_round_number (int)
        players (List[Player])
        rounds (List[Round])
        scores (Dict[national_id,float])
        past_pairs (Set[FrozenSet[str]])
    """
    def __init__(
            self,
            location: str,
            start_date: Optional[str] = "",
            end_date: Optional[str] = "",
            description: str = "",
            number_rounds: int = 4,
    ) -> None:
        self.location = location
        self.start_date = start_date or ""   # ex: "2025-08-10" (au lancement)
        self.end_date = end_date or ""       # défini à la fin
        self.started_at: str = ""            # ex: "2025-08-10T14:32:05.123456"
        self.finished_at: str = ""           # idem à la fin
        self.description = description
        self.number_rounds = number_rounds

        self.current_round_number = 0
        self.players: List[Player] = []
        self.rounds: List[Round] = []

        self.scores: Dict[str, float] = {}
        self.past_pairs: Set[FrozenSet[str]] = set()

        # NEW: keep the repository's display name (e.g., "tournament_1_nanterre_2025-08-15")
        self.repo_name: str = ""

    @property
    def status(self) -> str:
        """
        'En cours' si lancé et pas fini ; 'Terminé' si finished_at présent ;
        sinon 'En attente' avant lancement.
        """
        if self.finished_at:
            return "Terminé"
        if self.started_at:
            return "En cours"
        return "En attente"


    @property
    def name(self) -> str:
        """
        Génère automatiquement le nom du tournoi à partir du lieu et de la date.
        Exemple : "Paris_2025-07-01"
        """
        return f"{self.location}_{self.start_date}"

    @property
    def registration_open(self) -> bool:
        return self.current_round_number == 0

    def has_player(self, national_id: str) -> bool:
        return any(p.national_id == national_id for p in self.players)

    def roster_size(self) -> int:
        return len(self.players)


    # --- lifecycle helpers -------------------------------------------------

    def mark_launched(self) -> None:
        """À appeler au lancement (dans start_first_round)."""
        if not self.start_date:
            self.start_date = date.today().isoformat()
        if not self.started_at:
            self.started_at = datetime.now().isoformat(timespec="seconds")

    def mark_finished(self) -> None:
        """À appeler quand le dernier tour est terminé."""
        if not self.end_date:
            self.end_date = date.today().isoformat()
        if not self.finished_at:
            self.finished_at = datetime.now().isoformat(timespec="seconds")

    # -------------------------
    # Inscription des joueurs
    # -------------------------


    def add_player(self, player: Player) -> None:
        """
        Inscrit un joueur à CE tournoi (pas au registre global).
        Règles :
        - pas de doublon,
        - inscription fermée si un tour a déjà commencé.
        """
        if not self.registration_open:
            raise ValueError("Inscription fermée : le tournoi a déjà commencé.")
        if self.has_player(player.national_id):
            raise ValueError("Joueur déjà inscrit à ce tournoi.")
        self.players.append(player)
        # Initialise le score du joueur pour CE tournoi
        self.scores[player.national_id] = 0.0

    # If you prefer to keep the tournament storing only IDs:
    def add_player_id(self, national_id: str, lookup: dict[str, Player]) -> None:
        if not self.registration_open:
            raise ValueError("Inscription fermée : le tournoi a déjà commencé.")
        if self.has_player(national_id):
            raise ValueError("Joueur déjà inscrit à ce tournoi.")
        self.players.append(lookup[national_id])


    # ----------------------
    # Génération des tours
    # ----------------------
    def _validate_roster_before_launch(self) -> None:
        """Assure au moins 8 joueurs et des identifiants uniques."""
        if self.roster_size() < 8:
            raise ValueError("Il faut au moins 8 joueurs pour démarrer un tournoi.")
        ids = [p.national_id for p in self.players]
        if len(set(ids)) != len(ids):
            raise ValueError("Des identifiants joueurs en double ont été détectés.")


    def start_first_round(self) -> Round:
        if self.current_round_number != 0:
            raise ValueError("Le tournoi a déjà démarré.")
        self._validate_roster_before_launch()

        self.mark_launched()
        self.current_round_number = 1
        round = Round(self.current_round_number)

        pool = list(self.players)
        random.shuffle(pool)

        i = 0
        while i + 1 < len(pool):
            p1, p2 = pool[i], pool[i + 1]
            match = Match(p1, p2)
            round.add_match(match)
            self._remember_pair(p1.national_id, p2.national_id)
            i += 2

        if len(pool) % 2 == 1:
            exempt_player = pool[-1]
            exempt_match = Match(exempt_player, None)
            exempt_match.set_result_by_code("E")
            round.add_match(exempt_match)
            self._apply_match_points(exempt_match)

        self.rounds.append(round)
        return round

    def start_next_round(self) -> Round:
        if self.current_round_number == 0:
            raise ValueError("Le tournoi n’a pas encore démarré. Lancez d’abord le 1er tour.")
        if self.current_round_number >= self.number_rounds:
            raise ValueError("Nombre de tours maximum atteint.")

        self.current_round_number += 1
        round = Round(self.current_round_number)

        sorted_ids = self._sorted_player_ids_by_score()

        if len(sorted_ids) % 2 == 1:
            exempt_id = sorted_ids.pop()
            exempt_player = self._player_by_id(exempt_id)
            exempt_match = Match(exempt_player, None)
            exempt_match.set_result_by_code("E")
            round.add_match(exempt_match)
            self._apply_match_points(exempt_match)

        used: Set[str] = set()
        i = 0
        while i < len(sorted_ids):
            p1_id = sorted_ids[i]
            if p1_id in used:
                i += 1
                continue

            p2_id = self._find_partner(p1_id, sorted_ids, used)
            if p2_id is None:
                p2_id = next((pid for pid in sorted_ids[i + 1:] if pid not in used and pid != p1_id), None)

            if p2_id is None:
                i += 1
                continue

            p1 = self._player_by_id(p1_id)
            p2 = self._player_by_id(p2_id)
            match = Match(p1, p2)
            round.add_match(match)
            self._remember_pair(p1_id, p2_id)
            used.add(p1_id)
            used.add(p2_id)
            i += 1

        self.rounds.append(round)
        return round

    def update_scores_from_round(self, tournament_round: Round) -> None:
        for match in tournament_round.matches:
            self._apply_match_points(match)

    # --------------
    # Sérialisation
    # --------------
    def to_dict(self) -> Dict:
        return {
            "name": self.repo_name or self.name,  # << ensure repo can upsert
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "description": self.description,
            "number_rounds": self.number_rounds,
            "current_round_number": self.current_round_number,
            "players": [p.to_dict() for p in self.players],
            "rounds": [r.to_dict() for r in self.rounds],
            "scores": dict(self.scores),
            "past_pairs": [list(pair) for pair in self.past_pairs],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Tournament":
        start_date = data.get("start_date") or (data.get("created_at") or "")[:10]
        tournament = cls(
            location=data["location"],
            start_date=start_date or "",
            end_date=data.get("end_date", ""),
            description=data.get("description", ""),
            number_rounds=int(data.get("number_rounds", 4)),
        )
        tournament.repo_name = data.get("name", "")  # << preserve repo name
        tournament.started_at = data.get("started_at", "")
        tournament.finished_at = data.get("finished_at", "")
        tournament.current_round_number = int(data.get("current_round_number", 0))

        # players
        tournament.players = []
        for entry in data.get("players", []):
            if isinstance(entry, dict):
                tournament.players.append(Player.from_dict(entry))
            elif isinstance(entry, Player):
                tournament.players.append(entry)
            # elif isinstance(entry, str):  # legacy: skip or resolve elsewhere
            #     ...

        # rounds (needs lookup)
        player_lookup = {p.national_id: p for p in tournament.players}
        tournament.rounds = [Round.from_dict(rd, player_lookup) for rd in data.get("rounds", [])]

        # scores
        if isinstance(data.get("scores"), dict):
            tournament.scores = {k: float(v) for k, v in data["scores"].items()}
        else:
            tournament.scores = {p.national_id: 0.0 for p in tournament.players}

        # past pairs
        tournament.past_pairs = set()
        for pair in data.get("past_pairs", []):
            ids = [str(x) for x in pair]
            if len(ids) == 2:
                tournament.past_pairs.add(frozenset(ids))

        return tournament

    # =======================
    # Helpers (internal use)
    # =======================

    def _player_by_id(self, national_id: str) -> Player:
        for p in self.players:
            if p.national_id == national_id:
                return p
        raise KeyError(f"Joueur introuvable : {national_id}")

    def _remember_pair(self, id1: str, id2: str) -> None:
        """Enregistre une paire jouée dans l’historique des confrontations."""
        self.past_pairs.add(frozenset((id1, id2)))

    def _have_played_before(self, id1: str, id2: str) -> bool:
        return frozenset((id1, id2)) in self.past_pairs

    def _sorted_player_ids_by_score(self) -> List[str]:
        """
        Retourne les IDs triés par score décroissant.
        Mélange légèrement les égalités pour éviter des appariements répétitifs.
        """
        # groupe par score
        buckets: Dict[float, List[str]] = {}
        for p in self.players:
            buckets.setdefault(self.scores.get(p.national_id, 0.0), []).append(p.national_id)

        # tri des scores décroissants
        sorted_scores = sorted(buckets.keys(), reverse=True)

        result: List[str] = []
        for sc in sorted_scores:
            ids = buckets[sc]
            random.shuffle(ids)   # mélange dans le groupe à score égal (Swiss-like)
            result.extend(ids)
        return result

    def _find_partner(self, p1_id: str, sorted_ids: List[str], used: Set[str]) -> Optional[str]:
        """
        Cherche un partenaire compatible (pas déjà joué) en balayant la liste
        depuis la position de p1_id + 1.
        """
        # trouve l’indice de p1 dans sorted_ids
        try:
            start_idx = sorted_ids.index(p1_id) + 1
        except ValueError:
            return None

        for p2_id in sorted_ids[start_idx:]:
            if p2_id in used:
                continue
            if not self._have_played_before(p1_id, p2_id):
                return p2_id
        return None  # aucun partenaire “propre” trouvé

    def _apply_match_points(self, match: Match) -> None:
        """
        Ajoute les points d’un match aux scores du tournoi.
        Si 'exempt', le match contient déjà le score du joueur 1.
        """
        id1 = match.player1.national_id
        self.scores[id1] = self.scores.get(id1, 0.0) + float(match.score1 or 0.0)

        if match.player2:
            id2 = match.player2.national_id
            self.scores[id2] = self.scores.get(id2, 0.0) + float(match.score2 or 0.0)