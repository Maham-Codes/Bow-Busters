import pygame
class Window:
    """ 
    wrapper class for pygame window
    """

    def __init__(self, width, height):
        """ 
        constructor   
        args:
            width (int): window width, in pixels
            height (int): window height, in pixels
        """
        self.resolution = (width, height)
        self.screen = pygame.display.set_mode(self.resolution)
        self.set_background(0, 0, 0)

    def set_title(self, title):
        """ 
        s window title
        args:
            title (str): new title textt
        """
        pygame.display.set_caption(title)

    def set_background(self, r, g, b):
        """ 
        Sets the background colour 
        
        Args:
            r (float): The new r channel value
            g (float): The new g channel value
            b (float): The new b channel value
        """
        self.background = pygame.Surface(self.resolution)
        self.background.fill(pygame.Color(r, g, b))
        self.background = self.background.convert()

    def clear(self):
        """ 
        clears window using bg color
        """
        pygame.display.flip()
        self.screen.blit(self.background, (0, 0))
