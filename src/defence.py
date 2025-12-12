import pygame
import math
from pygame import Rect
from src.prefab import Prefab
from src.bullet import Bullet
from src.explosion import Explosion


class Defence(Prefab):
    # base class for all turrets that players can build
    # handles targeting shooting and rotating to face enemies
    
    def __init__(self, game, name, x, y):
        # creates a new turret at the specified position
        # args: game - reference to the main game object
        #       name - which type of turret to create
        #       x - horizontal position to place it
        #       y - vertical position to place it
        super().__init__(name, x, y)

        self.game = game
        self.fire_time = 0
        self.target = None

        if hasattr(self, "images"):
            self.image = self.images[0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

        if hasattr(self, "block"):
            self.game.level.collision.block_rect(x, y, self.rect.width, self.rect.height)

    def update(self, delta):
        # called every frame to update the turret
        # finds targets fires weapons and rotates to face enemies
        # args: delta - time in seconds since last frame
        # defences like walls dont attack so skip all the shooting logicp all the shooting logic
        if self.attack == "none":
            return

        target = self.get_target()

        self.fire_time += delta
        while self.fire_time >= self.attack_rate:
            self.fire_time -= self.attack_rate
        
            # make sure we have a target and its not exactly where we are to avoid math errors
            if target is not None and target != self.rect.center:
            
                # create the projectile based on attack typetile based on attack type
                if self.attack == "bullet":
                    self.game.bullets.add(Bullet(self.game, self.rect.center, target))
                elif self.attack == "explosion":
                    self.game.explosions.add(Explosion(self.game, target, self.explosion_radius, self.explosion_damage))

                # add muzzle flash effect if this turret has one
                if hasattr(self, "flash_offset"):
                    self.game.explosions.add(DefenceFlash(self.rect.center, target, self.flash_offset))

                # destroy turret after firing if its a one time use like mines
                if self.attack_rate <= 0:
                    self.kill()

            if self.attack_rate <= 0:
                break

        # make the turret sprite rotate to point at its target
        if self.rotate:
            center = self.rect.center

            # use default image if no target
            if self.target is None:
                self.image = self.images[0]
            else:
                # calculate angle to target and pick the right sprite frame
                dx = self.target.rect.center[0] - center[0]
                dy = self.target.rect.center[1] - center[1]
                angle = math.degrees(math.atan2(-dy, dx))
                if angle < 0:
                    angle += 360

                self.image = self.images[int(angle // 5)]

            self.rect = self.image.get_rect()
            self.rect.center = center

    def get_target(self):
        # tries to find an enemy within range to shoot at
        # keeps the same target if its still valid
        # returns: coordinates of target enemy or none if no valid targets
        if self.target is not None and self.is_target_suitable(self.target):
            return self.target.rect.center

        for t in self.game.wave.enemies:
            if self.is_target_suitable(t):
                self.target = t
                return t.rect.center

        return None

    def is_target_suitable(self, target):
        # checks if an enemy is within range and still alive
        # args: target - the enemy to check
        # returns: true if we can shoot it false if its too far or dead
        if target not in self.game.wave.enemies:
            return False

        a = target.rect.center
        b = self.rect.center
        sqrdist = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

        return sqrdist <= self.attack_range ** 2


class DefenceFlash(Prefab):
    # visual effect that shows when turrets fire
    # appears briefly near the turret muzzle

    def __init__(self, defence_position, target, offset):
        # creates a muzzle flash effect between the turret and target
        # args: defence_position - center of the turret
        #       target - center of what were shooting at
        #       offset - how far from turret center to place the flash
        dx = target[0] - defence_position[0]
        dy = target[1] - defence_position[1]
        magnitude = math.sqrt(dx * dx + dy * dy)
        dx *= (offset / magnitude)
        dy *= (offset / magnitude)

        super().__init__("defence_flash", defence_position[0] + dx - 16, defence_position[1] + dy - 16)

    def update(self, delta):
        # runs every frame to animate the flash effect
        # args: delta - time in seconds since last frame
        super().update_animation(delta)