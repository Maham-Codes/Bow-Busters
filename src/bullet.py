import math
import random
import pygame
from src.prefab import Prefab


class Bullet(Prefab):
    # represents a single projectile fired from a turret
    # flies in a straight line until it hits an enemy or obstacle

    def __init__(self, game, origin, target):
        # creates a new bullet that flies from origin toward target
        # calculates the velocity needed to reach the target
        # args: game - reference to the main game object
        #       origin - starting coordinates where the bullet spawns
        #       target - coordinates to aim at
        super().__init__("attack_bullet", origin[0], origin[1])
        self.game = game

        # calculate direction vector from origin to target
        dx = target[0] - origin[0]
        dy = target[1] - origin[1]

        # normalize the direction and apply speed with randomness
        magnitude = math.sqrt(dx ** 2 + dy ** 2)
        self.xSpeed = (dx / magnitude) * self.speed * random.randint(200, 500)
        self.ySpeed = (dy / magnitude) * self.speed * random.randint(200, 500)
        # calculate how long bullet should live based on distance
        self.life = magnitude / math.sqrt(self.xSpeed ** 2 + self.ySpeed ** 2)
        self.current_life = 0

        # rotate the bullet sprite to point in the direction its traveling
        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = origin

    def update(self, delta):
        # moves the bullet and checks for collisions every frame
        # args: delta - time in seconds since last frame for smooth movement
        self.rect.x += self.xSpeed * delta
        self.rect.y += self.ySpeed * delta

        # check if bullet has existed longer than its lifetime
        self.current_life += delta
        if self.life < self.current_life:
            self.kill()

        # check if bullet hit a wall or obstacle after a tiny delay
        if self.current_life > 0.03 and self.game.level.collision.point_blocked(self.rect.centerx, self.rect.centery):
            self.kill()

        # check for collisions with enemies using distance calculation
        for enemy in self.game.wave.enemies:
            # calculate distance between bullet and enemy center
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            sqrMagnitude = (dx ** 2) + (dy ** 2)

            # if distance is less than enemy radius we hit it
            if sqrMagnitude < (enemy.rect.width / 2) ** 2:
                enemy.take_damage(self.damage)
                self.kill()
                return
