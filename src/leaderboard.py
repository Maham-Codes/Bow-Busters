###########################################
# Leaderboard 
###########################################

import json
import os

# Place files next to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCORES_FILE = os.path.join(BASE_DIR, "leaderboard_local.json")
META_FILE = os.path.join(BASE_DIR, "leaderboard_meta.json")


class Leaderboard:
    """
    Handles a leaderboard stored locally in a JSON file.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.entries = []
        self.last_player = "player1"  # Default to player1 if no player was ever set
        # Try to load meta (last player) and scores at startup
        self._load_meta()
        self.retrieve()

    # ---------- internal helpers ----------
    def _load_meta(self):
        try:
            if os.path.exists(META_FILE):
                with open(META_FILE, "r") as f:
                    meta = json.load(f)
                loaded_player = meta.get("last_player", None)
                if loaded_player and str(loaded_player).strip() != "":
                    self.last_player = str(loaded_player).strip()
                # If no valid player was loaded, keep default "player1"
        except Exception as e:
            print("Warning: failed loading leaderboard meta:", e)
            # Keep default "player1" on error

    def _save_meta(self):
        try:
            with open(META_FILE, "w") as f:
                json.dump({"last_player": self.last_player}, f, indent=4)
        except Exception as e:
            print("Warning: failed saving leaderboard meta:", e)

    # ---------- public API ----------
    def retrieve(self):
        """
        Loads leaderboard from local JSON file.
        """
        try:
            if not os.path.exists(SCORES_FILE):
                self.entries = []
                return

            with open(SCORES_FILE, "r") as f:
                data = json.load(f)

            # Ensure data is a list
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
        """
        Adds a new entry to the leaderboard and saves it locally.
        """
        try:
            new_entry = {"level": str(level), "name": str(name), "score": int(score), "wave": int(wave)}

            # Load current (safe)
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

    # ---------- convenience methods expected by game.py ----------
    def set_player(self, name):
        """
        Stores player name. If name is empty, returns the current player name.
        Returns the name in use.
        """
        try:
            if name and str(name).strip() != "":
                self.last_player = str(name).strip()
                self._save_meta()
            # else, return current last_player (don't change it)
        except Exception as e:
            print("Warning: set_player failed:", e)
        return self.last_player
    
    def get_current_player(self):
        """
        Returns the current player name being tracked.
        """
        return self.last_player

    def add_score(self, score, level="default", wave=0):
        """
        Saves player's score to local leaderboard file using last_player.
        """
        try:
            self.add(level, self.last_player, int(score), wave)
        except Exception as e:
            print("Warning: add_score failed:", e)

    def get_top_scores(self, count=10):
        """
        Returns top scores as a list of dict for printing.
        """
        self.retrieve()
        out = []
        for e in self.entries[:count]:
            out.append({"name": e.name, "score": e.score, "level": e.level, "wave": e.wave})
        return out


class LeaderboardEntry:
    """
    A single entry in the leaderboard.
    """

    def __init__(self, data):
        """
        Constructor.
        """
        # Ensure data is a dict, otherwise use defaults
        if not isinstance(data, dict):
            data = {}
        
        # Use .get to avoid KeyError if a file is malformed
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
