from collections import defaultdict
import re
import unicodedata
from datetime import datetime
from rich.console import Console

console = Console()

def datetime_formatting(timestamp:str | None):
    """Format the timestamp in a readable format"""
    if not timestamp:
        return ""
    try:
        # Works with 'YYYY-MM-DDTHH:MM:SS' and with microseconds
        datetime_obj = datetime.fromisoformat(timestamp)
        return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        # if already friendly, just return
        return timestamp.replace("T", " ")


def slugify_location(loc: str) -> str:
    """Take the user input and strip it and lowercase it for file naming"""
    s = loc.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def _is_finished_tournament(t):
    """Return True if finished (status == 'Terminé' or has finished_at)."""
    if isinstance(t, dict):
        return bool(t.get("finished_at")) or (t.get("status") == "Terminé")
    return bool(getattr(t, "finished_at", "")) or (getattr(t, "status", "") == "Terminé")


def generate_tournament_name(location: str, existing_tournaments: list) -> str:
    """Uses slugify location to generate a tournament name"""
    slug = slugify_location(location)
    date_part = datetime.now().strftime("%Y-%m-%d")
    pattern = re.compile(r"^tournament_(\d+)_")
    max_id = 0
    for t in existing_tournaments:
        name = ""
        if isinstance(t, dict):
            name = t.get("name", "")
        elif hasattr(t, "name"):
            name = getattr(t, "name")
        m = pattern.match(name)
        if m:
            try:
                val = int(m.group(1))
                if val > max_id:
                    max_id = val
            except ValueError:
                continue
    next_id = max_id + 1
    return f"tournament_{next_id}_{slug}_{date_part}"


def _pid(x):
    """Return a national_id from str / dict / object."""
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        return x.get("identifiant_national") or x.get("national_id")
    return getattr(x, "national_id", None)


def participations_by_player(tournaments):
    """# tournois joués (1 par tournoi si le joueur est dans t.players)."""
    out = defaultdict(int)
    for t in (tournaments or []):
        players = getattr(t, "players", None)
        if players is None and isinstance(t, dict):
            players = t.get("players", [])

        # Fallback if 'players' is missing/empty: infer from rounds/scores
        inferred = set()
        if not players:
            scores = getattr(t, "scores", None)
            if scores is None and isinstance(t, dict):
                scores = t.get("scores")
            if isinstance(scores, dict):
                inferred.update(scores.keys())
            rounds = getattr(t, "rounds", None)
            if rounds is None and isinstance(t, dict):
                rounds = t.get("rounds")
            if isinstance(rounds, list):
                for r in rounds:
                    matches = r.get("matches", []) if isinstance(r, dict) else getattr(r, "matches", []) or []
                    for m in matches:
                        if isinstance(m, dict):
                            inferred.add(_pid(m.get("player1")))
                            inferred.add(_pid(m.get("player2")))
                        else:
                            inferred.add(_pid(getattr(m, "player1", None)))
                            inferred.add(_pid(getattr(m, "player2", None)))
        # Source of truth: players if present, else inferred
        participants = {_pid(p) for p in (players or [])} or {p for p in inferred if p}
        for pid in participants:
            out[pid] += 1
    return out


def wins_by_player(tournaments):
    """# tournois gagnés (ex-aequo inclus), via gagnants|winners ou top 'scores'."""
    out = defaultdict(int)
    for t in (tournaments or []):
        if not _is_finished_tournament(t):
            continue  # <-- do not count winners until the tournament is finished

        winners = getattr(t, "gagnants", None)
        if winners is None and isinstance(t, dict):
            winners = t.get("gagnants")
        if not winners:
            winners = getattr(t, "winners", None)
            if winners is None and isinstance(t, dict):
                winners = t.get("winners")

        ids = []
        if winners:
            for w in winners:
                wid = _pid(w)
                if wid:
                    ids.append(wid)
        else:
            scores = getattr(t, "scores", None)
            if scores is None and isinstance(t, dict):
                scores = t.get("scores")
            if isinstance(scores, dict) and scores:
                top = max(scores.values())
                ids = [pid for pid, s in scores.items() if s == top]

        for pid in set(ids):
            out[pid] += 1
    return out


def live_match_stats(tournaments):
    """Matchs joués + points cumulés à partir des rounds déjà saisis."""
    match_count = defaultdict(int)
    points = defaultdict(float)
    for t in (tournaments or []):
        rounds = getattr(t, "rounds", None)
        if rounds is None and isinstance(t, dict):
            rounds = t.get("rounds")
        if not isinstance(rounds, list):
            continue

        for r in rounds:
            matches = r.get("matches", []) if isinstance(r, dict) else getattr(r, "matches", []) or []
            for m in matches:
                if isinstance(m, dict):
                    p1, p2 = _pid(m.get("player1")), _pid(m.get("player2"))
                    s1, s2 = float(m.get("score1", 0.0) or 0.0), float(m.get("score2", 0.0) or 0.0)
                else:
                    p1 = _pid(getattr(m, "player1", None))
                    p2 = _pid(getattr(m, "player2", None))
                    s1 = float(getattr(m, "score1", 0.0) or 0.0)
                    s2 = float(getattr(m, "score2", 0.0) or 0.0)

                if p1:
                    match_count[p1] += 1
                    points[p1] += s1
                if p2:
                    match_count[p2] += 1
                    points[p2] += s2
    return match_count, points


def build_player_tournament_index(tournaments):
    """
    Aggregate per-player live stats across tournaments.
    Returns: { pid: {"participations", "victoires", "matchs", "points"} }
    """
    parts = participations_by_player(tournaments)
    wins = wins_by_player(tournaments)
    m_cnt, pts = live_match_stats(tournaments)

    all_ids = set(parts) | set(wins) | set(m_cnt) | set(pts)
    return {
        pid: {
            "participations": parts.get(pid, 0),
            "victoires": wins.get(pid, 0),
            "matchs": m_cnt.get(pid, 0),
            "points": round(pts.get(pid, 0.0), 1),
        }
        for pid in all_ids
    }
