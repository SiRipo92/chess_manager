from __future__ import annotations
from typing import Dict
from rich.console import Console
import questionary

from chess_manager.models.tournament_models import Tournament
from chess_manager.models.round_models import Round
from chess_manager.controllers.round_controller import score_round
from chess_manager.views.round_views import display_round_pairings
from chess_manager.views.tournament_views import (
    display_tournament_recap,
    display_tournament_description,
    prompt_description_menu,
    prompt_edit_description,
    confirm_clear_description,
    announce_tiebreak_start,
)

console = Console()


# Helper function to remove duplicated lines
def _score_and_persist_round(model: Tournament, rnd: Round, repo=None, persist: bool = True) -> bool:
    display_round_pairings(rnd)
    try:
        done = score_round(model, rnd)
    except KeyboardInterrupt:
        console.print("[yellow]Saisie interrompue par l'utilisateur.[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]Erreur pendant la saisie des résultats : {e}[/red]")
        return False

    if not done:
        return False

    if persist and repo is not None:
        try:
            repo.save_tournament(model.to_dict())
        except Exception as e:
            console.print(f"[red]Échec de la sauvegarde après un tour : {e}[/red]")
    return True

# Flows for launching tournament (First round and then all subsequent rounds)
def launch_first_round_flow(tournament_dict: Dict) -> Tournament:
    model = Tournament.from_dict(tournament_dict)
    if model.roster_size() < 8:
        raise ValueError("Il faut au moins 8 joueurs pour démarrer un tournoi.")

    confirm = questionary.confirm(
        f"Voulez-vous lancer le tournoi '{tournament_dict.get('name','(sans nom)')}' "
        f"avec {model.roster_size()} joueurs ?"
    ).ask()
    if not confirm:
        raise RuntimeError("Lancement annulé par l'utilisateur.")

    try:
        first_round: Round = model.start_first_round()
    except ValueError as e:
        raise ValueError(f"Impossible de lancer le 1er tour : {e}") from e
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la création du 1er tour : {e}") from e

    model.repo_name = tournament_dict.get("name", "") or model.repo_name
    return model


def run_rounds_until_done(model: Tournament, repo=None, player_controller=None) -> None:
    """Score current round, play remaining scheduled rounds, then auto tiebreaks if needed."""
    # 1) Score the round that already exists (from launch)
    try:
        current = model.rounds[-1]
    except (IndexError, AttributeError):
        console.print("[red]Aucun round à scorer.[/red]")
        return
    if not _score_and_persist_round(model, current, repo):
        return

    # 2) Play all scheduled rounds (no tiebreaks here)
    while model.current_round_number < model.number_rounds:
        try:
            nxt = model.start_next_round()
        except ValueError as e:
            console.print(f"[red]Impossible de créer le tour suivant : {e}[/red]")
            break
        except Exception as e:
            console.print(f"[red]Erreur interne lors de la création d'un nouveau tour : {e}[/red]")
            break

        if not _score_and_persist_round(model, nxt, repo):
            return

    # 3) AFTER scheduled rounds: automatic tie-break rounds until a single winner
    tiebreak_index = 1
    while model.have_first_place_tie():
        leaders = model.tied_leaders()
        top_score = max(model.scores.get(pid, 0.0) for pid in leaders)
        # Pretty labels for the announce
        by_id = {p.national_id: p for p in model.players}
        labels = [
            f"{by_id[pid].last_name.upper()}, {by_id[pid].first_name} ({pid})"
            if pid in by_id else pid
            for pid in leaders
        ]
        announce_tiebreak_start(labels, top_score, tiebreak_index)

        try:
            tb_round = model.start_tiebreak_round(leaders)
        except Exception as e:
            console.print(f"[red]Impossible de créer un round de départage : {e}[/red]")
            break

        if not _score_and_persist_round(model, tb_round, repo):
            return

        tiebreak_index += 1

    # 4) Optional description edit before finishing
    try:
        wants_desc = questionary.confirm(
            "Souhaitez-vous ajouter/modifier la description avant de clôturer le tournoi ?"
        ).ask()
    except KeyboardInterrupt:
        return
    except Exception:
        wants_desc = False

    if wants_desc:
        manage_tournament_description(model, repo=repo)

    # 5) Bumps tournaments_won in player model up for winner
    wid = model.compute_winner_id()
    if wid:
        model.winner_id = wid
        if player_controller is not None:
            try:
                players = player_controller.load_players()
                by_id = {p.national_id: p for p in players}
                if wid in by_id:
                    by_id[wid].record_tournament_win()
                    player_controller.save_players(list(by_id.values()))
            except Exception as e:
                console.print(f"[yellow]Avertissement : impossible de mettre à jour 'tournaments_won' : {e}[/yellow]")


    # 6) Finish + save + recap
    model.mark_finished()
    if repo is not None:
        try:
            repo.save_tournament(model.to_dict())
        except Exception as e:
            console.print(f"[red]Échec de la sauvegarde du tournoi finalisé : {e}[/red]")

    try:
        display_tournament_recap(model)
    except Exception as e:
        console.print(f"[red]Erreur lors de l'affichage du récapitulatif : {e}[/red]")


# ----------------------
# Modify and Clear Description flow
# ----------------------

def manage_tournament_description(model: Tournament, repo=None) -> None:
    """
    View/edit/clear the tournament single-string description.
    Saves after each modification when a repo is provided.
    """
    while True:
        display_tournament_description(model)
        has_text = bool(
            (
                model.get_description()
                if hasattr(model, "get_description")
                else model.description or ""
            ).strip()
        )
        action = prompt_description_menu(has_text)
        if action in (None, "back"):
            return

        if action == "edit":
            current = model.get_description() if hasattr(model, "get_description") else (model.description or "")
            try:
                new_text = prompt_edit_description(current)
            except KeyboardInterrupt:
                continue

            # Only persist if user actually provided a new value
            if new_text is not None:
                if hasattr(model, "set_description"):
                    model.set_description(new_text)
                else:
                    model.description = new_text

                if repo is not None:
                    try:
                        repo.save_tournament(model.to_dict())
                    except Exception as e:
                        console.print(f"[red]Échec de la sauvegarde de la description : {e}[/red]")

        elif action == "clear":
            try:
                if confirm_clear_description():
                    if hasattr(model, "set_description"):
                        model.set_description("")
                    else:
                        model.description = ""

                    # Persist/save regardless of which branch was taken
                    if repo is not None:
                        try:
                            repo.save_tournament(model.to_dict())
                        except Exception as e:
                            console.print(f"[red]Échec de la sauvegarde de la description : {e}[/red]")
            except KeyboardInterrupt:
                continue

        else:
            console.print("[red]Option invalide.[/red]")
