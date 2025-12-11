import random
import pygame
from src.prefab import Prefab
from src.pathfinding import heat   # heatmap (Counter)

class AbilityManager:

    def __init__(self, game):
        self.game = game

        # cooldown settings (seconds)
        self.cooldowns = {
            "crystal_spike": 20.0,
            "hot_zone": 15.0,
            "ice_zone": 18.0
        }

        # cooldown timers remaining (0 = ready)
        self.cooldown_timers = {k: 0.0 for k in self.cooldowns.keys()}

        # active effects: list of dicts {name, time_left, tiles, prefabs}
        self.active = []

        # ability parameters
        self.spike_count = 8         # how many spikes to place
        self.spike_duration = 5.0    # how long they stay (seconds)

        # Hot Zone parameters
        self.hot_zone_duration = 6.0

        # Ice Zone parameters
        self.ice_zone_duration = 8.0
        self.ice_tile_count = 6         # how many top-heat tiles to slow
        self.ice_slow_multiplier = 0.5  # speed multiplier while on ice tiles (0.5 means 50% speed)

        # Debug / visualization
        self.show_heat_overlay = False