from pygame.sprite import Sprite
from pygame.rect import Rect
import pygame


class Prefab(Sprite):
     # Used to cache config files { name, config }
    Cache = { }
    def __init__(self, name, x, y):
        """ 
        Constructor

        """
        super().__init__()

        self.name = name
        self.config = self.load_config(name)
        self.apply_config(self.config)

        # Handle animations
        if hasattr(self, "anim_source"):
            self.anim_change_time = self.anim_rate
            self.anim_index = 0
            self.image = self.anim_source[0]

        # Handle sprite images
        if hasattr(self, "image"):
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
        else:
            self.rect = Rect(x, y, 32, 32)

def update_animation(self, delta):
        """
        Updates any spritesheet animation on prefab
        """
        if hasattr(self, "anim_source"):
            self.anim_change_time -= delta

            if self.anim_change_time < 0:
                self.anim_change_time += self.anim_rate
                
                self.anim_index += 1
                if self.anim_index == len(self.anim_source):
                    self.anim_index = 0

                    if not hasattr(self, "anim_loop") or not self.anim_loop:
                        self.kill()

                self.image = self.anim_source[self.anim_index]

