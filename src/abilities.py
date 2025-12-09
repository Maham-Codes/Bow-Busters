# core/abilities.py
import random
import pygame
from src.prefab import Prefab

class AbilityManager:
    """
    Manages player abilities (cooldowns, active effects).
    Crystal Spike Barrier blocks several tiles for a short duration,
    adds visual spike prefabs, and schedules their unblocking.
    """

    def __init__(self, game):
        self.game = game

        # cooldown settings (seconds)
        self.cooldowns = {
            "crystal_spike": 20.0
        }

        # cooldown timers remaining (0 = ready)
        self.cooldown_timers = {k: 0.0 for k in self.cooldowns.keys()}

        # active effects: list of dicts {name, time_left, tiles, prefabs}
        self.active = []

        # ability parameters
        self.spike_count = 8         # how many spikes to place
        self.spike_duration = 5.0    # how long they stay (seconds)

    def update(self, delta):
        # decrement cooldown timers
        for k in list(self.cooldown_timers.keys()):
            if self.cooldown_timers[k] > 0:
                self.cooldown_timers[k] = max(0.0, self.cooldown_timers[k] - delta)

        # update active effects
        for effect in list(self.active):
            effect["time_left"] -= delta
            if effect["time_left"] <= 0:
                self._end_effect(effect)
                self.active.remove(effect)

    def use(self, name):
        """
        Attempt to use the named ability.
        Returns True if used, False if on cooldown or invalid.
        """
        if name not in self.cooldowns:
            return False

        if self.cooldown_timers[name] > 0:
            return False

        # call specific ability
        if name == "crystal_spike":
            self._use_crystal_spike()
            self.cooldown_timers[name] = self.cooldowns[name]
            return True

        return False

    def _use_crystal_spike(self):
        level = self.game.level
        collision = level.collision
        tile_size = collision.tile_size

        chosen = set()

        # ------------------------------
        # 1) PRIORITY: Place spikes under enemies
        # ------------------------------
        enemies = list(self.game.wave.enemies)
        random.shuffle(enemies)

        for enemy in enemies:
            if len(chosen) >= self.spike_count:
                break

            ex = enemy.rect.x - (enemy.rect.x % tile_size)
            ey = enemy.rect.y - (enemy.rect.y % tile_size)

            if not collision.point_blocked(ex, ey):
                chosen.add((ex, ey))

        # ------------------------------
        # 2) SECOND PRIORITY: block the tile the enemy is moving TOWARD
        # ------------------------------
        for enemy in enemies:
            if len(chosen) >= self.spike_count:
                break

            target = enemy.target
            if target is not None:
                tx, ty = target
                tx = tx - (tx % tile_size)
                ty = ty - (ty % tile_size)

                if not collision.point_blocked(tx, ty):
                    chosen.add((tx, ty))

        # ------------------------------
        # 3) LAST PRIORITY: fallback to random tiles
        # ------------------------------
        if len(chosen) < self.spike_count:
            max_x_tiles = collision.width
            max_y_tiles = collision.height

            attempts = 200
            while len(chosen) < self.spike_count and attempts > 0:
                attempts -= 1
                tx = random.randint(0, max_x_tiles - 1)
                ty = random.randint(0, max_y_tiles - 1)
                px = tx * tile_size
                py = ty * tile_size

                if not collision.point_blocked(px, py):
                    chosen.add((px, py))

        # If still empty somehow, stop
        if len(chosen) == 0:
            return

        # ------------------------------
        # Create spike prefabs & block tiles
        # ------------------------------
        spike_prefabs = []

        for (px, py) in chosen:
            # Block correct tile node
            collision.block_point(px, py)

            # Add visible spike prefab
            prefab = Prefab("crystal_spike", px, py)
            level.prefabs.add(prefab)
            spike_prefabs.append(prefab)

        # ------------------------------
        # Register the effect for cleanup
        # ------------------------------
        self.active.append({
            "name": "crystal_spike",
            "time_left": self.spike_duration,
            "tiles": list(chosen),
            "prefabs": spike_prefabs
        })


    def _end_effect(self, effect):
        # when effect ends, unblock tiles and remove prefabs
        level = self.game.level
        collision = level.collision

        for (px, py) in effect["tiles"]:
            collision.unblock_point(px, py)

        # remove visuals
        for p in effect["prefabs"]:
            try:
                p.kill()
            except:
                pass

    # helpers for UI/cooldown display
    def get_cooldown(self, name):
        return self.cooldown_timers.get(name, 0.0)

    def is_ready(self, name):
        return self.get_cooldown(name) <= 0.0
