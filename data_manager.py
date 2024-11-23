import os
import json

FILE_PATH = "players.json"

def load_players():
    """Carga los jugadores desde un archivo JSON"""
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    return {}

def save_players(players):
    """Guarda los jugadores en un archivo JSON"""
    with open(FILE_PATH, 'w') as file:
        json.dump(players, file, indent=4)
