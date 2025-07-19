from rich.console import Console
import questionary

console = Console()


def display_main_menu() -> str:
    """
    Affiche le menu principal de l'application en stylisant avec Rich et Questionary.
    """
    console.print("\n[bold cyan]---- MENU PRINCIPAL ----[/bold cyan]")
    try:
        console.print("Utilisez les flèches ↑ ↓ et [bold]Entrée[/bold] pour faire votre choix.", style="yellow")
        return questionary.select(
            "Choisissez une option :",
            choices=[
                "1. GÉRER LES JOUEURS",
                "2. GÉRER LES TOURNOIS ( *** bientôt disponible ***)",
                "3. QUITTER"
            ]
        ).ask()[0]  # renvoie le chiffre correspondant comme string
    except (EOFError, KeyboardInterrupt):
        console.print("\n⛔ [red]Entrée interrompue. Fermeture du programme.[/red]")
        return "3"
