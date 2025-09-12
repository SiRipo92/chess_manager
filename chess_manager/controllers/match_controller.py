from __future__ import annotations
from chess_manager.models.tournament_models import Tournament
from chess_manager.models.match_models import Match

# -------------------------------------------------
# Helper methods to manage match logic
# -------------------------------------------------


def _has_result(match: Match) -> bool:
    """True if the match already has a result (or is a bye)."""
    if hasattr(match, "is_scored") and callable(match.is_scored):
        return bool(match.is_scored())

    for attr in ("result_code", "result1"):
        if getattr(match, attr, None):
            return True

    if match.player2 is None:
        return True

    return False


def _apply_points_once(tournament: Tournament, match: Match) -> None:
    """Award points for a single match."""
    award = getattr(tournament, "award_points_for_match", None)
    if callable(award):
        award(match)
    else:
        tournament.apply_match_points(match)


def _rollback_points(tournament: Tournament, match: Match) -> None:
    """Subtract previously-applied points for this match."""
    id1 = match.player1.national_id
    s1 = float(getattr(match, "score1", 0.0) or 0.0)
    tournament.scores[id1] = tournament.scores.get(id1, 0.0) - s1

    if match.player2:
        id2 = match.player2.national_id
        s2 = float(getattr(match, "score2", 0.0) or 0.0)
        tournament.scores[id2] = tournament.scores.get(id2, 0.0) - s2
