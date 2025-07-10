# ♟️ Chess Tournament Manager (Offline CLI - Python)

This project is an offline, console-based chess tournament manager built with Python using the MVC (Model-View-Controller) design pattern. It allows club managers to create and run chess tournaments, track players, scores, and generate tournament reports.

## 📁 Project Structure

```text
chess_manager/
├── models/            # Contains Player, Match, Round, Tournament models
├── controllers/       # Application logic (starting tournaments, progressing rounds)
├── views/             # Text-based CLI interface using questionary and rich
├── repositories/      # Responsible for loading/saving data (JSON)
├── data/              # Contains .json files for persistence
├── tests/             # Unit tests
├── main.py            # Application entry point
├── requirements.txt   # List of Python dependencies
├── .gitignore
├── flake8_rapport/    # Linting report folder

## 📦 Setup Instructions

1. Clone this repository
2. Set up the virtual environment and install dependencies:

    ```text
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
3. Run the program
    ```text
    python3 main.py
    ```

## Features 
+ Player registration with national chess ID</li>

+ Tournament creation (rounds, pairings, scoring)

+ Score tracking: wins, losses, draws, total points

+ Ranking and tournament results

+ Persistent data storage using JSON

+ Clean architecture with full MVC separation

### 🧪 Linting & Code Style
- Run flake8 manually:

    ```text
    flake8 --max-line-length=119 --format=html --htmldir=flake8_rapport
    ```

## 📋 License
MIT License or School Submission — to be specified.