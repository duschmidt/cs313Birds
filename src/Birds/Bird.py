from Entity import *
from Frame import Cell

class Bird(Entity):
    """This is the entity class for birds"""

    def __init__(self, gameState, id, position):
        Entity.__init__(self, gameState, id, position)
        self.image, self.rect = load_image("bird.png", position, (Cell.width, Cell.height))

    def update(self):
        """Update the bird's position'"""
        #neighborhood = self.groups()[0].neighborhood(self.gameState.positionToDiscrete(self.position))