"""Constants (tuples, dicts) and the Player data model class."""
POSITIONS = ("GK", "DEF", "MID", "FWD")
STAT_FIELDS = ("goals", "assists", "clean_sheets", "saves", "tackles",
               "key_passes", "yellow_cards", "red_cards")
PLAYER_FIELDS = ("player_id", "name", "team", "jersey", "position",
                 "appearances") + STAT_FIELDS
TOTAL_MATCHDAYS = 38
MIN_APPEARANCES = 3
MAX_JERSEY = 99

# La Liga clubs and their 3-letter ID codes
TEAM_CODES = {
    "Athletic Club": "ATH", "Atletico Madrid": "ATM", "CA Osasuna": "OSA",
    "Celta Vigo": "CEL", "Deportivo Alaves": "ALA", "Elche": "ELC",
    "FC Barcelona": "BAR", "Getafe": "GET", "Girona": "GIR",
    "Levante": "LEV", "Mallorca": "MLL", "Rayo Vallecano": "RAY",
    "RCD Espanyol": "ESP", "Real Betis": "BET", "Real Madrid": "RMA",
    "Real Oviedo": "OVI", "Real Sociedad": "RSO", "Sevilla": "SEV",
    "Valencia": "VAL", "Villarreal": "VIL",
}

MAX_PER_MATCHDAY = {"goals": 8, "assists": 8, "clean_sheets": 1, "saves": 15,
                    "tackles": 15, "key_passes": 12, "yellow_cards": 2,
                    "red_cards": 1}

# Position-specific scoring weights (stats not listed have weight 0)
WEIGHTS = {
    "FWD": {"goals": 5, "assists": 4, "key_passes": 1, "yellow_cards": -1, "red_cards": -3},
    "MID": {"goals": 4, "assists": 5, "tackles": 2, "key_passes": 2,
            "yellow_cards": -1, "red_cards": -3},
    "DEF": {"goals": 4, "assists": 3, "clean_sheets": 5, "tackles": 4, "key_passes": 1,
            "yellow_cards": -1, "red_cards": -3},
    "GK":  {"clean_sheets": 5, "saves": 2, "yellow_cards": -1, "red_cards": -3},
}


class Player:

    def __init__(self, player_id, name, team, jersey, position, appearances=0, stats=None):
        self.player_id = player_id
        self.name = name
        self.team = team
        self.jersey = jersey
        self.position = position
        self.appearances = appearances
        if stats is None:
            stats = {field: 0 for field in STAT_FIELDS}
        self.stats = stats

    def add_matchday(self, new_stats):
        """Add one match day: new_stats is a dict {stat: int}. Updates the totals."""
        for field in STAT_FIELDS:
            self.stats[field] += new_stats[field]
        self.appearances += 1

    def to_dict(self):
        """Return a flat dictionary with the keys in PLAYER_FIELDS."""
        data = {"player_id": self.player_id, "name": self.name, "team": self.team,
                "jersey": self.jersey, "position": self.position,
                "appearances": self.appearances}
        data.update(self.stats)
        return data

    @staticmethod
    def from_dict(data):
        """Build a Player from a CSV row dictionary.
        Raises KeyError if a column is missing, ValueError if a value is invalid."""
        player_id = data["player_id"].strip()
        name = data["name"].strip()
        team = data["team"].strip()
        position = data["position"].strip()
        jersey = int(data["jersey"])
        appearances = int(data["appearances"])

        if not player_id or not name:
            raise ValueError("Missing player_id or name in CSV row")
        if team not in TEAM_CODES:
            raise ValueError("Unknown team in CSV row")
        if position not in POSITIONS:
            raise ValueError("Invalid position in CSV row")
        if jersey < 1 or jersey > MAX_JERSEY:
            raise ValueError("Invalid jersey number in CSV row")
        if appearances < 0 or appearances > TOTAL_MATCHDAYS:
            raise ValueError("Invalid appearances count in CSV row")

        stats = {}
        for field in STAT_FIELDS:
            value = int(data[field])
            if value < 0:
                raise ValueError("Negative stat in CSV row")
            stats[field] = value

        return Player(player_id, name, team, jersey, position, appearances, stats)
