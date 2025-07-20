import os

BASE_PLAYER_DIRECTORY = "data/players"
PLAYER_FILENAME = "players.json"

def get_player_filepath_for_city(city: str) -> str:
    """
    Retourne le chemin complet du fichier players.json pour une ville donnée.

    Exemple :
        city='Nanterre' ➜ 'data/players/Nanterre/players.json'
    """
    sanitized_city = city.strip().title()
    return os.path.join(BASE_PLAYER_DIRECTORY, sanitized_city, PLAYER_FILENAME)