import numpy as np
from scipy import *
from scipy import ndimage

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
        if self.inflation == None:
            self.inflation = self.calculateInflation()
        
    def clear(self):
        """Set all diffusion array elements to zero"""
        self.array.fill(0)

    # adapted from http://ml-ants.googlecode.com/hg-history/8f438bb37142cf2c6592b04dd205d1f7b2fe39d3/src/bot/ExploreBot.py
    def calculateInflation(self):
        """Not sure if we'll want to keep this it's not totally right, but better than what we have.
        The general idea of just multiplying by a constant array with larger values closer to obstacles is a good solution."""
        lost = (ndimage.correlate(self.obstacleAry.astype(float64),
                              array([[0,1,0],[1,0,1],[0,1,0]]), mode='wrap') * (1 - self.obstacleAry))
        return 4.0 / ((4 - lost).astype(float64))

    # adapted from http://ml-ants.googlecode.com/hg-history/8f438bb37142cf2c6592b04dd205d1f7b2fe39d3/src/bot/ExploreBot.py        
    def diffuse(self):
        """Not sure if we'll want to keep this it's not totally right, but better than what we have"""
        for n in xrange(self.diffusionIterations):
            self.array = ((ndimage.correlate(self.array*self.inflation, diffusionKernel) -
                     REMAIN * (self.inflation - 1)) * self.obstacleAry)
        
    def diffuse2(self):
        for n in xrange(self.diffusionIterations):
            # mode='same' means the output array should be the same size
            # bounary='wrap' means to wrap the convolution around the array dimensions
            # self.diffusionAry = sig.convolve2d(self.diffusionAry, diffusionKernel, mode='same', boundary='wrap')
            #                                   * self.obstacleAry
            ary = self.array
            for i in (-1, 1):
                for j in (0, 1):
                    #experimentation needed here, for efficiency.
                    ary += (self.rate*np.roll(self.array*self.obstacleAry, i, j))
            self.array = ary * self.obstacleAry
            # convolution is unbounded, so scale the array to range [0, 1]
            max = np.max(self.array)
            if max > 0:
                self.array /= max
                
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

