from pygame.sprite import Sprite
from pygame.rect import Rect
import pygame


class Prefab(Sprite):
     # Used to cache config files { name, config }
    Cache = { }
    def __init__(self, name, x, y):
        """ 
        Constructor. 
        
        Args:
            name (str): The config file name.
            x (int): The top left x coordinate.
            y (int): The top left y coordinate.

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