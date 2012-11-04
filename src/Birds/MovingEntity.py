from Entity import *
from Frame import Cell

class MovingEntity(Entity):
    """This is the base class for moving entities"""
    name = "moving"
    
    def update(self):
        """Update the bird's position"""
        # move to new cell if it's not occupied with an entity of the same type or an obstacle
        rankedDirections = self.groups()[0].getRankedDirections(self.discretePosition)
        newPos = None
        for direction in rankedDirections:
            newPos = self.positionInDirection(direction)
            if not (self.gameState.isEntityTypeAtPosition(self.name, newPos) or self.gameState.isObstacleAtPosition(newPos)):
                break # two birds can't occupy the same position, and of course, obstacles are out of bounds

        if newPos == None: # no valid neighbors, don't move
            return
            
        self.discretePosition = newPos
        self.rect.topleft = (newPos[0] * Cell.width, newPos[1] * Cell.height)
        