"""CSV load/save with error handling (missing or malformed files never crash the program)."""
import csv
import os
from models import Player, PLAYER_FIELDS


# Read the CSV; returns (players, skipped_rows)
def load_players(filepath):
    players = []
    skipped = 0
    try:
        with open(filepath, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    player = Player.from_dict(row)
                    players.append(player)
                except (KeyError, ValueError, TypeError, AttributeError):
                    skipped += 1
    except (FileNotFoundError, OSError):
        return ([], 0)
    return (players, skipped)


# Write the CSV; returns True on success, False on OSError
def save_players(filepath, players):
    try:
        folder = os.path.dirname(filepath)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=PLAYER_FIELDS)
            writer.writeheader()
            for player in players:
                writer.writerow(player.to_dict())
        return True
    except OSError:
        return False


