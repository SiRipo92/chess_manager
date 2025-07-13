from typing import List, Tuple
from chess_manager.models.player import Player


def prompt_new_player() -> Tuple[str, str, str, str]:
    """
    Affiche le formulaire de saisie pour ajouter un joueur.

    Retour :
        Tuple[str, str, str, str] : nom, prénom, date de naissance, ID.
    """
    print("\n + Ajout d'un nouveau joueur : ")
    last_name = input("Nom de famille : ")
    first_name = input("Prénom : ")
    birthdate = input("Date de naissance ( format : YYYY-MM-DD ) : ")
    national_id = input("Identifiant national d’échecs ( format : AB12345 ) : ")
    return last_name, first_name, birthdate, national_id


def confirm_player_added():
    """
    Affiche un message de confirmation après ajout d’un joueur.
    """
    print("✅ Le joueur a bien été ajouté à la base de données.\n")


def display_error_message(reason: str):
    """
    Affiche un message d'erreur avec la raison fournie.

    Paramètre :
        reason (str) : La raison de l'échec (format invalide, ID existant, etc.).
    """
    print(f"❌ Erreur : {reason}")


def display_all_players(players: List[Player]):
    """
    Affiche tous les joueurs enregistrés avec leurs informations principales.

    Paramètre :
        players (List[Player]) : Liste des joueurs à afficher.
    """
    if not players:
        print("Aucun joueur enregistré.")
        return

    print("\n📋 Liste des joueurs enregistrés :\n")
    for idx, player in enumerate(players, 1):
        print(f"{idx}. {player.last_name.upper()}, {player.first_name} (ID: {player.national_id})")
        print(f"   Né(e) le : {player.birthdate} — Âge : {player.age}")
        print(f"   Date d'inscription : {player.date_enrolled}\n")


def prompt_sort_or_filter():
    """
    Propose à l’utilisateur de trier ou filtrer la liste des joueurs.

    Retour :
        str : Choix de l’action ("Trier A-Z", "Filtrer par ID", etc.).
    """
    print("\n🔎 Options de tri / filtrage :")
    print("1. Trier les joueurs par nom (A-Z)")
    print("2. Filtrer par identifiant")
    print("3. Filtrer par nom de famille")
    return input("Votre choix : ")


def prompt_id_filter():
    """
    Demande à l’utilisateur une chaîne pour filtrer les identifiants.

    Retour :
        str : Partie d’ID à rechercher.
    """
    return input("Entrez une chaîne pour filtrer les identifiants : ")


def prompt_player_id_for_stats() -> str:
    """
    Demande l’identifiant d’un joueur pour consulter ses statistiques.

    Retour :
        str : ID du joueur à consulter.
    """
    return input("Entrez l’identifiant du joueur pour consulter ses statistiques : ")


def display_player_stats(stats: str):
    """
    Affiche les statistiques détaillées d’un joueur.

    Paramètre :
        stats (str) : Chaîne descriptive des performances.
    """
    print(f"\n📊 Statistiques du joueur :\n{stats}")
