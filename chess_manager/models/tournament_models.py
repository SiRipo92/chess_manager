from __future__ import annotations
import random
from datetime import datetime, date
from typing import List, Dict, Optional, Set, FrozenSet
from chess_manager.models.player_models import Player
from chess_manager.models.round_models import Round
from chess_manager.models.match_models import Match


class Tournament:
    """
    Chess tournament domain model.

    Attributes:
        location: Tournament location.
        start_date: 'YYYY-MM-DD'. Set when the tournament is launched.
        end_date: 'YYYY-MM-DD'. Set when the tournament is finished.
        started_at: ISO datetime timestamp set at launch (precise time).
        finished_at: ISO datetime timestamp set when finished.
        description: Single string describing the tournament (notes/summary).
        number_rounds: Planned number of rounds (default 4).
        current_round_number: 0 before start, increases as rounds are created.
        players: Roster for this tournament (Player instances).
        rounds: List of Round objects as they are created/closed.
        scores: Map national_id -> accumulated points for *this* tournament.
        past_pairs: Set of frozensets of two national_ids already paired.
        repo_name: Persistent display/name used by the repository layer.
    """
    def __init__(
            self,
            location: str,
            start_date: Optional[str] = "",
            end_date: Optional[str] = "",
            description: str = "",
            number_rounds: int = 4,
    ) -> None:
        """
        Initialize a new Tournament instance (not started yet).

        Args:
            location: Human-readable location.
            start_date: YYYY-MM-DD (optional). Typically filled at launch.
            end_date: YYYY-MM-DD (optional). Filled at finish time.
            description: Optional free text.
            number_rounds: Planned number of rounds (default 4).
        """
        self.location = location
        self.start_date = start_date or ""   # e.g. "2025-08-10" (at launch)
        self.end_date = end_date or ""       # set when finished
        self.started_at: str = ""            # ex: e.g. "2025-08-10T14:32:05.123456"
        self.finished_at: str = ""           # set when finished
        self.description = description.strip()
        self.number_rounds = number_rounds

        self.current_round_number = 0
        self.players: List[Player] = []
        self.rounds: List[Round] = []

        self.scores: Dict[str, float] = {}
        self.past_pairs: Set[FrozenSet[str]] = set()

        # Repository-facing persisted name (e.g., "tournament_1_nanterre_2025-08-15")
        self.repo_name: str = ""

        # Stores winner
        self.winner_id: str = ""

    # ----------------------
    # Basic derived props
    # ----------------------

    @property
    def status(self) -> str:
        """
        Human-friendly status label.

        Returns:
            "Terminé" if finished_at is set;
            "En cours" if started_at is set but finished_at is empty;
            "En attente" otherwise (not started yet).
        """
        if self.finished_at:
            return "Terminé"
        if self.started_at:
            return "En cours"
        return "En attente"

    @property
    def name(self) -> str:
        """
        Computed, human-friendly name (location + start_date).

        Returns:
            A string like "Paris_2025-07-01".
        """
        return f"{self.location}_{self.start_date}"

    @property
    def registration_open(self) -> bool:
        """
        Whether registration is open (no round started yet).

        Returns:
            True if current_round_number == 0, else False.
        """
        return self.current_round_number == 0

    # ----------------------
    # Description helpers
    # ----------------------
    def get_description(self) -> str:
        """
        Return the tournament description as a single string (also allowed to be empty).
        """
        return self.description or ""

    def set_description(self, text: str) -> None:
        """
        Overwrite the tournament description with the provided string (trimmed).
        """
        self.description = (text or "").strip()

    # ----------------------
    # Roster helpers
    # ----------------------

    def has_player(self, national_id: str) -> bool:
        """
        Check if a player (by ID) is already on the roster.

        Args:
            national_id: Player national ID.

        Returns:
            True if present, else False.
        """
        return any(p.national_id == national_id for p in self.players)

    def roster_size(self) -> int:
        """
        Number of players currently in the tournament roster.

        Returns:
            Roster size as an integer.
        """
        return len(self.players)

    # ----------------------
    # Lifecycle helpers
    # ----------------------

    def mark_launched(self) -> None:
        """
        Mark the tournament as launched.

        Side Effects:
            - Sets start_date to today's date if missing.
            - Sets started_at to now (seconds precision) if missing.
        """
        if not self.start_date:
            self.start_date = date.today().isoformat()
        if not self.started_at:
            self.started_at = datetime.now().isoformat(timespec="seconds")

    def mark_finished(self) -> None:
        """
        Mark the tournament as finished.

        Side Effects:
            - Sets end_date to today's date if missing.
            - Sets finished_at to now (seconds precision) if missing.
        """
        if not self.end_date:
            self.end_date = date.today().isoformat()
        if not self.finished_at:
            self.finished_at = datetime.now().isoformat(timespec="seconds")

    def compute_winner_id(self) -> Optional[str]:
        leaders = self.tied_leaders()
        return leaders[0] if len(leaders) == 1 else None

    # -------------------------
    # Inscription des joueurs
    # -------------------------

    def add_player(self, player: Player) -> None:
        """
        Add a Player object to this tournament.

        Rules:
            - Fails if registration is closed (a round has already started).
            - Fails if the player is already on the roster.
            - Initializes this player's score in `scores` to 0.0.

        Args:
            player: Player instance to add.

        Raises:
            ValueError: If registration is closed or the player is duplicated.
        """
        if not self.registration_open:
            raise ValueError("Inscription fermée : le tournoi a déjà commencé.")
        if self.has_player(player.national_id):
            raise ValueError("Joueur déjà inscrit à ce tournoi.")
        self.players.append(player)
        # Initialise le score du joueur pour CE tournoi
        self.scores[player.national_id] = 0.0

    def add_player_id(self, national_id: str, lookup: dict[str, Player]) -> None:
        """
        Add a player by ID using a provided lookup.

        Rules:
            - Same as `add_player` regarding registration and duplicates.

        Args:
            national_id: Player national ID.
            lookup: Mapping of national_id -> Player.

        Raises:
            ValueError: If registration is closed or the player is duplicated.
            KeyError: If `national_id` is not found in `lookup`.
        """
        if not self.registration_open:
            raise ValueError("Inscription fermée : le tournoi a déjà commencé.")
        if self.has_player(national_id):
            raise ValueError("Joueur déjà inscrit à ce tournoi.")
        self.players.append(lookup[national_id])

    # ----------------------
    # Génération des tours
    # ----------------------

    def validate_roster_before_launch(self) -> None:
        """
        Validate roster constraints before starting round 1.

        Ensures:
            - At least 8 players.
            - No duplicate national IDs.

        Raises:
            ValueError: If constraints are not satisfied.
        """
        if self.roster_size() < 8:
            raise ValueError("Il faut au moins 8 joueurs pour démarrer un tournoi.")
        ids = [p.national_id for p in self.players]
        if len(set(ids)) != len(ids):
            raise ValueError("Des identifiants joueurs en double ont été détectés.")

    def start_first_round(self) -> Round:
        """
        Launch the tournament and create the first round with random pairings.

        Behavior:
            - Validates roster (min 8, no duplicates).
            - Sets launch timestamps if needed.
            - Creates Round #1.
            - Shuffles players and pairs them.
            - If odd roster, the last player gets an automatic "exempt" match (1.0).
            - Applies points for the exempt match immediately.
            - Appends the round to `rounds`, sets `current_round_number` to 1.

        Returns:
            The created Round object.

        Raises:
            ValueError: If the tournament has already started or roster invalid.
        """
        if self.current_round_number != 0:
            raise ValueError("Le tournoi a déjà démarré.")
        self.validate_roster_before_launch()

        self.mark_launched()
        self.current_round_number = 1
        rnd = Round(self.current_round_number)

        pool = list(self.players)
        random.shuffle(pool)

        i = 0
        while i + 1 < len(pool):
            p1, p2 = pool[i], pool[i + 1]
            match = Match(p1, p2)
            rnd.add_match(match)
            self.remember_pair(p1.national_id, p2.national_id)
            i += 2

        if len(pool) % 2 == 1:
            self.add_exempt_bye(rnd, pool[-1])

        self.rounds.append(rnd)
        return rnd

    def start_next_round(self) -> Round:
        """
        Create the next round using Swiss-like pairing based on current scores.

        Behavior:
            - Requires the tournament to have started and not exceed `number_rounds`.
            - Sorts players by score descending; shuffles inside same-score buckets.
            - If odd count, last ID becomes exempt (earns 1.0 automatically).
            - Avoids repeating past pairs when possible via `_find_partner`.
            - Applies points for any exempt match immediately.
            - Appends the round to `rounds`, increments `current_round_number`.

        Returns:
            The created Round object.

        Raises:
            ValueError: If tournament not started or maximum rounds reached.
            KeyError: If a player ID cannot be resolved (should not happen with valid roster).
        """
        if self.current_round_number == 0:
            raise ValueError("Le tournoi n’a pas encore démarré. Lancez d’abord le 1er tour.")
        if self.current_round_number >= self.number_rounds:
            raise ValueError("Nombre de tours maximum atteint.")

        self.current_round_number += 1
        rnd = Round(self.current_round_number)

        sorted_ids = self.sorted_player_ids_by_score()

        if len(sorted_ids) % 2 == 1:
            exempt_id = sorted_ids.pop()
            self.add_exempt_bye_by_id(rnd, exempt_id)

        used: Set[str] = set()
        i = 0
        while i < len(sorted_ids):
            p1_id = sorted_ids[i]
            if p1_id in used:
                i += 1
                continue

            p2_id = self.find_partner(p1_id, sorted_ids, used)
            if p2_id is None:
                p2_id = next((pid for pid in sorted_ids[i + 1:] if pid not in used and pid != p1_id), None)

            if p2_id is None:
                i += 1
                continue

            p1 = self.get_player_by_id(p1_id)
            p2 = self.get_player_by_id(p2_id)
            match = Match(p1, p2)
            rnd.add_match(match)
            self.remember_pair(p1_id, p2_id)
            used.add(p1_id)
            used.add(p2_id)
            i += 1

        self.rounds.append(rnd)
        return rnd

    # --- Leaders / tie detection / tie breaking round (NEW) ---
    def tied_leaders(self) -> list[str]:
        """Return national_ids of players with the maximal score."""
        if not self.players:
            return []
        top_score = max(self.scores.get(p.national_id, 0.0) for p in self.players)
        return [p.national_id for p in self.players if self.scores.get(p.national_id, 0.0) == top_score]

    def have_first_place_tie(self) -> bool:
        """Returns a boolean flag indicating if a tie breaking rounds needs to take place."""
        return len(self.tied_leaders()) > 1

    def start_tiebreak_round(self, leader_ids: list[str])-> Round:
        """
        Create a new Round pairing only the given candidates (single-elimination style).
        - Shuffle candidates.
        - If odd, last gets an EXEMPT (1.0 point).
        - No rematch-avoidance: playoffs are allowed to rematch.
        """
        # Normalisation and avoids duplicated ids in list
        if not leader_ids:
            raise ValueError("Aucun départage nécessaire : pas d’égalité en tête.")
        ids_norm = []
        seen = set()
        for pid in leader_ids:
            pid = str(pid).strip().upper()
            if pid and pid not in seen:
                ids_norm.append(pid)
                seen.add(pid)

        if len(ids_norm) < 2:
            raise ValueError("Départage inutile : un seul joueur est en tête.")

        # Check that all IDs correspond to the current roster list in tournament
        for pid in ids_norm:
            try:
                self.get_player_by_id(pid)
            except KeyError:
                raise KeyError(f"Joueur inconnu dans ce tournoi : {pid}")

        # Create tiebreak round
        self.current_round_number += 1
        rnd = Round(self.current_round_number)

        # Random shuffle
        random.shuffle(ids_norm)

        # Bye/Exempt player handling in tiebreak round
        if len(ids_norm) % 2 == 1:
            bye_id = ids_norm.pop()
            self.add_exempt_bye_by_id(rnd, bye_id)

        # Matching 2 by 2 (authorizes rematches)
        for i in range(0, len(ids_norm), 2):
            p1 = self.get_player_by_id(ids_norm[i])
            p2 = self.get_player_by_id(ids_norm[i + 1])
            rnd.add_match(Match(p1, p2))

        self.rounds.append(rnd)
        return rnd

    def update_scores_from_round(self, tournament_round: Round) -> None:
        """
        Accumulate scores from the given round into the tournament `scores`.

        Args:
            tournament_round: Round whose matches have (final) scores.

        Side Effects:
            Mutates `self.scores` in place by adding match points.
        """
        for match in tournament_round.matches:
            self.apply_match_points(match)

    # --------------
    # Sérialisation
    # --------------

    def to_dict(self) -> Dict:
        """
        Serialize the tournament to a JSON-safe dictionary.

        Returns:
            Dict with primitive types only (nested players/rounds also serialized).
        """
        return {
            "name": self.repo_name or self.name,
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
            "winner_id": self.winner_id,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Tournament":
        """
        Reconstruct a Tournament object from a dictionary.

        Args:
            data: Dictionary produced by `to_dict()` (or the repository file).

        Returns:
            A Tournament instance populated with players, rounds, scores, pairs.

        Notes:
            - Uses 'created_at'[:10] as a fallback for 'start_date' when missing.
            - Players are rebuilt first to allow Round reconstruction with lookups.
        """
        start_date = data.get("start_date") or (data.get("created_at") or "")[:10]
        tournament = cls(
            location=data["location"],
            start_date=start_date or "",
            end_date=data.get("end_date", ""),
            description=str(data.get("description", "") or ""),
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

        # rounds
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

        # tournament winner
        tournament.winner_id = data.get("winner_id", "")

        return tournament

    # =======================
    # Helpers (internal use)
    # =======================

    def get_player_by_id(self, national_id: str) -> Player:
        """
        Resolve a Player instance by national ID from the current roster.

        Args:
            national_id: Player national ID.

        Returns:
            The Player instance.

        Raises:
            KeyError: If the ID is not found in the current roster.
        """
        for p in self.players:
            if p.national_id == national_id:
                return p
        raise KeyError(f"Joueur introuvable : {national_id}")

    def remember_pair(self, id1: str, id2: str) -> None:
        """
        Record that two players have already been paired in this tournament.

        Args:
            id1: National ID of player 1.
            id2: National ID of player 2.

        Side Effects:
            Adds a frozenset({id1, id2}) to `past_pairs`.
        """
        self.past_pairs.add(frozenset((id1, id2)))

    def have_played_before(self, id1: str, id2: str) -> bool:
        """
        Check if two players have previously been paired.

        Args:
            id1: National ID of player 1.
            id2: National ID of player 2.

        Returns:
            True if the pair exists in `past_pairs`, else False.
        """
        return frozenset((id1, id2)) in self.past_pairs

    def sorted_player_ids_by_score(self) -> List[str]:
        """
        Return player IDs sorted by current score (desc), shuffling within ties.

        Returns:
            List of national IDs ordered for Swiss-like pairing.
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
            random.shuffle(ids)   # randomness only among equal-score players
            result.extend(ids)
        return result

    def find_partner(self, p1_id: str, sorted_ids: List[str], used: Set[str]) -> Optional[str]:
        """
        Find a compatible partner for p1_id scanning forward in sorted_ids.

        Strategy:
            - Skip IDs already used in this round.
            - Prefer someone who hasn't played with p1_id before.
            - Returns the first compatible partner found.

        Args:
            p1_id: National ID of the first player.
            sorted_ids: Ordered list produced by `_sorted_player_ids_by_score`.
            used: Set of IDs already assigned in the current round.

        Returns:
            The partner national ID, or None if none found.
        """
        try:
            start_idx = sorted_ids.index(p1_id) + 1
        except ValueError:
            return None

        for p2_id in sorted_ids[start_idx:]:
            if p2_id in used:
                continue
            if not self.have_played_before(p1_id, p2_id):
                return p2_id
        return None  # aucun partenaire “propre” trouvé

    def apply_match_points(self, match: Match) -> None:
        """
        Add match points into the tournament `scores`.

        Notes:
            - For an exempt match (player2 is None), score1 is already set (1.0).

        Args:
            match: Match instance with score1/score2 finalized.

        Side Effects:
            Mutates `self.scores` to add score1 (and score2 if applicable).
        """
        id1 = match.player1.national_id
        self.scores[id1] = self.scores.get(id1, 0.0) + float(match.score1 or 0.0)

        if match.player2:
            id2 = match.player2.national_id
            self.scores[id2] = self.scores.get(id2, 0.0) + float(match.score2 or 0.0)

    def add_exempt_bye(self, rnd: Round, player: Player) -> None:
        """Create an EXEMPT match (bye) for `player`, credit 1.0, attach to `rnd`."""
        m = Match(player, None)
        m.set_result_by_code("E")  # EXEMPT -> 1.0
        rnd.add_match(m)
        self.apply_match_points(m)

    def add_exempt_bye_by_id(self, rnd: Round, player_id: str) -> None:
        """Convenience: same as above but starting from a national_id."""
        self.add_exempt_bye(rnd, self.get_player_by_id(player_id))
