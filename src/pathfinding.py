from collections import Counter 
heat = Counter() 

import random


class Pathfinding:
    """
    Manages pathfinding and path selection for enemies.
    ...
    """

    def __init__(self, game, collision):
        """
        Constructor.
        ...
        """
        self.game = game
        self.collision = collision
        self.pool = []
        self.partials = 0

    def precompute(self, count):
        """
        Starts precomputing a given number of paths.
        ...
        """
        for i in range(count):
            self.pool.append(Path(self, self.find_start()))
            
            
    def find_start(self):
        """
        Finds a start point for a full length path.
        ...
        """
        cells = self.collision.height
        x = self.game.window.resolution[0]
        attempts = 100
        
        while attempts > 0:
            attempts -= 1

            y = random.randint(0, cells - 1) * self.collision.tile_size
            if not self.collision.point_blocked(x - 32, y):
                return (x, y)

        # No start found, supply a default.
        return (x, random.randint(0, cells - 1) * self.collision.tile_size)

    
    def get_point_usage(self, point):
        """
        Returns the number of existing paths that use the given point.
        ...
        """
        total = 0

        for path in self.pool:
            if path.done and point in path.points:
                total += 1

        return total