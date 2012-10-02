import MapFrame
import random as rand

class Bird:
    color = "#00FF00"
    
    def __init__(self, map):
        self.map = map
        self.x = rand.randint(0, map.numCols)
        self.y = rand.randint(0, map.numRows)

    def move(self):
        # find the diffusion values neighboring bird
        neighborValues = dict()
        neighborValues['N'] = self.map.npAry[self.x, (self.y - 1) % self.map.numRows]
        neighborValues['S'] = self.map.npAry[self.x, (self.y + 1) % self.map.numRows]
        neighborValues['E'] = self.map.npAry[(self.x + 1) % self.map.numCols, self.y]
        neighborValues['W'] = self.map.npAry[(self.x - 1) % self.map.numCols, self.y]

            # find direction with the max diffusion value
        direction = max(neighborValues, key=neighborValues.get)
        # move bird in that direction
        self.moveInDirection(direction)
        # if bird got to goal, remove goal
        if [self.x, self.y] in self.map.goals:
            self.map.goals.remove([self.x, self.y])
        
    def moveInDirection(self, direction):
        if direction == 'N':
            self.y -= 1
        elif direction == 'S':
            self.y += 1
        elif direction == 'E':
            self.x += 1
        else:
            self.x -= 1
            
        # wrap bird loc around grid
        self.x %= self.map.numCols
        self.y %= self.map.numRows