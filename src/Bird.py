import MapFrame
import random as rand

class Bird:
    color = "#00FF00"
    
    def __init__(self, map):
        self.map = map
        self.x = rand.randint(0, map.numCols - 1)
        self.y = rand.randint(0, map.numRows - 1)

    def move(self):
        # find the diffusion values neighboring bird
        neighborValues = dict()
        neighborValues['N'] = self.map.npAry[self.x, (self.y - 1) % self.map.numRows]
        neighborValues['S'] = self.map.npAry[self.x, (self.y + 1) % self.map.numRows]
        neighborValues['E'] = self.map.npAry[(self.x + 1) % self.map.numCols, self.y]
        neighborValues['W'] = self.map.npAry[(self.x - 1) % self.map.numCols, self.y]

        # find direction with the max diffusion value
        while True:
            direction = max(neighborValues, key=neighborValues.get)
            neighborValues.pop(direction)
            newCell = self.cellInDirection(direction)
            # if a new, unoccupied cell has been found, or if we're out of directions to check, break
            if newCell != None or not neighborValues:
                break

        if newCell != None:
            self.x = newCell[0]
            self.y = newCell[1]
            
        # if bird got to goal, remove goal
        if [self.x, self.y] in self.map.goals:
            self.map.goals.remove([self.x, self.y])
        
    def cellInDirection(self, direction):
        cell = [self.x, self.y]
        if direction == 'N':
            cell[1] -= 1
        elif direction == 'S':
            cell[1] += 1
        elif direction == 'E':
            cell[0] += 1
        else:
            cell[0] -= 1
            
        # wrap bird loc around grid
        cell[0] %= self.map.numCols
        cell[1] %= self.map.numRows

        # check if another bird is in the new cell
        return None if self.map.occupied(cell[0], cell[1]) else cell
