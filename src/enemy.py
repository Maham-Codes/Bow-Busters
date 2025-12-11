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
