from typing import List
from chess_manager.models.tournament import Tournament


class TournamentRepository:
    """
    Gère la persistance des tournois : chargement, sauvegarde et recherche.

    Attributs :
        dir_path (str) : Chemin du répertoire où les fichiers JSON sont stockés.
        tournaments (List[Tournament]) : Liste des tournois chargés en mémoire.
    """

    def __init__(self, dir_path: str = "data/tournaments") -> None:
        """
        Initialise le référentiel des tournois et charge les tournois existants.

        Paramètre :
            dir_path (str) : Répertoire de sauvegarde des fichiers JSON.
        """
        pass

    def load_all_tournaments(self) -> List[Tournament]:
        """
        Charge tous les tournois depuis les fichiers JSON du répertoire.

        Retour :
            List[Tournament] : Liste des tournois chargés.
        """
        pass

    def save_tournament(self, tournament: Tournament) -> None:
        """
        Sauvegarde un tournoi dans un fichier JSON.

        Paramètre :
            tournament (Tournament) : Le tournoi à sauvegarder.
        """
        pass

    def add_tournament(self, tournament: Tournament) -> None:
        """
        Ajoute un tournoi à la mémoire et le sauvegarde sur disque.

        Paramètre :
            tournament (Tournament) : Le nouveau tournoi à ajouter.
        """
        pass

    def get_tournament_by_name(self, name: str) -> Tournament:
        """
        Recherche un tournoi par son nom.

        Paramètre :
            name (str) : Le nom du tournoi.
        Retour :
            Tournament : Le tournoi correspondant.
        """
        pass

    def get_tournament_by_location(self, location: str) -> List[Tournament]:
        """
        Recherche tous les tournois correspondant à un lieu donné.

        Paramètre :
            location (str) : Lieu du tournoi.
        Retour :
            List[Tournament] : Liste des tournois à cet endroit.
        """
        pass
