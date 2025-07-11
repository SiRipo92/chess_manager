import json
from typing import List, Optional
from models.player import Player

class PlayerRepository:
    """
    Gère la persistance des données des joueurs via un fichier JSON.

    Attributs :
        filepath (str) : Chemin du fichier JSON contenant les joueurs.
        players (List[Player]) : Liste en mémoire de tous les joueurs.
    """

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.players: List[Player] = []
        self.load_players()

    def load_players(self) -> None:
        """
        Charge les joueurs depuis un fichier JSON.
        Initialise les instances Player à partir des données chargées.
        """
        pass

    def save_players(self) -> None:
        """
        Sauvegarde la liste actuelle des joueurs dans le fichier JSON.
        """
        pass

    def add_player(self, player: Player) -> bool:
        """
        Ajoute un joueur à la base s'il n'existe pas encore.

        Paramètre :
            player (Player) : Instance de joueur à ajouter.

        Retour :
            bool : True si le joueur est ajouté, False si ID déjà présent.
        """
        pass

    def get_player_by_id(self, national_id: str) -> Optional[Player]:
        """
        Recherche un joueur par son identifiant unique.

        Retour :
            Player | None : Joueur correspondant ou None si inexistant.
        """
        pass

    def get_player_by_name(self, last_name: str, first_name: str) -> Optional[Player]:
        """
        Recherche un joueur par nom et prénom.

        Retour :
            Player | None : Joueur correspondant ou None si non trouvé.
        """
        pass

    def get_all_players(self) -> List[Player]:
        """
        Retourne tous les joueurs actuellement chargés en mémoire.
        """
        return self.players