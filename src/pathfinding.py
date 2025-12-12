from collections import Counter
heat = Counter() 

import random


class Pathfinding:
    # handles pathfinding and path selection for all enemies in the game
    # maintains a pool of precalculated paths that enemies can follow
    # when an enemy spawns it gets assigned a random path from this pool
    # if a turret blocks part of a path the system will try to repair it
    # or recalculate a new route so enemies can keep moving

    def __init__(self, game, collision):
        # sets up the pathfinding system
        # args: game - reference to the main game object
        #       collision - handles collision detection for path validation
        self.game = game
        self.collision = collision
        self.pool = []
        self.partials = 0

    def precompute(self, count):
        # begins calculating paths in advance so theyre ready when enemies spawn
        # args: count - how many paths to generate for the pool
        for i in range(count):
            self.pool.append(Path(self, self.find_start()))

    def find_start(self):
        # picks a random starting position on the right edge of the screen
        # makes sure the spot isnt blocked by checking collision
        # returns: tuple with x and y coordinates for the start point
        cells = self.collision.height
        x = self.game.window.resolution[0]
        attempts = 100
        
        while attempts > 0:
            attempts -= 1

            y = random.randint(0, cells - 1) * self.collision.tile_size
            if not self.collision.point_blocked(x - 32, y):
                return (x, y)

        # couldnt find clear spot so just pick any random position
        return (x, random.randint(0, cells - 1) * self.collision.tile_size)

    def get_point_usage(self, point):
        # counts how many paths go through a specific point
        # used to avoid crowding too many enemies on the same tiles
        # args: point - the coordinates to check
        # returns: number of paths that pass through this point
        total = 0

        for path in self.pool:
            if path.done and point in path.points:
                total += 1

        return total
    
    def update(self):
        # continues calculating any unfinished paths
        # call this every frame to gradually build up the path pool
        for path in self.pool:
            if not path.done:
                path.search()
                return

    def get_path(self):
        # selects a random path from the pool for a newly spawned enemy
        # tries to find a completed path but will create a partial one if needed
        # returns: a path object the enemy can follow
        attempts = 500
        while attempts > 0:
            attempts -= 1

            path = self.pool[random.randint(self.partials, len(self.pool) - 1)] 
            
            if path.done and path.start[0] >= self.game.window.resolution[0]:
                return path

        return self.get_partial_path(self.find_start())[0]

    def repair(self, point):
        # called when a player places a turret and blocks part of a path
        # tries to fix all affected paths or restarts their calculation
        # args: point - the coordinates that just got blocked
        for path in self.pool:
            # fix any completed paths that go through this blocked point
            if path.done and point in path.points:
                path.repair(point)

            # restart any paths that were considering this point during calculation
            if not path.done and (point in path.open_set or point in path.closed_set):
                path.start_search()

    def get_partial_path(self, point):
        # finds or creates a path that goes through a specific location
        # used when an enemy gets stuck and needs a new route from their current position
        # args: point - the coordinates where the enemy is currently located
        # returns: the path to follow and the immediate next position to move toward
        # check if any existing path goes through this exact spot
        for path in self.pool:
            if (path.done and point in path.points) or path.start == point:
                return path, point

        # check if any path goes through a neighboring tile
        for neighbour in self.pool[0].get_neighbours(point):
            for path in self.pool:
                if path.done and neighbour in path.points:
                    return path, neighbour

        # no existing path works so create a brand new one
        path = Path(self, point)
        self.pool.insert(0, path)
        self.partials += 1
        return path, point

    def is_critical(self, point):
        # checks if blocking this point would make it impossible for enemies to reach the goal
        # prevents players from completely blocking all possible paths
        # args: point - the coordinates to check
        # returns: true if blocking this would trap all enemies false if theres another way
        for path in self.pool:
            if path.done and path.start[0] >= self.game.window.resolution[0] and point not in path.points:
                return False

        return True


class Path:
    # represents one route from the right side of the screen to the left goal
    # uses a star algorithm to find the shortest path while avoiding obstacles
    # calculation happens gradually over multiple frames to avoid lag
    # can automatically fix itself when turrets block part of the route

    def __init__(self, pathfinding, start):
        # creates a new path starting from the given position
        # args: pathfinding - reference to the main pathfinding manager
        #       start - the coordinates where this path begins
        self.start = start
        self.pathfinding = pathfinding
        self.collision = self.pathfinding.collision
        self.res = self.collision.tile_size
        self.points = None
        self.start_search()

    def next(self, current):
        # gets the next waypoint an enemy should move toward
        # args: current - where the enemy is right now
        # returns: the next coordinates to move to or false if we reached the end
        if current not in self.points:
            return False

        index = self.points.index(current)
        length = len(self.points)

        if index + 1 == length:
            return False

        return self.points[index + 1]

    def start_search(self):
        # resets all variables and begins calculating the path from scratch
        self.done = False
        self.closed_set = set()
        self.open_set = {self.start}
        self.scores = {self.start: 0}
        self.came_from = { }

    def search(self):
        # runs a few iterations of the a star pathfinding algorithm
        # called repeatedly each frame until the path is complete
        iterations = 25
        while len(self.open_set) > 0 and iterations > 0:
            iterations -= 1

            # pick the most promising point to explore next
            current, current_score = self.get_lowest_score(self.open_set, self.scores)

            # if we reached the left edge were done
            if current[0] < 0:
                self.points = self.trace_path(current, self.came_from)
                self.done = True
                return

            # mark this point as being explored
            self.open_set.remove(current)

            # add to the list of already checked points
            self.closed_set.add(current)

            # look at all adjacent tiles
            for neighbour in self.get_neighbours(current):

                # dont recheck points weve already fully explored
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
        # finds which point in the open set has the best score
        # lower scores mean shorter estimated distance to goal
        # args: open_set - all points we havent fully explored yet
        #       scores - dictionary mapping each point to its calculated score
        # returns: the best point to explore next and its score value
        lowest_score = 999999999
        lowest_point = (0, 0)

        for p in open_set:
            score = scores[p]

            if lowest_score > score:
                lowest_score = score
                lowest_point = p

        return lowest_point, lowest_score

    def get_neighbours(self, position):
        # gets all tiles adjacent to the current position that arent blocked
        # includes diagonal movement if both intermediate tiles are clear
        # args: position - the coordinates to find neighbors for
        # returns: list of valid coordinates the enemy could move to next
        if position[0] >= self.pathfinding.game.window.resolution[0]:
            return [(position[0] - self.res, position[1])]

        x_diff = range(position[0] - self.res, position[0] + self.res + 1, self.res)
        y_diff = range(position[1] - self.res, position[1] + self.res + 1, self.res)

        return [(x, y) for x in x_diff for y in y_diff if (x, y) != position and (x == position[0] or y == position[1] or self.can_use_diagonal(position, (x, y))) and not self.collision.point_blocked(x, y)]
        
    def can_use_diagonal(self, a, b):
        # checks if an enemy can move diagonally without cutting through walls
        # makes sure both adjacent tiles are clear so no corner clipping
        # args: a - starting position
        #       b - destination position
        # returns: true if diagonal movement is safe false if it would clip a wall
        return not self.collision.point_blocked(b[0], a[1]) and not self.collision.point_blocked(a[0], b[1])

    def get_cost(self, a, b):
        # calculates how expensive it is to move from one point to another
        # diagonal moves cost more and crowded areas get penalized
        # args: a - starting position
        #       b - ending position
        # returns: cost value where lower is better
        base = 3 if a[0] == b[0] or a[1] == b[1] else 4
        crowding = self.pathfinding.get_point_usage(b)

        return base + crowding

    def trace_path(self, current, came_from):
        # works backwards from the goal to build the final path
        # follows the breadcrumb trail left by the a star algorithm
        # args: current - the goal position we just reached
        #       came_from - dictionary tracking how we got to each point
        # returns: ordered list of coordinates from start to finish
        path = [ current ]
        while current in came_from:
            current = came_from[current]
            path.insert(0, current)

        return path

    def repair(self, point):
        # tries to fix a path when one of its points gets blocked by a turret
        # looks for alternate routes nearby or recalculates if necessary
        # args: point - the coordinates that are now blocked
        index = self.points.index(point)

        if index != 0 and index < len(self.points) - 1:
            previous = self.points[index - 1]
            next = self.points[index + 1]

            previous_neighbours = self.get_neighbours(previous)
            next_neighbours = self.get_neighbours(next)

            # easiest fix just connect the previous and next points directly
            if next in previous_neighbours:
                self.points.remove(point)
                return

            # look for a single tile that connects both points
            for neighbour in previous_neighbours:
                if neighbour in next_neighbours:
                    self.points[index] = neighbour
                    return

            # try using two tiles to bridge the gap
            for neighbour in previous_neighbours:
                for neighbour_neighbour in self.get_neighbours(neighbour):
                    if neighbour_neighbour in next_neighbours:
                        self.points[index] = neighbour
                        self.points.insert(index + 1, neighbour_neighbour)
                        return

        # couldnt find a simple fix so recalculate the whole path
        self.start_search()