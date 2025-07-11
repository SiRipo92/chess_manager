from typing import List
from models.round import Round


class RoundRepository:
    """
    Gère le stockage et la récupération des objets Round à partir de fichiers JSON.

    Attributs :
        dir_path (str) : Répertoire de stockage des données de rounds.
        rounds (list) : Liste des rounds actuellement chargés en mémoire.
    """

    def __init__(self, dir_path: str) -> None:
        self.dir_path: str = dir_path
        self.rounds: list = []

    def load_all(self) -> None:
        """
        Charge tous les rounds depuis les fichiers JSON du répertoire.
        """
        pass

    def save_all(self) -> None:
        """
        Sauvegarde tous les rounds actuels dans des fichiers JSON.
        """
        pass

    def add_round(self, round_: Round) -> None:
        """
        Ajoute un round à la liste en mémoire et le marque pour sauvegarde.
        """
        pass

    def serialize(self, round_: Round) -> dict:
        """
        Sérialise un objet Round en dictionnaire.
        """
        pass

    def deserialize(self, data: dict) -> Round:
        """
        Désérialise un dictionnaire en objet Round.
        """
        pass