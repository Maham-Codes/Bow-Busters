import random

class Pathfinding:
    """
    Manages pathfinding and path selection for enemies.

    Keeps a pool of paths for use by enemies. A path is randomly
    selected for each enemy that is spawned. If a path becomes blocked,
    it will be repaired or recalculated. Enemies can switch between 
    paths to continue moving if their current path is being recalculated.
    """

    def __init__(self, game, collision):
        """
        Constructor.

        Args:
            game (Game): The game instance.
            collision (Collision): The collision manager instance.

        """
        self.game = game
        self.collision = collision
        self.pool = []
        self.partials = 0

    def precompute(self, count):
        """
        Starts precomputing a given number of paths.

        """
        for i in range(count):
            self.pool.append(Path(self, self.find_start()))

    def find_start(self):
        """
        Finds a start point for a full length path.
        Randomly picked, taking collision into account
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
        Returns the number of existing paths that use the given point
        """
        total = 0

        for path in self.pool:
            if path.done and point in path.points:
                total += 1

        return total
    
    def update(self):
        """
        Continues generating paths
        Run each frame
        """
        for path in self.pool:
            if not path.done:
                path.search()
                return

    def get_path(self):
        """
        Picks a path for enemy to follow

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
        Triggers path repair and regeneration (if needed)
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
        Used for enemies that are stuck due to a new turret placement

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
        Works out if blocking the given point may make reaching the finish impossible
        """
        for path in self.pool:
            if path.done and path.start[0] >= self.game.window.resolution[0] and point not in path.points:
                return False

        return True


class Path:
    """
    single path across the level
    Calculated using the A* pathfinding algorithm across multiple frames
    Can be repaired if one of its points becomes blocked
    """

    def __init__(self, pathfinding, start):
        """ 
        Constructor. 
        
        Args:
            pathfinding (Pathfinding): The pathfinding manager instance.
            start (int, int): The start position of the path.
        
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
        """
        if  current not in self.points:
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

    def get_lowest_score(self, open_set, scores):
        """
        Finds point with the lowest score.
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
        Finds list of neighbouring tiles for the given position

        """
        if position[0] >=  self.pathfinding.game.window.resolution[0]:
            return [(position[0] - self.res, position[1])]

        x_diff = range(position[0] - self.res, position[0] + self.res + 1, self.res)
        y_diff = range(position[1] - self.res, position[1] + self.res + 1, self.res)

        return [(x, y) for x in x_diff for y in y_diff if (x, y) != position and (x == position[0] or y == position[1] or self.can_use_diagonal(position, (x, y))) and not self.collision.point_blocked(x, y)]
        
    def can_use_diagonal(self, a, b):
        """
        Returns true if the diagonal between a and b issss clear

        """
        return not self.collision.point_blocked(b[0], a[1]) and not self.collision.point_blocked(a[0], b[1])

    def get_cost(self, a, b):
        """
        Calculates the cost of moving between the given positions.
          
        """
        base = 3 if a[0] == b[0] or a[1] == b[1] else 4
        crowding = self.pathfinding.get_point_usage(b)

        return base + crowding

    def trace_path(self, current, came_from):
        path = [ current ]
        while current in came_from:
            current = came_from[current]
            path.insert(0, current)

        return path

    def repair(self, point):
        """
        Attempts to repair a path after point  blocked
        Args:
            point (int, int): blocked point

        """
        index = self.points.index(point)

        if index != 0 and index < len(self.points) - 1:
            previous = self.points[index - 1]
            next = self.points[index + 1]

            previous_neighbours = self.get_neighbours(previous)
            next_neighbours = self.get_neighbours(next)

            #if next and previous are adjacent, just remove the point.
            if next in previous_neighbours:
                self.points.remove(point)
                return

            #if not, check for a common neighbour.
            for neighbour in previous_neighbours:
                if neighbour in next_neighbours:
                    self.points[index] = neighbour
                    return

            #if not, check neighbours of neighbours.
            for neighbour in previous_neighbours:
                for neighbour_neighbour in self.get_neighbours(neighbour):
                    if neighbour_neighbour in next_neighbours:
                        self.points[index] = neighbour
                        self.points.insert(index + 1, neighbour_neighbour)
                        return

        #no solution, remake path.
        self.start_search()
