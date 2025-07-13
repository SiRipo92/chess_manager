from chess_manager.models.player import Player
import json
import os
import re
from typing import List


class PlayerController:
    """
    Contrôleur responsable de la gestion des joueurs :
    ajout, chargement, tri, filtrage.
    """

    def __init__(self, filepath: str):
        """
        Initialise le contrôleur avec le chemin du fichier JSON.

        Paramètre :
            filepath (str) : Chemin du fichier de sauvegarde des joueurs.
        """
        self.filepath = filepath

    def add_player(self, last_name: str, first_name: str, birthdate: str, national_id: str) -> bool:
        """
        Crée un nouveau joueur et l’ajoute à la base de données (JSON),
        si l'ID n'est pas déjà utilisé et que le format est correct.

        Retour :
            bool : True si ajouté avec succès, False sinon.
        """
        if not self._is_valid_id(national_id):
            # ID invalide : ne respecte pas le format
            return False

        players = self.load_all_players()

        # Vérifie si l'ID existe déjà
        for player in players:
            if player.national_id == national_id:
                return False

        # Créer un nouvel objet Player
        new_player = Player(last_name, first_name, birthdate, national_id)
        players.append(new_player)
        self.save_all_players(players)
        return True

    @staticmethod
    def _is_valid_id(national_id: str) -> bool:
        """
        Vérifie si l'identifiant respecte le format attendu (2 lettres + 5 chiffres).
        Exemple valide : AB12345

        Retour :
            bool : True si l'ID est valide, sinon False.
        """
        return bool(re.match(r"^[A-Z]{2}[0-9]{5}$", national_id))

    def load_all_players(self) -> List[Player]:
        """
        Charge tous les joueurs enregistrés depuis le fichier JSON.

        Retour :
            List[Player] : Liste des joueurs existants.
        """
        if not os.path.exists(self.filepath):
            return []

        try:
            return Player.load_all_players(self.filepath)
        except FileNotFoundError:
            return []

    def save_all_players(self, players: List[Player]) -> None:
        """
        Sauvegarde la liste complète des joueurs dans le fichier JSON.

        Paramètre :
            players (List[Player]) : Liste des joueurs à sauvegarder.
        """
        with open(self.filepath, "w", encoding="utf-8") as f:
            # On suppose que Player.to_dict() est bien défini dans models/player.py
            data = [p.to_dict() for p in players]
            json.dump(data, f, indent=2, ensure_ascii=False)

    def sort_players_by_name(self, players: List[Player]) -> List[Player]:
        """
        Trie les joueurs par ordre alphabétique (nom, prénom).

        Retour :
            List[Player] : Liste triée.
        """
        return sorted(players, key=lambda p: (p.last_name.lower(), p.first_name.lower()))

    def filter_players_by_id(self, players: List[Player], query: str) -> List[Player]:
        """
        Filtre les joueurs dont l’identifiant contient une chaîne donnée.

        Retour :
            List[Player] : Liste filtrée.
        """
        return [p for p in players if query.lower() in p.national_id.lower()]

    def filter_players_by_name(self, players: List[Player], query: str) -> List[Player]:
        """
        Filtre les joueurs dont le nom de famille contient une chaine donnée
        """
        return [p for p in players if query.lower() in p.last_name.lower()]
