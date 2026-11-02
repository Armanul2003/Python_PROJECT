"""NumPy calculations: 38-match projection, weighted score (np.dot), leaderboard and summary."""
import numpy as np
from models import STAT_FIELDS, WEIGHTS, MIN_APPEARANCES, TOTAL_MATCHDAYS


# Stats as a float NumPy vector (order = STAT_FIELDS)
def get_stat_array(player):
    return np.array([player.stats[field] for field in STAT_FIELDS], dtype=float)


# Position weights as a NumPy vector aligned with STAT_FIELDS
def get_weight_array(position):
    weights = WEIGHTS[position]
    return np.array([weights.get(field, 0) for field in STAT_FIELDS], dtype=float)


# Scale season totals to 38 matches: stat / appearances * 38
def project_stats(player):
    """Scale season totals to a full 38-match season (rate per appearance * 38)."""
    if player.appearances == 0:
        return {field: 0.0 for field in STAT_FIELDS}
    projected = get_stat_array(player) / player.appearances * TOTAL_MATCHDAYS
    return {field: round(float(value), 1) for field, value in zip(STAT_FIELDS, projected)}


# Weighted score = np.dot(projected stats, position weights)
def calculate_score(player):
    """Weighted score of the projected stats using a NumPy dot product."""
    if player.appearances == 0:
        return 0.0
    projected = get_stat_array(player) / player.appearances * TOTAL_MATCHDAYS
    score = np.dot(projected, get_weight_array(player.position))
    return round(float(score), 1)


# Keep qualified players (>= MIN_APPEARANCES), score and rank them
def build_leaderboard(players, position):
    rows = []
    for player in players:
        if player.position != position or player.appearances < MIN_APPEARANCES:
            continue
        projected = project_stats(player)
        parts = [f"{field}={projected[field]}" for field in WEIGHTS[position]]
        rows.append({
            "rank": 0,
            "player_id": player.player_id,
            "name": player.name,
            "team": player.team,
            "appearances": player.appearances,
            "projected": ", ".join(parts),
            "score": calculate_score(player),
        })

    rows.sort(key=lambda row: -row["score"])
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    return rows


# Leaderboard summary statistics using NumPy
def summarize(rows):
    """Count, average, highest and lowest score of a leaderboard (NumPy)."""
    if not rows:
        return {"count": 0, "average": 0.0, "highest": 0.0, "lowest": 0.0}
    scores = np.array([row["score"] for row in rows], dtype=float)
    return {"count": int(scores.size), "average": round(float(scores.mean()), 1),
            "highest": round(float(scores.max()), 1), "lowest": round(float(scores.min()), 1)}
