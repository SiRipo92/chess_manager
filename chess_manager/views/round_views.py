from typing import Optional
from rich.console import Console
from rich.table import Table
from chess_manager.utils.tournament_utils import datetime_formatting
import questionary

from chess_manager.models.round_models import Round

console = Console()

def display_round_pairings(rnd: Round) -> None:
    """Affiche la table d’appariements d’un round (noms + IDs)."""
    table = Table(title=f"Appariements - Round {rnd.round_number}")
    table.add_column("Match #", justify="right")
    table.add_column("Joueur 1")
    table.add_column("Joueur 2 / Exempt")

    for i, m in enumerate(rnd.matches, start=1):
        p1 = f"{m.player1.last_name.upper()}, {m.player1.first_name} ({m.player1.national_id})"
        p2 = "EXEMPT" if m.player2 is None else f"{m.player2.last_name.upper()}, {m.player2.first_name} ({m.player2.national_id})"
        table.add_row(str(i), p1, p2)

    console.print(table)

def display_round_results(round):
    """Show results table for the round (after inputs)."""
    table = Table(title=f"Résultats - {round.name}")
    table.add_column("Match #", justify="right")
    table.add_column("Joueur 1")
    table.add_column("Résultat", justify="center")
    table.add_column("Joueur 2 / Exempt")
    for idx, match in enumerate(round.matches, 1):
        p1 = f"{match.player1.last_name.upper()}, {match.player1.first_name} ({match.player1.national_id})"
        if match.player2:
            p2 = f"{match.player2.last_name.upper()}, {match.player2.first_name} ({match.player2.national_id})"
        else:
            p2 = "EXEMPT"
        # Prefer the short code if you stored it; otherwise derive from scores
        pair = _result_pair_str(match)
        table.add_row(str(idx), p1, pair, p2)
    console.print(table)
    if round.end_time:
        console.print(f"✅ {round.name} terminé à {datetime_formatting(round.end_time)}.")

def _result_pair_str(match) -> str:
    # Pair string 'V - D', 'N - N', 'E - ', ...
    if match.player2 is None:
        return "E - "  # exempt

    s1 = float(getattr(match, "score1", 0.0) or 0.0)
    s2 = float(getattr(match, "score2", 0.0) or 0.0)

    if s1 == 1.0 and s2 == 0.0:
        return "V - D"
    if s1 == 0.0 and s2 == 1.0:
        return "D - V"
    if s1 == 0.5 and s2 == 0.5:
        return "N - N"

    # fallback if you store codes
    code1 = getattr(match, "result_code", None) or getattr(match, "result1", None)
    code2 = getattr(match, "result2", None)
    if code1 or code2:
        return f"{(code1 or '').upper()} - {(code2 or '').upper()}"

    return "- - -"

def display_standings(tournament) -> None:
    """
    Provisional standings table (can be called during scoring).
    """
    table = Table(title=f"Classement provisoire (Round {tournament.current_round_number} / {tournament.number_rounds})")
    table.add_column("Rang", justify="right")
    table.add_column("Joueur")
    table.add_column("ID")
    table.add_column("Score", justify="right")

    # sort by score desc, then name for stability
    players = list(tournament.players)
    players.sort(key=lambda p: (-float(tournament.scores.get(p.national_id, 0.0)), p.last_name, p.first_name))

    for idx, p in enumerate(players, start=1):
        score = f"{tournament.scores.get(p.national_id, 0.0):.1f}"
        table.add_row(str(idx), f"{p.last_name.upper()}, {p.first_name}", p.national_id, score)

    console.print(table)

def display_final_summary(tournament):
    from rich.panel import Panel
    title = f"🏁 Tournoi terminé : {tournament.repo_name or tournament.name}"
    subtitle = f"Début: {datetime_formatting(tournament.started_at)}  •  Fin: {datetime_formatting(tournament.finished_at)}"
    console.print(Panel.fit(subtitle, title=title, border_style="green"))

    # Winner = first in standings
    items = []
    for p in tournament.players:
        items.append((tournament.scores.get(p.national_id, 0.0), p))
    items.sort(key=lambda x: (-x[0], x[1].last_name.lower(), x[1].first_name.lower()))
    if items:
        top_score, top_player = items[0]
        console.print(f"🏆 Vainqueur: [bold]{top_player.first_name} {top_player.last_name}[/bold] ({top_player.national_id}) avec {top_score:.1f} points.\n")

    # Full standings
    display_standings(tournament)

def display_match_progress(round_no: int, total_rounds: int, remaining: int, total: int) -> None:
    """Affiche un résumé de progression du round."""
    console.print(
        f"[bold]Tournoi en cours (Round {round_no} / {total_rounds}).[/bold] "
        f"Il manque les résultats de {remaining} / {total} match(es)."
    )

def prompt_select_match_to_score(rnd: Round) -> Optional[int]:
    """
    Propose la liste des matches sans résultat pour saisie.
    Retourne l’index du match à noter (0-based) ou None si annulé.
    """
    choices = []
    for idx, m in enumerate(rnd.matches):
        if m.player2 is None:          # exempt -> pas de saisie
            continue
        if m.result1 is not None:      # déjà saisi
            continue
        p1 = f"{m.player1.last_name.upper()}, {m.player1.first_name} ({m.player1.national_id})"
        p2 = f"{m.player2.last_name.upper()}, {m.player2.first_name} ({m.player2.national_id})"
        choices.append({"name": f"{idx+1}. {p1}  vs  {p2}", "value": idx})

    if not choices:
        return None

    choices.append({"name": "Terminer plus tard / Annuler", "value": None})
    return questionary.select("Sélectionnez un match à saisir :", choices=choices).ask()

def announce_round_closed(rnd: Round) -> None:
    """Message de clôture d’un round."""
    console.print(f"✅ {rnd.name} terminé à {rnd.end_time}.")
