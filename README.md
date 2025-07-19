# ♟️ Chess Tournament Manager (Offline CLI - Python)

This project is an offline, console-based chess tournament manager built with Python using the MVC (Model-View-Controller) design pattern. It allows club managers to create and run chess tournaments, track players, scores, and generate tournament reports.

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
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── .gitignore
├── flake8_rapport/            # HTML report output from flake8
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

## Features 
+ Player registration with national chess ID

+ Tournament creation (rounds, pairings, scoring)

+ Score tracking: wins, losses, draws, total points

+ Ranking and tournament results

+ Persistent data storage using JSON

+ Clean architecture with full MVC separation


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
MIT License or School Submission — to be specified.

# Author
Sierra Ripoche
