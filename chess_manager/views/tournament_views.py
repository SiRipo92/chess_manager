from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
import questionary

from chess_manager.models.player_models import Player
from chess_manager.models.round_models import Round
from chess_manager.utils.tournament_utils import datetime_formatting

console = Console()


def confirm_launch_tournament(tournament_name: str, count: int) -> bool:
    """Yes/No before launching with the listed players."""
    return bool(questionary.confirm(
        f"Voulez-vous lancer le tournoi '{tournament_name}' avec {count} joueurs ?"
    ).ask())


def display_round_pairings(round_obj: Round) -> None:
    """Pretty table with IDs + names, and Exempt where applicable."""
    table = Table(title=f"Appariements - {round_obj.name}")
    table.add_column("Match #")
    table.add_column("Joueur 1 (ID)")
    table.add_column("Joueur 2 (ID) / Exempt")

    for idx, m in enumerate(round_obj.matches, 1):
        p1_label = f"{m.player1.last_name.upper()}, {m.player1.first_name} ({m.player1.national_id})"
        if m.player2 is None:  # exempt
            p2_label = "EXEMPT"
        else:
            p2_label = f"{m.player2.last_name.upper()}, {m.player2.first_name} ({m.player2.national_id})"
        table.add_row(str(idx), p1_label, p2_label)

    console.print(table)


def display_match_progress(round_no: int, total_rounds: int, remaining: int, total: int) -> None:
    """Short banner showing how many matches still need results."""
    console.print(
        f"[bold]Tournoi en cours (Round {round_no} / {total_rounds}).[/bold] "
        f"Résultats manquants : {remaining} / {total}."
    )


def prompt_select_match_to_score(round_obj: Round) -> Optional[int]:
    """
    Build a dynamic menu from matches that still need results.
    Returns the 0-based match index or None if user quits.
    """
    choices = []
    for idx, m in enumerate(round_obj.matches, 0):
        # Skip already resolved (including exempt automatically scored)
        if m.result1 is not None or (m.player2 is None):
            continue
        p1 = f"{m.player1.last_name.upper()}, {m.player1.first_name} ({m.player1.national_id})"
        p2 = f"{m.player2.last_name.upper()}, {m.player2.first_name} ({m.player2.national_id})" \
            if m.player2 else "EXEMPT"
        choices.append({"name": f"{idx+1}. {p1}  vs  {p2}", "value": idx})

    if not choices:
        return None

    choices.append({"name": "Annuler / Revenir plus tard", "value": None})
    return questionary.select("Sélectionnez un match à saisir :", choices=choices).ask()


def prompt_result_for_match() -> Optional[str]:
    """
    Ask result for Player1 perspective (V/D/N). Return code or None.
    """
    res = questionary.select(
        "Résultat pour le joueur 1 :",
        choices=[
            {"name": "Victoire (V)", "value": "V"},
            {"name": "Défaite (D)", "value": "D"},
            {"name": "Match nul (N)", "value": "N"},
            {"name": "Annuler", "value": None},
        ],
    ).ask()
    return res

# ─────────────────────────────────────────
# Description (single-string) view helpers
# ─────────────────────────────────────────

def display_tournament_description(tournament) -> None:
    """
    Show the tournament description (single string) or an empty message.
    """
    text = tournament.get_description() \
        if hasattr(tournament, "get_description")\
        else (getattr(tournament, "description", "") or "")
    console.print("\n[bold cyan]Description du tournoi[/bold cyan]")
    if not text.strip():
        console.print("[dim]Aucune description pour le moment.[/dim]") # rich library dimmed text
    else:
        console.print(text)

def prompt_description_menu() -> Optional[str]:
    """
    Return one of: 'edit', 'clear', 'back' (or None if cancelled).
    """
    return questionary.select(
        "Description : que souhaitez-vous faire ?",
        choices=[
            {"name": "1. Modifier la description", "value": "edit"},
            {"name": "2. Effacer la description", "value": "clear"},
            {"name": "3. Retour", "value": "back"},
        ],
    ).ask()

def prompt_edit_description(existing_text: str = "") -> Optional[str]:
    """
    Prompt the user for a tournament description directly in the CLI.
    """
    try:
        # When the user presses ESC/Ctrl+C or cancels, .ask() returns None

        value = questionary.text(
            "Nouvelle description :",
            default=existing_text
        ).ask()
    except KeyboardInterrupt:  # KeyboardInterrupt is caught to return
        return None
    except Exception as e:
        # catch any error without crashing the flow.
        console.print(f"[red]Erreur de saisie de la description : {e}[/red]")
        return None

    # If the prompt was cancelled or returned nothing, pass None to the caller.
    if value is None:
        return None
    return value

def confirm_clear_description() -> bool:
    """
    Yes/No confirmation for clearing the description.
    """
    return bool(questionary.confirm("Effacer la description du tournoi ?").ask())

def announce_round_closed(round_obj: Round) -> None:
    """Notifies the end of a round"""
    console.print(f"✅ {round_obj.name} terminé à {round_obj.end_time}.")


def display_rankings(scores: Dict[str, float], players: List[Player]) -> None:
    """
    Show a ranking table (by score desc). Names + IDs + points.
    """
    # Map id -> Player for pretty labels
    by_id = {p.national_id: p for p in players}
    ranking = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    table = Table(title="Classement actuel")
    table.add_column("#")
    table.add_column("Joueur")
    table.add_column("ID")
    table.add_column("Points")

    for i, (pid, pts) in enumerate(ranking, 1):
        p = by_id.get(pid)
        if p:
            name = f"{p.last_name.upper()}, {p.first_name}"
        else:
            name = "(inconnu)"
        table.add_row(str(i), name, pid, f"{pts:.1f}")

    console.print(table)


def announce_tournament_finished(winner_label: str) -> None:
    """Displays the announced winner of a tournament"""
    console.print("\n[bold green]🏁 Tournoi terminé ![/bold green]")
    console.print(f"Gagnant : [bold]{winner_label}[/bold]")


def per_round_code_for(player_id: str, rnd) -> str:
    """
    Return 'V', 'D', 'N', 'E' for the given player in this round (or '' if absent).
    """
    for m in rnd.matches:
        # Exempt match: only player1 exists
        if m.player2 is None:
            if m.player1.national_id == player_id:
                return "E"
            continue

        # If the player is in this match, normalize perspective:
        if m.player1.national_id == player_id or m.player2.national_id == player_id:
            if m.player1.national_id == player_id:
                s_self = float(getattr(m, "score1", 0.0) or 0.0)
                s_opp = float(getattr(m, "score2", 0.0) or 0.0)
                # Prefer a per-match result code if present, else player1-specific
                fallback = (getattr(m, "result_code", "") or getattr(m, "result1", "") or "")
            else:
                s_self = float(getattr(m, "score2", 0.0) or 0.0)
                s_opp = float(getattr(m, "score1", 0.0) or 0.0)
                fallback = (getattr(m, "result2", "") or "")

            # Compare using rounded tuples to avoid tiny float artifacts
            key = (round(s_self, 1), round(s_opp, 1))
            if key == (1.0, 0.0):
                return "V"
            if key == (0.5, 0.5):
                return "N"
            if key == (0.0, 1.0):
                return "D"

            # If scores don't map cleanly, fall back to any recorded code
            return str(fallback).upper()

    return ""


def display_final_standings(tournament) -> list:
    """
    Prints final standings and returns the sorted player list (for reuse).
    """
    table = Table(title=f"Classement final — {tournament.name}")
    table.add_column("Rang", justify="right")
    table.add_column("Joueur")
    table.add_column("ID")
    table.add_column("Score", justify="right")

    players = list(tournament.players)
    players.sort(key=lambda p: (-float(tournament.scores.get(p.national_id, 0.0)), p.last_name, p.first_name))

    for idx, p in enumerate(players, start=1):
        score = f"{tournament.scores.get(p.national_id, 0.0):.1f}"
        table.add_row(str(idx), f"{p.last_name.upper()}, {p.first_name}", p.national_id, score)

    console.print(table)
    return players


def display_tournament_recap(tournament) -> None:
    """
    Full recap: header, timestamps, final standings, per-round matrix.
    """
    console.print(f"\n[bold green]✅ Tournoi terminé : {tournament.name}[/bold green]")
    meta = Table(show_header=False, box=None)
    meta.add_row("Lieu :", tournament.location)
    meta.add_row("Statut :", getattr(tournament, "status", ""))
    meta.add_row("Date (début) :", tournament.start_date or "—")
    meta.add_row("Date (fin)   :", tournament.end_date or "—")
    meta.add_row("Heure (début):", datetime_formatting(getattr(tournament, "started_at", "")) or "—")
    meta.add_row("Heure (fin)  :", datetime_formatting(getattr(tournament, "finished_at", "")) or "—")
    console.print(meta)

    # Final standings
    players_sorted = display_final_standings(tournament)

    # Per-round codes matrix
    matrix = Table(title="Résultats par joueur et par round")
    matrix.add_column("Joueur")
    matrix.add_column("ID")
    for r in tournament.rounds:
        matrix.add_column(f"R{r.round_number}", justify="center")

    for p in players_sorted:
        row = [f"{p.last_name.upper()}, {p.first_name}", p.national_id]
        for r in tournament.rounds:
            row.append(per_round_code_for(p.national_id, r))
        matrix.add_row(*row)

    console.print(matrix)
    console.print("Le tournoi est terminé. Retour au menu principale ... ")
