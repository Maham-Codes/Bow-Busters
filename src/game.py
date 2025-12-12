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
            for name in ["bluechonk", "wall", "mines", "batcat"]
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

    def quit(self):
        """ Quits and closes the game. """
        self.running = False

    def select_defence(self, type):
        """ Select defence type. """
        self.defence_type = type

    def place_defence(self, position):
        """ Place a defence tower. """
        if self.defence_type < 0:
            return

        defence_proto = self.defence_prototypes[self.defence_type]

        if self.level.money < defence_proto.cost:
            return

        x = position[0] - position[0] % 32
        y = position[1] - position[1] % 32

        # Level collision check
        if self.level.collision.rect_blocked(x, y, defence_proto.rect.width - 2, defence_proto.rect.height - 2):
            return

        # Critical path (cannot block path)
        if hasattr(defence_proto, "block") and self.level.pathfinding.is_critical((x, y)):
            return

        new_defence = Defence(self, defence_proto.name, x, y)
        self.defences.add(new_defence)
        self.level.money -= defence_proto.cost

        self.purchase_history.append({
            "name": defence_proto.name,
            "x": x,
            "y": y,
            "cost": defence_proto.cost,
            "ref": new_defence,
        })

    def undo_last_purchase(self):
        """Undo the most recent defence placement."""
        if not self.purchase_history:
            return
        entry = self.purchase_history.pop()
        defence = entry.get("ref")

        if defence and defence.alive():
            if hasattr(defence, "block"):
                self.level.collision.unblock_rect(
                    defence.rect.x, defence.rect.y, defence.rect.width, defence.rect.height
                )
            self.defences.remove(defence)
            defence.kill()

        self.level.money += entry.get("cost", 0)
        
    def toggle_music(self):
        self.music_on = not self.music_on

        if self.music_on:
            pygame.mixer.music.set_volume(0.5)
        else:
            pygame.mixer.music.set_volume(0.0)


