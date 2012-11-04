from Entity import *
from Frame import Cell

class Bird(Entity):
    """This is the entity class for birds"""

    imageName = "bird.png"
    def update(self):
        """Update the bird's position"""
        # move to new cell if it's not occupied with a bird (value of -1)
        rankedDirections = self.groups()[0].getRankedDirections(self.discretePosition, "attract")
        newPos = None
        for direction in rankedDirections:
            newPos = self.positionInDirection(direction)
            if not (self.gameState.isBirdAtPosition(newPos) or self.gameState.isObstacleAtPosition(newPos)):
                break # two birds can't occupy the same position, and of course, obstacles are out of bounds

        if newPos == None: # no valid neighbors, don't move
            return
            
        for entity in self.gameState.getEntitiesAtPosition(newPos):
            if entity.id == 0:
                self.gameState.removeEntity(entity, "Food")

        self.discretePosition = newPos
        self.rect.topleft = (newPos[0] * Cell.width, newPos[1] * Cell.height)