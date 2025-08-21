import questionary
from typing import Optional

def prompt_result_for_match() -> Optional[str]:
    """
    Demande un résultat pour le joueur 1 du match.
    Retourne 'V' / 'D' / 'N' ou None si l’utilisateur annule.
    """
    return questionary.select(
        "Résultat pour le joueur 1 :",
        choices=[
            {"name": "Victoire (V)", "value": "V"},
            {"name": "Défaite (D)", "value": "D"},
            {"name": "Match nul (N)", "value": "N"},
            {"name": "Annuler", "value": None},
        ],
    ).ask()
