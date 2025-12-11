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
 
class Path:
    """
    A single path across the level.
    Calculated using the A* pathfinding algorithm across multiple frames.
    Can be repaired if one of its points becomes blocked.
    """

    def __init__(self, pathfinding, start):
        """ 
        Constructor. 
        ...
        """
        self.start = start
        self.pathfinding = pathfinding
        self.collision = self.pathfinding.collision
        self.res = self.collision.tile_size
        self.points = None
        self.start_search()

    def next(self, current):
        """
        Attempts to gets the next point in the path.
        ...
        """
        if current not in self.points:
            return False

        index = self.points.index(current)
        length = len(self.points)

        if index + 1 == length:
            return False

        return self.points[index + 1]

    def start_search(self):
        """
        (Re)starts the pathfinding search.
        """
        self.done = False
        self.closed_set = set()
        self.open_set = {self.start}
        self.scores = {self.start: 0}
        self.came_from = { }

    def search(self):
        """
        Starts or continues an A* search for an apropriate path.
        """
        iterations = 25
        while len(self.open_set) > 0 and iterations > 0:
            iterations -= 1

            # Find the next node to evaluate.
            current, current_score = self.get_lowest_score(self.open_set, self.scores)

            # Check if it is a destination
            if current[0] < 0:
                self.points = self.trace_path(current, self.came_from)
                self.done = True
                return

            # Remove from the open set.
            self.open_set.remove(current)

            # Add to the closed set.
            self.closed_set.add(current)

            # Consider each neighbour.
            for neighbour in self.get_neighbours(current):

                # Skip if already in the closed set
                if neighbour in self.closed_set:
                    continue

                score = current_score + self.get_cost(current, neighbour)
                exists = (neighbour in self.open_set)

                if not exists or self.scores[neighbour] > score:
                    self.scores[neighbour] = score
                    self.came_from[neighbour] = current

                if not exists:
                    self.open_set.add(neighbour)