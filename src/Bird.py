import MapFrame

import random as rand

class Bird:
    color = "#00FF00"
    
    def __init__(self, map):
        self.map = map
        self.pos = MapFrame.Position(rand.randint(0, map.numCols - 1), rand.randint(0, map.numRows - 1))

    def move(self):
        neighborValues = dict()
        # find the diffusion values neighboring the bird
        for direction in ('N', 'S', 'E', 'W'):
            neighborValues[direction] = self.map.valueInDirection(self.pos, direction)

        # find direction with the max diffusion value
        direction = max(neighborValues, key=neighborValues.get)
        # move to new position if it's not occupied with a bird (value of -1)
        if neighborValues[direction] != -1:
            self.pos = self.map.posInDirection(self.pos, direction)
            
        # if bird got to goal, remove goal
        if self.pos in self.map.goals:
            self.map.goals.remove(self.pos)
    