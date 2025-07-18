from typing import List, Tuple
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from chess_manager.models.player import Player

console = Console()

def prompt_new_player() -> Tuple[str, str, str, str]:
    """
    Affiche le formulaire de saisie pour ajouter un nouveau joueur.

    Retour :
        Tuple contenant le nom, prénom, date de naissance et identifiant national du joueur.
    """
    console.print("\n[bold cyan]+ Ajout d'un nouveau joueur :[/bold cyan]")
    last_name = questionary.text("Nom de famille").ask()
    first_name = questionary.text("Prénom").ask()
    birthdate = questionary.text("Date de naissance (format : YYYY-MM-DD)").ask()
    national_id = questionary.text("Identifiant national d’échecs (format : AB12345)").ask()
    return last_name, first_name, birthdate, national_id


def confirm_player_added():
    """
    Affiche un message de confirmation après l'ajout d’un joueur.
    """
    console.print("✅ [green]Le joueur a bien été ajouté à la base de données.[/green]\n")


def display_error_message(reason: str):
    """
    Affiche un message d'erreur avec une raison explicite.

    Paramètre :
        reason (str) : Message décrivant la cause de l’échec (ex : format invalide, ID existant).
    """
    console.print(f"❌ [red]Erreur : {reason}[/red]")


def display_all_players(players: List[Player]):
    """
    Affiche la liste des joueurs enregistrés avec leurs informations principales.

    Paramètre :
        players (List[Player]) : Liste d'objets Player à afficher.
    """
    if not players:
        console.print("[yellow]Aucun joueur enregistré.[/yellow]")
        return

    table = Table(title="📋 Joueurs enregistrés")
    table.add_column("#", style="cyan")
    table.add_column("Nom complet")
    table.add_column("ID")
    table.add_column("Naissance")
    table.add_column("Âge")
    table.add_column("Inscription")

    for idx, player in enumerate(players, 1):
        table.add_row(
            str(idx),
            f"{player.last_name.upper()}, {player.first_name}",
            player.national_id,
            player.birthdate,
            str(player.age),
            player.date_enrolled
        )
    console.print(table)

def prompt_player_national_id(prompt="Entrez l'identifiant national d'échecs du joueur : ") -> str:
    """
    Invite l'utilisateur à saisir un identifiant national.

    Paramètre :
        prompt_text (str) : Texte affiché pour la saisie.
    Retour :
        str : L'identifiant entré.
    """
    return questionary.text(prompt).ask().strip().upper()

def prompt_match_result() -> Tuple[str, str]:
    """
    À terme, ce formulaire sera remplacé par une sélection de match
    (suggérée automatiquement par le système via la ronde en cours).

    Retour :
        Tuple contenant le nom du match et le résultat abrégé (V, D, N).
    """
    try:
        match_name = questionary.text("Nom du match (ex: 'Ronde 1')").ask()
        result = questionary.select(
            "Résultat",
            choices=["V", "D", "N"]
        ).ask()
        return match_name, result
    except (EOFError, KeyboardInterrupt):
        # EOFError : saisie interrompue via redirection ou fin de fichier
        # KeyboardInterrupt : interruption clavier (ex: Ctrl+C)
        console.print("\n⛔ [red]Entrée interrompue.[/red]")
        return "", ""

def prompt_player_name_filter():
    """
    Invite à saisir un nom ou une chaîne de caractères pour filtrer les joueurs.
    """
    return questionary.text("Entrez une chaîne pour trouver un joueur par nom de famille :").ask()

def display_player_stats(stats: str):
    """
    Affiche un résumé statistique formaté d’un joueur.

    Paramètre :
        stats (str) : Chaîne formatée générée par get_stats_summary().
    """
    console.print(Panel(f"{stats}", title="📊 STATISTIQUES D'UN JOUEUR"))

def show_player_main_menu() -> str:
    """
    Affiche le menu principal de la gestion des joueurs et attend le choix de l'utilisateur.

    Gestion des erreurs :
        Intercepte EOFError ou KeyboardInterrupt pour retourner à un état sûr.
    """
    try:
        return questionary.select(
            "---- MENU DES JOUEURS ----",
            choices=[
                "1. VOIR TOUS LES JOUEURS INSCRITS",
                "2. FILTRER / TRIER LES JOUEURS INSCRITS",
                "3. VOIR LE MENU D'UN JOUEUR INSCRIT",
                "4. AJOUTER UN NOUVEAU JOUEUR",
                "5. RETOUR AU MENU PRINCIPAL"
            ]
        ).ask()[0]  # return the first character (e.g. '1')
    except (EOFError, KeyboardInterrupt):
        console.print("\n⛔ [red]Entrée interrompue. Retour au menu principal.[/red]")
        return "7"

def show_player_sort_filter_menu() -> str:
    """
    Affiche le menu pour trier ou filtrer les joueurs selon divers critères.

    Retour :
        str : Choix de l’utilisateur.
    """
    try:
        return questionary.select(
            "-- MENU DE FILTRAGE OU TRI DES JOUEURS  --",
            choices=[
                "1. TRIER LES JOUEURS PAR NOM DE FAMILLE (A-Z)",
                "2. TRIER LES JOUEURS PAR NOM DE FAMILLE (Z-A)",
                "3. TRIER LES JOUEURS PAR CLASSEMENT",
                "4. TROUVER UN JOUEUR PAR IDENTIFIANT NATIONAL D'ÉCHECS",
                "5. TROUVER UN JOUEUR PAR NOM DE FAMILLE",
                "6. VOIR LE MENU D'UN JOUEUR INSCRIT (Fiche Joueur)",
                "7. RETOUR AU MENU DES JOUEURS",
                "8. QUITTER LE PROGRAMME"
            ]
        ).ask()[0]
    except (EOFError, KeyboardInterrupt):
        console.print("\n⛔ [red]Entrée interrompue. Retour au menu principal.[/red]")
        return "8"

def display_player_identity(player: Player):
    """
    Affiche l’identité d’un joueur sélectionné.

    Paramètre :
        player (Player) : Objet représentant le joueur.
    """
    console.print(f"\n🧾 [bold]{player.first_name} {player.last_name}[/bold] (ID: {player.national_id})")

    try:
        stats = player.get_stats_summary(None)
        console.print("\n📊 [bold]Statistiques actuelles :[/bold]")
        for key, value in stats.items():
            console.print(f"   - {key} : {value}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des statistiques : {e}")

def display_stats_summary(stats: dict):
    """
    Affiche proprement les statistiques retournées par get_stats_summary().
    """
    table = Table(title="📊 Statistiques du joueur")
    table.add_column("Statut")
    table.add_column("Valeur")
    for key, value in stats.items():
        table.add_row(key, str(value))
    console.print(table)

def display_user_action_menu_for_player_page(player: Player) -> str:
    """
    Affiche les actions possibles sur un joueur (fiche individuelle).

    Paramètre :
        player (Player) : Le joueur actuellement sélectionné.

    Retour :
        str : Choix de l’utilisateur.
    """
    try:
        return questionary.select(
            f"---- FICHE JOUEUR : {player.first_name} {player.last_name} (ID: {player.national_id}) ----",
            choices=[
                "1. MODIFIER LES INFO D'UN JOUEUR",
                "2. CONSULTER LES STATISTIQUES D'UN JOUEUR",
                "3. RETOUR AU MENU DES JOUEURS",
                "4. RETOUR AU MENU PRINCIPAL"
            ]
        ).ask()[0]
    except (EOFError, KeyboardInterrupt):
        console.print("\n⛔ [red]Entrée interrompue.[/red]")
        return "5"
