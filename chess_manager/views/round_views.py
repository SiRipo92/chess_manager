from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import questionary
from chess_manager.utils.tournament_utils import datetime_formatting
from chess_manager.models.round_models import Round

console = Console()


def display_round_pairings(rnd: Round) -> None:
    """Affiche la table d’appariements d’un round (noms + IDs)."""
    table = Table(title=f"Appariements - Tour {rnd.round_number}")
    table.add_column("Match #", justify="right")
    table.add_column("Joueur 1")
    table.add_column("Joueur 2 / Exempt")

    for i, m in enumerate(rnd.matches, start=1):
        p1 = f"{m.player1.last_name.upper()}, {m.player1.first_name} ({m.player1.national_id})"
        p2 = "EXEMPT" if m.player2 is None \
            else f"{m.player2.last_name.upper()}, {m.player2.first_name} ({m.player2.national_id})"
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
        # Prefer the short code stored (V-D); otherwise derive from scores
        pair = _result_pair_str(match)
        table.add_row(str(idx), p1, pair, p2)
    console.print(table)
    if round.end_time:
        console.print(f"✅ {round.name} terminé à {datetime_formatting(round.end_time)}.")


def display_standings(tournament) -> None:
    """Provisional ranking (called again after each confirmed input for round)."""
    table = Table(
        title=f"Classement provisoire (Tour {tournament.current_round_number} / {tournament.number_rounds})"
    )
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

# --- Helper ---------------------------------------------------------------


def perspective_code(player_id: str, rnd) -> str:
    """
    Returns le abbreviated 'V', 'D', 'N', or 'E' codes for each player per round.
    """
    for m in rnd.matches:
        # Exempt?
        if m.player2 is None:
            if m.player1 and m.player1.national_id == player_id:
                return "E"
            continue

        pid1 = m.player1.national_id
        pid2 = m.player2.national_id
        s1 = float(getattr(m, "score1", 0.0) or 0.0)
        s2 = float(getattr(m, "score2", 0.0) or 0.0)

        if player_id == pid1:
            if m.result1 is None and m.result2 is None and s1 == 0.0 and s2 == 0.0:
                return "-"  # pas encore saisi
            if s1 > s2:
                return "V"
            if s1 < s2:
                return "D"
            return "N"

        if player_id == pid2:
            if m.result1 is None and m.result2 is None and s1 == 0.0 and s2 == 0.0:
                return "-"
            if s2 > s1:
                return "V"
            if s2 < s1:
                return "D"
            return "N"

    return "-"  # fallback défensif


# --- Main function --------------------------------------------------------

def display_final_summary(tournament) -> None:
    """
    Display a complete tournament recap:
      - header (name + formatted start/finish)
      - co-winners if tied on top score
      - final standings
      - per-round results matrix (from each player's perspective)
    """
    # Header panel
    title = f"🏁 Tournoi terminé : {getattr(tournament, 'repo_name', '') or tournament.name}"
    subtitle = (
        f"Début : {datetime_formatting(getattr(tournament, 'started_at', ''))}  •  "
        f"Fin : {datetime_formatting(getattr(tournament, 'finished_at', ''))}"
    )
    console.print(Panel.fit(subtitle, title=title, border_style="green"))

    # --- Compute standings -------------------------------------------------
    players = list(tournament.players)
    scores = {p.national_id: float(tournament.scores.get(p.national_id, 0.0)) for p in players}

    players.sort(
        key=lambda p: (-scores.get(p.national_id, 0.0), p.last_name.lower(), p.first_name.lower())
    )

    # Winners
    top_score = scores[players[0].national_id] if players else 0.0
    winners = [p for p in players if scores[p.national_id] == top_score]
    if winners:
        winners_str = ", ".join(
            f"{w.first_name} {w.last_name} ({w.national_id})" for w in winners
        )
        plural = "s" if len(winners) > 1 else ""
        console.print(
            f"🏆 Vainqueur{plural} : [bold]{winners_str}[/bold] avec {top_score:.1f} points.\n"
        )

    # --- Final standings table --------------------------------------------
    standings = Table(
        title=f"Classement final (Tour {tournament.current_round_number} / {tournament.number_rounds})"
    )
    standings.add_column("Rang", justify="right")
    standings.add_column("Joueur")
    standings.add_column("ID")
    standings.add_column("Score", justify="right")

    for idx, p in enumerate(players, start=1):
        standings.add_row(
            str(idx),
            f"{p.last_name.upper()}, {p.first_name}",
            p.national_id,
            f"{scores[p.national_id]:.1f}",
        )
    console.print(standings)

    # --- Per-round results matrix -----------------------------------------
    rounds = list(getattr(tournament, "rounds", []))
    if rounds:
        matrix = Table(title="Résultats par round (perspective joueur)")
        matrix.add_column("Joueur")
        for i, _ in enumerate(rounds, start=1):
            matrix.add_column(f"R{i}", justify="center")
        matrix.add_column("Total", justify="right")

        for p in players:
            row = [f"{p.last_name.upper()}, {p.first_name} ({p.national_id})"]
            for rnd in rounds:
                row.append(perspective_code(p.national_id, rnd))  # <- 🔑 call helper here
            row.append(f"{scores[p.national_id]:.1f}")
            matrix.add_row(*row)

        console.print(matrix)


def display_match_progress(round_no: int, total_rounds: int, remaining: int, total: int) -> None:
    """Display a round progress summary (number of missing match inputs per round)"""
    console.print(
        f"[bold]Tournoi en cours (Tour {round_no} / {total_rounds}).[/bold] "
        f"Il manque les résultats de {remaining} / {total} match(es)."
    )


def prompt_select_match_to_score(rnd: Round) -> Optional[int]:
    """
    List of matches without results that make a dynamic menu, where each match missing results can be selected
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
    """Message to announce the end of a round and it's registered close time"""
    console.print(f"✅ {rnd.name} terminé à {rnd.end_time}.")

# -----------------------
# Helpers (views only)
# -----------------------


def _name_id(player) -> str:
    return f"{player.last_name.upper()}, {player.first_name} ({player.national_id})"


def _result_pair_str(match) -> str:
    """
    Renvoie 'V - D', 'N - N', 'E - ', etc.
    Déduit à partir des scores si nécessaire.
    """
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

    # fallback si vous stockez des codes
    code1 = (getattr(match, "result_code", None) or getattr(match, "result1", None) or "").upper()
    code2 = (getattr(match, "result2", None) or "").upper()
    if code1 or code2:
        return f"{code1} - {code2}"

    return "- - -"
