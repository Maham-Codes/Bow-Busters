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
        
        def update(self, delta):
        # decrement cooldown timers
        for k in list(self.cooldown_timers.keys()):
            if self.cooldown_timers[k] > 0:
                self.cooldown_timers[k] = max(0.0, self.cooldown_timers[k] - delta)

        # update active effects
        for effect in list(self.active):
            effect["time_left"] -= delta
            
            #  NEW: Check for Ice Zone effects and apply slow to enemies
            if effect["name"] == "ice_zone":
                self._apply_ice_slow(effect)

            if effect["time_left"] <= 0:
                self._end_effect(effect)
                try:
                    self.active.remove(effect)
                except ValueError:
                    pass

    # NEW HELPER METHOD TO PUSH SLOW TO ENEMIES
    def _apply_ice_slow(self, effect):
        """
        Applies the Ice Zone slow modifier to all enemies currently on affected tiles.
        """
        level = self.game.level
        tile_size = level.collision.tile_size
        
        # Get the required parameters from the effect
        multiplier = effect.get("multiplier", self.ice_slow_multiplier) 
        # Short duration forces the slow to be refreshed every frame the enemy stays in the zone.
        duration = 0.1 
        source_id = 'ice_zone_slow'
        
        # Iterate over all enemies
        for enemy in self.game.wave.enemies.sprites():
            # Calculate the tile the enemy is currently occupying (aligned coordinates)
            enemy_tile = (enemy.rect.x - (enemy.rect.x % tile_size),
                          enemy.rect.y - (enemy.rect.y % tile_size))
            
            # Check if the enemy is on one of the slow tiles
            if enemy_tile in effect.get("tiles", []):
                # Apply the slow modifier to the enemy's Max-Heap
                enemy.apply_speed_modifier(multiplier, duration, source_id)

    def use(self, name):
        """ 
        Uses an ability. 
        """
        if not self.is_ready(name):
            return False

        self.cooldown_timers[name] = self.cooldowns[name]
        
        if name == "crystal_spike":
            level = self.game.level
            collision = level.collision
            prefabs = []
            tiles = []

            # 8 top-heat tiles get spikes
            top_tiles = heat.most_common(self.spike_count)

            for (px, py), _ in top_tiles:
                # Add prefab
                p = Prefab("ability_spike", px, py)
                level.prefabs.add(p)
                prefabs.append(p)
                tiles.append((px, py))

                # Block point
                collision.block_point(px, py)

            self.active.append({
                "name": name,
                "time_left": self.spike_duration,
                "tiles": tiles,
                "prefabs": prefabs,
                "multiplier": 0.0 # blocks movement entirely
            })

            return True

        if name == "hot_zone":
            level = self.game.level
            collision = level.collision
            prefabs = []
            tiles = []

            # random tile placement for simplicity
            for i in range(10):
                px = random.randint(0, level.collision.width - 1) * level.collision.tile_size
                py = random.randint(0, level.collision.height - 1) * level.collision.tile_size
                
                # Check for critical path
                if level.pathfinding.is_critical((px, py)):
                    continue

                # Add prefab
                p = Prefab("ability_hot_zone", px, py)
                level.prefabs.add(p)
                prefabs.append(p)
                tiles.append((px, py))

                # Block point
                collision.block_point(px, py)


            self.active.append({
                "name": name,
                "time_left": self.hot_zone_duration,
                "tiles": tiles,
                "prefabs": prefabs,
                "damage_per_sec": 10
            })

            return True

        if name == "ice_zone":
            level = self.game.level
            tiles = []

            # 6 top-heat tiles get slowed
            top_tiles = heat.most_common(self.ice_tile_count)

            for (px, py), _ in top_tiles:
                tiles.append((px, py))

            self.active.append({
                "name": name,
                "time_left": self.ice_zone_duration,
                "tiles": tiles,
                "multiplier": self.ice_slow_multiplier
            })

            return True

        return False
   # ---------------- Effect cleanup ----------------
    def _end_effect(self, effect):
        level = self.game.level
        collision = level.collision

        # For blocking effects (spikes, hot_zone) — unblock tiles
        if effect["name"] in ("crystal_spike", "hot_zone"):
            for (px, py) in effect["tiles"]:
                try:
                    collision.unblock_point(px, py)
                except Exception:
                    pass

        # Remove prefabs that were placed for the effect
        for p in effect.get("prefabs", []):
            try:
                p.kill()
            except Exception:
                pass

    # ---------------- Helpers used by enemies / UI ----------------
    def get_cooldown(self, name):
        return self.cooldown_timers.get(name, 0.0)

    def is_ready(self, name):
        return self.get_cooldown(name) <= 0.0

    def toggle_heat_overlay(self):
        self.show_heat_overlay = not self.show_heat_overlay
