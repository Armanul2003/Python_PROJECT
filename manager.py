"""PlayerManager: owns the player list and duplicate-check sets; coordinates all operations."""
import file_handler
import analysis
import validation
from models import Player, STAT_FIELDS, POSITIONS, TEAM_CODES


class PlayerManager:
    def __init__(self, players_file):
        self.players_file = players_file
        self.players = []
        self.player_ids = set()
        self.name_keys = set()

    # Load players from CSV; skip corrupted, duplicated or mismatched-ID rows
    def load_all(self):
        loaded_players, skipped = file_handler.load_players(self.players_file)
        self.players = []
        self.player_ids = set()
        self.name_keys = set()

        for player in loaded_players:
            expected_id = self.make_player_id(player.team, player.jersey)
            name_key = (player.name.lower(), player.team)
            if (player.player_id != expected_id or
                    player.player_id in self.player_ids or
                    name_key in self.name_keys):
                skipped += 1
            else:
                self.players.append(player)
                self.player_ids.add(player.player_id)
                self.name_keys.add(name_key)

        return f"Loaded {len(self.players)} players. Skipped {skipped} bad rows."

    # Write every player back to the CSV file (called after each change)
    def save_all(self):
        return file_handler.save_players(self.players_file, self.players)

    # Build an ID such as BAR-08 from team code and jersey number
    def make_player_id(self, team, jersey):
        return f"{TEAM_CODES[team]}-{jersey:02d}"

    # Live ID preview for the form; returns "" while input is incomplete/invalid
    def preview_player_id(self, team, jersey_text):
        if team not in TEAM_CODES:
            return ""
        try:
            jersey = validation.validate_jersey(jersey_text)
            return self.make_player_id(team, jersey)
        except ValueError:
            return ""

    # Validate input, reject duplicates (sets), add the player and save
    def create_player(self, name, team, jersey_text, position):
        name = validation.validate_name(name)
        team = validation.validate_choice(team, TEAM_CODES, "team")
        jersey = validation.validate_jersey(jersey_text)
        position = validation.validate_choice(position, POSITIONS, "position")
        player_id = self.make_player_id(team, jersey)
        validation.validate_no_duplicate(player_id, name, team, self.player_ids, self.name_keys)

        new_player = Player(player_id, name, team, jersey, position)
        self.players.append(new_player)
        self.player_ids.add(player_id)
        self.name_keys.add((name.lower(), team))
        self.save_all()
        return new_player

    # Linear search by player_id; returns None if not found
    def find_player(self, player_id):
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    # Remove a player and release its ID and name key from the sets
    def delete_player(self, player_id):
        player_id = validation.validate_existing_player_id(player_id, self.player_ids)
        player = self.find_player(player_id)
        if player is not None:
            self.players.remove(player)
            self.name_keys.discard((player.name.lower(), player.team))
        self.player_ids.discard(player_id)
        self.save_all()

    # Case-insensitive keyword search (ID/name/team) plus position filter
    def search_players(self, keyword, position="All"):
        kw = keyword.strip().lower()
        results = []
        for player in self.players:
            if position != "All" and player.position != position:
                continue
            if (kw == "" or
                    kw in player.player_id.lower() or
                    kw in player.name.lower() or
                    kw in player.team.lower()):
                results.append(player)
        return results

    # Validate 38-match limit and every stat, then add one appearance
    def add_matchday_stats(self, player_id, stat_texts):
        player_id = validation.validate_existing_player_id(player_id, self.player_ids)
        player = self.find_player(player_id)
        validation.validate_appearance_limit(player.appearances)
        new_stats = {}
        for field in STAT_FIELDS:
            new_stats[field] = validation.validate_stat(stat_texts[field], field)
        player.add_matchday(new_stats)
        self.save_all()
        return player

    def get_all_players(self):
        return self.players

    def get_team_names(self):
        return sorted(TEAM_CODES)

    def get_player_labels(self):
        labels = [f"{p.player_id} | {p.name}" for p in self.players]
        return sorted(labels)

    # Ranked rows for one position (delegates to analysis.py)
    def get_leaderboard(self, position):
        return analysis.build_leaderboard(self.players, position)

    # Count/average/highest/lowest score for one position
    def get_summary(self, position):
        return analysis.summarize(self.get_leaderboard(position))
