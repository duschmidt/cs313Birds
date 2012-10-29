import numpy as np

class Metric:
    obstacleAry = None # instantiated as a static field in GameState
    
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
        if not self.obstacleAry[position]:
            return -1
            
        return self.array[neighborPos]

    def getRankedDirections(self, position):
        neighborValues = {}
        # find the diffusion values neighboring the bird
        for direction in ('N', 'S', 'E', 'W'):
            neighborValues[direction] = self.array[self.positionInDirection(position, direction)]
        # find direction with the max diffusion value
        return reversed(sorted(neighborValues, key=neighborValues.get))

