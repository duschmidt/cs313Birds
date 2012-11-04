from Entity import *
from Frame import Cell

class Food(Entity):
    """This is the entity class for food"""

    imageName = "apple.png"
    name = "food"
    
    def update(self):
        """Override the Sprite update method.  Food does not change position"""
        pass

    def eat(self):
        pass