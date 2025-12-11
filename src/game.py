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
        self.purchase_history = []  # stack of recent defences

      
        self.abilities = AbilityManager(self) 
        
        # Load level (This calls self.load_level and initializes self.menu)
        self.purchase_history = []        # stack of recent defences
        self.music_on = True   # music starts enabled

        # Load level
        self.load_level("path")

        # Tower types
        self.defence_type = 0
        self.defence_prototypes = [
            Defence(self, "defence_" + name, -100, -100)
            for name in ["pillbox", "wall", "mines", "artillery"]
        ]
        
    def load_level(self, name):
        """ Loads a new level. """
        self.defences.empty()
        self.bullets.empty()
        self.explosions.empty()
        self.level = Level(self, name)
        self.wave = Wave(self, 1)
        self.menu = Menu(self)
        self.purchase_history = []  # reset history when level restarts

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
                    if event.key == pygame.K_u:
                        self.undo_last_purchase()
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
            
            # The heat overlay is drawn by the menu if toggled on
            if self.abilities.show_heat_overlay:
                self.menu.draw_heat_overlay(self.window.screen)

            pygame.display.flip()

