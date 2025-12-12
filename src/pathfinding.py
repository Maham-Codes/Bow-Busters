from collections import Counter
heat = Counter() 

import random


class Pathfinding:
    """
    manages pathfinding and path selection for enemies

    keeps a pool of paths for use by enemies a path is randomly
    selected for each enemy that is spawned if a path becomes blocked
    it will be repaired or recalculated enemies can switch between 
    paths to continue moving if their current path is being recalculated
    """

    def __init__(self, game, collision):
        """
        constructor

        args:
            game (Game): the game instance
            collision (Collision): the collision manager instance

        """
        self.game = game
        self.collision = collision
        self.pool = []
        self.partials = 0

    def precompute(self, count):
        """
        starts precomputing a given number of paths

        args:
            count (int): the number of paths to precompute

        """
        for i in range(count):
            self.pool.append(Path(self, self.find_start()))

    def find_start(self):
        """
        finds a start point for a full length path
        randomly picked taking collision into account

        returns:
            (int, int): the start position

        """
        cells = self.collision.height
        x = self.game.window.resolution[0]
        attempts = 100
        
        while attempts > 0:
            attempts -= 1

            y = random.randint(0, cells - 1) * self.collision.tile_size
            if not self.collision.point_blocked(x - 32, y):
                return (x, y)

        # no start found supply a default
        return (x, random.randint(0, cells - 1) * self.collision.tile_size)

    def get_point_usage(self, point):
        """
        returns the number of existing paths that use the given point

        args:
            point (int, int): the point to check

        returns:
            (int): the number of paths using the given point

        """
        total = 0

        for path in self.pool:
            if path.done and point in path.points:
                total += 1

        return total
    
    def update(self):
        """
        continues generating paths
        run each frame
        """
        for path in self.pool:
            if not path.done:
                path.search()
                return

    def get_path(self):
        """
        picks a path for an enemy to follow

        returns:
            a random path (may still be generating)

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
        called when a point has been blocked by a turret
        triggers path repair and regeneration (if needed)

        args:
            point (int, int): the point that is now blocked

        """
        for path in self.pool:
            # repair paths that contain the point
            if path.done and point in path.points:
                path.repair(point)

            # restart calculations of paths that may include the point
            if not path.done and (point in path.open_set or point in path.closed_set):
                path.start_search()

    def get_partial_path(self, point):
        """
        gets or creates a path that starts or passes through the given point
        used for enemies that are stuck due to a new turret placement

        args:
            start (int, int): the point that the path must include

        returns:
            (Path), (int, int): the requested path and the point to move to whilst waiting

        """
        # try intersecting paths
        for path in self.pool:
            if (path.done and point in path.points) or path.start == point:
                return path, point

        # try paths that intersect with neighbours
        for neighbour in self.pool[0].get_neighbours(point):
            for path in self.pool:
                if path.done and neighbour in path.points:
                    return path, neighbour

        # no suitable path make a new one
        path = Path(self, point)
        self.pool.insert(0, path)
        self.partials += 1
        return path, point

    def is_critical(self, point):
        """
        works out if blocking the given point may make reaching the finish impossible
        
        args:
            point (int, int): the point to check

        returns:
            true if the point must be kept clear otherwise returns false

        """
        for path in self.pool:
            if path.done and path.start[0] >= self.game.window.resolution[0] and point not in path.points:
                return False

        return True


class Path:
    """
    a single path across the level
    calculated using the a star pathfinding algorithm across multiple frames
    can be repaired if one of its points becomes blocked
    """

    def __init__(self, pathfinding, start):
        """ 
        constructor
        
        args:
            pathfinding (Pathfinding): the pathfinding manager instance
            start (int, int): the start position of the path
        
        """
        self.start = start
        self.pathfinding = pathfinding
        self.collision = self.pathfinding.collision
        self.res = self.collision.tile_size
        self.points = None
        self.start_search()

    def next(self, current):
        """
        attempts to gets the next point in the path
        
        args:
            current (int, int): the current point

        returns:
            (int, int) if successful false if there are no more points in the path

        """
        if current not in self.points: # this is the fully corrected line
            return False

        index = self.points.index(current)
        length = len(self.points)

        if index + 1 == length:
            return False

        return self.points[index + 1]

    def start_search(self):
        """
        restarts the pathfinding search
        """
        self.done = False
        self.closed_set = set()
        self.open_set = {self.start}
        self.scores = {self.start: 0}
        self.came_from = { }

    def search(self):
        """
        starts or continues an a star search for an apropriate path
        """
        iterations = 25
        while len(self.open_set) > 0 and iterations > 0:
            iterations -= 1

            # find the next node to evaluate
            current, current_score = self.get_lowest_score(self.open_set, self.scores)

            # check if it is a destination
            if current[0] < 0:
                self.points = self.trace_path(current, self.came_from)
                self.done = True
                return

            # remove from the open set
            self.open_set.remove(current)

            # add to the closed set
            self.closed_set.add(current)

            # consider each neighbour
            for neighbour in self.get_neighbours(current):

                # skip if already in the closed set
                if neighbour in self.closed_set:
                    continue

                score = current_score + self.get_cost(current, neighbour)
                exists = (neighbour in self.open_set)

                if not exists or self.scores[neighbour] > score:
                    self.scores[neighbour] = score
                    self.came_from[neighbour] = current

                if not exists:
                    self.open_set.add(neighbour)

    def get_lowest_score(self, open_set, scores):
        """
        finds the point with the lowest score
        
        args:
            open_set (set(int, int)): a set of possible points
            scores (list(int)): a list with the score of each position

        returns:
            ((int, int), int) the lowest scoring point and its score

        """
        lowest_score = 999999999
        lowest_point = (0, 0)

        for p in open_set:
            score = scores[p]

            if lowest_score > score:
                lowest_score = score
                lowest_point = p

        return lowest_point, lowest_score

    def get_neighbours(self, position):
        """
        finds a list of neighbouring tiles for the given position

        args:
            position (int, int): the start position

        returns:
            a list of (int, int) tuples

        """
        if position[0] >= self.pathfinding.game.window.resolution[0]:
            return [(position[0] - self.res, position[1])]

        x_diff = range(position[0] - self.res, position[0] + self.res + 1, self.res)
        y_diff = range(position[1] - self.res, position[1] + self.res + 1, self.res)

        return [(x, y) for x in x_diff for y in y_diff if (x, y) != position and (x == position[0] or y == position[1] or self.can_use_diagonal(position, (x, y))) and not self.collision.point_blocked(x, y)]
        
    def can_use_diagonal(self, a, b):
        """
        returns true if the diagonal between a and b is clear

        args:
            a (int, int): position a
            b (int, int): position b

        returns:
            (bool) true if the diagonal is clear otherwise false

        """
        return not self.collision.point_blocked(b[0], a[1]) and not self.collision.point_blocked(a[0], b[1])

    def get_cost(self, a, b):
        """
        calculates the cost of moving between the given positions
        
        args:
            a (int, int): position a
            b (int, int): position b
            
        returns:
            (int) the cost of moving from a to b
          
        """
        base = 3 if a[0] == b[0] or a[1] == b[1] else 4
        crowding = self.pathfinding.get_point_usage(b)

        return base + crowding

    def trace_path(self, current, came_from):
        """
        traces a finished path from finish to start

        args:
            current (int, int): the last position in the path
            came_from (dict): the location each position was reached from

        returns:
            (list(int, int)): a list of points in the path

        """
        path = [ current ]
        while current in came_from:
            current = came_from[current]
            path.insert(0, current)

        return path

    def repair(self, point):
        """
        attempts to repair a path after a point is blocked
        
        args:
            point (int, int): the blocked point

        """
        index = self.points.index(point)

        if index != 0 and index < len(self.points) - 1:
            previous = self.points[index - 1]
            next = self.points[index + 1]

            previous_neighbours = self.get_neighbours(previous)
            next_neighbours = self.get_neighbours(next)

            # if next and previous are adjacent just remove the point
            if next in previous_neighbours:
                self.points.remove(point)
                return

            # if not check for a common neighbour
            for neighbour in previous_neighbours:
                if neighbour in next_neighbours:
                    self.points[index] = neighbour
                    return

            # if not check neighbours of neighbours
            for neighbour in previous_neighbours:
                for neighbour_neighbour in self.get_neighbours(neighbour):
                    if neighbour_neighbour in next_neighbours:
                        self.points[index] = neighbour
                        self.points.insert(index + 1, neighbour_neighbour)
                        return

        # no solution remake path
        self.start_search()