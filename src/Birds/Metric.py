import diffuse
import numpy as np
from scipy import *
from scipy import ndimage
import scipy.signal as sig

TRANSITION = 0.125
REMAIN = 0.5

diffusionKernel = array([[0,          TRANSITION, 0         ],
                         [TRANSITION, REMAIN,     TRANSITION],
                         [0,          TRANSITION, 0         ]])
class Metric:
    obstacleAry = None # instantiated as a static field in GameState
    inflation = None
    
    """Class to hold name, rate and numpy array for a diffusion metric"""
    def __init__(self, name, rate, diffusionIterations):
        self.name = name
        self.rate = rate
        self.diffusionIterations = diffusionIterations
        self.array = np.zeros((self.obstacleAry.shape[0], self.obstacleAry.shape[1]))
        
    def clear(self):
        """Set all diffusion array elements to zero"""
        self.array.fill(0)

    def diffuse(self):
        # could speed this up even more by doing all iterations and array
        # multiplications in c
        for d in xrange(self.diffusionIterations):
            self.array = diffuse.diffuse(self.array, self.obstacleAry)
            self.array *= self.obstacleAry
            
    #Map Method, maybe a frame method?
    def positionInDirection(self, pos, direction):
        col, row = pos
        if direction == 'N':
            row -= 1
        elif direction == 'S':
            row += 1
        elif direction == 'E':
            col += 1
        else:
            col -= 1

        # wrap around grid boundaries
        col %= self.array.shape[0]
        row %= self.array.shape[1]

        return (col, row)

    def valueInDirection(self, position, direction):
        neighborPos = self.positionInDirection(position, direction)
        if not self.obstacleAry[neighborPos]:
            return -sys.maxint
            
        return self.array[neighborPos]

    def getRankedDirections(self, position):
        neighborValues = {}
        # find the diffusion values neighboring the bird
        for direction in ('N', 'S', 'E', 'W'):
            neighborValues[direction] = self.array[self.positionInDirection(position, direction)]
        # find direction with the max diffusion value
        return reversed(sorted(neighborValues, key=neighborValues.get))

