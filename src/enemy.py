from pygame.sprite import Sprite
from src.prefab import Prefab
from src.pathfinding import heat

import pygame
import math
import random
import heapq 

class Enemy(Prefab):
    # represents a single enemy that follows paths to reach the goal
    # controlled by ai using pathfinding and gets tougher each wave

    def __init__(self, game, name, x, y):
        # creates a new enemy and assigns it a path to follow
        # scales stats based on wave number to increase difficulty
        super().__init__(name, x, y)

        self.game = game
        self.path = game.level.pathfinding.get_path()
        self.target = self.path.start
        self.rect.topleft = self.target
        self.x = self.target[0]
        self.y = self.target[1]

        
        # fallback values if prefab doesnt define speed or health
        if not hasattr(self, 'speed'):
            self.speed = 150
        if not hasattr(self, 'health'):
            self.health = 100

        self.speed += random.randint(-25, 25)

        # make enemies faster in later waves for increased difficulty
        self.speed += random.randint(0, self.game.wave.number * 2)
        
        # save base health then scale it exponentially based on wave number
        self.max_health = self.health 
        self.health = self.health ** (1 + (self.game.wave.number / 35))
        self.max_health = self.health

        # max heap to track speed modifiers like slows and speed boosts
        # stores negative multiplier so python min heap acts like max heap
        # format is [(-multiplier, time_remaining, modifier_id)]
        self.speed_modifiers = [(-1.0, 0.0, 'base')] 
        self.effective_speed = self.speed * 1.0
        self.surged = False
        self.surge_multiplier = 2.5
        self.surge_duration = 2.5
 

    def apply_speed_modifier(self, multiplier, duration, source_id):
        # adds a new speed effect to the enemy like slow or speed boost
        # replaces any existing effect from the same source
        # args: multiplier - how much to multiply speed by
        #       duration - how long the effect lasts in seconds
        #       source_id - unique name for this effect source
        # remove old modifier from this source if it exists
        new_heap = [m for m in self.speed_modifiers if m[2] != source_id]
        self.speed_modifiers = new_heap
        heapq.heapify(self.speed_modifiers) # Re-heapify after removal

        # Push the new modifier (negative multiplier for Max-Heap)
        heapq.heappush(self.speed_modifiers, (-multiplier, duration, source_id))

    def _manage_speed_modifiers(self, delta):
        # updates all active speed effects and applies the strongest one
        # removes expired effects and recalculates current speed
        # args: delta - time in seconds since last frame
        new_heap = []
        
        # decrease the time remaining on all active speed effects
        for neg_m, dur, sid in self.speed_modifiers:
            new_dur = dur - delta
            if new_dur > 0:
                heapq.heappush(new_heap, (neg_m, new_dur, sid))
                
        # save the updated heap
        self.speed_modifiers = new_heap
        
        # apply the strongest speed modifier from the top of the heap
        if self.speed_modifiers:
            dominant_multiplier = -self.speed_modifiers[0][0]
            self.effective_speed = self.speed * dominant_multiplier
        else:
            # if no modifiers exist add back the base speed
            self.apply_speed_modifier(1.0, 0.0, 'base')
            self.effective_speed = self.speed * 1.0


    def update(self, delta):
        # runs every frame to move the enemy and update effects
        # args: delta - time in seconds since last frame
        # check if our target got blocked by a new turret and find alternate path
        try:
            target = self.target
            if target and self.game.level.collision.point_blocked(target[0], target[1]):
                self.path, self.target = self.game.level.pathfinding.get_partial_path(target)
        except Exception:
            pass
            
        # update all speed modifiers and calculate current speed
        self._manage_speed_modifiers(delta)

        self.update_position(delta)

    def update_position(self, delta):
        # moves the enemy toward its current target waypoint
        # tracks tile changes for heat map and applies speed modifiers
        # args: delta - time in seconds since last frameted on
        tile_size = self.game.level.collision.tile_size
        old_tile = (int(self.rect.x) - (int(self.rect.x) % tile_size),
                    int(self.rect.y) - (int(self.rect.y) % tile_size))

        current = self.rect.topleft
        target = self.target

        # calculate direction and distance to next waypoint
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # use speed from the max heap system
        effective_speed = self.effective_speed 

        max_move = delta * effective_speed

        # if we can reach the target this frame just jump to it target this frame just jump to it
        if distance < max_move:
            self.x = target[0]
            self.y = target[1]
            self.reached_target()
        else:
            # move partway toward the target based on speed
            proportion = max_move / distance
            self.x += dx * proportion
            self.y += dy * proportion

        self.rect.x = self.x
        self.rect.y = self.y

        # check which tile were on now
        new_tile = (int(self.rect.x) - (int(self.rect.x) % tile_size),
                    int(self.rect.y) - (int(self.rect.y) % tile_size))

        # update heat map when enemy moves to a new tile
        if new_tile != old_tile:
            try:
                heat[new_tile] += 1
            except Exception:
                pass


    def reached_target(self):
        # called when enemy arrives at a waypoint
        # gets the next waypoint or ends the game if they reached the goal
        if not self.path.done:

            # check if the path got blocked while we were movinge we were moving
            if self.target[0] < self.game.window.resolution[0] and self.path.points is not None and self.target in self.path.points:
                self.path, self.target = self.game.level.pathfinding.get_partial_path(self.target)

            return

        # get the next waypoint in the path
        self.target = self.path.next(self.target)
        if not self.target:
            # enemy reached the goal remove a life
            self.game.level.lives -= 1
            if(self.game.level.lives == 0):
                self.game.menu.show_lose_screen()
                
            self.kill()

    def take_damage(self, damage):
        # reduces enemy health and triggers surge boost at half health
        # kills the enemy if health drops to zero or below
        # args: damage - how much health to remove
        self.health -= damage

        # give speed boost when enemy drops below half health for first time
        if not self.surged and self.health <= self.max_health / 2:
            self.apply_speed_modifier(
                self.surge_multiplier, 
                self.surge_duration, 
                'surge'
            )
            self.surged = True
        
        if self.health <= 0:
            self.kill()

    def kill(self):
        # removes the enemy from the game
        # gives money reward if enemy died on map instead of escaping
        super().kill()

        self.game.wave.enemy_killed()  
        
        # only give money if enemy died on the map not at the goal
        if self.rect.x > 1:       
            self.game.level.money += self.money