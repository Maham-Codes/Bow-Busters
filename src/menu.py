from core.prefab import Prefab
from core.leaderboard import Leaderboard
from pygame.sprite import OrderedUpdates
import pygame
import math


class Menu(Prefab):
    """
    Controls the menu system.
    """
    def __init__(self, game):
        """
        Constructor.

        Args:
            game (Game): The game instance.

        """
        super().__init__("menu", 0, 0)

        self.game = game
        self.leaderboard = Leaderboard()
        self.components = OrderedUpdates()
        self.clear()
        self.show_main_screen()
        self.visible = True
        self.leaderboard_name = None
        
    def show(self):
        """
        Shows the menu.
        """
        self.visible = True
        self.show_main_screen()

    def hide(self):
        """
        Hides the menu and enables in game icons.
        """
        self.visible = False
        self.clear()

        self.defence_buttons = [MenuButton(self, "menu_defence_button", self.game.defence_prototypes[i].display_name, (i + 1) * 64, 0, lambda: self.game.select_defence((pygame.mouse.get_pos()[0] - 64) // 64)) for i in range(len(self.game.defence_prototypes))]
        self.components.add(self.defence_buttons)

        self.wave_label = MenuLabel(self, "menu_pause_button", "Wave", 448, 0)
        self.lives_label = MenuLabel(self, "menu_pause_button", "Lives", 576, 0)
        self.money_label = MenuLabel(self, "menu_pause_button", "Money", 704, 0)
        self.score_label = MenuLabel(self, "menu_pause_button", "Score", 832, 0)
        self.components.add(self.wave_label)
        self.components.add(self.lives_label)
        self.components.add(self.money_label)
        self.components.add(self.score_label)

        self.components.add(MenuButton(self, "menu_pause_button", "Menu", 1088, 0, self.show))

        self.update()

    def clear(self):
        """
        Removes all components from the menu.
        """
        self.components.remove(self.components)
        self.component_next = self.top

    def update(self):
        """
        Called each frame.
        """
        if not self.visible:
            self.wave_label.set_text("Wave: " + str(self.game.wave.number))
            self.lives_label.set_text("Lives: " + str(self.game.level.lives))
            self.lives_label.highlighted = (self.game.level.lives < 5)
            self.money_label.set_text("Money: " + str(self.game.level.money))
            self.score_label.set_text("Score: " + str(self.game.level.get_score()))

            for i in range(len(self.defence_buttons)):
                self.defence_buttons[i].disabled = (self.game.defence_prototypes[i].cost > self.game.level.money)
                self.defence_buttons[i].selected = (self.game.defence_type == i)
        
        self.components.update()

    def clicked(self):
        """
        Called when a mouse button is pressed.
        """
        for component in self.components:
            if isinstance(component, MenuButton):
                component.clicked()

    def key_pressed(self, key):
        """
        Called when a key has been pressed.

        Args:
            key: The key that was pressed.

        """
        if self.leaderboard_name is None:
            return

        keys = { pygame.K_a: "a", pygame.K_b: "b", pygame.K_c: "c", pygame.K_d: "d", pygame.K_e: "e", pygame.K_f: "f", pygame.K_g: "g", pygame.K_h: "h", pygame.K_i: "i", 
                pygame.K_j: "j", pygame.K_k: "k", pygame.K_l: "l", pygame.K_m: "m", pygame.K_n: "n", pygame.K_o: "o", pygame.K_p: "p", pygame.K_q: "q", pygame.K_r: "r", 
                pygame.K_s: "s", pygame.K_t: "t", pygame.K_u: "u", pygame.K_v: "v", pygame.K_w: "w", pygame.K_x: "x", pygame.K_y: "y", pygame.K_z: "z",
                pygame.K_0: "0", pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3", pygame.K_4: "4", pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7",
                pygame.K_8: "8", pygame.K_9: "9" }

        if key in keys.keys():
            self.leaderboard_name.set_text(self.leaderboard_name.text + (keys[key].upper() if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT] else keys[key]))
        elif key is pygame.K_BACKSPACE and self.leaderboard_name.text != "":
            self.leaderboard_name.set_text(self.leaderboard_name.text[:-1])

    def draw(self, screen):
        """
        Draws the menu and its components.

        Args:
            screen (Surface): The surface that is blitted to.

        """
        if self.visible:
            screen.blit(self.image, (0, 0))

        self.components.draw(screen)

    def add_button(self, text, callback):
        """
        Adds a standard button to the menu screen.

        Args:
            text (str): The text to display on the button.
            callback (callable): The callback when the button is clicked.

        Returns:
            (MenuButton): The button.

        """
        button = MenuButton(self, "menu_button", text, 0, self.component_next, callback)
        button.rect.x = (self.rect.width - button.rect.width) / 2

        self.components.add(button)
        self.component_next += button.rect.height
        self.component_next += button.padding

        return button

    def add_level_button(self, level):
        """
        Adds a change level button to the menu screen.

        Args:
            level (str): The name of the level to display on the button.

        """
        button = MenuButton(self, "menu_level_" + level, level, 0, self.component_next, lambda: self.game.load_level(level))
        button.rect.x = (self.rect.width - button.rect.width) / 2
        
        self.components.add(button)
        self.component_next += button.rect.height
        self.component_next += button.padding

    def show_main_screen(self):
        """
        Shows the main menu screen.
        """
        self.clear()

        if self.game.level.time > 0:
            self.add_button("Continue", self.hide)
            self.add_button("Restart Game", lambda: self.game.load_level(self.game.level.name))
        else:
            self.add_button("Start Game", self.hide)

        self.add_button("How To Play", self.show_how_to_play_screen)
        self.add_button("Change Level", self.show_change_level_screen)
        self.add_button("Leaderboard", self.show_leaderboard_screen)
        self.add_button("Quit Game", self.game.quit)

    def show_how_to_play_screen(self):
        """
        Shows the how to play menu screen.
        """
        self.clear()
        self.add_button("Back", self.show_main_screen)

        instructions = Prefab("menu_how_to_play", 0, self.component_next)
        self.components.add(instructions)
        instructions.rect.x = (self.rect.width - instructions.rect.width) / 2

    def show_change_level_screen(self):
        """
        Shows the change level screen.
        """
        self.clear()
        self.add_button("Back", self.show_main_screen)

        if self.game.level.name != "basic":
            self.add_level_button("basic")

        if self.game.level.name != "path":
            self.add_level_button("path")

        if self.game.level.name != "maze":
            self.add_level_button("maze")

    def show_leaderboard_screen(self):
        """
        Shows the leaderboard screen.
        """
        self.leaderboard.retrieve()
        self.clear()
        self.add_button("Back", self.show_main_screen)
        self.add_button("Enter Player", self.show_enter_player_screen)
        self.add_button("Current Player: " + self.leaderboard.get_current_player(), None)

        if self.leaderboard.entries is None:
            self.add_button("Error Loading Leaderboard", None)
        elif len(self.leaderboard.entries) == 0:
            self.add_button("No scores yet", None)
        else:
            # Show all entries with only name and score
            for entry in self.leaderboard.entries:
                self.add_button(entry.name + " - " + str(entry.score), None)

    def show_lose_screen(self):
        """
        Shows the game over screen and automatically adds score to leaderboard.
        """
        # Automatically add score for current player
        current_score = self.game.level.get_score()
        current_wave = self.game.wave.number
        current_level = self.game.level.name
        self.leaderboard.add_score(current_score, current_level, current_wave)
        
        self.show()
        self.clear()
        self.add_button("Game Over", None)
        self.add_button("You Reached Wave " + str(current_wave), None)
        self.add_button(str(current_score) + " Points", None)
        self.add_button("Score added for: " + self.leaderboard.get_current_player(), None)
        self.add_button("Restart Game", lambda: self.game.load_level(current_level))

    def show_enter_player_screen(self):
        """
        Shows the enter player name screen.
        """
        self.clear()
        self.add_button("Enter Player Name", None)
        self.leaderboard_name = self.add_button("", None)
        self.add_button("Submit", self.submit_player_name)
        self.add_button("Back", self.show_leaderboard_screen)

    def submit_player_name(self):
        """
        Sets the player name for tracking.
        """
        if self.leaderboard_name and self.leaderboard_name.text != "":
            self.leaderboard.set_player(self.leaderboard_name.text)
            self.show_leaderboard_screen()
        else:
            self.show_leaderboard_screen()

    def show_add_to_leaderboard_screen(self):
        """
        Shows the add to leaderboard screen (deprecated - now automatic).
        """
        # This method is kept for backward compatibility but scores are now added automatically
        self.show_lose_screen()

    def submit_leaderboard(self):
        """
        Attempts to submit a score to the leaderboard (deprecated - now automatic).
        """
        # This method is kept for backward compatibility but scores are now added automatically
        pass


    

   
class MenuLabel(Prefab):
    """
    A label displayed by the menu system. Contains a background.
    """

    