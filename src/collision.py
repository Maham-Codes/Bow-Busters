import pygame
import random

class Collision:
    # manages collision detection using a grid of tiles
    # tracks which tiles are blocked by walls or turrets
    # used for checking turret placement pathfinding and projectile hits

    def __init__(self, level, resolution, tile_size):
        # sets up the collision grid system
        # args: level - reference to the current level
        #       resolution - screen width and height in pixels
        #       tile_size - how many pixels each collision tile covers
        self.level = level
        self.tile_size = tile_size
        self.width = resolution[0] // tile_size
        self.height = resolution[1] // tile_size
        self.blocked_tiles = []
        self.overlay = None

    def point_to_index(self, x, y):
        # converts x y coordinates into a single unique index number
        # makes it easy to store and lookup blocked tiles
        xIndex = x // self.tile_size
        yIndex = y // self.tile_size

        return (yIndex * 1000) + xIndex
    
    def point_blocked(self, x, y):
        # checks if a specific coordinate is blocked by an obstacle
        # args: x - horizontal position to check
        #       y - vertical position to check
        # returns: true if blocked false if clear
        return self.point_to_index(x, y) in self.blocked_tiles

    def block_point(self, x, y):
        # marks a specific coordinate as blocked
        # triggers path repair so enemies can find new routes
        # args: x - horizontal position to block
        #       y - vertical position to block
        index = self.point_to_index(x, y)

        if index not in self.blocked_tiles:
            self.blocked_tiles.append(index)
            self.overlay = None
            self.level.pathfinding.repair((x - (x % self.tile_size), y - (y % self.tile_size)))
            
    def unblock_point(self, x, y):
        # marks a specific coordinate as no longer blocked
        # called when a turret is removed or destroyed
        # args: x - horizontal position to unblock
        #       y - vertical position to unblock
        index = self.point_to_index(x, y)

        if index in self.blocked_tiles:
            self.blocked_tiles.remove(index)
            self.overlay = None
    
    def rect_blocked(self, x, y, width, height):
        # checks if any part of a rectangular area is blocked
        # used for checking if turrets can be placed in a spot
        # args: x - top left corner horizontal position
        #       y - top left corner vertical position
        #       width - how wide the rectangle is
        #       height - how tall the rectangle is
        # returns: true if any tile in the area is blocked false if all clear
        xOffset = x % self.tile_size
        yOffset = y % self.tile_size

        for xPos in range(x - xOffset, x + width, self.tile_size):
            for yPos in range(y - yOffset, y + height, self.tile_size):
                
                if self.point_blocked(xPos, yPos):
                    return True

        return False

    def block_rect(self, x, y, width, height):
        # marks an entire rectangular area as blocked
        # used when placing turrets or walls
        # args: x - top left corner horizontal position
        #       y - top left corner vertical position
        #       width - how wide the rectangle is
        #       height - how tall the rectangle is
        xOffset = x % self.tile_size
        yOffset = y % self.tile_size

        for xPos in range(x - xOffset, x + width - 2, self.tile_size):
            for yPos in range(y - yOffset, y + height - 2, self.tile_size):
                self.block_point(xPos, yPos)

    def unblock_rect(self, x, y, width, height):
        # marks an entire rectangular area as no longer blocked
        # used when removing turrets or walls
        # args: x - top left corner horizontal position
        #       y - top left corner vertical position
        #       width - how wide the rectangle is
        #       height - how tall the rectangle is
        xOffset = x % self.tile_size
        yOffset = y % self.tile_size

        for xPos in range(x - xOffset, x + width, self.tile_size):
            for yPos in range(y - yOffset, y + height, self.tile_size):
                
                self.unblock_point(xPos, yPos)

    


    

    
