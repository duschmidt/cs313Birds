from Entity import *
from Frame import Cell

class Food(Entity):
    """This is the entity class for food"""

    def __init__(self, gameState, id, position):
        Entity.__init__(self, gameState, id, position)
        self.image, self.rect = load_image("apple.png", position, (Cell.width, Cell.height))

    def update(self):
        """Override the Sprite update method.  Food does not change position"""
        pass
            