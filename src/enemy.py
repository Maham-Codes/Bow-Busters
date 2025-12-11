from pygame.sprite import Sprite
from core.prefab import Prefab
#from core.pathfinding import heat

import pygame
import math
import random
import heapq 

class Enemy(Prefab):
    """ 
    A spawned enemy in the game. AI controlled. 
    """

    def __init__(self, game, name, x, y):
        """ 
        Constructor. 
        """
        super().__init__(name, x, y)

        self.game = game
        self.path = game.level.pathfinding.get_path()
        self.target = self.path.start
        self.rect.topleft = self.target
        self.x = self.target[0]
        self.y = self.target[1]

        
        # (Assuming a base speed of 150 and base health of 100 if Prefab fails)
        if not hasattr(self, 'speed'):
            self.speed = 150
        if not hasattr(self, 'health'):
            self.health = 100

        self.speed += random.randint(-25, 25)

        # Make the enemies tougher each round
        self.speed += random.randint(0, self.game.wave.number * 2)
        
        # SAVE MAX HEALTH BEFORE SCALING
        self.max_health = self.health 
        self.health = self.health ** (1 + (self.game.wave.number / 35))
        self.max_health = self.health # Update max_health after scaling

        # MAX-HEAP IMPLEMENTATION
        # Stores active speed modifiers as: [(-multiplier, duration_left, id)]
        # We negate the multiplier to simulate a Max-Heap (highest value goes to the top).
        self.speed_modifiers = [(-1.0, 0.0, 'base')] 
        self.effective_speed = self.speed * 1.0 # Current speed used for movement
        self.surged = False          # Flag to prevent multiple surges per life
        self.surge_multiplier = 2.5  # 250% speed
        self.surge_duration = 3.0    # Lasts 3 seconds
 
    def apply_speed_modifier(self, multiplier, duration, source_id):
        """
        Adds a new speed modifier to the heap.
        """
        # Remove any existing modifier from this source_id (allows refresh)
        new_heap = [m for m in self.speed_modifiers if m[2] != source_id]
        self.speed_modifiers = new_heap
        heapq.heapify(self.speed_modifiers) # Re-heapify after removal

        # Push the new modifier (negative multiplier for Max-Heap)
        heapq.heappush(self.speed_modifiers, (-multiplier, duration, source_id))

    def _manage_speed_modifiers(self, delta):
        """
        Decays modifiers and recalculates effective speed from the Max-Heap.
        """
        new_heap = []
        
        # Decay the duration of all active modifiers
        for neg_m, dur, sid in self.speed_modifiers:
            new_dur = dur - delta
            if new_dur > 0:
                heapq.heappush(new_heap, (neg_m, new_dur, sid))
                
        # Update the heap
        self.speed_modifiers = new_heap
        
        # Determine the effective speed
        if self.speed_modifiers:
            dominant_multiplier = -self.speed_modifiers[0][0]
            self.effective_speed = self.speed * dominant_multiplier
        else:
            # Safety fallback: re-add base speed
            self.apply_speed_modifier(1.0, 0.0, 'base')
            self.effective_speed = self.speed * 1.0
    def update(self, delta):
        """ 
        Called once per frame. 
        """
        # quick check: if our current target tile became blocked, ask for partial path
        try:
            target = self.target
            if target and self.game.level.collision.point_blocked(target[0], target[1]):
                self.path, self.target = self.game.level.pathfinding.get_partial_path(target)
        except Exception:
            pass
            
        # CALL HEAP MANAGEMENT
        self._manage_speed_modifiers(delta)

        self.update_position(delta)

    #FIX: update_position MUST NOT be nested inside update
    def update_position(self, delta):
        # Track tile before movement (tile-aligned coordinates)
        tile_size = self.game.level.collision.tile_size
        old_tile = (int(self.rect.x) - (int(self.rect.x) % tile_size),
                    int(self.rect.y) - (int(self.rect.y) % tile_size))

        current = self.rect.topleft
        target = self.target

        dx = target[0] - current[0]
        dy = target[1] - current[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # REMOVED OLD SLOW CHECK - speed is managed by Max-Heap now
        # Determine slow multiplier for current tile (1.0 default)
        # try:
        #     slow_multiplier = self.game.ability_manager.is_tile_slow(old_tile)
        # except Exception:
        #     slow_multiplier = 1.0

        # effective movement speed uses the Max-Heap result
        effective_speed = self.effective_speed 

        max_move = delta * effective_speed

        # Snap to the target.
        if distance < max_move:
            self.x = target[0]
            self.y = target[1]
            self.reached_target()
        else:
            proportion = max_move / distance
            self.x += dx * proportion
            self.y += dy * proportion

        self.rect.x = self.x
        self.rect.y = self.y

        # Track tile after movement
        new_tile = (int(self.rect.x) - (int(self.rect.x) % tile_size),
                    int(self.rect.y) - (int(self.rect.y) % tile_size))

        # Increase heat if enemy stepped on a new tile
        if new_tile != old_tile:
            try:
                heat[new_tile] += 1
            except Exception:
                pass

