from src.prefab import Prefab
from src.leaderboard import Leaderboard
from pygame.sprite import OrderedUpdates
import pygame
import math
import os


LEADERBOARD_ASSET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "textures"))
TROPHY_ICON_SIZE = (32, 32)
TROPHY_FILENAMES = ["trophy_gold.png", "trophy_silver.png", "trophy_bronze.png"]
_TROPHY_CACHE = [None, None, None]


def _load_trophy_texture(filename):
    # loads a trophy icon image from the textures folder
    # scales it to the right size for display in the leaderboard
    # args: filename - name of the trophy image file
    path = os.path.join(LEADERBOARD_ASSET_DIR, filename)
    if not os.path.exists(path):
        print(f"Warning: missing leaderboard trophy asset '{filename}' in textures/")
        return None
    try:
        surface = pygame.image.load(path).convert_alpha()
        if TROPHY_ICON_SIZE is not None:
            surface = pygame.transform.smoothscale(surface, TROPHY_ICON_SIZE)
        return surface
    except Exception as exc:
        print(f"Warning: failed to load trophy asset '{filename}': {exc}")
        return None
        

def _get_trophy_surface(index):
    # gets a trophy icon for the leaderboard top 3 players
    # loads and caches them so we dont reload every time
    # args: index - which trophy to get (0=gold 1=silver 2=bronze)
    if index < 0 or index >= len(TROPHY_FILENAMES):
        return None
    cached = _TROPHY_CACHE[index]
    if cached is None:
        cached = _load_trophy_texture(TROPHY_FILENAMES[index])
        _TROPHY_CACHE[index] = cached
    return cached


class Menu(Prefab):
    # manages all the menus in the game
    # handles main menu pause screen leaderboard and game over screens

    def __init__(self, game):
        # sets up the menu system with leaderboard and buttons
        # args: game - reference to the main game object
        super().__init__("menu", 0, 0)

        self.game = game
        self.leaderboard = Leaderboard()
        self.components = OrderedUpdates()
        self.clear()
        self.show_main_screen()
        self.visible = True
        self.leaderboard_name = None
        self.defence_buttons = []
        self.ability_buttons = []
        
    def show(self):
        # displays the menu and pauses the game
        self.visible = True
        self.show_main_screen()

    def hide(self):
        # closes the menu and shows the in game ui instead
        # creates tower selection buttons and stat displays
        self.visible = False
        self.clear()

        # create tower selection buttons along the left side
        self.defence_buttons = [
            MenuButton(
                self,
                "menu_defence_button",
                self.game.defence_prototypes[i].display_name,
                (i + 1) * 64,
                0,
                lambda i=i: self.game.select_defence(i),
            )
            for i in range(len(self.game.defence_prototypes))
        ]
        self.components.add(self.defence_buttons)

        # create special ability buttons on the right side
        self.ability_buttons = [
            MenuButton(self, "menu_pause_button", "Spike", 960, 0, lambda: self.game.abilities.use("crystal_spike")),
            MenuButton(self, "menu_pause_button", "Undo", 960, 64, self.game.undo_last_purchase),
        ]
        for btn in self.ability_buttons:
            self.components.add(btn)

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
        # removes all buttons and labels from the current menu screen
        # called when switching between different menu screens
        self.components.remove(self.components)
        self.component_next = self.top

    def update(self):
        # runs every frame to update ui text and button states
        # updates wave count lives money and tower availability
        if not self.visible:
            self.wave_label.set_text("Wave: " + str(self.game.wave.number))
            self.lives_label.set_text("Lives: " + str(self.game.level.lives))
            self.lives_label.highlighted = (self.game.level.lives < 5)
            self.money_label.set_text("Money: " + str(self.game.level.money))
            self.score_label.set_text("Score: " + str(self.game.level.get_score()))

            # disable tower buttons that cost too much money
            for i in range(len(self.defence_buttons)):
                self.defence_buttons[i].disabled = (self.game.defence_prototypes[i].cost > self.game.level.money)
                self.defence_buttons[i].selected = (self.game.defence_type == i)

        self.components.update()
        
        # update ability button cooldowns and availabilitys and availability
        for btn in getattr(self, "ability_buttons", []):
            if btn.text.startswith("Spike"):
                # check if spike ability is ready and show cooldown timer
                ready = self.game.abilities.is_ready("crystal_spike")
                btn.disabled = not ready
                cd = self.game.abilities.get_cooldown("crystal_spike")
                btn.set_text("Spike" if cd <= 0 else "Spike ({:.1f})".format(cd))
            elif btn.text == "Undo":
                # disable undo button if no towers have been placed
                has_history = len(self.game.purchase_history) > 0
                btn.disabled = not has_history


    def clicked(self):
        # handles mouse clicks by checking all buttons
        for component in self.components:
            if isinstance(component, MenuButton):
                component.clicked()

    def key_pressed(self, key):
        # handles keyboard input for typing player names
        # only works when entering a name on the leaderboard screen
        # args: key - which key was pressed
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
        # renders the menu background and all buttons to the screen
        # args: screen - pygame surface to draw on
        if self.visible:
            screen.blit(self.image, (0, 0))

        self.components.draw(screen)

    def add_button(self, text, callback, tint=None, icon=None, left_align=False, text_colour=None):
        # creates a new button and adds it to the current menu screen
        # can customize colors icons and alignment for special buttons
        # args: text - what to display on the button
        #       callback - function to call when clicked
        #       tint - optional background color
        #       icon - optional image to show
        #       left_align - align text left instead of center
        #       text_colour - optional text color
        # returns: the created button
        button = MenuButton(self, "menu_button", text, 0, self.component_next, callback)

        # apply custom styling if any options were provided
        customised = False
        if left_align:
            button.left_align = True
            customised = True
        if text_colour is not None:
            button.text_colour_override = text_colour
            customised = True

        # apply background color tint or icon if specified
        if tint is not None:
            button.tint = tint
            customised = True
        if icon is not None:
            button.icon_surface = icon
            customised = True
        # rebuild button image if we changed anything
        if customised:
            img = button.image_template
            button.image_template = None
            button.set_image(img)
        button.rect.x = (self.rect.width - button.rect.width) / 2

        self.components.add(button)
        self.component_next += button.rect.height
        self.component_next += button.padding

        return button

    def add_level_button(self, level):
        # creates a button for switching to a different level
        # args: level - name of the level to load when clicked
        button = MenuButton(self, "menu_level_" + level, level, 0, self.component_next, lambda: self.game.load_level(level))
        button.rect.x = (self.rect.width - button.rect.width) / 2
        
        self.components.add(button)
        self.component_next += button.rect.height
        self.component_next += button.padding

    def show_main_screen(self):
        # displays the main menu with start continue and settings options
        self.clear()
        self.add_button("Music: " + ("ON" if self.game.music_on else "OFF"), self.toggle_music_button)

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
        # displays instructions on how to play the game
        self.clear()
        self.add_button("Back", self.show_main_screen)

        instructions = Prefab("menu_how_to_play", 0, self.component_next)
        self.components.add(instructions)
        instructions.rect.x = (self.rect.width - instructions.rect.width) / 2

    def show_change_level_screen(self):
        # shows buttons to switch to different available levels
        self.clear()
        self.add_button("Back", self.show_main_screen)

        if self.game.level.name != "basic":
            self.add_level_button("basic")

        if self.game.level.name != "path":
            self.add_level_button("path")

        if self.game.level.name != "maze":
            self.add_level_button("maze")

    def show_leaderboard_screen(self):
        # displays the high score leaderboard with player names and scores
        # top 3 get special purple styling and trophy icons
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
            # display all scores with player names
            # give top 3 players fancy purple colors and trophy icons
            for index, entry in enumerate(self.leaderboard.entries):
                text = entry.name + " - " + str(entry.score)

                # default colors for most players
                tint = None
                text_colour = None
                icon = _get_trophy_surface(index)

                # special styling for gold silver bronze winners
                if index < 3:
                    tint = (60, 20, 90)
                    text_colour = (230, 210, 255)

                self.add_button(
                    text,
                    None,
                    tint=tint,
                    icon=icon,
                    left_align=True,
                    text_colour=text_colour,
                )

    def show_lose_screen(self):
        # displays game over screen when player loses all lives
        # automatically saves the score to the leaderboard
        # save score for the current player
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
        # shows a screen where player can type their name
        # used for tracking scores on the leaderboard
        self.clear()
        self.add_button("Enter Player Name", None)
        self.leaderboard_name = self.add_button("", None)
        self.add_button("Submit", self.submit_player_name)
        self.add_button("Back", self.show_leaderboard_screen)

    def submit_player_name(self):
        # saves the typed player name and returns to leaderboard
        if self.leaderboard_name and self.leaderboard_name.text != "":
            self.leaderboard.set_player(self.leaderboard_name.text)
            self.show_leaderboard_screen()
        else:
            self.show_leaderboard_screen()

    def show_add_to_leaderboard_screen(self):
        # old method kept for compatibility but not used anymore
        # scores are added automatically now
        self.show_lose_screen()

    def submit_leaderboard(self):
        # old method kept for compatibility but not used anymore
        # scores are added automatically now
        pass
    
    def toggle_music_button(self):
        # turns music on or off and updates the menu button text
        self.game.toggle_music()
        self.show_main_screen()



class MenuLabel(Prefab):
    # a text display with a background used in menus
    # shows information like wave count lives and money

    def __init__(self, menu, type, text, x, y):
        # creates a new label with text and background
        # args: menu - reference to the menu system
        #       type - prefab name for styling
        #       text - what to display
        #       x - horizontal position
        #       y - vertical position
        super().__init__(type, x, y)

        self.text = text
        self.image_template = None
        self.highlighted = False
        self.selected = False
        self.disabled = False
        # optional styling used by fancy leaderboard buttons
        self.tint = None
        self.icon_surface = None
        self.left_align = False
        self.text_colour_override = None
        self.set_image(self.image_s)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def update(self):
        # runs every frame to change appearance based on state
        # shows different images for disabled highlighted or normal
        if self.disabled:
            self.set_image(self.image_d)
        elif self.highlighted or self.selected:
            self.set_image(self.image_h)
        else:
            self.set_image(self.image_s)

    def set_text(self, text):
        # changes the text displayed on the label
        # args: text - new text to show
        if self.text != text:
            self.text = text
            
            img = self.image_template
            self.image_template = None
            self.set_image(img)

    def set_image(self, image):
        # changes the background image of the label
        # applies tinting if needed and renders text on top
        # args: image - pygame surface to use as background
        if self.image_template == image:
            return

        self.image_template = image

        if hasattr(self, "font"):
            # make a copy so we dont modify the original
            base = image.copy()

            # apply color tint for special buttons like leaderboard entries
            tint = getattr(self, "tint", None)
            if tint is not None:
                # add semi transparent color overlay
                tint_surface = pygame.Surface(base.get_size(), pygame.SRCALPHA)
                tint_surface.fill((*tint, 140))
                base.blit(tint_surface, (0, 0))

            # draw the text on top of the background
            self.image = base
            self.render_text(self.image)
        else:
            self.image = image
           
    def render_text(self, background):
        # draws the text and optional icon onto the button background
        # handles alignment and positioning
        # args: background - surface to draw on
        # use default color or custom color if specified
        colour = (self.col_r, self.col_g, self.col_b)
        override = getattr(self, "text_colour_override", None)
        if override is not None:
            colour = override

        rendered = self.font.render(self.text, True, colour)
        bg_rect = background.get_rect()

        # Vertical centring
        text_y = (bg_rect.height - rendered.get_rect().height) // 2

        # Horizontal alignment: left or centred
        if getattr(self, "left_align", False):
            text_x = bg_rect.left + 20
        else:
            text_x = (bg_rect.width - rendered.get_rect().width) // 2

        # Draw text first
        background.blit(rendered, (text_x, text_y))

        # Then optional trophy icon on the right side
        icon = getattr(self, "icon_surface", None)
        if icon is not None:
            icon_rect = icon.get_rect()
            icon_rect.centery = bg_rect.centery
            icon_rect.x = bg_rect.right - icon_rect.width - 20
            background.blit(icon, icon_rect)


class MenuButton(MenuLabel):
    # a clickable button that can trigger actions when pressed
    # extends menulabel with mouse interaction

    def __init__(self, menu, type, text, x, y, callback):
        # creates a clickable button
        # args: menu - reference to menu system
        #       type - prefab name for styling
        #       text - button label
        #       x - horizontal position
        #       y - vertical position
        #       callback - function to call when clicked
        super().__init__(menu, type, text, x, y)

        self.callback = callback
        self.last_pressed = True

    def update(self):
        # runs every frame to check if mouse is hovering over button
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        self.highlighted = hover and self.callback is not None

        super().update()

    def clicked(self):
        # checks if button was clicked and triggers its callback function
        hover = self.rect.collidepoint(pygame.mouse.get_pos())

        if hover and self.callback is not None:
            self.callback()
