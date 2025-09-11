from __future__ import annotations
from datetime import datetime
from typing import Optional, Union, List
import questionary
from rich.console import Console
from chess_manager.views import player_views, round_views
from chess_manager.models.player_models import Player
from chess_manager.controllers.player_controller import PlayerController
from chess_manager.models.tournament_repository import TournamentRepository
from chess_manager.utils.tournament_utils import generate_tournament_name, build_player_tournament_index
from chess_manager.controllers.tournament_controller import (
    launch_first_round_flow,
    run_rounds_until_done,
    manage_tournament_description,
)

console = Console()


# ----------------------
# Helpers
# ----------------------

def _prompt_location() -> Optional[str]:
    """Helper function to obtain the location of the tournament to be turned into a slug for file naming"""
    loc = questionary.text("Lieu du tournoi :").ask()
    if not loc or not loc.strip():
        player_views.display_error_message("Lieu requis pour nom de tournoi.")
        return None
    return loc.strip()


def _create_and_open_tournament(
    repo: TournamentRepository,
    location: str,
    players: List[Player],
    controller: PlayerController,
    success_message_template: str,
) -> None:
    """Creates new tournament object in tournament repo, obtains location and players in order to open and prepare a
    tournament.
    """
    existing = repo.load_all_tournaments()
    name = generate_tournament_name(location, existing)
    meta = {
        "name": name,
        "location": location,
        "players": [p.to_dict() for p in players],
        "created_at": datetime.now().isoformat(),
    }
    repo.add_tournament(meta)

    # Interpolate both {name} and {count} when present in the template
    console.print(success_message_template.format(name=name, count=len(players)))

    current = repo.get_tournament_by_name(name)
    if current:
        current = _as_dict(current)
        _manage_tournament_player_menu(repo, current, controller)


def _tournament_progress_percent(t: dict | object) -> int:
    """Return 0/25/50/75/100 based on closed rounds vs number_rounds."""
    if _is_finished(t):
        return 100
    if not _is_started(t):
        return 0

    rounds = getattr(t, "rounds", None)
    if rounds is None and isinstance(t, dict):
        rounds = t.get("rounds")

    total = getattr(t, "number_rounds", None)
    if total is None and isinstance(t, dict):
        total = t.get("number_rounds", 0)
    if not isinstance(total, int) or total <= 0:
        total = len(rounds) if isinstance(rounds, list) else 0
    if total <= 0:
        return 0

    closed = 0
    if isinstance(rounds, list):
        for r in rounds:
            if isinstance(r, dict):
                if r.get("end_time"):
                    closed += 1
                    continue
                matches = r.get("matches", [])
                if matches and all(
                    (m.get("player2") is None) or
                    (m.get("result1") is not None or m.get("result2") is not None) or
                    (m.get("score1") is not None and m.get("score2") is not None)
                    for m in matches
                ):
                    closed += 1
            else:
                if getattr(r, "end_time", None):
                    closed += 1
                    continue
                matches = getattr(r, "matches", []) or []
                if matches and all(
                    (getattr(m, "player2", None) is None) or
                    (getattr(m, "result1", None) is not None or getattr(m, "result2", None) is not None) or
                    (getattr(m, "score1", None) is not None and getattr(m, "score2", None) is not None)
                    for m in matches
                ):
                    closed += 1

    pct = int(round((closed / float(total)) * 100))
    if total == 4:
        pct = {0: 0, 1: 25, 2: 50, 3: 75, 4: 100}.get(closed, pct)
    return max(0, min(100, pct))


def _status_label_plain(t: dict | object) -> str:
    """Plain text: 'Terminé', 'Non démarré', or 'En cours {pct}%'."""
    if _is_finished(t):
        return "Terminé"
    # _tournament_progress_percent must already exist
    pct = _tournament_progress_percent(t)
    if pct <= 0:
        return "Non démarré"
    return f"En cours {pct}%"


def _select_existing_tournament(repo: TournamentRepository) -> Optional[dict]:
    """Allows user to select from an existing tournament
        -- can be built out more later to view, sort, filter and modify tournament objects
    """
    raw_list = repo.load_all_tournaments()
    candidates = []
    for t in raw_list:
        if isinstance(t, dict):
            candidates.append(t)
        elif hasattr(t, "to_dict") and callable(getattr(t, "to_dict")):
            # Only catch likely/known issues; avoid a broad blanket.
            try:
                candidates.append(t.to_dict())  # type: ignore[call-arg]
            except (TypeError, ValueError, AttributeError):
                continue
        # if neither dict nor model-like, skip silently

    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    # Show status next to each tournament name (colored if possible).
    choices = []
    for i, t in enumerate(candidates):
        name = t.get("name", f"Sans titre_{i + 1}")
        badge = _status_label_plain(t)  # plain text only
        choices.append({"name": f"{name}  —  {badge}", "value": t.get("name")})

    selected_name = questionary.select("Sélectionnez un tournoi à gérer :", choices=choices).ask()
    if not selected_name:
        return None
    for t in candidates:
        if t.get("name") == selected_name:
            return t
    return None


def _extract_players_from_tournament(tournament: Union[dict, object], controller: PlayerController):
    """
    Rebuild a list of Player objects from a stored tournament, whether
    it is a dict or an object. Duplicates (by national_id) are removed.
    """

    collected: List[Player] = []
    if isinstance(tournament, dict):
        raw_players = tournament.get("players", [])
    else:
        raw_players = getattr(tournament, "players", [])

    for p in raw_players:
        if isinstance(p, dict):
            try:
                collected.append(Player.from_dict(p))
            except (KeyError, TypeError, ValueError):
                continue
        elif isinstance(p, str):
            candidate = controller.get_player_by_id(p)
            if candidate:
                collected.append(candidate)
        elif isinstance(p, Player):
            collected.append(p)
    unique = {p.national_id: p for p in collected}
    return list(unique.values())


def _is_started(t: dict | object) -> bool:
    """
    Return True if a tournament has started (has started_at or a positive
    current_round_number), False otherwise.

    Works for both raw dict tournaments and model objects.
    """
    if isinstance(t, dict):
        return bool(t.get("started_at")) or bool(t.get("current_round_number", 0))
    return bool(getattr(t, "started_at", "")) or getattr(t, "current_round_number", 0) > 0


def _is_finished(t: dict | object) -> bool:
    """
    Return True if a tournament is marked finished (has finished_at or
    status == 'Terminé'), False otherwise.

    Works for both raw dict tournaments and model objects.
    """
    if isinstance(t, dict):
        return bool(t.get("finished_at")) or (t.get("status") == "Terminé")
    return bool(getattr(t, "finished_at", "")) or getattr(t, "status", "") == "Terminé"


def _as_model(t: Union[dict, object]):
    """
    Convert a raw dict or a model-like object to a Tournament model instance.
    Leaves model as-is if already a Tournament. Minimal conversion for dict.
    """
    from chess_manager.models.tournament_models import Tournament

    if isinstance(t, dict):
        return Tournament.from_dict(t)
    # If it already quacks like a Tournament (has to_dict), assume it's fine
    if hasattr(t, "to_dict"):
        return t
    # Fallback: try to build from whatever attributes exist
    return Tournament.from_dict(getattr(t, "__dict__", {}))


def _as_dict(t: Union[dict, object]) -> dict:
    """
    Normalize a tournament (dict or model) to a dict for persistence.
    """
    if isinstance(t, dict):
        return t
    if hasattr(t, "to_dict"):
        return t.to_dict()  # type: ignore[attr-defined]
    return getattr(t, "__dict__", {})

# ----------------------
# Tournament operations
# ----------------------


def _launch_tournament_flow(
        repo: TournamentRepository, tournament: dict
) -> None:
    """
    Build a Tournament model from a dict, confirm, create pairings,
    then run all rounds (with persistence after each step).
    """
    try:
        # Build model from dict + confirm + create pairings
        model = launch_first_round_flow(tournament)
    except RuntimeError:
        console.print("Lancement annulé.")
        return
    except Exception as e:
        player_views.display_error_message(str(e))
        return

    # Persist immediately (round created + exempts scored)
    repo.save_tournament(model.to_dict())

    # Run scoring loop for all rounds (resumable if user quits mid-way)
    run_rounds_until_done(model, repo=repo)

    # Persist final state
    repo.save_tournament(model.to_dict())


def _resume_tournament_flow(
        repo: TournamentRepository, tournament: Union[dict, object]
) -> None:
    """
    Resume an in-progress tournament (not finished). If the last round was
    partially entered, continue; otherwise start the next round.
    """
    model = _as_model(tournament)
    run_rounds_until_done(model, repo=repo)
    repo.save_tournament(model.to_dict())


def _show_summary(tournament: Union[dict, object]) -> None:
    """
    Display the final tournament summary (supports co-winners, as implemented
    in round_views.display_final_summary).
    """
    model = _as_model(tournament)
    round_views.display_final_summary(model)


def _pick_players_from_global(global_players):
    """
    Multi-select from global players, returns a list of selected Player objects.
    Ensures at least 8 are picked.
    """
    choices = [
        questionary.Choice(
            title=f"{p.last_name.upper()}, {p.first_name} ({p.national_id})",
            value=p.national_id,
        )
        for p in global_players
    ]
    picked_ids = questionary.checkbox(
        "Sélectionnez au moins 8 joueurs :", choices=choices
    ).ask()

    if not picked_ids or len(picked_ids) < 8:
        player_views.display_error_message("Vous devez sélectionner au moins 8 joueurs.")
        return None

    idset = set(picked_ids)
    return [p for p in global_players if p.national_id in idset]


# ---------------------------------------------------------------------
# Menu for managing one tournament
# ---------------------------------------------------------------------
def _manage_tournament_player_menu(
    repo: TournamentRepository, tournament: dict, controller: PlayerController
) -> None:
    """
    Menu to add players (only before start), launch/resume/summary depending on status, or quit.
    """
    while True:
        # Refresh from repo every loop so we never use a stale dict
        name = tournament.get("name", "")
        if name:
            fresh = repo.get_tournament_by_name(name)
            if fresh:
                tournament = _as_dict(fresh)

        players_in_tournament = _extract_players_from_tournament(tournament, controller)
        current_stats = build_player_tournament_index([tournament])

        console.print("\n[bold]Joueurs du tournoi actuel :[/bold]")
        player_views.display_all_players(
            players_in_tournament,
            scope="tournament",
            stats_index=current_stats
        )
        console.print()

        # --- state flags
        started = _is_started(tournament)
        finished = _is_finished(tournament)
        enough = len(players_in_tournament) >= 8

        # Unified status line (always shown)
        console.print(f"[dim]Statut : {_status_label_plain(tournament)}[/dim]")

        # --- build choices by status (no extra status prints below)
        if not started and not finished:
            choices = [{"name": "1. Ajouter un joueur manuellement", "value": "add"}]
            if enough:
                choices.append({"name": "2. Lancer le tournoi", "value": "launch"})
            else:
                missing = 8 - len(players_in_tournament)
                choices.append({
                    "name": f"2. Lancer le tournoi (requiert {missing} joueur(s) de plus)",
                    "value": "launch_disabled",
                })
            choices.append({"name": "3. Voir / Modifier la description", "value": "description"})  # ← add
            choices.append({"name": "4. Quitter", "value": "quit"})

        elif started and not finished:
            # In progress: resume only; no adding players
            choices = [
                {"name": "1. Reprendre la saisie / continuer", "value": "resume"},
                {"name": "2. Voir / Modifier la description", "value": "description"},
                {"name": "3. Quitter", "value": "quit"},
            ]

        else:
            # Finished
            choices = [
                {"name": "1. Voir le récapitulatif", "value": "summary"},
                {"name": "2. Voir / Modifier la description", "value": "description"},  # ← add
                {"name": "3. Quitter", "value": "quit"},
            ]

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

            existing_ids = {p.national_id for p in players_in_tournament}
            if new_player.national_id not in existing_ids:
                tournament_players = tournament.get("players", [])
                tournament_players.append(new_player.to_dict())
                tournament["players"] = tournament_players
                repo.save_tournament(tournament)
                console.print("✅ Joueur {} {} ajouté au tournoi.".format(new_player.first_name, new_player.last_name))
            else:
                console.print("[yellow]Le joueur {} est déjà dans le tournoi.[/yellow]".format(new_player.national_id))

        elif action == "launch":
            _launch_tournament_flow(repo, tournament)
            # reload the latest snapshot
            fresh = repo.get_tournament_by_name(tournament.get("name", ""))
            if fresh:
                tournament = _as_dict(fresh)

        elif action == "launch_disabled":
            player_views.display_error_message("Impossible de lancer : il faut au moins 8 joueurs.")

        elif action == "resume":
            _resume_tournament_flow(repo, tournament)
            fresh = repo.get_tournament_by_name(tournament.get("name", ""))
            if fresh:
                tournament = _as_dict(fresh)

        elif action == "summary":
            _show_summary(tournament)
            fresh = repo.get_tournament_by_name(tournament.get("name", ""))
            if fresh:
                tournament = _as_dict(fresh)

        elif action == "description":
            # Load latest snapshot description, convert to model for setters/getters
            fresh = repo.get_tournament_by_name(tournament.get("name", "")) if tournament.get("name") else None
            model = _as_model(fresh if fresh else tournament)

            try:
                manage_tournament_description(model, repo=repo)
            except KeyboardInterrupt:
                pass
            except Exception as e:
                player_views.display_error_message(f"Erreur lors de l'édition de la description : {e}")

            # Refresh local dict after possible edits
            fresh = repo.get_tournament_by_name(tournament.get("name", ""))
            if fresh:
                tournament = _as_dict(fresh)

        elif action == "quit":
            console.print("✅ Sauvegarde en cours et sortie du menu tournoi...")
            break

        else:
            player_views.display_error_message("Option invalide.")


# ----------------------
# Entry point (new simplified flow)
# ----------------------


def handle_main_menu(controller: PlayerController) -> None:
    """
    Top-level main menu:
      - Launch a new tournament with listed players
      - Create a tournament by selecting players
      - Create an empty tournament
      - Manage global players
      - Select an existing tournament (resume/summary)
      - Quit
    """
    tournaments_repo = TournamentRepository()

    while True:
        # Show global players + live stats from all tournaments
        global_players = controller.load_players()

        all_tournaments = tournaments_repo.load_all_tournaments()
        stats_index = build_player_tournament_index(all_tournaments)

        console.print("\n" + "-" * 60)
        console.print("[bold cyan]Joueurs globaux disponibles[/bold cyan]")
        if global_players:
            player_views.display_all_players(
                global_players,
                scope="global",
                stats_index=stats_index
            )
            console.print()  # newline so the Questionary prompt appears below the table cleanly
        else:
            console.print("[yellow]Aucun joueur global trouvé. Ajoutez-en ou importez un fichier.[/yellow]")

        # Build main choices
        choices = []
        if len(global_players) >= 8:
            choices.append(
                {
                    "name": "1. Lancer un nouveau tournoi avec les joueurs listés",
                    "value": "launch_with_listed",
                }
            )
        choices.append(
            {
                "name": "2. Créer un tournoi en sélectionnant des joueurs",
                "value": "select_players",
            }
        )
        choices.extend(
            [
                {
                    "name": "3. Créer un nouveau tournoi vide et ajouter des joueurs",
                    "value": "create_empty_tournament",
                },
                {
                    "name": "4. Gérer les joueurs globaux (ajouter / modifier)",
                    "value": "manage_global_players",
                },
                {"name": "5. Sélectionner un tournoi existant", "value": "select_existing"},
                {"name": "6. Quitter", "value": "quit"},
            ]
        )

        action = questionary.select("Que souhaitez-vous faire ?", choices=choices).ask()

        if action == "launch_with_listed":
            location = _prompt_location()
            if not location:
                continue
            _create_and_open_tournament(
                tournaments_repo,
                location,
                global_players,
                controller,
                "✅ Tournoi '{name}' créé avec les joueurs listés et prêt à être géré."
            )

        elif action == "select_players":
            if not global_players or len(global_players) < 8:
                player_views.display_error_message("Il faut au moins 8 joueurs globaux pour cette option.")
                continue
            selected_players = _pick_players_from_global(global_players)
            if not selected_players:
                continue
            location = _prompt_location()
            if not location:
                continue
            _create_and_open_tournament(
                tournaments_repo,
                location,
                selected_players,
                controller,
                "✅ Tournoi '{name}' créé avec {count} joueur(s) sélectionné(s)."
            )

        elif action == "create_empty_tournament":
            location = _prompt_location()
            if not location:
                continue
            _create_and_open_tournament(
                tournaments_repo,
                location,
                [],
                controller,
                "✅ Tournoi '{name}' vide créé et prêt à être rempli."
            )

        elif action == "manage_global_players":
            controller.manage_players()

        elif action == "select_existing":
            selected = _select_existing_tournament(tournaments_repo)
            if not selected:
                continue

            # Normalize for the submenu
            current_tournament = _as_dict(selected)
            _manage_tournament_player_menu(
                tournaments_repo, current_tournament, controller
            )

        elif action == "quit":
            console.print("\n👋 Au revoir ! Sauvegarde en cours...")
            break

        else:
            player_views.display_error_message("Option invalide.")
