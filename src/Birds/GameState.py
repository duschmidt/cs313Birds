import numpy as np
from EntityGroup import EntityGroup
from Entity import Entity

class GameState():
	"""This is the top level class responsible for managing game state"""
	entityGroups={}		#:dictionary of entity groups keyed by group name
	obstacleArray = None	#:A numpy array for storing diffusion obstacles
        numCols = 0
        numRows = 0

        class Metric:
                """Class to hold name, rate and numpy array for a diffusion metric"""
                def __init__(self, gameState, name, rate, numDiffusions):
                        self.gameState = gameState
                        self.name = name
                        self.rate = rate
                        self.numDiffusions = numDiffusions
                        self.array = np.zeros((gameState.numCols, gameState.numRows))

                def diffuse(self):
                    for n in xrange(self.numDiffusions):
                        # mode='same' means the output array should be the same size
                        # bounary='wrap' means to wrap the convolution around the array dimensions
                        # self.diffusionAry = sig.convolve2d(self.diffusionAry, diffusionKernel, mode='same', boundary='wrap')
                        #                                   * self.obstacleAry
                        for i in (-1, 1):
                            for j in (0, 1):
                                #experimentation needed here, for efficiency.
                                self.array += (diffuseAmt*np.roll(self.array*self.gameState.obstacleAry, i, j))
                                self.array = ary * self.gameState.obstacleAry
                                # convolution is unbounded, so scale the array to range [0, 1]
                                max = np.max(self.array)
                                if max > 0:
                                    self.array /= max
                                            
	def __init__(self, mapFile):
		"""Constructs a new GameState object"""
                # load obstacle array from map file
                self.obstacleAry = np.loadtxt(mapFile, dtype='c').astype('float')
                # how many columns and rows are in this map?  (it is assumed that maps are rectangular)
                self.numCols = self.obstacleAry.shape[0]
                self.numRows = self.obstacleAry.shape[1]
                # instantiate EntityGroups
                self.entityGroups["Bird"] = EntityGroup(self, "Bird", (Metric(self, "attract",  .3, 30),
                                                                       Metric(self, "repulse", -.1, 30))
                self.entityGroups["Food"] = EntityGroup(self, "Food", (Metric(self, "attract",  .5, 30)))

	def update(self):
		"""Applies diffusion to all environment metrics.  Also calls update on all entity groups"""
		pass

	def getAllUpdatedEntities(self):
		"""Returns a list of Entity objects whose states were updated as a result of the last call to update."""
		pass

	def positionToDiscrete(self, position):
		"""Convert a continuous position given by position into discrete cells"""
		pass

	def addEntityGroup(self, groupName, diffusionRate):
		"""Create a new entity group with the given group name and diffusion rate"""
		pass

	def removeEntityGroup(self, groupName):
		"""Remove the entity group with the given name"""
		pass

	def addEntity(self, entity, groupName):
		"""Add the given entity to the group given by groupName"""
		pass

	def removeEntity(self, entity, groupName):
		"""Remove the givent entity from the group given by groupName"""
		pass

	def getEntitiesAtPosition(self, position):
		"""Returns a list of Entity objects who are occupying the discrete cell which contains
		the given position."""
		pass


