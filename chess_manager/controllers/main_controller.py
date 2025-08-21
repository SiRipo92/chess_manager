import os
import random
from datetime import datetime
from typing import Optional, Union

import questionary
from rich.console import Console
from rich.table import Table

from chess_manager.views import player_views
from chess_manager.controllers.player_controller import PlayerController
from chess_manager.models.tournament_repository import TournamentRepository
from chess_manager.utils.tournament_utils import generate_tournament_name, browse_for_file
from chess_manager.controllers.tournament_controller import (
    launch_first_round_flow,
    run_rounds_until_done,
)

console = Console()


# ----------------------
# Helpers
# ----------------------
def _select_existing_tournament(repo: TournamentRepository) -> Optional[dict]:
    """Allows user to select from an existing tournament
        -- can be built out more later to view, sort, filter and modify tournament objects
    """
    raw_list = repo.load_all_tournaments()
    candidates = []
    for t in raw_list:
        if isinstance(t, dict):
            candidates.append(t)
        else:
            try:
                candidates.append(t.to_dict())  # type: ignore
            except Exception:
                continue
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    choices = [
        {"name": t.get("name", f"Untitled_{i+1}"), "value": t.get("name")}
        for i, t in enumerate(candidates)
    ]
    selected_name = questionary.select("Sélectionnez un tournoi à gérer :", choices=choices).ask()
    if not selected_name:
        return None
    for t in candidates:
        if t.get("name") == selected_name:
            return t
    return None


def _extract_players_from_tournament(tournament: Union[dict, object], controller: PlayerController):
    """Reviews tournament repository to extract a list of players if no players.json file is provided"""
    from chess_manager.models.player_models import Player

    collected = []
    if isinstance(tournament, dict):
        raw_players = tournament.get("players", [])
    else:
        raw_players = getattr(tournament, "players", [])

    for p in raw_players:
        if isinstance(p, dict):
            try:
                collected.append(Player.from_dict(p))
            except Exception:
                continue
        elif isinstance(p, str):
            candidate = controller.get_player_by_id(p)
            if candidate:
                collected.append(candidate)
        elif isinstance(p, Player):
            collected.append(p)
    unique = {p.national_id: p for p in collected}
    return list(unique.values())


# ----------------------
# Tournament operations
# ----------------------
def _launch_tournament_flow(
        repo: TournamentRepository, tournament: dict, controller: PlayerController
) -> None:
    try:
        # 2) build model from dict + confirm + create pairings
        model = launch_first_round_flow(tournament)
    except RuntimeError:
        console.print("Lancement annulé.")
        return
    except Exception as e:
        player_views.display_error_message(str(e))
        return

    # 3) persist immediately (round created + exempts scored)
    repo.save_tournament(model.to_dict())

    # 4) run scoring loop for all rounds
    run_rounds_until_done(model)

    # 5) persist after scoring changes
    repo.save_tournament(model.to_dict())

    # TODO later: show final ranking / winner, etc.


def _manage_tournament_player_menu(
    repo: TournamentRepository, tournament: dict, controller: PlayerController
) -> None:
    """This controls the menu options to either add a player manually or import a players.json
        in order to populate a tournament with players, add additional players, or change the current player list
    """
    from chess_manager.models.player_models import Player

    while True:
        players_in_tourn = _extract_players_from_tournament(tournament, controller)
        console.print("\n[bold]Joueurs du tournoi actuel :[/bold]")
        player_views.display_all_players(players_in_tourn)

        choices = [
            {"name": "1. Ajouter un joueur manuellement", "value": "add"},
            {"name": "2. Importer un fichier players.json", "value": "import"},
        ]

        if len(players_in_tourn) >= 8:
            choices.append({"name": "3. Lancer le tournoi", "value": "launch"})
        else:
            missing = 8 - len(players_in_tourn)
            choices.append(
                {
                    "name": f"3. Lancer le tournoi (requiert {missing} joueur(s) de plus)",
                    "value": "launch_disabled",
                }
            )

        choices.append({"name": "4. Quitter", "value": "quit"})

        action = questionary.select("Que souhaitez-vous faire ?", choices=choices).ask()

        if action == "add":
            result = player_views.prompt_new_player_inputs_with_review()
            if result is None:
                continue
            last_name, first_name, birthdate, national_id = result
            success, message = controller.add_new_player(last_name, first_name, birthdate, national_id)
            if not success:
                player_views.display_error_message(message or "Échec de création du joueur.")
                continue
            new_player = controller.get_player_by_id(national_id)
            if not new_player:
                player_views.display_error_message("Impossible de retrouver le joueur après création.")
                continue
            existing_ids = {p.national_id for p in players_in_tourn}
            if new_player.national_id not in existing_ids:
                tournament_players = tournament.get("players", [])
                tournament_players.append(new_player.to_dict())
                tournament["players"] = tournament_players
                repo.save_tournament(tournament)
                console.print(f"✅ Joueur {new_player.first_name} {new_player.last_name} ajouté au tournoi.")
            else:
                console.print(f"[yellow]Le joueur {new_player.national_id} est déjà dans le tournoi.[/yellow]")

        elif action == "import":
            # smarter path prompt with fallback
            path = None
            try:
                path = questionary.path(
                    "Chemin vers un fichier players.json à importer :",
                    default=os.path.expanduser("~"),
                ).ask()
            except TypeError:
                # older questionary does not support some args; ignore and fallback
                path = None
            if not path:
                path = browse_for_file(start_dir=os.path.expanduser("~"), file_glob="players.json")
            if not path:
                console.print("[yellow]Import annulé.[/yellow]")
                continue
            if not os.path.isfile(path):
                player_views.display_error_message("Le fichier sélectionné n'existe pas ou n'est pas un fichier.")
                continue
            if os.path.basename(path).lower() != "players.json":
                confirm = questionary.confirm(
                    f"Le fichier sélectionné s'appelle '{os.path.basename(path)}'. Continuer quand même ?"
                ).ask()
                if not confirm:
                    continue
            try:
                imported_players = Player.load_all_players(path)
            except Exception as e:
                player_views.display_error_message(f"Erreur pendant l'import : {e}")
                continue
            if not imported_players:
                player_views.display_error_message("Aucun joueur valide dans le fichier.")
                continue
            global_players = controller.load_players()
            global_ids = {p.national_id for p in global_players}
            tournament_player_ids = {p.national_id for p in players_in_tourn}
            added = 0
            for p in imported_players:
                if p.national_id not in global_ids:
                    controller._save_player(p)
                    global_ids.add(p.national_id)
                if p.national_id not in tournament_player_ids:
                    tournament_players = tournament.get("players", [])
                    tournament_players.append(p.to_dict())
                    tournament["players"] = tournament_players
                    tournament_player_ids.add(p.national_id)
                    added += 1
            repo.save_tournament(tournament)
            console.print(f"✅ {added} joueur(s) ajoutés au tournoi via import.")
            if len(tournament_player_ids) < 8:
                console.print(f"[yellow]Il manque {8 - len(tournament_player_ids)} joueur(s) pour démarrer.[/yellow]")

        elif action == "launch":
            _launch_tournament_flow(repo, tournament, controller)

        elif action == "launch_disabled":
            player_views.display_error_message("Impossible de lancer : il faut au moins 8 joueurs.")

        elif action == "quit":
            console.print("✅ Sauvegarde en cours et sortie du menu tournoi...")
            break

        else:
            player_views.display_error_message("Option invalide.")


# ----------------------
# Entry point (new simplified flow)
# ----------------------
def handle_main_menu(controller: PlayerController) -> None:
    """Entry point menu """
    tournaments_repo = TournamentRepository()

    while True:
        # Show global players
        global_players = controller.load_players()
        console.print("\n" + "-" * 60)
        console.print("[bold cyan]Joueurs globaux disponibles[/bold cyan]")
        if global_players:
            player_views.display_all_players(global_players)
        else:
            console.print("[yellow]Aucun joueur global trouvé. Ajoutez-en ou importez un fichier.[/yellow]")

        # Build main choices
        choices = []
        if len(global_players) >= 8:
            choices.append({"name": "1. Lancer un nouveau tournoi avec les joueurs listés", "value": "launch_with_listed"})
        choices.extend([
            {"name": "2. Créer un nouveau tournoi vide et ajouter des joueurs", "value": "create_empty_tournament"},
            {"name": "3. Importer un fichier players.json pour peupler un nouveau tournoi", "value": "import_and_create"},
            {"name": "4. Gérer les joueurs globaux (ajouter / modifier)", "value": "manage_global_players"},
            {"name": "5. Sélectionner un tournoi existant", "value": "select_existing"},
            {"name": "6. Quitter", "value": "quit"},
        ])

        action = questionary.select("Que souhaitez-vous faire ?", choices=choices).ask()

        if action == "launch_with_listed":
            location = questionary.text("Lieu du tournoi :").ask()
            if not location or not location.strip():
                player_views.display_error_message("Lieu requis pour nom de tournoi.")
                continue
            existing = tournaments_repo.load_all_tournaments()
            name = generate_tournament_name(location, existing)
            meta = {
                "name": name,
                "location": location.strip(),
                "players": [p.to_dict() for p in global_players],
                "created_at": datetime.now().isoformat(),
            }
            tournaments_repo.add_tournament(meta)
            console.print(f"✅ Tournoi '{name}' créé avec les joueurs listés et prêt à être géré.")
            current_tournament = tournaments_repo.get_tournament_by_name(name)
            if current_tournament:
                _manage_tournament_player_menu(tournaments_repo, current_tournament, controller)

        elif action == "create_empty_tournament":
            # ask for location and create empty tournament
            location = questionary.text("Lieu du tournoi :").ask()
            if not location or not location.strip():
                player_views.display_error_message("Lieu requis pour nom de tournoi.")
                continue
            existing = tournaments_repo.load_all_tournaments()
            name = generate_tournament_name(location, existing)
            meta = {
                "name": name,
                "location": location.strip(),
                "players": [],
                "created_at": datetime.now().isoformat(),
            }
            tournaments_repo.add_tournament(meta)
            console.print(f"✅ Tournoi '{name}' vide créé et prêt à être rempli.")
            current_tournament = tournaments_repo.get_tournament_by_name(name)
            if current_tournament:
                _manage_tournament_player_menu(tournaments_repo, current_tournament, controller)

        elif action == "import_and_create":
            # import a players.json and create tournament seeded with its players
            # prompt file
            path = questionary.path(
                "Chemin vers un fichier players.json à importer :",
                only_files=True,
                default=os.path.expanduser("~"),
            ).ask()
            if not path:
                path = browse_for_file(start_dir=os.path.expanduser("~"), file_glob="players.json")
            if not path:
                console.print("[yellow]Import annulé.[/yellow]")
                continue
            if not os.path.exists(path):
                player_views.display_error_message("Le fichier sélectionné n'existe pas.")
                continue
            from chess_manager.models.player_models import Player

            try:
                imported_players = Player.load_all_players(path)
            except Exception as e:
                player_views.display_error_message(f"Erreur pendant l'import : {e}")
                continue
            if not imported_players:
                player_views.display_error_message("Le fichier ne contient aucun joueur valide.")
                continue
            location = questionary.text("Lieu du tournoi :").ask()
            if not location or not location.strip():
                player_views.display_error_message("Lieu requis pour nom de tournoi.")
                continue
            existing = tournaments_repo.load_all_tournaments()
            name = generate_tournament_name(location, existing)
            meta = {
                "name": name,
                "location": location.strip(),
                "players": [p.to_dict() for p in imported_players],
                "created_at": datetime.now().isoformat(),
            }
            tournaments_repo.add_tournament(meta)
            console.print(f"✅ Tournoi '{name}' créé avec {len(imported_players)} joueur(s) importés.")
            current_tournament = tournaments_repo.get_tournament_by_name(name)
            if current_tournament:
                _manage_tournament_player_menu(tournaments_repo, current_tournament, controller)

        elif action == "manage_global_players":
            controller.manage_players()

        elif action == "select_existing":
            selected = _select_existing_tournament(tournaments_repo)
            if not selected:
                continue
            # if empty, offer to import global players
            existing_players = _extract_players_from_tournament(selected, controller)
            if not existing_players and global_players:
                should_import = questionary.confirm(
                    f"Le tournoi '{selected.get('name')}' est vide. Importer les {len(global_players)} joueur(s) globaux ?"
                ).ask()
                if should_import:
                    if isinstance(selected, dict):
                        selected["players"] = [p.to_dict() for p in global_players]
                    else:
                        try:
                            setattr(selected, "players", [p.to_dict() for p in global_players])  # type: ignore
                        except Exception:
                            console.print("[red]Impossible d'injecter les joueurs globaux.[/red]")
                    tournaments_repo.save_tournament(selected)
            current_tournament = selected
            if current_tournament:
                _manage_tournament_player_menu(tournaments_repo, current_tournament, controller)

        elif action == "quit":
            console.print("\n👋 Au revoir ! Sauvegarde en cours...")
            break

        else:
            player_views.display_error_message("Option invalide.")
