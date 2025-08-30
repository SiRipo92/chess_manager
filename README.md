# ♟️ Chess Tournament Manager (Offline CLI - Python)
<br>[![Flake8](https://github.com/SiRipo92/chess_manager/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/SiRipo92/chess_manager/actions/workflows/lint.yml)
<br>[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
<p>This project is an offline, console-based chess tournament manager built with Python using the MVC (Model-View-Controller) design pattern. It allows club managers to create and run chess tournaments, track players, scores, and generate tournament reports.
## 📁 Project Structure

```bash
chess_manager/                  # Project root
├── chess_manager/             # Internal package containing core logic
│   ├── controllers/           # Business logic (managing players, tournaments, rounds)
│   ├── models/                # Data models (Player, Match, Round, Tournament)
│   ├── views/                 # CLI views using `questionary` and `rich`
│   ├── constants/             # Centralized constants (labels, validation rules, mappings)
│   ├── utils/                 # Helper/validator functions for field inputs
│
├── repositories/              # Persistence layer for loading/saving JSON files
├── data/                      # Directory containing JSON data files
│   ├── players/
│   │   ├── players.json       # JSON data file with enrolled players
│   ├── tournaments/
│   │   ├── tournaments.json   # TOURNAMENT REPOSITORY - Persistent memory/json of all tournaments played
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
+ **Models** 
<br> Player, Match, Round, Tournament (with lifecycle helpers: mark_launched, mark_finished, start_first_round, start_next_round, etc.).
Tournament.status is derived: En attente → En cours → Terminé.

+ **Controllers**
<br> PlayerController — CRU, search, edit flow (per-field confirmation), JSON persistence.
TournamentController — launching rounds, entering/correcting results, provisional standings, persistence.

+ **Views**
<br> player_views and round_views render Rich tables and drive interactive Questionary prompts. Views also explain what’s happening (what changed, what’s left, summaries, confirmations).

+ **Utilities**
<br> player_validators (names, dates, national-ID), tournament_utils (progress %, winners/participations/matches/points aggregation).

+ **Repositories**
<br> Thin wrappers around JSON (load/save; tolerant of dict vs. model instances).


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
  - ```

## 📋 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2025 Sierra Ripoche

If you use or modify this software, you must keep the above copyright notice
and this license text in copies or substantial portions of the software.

# Author
Sierra Ripoche
