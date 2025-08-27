import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from chess_manager.controllers.player_controller import PlayerController
from chess_manager.controllers.main_controller import handle_main_menu


def main() -> None:
    """
    Point d'entrée principal de l'application. Initialise le contrôleur principal et démarre le menu.
    """
    console = Console()

    # Header/banner
    title = "[bold cyan]♟️ Chess Tournament Manager (v0.1)[/bold cyan]"
    subtitle = "[cyan]Gestion de tournois et de joueurs depuis la ligne de commande[/cyan]"
    timestamp = datetime.now().strftime("%Y-%m-%d")
    banner_content = f"{title}\n{subtitle}\n[grey58]{timestamp}[/grey58]"
    panel = Panel(
        Align.center(banner_content, vertical="middle"),
        border_style="cyan",
        padding=(1, 4),
        width=72,
        subtitle="Bienvenue",
    )
    console.print("\n")
    console.print(panel)

    # Prépare les répertoires
    os.makedirs("data/players", exist_ok=True)
    os.makedirs("data/tournaments", exist_ok=True)

    player_controller = PlayerController(file_path="data/players/players.json")

    handle_main_menu(player_controller)


if __name__ == "__main__":
    main()
