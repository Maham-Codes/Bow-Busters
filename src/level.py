from src.prefab import Prefab
from src.collision import Collision
from src.wave import Wave
from src.pathfinding import Pathfinding
from pygame.sprite import OrderedUpdates


class Level:
    # represents a game level loaded from a text file
    # contains all the walls decorations collision data and enemy paths

    def __init__(self, game, name):
        # creates and loads a level by its filename
        # args: game - reference to the main game object
        #       name - name of the level file without extension
        self.game = game
        self.name = name
        self.load_data()
        self.start()

    def load_data(self):
        # reads the level file and parses it into a list of objects to place
        # level files are text based with one object per line
        # format is: prefab_name x_position y_position
        # lines starting with # are comments and get skipped
        try:
            with open("levels\\" + self.name + ".level", "r") as file:
                self.data = [line.strip().split(" ") for line in file.readlines() if len(line.strip()) > 0 and line[0] != "#"]

        except IOError:
            print("Error loading level")

    def start(self):
        # sets up all the systems needed to run the level
        # creates collision grid pathfinding and places all objects
        self.collision = Collision(self, self.game.window.resolution, 32)
        self.prefabs = OrderedUpdates()
        self.pathfinding = Pathfinding(self.game, self.collision)

        # create all the objects defined in the level file
        for args in self.data:
            name = args[0]
            x = int(args[1])
            y = int(args[2])

            prefab = Prefab(name, x, y)
            self.prefabs.add(prefab)

            # if this object blocks movement add it to collision grid
            if hasattr(prefab, "block"):
                # block textures are 1 pixel wider to make a full border
                self.collision.block_rect(x, y, prefab.rect.width - 1, prefab.rect.height - 1)

        # precalculate paths for enemies to follow
        self.pathfinding.precompute(30)
        self.wave = Wave(self.game, 1)
        # starting values for player resources
        self.lives = 20
        self.money = 600
        self.time = 0

    def get_score(self):
        # calculates the players score based on time survived and waves completed
        # returns: integer score value
        return int((self.time / 5) ** 1.4 + (self.game.wave.number - 1) ** 3)
