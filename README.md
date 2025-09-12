# ♟️ Chess Tournament Manager (Offline CLI - Python)
<br>[![Flake8](https://github.com/SiRipo92/chess_manager/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/SiRipo92/chess_manager/actions/workflows/lint.yml)
<br>[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
<p>This project is an offline, console-based chess tournament manager built with Python using the MVC (Model-View-Controller) design pattern. It allows club managers to create and run chess tournaments, track players, scores, and generate tournament reports.

## 📁 Project Structure

```bash
chess_manager/                  # Project root
├── chess_manager/             # Internal package containing core logic
│   ├── controllers/           # Business logic (managing players, tournaments, rounds, main)
│   ├── models/                # Data models (Player, Match, Round, Tournament, TournamentRepository)
│   ├── views/                 # CLI views using `questionary` and `rich`
│   ├── constants/             # Centralized constants (labels, validation rules, mappings)
│   ├── utils/                 # Helper/validator functions for field inputs
├── data/                      # Directory containing JSON data files
│   ├── players/
│   │   ├── players.json       # JSON data file with enrolled players
│   ├── tournaments/
│   │   ├── tournaments.json   # TOURNAMENT REPOSITORY - Persistent memory/json of all tournaments
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── .gitignore
├── flake8_report/             # HTML report output from flake8
├── setup.cfg                  # Configuration for flake8 and coverage
├── .github/                   # Linting CI via GitHub Actions
```

## 📦 Setup Instructions

1. Clone this repository
2. Set up the virtual environment and install dependencies:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
3. Run the program
    ```bash
    python3 main.py
    ```

## ✨ Key Features
+ **Resumable tournaments**
<br>Close the program anytime; progress is persisted. Resume an existing tournament from the main menu.

+ **Round results in any order**
<br> Enter match results as games finish. The UI shows remaining matches; order doesn’t matter.

+ **User-friendly result entry**
<br> You input the result only for Player 1 (V/D/N). The complementary result for Player 2 is filled automatically.

+ **Swiss-like pairing**
<br> Pair by score buckets with a light shuffle inside ties; avoids repeat pairings within a tournament (tracks past pairs).

+ **Roster rules**
<br> Minimum 8 players required to launch. Once the tournament starts, registration is locked (no adding/removing mid-tournament).

+ **Odd-player handling (byes)**
<br> If there’s an odd number of players, the last one is exempt (bye) and receives the appropriate score automatically.

+ **Tournament progress indicator**
<br> When selecting an existing tournament you’ll see:
  + Non démarré 
  + En cours X% (4 rounds → 0/25/50/75/100)
  + Terminé

+ **Global player stats**
<br> The “Joueurs globaux” table shows matches, cumulative points, tournament participations, and tournament wins (ties for 1st included).
These stats are computed from the tournament repository, so the view always reflects reality.

+ **Player management (CRU)**
  + Create a player with validations (name, birthdate, national ID). 
  + Read (list/inspect). 
  + Update any personal field (last name, first name, birthdate, national ID) with the same validators used at creation and confirmation prompts. 
  + Safe cancel on empty input (press Enter to skip a change).
  + (No Delete — by design; easy to add later.)

+ **Informative, real-time views**
  + Round-by-round tables of results per player. 
  + Provisional standings after each match entry. 
  + Final standings and a per-round results grid at the end. 
  + Clear status banners (“Non démarré”, “En cours X%”, “Terminé”).

+ **Tournament notes / descriptions**
  + Add/Edit/Clear a single-string description any time (before, during, or after the event).
  + The description is persisted and shown in the final recap if present.

+ **Correcting input**
  + During a round (before confirming it), you can reselect a match and overwrite its result to correct mistakes. 
  + After confirmation, you can resume later rounds; (post-confirmation edits can be added if needed).

+ **Validation & typing**
  + Strong input validators (date format and range, name characters, national-ID pattern; uniqueness on create/edit). 
  + Type hints throughout to keep data handling consistent.

+ **Persistent storage (JSON)**
  + players.json — normalized player registry. 
  + tournaments.json — authoritative record for all tournaments (finished + in-progress).

+ **Nice CLI**
<br> Built with Rich for tables/formatting and Questionary for prompts. User-friendly messages, colors, and summaries at each step.

## 🧠 How It Works (Architecture)
### Models
+ **Player** : One chess player with validated fields (name, <code>YYYY-MM-DD birthdate</code>, ID like <code>AB12345</code>). Normalizes names, timestamps enrollment, records match results (<code>V/D/N</code> → “victoire/défaite/nul”), computes age/points, and (de)serializes cleanly to JSON.
<br><br>
+ **Match** : One game between two players (or a bye). Stores result as labels and numeric scores; supports set_result_by_code(<code>'V'|'D'|'N'|'E'</code>), auto-handles byes when <code>player2=None</code>, and (de)serializes using player IDs.
<br><br>
+ **Round** : A round with start/end timestamps and a list of matches. Adds matches, marks completion, and (de)serializes; rebuilds matches via a <code>player_lookup</code>.
<br><br>
+ **Tournament** : The event: location/dates, roster, rounds, live <code>scores{pid:points}</code>, and <code>past_pairs</code>. Validates roster (min 8), launches <code>start_first_round()</code> (shuffle + auto-bye), pairs Swiss-like in <code>start_next_round()</code> (bucket by score, avoid repeats), applies points, manages a single description, and (de)serializes (players/rounds/scores/pairs). Preserves a stable <code>repo_name</code>.
<br><br>
+ **TournamentRepository** : Flat JSON persistence at <code>data/tournaments/tournaments.json</code> (auto-creates). Loads all, upserts by case-insensitive <ode>name</code>, and fetches by name (returns dicts). Tournaments form the authoritative history; if <code>players.json</code> is missing, global stats can still be inferred from past tournaments.

## Views
+ **Player** : All player UI (create/edit/search) with Questionary + Rich, reusing the same validators; renders recap and lists with optional global stats. Pure presentation (returns values or <code>None</code>).
<br><br>
+ **Match** : Tiny prompt that returns a result for Player 1 (<code>'V'|'D'|'N'</code> or <code>None</code>). No side effects.
<br><br>
+ **Round** : Pairings, per-match result table, live standings, “round finished” banner, and “which match to score” menu. Display-only.
<br><br>
+ **Tournament** : Launch confirmation, pairings tables, match-selection menu, P1 result picker, live rankings/progress, final recap (timestamps, standings, per-round matrix), and view/edit/clear for the description. Display-only.


## Controllers
+ **Main Controller** : Entry point and top-level menu. Creates tournaments (named via generator) in the repo, opens a per-tournament submenu (add players, launch/resume, summary, description), reloads state each loop, and delegates to other controllers/views; persists after critical steps.
<br><br>
+ **Player** : Ensures <code>players.json</code> exists, loads/saves (keeps alphabetical), validates on create, enforces unique IDs, supports fuzzy search, and drives interactive add/edit/manage using <code>player_views</code>. Pulls live stats from tournaments for the list view.
<br><br>
+ **Match** : Match-centric helpers: detect if a match already has a result/bye, apply points exactly once, and rollback when editing—pure logic (no prompts/files).
<br><br>
+ **Round** : Interactive scoring loop for one round: pick unscored match → ask result → apply/rollback points via Match Controller → show live standings → confirm/edit round → return <code>True/False</code>. Pairings come from the model; saving is done by the caller.
<br><br>
+ **Tournament** : Orchestrates launch and multi-round flow around the model: confirm → <code>start_first_round()</code> → score → loop <code>start_next_round()</code>/score with best-effort saves each round; optional description edit; <code>mark_finished()</code> + final save + recap. Separate loop to view/edit/clear description.

## Utilities
+ **Tournament Utilities** : Glue helpers: <code>as_model</code>/<code>as_dict</code>, timestamp formatting, slug + <code>generate_tournament_name</code>, and global stats (<code>participations_by_player</code>, <code>wins_by_player</code> (finished-only), <code>live_match_stats</code>) combined by <code>build_player_tournament_index</code> (works with dicts or models; can infer players from rounds if <code>players.json</code> is absent).
<br><br>
+ **Match Validators** : <code>is_valid_match_result_code('V'|'D'|'N'|'E')</code>, <code>is_valid_match_result_label('victoire'|'défaite'|'nul'|'exempt')</code>.
  <br><br>
+ **Player Validators** : <code>is_valid_birthdate(YYYY-MM-DD, past, 1915..current)</code>, <code>is_valid_name (letters+accents/' -)</code>, <code>is_valid_id</code> (2 letters + 5 digits). Reused across the app for consistent checks.



### 📊 Stats & Leaderboards
+ **Global players table** (main menu) combines:
  + Matchs — total matches across all tournaments/rounds. 
  + Points — sum of scored points (win=1, draw=0.5, loss=0). 
  + Tournois — participations (on roster or inferred from rounds). 
  + Victoires — tournament wins **including ties**.
+ **Tournament summary (end):** final standings + per-round result grid.

### 🔒 Reliability & Error Handling
+ **Persistence after critical ops**
  + On tournament creation/launch. 
  + After each confirmed round. 
  + On resume/quit flows. 
  + Menus re-load from disk to avoid stale state.

+ **Happy & sad paths handled**
  + Validators prevent bad inputs. 
  + Try/except blocks around I/O and parsing. 
  + Clear, user-friendly error messages and confirmations. 
  + Safe cancels: pressing Enter on an optional edit **does nothing** (no accidental mutations).

### 🧪 Linting & Code Style
- Run flake8 manually:

    ```bash
    flake8 --max-line-length=119 --format=html --htmldir=flake8_rapport
    ```

- Run linting checks on all Python files (.py) within the current directory (.) and all subdirectories, recursively.

  ```bash
  flake8 .
  ```

## 📋 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2025 Sierra Ripoche

If you use or modify this software, you must keep the above copyright notice
and this license text in copies or substantial portions of the software.

# Author
Sierra Ripoche
