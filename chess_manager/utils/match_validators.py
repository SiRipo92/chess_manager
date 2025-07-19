from chess_manager.constants.match_results import MATCH_RESULT_CODES, VALID_RESULT_LABELS


def is_valid_match_result_code(code: str) -> bool:
    """
    Vérifie si l’abréviation entrée par l'utilisateur est valide (ex : 'V', 'D', 'N').
    """
    return code.strip().upper() in MATCH_RESULT_CODES


def is_valid_match_result_label(label: str) -> bool:
    """
    Vérifie si le résultat normalisé est valide (ex : 'victoire', 'défaite', 'nul').
    """
    return label.strip().lower() in VALID_RESULT_LABELS
