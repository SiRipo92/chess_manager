from typing import List, Tuple
from chess_manager.models.player import Player


def prompt_new_player() -> Tuple[str, str, str, str]:
    """
    Affiche le formulaire de saisie pour ajouter un nouveau joueur.

    Retour :
        Tuple contenant le nom, prénom, date de naissance et identifiant national du joueur.
    """
    print("\n + Ajout d'un nouveau joueur : ")
    last_name = input("Nom de famille : ")
    first_name = input("Prénom : ")
    birthdate = input("Date de naissance (format : YYYY-MM-DD) : ")
    national_id = input("Identifiant national d’échecs (format : AB12345) : ")
    return last_name, first_name, birthdate, national_id


def confirm_player_added():
    """
    Affiche un message de confirmation après l'ajout d’un joueur.
    """
    print("✅ Le joueur a bien été ajouté à la base de données.\n")


def display_error_message(reason: str):
    """
    Affiche un message d'erreur avec une raison explicite.

    Paramètre :
        reason (str) : Message décrivant la cause de l’échec (ex : format invalide, ID existant).
    """
    print(f"❌ Erreur : {reason}")


def display_all_players(players: List[Player]):
    """
    Affiche la liste des joueurs enregistrés avec leurs informations principales.

    Paramètre :
        players (List[Player]) : Liste d'objets Player à afficher.
    """
    if not players:
        print("Aucun joueur enregistré.")
        return

    print("\n📋 Liste des joueurs enregistrés :\n")
    for idx, player in enumerate(players, 1):
        print(f"{idx}. {player.last_name.upper()}, {player.first_name} (ID: {player.national_id})")
        print(f"   Né(e) le : {player.birthdate} — Âge : {player.age}")
        print(f"   Date d'inscription : {player.date_enrolled}\n")


def prompt_player_national_id(prompt="Entrez l'identifiant national d'échecs du joueur : ") -> str:
    """
    Invite l'utilisateur à saisir un identifiant national.

    Paramètre :
        prompt_text (str) : Texte affiché pour la saisie.
    Retour :
        str : L'identifiant entré.
    """
    return input(prompt).strip().upper()


def prompt_match_result() -> Tuple[str, str]:
    """
    À terme, ce formulaire sera remplacé par une sélection de match
    (suggérée automatiquement par le système via la ronde en cours).

    Retour :
        Tuple contenant le nom du match et le résultat abrégé (V, D, N).
    """
    try:
        match_name = input("Nom du match (ex: 'Ronde 1') : ")
        result = input("Résultat (V = victoire, D = défaite, N = nul) : ")
        return match_name, result
    except (EOFError, KeyboardInterrupt):
        # EOFError : saisie interrompue via redirection ou fin de fichier
        # KeyboardInterrupt : interruption clavier (ex: Ctrl+C)
        print("\n⛔ Entrée interrompue.")
        return "", ""


def prompt_player_name_filter():
    """
    Invite à saisir un nom ou une chaîne de caractères pour filtrer les joueurs.
    """
    return input("Entrez une chaîne pour trouver un joueur par nom de famille : ")


def display_player_stats(stats: str):
    """
    Affiche un résumé statistique formaté d’un joueur.

    Paramètre :
        stats (str) : Chaîne formatée générée par get_stats_summary().
    """
    print(f"\n📊 STATISTIQUES D'UN JOUEUR :\n{stats}")


def show_player_main_menu() -> str:
    """
    Affiche le menu principal de la gestion des joueurs et attend le choix de l'utilisateur.

    Gestion des erreurs :
        Intercepte EOFError ou KeyboardInterrupt pour retourner à un état sûr.
    """
    try:
        print("\n---- MENU DES JOUEURS ----")
        print("1. VOIR TOUS LES JOUEURS INSCRITS")
        print("2. FILTRER / TRIER LES JOUEURS INSCRITS")
        print("3. VOIR LE MENU D'UN JOUEUR INSCRIT")
        print("4. AJOUTER UN JOUEUR INSCRIT")
        print("5. RETOUR AU MENU PRINCIPAL")
        return input("Votre choix : ")
    except (EOFError, KeyboardInterrupt):
        print("\n⛔ Entrée interrompue. Retour au menu principal.")
        return "7"

def show_player_sort_filter_menu() -> str:
    """
    Affiche le menu pour trier ou filtrer les joueurs selon divers critères.

    Retour :
        str : Choix de l’utilisateur.
    """
    try:
        print("\n-- MENU DE FILTRAGE OU TRI DES JOUEURS  --")
        print("1. TRIER LES JOUEURS PAR NOM DE FAMILLE (A-Z)")
        print("2. TRIER LES JOUEURS PAR NOM DE FAMILLE (Z-A)")
        print("3. TRIER LES JOUEURS PAR CLASSEMENT")
        print("4. TROUVER UN JOUEUR PAR IDENTIFIANT NATIONAL D'ÉCHECS")
        print("5. TROUVER UN JOUEUR PAR NOM DE FAMILLE")
        print("6. VOIR LE MENU D'UN JOUEUR INSCRIT (Fiche Joueur)")
        print("7. RETOUR AU MENU DES JOUEURS")
        print("8. QUITTER LE PROGRAMME")
        return input("Votre choix : ")
    except (EOFError, KeyboardInterrupt):
        print("\n⛔ Entrée interrompue. Retour au menu principal.")
        return "8"


def display_player_identity(player: Player):
    """
    Affiche l’identité d’un joueur sélectionné.

    Paramètre :
        player (Player) : Objet représentant le joueur.
    """
    print(f"\n🧾 JOUEUR SÉLECTIONNÉ : {player.first_name} {player.last_name} (ID: {player.national_id})")

    try:
        stats = player.get_stats_summary(None)
        print("\n📊 Statistiques actuelles :")
        for key, value in stats.items():
            print(f"   - {key} : {value}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des statistiques : {e}")


def display_player_action_menu(player: Player) -> str:
    """
    Affiche les actions possibles sur un joueur (fiche individuelle).

    Paramètre :
        player (Player) : Le joueur actuellement sélectionné.

    Retour :
        str : Choix de l’utilisateur.
    """
    try:
        print(f"\n---- FICHE JOUEUR : {player.first_name} {player.last_name} (ID: {player.national_id}) ----")
        print("1. MODIFIER LES INFO D'UN JOUEUR")
        print("2. CONSULTER LES STATISTIQUES D'UN JOUEUR")
        print("3. INSCRIRE À UN TOURNOI ( *** bientôt disponible ***)")
        print("4. RETOUR AU MENU DES JOUEURS")
        print("5. RETOUR AU MENU PRINCIPAL")
        return input("Votre choix : ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n⛔ Entrée interrompue.")
        return "5"
