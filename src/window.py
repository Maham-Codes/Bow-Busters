import pygame
class Window:
    # wrapper for pygame window that handles display and background music
    # sets up screen size colors and audio

    def __init__(self, width, height):
        # creates the game window and starts background music
        # args: width - window width in pixels
        #       height - window height in pixels
        self.resolution = (width, height)
        self.screen = pygame.display.set_mode(self.resolution)
        self.set_background(0, 0, 0)
        # load and loop background music
        pygame.mixer.music.load("textures/background_music.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)

    def set_title(self, title):
        # changes the text shown in the window title bar
        # args: title - new title text to display
        pygame.display.set_caption(title)

    def set_background(self, r, g, b):
        # changes the background color of the window
        # args: r - red value 0 to 255
        #       g - green value 0 to 255
        #       b - blue value 0 to 255
        self.background = pygame.Surface(self.resolution)
        self.background.fill(pygame.Color(r, g, b))
        self.background = self.background.convert()

    def clear(self):
        # clears the screen by filling it with the background color
        # called before drawing each new frame
        pygame.display.flip()
        self.screen.blit(self.background, (0, 0))
