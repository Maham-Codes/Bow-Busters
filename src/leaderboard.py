# local leaderboard system for saving high scores
# stores data in json files instead of using online services
# keeps track of player names scores and waves reached

import json
import os

# save leaderboard files in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCORES_FILE = os.path.join(BASE_DIR, "leaderboard_local.json")
META_FILE = os.path.join(BASE_DIR, "leaderboard_meta.json")


class Leaderboard:
    # manages the high score leaderboard stored in a local json file
    # tracks player names and loads saves scores automatically

    def __init__(self):
        # sets up the leaderboard and loads saved data from files
        self.entries = []
        self.last_player = "player1"
        # load the last player name and all scores from disk
        self._load_meta()
        self.retrieve()

    # internal helper functions for loading and saving data
    def _load_meta(self):
        # loads the last player name from the meta file
        try:
            if os.path.exists(META_FILE):
                with open(META_FILE, "r") as f:
                    meta = json.load(f)
                loaded_player = meta.get("last_player", None)
                if loaded_player and str(loaded_player).strip() != "":
                    self.last_player = str(loaded_player).strip()
                # if no valid name found keep using default player1
        except Exception as e:
            print("Warning: failed loading leaderboard meta:", e)
            # on error keep default player1

    def _save_meta(self):
        # saves the current player name to the meta file
        try:
            with open(META_FILE, "w") as f:
                json.dump({"last_player": self.last_player}, f, indent=4)
        except Exception as e:
            print("Warning: failed saving leaderboard meta:", e)

    # public functions that other parts of the game can use
    def retrieve(self):
        # loads all high scores from the json file
        # sorts them by score from highest to lowest
        try:
            if not os.path.exists(SCORES_FILE):
                self.entries = []
                return

            with open(SCORES_FILE, "r") as f:
                data = json.load(f)

            # make sure the file contains a list not something else
            if not isinstance(data, list):
                print("Warning: leaderboard data is not a list, resetting")
                self.entries = []
                return

            self.entries = [LeaderboardEntry(d) for d in data if isinstance(d, dict)]
            self.entries.sort(key=lambda e: e.score, reverse=True)

        except Exception as e:
            print("Error loading leaderboard:", e)
            self.entries = []

    def add(self, level, name, score, wave):
        # adds a new high score entry to the leaderboard
        # keeps only the top 20 scores and saves to file
        # args: level - which level this score is from
        #       name - player name
        #       score - points earned
        #       wave - how many waves the player survived
        try:
            new_entry = {"level": str(level), "name": str(name), "score": int(score), "wave": int(wave)}

            # load current scores safely
            current = []
            if os.path.exists(SCORES_FILE):
                try:
                    with open(SCORES_FILE, "r") as f:
                        loaded = json.load(f)
                        # Ensure loaded data is a list
                        if isinstance(loaded, list):
                            current = loaded
                        else:
                            print("Warning: leaderboard file contains non-list data, resetting")
                            current = []
                except Exception:
                    current = []

            current.append(new_entry)
            # Keep top 20
            current = sorted(current, key=lambda e: int(e.get("score", 0)) if isinstance(e, dict) else 0, reverse=True)[:20]

            with open(SCORES_FILE, "w") as f:
                json.dump(current, f, indent=4)

            # Update internal entries
            self.entries = [LeaderboardEntry(d) for d in current]

        except Exception as e:
            print("Error updating leaderboard:", e)

    # helper functions used by other parts of the game
    def set_player(self, name):
        # updates the current player name
        # if name is empty just returns the current player name
        # args: name - new player name to save
        # returns: the player name being used
        try:
            if name and str(name).strip() != "":
                self.last_player = str(name).strip()
                self._save_meta()
            # if empty name dont change anything just return current name
        except Exception as e:
            print("Warning: set_player failed:", e)
        return self.last_player
    
    def get_current_player(self):
        # gets the name of the player currently being tracked
        # returns: current player name
        return self.last_player

    def add_score(self, score, level="default", wave=0):
        # saves the players score using the current player name
        # args: score - points to save
        #       level - which level this is from
        #       wave - wave number reached
        try:
            self.add(level, self.last_player, int(score), wave)
        except Exception as e:
            print("Warning: add_score failed:", e)

    def get_top_scores(self, count=10):
        # gets the highest scores from the leaderboard
        # args: count - how many scores to return
        # returns: list of score dictionaries
        self.retrieve()
        out = []
        for e in self.entries[:count]:
            out.append({"name": e.name, "score": e.score, "level": e.level, "wave": e.wave})
        return out


class LeaderboardEntry:
    # represents one entry in the high score leaderboard
    # stores player name score level and wave number

    def __init__(self, data):
        # creates a leaderboard entry from saved data
        # handles missing or corrupted data gracefully
        # args: data - dictionary with score information
        # make sure data is a dict use defaults if not
        if not isinstance(data, dict):
            data = {}
        
        # extract values safely with fallbacks if keys are missing
        self.level = str(data.get("level", "default"))
        self.name = str(data.get("name", "Player"))
        try:
            self.score = int(data.get("score", 0))
        except (ValueError, TypeError):
            self.score = 0
        try:
            self.wave = int(data.get("wave", 0))
        except (ValueError, TypeError):
            self.wave = 0
