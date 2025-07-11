from typing import List
from models.match import Match


class MatchRepository:
    """
    Gère le stockage et la récupération des objets Match à partir de fichiers JSON.

    Attributs :
        dir_path (str) : Répertoire de stockage des données de matchs.
        matches (list) : Liste des matchs actuellement chargés en mémoire.
    """

    def __init__(self, dir_path: str) -> None:
        self.dir_path: str = dir_path
        self.matches: list = []

    def load_all(self) -> None:
        """
        Charge tous les matchs depuis les fichiers JSON du répertoire.
        """
        pass

    def save_all(self) -> None:
        """
        Sauvegarde tous les matchs actuels dans des fichiers JSON.
        """
        pass

    def add_match(self, match: Match) -> None:
        """
        Ajoute un match à la liste en mémoire et le marque pour sauvegarde.
        """
        pass

    def serialize(self, match: Match) -> dict:
        """
        Sérialise un objet Match en dictionnaire.
        """
        pass

    def deserialize(self, data: dict) -> Match:
        """
        Désérialise un dictionnaire
        """
        pass