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
    
    def update(self):
        """
        Continues generating paths.
        Run each frame.
        """
        for path in self.pool:
            if not path.done:
                path.search()
                return

    def get_path(self):
        """
        Picks a path for an enemy to follow.
        ...
        """
        attempts = 500
        while attempts > 0:
            attempts -= 1

            path = self.pool[random.randint(self.partials, len(self.pool) - 1)] 
            
            if path.done and path.start[0] >= self.game.window.resolution[0]:
                return path

        return self.get_partial_path(self.find_start())[0]
    
    def repair(self, point):
        """
        Called when a point has been blocked by a turret.
        ...
        """
        for path in self.pool:
            # Repair paths that contain the point.
            if path.done and point in path.points:
                path.repair(point)

            # Restart calculations of paths that may include the point.
            if not path.done and (point in path.open_set or point in path.closed_set):
                path.start_search()

    def get_partial_path(self, point):
        """
        Gets or creates a path that starts or passes through the given point.
        ...
        """
        # Try intersecting paths.
        for path in self.pool:
            if (path.done and point in path.points) or path.start == point:
                return path, point

        # Try paths that intersect with neighbours.
        for neighbour in self.pool[0].get_neighbours(point):
            for path in self.pool:
                if path.done and neighbour in path.points:
                    return path, neighbour

        # No suitable path, make a new one.
        path = Path(self, point)
        self.pool.insert(0, path)
        self.partials += 1
        return path, point

    def is_critical(self, point):
        """
        Works out if blocking the given point may make reaching the finish impossible.
        ...
        """
        for path in self.pool:
            if path.done and path.start[0] >= self.game.window.resolution[0] and point not in path.points:
                return False

        return True
 