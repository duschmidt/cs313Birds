from Entity import *
from Frame import Cell

class Bird(Entity):
    """This is the entity class for birds"""

    def __init__(self, gameState, id, position):
        Entity.__init__(self, gameState, id, position)
        self.image, self.rect = load_image("bird.png", position, (Cell.width, Cell.height))

    def update(self):
        """Update the bird's position"""
        # move to new cell if it's not occupied with a bird (value of -1)
        rankedDirections = self.groups()[0].getRankedDirections(self.rect.topleft, "attract")
        newPos = None
        for direction in rankedDirections:
            newPos = self.positionInDirection(direction)
            if not (self.gameState.isBirdAtPosition(newPos) or self.gameState.isObstacleAtPosition(newPos)):
                break # two birds can't occupy the same position, and of course, obstacles are out of bounds

        if newPos == None: # no valid neighbors, don't move
            return
        
        self.rect.topleft = newPos
        for entity in self.gameState.getEntitiesAtPosition(newPos):
            if entity.id == 0:
                self.gameState.removeEntity(entity, "Food")