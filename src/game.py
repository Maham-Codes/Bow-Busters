import random
import pygame
from src.level import Level
from src.collision import Collision
from src.defence import Defence
from src.enemy import Enemy
from src.wave import Wave
from src.menu import Menu
from src.prefab import Prefab
from src.abilities import AbilityManager


class Game:
    """ 
    Contains the main control code and the game loop.
    """

    def __init__(self, window):
        """ Constructor """
        self.window = window
        self.clock = pygame.time.Clock()
        self.defences = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()

        # Load level
        self.load_level("path")

        # Tower types
        self.defence_type = 0
        self.defence_prototypes = [
            Defence(self, "defence_" + name, -100, -100)
            for name in ["pillbox", "wall", "mines", "artillery"]
        ]

        self.abilities = AbilityManager(self)
        # Leaderboard is now handled by Menu class
        # No need to initialize here since Menu creates its own instance

    def load_level(self, name):
        """ Loads a new level. """
        self.defences.empty()
        self.bullets.empty()
        self.explosions.empty()
        self.level = Level(self, name)
        self.wave = Wave(self, 1)
        self.menu = Menu(self)

    def run(self):
        """ Runs the main game loop. """
        self.running = True

        while self.running:
            delta = self.clock.tick(60) / 1000.0

            # Input event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.menu.visible:
                        self.place_defence(pygame.mouse.get_pos())
                    self.menu.clicked()
                elif event.type == pygame.KEYDOWN:
                    self.menu.key_pressed(event.key)

            # Update systems
            self.menu.update()
            self.level.pathfinding.update()
            self.abilities.update(delta)

            if not self.menu.visible:
                self.level.time += delta
                self.defences.update(delta)
                self.bullets.update(delta)
                self.explosions.update(delta)

                self.wave.update(delta)
                if self.wave.done:
                    self.wave = Wave(self, self.wave.number + 1)

            # Redraw
            self.window.clear()
            self.level.prefabs.draw(self.window.screen)
            self.defences.draw(self.window.screen)
            self.bullets.draw(self.window.screen)
            self.wave.enemies.draw(self.window.screen)
            self.explosions.draw(self.window.screen)
            self.menu.draw(self.window.screen)

    def quit(self):
        """
        Quits and closes the game.
        """
        # Scores are automatically saved when game ends (in Menu.show_lose_screen)
        self.running = False

    def select_defence(self, type):
        """ Select defence type. """
        self.defence_type = type

    def place_defence(self, position):
        """ Place a defence tower. """
        if self.defence_type < 0:
            return

        defence = self.defence_prototypes[self.defence_type]

        if self.level.money < defence.cost:
            return

        x = position[0] - position[0] % 32
        y = position[1] - position[1] % 32

        # Level collision check
        if self.level.collision.rect_blocked(x, y, defence.rect.width - 2, defence.rect.height - 2):
            return

        # Critical path (cannot block path)
        if hasattr(defence, "block") and self.level.pathfinding.is_critical((x, y)):
            return

        self.defences.add(Defence(self, defence.name, x, y))
        self.level.money -= defence.cost
