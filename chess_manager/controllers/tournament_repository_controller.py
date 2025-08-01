from chess_manager.views.tournament_repository_views import (
    prompt_user_for_location_selection
)
from chess_manager.models.player_models import Player
from chess_manager.constants.player_repository import BASE_PLAYER_DIRECTORY
from chess_manager.utils.tournament_starter import get_player_filepath_for_city
from chess_manager.constants.navigation import labels
import os
import questionary
from rich.console import Console
import json
from typing import Tuple, List, Optional, Callable
from chess_manager.utils.helpers import raise_quit_program


console = Console()


def handle_create_new_group() -> Optional[Tuple[str, str, List[Player]]]:
    city = questionary.text("Nom de la ville pour le nouveau groupe de joueurs :").ask()
    if not city:
        return None
    city = city.strip().title()
    filepath = get_player_filepath_for_city(city)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("[]")
    return city, filepath, []


def handle_import_group() -> Optional[Tuple[str, str, List[Player]]]:
    city = questionary.text("Nom de la ville à associer à ce groupe de joueurs :").ask()
    if not city:
        return None
    city = city.strip().title()
    filepath = get_player_filepath_for_city(city)

    source_path = questionary.path(
        "Entrez le chemin absolu du fichier 'players.json' à importer :"
    ).ask()
    if not source_path or not os.path.exists(source_path):
        console.print("❌ [red]Fichier introuvable ou chemin vide.[/red]")
        return None

    try:
        with open(source_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            players = [Player.from_dict(p) for p in data]
    except Exception as e:
        console.print(f"❌ [red]Erreur de lecture : {e}[/red]")
        return None

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in players], f, indent=4, ensure_ascii=False)

    return city, filepath, players

# 2. Now the functions exist, safe to reference them
MENU_ACTIONS: dict[str, Callable[[], Optional[Tuple[str, str, List[Player]]]]] = {
    labels.OPTION_CREATE_NEW_PLAYERS_FILE: handle_create_new_group,
    labels.OPTION_IMPORT_FILE: handle_import_group,
    labels.OPTION_QUIT_PROGRAM: raise_quit_program,
}

def get_existing_locations_for_tournaments() -> list[str]:
    """
    Liste les sous-dossiers représentant des groupes de joueurs (ex: Nanterre, Paris).
    """
    if not os.path.exists(BASE_PLAYER_DIRECTORY):
        return []

    return sorted([
        name for name in os.listdir(BASE_PLAYER_DIRECTORY)
        if os.path.isdir(os.path.join(BASE_PLAYER_DIRECTORY, name))
    ])


def load_players_for_tournament_group() -> Optional[Tuple[str, str, List[Player]]]:
    """
    Gère la sélection, création ou importation d'un groupe de joueurs.

    Retour :
        - Tuple[str, str, List[Player]] : (ville, chemin du fichier, joueurs)
        - None : si l'utilisateur annule ou sort
    """
    existing_locations = get_existing_locations_for_tournaments()
    choice = prompt_user_for_location_selection(existing_locations)

    # 1. Si l'utilisateur choisit une action spéciale (créer, importer, quitter)
    if choice in MENU_ACTIONS:
        return MENU_ACTIONS[choice]()

    # 2. Sinon, c'est un nom de ville existant → charger le fichier
    city = choice.strip().title()
    filepath = get_player_filepath_for_city(city)

    if not os.path.exists(os.path.dirname(filepath)):
        console.print(f"❌ [red]Le dossier du groupe '{city}' n'existe pas.[/red]")
        return None

    json_files = [
        f for f in os.listdir(os.path.dirname(filepath))
        if f.endswith(".json") and os.path.isfile(os.path.join(os.path.dirname(filepath), f))
    ]

    if not json_files:
        console.print("⚠️ [yellow]Aucun fichier JSON trouvé dans ce groupe.[/yellow]")
        create = questionary.confirm("Souhaitez-vous créer un nouveau fichier 'players.json' vide ?").ask()
        if create:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("[]")
            return city, filepath, []
        return None

    elif len(json_files) > 1:
        selected_file = questionary.select(
            "Plusieurs fichiers trouvés. Lequel souhaitez-vous utiliser ?",
            choices=json_files
        ).ask()
        filepath = os.path.join(os.path.dirname(filepath), selected_file)
    else:
        filepath = os.path.join(os.path.dirname(filepath), json_files[0])

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data:
                console.print("⚠️ [yellow]Le fichier est vide.[/yellow]")
                proceed = questionary.confirm("Continuer avec un fichier vide ?").ask()
                if not proceed:
                    return None
            players = [Player.from_dict(p) for p in data]
    except Exception as e:
        console.print(f"❌ [red]Erreur lors du chargement du fichier : {e}[/red]")
        retry = questionary.confirm("Souhaitez-vous réessayer ou importer un autre fichier ?").ask()
        return load_players_for_tournament_group() if retry else None

    return city, filepath, players
