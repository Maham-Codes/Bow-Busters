import pygame
from src.game import Game
from src.window import Window

#init pygame
pygame.init()

#create window
window = Window(1280, 768)
window.set_title("Bow Busters")
window.set_background(148, 168, 176)

#create game instance
game = Game(window)
game.run()

#quit pygame
pygame.quit()
