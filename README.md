# ♟️ Chess Tournament Manager (Offline CLI - Python)

This project is an offline, console-based chess tournament manager built with Python using the MVC (Model-View-Controller) design pattern. It allows club managers to create and run chess tournaments, track players, scores, and generate tournament reports.

## 📁 Project Structure

```bash
chess_manager/         # Project namespace
├── chess_maanager/    # Microservice package for the chess management tool 
    ├── models/            # Contains Player, Match, Round, Tournament models
    ├── controllers/       # Application logic (starting tournaments, progressing rounds)
    ├── views/             # Text-based CLI interface using questionary and rich
    ├── tests/             # Unit tests with nose2 and coverage
    ├── main.py            # Application entry point
├── repositories/      # Responsible for loading/saving data (JSON)
├── data/              # Contains .json files for persistence
├── main.py            # Application entry point
├── requirements.txt   # List of Python dependencies
├── .gitignore
├── flake8_rapport/    # Linting report folder
├── setup.cfg          # Setup configuration for nose, coverage and flake8 linting
├── .github/           # Automated workflows for linting and testing
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
### Running Tests and Coverage
This project uses nose2 for unit testing and coverage for code coverage analysis.

1. Install test dependencies
```bash
pip install -r requirements.txt
pip install nose2 coverage
```
2. Run all unit tests
```bash
nose2 -v
```
3. View coverage report in terminal
```bash
coverage report -m
```
4. Custom .coverage file location
```bash
coverage report -m
```

## 📋 License
MIT License or School Submission — to be specified.
