import numpy as np

class Metric:
    obstacleAry = None # instantiated as a static field in GameState

    """Class to hold name, rate and numpy array for a diffusion metric"""
    def __init__(self, name, rate, diffusionIterations):
        self.name = name
        self.rate = rate
        self.diffusionIterations = diffusionIterations
        self.array = np.zeros((self.obstacleAry.shape[0], self.obstacleAry.shape[1]))

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
