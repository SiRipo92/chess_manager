from __future__ import annotations
from rich.console import Console
import questionary
from datetime import datetime
from chess_manager.models.tournament_models import Tournament
from chess_manager.models.round_models import Round
from chess_manager.views.round_views import display_round_results, display_standings
from chess_manager.views.match_views import prompt_result_for_match
from chess_manager.controllers.match_controller import (
    _has_result,
    _apply_points_once,
    _rollback_points,
)

console = Console()


def score_round(tournament: Tournament, rnd: Round) -> bool:
    """
    Interactive scoring for a single round,
    Returns True if round confirmed; False if user aborted.
    Assumes: each Match has set_result_by_code('V'|'D'|'N'|'E') and is_scored().
    """
    # Matches that still need a result
    pending = {
        i for i in range(len(rnd.matches))
        if not _has_result(rnd.matches[i])
    }

    while pending:
        left = len(pending)
        console.print(
            f"[bold]Tournoi en cours (Round {rnd.round_number} / {tournament.number_rounds}). "
            f"Il manque les résultats de {left} / {len(rnd.matches)} match(es).[/bold]"
        )

        # Menu of pending matches
        choices = []
        for i in sorted(pending):
            m = rnd.matches[i]
            p1 = f"{m.player1.last_name.upper()}, {m.player1.first_name} ({m.player1.national_id})"
            p2 = "EXEMPT" if m.player2 is None else \
                f"{m.player2.last_name.upper()}, {m.player2.first_name} ({m.player2.national_id})"
            choices.append({"name": f"{i+1}. {p1}  vs  {p2}", "value": i})
        choices.append({"name": "Quitter (annuler la saisie)", "value": "quit"})

        sel = questionary.select("Sélectionnez un match à saisir :", choices=choices).ask()
        if sel == "quit" or sel is None:
            return False

        match = rnd.matches[sel]

        # Exempt: auto “E” if not already set
        if match.player2 is None:
            if not _has_result(match):
                match.set_result_by_code("E")
                _apply_points_once(tournament, match)
            pending.discard(sel)
            continue

        # Ask for result
        result_code = prompt_result_for_match()
        if result_code is None:
            continue

        match.set_result_by_code(result_code)
        _apply_points_once(tournament, match)
        pending.discard(sel)

        # Live standings after each entry (optional but useful)
        display_standings(tournament)

    # All results entered -> summary + confirm/edit
    rnd.end_time = datetime.now().isoformat(timespec="seconds")
    console.print()
    display_round_results(rnd)

    while True:
        action = questionary.select(
            "Confirmer ces résultats ?",
            choices=[
                {"name": "1. Confirmer le round", "value": "confirm"},
                {"name": "2. Modifier un résultat", "value": "edit"},
                {"name": "3. Annuler (retour)", "value": "abort"},
            ],
        ).ask()

        if action == "confirm":
            return True
        if action in (None, "abort"):
            return False

        # Edit one match
        if action == "edit":
            edit_choices = []
            for i, m in enumerate(rnd.matches, start=1):
                p1 = f"{m.player1.last_name.upper()}, {m.player1.first_name} ({m.player1.national_id})"
                p2 = "EXEMPT" if m.player2 is None else \
                    f"{m.player2.last_name.upper()}, {m.player2.first_name} ({m.player2.national_id})"
                status = "✅" if _has_result(m) else "⏳"
                edit_choices.append({"name": f"{i}. {p1}  vs  {p2}   {status}", "value": i - 1})
            edit_choices.append({"name": "Retour", "value": None})

            idx = questionary.select("Quel match modifier ?", choices=edit_choices).ask()
            if idx is None:
                continue

            m = rnd.matches[idx]
            if m.player2 is None:
                console.print("[yellow]Impossible de modifier un exempt (E).[/yellow]")
                continue

            # Roll back previous points, re-enter result, re-apply
            _rollback_points(tournament, m)
            new_code = prompt_result_for_match()
            if new_code is None:
                # restore old points if user cancels
                _apply_points_once(tournament, m)
                continue

            m.set_result_by_code(new_code)
            _apply_points_once(tournament, m)

            console.print()
            display_round_results(rnd)
        else:
            continue


# -----------------------
# Helpers
# -----------------------

def _count_pending_matches(rnd: Round) -> int:
    """Matches with missing results (excluding byes)."""
    n = 0
    for m in rnd.matches:
        if m.player2 is None:
            continue
        if m.result1 is None:
            n += 1
    return n
