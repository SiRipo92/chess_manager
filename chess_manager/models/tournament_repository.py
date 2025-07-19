import os
import json
from datetime import datetime
from typing import List, Optional
from chess_manager.models.tournament_models import Tournament
from chess_manager.constants.tournament_repository import (
    DEFAULT_TOURNAMENT_DIRECTORY,
    TOURNAMENT_FILE_TEMPLATE
)
from chess_manager.constants.datetime_formats import DATE_FORMAT

class TournamentRepository:
    """
    Gère la persistance des tournois : chargement, sauvegarde et recherche.

    Attributs :
        dir_path (str) : Chemin du répertoire où les fichiers JSON sont stockés.
        tournaments (List[Tournament]) : Liste des tournois chargés en mémoire.
    """

    def __init__(self, dir_path: str = DEFAULT_TOURNAMENT_DIRECTORY) -> None:
        self.dir_path = dir_path
        self.tournaments: List[Tournament] = []
        self.tournaments = self.load_all_tournaments()

    def load_all_tournaments(self) -> List[Tournament]:
        """
        Charge tous les tournois depuis les fichiers JSON du répertoire.

        Retour :
            List[Tournament] : Liste des tournois chargés.
        """
        tournaments = []
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

        for location_folder in os.listdir(self.dir_path):
            location_path = os.path.join(self.dir_path, location_folder)
            if os.path.isdir(location_path):
                for filename in os.listdir(location_path):
                    if filename.endswith(".json"):
                        full_path = os.path.join(location_path, filename)
                        try:
                            with open(full_path, "r", encoding="utf-8") as file:
                                data = json.load(file)
                                tournaments.append(Tournament.from_dict(data))
                        except (json.JSONDecodeError, KeyError, ValueError) as e:
                            print(f"❌ Erreur lors du chargement de {filename} : {e}")
        return tournaments

    def save_tournament(self, tournament: Tournament) -> None:
        """
        Sauvegarde un tournoi dans un fichier JSON avec un nom de fichier unique.
        """
        sanitized_location = tournament.location.strip().replace(" ", "_")
        date_str = datetime.strptime(tournament.start_date, DATE_FORMAT).strftime(DATE_FORMAT)
        location_dir = os.path.join(self.dir_path, sanitized_location)
        os.makedirs(location_dir, exist_ok=True)

        index = 1
        while True:
            filename = TOURNAMENT_FILE_TEMPLATE.format(
                location=sanitized_location,
                index=index,
                date=date_str
            )
            full_path = os.path.join(location_dir, filename)
            if not os.path.exists(full_path):
                break
            index += 1

        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(tournament.save_tournament_to_dict(), file , indent=2, ensure_ascii=False)
        print(f"✅ Tournoi sauvegardé sous : {full_path}")

    def add_tournament(self, tournament: Tournament) -> None:
        """
        Ajoute un tournoi à la mémoire et le sauvegarde sur disque.
        """
        self.tournaments.append(tournament)
        self.save_tournament(tournament)

    def get_tournament_by_name(self, name: str) -> Optional[Tournament]:
        """
        Recherche un tournoi par son nom complet.

        Paramètre :
            name (str) : Le nom du tournoi, ex: 'Paris_2025-08-01'
        """
        for tournament in self.tournaments:
            if tournament.name == name:
                return tournament
        print(f"⚠️ Aucun tournoi trouvé avec le nom : {name}")
        return None

    def get_tournament_by_location(self, location: str) -> List[Tournament]:
        """
        Recherche tous les tournois correspondant à un lieu donné.
        """
        location_normalized = location.strip().lower()
        return [
            t for t in self.tournaments
            if t.location.strip().lower() == location_normalized
        ]
