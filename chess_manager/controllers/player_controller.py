import json
import os
import re
from typing import List, Optional

from chess_manager.models.player import Player
from chess_manager.views import player_views


class PlayerController:
    """
    Gère les opérations CRUD et de consultation/statistiques sur les joueurs.
    """

    def __init__(self, filepath: str) -> None:
        """
        Initialise le contrôleur avec le chemin du fichier JSON de persistance.

        Paramètre
        ---------
        filepath : str
            Chemin absolu ou relatif vers le fichier « players.json ».
        """
        self.filepath = filepath

    @staticmethod
    def _is_valid_id(national_id: str) -> bool:
        """
        Vérifie si l’ID est conforme au format : 2 lettres majuscules + 5 chiffres.

        :param national_id: Identifiant national à valider.
        :return: True si valide, False sinon.
        """
        return bool(re.match(r"^[A-Z]{2}[0-9]{5}$", national_id))

    def _ensure_file_exists(self) -> None:
        """
        Crée le fichier JSON vide si nécessaire afin d’éviter FileNotFoundError
        lors de la première sauvegarde.
        """
        if not os.path.exists(self.filepath):
            try:
                with open(self.filepath, "w", encoding="utf-8") as f:
                    json.dump([], f)
            except IOError as e:
                # On laisse l’erreur remonter : l’appelant décidera quoi faire.
                raise IOError(f"Impossible de créer {self.filepath} : {e}") from e

    def load_all_players(self) -> List[Player]:
        """
        Charge tous les joueurs depuis le fichier JSON.

        Retour
        ------
        List[Player] : Liste éventuellement vide de joueurs.
        """
        if not os.path.exists(self.filepath):
            return []  # Premier lancement : aucun joueur.

        try:
            return Player.load_all_players(self.filepath)
        except (json.JSONDecodeError, ValueError) as e:
            # Fichier corrompu ou données mal formées.
            print(f"❌ Impossible de lire {self.filepath} : {e}")
            return []

    def save_all_players(self, players: List[Player]) -> None:
        """
        Écrit la liste complète des joueurs dans le fichier JSON.

        Paramètre
        ---------
        players : List[Player]
            Liste à persister.
        """
        self._ensure_file_exists()

        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in players], f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"❌ Erreur de sauvegarde : {e}")

    def add_new_player(
        self,
        last_name: str,
        first_name: str,
        birthdate: str,
        national_id: str,
    ) -> bool:
        """
        Ajoute un joueur si l’ID est valide et inexistant. Renvoie True si succès.
        """
        if not self._is_valid_id(national_id):
            return False  # Format invalide.

        try:
            players = self.load_all_players()

            # Vérifier l’ID unique
            if any(p.national_id == national_id for p in players):
                return False

            new_player = Player(last_name, first_name, birthdate, national_id)
            players.append(new_player)
            self.save_all_players(players)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l’ajout du joueur : {e}")
            return False

    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        """
        Retourne un joueur correspondant à l’ID, ou None si inexistant.
        """
        players = self.load_all_players()
        return next((p for p in players if p.national_id == player_id), None)

    def sort_players_by_name(self, players: List[Player], reverse: bool = False) -> List[Player]:
        """
            Trie les joueurs par nom puis prénom.

            :param players: Liste des joueurs à trier.
            :param reverse: Si True, tri dans l'ordre Z → A ; sinon A → Z.
            :return: Liste triée des joueurs.
            """
        return sorted(players, key=lambda p: (p.last_name.lower(), p.first_name.lower()), reverse=reverse)

    def sort_players_by_ranking(self, players: List[Player]) -> List[Player]:
        """
        Trie par score total décroissant (méthode get_total_score()).
        """
        return sorted(players, key=lambda p: p.get_total_score(), reverse=True)

    def find_players_by_id(self, players: List[Player], query: str) -> List[Player]:
        """
        Filtre les joueurs dont l’ID contient la sous-chaîne « query » (insensible à la casse).
        """
        q = query.lower()
        return [p for p in players if query.lower() in p.national_id.lower()]

    def find_players_by_name(self, players: List[Player], query: str) -> List[Player]:
        """
        Filtre les joueurs dont le NOM de famille contient « query ».
        """
        q = query.lower()
        return [p for p in players if q in p.last_name.lower()]

    def view_player_statistics(self) -> None:
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
            player_views.display_player_stats(stats)
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
            player.record_match(match_name, result)
            players = self.load_all_players()
            for i, p in enumerate(players):
                if p.national_id == player.national_id:
                    players[i] = player
                    break
            self.save_all_players(players)
            print("✅ Match enregistré avec succès.")
        except ValueError as e:
            player_views.display_error_message(str(e))
        except Exception as e:
            player_views.display_error_message(f"Erreur inattendue : {e}")
