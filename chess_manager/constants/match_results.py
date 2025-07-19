# Abréviations acceptées par l'utilisateur pour enregistrer un résultat
MATCH_RESULT_CODES = {
    "V": "victoire",
    "D": "défaite",
    "N": "nul"
}

# Points associés à chaque résultat normalisé (utilisé pour le score)
MATCH_RESULT_POINTS = {
    "victoire": 1.0,
    "nul": 0.5,
    "défaite": 0.0
}

# Liste explicite des résultats normalisés autorisés
VALID_RESULT_LABELS = list(MATCH_RESULT_POINTS.keys())

# Optionnel : libellés affichables pour l'IHM ou la console (ex: en français ou traduits)
MATCH_RESULT_DISPLAY_NAMES = {
    "victoire": "Victoire",
    "défaite": "Défaite",
    "nul": "Match nul"
}
