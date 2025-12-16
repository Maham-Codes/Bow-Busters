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
    # main game controller that handles the game loop and coordinates all systems
    # manages level loading enemy waves tower placement and user input

    def __init__(self, window):
        # sets up the game with all its systems and groups
        self.window = window
        self.clock = pygame.time.Clock()
        # sprite groups for different game objects
        self.defences = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.purchase_history = []  # stack of recent defences

      
        self.abilities = AbilityManager(self) 
        
        # initialize game state
        self.purchase_history = []        # stack of recent defences
        self.music_on = True   # music will start khud ba khud, then we can just turn it off,our choice

        # load the starting level
        self.load_level("path")

        # set up available tower types that players can build
        self.defence_type = 0
        self.defence_prototypes = [
            Defence(self, "defence_" + name, -100, -100)
            for name in ["bluechonk", "wall", "mines", "batcat"]
        ]
        
    def load_level(self, name):
        # loads a new level and resets all game state
        # args: name - which level file to load
        self.defences.empty()
        self.bullets.empty()
        self.explosions.empty()
        self.level = Level(self, name)
        self.wave = Wave(self, 1)
        self.menu = Menu(self)
        self.purchase_history = []  # reset history when level restarts

    def run(self):
        # main game loop that runs 60 times per second
        # handles input updates all systems and redraws everything
        self.running = True

        while self.running:
            # calculate time since last frame for smooth movement
            delta = self.clock.tick(60) / 1000.0

            # handle all user input events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # place tower if game is running or interact with menu if paused
                    if not self.menu.visible:
                        self.place_defence(pygame.mouse.get_pos())
                    self.menu.clicked()

                elif event.type == pygame.KEYDOWN:
                    # undo last tower placement with u key
                    if event.key == pygame.K_u:
                        self.undo_last_purchase()
                    self.menu.key_pressed(event.key)

            # update all game systems each frame
            self.menu.update()
            self.level.pathfinding.update()
            self.abilities.update(delta)

            # only update gameplay when menu is not visible
            if not self.menu.visible:
                self.level.time += delta
                self.defences.update(delta)
                self.bullets.update(delta)
                self.explosions.update(delta)

                # spawn next wave when current one is finished
                self.wave.update(delta)
                if self.wave.done:
                    self.wave = Wave(self, self.wave.number + 1)

            # draw everything in the correct order from back to front
            self.window.clear()
            self.level.prefabs.draw(self.window.screen)
            self.defences.draw(self.window.screen)
            self.bullets.draw(self.window.screen)
            self.wave.enemies.draw(self.window.screen)
            self.explosions.draw(self.window.screen)
            self.menu.draw(self.window.screen)
            
            # draw heat map overlay if ability is toggled on
            if self.abilities.show_heat_overlay:
                self.menu.draw_heat_overlay(self.window.screen)

            pygame.display.flip()

    def quit(self):
        # stops the game loop and closes the window
        self.running = False

    def select_defence(self, type):
        # changes which type of tower will be placed on next click
        # args: type - index of tower type in defence_prototypes list
        self.defence_type = type

    def place_defence(self, position):
        # attempts to place a tower at the clicked position
        # checks if player has enough money and spot is not blocked
        # args: position - mouse click coordinates
        if self.defence_type < 0:
            return

        # get the tower prototype for the selected type
        defence_proto = self.defence_prototypes[self.defence_type]

        # check if player has enough money
        if self.level.money < defence_proto.cost:
            return

        # snap position to grid
        x = position[0] - position[0] % 32
        y = position[1] - position[1] % 32

        # make sure spot is not already blocked by walls or other towers
        if self.level.collision.rect_blocked(x, y, defence_proto.rect.width - 2, defence_proto.rect.height - 2):
            return

        # prevent blocking the only path enemies can takeemies can take
        if hasattr(defence_proto, "block") and self.level.pathfinding.is_critical((x, y)):
            return

        # all checks passed create the tower and deduct money
        new_defence = Defence(self, defence_proto.name, x, y)
        self.defences.add(new_defence)
        self.level.money -= defence_proto.cost

        # save this purchase so player can undo it later
        self.purchase_history.append({
            "name": defence_proto.name,
            "x": x,
            "y": y,
            "cost": defence_proto.cost,
            "ref": new_defence,
        })

    def undo_last_purchase(self):
        # removes the most recently placed tower and refunds its cost
        # triggered by pressing u key
        if not self.purchase_history:
            return
        # get the last tower that was placed
        entry = self.purchase_history.pop()
        defence = entry.get("ref")

        # remove it from the game if it still exists
        if defence and defence.alive():
            # unblock the collision grid if this tower blocks movement
            if hasattr(defence, "block"):
                self.level.collision.unblock_rect(
                    defence.rect.x, defence.rect.y, defence.rect.width, defence.rect.height
                )
            self.defences.remove(defence)
            defence.kill()

        # give the money back to the player
        self.level.money += entry.get("cost", 0)
        
    def toggle_music(self):
        # turns background music on or off-toggling
        self.music_on = not self.music_on

        # music on hoga to volume 0.5 warna 0, not using stop aur pause wali cheez-making things easier
        if self.music_on:
            pygame.mixer.music.set_volume(0.5)
        else:
            pygame.mixer.music.set_volume(0.0)


