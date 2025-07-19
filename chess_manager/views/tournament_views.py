from questionary import text, select
from chess_manager.utils.tournament_validator import (
    is_valid_location,
    is_valid_date,
    is_valid_number_of_rounds,
)

def prompt_tournament_info() -> dict:
    """
    Collecte les informations de base pour créer un tournoi via CLI.
    Retour : dict avec les champs : location, start_date, end_date, rounds, description
    """
    while True:
        location = text("Lieu du tournoi :").ask()
        if is_valid_location(location):
            break
        print("❌ Lieu invalide.")

    while True:
        start_date = text("Date de début (YYYY-MM-DD) :").ask()
        if is_valid_date(start_date):
            break
        print("❌ Date invalide.")

    while True:
        end_date = text("Date de fin (YYYY-MM-DD) :").ask()
        if is_valid_date(end_date):
            break
        print("❌ Date invalide.")

    while True:
        rounds = text("Nombre de tours (par défaut : 4) :").ask()
        if is_valid_number_of_rounds(rounds):
            break
        print("❌ Nombre de tours invalide.")

    description = text("Commentaires du directeur du tournoi :").ask()

    return {
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "rounds": int(rounds),
        "description": description,
    }

def show_tournament_main_menu() -> str:
    """
    Affiche le menu principal de gestion des tournois.
    Retourne le choix sélectionné.
    """
    return select(
        "=== Menu Tournois ===",
        choices=[
            "1. Lancer un tournoi (nouveau)",
            "2. Voir l’état d’un tournoi",
            "3. Conclure un tournoi (sauvegarde)",
            "4. Quitter"
        ]
    ).ask()