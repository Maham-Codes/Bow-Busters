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
    """
    Loads and scales a trophy texture located inside textures/.
    """
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
    """
    Lazily loads and caches trophy surfaces (to avoid convert_alpha before display init).
    """
    if index < 0 or index >= len(TROPHY_FILENAMES):
        return None
    cached = _TROPHY_CACHE[index]
    if cached is None:
        cached = _load_trophy_texture(TROPHY_FILENAMES[index])
        _TROPHY_CACHE[index] = cached
    return cached


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
        self.defence_buttons = []
        self.ability_buttons = []
        
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

        # defence buttons (left bar)
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

        # ability buttons (right bar)
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