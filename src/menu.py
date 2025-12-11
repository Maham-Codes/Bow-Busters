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