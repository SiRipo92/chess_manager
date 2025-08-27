import json
import os
import sys
from typing import List, Optional, Tuple
from rich.console import Console
from chess_manager.models.player_models import Player
from chess_manager.constants.player_fields import VALIDATION_MAP
from chess_manager.views import player_views

console = Console()


class PlayerController:
    """
    Gère les opérations de base sur les joueurs : création, lecture, persistance.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """ Checks if file exists, if not - it creates it """
        if not os.path.exists(self.file_path):
            try:
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
            except IOError as e:
                raise IOError(f"Impossible de créer {self.file_path} : {e}") from e

    def load_players(self) -> List[Player]:
        """Charge les joueurs depuis le JSON et les retourne triés par nom."""
        if not os.path.exists(self.file_path):
            return []
        try:
            players = Player.load_all_players(self.file_path)
            # return players list alphabetically as detailed in requirements
            return self.sort_players_by_name(players)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Impossible de lire {self.file_path} : {e}")
        return []

    # -----------------------
    # Création
    # -----------------------
    def add_new_player(
        self, last_name: str, first_name: str, birthdate: str, national_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Add new player to list"""
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
            players = self.load_players()
            normalized_id = national_id.strip().upper()
            if any(p.national_id == normalized_id for p in players):
                return False, "Cet identifiant est déjà utilisé."

            # Create the player with the normalized ID
            new_player = Player(last_name, first_name, birthdate, normalized_id)
            players.append(new_player)
            self.save_players(players)
            return True, None
        except (IOError, ValueError) as e:
            return False, f"Erreur système lors de l'ajout du joueur : {e}"

    def handle_add_new_player(self) -> None:
        """Handles the confirmations and errors when reviewing an added new player """
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

    # -----------------------
    # Récupération
    # -----------------------
    def get_player_by_id(self, national_id: str) -> Optional[Player]:
        """ Filter player by id """
        normalized_id = national_id.strip().upper()
        players = self.load_players()
        for p in players:
            if p.national_id == normalized_id:
                return p
        return None

    # -----------------------
    # Helpers internes
    # -----------------------
    def _save_player(self, updated_player: Player) -> None:
        """Serialize and save new player to player file"""
        players = self.load_players()
        for idx, p in enumerate(players):
            if p.national_id == updated_player.national_id:
                players[idx] = updated_player
                break
        else:
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

    # -----------------------
    # Sorting helpers
    # -----------------------
    @staticmethod
    def sort_players_by_name(players: List[Player], reverse: bool = False) -> List[Player]:
        """
        Trie les joueurs par NOM puis PRÉNOM, insensible à la casse.
        """
        return sorted(players, key=lambda p: (p.last_name.lower(), p.first_name.lower()), reverse=reverse)

    # -----------------------
    # Interface utilisateur (simplifiée)
    # -----------------------
    def manage_players(self):
        """
        Boucle de gestion simple des joueurs : voir, ajouter, retour, quitter.
        Quitte complètement si l'utilisateur choisit '4'.
        """
        while True:
            choice = player_views.show_player_main_menu()

            if choice == "1":  # voir les joueurs
                players = self.load_players()
                player_views.display_all_players(players)

            elif choice == "2":  # ajouter un joueur
                self.handle_add_new_player()

            elif choice == "3":  # retour
                return  # remonte au menu appelant

            elif choice == "4":  # quitter programme
                console.print("✅ Sauvegarde en cours et fermeture...")
                sys.exit(0)

            else:
                player_views.display_error_message("Option invalide.")