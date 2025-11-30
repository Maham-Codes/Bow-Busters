import pygame
import random

class Collision:
    """ 
    Handles collision detection on a grid of tiles.
    Used for turret placement, projectiles and navigation.
    """

    def __init__(self, level, resolution, tile_size):
        """ 
        Constructor. 
        Args:
            game (Game): The game instance.
            resolution (int, int): The screen resolution.
            tile_size (int): The size (pixels) of each cached tile.

        """
        self.level = level
        self.tile_size = tile_size
        self.width = resolution[0] // tile_size
        self.height = resolution[1] // tile_size
        self.blocked_tiles = []
        self.overlay = None

    def point_to_index(self, x, y):
       
        xIndex = x // self.tile_size
        yIndex = y // self.tile_size

        return (yIndex * 1000) + xIndex
    
    def point_blocked(self, x, y):
        """
        Checks if the given point is blocked.

        Args:
            x (int): The x coordinate.
            y (int): The y coordinate.

        Returns:
            True if blocked, otherwise False.

        """
        return self.point_to_index(x, y) in self.blocked_tiles

    def block_point(self, x, y):
        """
        Makes the given point blocked.

        Args:
            x (int): The x coordinate.
            y (int): The y coordinate.

        """
        index = self.point_to_index(x, y)

        if index not in self.blocked_tiles:
            self.blocked_tiles.append(index)
            self.overlay = None
            self.level.pathfinding.repair((x - (x % self.tile_size), y - (y % self.tile_size)))
            