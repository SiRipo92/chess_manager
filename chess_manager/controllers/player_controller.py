import json
from json import JSONDecodeError
import os
from rich.console import Console
from typing import List, Optional, Tuple

from chess_manager.constants.navigation.labels import OPTION_RETURN_TO_CLUB_MENU, OPTION_RETURN_TO_PLAYERS_MENU
from chess_manager.models.player_models import Player
from chess_manager.constants.player_fields import VALIDATION_MAP
from chess_manager.utils.player_validators import is_valid_name, is_valid_birthdate, is_valid_id
from chess_manager.views import player_views
from chess_manager.constants.player_repository import BASE_PLAYER_DIRECTORY, PLAYER_FILENAME
from chess_manager.constants.navigation import labels, titles, menu_keys
from chess_manager.utils.helpers import (
    display_error_message,
    raise_quit_program,
)
from chess_manager.utils.navigation import menu_builder, menu_map

console = Console()


# Unified field definitions with validator and setter
FIELD_DEFINITIONS = {
    labels.FIELD_LAST_NAME: {
        "label": labels.FIELD_LAST_NAME,
        "validator": is_valid_name,
        "setter": Player.set_last_name
    },
    labels.FIELD_FIRST_NAME: {
        "label": labels.FIELD_FIRST_NAME,
        "validator": is_valid_name,
        "setter": Player.set_first_name
    },
    labels.FIELD_BIRTHDATE: {
        "label": labels.FIELD_BIRTHDATE,
        "validator": is_valid_birthdate,
        "setter": Player.set_birthdate
    },
    labels.FIELD_ID: {
        "label": labels.FIELD_ID,
        "validator": is_valid_id,
        "setter": Player.set_national_id
    },
}


def get_player_filepath_for_city(city: str) -> str:
    """
    Retourne le chemin complet du fichier players.json pour une ville donnée.
        Exemple : city='Nanterre' ➜ 'data/players/Nanterre/players.json'
    """
    # Function needed to set up Player File storage by Location
    sanitized_city = city.strip().title()
    return os.path.join(str(BASE_PLAYER_DIRECTORY), sanitized_city, str(PLAYER_FILENAME))


def get_menu_actions(self) -> dict:
    """
    Retourne un dictionnaire d'actions du menu, mappées à des méthodes du contrôleur.
    """
    return {
        labels.OPTION_ADD_NEW_PLAYER: self.handle_add_new_player,
        labels.OPTION_SHOW_PLAYERS: lambda: player_views.display_all_players(self.load_players()),
        labels.OPTION_SHOW_PLAYER_FILE: self.handle_player_file_view,

        labels.OPTION_QUIT_PROGRAM: lambda: exit(),
    }


class PlayerController:
    """
    Gère les opérations CRUD et de consultation/statistiques sur les joueurs.
    """

    # ===============================
    # 1. Initialisation & Persistence
    # ===============================

    def __init__(self, players: list[Player], filepath: str, city: str) -> None:
        """
        Initialise le contrôleur des joueurs avec un sous-dossier de localisation.
        """
        self.players = players
        self.file_path = filepath
        self.city = city
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """
        Crée un fichier JSON vide (liste) s’il n’existe pas encore.
        """
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            try:
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)  # type: ignore
            except IOError as e:
                raise IOError(f"Impossible de créer {self.file_path} : {e}") from e

    def load_players(self) -> List[Player]:
        """
        Charge tous les joueurs depuis le fichier JSON.
        Retour
        ------ List[Player] : Liste éventuellement vide de joueurs.
        """
        if not os.path.exists(self.file_path):
            return []  # Premier lancement : aucun joueur.
        try:
            return Player.load_all_players(self.file_path)
        except (json.JSONDecodeError, ValueError) as e:
            # Fichier corrompu ou données mal formées.
            print(f"❌ Impossible de lire {self.file_path} : {e}")
            return []

    def save_players(self, players: List[Player]) -> None:
        """
        Écrit la liste complète des joueurs dans le fichier JSON.

        Paramètre
        --------- players : List[Player]
        Liste à persister.
        """
        self._ensure_file_exists()

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in players], f, indent=2, ensure_ascii=False)  # type: ignore
        except IOError as e:
            print(f"❌ Erreur de sauvegarde : {e}")

    # ===================
    # 2. Player Creation
    # ===================

    def add_new_player(self, last_name: str, first_name: str, birthdate: str, national_id: str
            ) -> Tuple[bool, Optional[str]]:
        """
        Tente d’ajouter un nouveau joueur avec validations.
        Retour : Tuple(bool, str) :
            - True + None si succès
            - False + message d’erreur sinon
        """
        field_inputs = {
            "Nom de famille": last_name,
            "Prénom": first_name,
            "Date de naissance": birthdate,
            "Identifiant national": national_id,
        }

        # Valide les champs saisis via la map VALIDATION_MAP
        for label, value in field_inputs.items():
            validator = VALIDATION_MAP.get(label)
            if not value:
                return False, f"Le champ '{label}' est obligatoire."
            if validator and not validator(value):
                return False, f"Le champ '{label}' est invalide."

        try:
            players = self.load_players()
            # Empêche la duplication d'identifiants
            if any(p.national_id == national_id for p in players):
                return False, "Cet identifiant est déjà utilisé."

            new_player = Player(last_name, first_name, birthdate, national_id)
            players.append(new_player)
            self.save_players(players)
            return True, None
        except (IOError, JSONDecodeError, ValueError) as e:
            return False, f"Erreur système lors de l'ajout du joueur : {e}"

    def handle_add_new_player(self) -> None:
        """
        Gère le processus d’ajout d’un nouveau joueur avec validation et confirmation.
        """
        result = player_views.prompt_new_player_inputs_with_review()
        if result is None:
            display_error_message("Ajout annulé.")
            return
        last_name, first_name, birthdate, national_id = result
        success, message = self.add_new_player(last_name, first_name, birthdate, national_id)
        if success:
            player_views.confirm_player_added()
        else:
            display_error_message(message)

    # ======================
    # 3. Player Retrieval
    # ======================

    def get_player_by_id(self, national_id: str) -> Optional[Player]:
        """
        Récupère un joueur à partir de son identifiant national.

        Paramètre :
            national_id (str) : L’identifiant unique du joueur.

        Retour :
            Player | None : L'objet joueur correspondant, ou None si introuvable.
        """
        try:
            players = self.load_players()
            for p in players:
                if isinstance(p, Player):
                    if p.national_id == national_id:
                        return p
                elif isinstance(p, dict):
                    if p.get("national_id") == national_id:
                        return Player.from_dict(p)
            return None
        except Exception as e:
            display_error_message(f"Erreur de lecture des joueurs : {e}")
            return None

    def handle_player_file_view(self) -> None:
        """
        Simplifies the handling of the requests/displays
        for the retrieving the player id and retrieving the player profile
        """
        player_id = player_views.prompt_player_national_id()
        player = self.get_player_by_id(player_id)
        if player:
            player_views.display_full_player_profile(player)
        else:
            player_views.display_error_message("Aucun joueur trouvé.")


    # ======================
    # 4. Sorting & Searching
    # ======================

    @staticmethod
    def sort_players_by_name(players: List[Player], reverse: bool = False) -> List[Player]:
        """
            Trie les joueurs par nom puis prénom.

            :param players: Liste des joueurs à trier.
            :param reverse: Si True, tri dans l'ordre Z → A ; sinon A → Z.
            :return: Liste triée des joueurs.
            """
        return sorted(players, key=lambda p: (p.last_name.lower(), p.first_name.lower()), reverse=reverse)

    @staticmethod
    def sort_players_by_ranking(players: List[Player]) -> List[Player]:
        """
        Trie par score total décroissant (méthode get_total_score()).
        """
        return sorted(players, key=lambda p: p.get_total_score(), reverse=True)

    @staticmethod
    def find_player_by_id(players: List[Player], query: str) -> List[Player]:
        """
        Filtre les joueurs dont l’ID contient la sous-chaîne « query » (insensible à la casse).
        """
        return [p for p in players if query.lower() in p.national_id.lower()]

    @staticmethod
    def find_player_by_name(players: List[Player], query: str) -> List[Player]:
        """
        Filtre les joueurs dont le NOM de famille contient « query ».
        """
        return [p for p in players if query.lower() in p.last_name.lower()]

    # ======================
    # 5. Statistics & Match History
    # ======================

    def get_player_statistics(self) -> None:
        """
        Demande un ID, récupère le joueur correspondant, puis affiche ses stats.
        Les exceptions sont gérées pour éviter un crash lors de l’affichage.
        """
        player_id = player_views.prompt_player_national_id()

        player = self.get_player_by_id(player_id)
        if not player:
            display_error_message("Aucun joueur trouvé avec cet identifiant.")
            return
        try:
            stats = player.get_stats_summary(None)
            player_views.display_stats_summary(stats)
        except Exception as e:
            display_error_message(f"Erreur lors de la récupération des stats : {e}")

    def record_match_for_player(self) -> None:
        """
        Workflow actuel (temporaire) : permet d’enregistrer un match
        en entrant manuellement le nom + le résultat.

        FUTURE AMÉLIORATION :
        Ce workflow sera remplacé par un enregistrement automatique
        après validation du résultat d’un Match (lié à un tournoi).

        Le système devra :
            - identifier le match automatiquement
            - appliquer le résultat à chaque joueur (victoire, défaite, nul)
        """

        player_id = player_views.prompt_player_national_id()
        player = self.get_player_by_id(player_id)
        if not player:
            display_error_message("Aucun joueur trouvé avec cet identifiant.")
            return
        match_name, result = player_views.prompt_match_result()
        if not match_name or not result:
            return
        try:
            player.record_match_result(match_name, result)
            players = self.load_players()
            for i, p in enumerate(players):
                if p.national_id == player.national_id:
                    players[i] = player
                    break
            self.save_players(players)
            console.print("✅ Match enregistré avec succès.")
        except ValueError as e:
            display_error_message(str(e))
        except Exception as e:
            display_error_message(f"Erreur inattendue : {e}")

    # ======================
    # 6. Player Management
    # ======================
    def manage_players(self):
        while True:
            action = player_views.display_player_management_menu()

            if action == labels.OPTION_SHOW_PLAYERS:
                players = self.load_players()
                player_views.display_all_players(players)

            elif action == labels.OPTION_SORT_PLAYERS:
                result = self.handle_user_sort_filter_menu()
                # Option Go Back or Quit Program
                if result == labels.OPTION_QUIT_PROGRAM:
                    return
                elif result == labels.OPTION_GO_BACK:
                    continue

            elif action == labels.OPTION_SHOW_PLAYER_FILE:
                player_id = player_views.prompt_player_national_id()
                player = self.get_player_by_id(player_id)
                if not player:
                    display_error_message("Aucun joueur trouvé avec cet ID.")
                else:
                    action_result = self.handle_actions_on_player_page_menu(player)
                    if action_result == OPTION_RETURN_TO_CLUB_MENU:
                        return  # back to club menu
                    elif action_result == labels.OPTION_RETURN_TO_STARTING_MENU:
                        return  # or bubble up as appropriate
                    elif action_result == labels.OPTION_RETURN_TO_PLAYER_FILE:
                        continue  # stay on player view / re-enter loop as needed

            elif action == labels.OPTION_ADD_NEW_PLAYER:
                self.handle_add_new_player()


            elif action == labels.OPTION_QUIT_PROGRAM:

                raise_quit_program()


            elif action == labels.STANDARD_ESCAPE_SEQUENCE:
                break

            else:
                display_error_message("Option invalide.")

    # Méthode pour modifier le bio d'un joueur
    def update_player_info(self, player: Player) -> None:
        """
        Permet à l’utilisateur de modifier une information du joueur avec confirmation.
        """
        while True:
            field_to_edit = player_views.prompt_edit_player_field_choice()
            if field_to_edit == labels.OPTION_CANCEL_PLAYER_MODIFICATION:
                return

            field_def = FIELD_DEFINITIONS.get(field_to_edit)
            if not field_def:
                player_views.display_error_message("Champ non reconnu.")
                continue

            validator = field_def["validator"]
            setter = field_def["setter"]

            new_value = player_views.prompt_field_with_validation(f"{field_to_edit} :", validator)

            if not new_value:
                player_views.display_error_message("Aucune valeur saisie.")
                continue

            confirmation = player_views.confirm_field_update(field_to_edit, new_value)
            if confirmation == labels.OPTION_CANCEL_PLAYER_MODIFICATION:
                return
            elif confirmation == labels.OPTION_TRY_AGAIN:
                continue

            # Uniqueness check for national ID
            if field_to_edit == labels.FIELD_ID:
                all_players = self.load_players()
                if any(p.national_id == new_value and p != player for p in all_players):
                    player_views.display_error_message("Cet identifiant est déjà utilisé par un autre joueur.")
                    continue

            setter(player, new_value)
            self._save_player(player)
            player_views.confirm_player_updated()
            player_views.display_full_player_profile(player)
            return

    def _save_player(self, updated_player: Player) -> None:
        """
        Helper function to save updates to a single player
        """
        players = self.load_players()
        for idx, p in enumerate(players):
            if p.national_id == updated_player.national_id or p is updated_player:
                players[idx] = updated_player
                break
        self.save_players(players)

    def handle_actions_on_player_page_menu(self, player: Player) -> str:
        """
        Gère les actions après affichage de la fiche d’un joueur.
        Permet de modifier les informations ou de retourner à différents menus.
        """
        """
            Gère les actions après affichage de la fiche d’un joueur.
            Retourne une constante indiquant ce que l’appelant doit faire ensuite.
            """
        while True:
            action = player_views.ask_yes_no(titles.PLAYER_MOD_YES_NO_TITLE)
            if action == labels.OPTION_YES:
                self.update_player_info(player)
                # After editing, stay on player file view
                return labels.OPTION_RETURN_TO_PLAYER_FILE

            elif action == labels.OPTION_NO:
                next_action = player_views.display_menu_from_key(
                    menu_keys.PLAYER_MODIFICATION_ESCAPE_SEQUENCE
                )
                if not next_action:
                    console.print("[red]Menu introuvable ou annulé. Retour à la fiche joueur.[/red]")
                    return labels.OPTION_RETURN_TO_PLAYER_FILE

                if next_action == labels.OPTION_CANCEL_PLAYER_MODIFICATION:
                    return labels.OPTION_RETURN_TO_PLAYER_FILE  # go back to profile / yes-no loop

                elif next_action == labels.OPTION_RETURN_TO_PLAYER_FILE:
                    # Redisplay and re-prompt
                    player_views.display_full_player_profile(player)
                    continue  # loop again to ask yes/no

                elif next_action == labels.OPTION_RETURN_TO_STARTING_MENU:
                    return labels.OPTION_RETURN_TO_STARTING_MENU

                elif next_action == labels.OPTION_QUIT_PROGRAM:
                    raise SystemExit()

                else:
                    display_error_message("Option invalide.")
                    return None

            else:
                display_error_message("Choix invalide.")
                return None


    def handle_user_sort_filter_menu(self) -> str:
        while True:
            players = self.load_players()
            choice = player_views.show_player_sort_filter_menu()

            # Sort by ascending last names (normal)
            if choice == labels.OPTION_SORT_BY_NAME_ASC:
                sorted_players = self.sort_players_by_name(players)
                player_views.display_all_players(sorted_players)
            # Sort by descending last names
            elif choice == labels.OPTION_SORT_BY_NAME_DESC:
                sorted_players = self.sort_players_by_name(players, reverse=True)
                player_views.display_all_players(sorted_players)
            # sort by player rank
            elif choice == labels.OPTION_SORT_BY_RANKING:
                ranked_players = self.sort_players_by_ranking(players)
                player_views.display_all_players(ranked_players)
            # filter by partial ID
            elif choice == labels.OPTION_SEARCH_BY_ID:
                partial_id = player_views.prompt_player_national_id("Entrez une partie de l’ID à rechercher : ")
                filtered_players = self.find_player_by_id(players, partial_id)
                player_views.display_all_players(filtered_players)
            # filter by last name
            elif choice == labels.OPTION_SEARCH_BY_NAME:
                partial_name = player_views.prompt_player_name_filter()
                filtered_players = self.find_player_by_name(players, partial_name)
                player_views.display_all_players(filtered_players)
            # view a player's profile
            elif choice == labels.OPTION_VIEW_PLAYER_FILE:
                player_id = player_views.prompt_player_national_id()
                player = self.get_player_by_id(player_id)
                if player:
                    player_views.display_full_player_profile(player)
                    # Show player profile menu
                    result = self.handle_actions_on_player_page_menu(player)
                    if result == labels.OPTION_RETURN_TO_CLUB_MENU:
                        return # The action that handles this return to club menu view & controller
                    elif result == labels.OPTION_RETURN_TO_PLAYERS_MENU:
                        return # The action that handles this return to player menu view & controller
                else:
                    display_error_message("Aucun joueur trouvé avec cet ID.")

            elif choice == labels.OPTION_RETURN_TO_CLUB_MENU:
                return # The action that returns the player to the club menu view & controller

            elif choice == labels.OPTION_QUIT_PROGRAM:
                raise_quit_program()

            else:
                display_error_message("Option invalide.")
