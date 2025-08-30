import json
import os
import sys
from typing import List, Optional, Tuple
from rich.console import Console
from chess_manager.models.player_models import Player
from chess_manager.models.tournament_repository import TournamentRepository
from chess_manager.utils.tournament_utils import build_player_tournament_index
from chess_manager.constants.player_fields import VALIDATION_MAP, FIELD_LABELS
from chess_manager.views import player_views

console = Console()


class PlayerController:
    """
    Handles basic player operations: creation, reading, searching, editing, and persistence.
    """

    # -----------------------
    # Init & file setup
    # -----------------------
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the JSON storage file exists; create an empty list file if missing."""
        if not os.path.exists(self.file_path):
            try:
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
            except IOError as e:
                raise IOError(f"Impossible de créer {self.file_path} : {e}") from e

    # -----------------------
    # Load & Save
    # -----------------------
    def load_players(self) -> List[Player]:
        """Load players from JSON and return them sorted by name."""
        if not os.path.exists(self.file_path):
            return []
        try:
            players = Player.load_all_players(self.file_path)
            # return players list alphabetically as detailed in requirements
            return self.sort_players_by_name(players)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Impossible de lire {self.file_path} : {e}")
        return []

    def _save_player(self, updated_player: Player, original_id: Optional[str] = None) -> None:
        """
        Persist a player. If national_id was changed, use original_id to replace
        the correct record; otherwise, match by the player's current national_id.
        """
        players = self.load_players()
        key = original_id or updated_player.national_id
        replaced = False
        for idx, p in enumerate(players):
            if p.national_id == key:
                players[idx] = updated_player
                replaced = True
                break
        if not replaced:
            players.append(updated_player)
        self.save_players(players)

    def save_players(self, players: List[Player]) -> None:
        """Serialize and save new players to player file"""
        self._ensure_file_exists()
        try:
            players = self.sort_players_by_name(players)  # keep file alphabetized
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in players], f, indent=2, ensure_ascii=False)
        except IOError as e:
            console.print(f"❌ Erreur de sauvegarde : {e}")

    # ===========================
    # Queries & helpers
    # ===========================

    @staticmethod
    def sort_players_by_name(players: List[Player], reverse: bool = False) -> List[Player]:
        """
        Trie les joueurs par NOM puis PRÉNOM, insensible à la casse.
        """
        return sorted(players, key=lambda p: (p.last_name.lower(), p.first_name.lower()), reverse=reverse)

    @staticmethod
    def _normalize_id(national_id: str) -> str:
        """Return a normalized national ID (trim + uppercase)."""
        return (national_id or "").strip().upper()

    def _is_national_id_taken(self, national_id: str, *, exclude_id: Optional[str] = None) -> bool:
        """
        Return True if `national_id` already exists in storage.
        If `exclude_id` is provided, ignore that one (useful when editing the same player).
        """
        new_id = self._normalize_id(national_id)
        excluded = self._normalize_id(exclude_id) if exclude_id else None
        for p in self.load_players():
            if p.national_id == new_id and (excluded is None or p.national_id != excluded):
                return True
        return False

    def get_player_by_id(self, national_id: str) -> Optional[Player]:
        """ Filter player by id """
        normalized_id = national_id.strip().upper()
        players = self.load_players()
        for p in players:
            if p.national_id == normalized_id:
                return p
        return None

    def _search_players(self, query: str) -> List[Player]:
        """
        Search players by national ID or partial name (case-insensitive).

        Matching rules:
          - If query matches national_id (case-insensitive), it's a hit.
          - Otherwise, if query is contained in "LASTNAME FIRSTNAME" or
            "FIRSTNAME LASTNAME" or either part alone.
        """
        q = query.strip()
        if not q:
            return []

        players = self.load_players()
        q_upper = q.upper()
        q_lower = q.lower()

        matches: List[Player] = []
        for p in players:
            if p.national_id.upper() == q_upper or q_upper in p.national_id.upper():
                matches.append(p)
                continue

            full1 = f"{p.last_name} {p.first_name}".lower()
            full2 = f"{p.first_name} {p.last_name}".lower()
            if (q_lower in full1) or (q_lower in full2) or (q_lower in p.last_name.lower()) or (
                    q_lower in p.first_name.lower()):
                matches.append(p)

        return matches

    # -------------------------------------------------
    # Create
    # -------------------------------------------------

    def add_new_player(
            self, last_name: str, first_name: str, birthdate: str, national_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate inputs, enforce unique national_id, create player, persist to disk.
        Returns (success, error_message_if_any).
        """
        field_inputs = {
            "Nom de famille": last_name,
            "Prénom": first_name,
            "Date de naissance": birthdate,
            "Identifiant national": national_id,
        }

        for label, value in field_inputs.items():
            validator = VALIDATION_MAP.get(label)
            if not value:
                return False, f"Le champ '{label}' est obligatoire."
            if validator and not validator(value):
                return False, f"Le champ '{label}' est invalide."

        try:
            normalized_id = self._normalize_id(national_id)
            if self._is_national_id_taken(normalized_id):
                return False, "Cet identifiant est déjà utilisé."

            new_player = Player(last_name, first_name, birthdate, normalized_id)
            players = self.load_players()
            players.append(new_player)
            self.save_players(players)
            return True, None
        except (IOError, ValueError) as e:
            return False, f"Erreur système lors de l'ajout du joueur : {e}"

    def handle_add_new_player(self) -> None:
        """Interactive wrapper for creating a player with review/confirm UI."""
        result = player_views.prompt_new_player_inputs_with_review()
        if result is None:
            player_views.display_error_message("Ajout annulé.")
            return

        last_name, first_name, birthdate, national_id = result
        success, message = self.add_new_player(last_name, first_name, birthdate, national_id)
        if success:
            player_views.confirm_player_added()
        else:
            player_views.display_error_message(message or "Erreur inconnue lors de l'ajout.")

    # ---------- Edit flow ----------
    def edit_player_flow(self) -> None:
        """
        Interactive edit flow:
          1) Ask a search query (ID or partial name).
          2) Let the user pick among matches.
          3) Edit one field at a time (validated) with per-field confirmation.
          4) Confirm and save at the end.
        """
        query = player_views.prompt_search_player_query()
        if not query:
            return

        matches = self._search_players(query)
        if not matches:
            player_views.notify_no_match()
            return

        player = player_views.prompt_select_player(matches)
        if not player:
            return

        original_id = player.national_id  # used if ID changes

        while True:
            # Show a compact recap before each change
            player_views.display_player_brief_info(player)

            choice = player_views.prompt_select_field_to_edit()
            if choice is None:
                # Cancel the whole edit
                return
            if choice == "done":
                if player_views.confirm_save_changes():
                    self._save_player(player, original_id=original_id)
                    player_views.notify_saved()
                return

            # Map attribute -> French label for confirmation message
            label_fr = {
                "last_name": FIELD_LABELS["last_name"],
                "first_name": FIELD_LABELS["first_name"],
                "birthdate": FIELD_LABELS["birthdate"],
                "national_id": FIELD_LABELS["national_id"],
            }[choice]

            # Ask new value with same validation rules as creation
            new_val = player_views.prompt_new_value_for_field(choice)
            if new_val is None:
                # User cancelled this field; keep editing loop
                continue

            old_display = getattr(player, choice, "")
            new_display = new_val

            # Unique ID guard if changing national_id
            if choice == "national_id":
                normalized_new_id = self._normalize_id(new_val)
                if normalized_new_id != player.national_id and self._is_national_id_taken(
                    normalized_new_id, exclude_id=player.national_id
                ):
                    player_views.notify_duplicate_id()
                    continue

            # Confirm this specific change
            if not player_views.confirm_field_change(label_fr, str(old_display), str(new_display)):
                continue

            # Apply change via dedicated setters (centralized validation/normalization)
            try:
                if choice == "last_name":
                    player.set_last_name(new_val)
                elif choice == "first_name":
                    player.set_first_name(new_val)
                elif choice == "birthdate":
                    player.set_birthdate(new_val)
                elif choice == "national_id":
                    player.set_national_id(new_val)
            except ValueError as e:
                player_views.display_error_message(str(e))
                continue

    # -----------------------
    # User-facing menu loop
    # -----------------------

    def manage_players(self):
        """
        Simple player management loop (view, add, edit, back, quit).
        Exits the entire program if user chooses '5'.
        """
        while True:
            choice = player_views.show_player_main_menu()

            if choice == "1":  # view players
                players = self.load_players()
                # compute live stats from all tournaments
                tournaments_repo = TournamentRepository()
                all_tournaments = tournaments_repo.load_all_tournaments()
                stats_index = build_player_tournament_index(all_tournaments)

                player_views.display_all_players(
                    players,
                    scope="global",
                    stats_index=stats_index
                )

            elif choice == "2":  # add new player
                self.handle_add_new_player()

            elif choice == "3":  # edit a player
                self.edit_player_flow()

            elif choice == "4":  # back to caller
                return

            elif choice == "5":  # quit program
                console.print("✅ Sauvegarde en cours et fermeture...")
                sys.exit(0)

            else:
                player_views.display_error_message("Option invalide.")
