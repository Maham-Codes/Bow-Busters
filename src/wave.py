import pygame
import random
from core.enemy import Enemy


class Wave:
    def __init__(self, game, number):
        self.game = game
        self.number = number
        self.started = False
        self.done = False
        self.enemies = pygame.sprite.Group()
        self.spawn_time = 0
        self.spawn_gap = 3 - (number ** 0.6)
        self.spawn_count_small = int(number ** 2.5)
        self.spawn_count_medium = int(number ** 2 - number)
        self.spawn_count_large = int(number ** 1.7 - 4)

    def update(self, delta):
        self.enemies.update(delta)
