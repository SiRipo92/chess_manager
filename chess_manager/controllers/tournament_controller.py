from __future__ import annotations
from typing import Dict
from rich.console import Console
import questionary

from chess_manager.models.tournament_models import Tournament
from chess_manager.models.round_models import Round
from chess_manager.controllers.round_controller import score_round
from chess_manager.views.round_views import display_round_pairings
from chess_manager.views.tournament_views import display_tournament_recap

console = Console()


def launch_first_round_flow(tournament_dict: Dict) -> Tournament:
    """
    Construit un Tournament depuis un dict repo, lance le 1er round (pairings au niveau modèle),
    affiche les appariements, et retourne le modèle prêt à être scoré.
    """

    model = Tournament.from_dict(tournament_dict)
    if model.roster_size() < 8:
        raise ValueError("Il faut au moins 8 joueurs pour démarrer un tournoi.")

    confirm = questionary.confirm(
        f"Voulez-vous lancer le tournoi '{tournament_dict.get('name','(sans nom)')}' "
        f"avec {model.roster_size()} joueurs ?"
    ).ask()
    if not confirm:
        raise RuntimeError("Lancement annulé par l'utilisateur.")

    first_round: Round = model.start_first_round()
    model.repo_name = tournament_dict.get("name", "") or model.repo_name
    display_round_pairings(first_round)
    return model

def run_rounds_until_done(model: Tournament, repo=None) -> None:
    """
    Score the current round, then keep creating/scoring next rounds until done.
    When finished, mark tournament as finished, save, and show recap.
    """
    # Score the round that was just created/launched
    current = model.rounds[-1]
    done = score_round(model, current)
    if not done:
        return

    # Next rounds
    while model.current_round_number < model.number_rounds:
        next_round = model.start_next_round()
        display_round_pairings(next_round)
        done = score_round(model, next_round)
        if not done:
            return

    # All rounds completed -> finalize and recap
    model.mark_finished()
    if repo is not None:
        try:
            repo.save_tournament(model.to_dict())
        except Exception:
            console.print("[red]Échec de la sauvegarde du tournoi finalisé.[/red]")
    display_tournament_recap(model)

