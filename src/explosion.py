import math
import random
import pygame
from src.prefab import Prefab


class Explosion(Prefab):
    # represents an explosion effect that damages nearby enemies
    # uses an animated sprite and calculates damage based on distance

    def  __init__(self, game, position, radius, damage):
       # creates an explosion that damages all enemies in its radius
       # damage falls off with distance from the center
       # args: game - reference to the main game object
       #       position - coordinates where explosion happens
       #       radius - how far the explosion reaches
       #       damage - max damage dealt at the center
       super().__init__("attack_explosion", position[0], position[1])
       self.rect.center = position

       # calculate the maximum distance squared for efficiency
       max_magnitude = radius ** 2

       # check every enemy to see if theyre in blast radius
       for enemy in game.wave.enemies:
            # calculate distance squared to avoid expensive sqrt
            dx = enemy.rect.centerx-self.rect.centerx
            dy = enemy.rect.centery-self.rect.centery
            magnitude = (dx ** 2) + (dy ** 2)

            # if enemy is close enough deal damage that decreases with distance
            if magnitude < max_magnitude:
                enemy.take_damage(damage * (1 - (magnitude / max_magnitude)))

    def update(self, delta):
        # runs every frame to animate the explosion sprite
        # args: delta - time in seconds since last frame
        super().update_animation(delta)