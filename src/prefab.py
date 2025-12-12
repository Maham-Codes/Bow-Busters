from pygame.sprite import Sprite
from pygame.rect import Rect
import pygame


class Prefab(Sprite):
    # a game object loaded from a config file
    # prefab files define properties like images stats and behavior
    # each prefab type is cached so we only load it once

    # stores loaded prefab configs so we dont reload them
    Cache = { }

    def __init__(self, name, x, y):
        # creates a new prefab by loading its config file
        # sets up position and initializes animations if needed
        # args: name - prefab type to load
        #       x - horizontal spawn position
        #       y - vertical spawn position
        super().__init__()

        self.name = name
        self.config = self.load_config(name)
        self.apply_config(self.config)

        # set up animation system if this prefab has animated sprites
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

    def update_animation(self, delta):
        # advances animation frames based on time
        # loops or destroys object when animation finishes
        # args: delta - time in seconds since last frame
        if hasattr(self, "anim_source"):
            self.anim_change_time -= delta

            if self.anim_change_time < 0:
                self.anim_change_time += self.anim_rate
                
                self.anim_index += 1
                if self.anim_index == len(self.anim_source):
                    self.anim_index = 0

                    if not hasattr(self, "anim_loop") or not self.anim_loop:
                        self.kill()

                self.image = self.anim_source[self.anim_index]


    def load_config(self, name):
        # loads a prefab config file and parses all its properties
        # caches the result so we dont reload the same file multiple times
        # args: name - prefab filename without extension
        # returns: dictionary of property names and values
        # check if we already loaded this prefab before
        if name in Prefab.Cache.keys():
            return Prefab.Cache[name]

        entries = { }

        try:
            with open("prefabs\\" + name + ".prefab", "r") as file:
                for line in [f.split(":") for f in file.readlines() if f[0] != "#" and len(f.strip()) != 0]:
                    key = line[0].strip()
                    type = line[1].strip()
                    value = line[2].strip()

                    if type == "str":
                        entries[key] = value.replace("\\n", "\n")
                    elif type == "int":
                        entries[key] = int(value)
                    elif type == "float":
                        entries[key] = float(value)
                    elif type == "bool":
                        entries[key] = (value == "1")
                    elif type == "img":
                        entries[key] = pygame.image.load(value).convert()
                    elif type == "aimg":
                        entries[key] = pygame.image.load(value).convert_alpha()
                    elif type == "font":
                        entries[key] = pygame.font.Font(pygame.font.match_font(value, "font_bold" in entries.keys()), entries["font_size"])
                    elif type == "spritesheet":
                        entries[key] = [pygame.image.load(value + str(i) + ".png").convert_alpha() for i in range(entries["anim_count"])]
                    elif type == "rotimg":
                        original = pygame.image.load(value).convert_alpha()
                        entries[key] = [original] + [pygame.transform.rotate(original, angle) for angle in range(5, 361, 5)]

        except OSError:
            print("Could not read prefab " + name)

        Prefab.Cache[name] = entries
        return entries

    def apply_config(self, config):
        # takes all properties from config file and sets them on this object
        # makes the prefab data become actual object attributes
        # args: config - dictionary of property names and values
        for name in config.keys():
            setattr(self, name, config[name])
