from models.player import Player
import json
import os
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

    def add_player(self, last_name: str, first_name: str, birthdate: str, national_id: str ) -> None:
        """
        Crée un nouveau joueur et l’ajoute à la base de données.

        Paramètres :
            last_name (str) : Nom de famille du joueur.
            first_name (str) : Prénom du joueur.
            birth_date (str) : Date de naissance (YYYY-MM-DD).
            national_id (str) : Identifiant national d’échecs.
        """
        # (à implémenter plus tard) : Créer, charger, ajouter, sauvegarder
        pass

    def load_all_players(self) -> List[Player]:
        """
        Charge tous les joueurs enregistrés depuis le fichier JSON.

        Retour :
            List[Player] : Liste des joueurs existants.
        """
        pass

    def save_all_players(self, players: List[Player]) -> None:
        """
        Sauvegarde la liste complète des joueurs dans le fichier JSON.

        Paramètre :
            players (List[Player]) : Liste des joueurs à sauvegarder.
        """
        pass

    def sort_players_by_name(self, players: List[Player]) -> List[Player]:
        """
        Trie les joueurs par ordre alphabétique (nom, prénom).

        Paramètre :
            players (List[Player]) : Liste à trier.

        Retour :
            List[Player] : Liste triée.
        """
        pass

    def filter_players_by_id(self, players: List[Player], query: str) -> List[Player]:
        """
        Filtre les joueurs dont l’identifiant contient une chaîne donnée.

        Paramètres :
            players (List[Player]) : Liste de départ.
            query (str) : Sous-chaîne à rechercher dans les ID.

        Retour :
            List[Player] : Liste filtrée.
        """
        pass
