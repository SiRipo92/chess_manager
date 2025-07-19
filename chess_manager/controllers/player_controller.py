import json
from json import JSONDecodeError
import os
from rich.console import Console
from typing import List, Optional, Tuple

from chess_manager.models.player_models import Player
from chess_manager.constants.player_fields import VALIDATION_MAP
from chess_manager.views import player_views
from chess_manager.utils.player_validators import is_valid_id, is_valid_birthdate


console = Console()


# CONSTANTS
ACTION_UPDATE_INFO = "1"
ACTION_BACK_TO_PLAYERS = "2"
ACTION_BACK_TO_MAIN = "3"


class PlayerController:
    """
    Gère les opérations CRUD et de consultation/statistiques sur les joueurs.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialise le contrôleur avec le chemin du fichier JSON des joueurs.
        """
        self.file_path = file_path  # 🔁 cette ligne est essentielle
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """
        Crée un fichier JSON vide (liste) s’il n’existe pas encore.
        """
        if not os.path.exists(self.file_path):
            try:
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
            except IOError as e:
                raise IOError(f"Impossible de créer {self.file_path} : {e}") from e

    def load_players(self) -> List[Player]:
        """
        Charge tous les joueurs depuis le fichier JSON.

        Retour
        ------
        List[Player] : Liste éventuellement vide de joueurs.
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
        ---------
        players : List[Player]
            Liste à persister.
        """
        self._ensure_file_exists()

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in players], f, indent=2, ensure_ascii=False)  # type: ignore
        except IOError as e:
            print(f"❌ Erreur de sauvegarde : {e}")

    def add_new_player(
            self, last_name: str, first_name: str, birthdate: str, national_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Tente d’ajouter un nouveau joueur avec validations.

        Retour :
            Tuple(bool, str) :
                - True + None si succès
                - False + message d’erreur sinon
        """
        field_inputs = {
            "Nom de famille": last_name,
            "Prénom": first_name,
            "Date de naissance": birthdate,
            "Identifiant national": national_id,
        }

        # Centralized validation loop
        for label, value in field_inputs.items():
            validator = VALIDATION_MAP.get(label)
            if not value:
                return False, f"Le champ '{label}' est obligatoire."
            if validator and not validator(value):
                return False, f"Le champ '{label}' est invalide."

        try:
            players = self.load_players()
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
            player_views.display_error_message("Ajout annulé.")
            return

        last_name, first_name, birthdate, national_id = result

        success, message = self.add_new_player(last_name, first_name, birthdate, national_id)

        if success:
            player_views.confirm_player_added()
        else:
            player_views.display_error_message(message)

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
            player_views.display_error_message(f"Erreur de lecture des joueurs : {e}")
            return None

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
    def find_players_by_id(players: List[Player], query: str) -> List[Player]:
        """
        Filtre les joueurs dont l’ID contient la sous-chaîne « query » (insensible à la casse).
        """
        return [p for p in players if query.lower() in p.national_id.lower()]

    @staticmethod
    def find_players_by_name(players: List[Player], query: str) -> List[Player]:
        """
        Filtre les joueurs dont le NOM de famille contient « query ».
        """
        return [p for p in players if query.lower() in p.last_name.lower()]

    def get_player_statistics(self) -> None:
        """
        Demande un ID, récupère le joueur correspondant, puis affiche ses stats.
        Les exceptions sont gérées pour éviter un crash lors de l’affichage.
        """
        player_id = player_views.prompt_player_national_id()

        player = self.get_player_by_id(player_id)
        if not player:
            player_views.display_error_message("Aucun joueur trouvé avec cet identifiant.")
            return
        try:
            stats = player.get_stats_summary(None)
            player_views.display_stats_summary(stats)
        except Exception as e:
            player_views.display_error_message(f"Erreur lors de la récupération des stats : {e}")

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
            player_views.display_error_message("Aucun joueur trouvé avec cet identifiant.")
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
            player_views.display_error_message(str(e))
        except Exception as e:
            player_views.display_error_message(f"Erreur inattendue : {e}")

    def manage_players(self):
        while True:
            subchoice = player_views.show_player_main_menu()

            if subchoice == "1":
                players = self.load_players()
                player_views.display_all_players(players)

            elif subchoice == "2":
                result = self.handle_user_sort_filter_menu()
                if result == "return_to_main":
                    return
                elif result == "return_to_players":
                    continue

            elif subchoice == "3":
                player_id = player_views.prompt_player_national_id()
                player = self.get_player_by_id(player_id)
                if not player:
                    player_views.display_error_message("Aucun joueur trouvé avec cet ID.")
                else:
                    player_views.display_full_player_profile(player)
                    action_result = self.handle_actions_on_player_page_menu(player)
                    if action_result == "return_to_main":
                        return

            elif subchoice == "4":
                self.handle_add_new_player()

            elif subchoice == "5":
                break

            else:
                player_views.display_error_message("Option invalide.")

    # Méthode pour modifier le bio d'un joueur
    def update_player_info(self, player: Player) -> None:
        """
        Permet à l’utilisateur de modifier une information du joueur avec confirmation.
        """
        while True:
            field_to_edit = player_views.prompt_edit_player_field_choice()
            if field_to_edit == "Annuler":
                return

            new_value = player_views.prompt_field_with_validation(
                f"{field_to_edit} :", VALIDATION_MAP[field_to_edit]
            )

            if not new_value:
                player_views.display_error_message("Aucune valeur saisie.")
                continue

            confirmation = player_views.confirm_field_update(field_to_edit, new_value)
            if confirmation == "Annuler":
                return
            elif confirmation == "Réessayer":
                continue

            # Validation-specific logic for national_id uniqueness
            if field_to_edit == "Identifiant national":
                all_players = self.load_players()
                if any(p.national_id == new_value and p != player for p in all_players):
                    player_views.display_error_message("Cet identifiant est déjà utilisé par un autre joueur.")
                    continue
                player.set_national_id(new_value)

            elif field_to_edit == "Nom de famille":
                player.set_last_name(new_value)

            elif field_to_edit == "Prénom":
                player.set_first_name(new_value)

            elif field_to_edit == "Date de naissance":
                player.set_birthdate(new_value)

            # Save player changes
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

    def handle_actions_on_player_page_menu(self, player: Player, max_loops: int = 10) -> str:
        """
        Gère les actions sur la fiche d’un joueur. Retourne une chaîne selon l’action choisie.

        Paramètres :
            player (Player): Le joueur concerné.
            max_loops (int): Nombre maximal d’itérations pour éviter une boucle infinie
            en cas d’erreur (par défaut : 10).

        Retour :
            str : "return_to_players", "return_to_main", ou "" si aucune sortie claire.
        """
        loop_count = 0

        while loop_count < max_loops:
            action = player_views.display_user_action_menu_for_player_page(player)

            if action == ACTION_UPDATE_INFO:
                self.update_player_info(player)

            elif action == ACTION_BACK_TO_PLAYERS:
                return "return_to_players"

            elif action == ACTION_BACK_TO_MAIN:
                return "return_to_main"

            else:
                player_views.display_error_message("Option invalide.")

            loop_count += 1

        # Si la boucle dépasse le maximum, afficher une erreur et sortir.
        player_views.display_error_message("Trop de tentatives invalides. Retour au menu précédent.")
        return "return_to_main"

    def handle_user_sort_filter_menu(self) -> str:
        while True:
            players = self.load_players()
            choice = player_views.show_player_sort_filter_menu()

            if choice == "1":
                sorted_players = self.sort_players_by_name(players)
                player_views.display_all_players(sorted_players)

            elif choice == "2":
                sorted_players = self.sort_players_by_name(players, reverse=True)
                player_views.display_all_players(sorted_players)

            elif choice == "3":
                ranked_players = self.sort_players_by_ranking(players)
                player_views.display_all_players(ranked_players)

            elif choice == "4":
                partial_id = player_views.prompt_player_national_id("Entrez une partie de l’ID à rechercher : ")
                filtered_players = self.find_players_by_id(players, partial_id)
                player_views.display_all_players(filtered_players)

            elif choice == "5":
                partial_name = player_views.prompt_player_name_filter()
                filtered_players = self.find_players_by_name(players, partial_name)
                player_views.display_all_players(filtered_players)

            elif choice == "6":
                player_id = player_views.prompt_player_national_id()
                player = self.get_player_by_id(player_id)
                if player:
                    player_views.display_full_player_profile(player)
                    result = self.handle_actions_on_player_page_menu(player)
                    if result == "return_to_main":
                        return "return_to_main"
                    elif result == "return_to_players":
                        return "return_to_players"
                else:
                    player_views.display_error_message("Aucun joueur trouvé avec cet ID.")

            elif choice == "7":
                return "return_to_players"

            elif choice == "8":
                exit()

            else:
                player_views.display_error_message("Option invalide.")
